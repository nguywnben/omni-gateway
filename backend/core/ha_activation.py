"""Exact coordinated topology activation allowlist, populated only by W4.19 evidence."""

from __future__ import annotations

from typing import Final

SUPPORTED_HA_ACTIVATION_RECORDS: Final = frozenset()


def verify_ha_activation_record(record: str) -> bool:
    """Return true only for an evidence record compiled into this release."""

    return isinstance(record, str) and record in SUPPORTED_HA_ACTIVATION_RECORDS
