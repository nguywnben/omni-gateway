"""Production R1 isolation contract for unfinished coordinated-runtime work."""

from __future__ import annotations

import base64
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from core.ha_runtime import close_ha_runtime, initialize_ha_runtime

from backend.tests.suite_manifest import (
    EXPERIMENTAL_HA_MODULES,
    core_test_modules,
    validate_suite_partition,
)


def _coordinated_environment(**overrides: str) -> dict[str, str]:
    environment = {
        "OMNI_RUNTIME_MODE": "coordinated",
        "WORKERS": "1",
        "OMNI_REPLICA_COUNT": "1",
        "POSTGRESQL_URI": "postgresql://database/omni",
        "REDIS_URL": "redis://redis/0",
        "OMNI_COORDINATION_NAMESPACE": "experimental-r1",
        "OMNI_DEPLOYMENT_ID": "gateway-test-01",
        "OMNI_COORDINATION_KEY": base64.urlsafe_b64encode(b"k" * 32).decode("ascii"),
        "OMNI_COORDINATION_EPOCH": "1",
    }
    environment.update(overrides)
    return environment


class ExperimentalHaRuntimeIsolationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self) -> None:
        await close_ha_runtime()

    async def test_default_start_selects_standalone_without_redis(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            lifecycle = await initialize_ha_runtime(storage=object())

        self.assertEqual(lifecycle.policy.mode, "standalone")
        self.assertEqual((lifecycle.policy.workers, lifecycle.policy.replicas), (1, 1))
        self.assertIsNone(lifecycle.policy.redis_url)
        self.assertEqual(lifecycle.state, "standalone_ready")

    async def test_normal_start_rejects_coordinated_mode_before_storage_or_redis(self) -> None:
        storage_factory = AsyncMock()
        with (
            patch.dict(os.environ, _coordinated_environment(), clear=True),
            patch("core.storage_adapter.get_storage_adapter", storage_factory),
        ):
            with self.assertRaisesRegex(RuntimeError, "experimental.*disabled"):
                await initialize_ha_runtime()

        storage_factory.assert_not_awaited()

    async def test_explicit_experimental_start_stays_closed_without_activation_record(self) -> None:
        storage_factory = AsyncMock()
        environment = _coordinated_environment(OMNI_EXPERIMENTAL_COORDINATION="true")
        with (
            patch.dict(os.environ, environment, clear=True),
            patch("core.storage_adapter.get_storage_adapter", storage_factory),
        ):
            with self.assertRaisesRegex(RuntimeError, "no accepted activation record"):
                await initialize_ha_runtime()

        storage_factory.assert_not_awaited()


class ExperimentalHaSuiteIsolationTests(unittest.TestCase):
    def test_suite_partition_is_complete_and_keeps_safety_guards_in_core(self) -> None:
        validate_suite_partition()
        core = set(core_test_modules())

        self.assertIn("test_ha_topology_evidence_runner", EXPERIMENTAL_HA_MODULES)
        self.assertIn("test_coordination_redis_live", EXPERIMENTAL_HA_MODULES)
        self.assertIn("test_ha_runtime_policy", core)
        self.assertIn("test_ha_runtime_lifecycle", core)
        self.assertTrue(core.isdisjoint(EXPERIMENTAL_HA_MODULES))

    def test_experimental_suite_is_independently_listable(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "backend.tests", "--suite", "experimental-ha", "--list"],
            cwd=ROOT,
            capture_output=True,
            check=False,
            text=True,
            timeout=15,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("suite=experimental-ha", completed.stdout)
        self.assertIn("test_ha_topology_evidence_runner", completed.stdout)
        self.assertNotIn("test_ha_runtime_policy\n", completed.stdout)

    def test_default_compose_does_not_request_experimental_dependencies(self) -> None:
        compose = (ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn("OMNI_RUNTIME_MODE=${OMNI_RUNTIME_MODE:-standalone}", compose)
        for name in (
            "REDIS_URL",
            "OMNI_COORDINATION_NAMESPACE",
            "OMNI_DEPLOYMENT_ID",
            "OMNI_COORDINATION_KEY",
            "OMNI_COORDINATION_EPOCH",
            "OMNI_EXPERIMENTAL_COORDINATION",
        ):
            self.assertNotIn(name, compose)

    def test_ci_audits_partition_and_runs_only_core_suite(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

        self.assertIn("python -m backend.tests --audit", workflow)
        self.assertIn("python -m backend.tests --suite core", workflow)
        self.assertNotIn("python -m backend.tests --suite experimental-ha", workflow)

    def test_release_checklist_keeps_experimental_ha_out_of_required_gates(self) -> None:
        checklist = (ROOT / "docs" / "release-checklist.md").read_text(encoding="utf-8")

        self.assertIn("python tools/quality_gate.py release", checklist)
        automated_gates = checklist.split("## Manual Provider Checks", 1)[0]
        self.assertNotIn("python -m backend.tests --suite experimental-ha", automated_gates)


if __name__ == "__main__":
    unittest.main()
