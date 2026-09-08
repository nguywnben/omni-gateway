"""Run the backend test suite with repository-safe defaults."""

from __future__ import annotations

import argparse
import sys
import unittest

from backend.tests.suite_manifest import (
    all_test_modules,
    build_suite,
    core_test_modules,
    experimental_ha_test_modules,
    validate_suite_partition,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a named Omni Gateway backend test suite.")
    parser.add_argument(
        "--suite",
        choices=("core", "experimental-ha", "all"),
        default="core",
        help="Suite to run. The default production gate excludes experimental HA evidence.",
    )
    parser.add_argument("--list", action="store_true", help="List modules without importing them.")
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Validate that every HA/live-Redis module has an explicit suite assignment.",
    )
    return parser


def _modules_for_suite(name: str) -> tuple[str, ...]:
    if name == "core":
        return core_test_modules()
    if name == "experimental-ha":
        return experimental_ha_test_modules()
    return all_test_modules()


def main(arguments: list[str] | None = None) -> int:
    options = _parser().parse_args(arguments)
    validate_suite_partition()
    modules = _modules_for_suite(options.suite)
    if options.audit:
        print(
            "Backend test partition valid: "
            f"core={len(core_test_modules())}, "
            f"experimental-ha={len(experimental_ha_test_modules())}."
        )
        if not options.list:
            return 0
    if options.list:
        print(f"suite={options.suite}; modules={len(modules)}")
        print("\n".join(modules))
        return 0
    suite = build_suite(options.suite)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
