"""Isolated external HA evidence tooling; never production activation authority."""

import sys
from pathlib import Path

_REPOSITORY_BACKEND = Path(__file__).resolve().parents[2] / "backend"
if _REPOSITORY_BACKEND.is_dir() and str(_REPOSITORY_BACKEND) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_BACKEND))

from .contract import (  # noqa: E402
    REQUIRED_SCENARIOS,
    CandidateTopology,
    CandidateVerifier,
    CorrectnessCounters,
    EvidenceVerificationError,
    RunManifest,
    ScenarioResult,
    verify_run_manifest,
)

__all__ = (
    "REQUIRED_SCENARIOS",
    "CandidateTopology",
    "CandidateVerifier",
    "CorrectnessCounters",
    "EvidenceVerificationError",
    "RunManifest",
    "ScenarioResult",
    "verify_run_manifest",
)
