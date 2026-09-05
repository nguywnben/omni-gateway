from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.credential_manager import _CredentialManagerSingleton
from core.ha_runtime import HaRuntimeLifecycle, HaRuntimeState
from core.ha_runtime_policy import HaRuntimePolicy
from core.state_store import InMemoryStateStore


class HaRuntimeLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_standalone_injects_one_store_into_every_runtime_consumer(self) -> None:
        singleton = _CredentialManagerSingleton()
        lifecycle = HaRuntimeLifecycle(
            policy=HaRuntimePolicy.from_environment({}),
            standalone_store_factory=InMemoryStateStore,
        )

        with (
            patch("core.ha_runtime.credential_manager", singleton),
            patch("core.ha_runtime.configure_governance_coordination") as governance,
            patch("core.ha_runtime.configure_authentication_attempt_service") as attempts,
            patch("core.ha_runtime.configure_oidc_transaction_coordination") as oidc,
            patch("core.ha_runtime.configure_device_authorization_service") as device_auth,
            patch("core.ha_runtime.configure_credential_batch_coordination_service") as batch,
            patch("core.ha_runtime.configure_provider_authorization_service") as provider_auth,
            patch("core.ha_runtime.virtual_key_manager.configure_coordination") as quota,
            patch("core.ha_runtime.response_cache_coordinator.configure_coordination") as cache,
        ):
            await lifecycle.start(storage=object())

        service = lifecycle.coordination_service
        self.assertIsNotNone(service)
        self.assertIs(lifecycle.state, HaRuntimeState.STANDALONE_READY)
        self.assertIs(singleton._routing_coordination._store, service)
        governance.assert_called_once_with(singleton._routing_coordination)
        attempts.assert_called_once()
        self.assertIs(attempts.call_args.args[0]._coordination, service)
        oidc.assert_called_once_with(service, fencing_epoch=1)
        device_auth.assert_called_once()
        self.assertIs(device_auth.call_args.args[0]._coordination, service)
        batch.assert_called_once()
        self.assertIs(batch.call_args.args[0]._coordination, service)
        provider_auth.assert_called_once()
        self.assertIs(provider_auth.call_args.args[0]._coordination, service)
        quota.assert_called_once_with(service, fencing_epoch=1)
        cache.assert_called_once_with(singleton._routing_coordination)
        self.assertEqual(lifecycle.session_initialization_kwargs["fencing_epoch"], 1)
        self.assertIs(lifecycle.session_initialization_kwargs["coordination"], service)
        self.assertTrue(await lifecycle.check_ready())

        await lifecycle.close()
        self.assertIs(lifecycle.state, HaRuntimeState.CLOSED)
        self.assertIsNone(singleton._routing_coordination)

    async def test_coordinated_start_never_injects_before_binding_and_activation_verify(
        self,
    ) -> None:
        coordinated = HaRuntimePolicy.from_environment(
            {
                "OMNI_RUNTIME_MODE": "coordinated",
                "WORKERS": "1",
                "OMNI_REPLICA_COUNT": "1",
                "POSTGRESQL_URI": "postgresql://database/omni",
                "REDIS_URL": "redis://redis/0",
                "OMNI_COORDINATION_NAMESPACE": "production-east",
                "OMNI_DEPLOYMENT_ID": "gateway-east-01",
                "OMNI_COORDINATION_KEY": "a2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2s=",
                "OMNI_COORDINATION_EPOCH": "1",
            }
        )
        store = InMemoryStateStore()
        lifecycle = HaRuntimeLifecycle(
            policy=coordinated,
            coordinated_store_factory=lambda _policy: store,
            activation_verifier=lambda _record: False,
        )
        binding = AsyncMock()
        binding.activation_record = "act_" + ("a" * 32)

        with (
            patch("core.ha_runtime.CoordinationBindingManager") as manager_type,
            patch("core.ha_runtime.configure_governance_coordination") as governance,
        ):
            manager_type.return_value.verify = AsyncMock(return_value=binding)
            with self.assertRaisesRegex(RuntimeError, "activation record"):
                await lifecycle.start(storage=object())

        governance.assert_not_called()
        self.assertIs(lifecycle.state, HaRuntimeState.UNAVAILABLE)
        self.assertIsNone(lifecycle.coordination_service)

    async def test_dependency_failure_closes_readiness_until_a_successful_probe(self) -> None:
        lifecycle = HaRuntimeLifecycle(policy=HaRuntimePolicy.from_environment({}))
        with (
            patch(
                "core.ha_runtime.credential_manager.configure_routing_coordination", new=AsyncMock()
            ),
            patch("core.ha_runtime.configure_governance_coordination"),
            patch("core.ha_runtime.configure_authentication_attempt_service"),
            patch("core.ha_runtime.configure_oidc_transaction_coordination"),
            patch("core.ha_runtime.configure_device_authorization_service"),
            patch("core.ha_runtime.configure_credential_batch_coordination_service"),
            patch("core.ha_runtime.configure_provider_authorization_service"),
            patch("core.ha_runtime.virtual_key_manager.configure_coordination"),
            patch("core.ha_runtime.response_cache_coordinator.configure_coordination"),
        ):
            await lifecycle.start(storage=object())
        service = lifecycle.coordination_service
        service.read_coordination_time = AsyncMock(side_effect=RuntimeError("secret endpoint"))

        self.assertFalse(await lifecycle.check_ready())
        self.assertEqual(lifecycle.health_snapshot()["failure_code"], "dependency_unavailable")
        service.read_coordination_time = AsyncMock(return_value=object())
        self.assertTrue(await lifecycle.check_ready())
        self.assertEqual(lifecycle.health_snapshot()["failure_code"], "")

    async def test_coordinated_dependency_failure_latches_until_process_restart(self) -> None:
        coordinated = HaRuntimePolicy.from_environment(
            {
                "OMNI_RUNTIME_MODE": "coordinated",
                "WORKERS": "1",
                "OMNI_REPLICA_COUNT": "1",
                "POSTGRESQL_URI": "postgresql://database/omni",
                "REDIS_URL": "redis://redis/0",
                "OMNI_COORDINATION_NAMESPACE": "production-east",
                "OMNI_DEPLOYMENT_ID": "gateway-east-01",
                "OMNI_COORDINATION_KEY": "a2tra2tra2tra2tra2tra2tra2tra2tra2tra2tra2s=",
                "OMNI_COORDINATION_EPOCH": "1",
            }
        )
        store = InMemoryStateStore()
        lifecycle = HaRuntimeLifecycle(
            policy=coordinated,
            coordinated_store_factory=lambda _policy: store,
            activation_verifier=lambda _record: True,
        )
        binding = AsyncMock()
        binding.activation_record = "act_" + ("a" * 32)
        manager = AsyncMock()
        manager.verify = AsyncMock(return_value=binding)

        with (
            patch("core.ha_runtime.CoordinationBindingManager", return_value=manager),
            patch(
                "core.ha_runtime.credential_manager.configure_routing_coordination",
                new=AsyncMock(),
            ),
            patch("core.ha_runtime.configure_governance_coordination"),
            patch("core.ha_runtime.configure_authentication_attempt_service"),
            patch("core.ha_runtime.configure_oidc_transaction_coordination"),
            patch("core.ha_runtime.configure_device_authorization_service"),
            patch("core.ha_runtime.configure_credential_batch_coordination_service"),
            patch("core.ha_runtime.configure_provider_authorization_service"),
            patch("core.ha_runtime.virtual_key_manager.configure_coordination"),
            patch("core.ha_runtime.response_cache_coordinator.configure_coordination"),
            patch("core.ha_runtime.configure_primary_session_coordinator"),
        ):
            await lifecycle.start(storage=object())
            self.assertTrue(await lifecycle.check_ready())
            manager.verify.side_effect = RuntimeError("redis credential leaked-secret")
            self.assertFalse(await lifecycle.check_ready())
            failed_probe_count = manager.verify.await_count
            manager.verify.side_effect = None
            manager.verify.return_value = binding
            self.assertFalse(await lifecycle.check_ready())

        snapshot = lifecycle.health_snapshot()
        self.assertEqual(manager.verify.await_count, failed_probe_count)
        self.assertIs(lifecycle.state, HaRuntimeState.UNAVAILABLE)
        self.assertTrue(snapshot["recovery_latched"])
        self.assertEqual(snapshot["recovery_reason"], "dependency_unavailable")
        self.assertNotIn("credential", repr(snapshot))
        self.assertNotIn("leaked-secret", repr(snapshot))


if __name__ == "__main__":
    unittest.main()
