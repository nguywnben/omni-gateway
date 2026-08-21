"""Sanitized routing decisions shared by execution, diagnostics, and telemetry."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class RouteCandidate:
    """One credential considered during a routing decision."""

    filename: str
    provider_id: str
    state: str
    reason: str = ""
    support_level: int = 0
    in_flight: int = 0
    consecutive_failures: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RouteDecision:
    """A secret-free record explaining one credential selection attempt."""

    mode: str
    requested_model: str
    required_provider: str
    routing_strategy: str
    selected_filename: Optional[str]
    selected_provider: Optional[str]
    candidates: tuple[RouteCandidate, ...]
    created_at: float
    request_id: str = ""

    @property
    def selected(self) -> bool:
        return self.selected_filename is not None

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "requested_model": self.requested_model,
            "required_provider": self.required_provider,
            "routing_strategy": self.routing_strategy,
            "selected_filename": self.selected_filename,
            "selected_provider": self.selected_provider,
            "selected": self.selected,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "created_at": self.created_at,
            "request_id": self.request_id,
        }
