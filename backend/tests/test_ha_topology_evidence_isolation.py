from __future__ import annotations

import base64
import dataclasses
import sys
import unittest
from contextlib import asynccontextmanager
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.ha_activation import SUPPORTED_HA_ACTIVATION_RECORDS, verify_ha_activation_record
from core.ha_runtime_policy import HaRuntimePolicy

from backend.tests.test_ha_topology_evidence_contract import candidate
from tools.ha_topology_evidence.admin import CandidateAdmin, experimental_policy
from tools.ha_topology_evidence.app import candidate_lifespan
from tools.ha_topology_evidence.contract import CandidateVerifier, EvidenceVerificationError

ROOT = Path(__file__).resolve().parents[2]


def coordinated_environment() -> dict[str, str]:
    return {
        "OMNI_RUNTIME_MODE": "coordinated",
        "WORKERS": "1",
        "OMNI_REPLICA_COUNT": "2",
        "POSTGRESQL_URI": "postgresql://database/omni",
        "REDIS_URL": "redis://redis/0",
        "OMNI_COORDINATION_NAMESPACE": "evidence-only",
        "OMNI_DEPLOYMENT_ID": "evidence-gateway-01",
        "OMNI_COORDINATION_KEY": base64.urlsafe_b64encode(b"k" * 32).decode(),
        "OMNI_COORDINATION_EPOCH": "1",
    }


class CandidateIsolationTests(unittest.TestCase):
    def test_production_policy_and_verifier_stay_closed_to_candidate(self) -> None:
        topology = candidate()
        with self.assertRaisesRegex(RuntimeError, "(?i)replica"):
            HaRuntimePolicy.from_environment(coordinated_environment())
        self.assertEqual(SUPPORTED_HA_ACTIVATION_RECORDS, frozenset())
        self.assertFalse(verify_ha_activation_record(topology.candidate_id))

    def test_verifier_rejects_any_observed_source_image_or_manifest_mismatch(self) -> None:
        topology = candidate()
        exact = CandidateVerifier.exact(topology, replica_count=2)
        for field, value in (
            ("source_revision", "9" * 40),
            ("source_tree_digest", "9" * 64),
            ("production_image", "sha256:" + ("9" * 64)),
            ("evidence_image", "sha256:" + ("8" * 64)),
            ("evidence_launcher_digest", "9" * 64),
            ("migration_manifest_checksum", "9" * 64),
            ("redis_primary_image", "redis:8.2.1@sha256:" + ("9" * 64)),
            ("redis_standby_image", "redis:8.2.1@sha256:" + ("9" * 64)),
            ("postgresql_image", "postgres:17.6@sha256:" + ("9" * 64)),
            ("workers_per_replica", 2),
        ):
            with self.subTest(field=field):
                self.assertFalse(
                    dataclasses.replace(exact, **{field: value})(topology.candidate_id)
                )

    def test_evidence_policy_derives_only_the_frozen_replica_count(self) -> None:
        topology = candidate()
        environment = coordinated_environment()
        before = dict(environment)

        policy = experimental_policy(environment, topology, replica_count=2)

        self.assertEqual(
            (policy.workers, policy.replicas, policy.durable_backend),
            (1, 2, "postgresql"),
        )
        self.assertEqual(environment, before)

    def test_activated_candidate_must_use_the_production_gate(self) -> None:
        predecessor = candidate()
        topology = dataclasses.replace(
            predecessor,
            activation_record=predecessor.candidate_id,
        )
        verifier = CandidateVerifier.exact(topology, replica_count=2)

        with self.assertRaisesRegex(RuntimeError, "replica|OMNI_REPLICA_COUNT"):
            experimental_policy(coordinated_environment(), topology, replica_count=2)

        preactivation_policy = experimental_policy(
            coordinated_environment(), predecessor, replica_count=2
        )
        with self.assertRaisesRegex(EvidenceVerificationError, "activation record"):
            CandidateAdmin(preactivation_policy, object(), object(), verifier)

    def test_no_environment_bypass_or_production_image_copy_exists(self) -> None:
        sources = "\n".join(
            path.read_text(encoding="utf-8") for path in (ROOT / "backend" / "core").rglob("*.py")
        )
        self.assertNotIn("OMNI_ALLOW_HA_TEST", sources)
        self.assertNotIn("OMNI_HA_CANDIDATE", sources)
        dockerfile = (ROOT / "deploy" / "Dockerfile").read_text(encoding="utf-8")
        self.assertNotIn("tools/ha_topology_evidence", dockerfile)
        self.assertNotIn("COPY tools", dockerfile)


class CandidateApplicationLifecycleTests(unittest.IsolatedAsyncioTestCase):
    def test_evidence_server_uses_the_locked_production_asgi_runtime(self) -> None:
        source = (ROOT / "tools" / "ha_topology_evidence" / "app.py").read_text(encoding="utf-8")
        self.assertIn("from hypercorn.asyncio import serve", source)
        self.assertNotIn("import uvicorn", source)

    async def test_original_lifespan_owns_exactly_one_candidate_start_and_close(self) -> None:
        from tools.ha_topology_evidence import app as evidence_app

        topology = candidate()
        verifier = CandidateVerifier.exact(topology, replica_count=2)
        environment = coordinated_environment()
        installed = None
        starts = 0
        closes = 0
        storage_calls = 0

        class Lifecycle:
            def __init__(self, *, policy, activation_verifier):
                self.policy = policy
                self.verifier = activation_verifier

            async def start(self, *, storage):
                nonlocal starts
                starts += 1

            async def close(self):
                nonlocal closes
                closes += 1

        def get_lifecycle():
            return installed

        def set_lifecycle(value):
            nonlocal installed
            installed = value

        async def close_lifecycle():
            nonlocal installed
            current, installed = installed, None
            if current is not None:
                await current.close()

        async def storage_factory():
            nonlocal storage_calls
            storage_calls += 1
            return object()

        @asynccontextmanager
        async def original_lifespan(_application):
            self.assertIsNotNone(installed)
            yield
            await close_lifecycle()

        with (
            patch.object(evidence_app, "HaRuntimeLifecycle", Lifecycle),
            patch.object(evidence_app, "get_runtime_lifecycle", get_lifecycle),
            patch.object(evidence_app, "set_runtime_lifecycle", set_lifecycle),
            patch.object(evidence_app, "close_ha_runtime", close_lifecycle),
        ):
            async with candidate_lifespan(
                object(),
                candidate=topology,
                verifier=verifier,
                environment=environment,
                replica_count=2,
                original_lifespan=original_lifespan,
                storage_factory=storage_factory,
            ):
                self.assertEqual(installed.policy.replicas, 2)

        self.assertEqual((storage_calls, starts, closes), (1, 1, 1))
        self.assertIsNone(installed)


if __name__ == "__main__":
    unittest.main()
