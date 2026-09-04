from __future__ import annotations

import base64
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.coordination import EpochState
from core.ha_coordination_binding import CoordinationBindingManager
from core.ha_operator import HaRuntimeOperator
from core.ha_runtime_policy import HaRuntimePolicy
from core.state_store import InMemoryStateStore


class _Storage:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    async def get_config(self, key: str, default=None):
        return self.values.get(key, default)

    async def set_config(self, key: str, value: object) -> bool:
        self.values[key] = value
        return True


def policy(epoch: int = 1) -> HaRuntimePolicy:
    return HaRuntimePolicy.from_environment(
        {
            "OMNI_RUNTIME_MODE": "coordinated",
            "WORKERS": "1",
            "OMNI_REPLICA_COUNT": "1",
            "POSTGRESQL_URI": "postgresql://database/omni",
            "REDIS_URL": "redis://redis/0",
            "OMNI_COORDINATION_NAMESPACE": "production-east",
            "OMNI_DEPLOYMENT_ID": "gateway-east-01",
            "OMNI_COORDINATION_KEY": base64.urlsafe_b64encode(b"k" * 32).decode("ascii"),
            "OMNI_COORDINATION_EPOCH": str(epoch),
        }
    )


class HaRuntimeOperatorTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.storage = _Storage()
        self.store = InMemoryStateStore()
        manager = CoordinationBindingManager(
            self.storage,
            self.store,
            activation_verifier=lambda _record: True,
        )
        await manager.bootstrap(policy(), activation_record="act_" + ("a" * 32), apply=True)

    async def test_full_drain_epoch_reconcile_ready_flow_is_bounded_and_idempotent(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        dry = await operator.drain(apply=False)
        self.assertFalse(dry["applied"])
        self.assertIsNone(await self.store.get(operator.DRAIN_KEY))

        drained = await operator.drain(apply=True)
        self.assertTrue(drained["applied"])
        self.assertEqual((await operator.status())["state"], "draining")

        preview = await operator.advance_epoch("epoch-op-00000001", apply=False)
        self.assertEqual(preview["next_epoch"], 2)
        self.assertEqual((await self.store.read_epoch()).epoch, 1)
        advanced = await operator.advance_epoch("epoch-op-00000001", apply=True)
        self.assertEqual(advanced["epoch"], 2)
        repeated_advance = await operator.advance_epoch("epoch-op-00000001", apply=True)
        self.assertEqual(repeated_advance["epoch"], 2)
        self.assertIs((await self.store.read_epoch()).state, EpochState.RECONCILING)

        next_operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        reconciled = await next_operator.reconcile(apply=True)
        self.assertTrue(reconciled["applied"])
        self.assertEqual(reconciled["epoch"], 2)
        self.assertEqual((await next_operator.reconcile(apply=True))["epoch"], 2)

        ready = await next_operator.mark_ready("ready-op-00000001", apply=True)
        self.assertEqual(ready["state"], "ready")
        self.assertIsNone(await self.store.get(operator.DRAIN_KEY))
        repeated = await next_operator.mark_ready("ready-op-00000001", apply=True)
        self.assertEqual(repeated["state"], "ready")
        self.assertEqual(
            (
                await CoordinationBindingManager(self.storage, self.store).verify(policy(2))
            ).fencing_epoch,
            2,
        )

    async def test_reconcile_requires_drain_and_exact_one_epoch_transition(self) -> None:
        await self.store.delete(HaRuntimeOperator.DRAIN_KEY)
        operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        with self.assertRaisesRegex(RuntimeError, "drain"):
            await operator.reconcile(apply=True)

    async def test_rollback_plan_is_content_free_and_never_mutates(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        before = await self.store.read_epoch()
        plan = await operator.rollback_plan()
        after = await self.store.read_epoch()

        self.assertEqual(before, after)
        self.assertEqual(plan["target_mode"], "standalone")
        self.assertEqual(plan["workers"], 1)
        self.assertEqual(plan["replicas"], 1)
        self.assertNotIn("redis://", repr(plan))

    async def test_status_fails_closed_when_the_namespace_binding_is_missing(self) -> None:
        await self.store.delete(CoordinationBindingManager.STORE_KEY)
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )

        with self.assertRaisesRegex(Exception, "namespace_missing"):
            await operator.status()


if __name__ == "__main__":
    unittest.main()
