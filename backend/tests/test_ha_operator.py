from __future__ import annotations

import base64
import json
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.coordination import (
    CoordinationReconciliationRequiredError,
    EpochState,
    QuotaReconciliationResult,
    QuotaReservationRequest,
)
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
        self.assertIsInstance(await self.store.get(operator.DRAIN_KEY), str)
        self.assertEqual(
            json.loads(await self.store.get(operator.DRAIN_KEY))["schema_version"],
            2,
        )
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

    async def test_mark_ready_requires_complete_quota_reconciliation(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("epoch-op-quota-gate", apply=True)

        async def incomplete_reconciliation(**_kwargs: object) -> QuotaReconciliationResult:
            return QuotaReconciliationResult(256, False, "opaque-cursor")

        self.store.reconcile_quota_state = incomplete_reconciliation  # type: ignore[method-assign]
        next_operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        page = await next_operator.reconcile(apply=True)

        self.assertFalse(page["quota_complete"])
        self.assertTrue(page["quota_cursor_present"])
        self.assertNotIn("opaque-cursor", repr(page))
        with self.assertRaisesRegex(RuntimeError, "quota reconciliation"):
            await next_operator.mark_ready("ready-op-quota-gate", apply=True)

    async def test_mark_ready_revalidates_a_tampered_complete_drain_record(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        decision = await self.store.reserve_quota(
            QuotaReservationRequest(
                reservation_id="active-before-drain",
                key_id="virtual-key",
                now=1.0,
                ttl_seconds=61.0,
                estimated_tokens=1,
                estimated_cost_usd=0.0,
                rpm_limit=None,
                tpm_limit=None,
                daily_budget_usd=None,
                monthly_budget_usd=None,
                daily_spend_usd=0.0,
                monthly_spend_usd=0.0,
                daily_snapshot_started_at=1.0,
                monthly_snapshot_started_at=1.0,
            )
        )
        self.assertTrue(decision.accepted)
        await operator.drain(apply=True)
        await operator.advance_epoch("epoch-op-tampered-drain", apply=True)
        next_operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        with self.assertRaises(CoordinationReconciliationRequiredError):
            await next_operator.reconcile(apply=True)
        drain = json.loads(await self.store.get(operator.DRAIN_KEY))
        await self.store.set(
            operator.DRAIN_KEY,
            operator._encode_record(
                {
                    **drain,
                    "quota_reconciliation_cursor": None,
                    "quota_reconciliation_complete": True,
                }
            ),
        )

        with self.assertRaises(CoordinationReconciliationRequiredError):
            await next_operator.mark_ready("ready-op-tampered-drain", apply=True)
        self.assertIs((await self.store.read_epoch()).state, EpochState.RECONCILING)

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
