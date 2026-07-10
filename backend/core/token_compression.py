"""Bounded conversation-history compression for Gemini request payloads."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict

from core.token_estimator import estimate_input_tokens


@dataclass(frozen=True)
class CompressionSettings:
    enabled: bool = True
    threshold_tokens: int = 32_000
    target_tokens: int = 24_000
    min_recent_turns: int = 4

    def __post_init__(self) -> None:
        if self.threshold_tokens < 128:
            raise ValueError("Compression threshold must be at least 128 tokens.")
        if self.target_tokens < 64:
            raise ValueError("Compression target must be at least 64 tokens.")
        if self.target_tokens >= self.threshold_tokens:
            raise ValueError("Compression target must be lower than the threshold.")
        if self.min_recent_turns < 1:
            raise ValueError("At least one recent turn must be preserved.")


@dataclass(frozen=True)
class CompressionResult:
    request: Dict[str, Any]
    original_estimated_tokens: int
    final_estimated_tokens: int
    removed_contents: int
    applied: bool
    reason: str

    @property
    def estimated_tokens_saved(self) -> int:
        return max(0, self.original_estimated_tokens - self.final_estimated_tokens)

    def as_metrics(self) -> Dict[str, int]:
        return {
            "estimated_input_tokens": self.final_estimated_tokens,
            "estimated_tokens_saved": self.estimated_tokens_saved,
            "compressed_messages": self.removed_contents,
        }


def _contains_function_response(content: Any) -> bool:
    if not isinstance(content, dict):
        return False
    parts = content.get("parts")
    if not isinstance(parts, list):
        return False
    return any(
        isinstance(part, dict)
        and ("functionResponse" in part or "function_response" in part)
        for part in parts
    )


def _is_safe_turn_start(content: Any) -> bool:
    return (
        isinstance(content, dict)
        and content.get("role") == "user"
        and not _contains_function_response(content)
    )


def _unchanged_result(
    request: Dict[str, Any], estimated_tokens: int, reason: str
) -> CompressionResult:
    return CompressionResult(
        request=request,
        original_estimated_tokens=estimated_tokens,
        final_estimated_tokens=estimated_tokens,
        removed_contents=0,
        applied=False,
        reason=reason,
    )


def compress_gemini_request(
    request: Dict[str, Any], settings: CompressionSettings
) -> CompressionResult:
    """Prune an old conversation prefix while preserving recent complete turns."""
    original_estimate = estimate_input_tokens(request)
    if not settings.enabled:
        return _unchanged_result(request, original_estimate, "disabled")
    if original_estimate <= settings.threshold_tokens:
        return _unchanged_result(request, original_estimate, "below_threshold")

    contents = request.get("contents")
    if not isinstance(contents, list) or len(contents) < 2:
        return _unchanged_result(request, original_estimate, "no_history")

    safe_starts = [
        index for index, content in enumerate(contents) if _is_safe_turn_start(content)
    ]
    if len(safe_starts) <= settings.min_recent_turns:
        return _unchanged_result(request, original_estimate, "minimum_history")

    latest_allowed_cut = safe_starts[-settings.min_recent_turns]
    cut_candidates = [
        index for index in safe_starts[1:] if index <= latest_allowed_cut
    ]
    if not cut_candidates:
        return _unchanged_result(request, original_estimate, "no_safe_boundary")

    estimate_cache: Dict[int, int] = {}

    def estimate_after_cut(cut_index: int) -> int:
        if cut_index not in estimate_cache:
            candidate = dict(request)
            candidate["contents"] = contents[cut_index:]
            estimate_cache[cut_index] = estimate_input_tokens(candidate)
        return estimate_cache[cut_index]

    selected_cut = cut_candidates[-1]
    selected_estimate = estimate_after_cut(selected_cut)
    low = 0
    high = len(cut_candidates) - 1
    while low <= high:
        middle = (low + high) // 2
        cut_index = cut_candidates[middle]
        candidate_estimate = estimate_after_cut(cut_index)
        if candidate_estimate <= settings.target_tokens:
            selected_cut = cut_index
            selected_estimate = candidate_estimate
            high = middle - 1
        else:
            low = middle + 1

    if selected_estimate >= original_estimate:
        return _unchanged_result(request, original_estimate, "no_savings")

    selected_source = dict(request)
    selected_source["contents"] = contents[selected_cut:]
    selected_request = copy.deepcopy(selected_source)

    return CompressionResult(
        request=selected_request,
        original_estimated_tokens=original_estimate,
        final_estimated_tokens=selected_estimate,
        removed_contents=selected_cut,
        applied=True,
        reason=(
            "target_reached"
            if selected_estimate <= settings.target_tokens
            else "minimum_history_reached"
        ),
    )
