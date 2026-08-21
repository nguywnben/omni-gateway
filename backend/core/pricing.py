"""Model pricing table and cost calculation for the usage ledger.

Design notes (distilled from LiteLLM's ``model_prices_and_context_window.json``
and Langfuse's provided-vs-computed cost model):

- Prices are expressed in **USD per 1 million tokens** for readability and are
  converted to per-token values at calculation time.
- Model lookup uses longest-prefix matching on a normalized model name so that
  dated/versioned variants (``gpt-5-2026-01-12``, ``gemini-2.5-pro-preview``)
  automatically inherit the base price.
- Operators can override or extend the table by dropping a
  ``model_pricing.json`` file into the credentials directory; the file is
  merged over the built-in table and hot-reloaded on mtime change.
- Unknown models cost ``0.0`` (unpriced) instead of guessing: the ledger keeps
  an honest record and the aggregate endpoint exposes how many calls were
  unpriced so operators can fix the table.
"""

from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from log import log
from paths import DEFAULT_CREDENTIALS_DIR

PRICING_OVERRIDES_FILENAME = "model_pricing.json"

# Providers whose inference is local/self-hosted and therefore free.
ZERO_COST_PROVIDERS = frozenset({"ollama"})


@dataclass(frozen=True)
class ModelPricing:
    """USD prices per 1M tokens for a model family."""

    input_per_million: float
    output_per_million: float
    cache_read_per_million: Optional[float] = None
    reasoning_per_million: Optional[float] = None

    def effective_cache_read(self) -> float:
        if self.cache_read_per_million is not None:
            return self.cache_read_per_million
        # Common industry default: cached input billed at 25% of input price.
        return self.input_per_million * 0.25

    def effective_reasoning(self) -> float:
        if self.reasoning_per_million is not None:
            return self.reasoning_per_million
        # Reasoning/thinking tokens are billed as output by every major vendor.
        return self.output_per_million


# Built-in price table (USD per 1M tokens). Longest-prefix match wins.
BUILTIN_MODEL_PRICING: Dict[str, ModelPricing] = {
    # --- Google Gemini ---
    "gemini-3-pro": ModelPricing(2.00, 12.00, 0.50),
    "gemini-3-flash": ModelPricing(0.50, 3.00, 0.125),
    "gemini-2.5-pro": ModelPricing(1.25, 10.00, 0.31),
    "gemini-2.5-flash-lite": ModelPricing(0.10, 0.40, 0.025),
    "gemini-2.5-flash": ModelPricing(0.30, 2.50, 0.075),
    "gemini-2.0-flash-lite": ModelPricing(0.075, 0.30, 0.019),
    "gemini-2.0-flash": ModelPricing(0.10, 0.40, 0.025),
    "gemini-1.5-pro": ModelPricing(1.25, 5.00, 0.3125),
    "gemini-1.5-flash": ModelPricing(0.075, 0.30, 0.019),
    # --- OpenAI ---
    "gpt-5-nano": ModelPricing(0.05, 0.40, 0.005),
    "gpt-5-mini": ModelPricing(0.25, 2.00, 0.025),
    "gpt-5": ModelPricing(1.25, 10.00, 0.125),
    "gpt-4.1-nano": ModelPricing(0.10, 0.40, 0.025),
    "gpt-4.1-mini": ModelPricing(0.40, 1.60, 0.10),
    "gpt-4.1": ModelPricing(2.00, 8.00, 0.50),
    "gpt-4o-mini": ModelPricing(0.15, 0.60, 0.075),
    "gpt-4o": ModelPricing(2.50, 10.00, 1.25),
    "o3-mini": ModelPricing(1.10, 4.40, 0.55),
    "o3": ModelPricing(2.00, 8.00, 0.50),
    "o4-mini": ModelPricing(1.10, 4.40, 0.275),
    "codex-mini": ModelPricing(1.50, 6.00, 0.375),
    # --- Anthropic Claude ---
    "claude-opus-4": ModelPricing(15.00, 75.00, 1.50),
    "claude-sonnet-4": ModelPricing(3.00, 15.00, 0.30),
    "claude-haiku-4": ModelPricing(0.80, 4.00, 0.08),
    "claude-3-7-sonnet": ModelPricing(3.00, 15.00, 0.30),
    "claude-3-5-sonnet": ModelPricing(3.00, 15.00, 0.30),
    "claude-3-5-haiku": ModelPricing(0.80, 4.00, 0.08),
    "claude-3-opus": ModelPricing(15.00, 75.00, 1.50),
    # --- xAI Grok ---
    "grok-4": ModelPricing(3.00, 15.00, 0.75),
    "grok-3-mini": ModelPricing(0.30, 0.50, 0.075),
    "grok-3": ModelPricing(3.00, 15.00, 0.75),
    "grok-code-fast": ModelPricing(0.20, 1.50, 0.02),
    "grok-2": ModelPricing(2.00, 10.00),
}


