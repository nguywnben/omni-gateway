"""Advanced Load Balancing and Routing Policies.

Supports:
- Weighted Round-Robin
- Lowest Latency First
- Cost-Minimized Routing (Free/High-Quota tiers prioritized)
"""

from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional


def select_weighted_candidate(candidates: List[Dict[str, Any]], weights: Optional[Dict[str, float]] = None) -> Optional[Dict[str, Any]]:
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
        w = max(0.1, float(weights_map.get(name, 1.0)))
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
        key=lambda c: latency_history.get(str(c.get("filename") or c.get("name") or ""), 9999.0)
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
        if "free" in tier or "gemini_cli" in provider:
            return 100
        if "google_ai_studio" in provider:
            return 80
        if "antigravity" in provider:
            return 70
        if "openai_codex" in provider:
            return 60
        return 10  # Standard commercial API

    return max(candidates, key=_tier_score)
