"""Lightweight token estimation for request budgeting and usage hints."""

from __future__ import annotations

import math
from typing import Any, Dict


def _string_tokens(value: str) -> int:
    return max(1, math.ceil(len(value.encode("utf-8")) / 4))


def _estimate_value(value: Any) -> int:
    if isinstance(value, str):
        return _string_tokens(value)
    if isinstance(value, dict):
        image_cost = 300 if value.get("type") == "image" or "inlineData" in value else 0
        return image_cost + 2 + sum(
            _string_tokens(str(key)) + _estimate_value(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return 1 + len(value) + sum(_estimate_value(item) for item in value)
    if value is None:
        return 0
    return 1


def estimate_input_tokens(payload: Dict[str, Any]) -> int:
    """Estimate serialized prompt tokens without a provider tokenizer dependency."""
    return max(1, _estimate_value(payload))