def _pricing_overrides_path() -> Path:
    credentials_dir = Path(
        os.getenv("CREDENTIALS_DIR", str(DEFAULT_CREDENTIALS_DIR))
    ).expanduser()
    return credentials_dir / PRICING_OVERRIDES_FILENAME


class _PricingTable:
    """Merged built-in + operator-override pricing table with hot reload."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._merged: Dict[str, ModelPricing] = dict(BUILTIN_MODEL_PRICING)
        self._overrides_mtime: Optional[float] = None

    def _load_overrides_locked(self) -> None:
        path = _pricing_overrides_path()
        try:
            mtime = path.stat().st_mtime if path.exists() else None
        except OSError:
            mtime = None

        if mtime == self._overrides_mtime:
            return
        self._overrides_mtime = mtime
        self._merged = dict(BUILTIN_MODEL_PRICING)
        if mtime is None:
            return

        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("pricing overrides must be a JSON object")
            for model_name, entry in raw.items():
                pricing = _parse_override_entry(entry)
                if pricing is not None:
                    self._merged[_normalize_model_name(model_name)] = pricing
            log.info(
                f"[pricing] loaded {len(raw)} model pricing overrides from {path.name}"
            )
        except Exception as exc:
            log.error(f"[pricing] failed to load pricing overrides: {exc}")

    def lookup(self, model: str) -> Optional[ModelPricing]:
        normalized = _normalize_model_name(model)
        if not normalized:
            return None
        with self._lock:
            self._load_overrides_locked()
            table = self._merged
            # Longest-prefix match so dated variants inherit base pricing.
            best_key = ""
            for key in table:
                if normalized.startswith(key) and len(key) > len(best_key):
                    best_key = key
            return table.get(best_key) if best_key else None


def _parse_override_entry(entry: Any) -> Optional[ModelPricing]:
    if not isinstance(entry, dict):
        return None
    try:
        return ModelPricing(
            input_per_million=float(entry.get("input", 0.0)),
            output_per_million=float(entry.get("output", 0.0)),
            cache_read_per_million=(
                float(entry["cache_read"]) if entry.get("cache_read") is not None else None
            ),
            reasoning_per_million=(
                float(entry["reasoning"]) if entry.get("reasoning") is not None else None
            ),
        )
    except (TypeError, ValueError):
        return None


def _normalize_model_name(model: Any) -> str:
    name = str(model or "").strip().lower()
    if name.startswith("models/"):
        name = name[len("models/") :]
    # Strip local-model tag suffixes such as ``llama3:8b``.
    if ":" in name:
        name = name.split(":", 1)[0]
    return name


_pricing_table = _PricingTable()


def find_model_pricing(model: str) -> Optional[ModelPricing]:
    """Return the pricing entry for ``model`` or ``None`` when unpriced."""
    return _pricing_table.lookup(model)


def calculate_cost_usd(
    model: str,
    *,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cached_tokens: int = 0,
    reasoning_tokens: int = 0,
    provider: str = "",
) -> float:
    """Compute the USD cost of one call from its normalized token counts.

    Token semantics follow ``core.usage_stats.normalize_token_usage``:
    ``cached_tokens`` is the cache-read subset of ``input_tokens`` and
    ``reasoning_tokens`` is tracked separately from ``output_tokens``.
    Unknown models return ``0.0`` (the ledger records them as unpriced).
    """
    if str(provider or "").strip().lower() in ZERO_COST_PROVIDERS:
        return 0.0

    pricing = find_model_pricing(model)
    if pricing is None:
        return 0.0

    safe_input = max(0, int(input_tokens or 0))
    safe_output = max(0, int(output_tokens or 0))
    safe_cached = min(max(0, int(cached_tokens or 0)), safe_input)
    safe_reasoning = max(0, int(reasoning_tokens or 0))
    uncached_input = safe_input - safe_cached

    cost = (
        uncached_input * pricing.input_per_million
        + safe_cached * pricing.effective_cache_read()
        + safe_output * pricing.output_per_million
        + safe_reasoning * pricing.effective_reasoning()
    ) / 1_000_000.0
    return round(cost, 10)
