"""Advanced Load Balancing and Routing Policies.

Supports:
- Weighted Round-Robin
- Lowest Latency First
- Cost-Minimized Routing (Free/High-Quota tiers prioritized)
"""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional, Sequence, Tuple

# Cost rank per provider: lower ranks are cheaper and preferred by the
# ``lowest_cost`` routing strategy. OAuth/local quota-based providers rank
# before metered pay-per-token API platforms.
PROVIDER_COST_RANKS: Dict[str, int] = {
    "ollama": 0,
    "google_antigravity": 1,
    "openai": 1,  # Codex/ChatGPT OAuth (subscription quota)
    "anthropic": 1,  # Claude Code OAuth (subscription quota)
    "xai": 1,  # Grok Build OAuth (subscription quota)
    "google_ai_studio": 2,  # free-tier API key with limits
    "code_assist": 2,
    "openai_platform": 3,
    "claude_platform": 3,
    "xai_console": 3,
}
DEFAULT_COST_RANK = 2


def provider_cost_rank(provider_id: Any) -> int:
    """Return the cost tier for a provider (lower = cheaper = preferred)."""
    return PROVIDER_COST_RANKS.get(str(provider_id or "").strip().lower(), DEFAULT_COST_RANK)


def weighted_order(
    items: Sequence[Tuple[Any, float]],
    *,
    rng: Optional[random.Random] = None,
) -> List[Any]:
    """Return items in weighted-random order (sampling without replacement).

    ``items`` are ``(value, weight)`` pairs; non-positive weights are clamped
    to a tiny epsilon so every candidate keeps a nonzero chance.
    """
    generator = rng or random
    remaining = [(value, max(1e-6, float(weight))) for value, weight in items]
    ordered: List[Any] = []
    while remaining:
        total = sum(weight for _, weight in remaining)
        pick = generator.uniform(0, total)
        cursor = 0.0
        for index, (value, weight) in enumerate(remaining):
            cursor += weight
            if cursor >= pick:
                ordered.append(value)
                remaining.pop(index)
                break
        else:
            ordered.append(remaining.pop()[0])
    return ordered


def select_weighted_candidate(
    candidates: List[Dict[str, Any]], weights: Optional[Dict[str, float]] = None
) -> Optional[Dict[str, Any]]:
    """Select a candidate based on assigned weights."""
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    weights_map = weights or {}
    total_weight = 0.0
    item_weights = []

    for c in candidates:
        name = str(c.get("filename") or c.get("name") or "")
        w = max(0.000001, float(weights_map.get(name, 1.0)))
        item_weights.append(w)
        total_weight += w

    r = random.uniform(0, total_weight)
    upto = 0.0
    for c, w in zip(candidates, item_weights):
        if upto + w >= r:
            return c
        upto += w
    return candidates[-1]


def select_lowest_latency_candidate(
    candidates: List[Dict[str, Any]],
    latency_history: Dict[str, float],
) -> Optional[Dict[str, Any]]:
    """Select the candidate with the lowest recorded average latency."""
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    return min(
        candidates,
        key=lambda c: latency_history.get(str(c.get("filename") or c.get("name") or ""), 9999.0),
    )


def select_cost_minimized_candidate(candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Prioritize free tier credentials and high quota allocations before paid providers."""
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    # Priority score: Higher is cheaper/preferable
    def _tier_score(c: Dict[str, Any]) -> int:
        provider = str(c.get("provider") or "").lower()
        tier = str(c.get("tier") or "").lower()
        if "free" in tier:
            return 100
        if "google_ai_studio" in provider:
            return 80
        if "antigravity" in provider:
            return 70
        if "openai_codex" in provider:
            return 60
        return 10  # Standard commercial API

    return max(candidates, key=_tier_score)
