"""Explicit production and experimental backend test-suite partition."""

from __future__ import annotations

import unittest
from pathlib import Path

TESTS_DIRECTORY = Path(__file__).resolve().parent

CORE_HA_SAFETY_MODULES = frozenset(
    {
        "test_ha_runtime_lifecycle",
        "test_ha_runtime_policy",
    }
)

EXPERIMENTAL_HA_MODULES = frozenset(
    {
        "test_coordination_redis_live",
        "test_ha_admin",
        "test_ha_coordination_binding",
        "test_ha_deployment_assets",
        "test_ha_evidence",
        "test_ha_operator",
        "test_ha_reconciliation",
        "test_ha_topology_evidence_contract",
        "test_ha_topology_evidence_isolation",
        "test_ha_topology_evidence_live",
        "test_ha_topology_evidence_runner",
        "test_routing_coordination_redis_live",
        "test_security_coordination_redis_live",
    }
)


def all_test_modules() -> tuple[str, ...]:
    """Return every discoverable backend unittest module in deterministic order."""

    return tuple(sorted(path.stem for path in TESTS_DIRECTORY.glob("test_*.py")))


def core_test_modules() -> tuple[str, ...]:
    """Return the production R1 suite, excluding experimental HA evidence."""

    return tuple(name for name in all_test_modules() if name not in EXPERIMENTAL_HA_MODULES)


def experimental_ha_test_modules() -> tuple[str, ...]:
    """Return the independently runnable coordinated-runtime evidence suite."""

    return tuple(sorted(EXPERIMENTAL_HA_MODULES))


def validate_suite_partition() -> None:
    """Fail when an HA/live-Redis module bypasses the explicit partition."""

    available = set(all_test_modules())
    missing = sorted(EXPERIMENTAL_HA_MODULES - available)
    expected_experimental = {
        name
        for name in available
        if (name.startswith("test_ha_") and name not in CORE_HA_SAFETY_MODULES)
        or name.endswith("_redis_live")
    }
    unclassified = sorted(expected_experimental - EXPERIMENTAL_HA_MODULES)
    incorrectly_classified = sorted(EXPERIMENTAL_HA_MODULES - expected_experimental)
    if missing or unclassified or incorrectly_classified:
        raise RuntimeError(
            "Invalid backend test-suite partition: "
            f"missing={missing}, unclassified={unclassified}, "
            f"incorrectly_classified={incorrectly_classified}."
        )


def build_suite(name: str) -> unittest.TestSuite:
    """Load one named suite without importing modules assigned to another suite."""

    validate_suite_partition()
    if name == "core":
        modules = core_test_modules()
    elif name == "experimental-ha":
        modules = experimental_ha_test_modules()
    elif name == "all":
        modules = all_test_modules()
    else:
        raise ValueError(f"Unknown backend test suite: {name}")
    loader = unittest.defaultTestLoader
    return unittest.TestSuite(
        loader.loadTestsFromName(f"backend.tests.{module}") for module in modules
    )
