"""Fail-closed activation boundary for the experimental coordinated runtime."""

from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Final

SUPPORTED_HA_ACTIVATION_RECORDS: Final = frozenset()
EXPERIMENTAL_COORDINATION_ENV: Final = "OMNI_EXPERIMENTAL_COORDINATION"


def verify_ha_activation_record(record: str) -> bool:
    """Return true only for an evidence record compiled into this release."""

    return isinstance(record, str) and record in SUPPORTED_HA_ACTIVATION_RECORDS


def require_coordinated_runtime_activation(
    mode: str,
    environment: Mapping[str, str] | None = None,
) -> None:
    """Reject normal coordinated startup before opening storage or Redis connections."""

    if str(mode) != "coordinated":
        return
    selected = os.environ if environment is None else environment
    opt_in = selected.get(EXPERIMENTAL_COORDINATION_ENV, "")
    if not isinstance(opt_in, str) or opt_in.strip().lower() != "true":
        raise RuntimeError("Coordinated mode is experimental and disabled for normal startup.")
    if not SUPPORTED_HA_ACTIVATION_RECORDS:
        raise RuntimeError(
            "Experimental coordinated startup has no accepted activation record in this build."
        )
