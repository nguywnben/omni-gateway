from __future__ import annotations

import base64
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.ha_runtime_policy import HaRuntimePolicy, RuntimeMode


def coordinated_env(**overrides: str) -> dict[str, str]:
    values = {
        "OMNI_RUNTIME_MODE": "coordinated",
        "WORKERS": "1",
        "OMNI_REPLICA_COUNT": "1",
        "POSTGRESQL_URI": "postgresql://user:secret@database/omni",
        "REDIS_URL": "rediss://user:secret@redis.example/0",
        "OMNI_COORDINATION_NAMESPACE": "production-east",
        "OMNI_DEPLOYMENT_ID": "gateway-east-01",
        "OMNI_COORDINATION_KEY": base64.urlsafe_b64encode(b"k" * 32).decode("ascii"),
        "OMNI_COORDINATION_EPOCH": "7",
    }
    values.update(overrides)
    return values


class HaRuntimePolicyTests(unittest.TestCase):
    def test_empty_environment_is_safe_standalone(self) -> None:
        policy = HaRuntimePolicy.from_environment({})

        self.assertIs(policy.mode, RuntimeMode.STANDALONE)
        self.assertEqual((policy.workers, policy.replicas), (1, 1))
        self.assertEqual(policy.durable_backend, "sqlite")
        self.assertIsNone(policy.coordination_key)

    def test_standalone_accepts_one_selected_external_backend_and_legacy_redis_cache(self) -> None:
        policy = HaRuntimePolicy.from_environment(
            {
                "MONGODB_URI": "mongodb://database/omni",
                "REDIS_URL": "redis://cache/0",
            }
        )

        self.assertEqual(policy.durable_backend, "mongodb")
        self.assertIsNone(policy.coordination_namespace)

    def test_coordinated_policy_is_closed_and_secret_safe(self) -> None:
        policy = HaRuntimePolicy.from_environment(coordinated_env())

        self.assertIs(policy.mode, RuntimeMode.COORDINATED)
        self.assertEqual(policy.durable_backend, "postgresql")
        self.assertEqual(policy.fencing_epoch, 7)
        self.assertEqual(policy.coordination_key, b"k" * 32)
        rendered = repr(policy)
        self.assertNotIn("secret", rendered)
        self.assertNotIn("rediss://", rendered)
        self.assertNotIn(coordinated_env()["OMNI_COORDINATION_KEY"], rendered)

    def test_unknown_and_contradictory_configuration_is_rejected(self) -> None:
        invalid = [
            {"OMNI_RUNTIME_MODE": "distributed"},
            {"WORKERS": "2"},
            {"OMNI_REPLICA_COUNT": "0"},
            {"POSTGRESQL_URI": "postgres://one", "MONGODB_URI": "mongodb://two"},
            {"OMNI_COORDINATION_NAMESPACE": "unexpected"},
            coordinated_env(REDIS_URL=""),
            coordinated_env(POSTGRESQL_URI="", MONGODB_URI=""),
            coordinated_env(POSTGRESQL_URI="postgres://one", MONGODB_URI="mongodb://two"),
            coordinated_env(WORKERS="2"),
            coordinated_env(OMNI_REPLICA_COUNT="2"),
            coordinated_env(OMNI_COORDINATION_NAMESPACE="UPPER_CASE"),
            coordinated_env(OMNI_DEPLOYMENT_ID="short"),
            coordinated_env(OMNI_COORDINATION_EPOCH="0"),
            coordinated_env(OMNI_COORDINATION_EPOCH="true"),
            coordinated_env(OMNI_COORDINATION_KEY="not-base64!"),
            coordinated_env(
                OMNI_COORDINATION_KEY=base64.urlsafe_b64encode(b"short").decode("ascii")
            ),
            coordinated_env(REDIS_URL="http://redis.example"),
            coordinated_env(REDIS_URL="redis://redis.example/0#fragment"),
        ]

        for values in invalid:
            with self.subTest(values=sorted(values)):
                with self.assertRaises(RuntimeError):
                    HaRuntimePolicy.from_environment(values)


if __name__ == "__main__":
    unittest.main()
