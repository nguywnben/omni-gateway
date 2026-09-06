from __future__ import annotations

import base64
import json
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.coordination import EpochState, QuotaReconciliationResult
from core.ha_coordination_binding import CoordinationBindingManager
from core.ha_operator import HaRuntimeOperator
from core.ha_reconciliation import ReconciliationComponent, ReconciliationPage
from core.ha_runtime_policy import HaRuntimePolicy
from core.identity.repository import OidcPolicyRevisionRecord
from core.state_store import InMemoryStateStore
from core.usage_ledger import UsageLiabilityPage

from backend.tests.durable_migration_fixtures import (
    PLAN_ID,
    MemoryMigrationCheckpoints,
    completed_migration_checkpoint,
)


class _Storage:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}
        self.checkpoints = MemoryMigrationCheckpoints(completed_migration_checkpoint())

    async def get_config(self, key: str, default=None):
        return self.values.get(key, default)

    async def set_config(self, key: str, value: object) -> bool:
        self.values[key] = value
        return True

    async def create_migration_checkpoint_repository(self):
        return self.checkpoints

    async def create_usage_ledger_repository(self):
        return self

    async def reconciliation_page(self, *, after, limit):
        return UsageLiabilityPage(0, True, None, "a" * 64, 0)

    async def create_identity_repository(self):
        return self

    async def list_identities(self, *, limit=100, after=None):
        return []

    async def get_oidc_policy_revision(self):
        return OidcPolicyRevisionRecord.initial(now=datetime(2026, 9, 6, tzinfo=timezone.utc))


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
        await manager.bootstrap(
            policy(),
            activation_record="act_" + ("a" * 32),
            migration_plan_id=PLAN_ID,
            apply=True,
        )

    async def _reconcile_all(
        self,
        operator: HaRuntimeOperator,
        operation_id: str = "reconcile-operation-1",
    ) -> dict[str, object]:
        result: dict[str, object] = {}
        for _ in range(8):
            result = await operator.reconcile(operation_id, apply=True)
            if result["reconciliation_complete"]:
                return result
        self.fail("Reconciliation did not complete within the bounded component inventory.")

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
            3,
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
        reconciled = await self._reconcile_all(next_operator)
        self.assertTrue(reconciled["applied"])
        self.assertEqual(reconciled["epoch"], 2)
        self.assertEqual(
            (await next_operator.reconcile("reconcile-operation-1", apply=True))["epoch"], 2
        )

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
            await operator.reconcile("reconcile-without-drain", apply=True)

    async def test_mark_ready_retry_removes_drain_after_crash_boundary(self) -> None:
        from unittest.mock import patch

        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("crash-advance", apply=True)
        operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await self._reconcile_all(operator, "reconcile-crash-retry")
        with patch.object(
            self.store, "complete_admission_drain", side_effect=RuntimeError("injected crash")
        ):
            with self.assertRaisesRegex(RuntimeError, "injected crash"):
                await operator.mark_ready("crash-ready", apply=True)
        before = await self.store.read_epoch()
        self.assertIs(before.state, EpochState.READY)
        self.assertIsNotNone(await self.store.get(operator.DRAIN_KEY))
        await operator.mark_ready("crash-ready", apply=False)
        self.assertIsNotNone(await self.store.get(operator.DRAIN_KEY))
        await operator.mark_ready("crash-ready", apply=True)
        self.assertEqual(await self.store.read_epoch(), before)
        self.assertIsNone(await self.store.get(operator.DRAIN_KEY))

    async def test_mark_ready_ready_epoch_rejects_mismatched_drain(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        with self.assertRaisesRegex(RuntimeError, "reconciliation"):
            await operator.mark_ready("unrelated-ready", apply=True)

    async def test_mark_ready_crash_retry_rejects_different_operation(self) -> None:
        from unittest.mock import patch

        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("exact-advance", apply=True)
        operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await self._reconcile_all(operator, "reconcile-ready-operation")
        with patch.object(
            self.store, "complete_admission_drain", side_effect=RuntimeError("injected crash")
        ):
            with self.assertRaises(RuntimeError):
                await operator.mark_ready("exact-ready", apply=True)
        with self.assertRaisesRegex(RuntimeError, "drain"):
            await operator.mark_ready("different-ready", apply=True)
        self.assertIsNotNone(await self.store.get(operator.DRAIN_KEY))

    async def test_mark_ready_requires_complete_reconciliation_receipt(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("epoch-op-quota-gate", apply=True)

        async def incomplete_reconciliation(**_kwargs: object) -> QuotaReconciliationResult:
            return QuotaReconciliationResult(256, False, "opaque-cursor", "a" * 64)

        self.store.reconcile_quota_state = incomplete_reconciliation  # type: ignore[method-assign]
        next_operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        page = await next_operator.reconcile("reconcile-quota-gate", apply=True)

        self.assertFalse(page["reconciliation_complete"])
        self.assertTrue(page["cursor_present"])
        self.assertNotIn("opaque-cursor", repr(page))
        with self.assertRaisesRegex(RuntimeError, "reconciliation evidence"):
            await next_operator.mark_ready("ready-op-quota-gate", apply=True)

    async def test_reconciliation_resumes_after_restart_at_every_component_boundary(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("boundary-advance", apply=True)

        expected_components = (
            "quota_state",
            "usage_liability",
            "identity_policy",
            "cache_invalidation",
        )
        for index, component in enumerate(expected_components):
            # Recreate the operator on every boundary to prove that the durable
            # receipt, rather than process memory, is the resume authority.
            operator = HaRuntimeOperator(
                policy(2),
                self.storage,
                self.store,
                activation_verifier=lambda _record: True,
            )
            result = await operator.reconcile("boundary-reconcile", apply=True)
            self.assertEqual(result["component"], component)
            self.assertEqual(
                result["reconciliation_complete"],
                index == len(expected_components) - 1,
            )

        receipt = await operator._receipt()
        self.assertIsNotNone(receipt)
        assert receipt is not None
        self.assertTrue(receipt.complete)
        self.assertTrue(all(item.pages == 1 for item in receipt.components))

    async def test_reconciliation_is_side_effect_free_in_preview_and_operation_bound(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("preview-advance", apply=True)
        operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )

        preview = await operator.reconcile("preview-reconcile", apply=False)

        self.assertFalse(preview["applied"])
        self.assertIsNone(await self.storage.get_config(operator.RECEIPT_KEY, None))
        await operator.reconcile("preview-reconcile", apply=True)
        with self.assertRaisesRegex(RuntimeError, "operation identity"):
            await operator.reconcile("different-reconcile", apply=True)

    async def test_reconciliation_and_ready_mutations_share_one_owned_transition_lock(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("locked-transition-advance", apply=True)
        operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )

        self.assertTrue(
            await self.store.acquire_lock(
                operator.RECONCILIATION_LOCK_KEY,
                ttl_seconds=operator.RECONCILIATION_LOCK_TTL_SECONDS,
            )
        )
        with self.assertRaisesRegex(RuntimeError, "in progress"):
            await operator.reconcile("locked-transition-reconcile", apply=True)
        await self.store.release_lock(operator.RECONCILIATION_LOCK_KEY)

        await self._reconcile_all(operator, "locked-transition-reconcile")
        self.assertTrue(
            await self.store.acquire_lock(
                operator.RECONCILIATION_LOCK_KEY,
                ttl_seconds=operator.RECONCILIATION_LOCK_TTL_SECONDS,
            )
        )
        with self.assertRaisesRegex(RuntimeError, "in progress"):
            await operator.mark_ready("locked-transition-ready", apply=True)
        await self.store.release_lock(operator.RECONCILIATION_LOCK_KEY)
        self.assertIs((await self.store.read_epoch()).state, EpochState.RECONCILING)

    async def test_expired_lock_owner_cannot_publish_after_a_newer_fence(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("stale-owner-advance", apply=True)
        operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        stale_fence = await self.store.increment(operator.RECONCILIATION_FENCE_KEY)

        async def lose_ownership(*_args, **_kwargs):
            await self.store.increment(operator.RECONCILIATION_FENCE_KEY)
            return ReconciliationPage(
                ReconciliationComponent.QUOTA,
                None,
                0,
                True,
                None,
                "a" * 64,
                1,
            )

        operator._reconciliation.next_page = lose_ownership  # type: ignore[method-assign]
        with self.assertRaisesRegex(RuntimeError, "ownership is stale"):
            await operator._reconcile_locked(
                "stale-owner-reconcile",
                apply=True,
                page_size=256,
                transition_fence=stale_fence,
            )
        self.assertNotIn(operator._receipt_storage_key(stale_fence), self.storage.values)

    async def test_reconciliation_rejects_a_tampered_incomplete_binding(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("tampered-incomplete-advance", apply=True)
        operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.reconcile("tampered-incomplete-reconcile", apply=True)
        latest = await operator._receipt()
        assert latest is not None
        receipt_key = operator._receipt_storage_key(latest.transition_fence)
        receipt = dict(self.storage.values[receipt_key])
        self.storage.values[receipt_key] = {
            **receipt,
            "manifest_checksum": "e" * 64,
        }

        with self.assertRaisesRegex(RuntimeError, "not authentic"):
            await operator.reconcile("tampered-incomplete-reconcile", apply=True)

    async def test_mark_ready_rejects_tampered_receipt_binding_fields(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("receipt-binding-advance", apply=True)
        operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await self._reconcile_all(operator, "receipt-binding-reconcile")
        latest = await operator._receipt()
        assert latest is not None
        receipt_key = operator._receipt_storage_key(latest.transition_fence)
        original = dict(self.storage.values[receipt_key])

        for field, value in (
            ("target_epoch", 3),
            ("manifest_checksum", "e" * 64),
            ("migration_checkpoint_revision", 999),
            ("migration_checkpoint_checksum", "f" * 64),
            ("operation_id", "tampered-operation"),
        ):
            with self.subTest(field=field):
                self.storage.values[receipt_key] = {**original, field: value}
                with self.assertRaisesRegex(RuntimeError, "reconciliation"):
                    await operator.mark_ready("receipt-binding-ready", apply=True)
        self.storage.values[receipt_key] = original

    async def test_mark_ready_revalidates_a_tampered_complete_drain_record(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("epoch-op-tampered-drain", apply=True)
        next_operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await self._reconcile_all(next_operator, "reconcile-tampered-drain")
        drain = json.loads(await self.store.get(operator.DRAIN_KEY))
        await self.store.set(
            operator.DRAIN_KEY,
            operator._encode_record(
                {
                    **drain,
                    "reconciliation_receipt_checksum": "e" * 64,
                }
            ),
        )

        with self.assertRaisesRegex(RuntimeError, "reconciliation"):
            await next_operator.mark_ready("ready-op-tampered-drain", apply=True)
        self.assertIs((await self.store.read_epoch()).state, EpochState.RECONCILING)

    async def test_rollback_plan_requires_a_fresh_active_drain_and_never_mutates(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("rollback-advance", apply=True)
        operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await self._reconcile_all(operator, "rollback-reconcile")
        before = await self.store.read_epoch()
        plan = await operator.rollback_plan()
        after = await self.store.read_epoch()

        self.assertEqual(before, after)
        self.assertEqual(plan["target_mode"], "standalone")
        self.assertEqual(plan["workers"], 1)
        self.assertEqual(plan["replicas"], 1)
        self.assertNotIn("redis://", repr(plan))

    async def test_rollback_plan_rejects_a_receipt_after_admission_resumes(self) -> None:
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await operator.drain(apply=True)
        await operator.advance_epoch("rollback-stale-advance", apply=True)
        operator = HaRuntimeOperator(
            policy(2), self.storage, self.store, activation_verifier=lambda _record: True
        )
        await self._reconcile_all(operator, "rollback-stale-reconcile")
        await operator.mark_ready("rollback-stale-ready", apply=True)

        with self.assertRaisesRegex(RuntimeError, "active completed drain"):
            await operator.rollback_plan()

    async def test_status_fails_closed_when_the_namespace_binding_is_missing(self) -> None:
        await self.store.delete(CoordinationBindingManager.STORE_KEY)
        operator = HaRuntimeOperator(
            policy(), self.storage, self.store, activation_verifier=lambda _record: True
        )

        with self.assertRaisesRegex(Exception, "namespace_missing"):
            await operator.status()


if __name__ == "__main__":
    unittest.main()
