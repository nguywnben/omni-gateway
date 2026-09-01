"""Behavioral tests for the in-process coordination reference."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from coordination_store_contract import CoordinationStoreContract
from core.coordination import CasRequest, CoordinationReconciliationRequiredError, EpochState
from core.state_store import InMemoryStateStore, QuotaCommitRequest, QuotaReservationRequest


class _Clock:
    def __init__(self) -> None:
        self.value = 1_000.0

    def __call__(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


def _reservation(reservation_id: str, **overrides: object) -> QuotaReservationRequest:
    values: dict[str, object] = {
        "reservation_id": reservation_id,
        "key_id": "virtual-key",
        "now": 1_000.0,
        "ttl_seconds": 1.0,
        "estimated_tokens": 1,
        "estimated_cost_usd": 0.0,
        "rpm_limit": None,
        "tpm_limit": None,
        "daily_budget_usd": None,
        "monthly_budget_usd": None,
        "daily_spend_usd": 0.0,
        "monthly_spend_usd": 0.0,
        "daily_snapshot_started_at": 1_000.0,
        "monthly_snapshot_started_at": 1_000.0,
    }
    values.update(overrides)
    return QuotaReservationRequest(**values)  # type: ignore[arg-type]


class InMemoryCoordinationTests(CoordinationStoreContract, unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.clock = _Clock()
        self.store = InMemoryStateStore(clock=self.clock)

    async def test_shared_coordination_contract(self) -> None:
        async def advance(seconds: float) -> None:
            self.clock.advance(seconds)

        await self.assert_epoch_cas_and_invalidation_contract(advance_cas_clock=advance)

    async def test_quota_mutations_require_the_exact_ready_epoch(self) -> None:
        advanced = await self.store.advance_epoch(1, "advance")
        self.assertEqual(advanced.state, EpochState.RECONCILING)

        reconciling = await self.store.reserve_quota(_reservation("reconciling", fencing_epoch=2))
        self.assertFalse(reconciling.accepted)
        self.assertEqual(reconciling.reason, "reconciling")

        await self.store.mark_epoch_ready(2, "ready")
        stale = await self.store.reserve_quota(_reservation("stale", fencing_epoch=1))
        self.assertFalse(stale.accepted)
        self.assertEqual(stale.reason, "stale_epoch")

        accepted = await self.store.reserve_quota(_reservation("ready", fencing_epoch=2))
        self.assertTrue(accepted.accepted)

    async def test_quota_replay_with_changed_payload_conflicts(self) -> None:
        first = await self.store.reserve_quota(_reservation("same", fencing_epoch=1))
        replay = await self.store.reserve_quota(_reservation("same", fencing_epoch=1))
        conflict = await self.store.reserve_quota(
            _reservation("same", fencing_epoch=1, estimated_tokens=2)
        )

        self.assertTrue(first.accepted)
        self.assertTrue(replay.idempotent)
        self.assertFalse(conflict.accepted)
        self.assertEqual(conflict.reason, "conflict")

    async def test_quota_commit_and_release_are_fenced_and_replay_safe(self) -> None:
        await self.store.advance_epoch(1, "advance")
        await self.store.mark_epoch_ready(2, "ready")
        self.assertTrue(
            (
                await self.store.reserve_quota(
                    _reservation("reservation", fencing_epoch=2, ttl_seconds=10.0)
                )
            ).accepted
        )
        committed = await self.store.commit_quota(
            QuotaCommitRequest("reservation", 1_001.0, 2, 0.0, True, 2, "commit")
        )
        replay = await self.store.commit_quota(
            QuotaCommitRequest("reservation", 1_002.0, 2, 0.0, True, 2, "commit")
        )
        conflict = await self.store.commit_quota(
            QuotaCommitRequest("reservation", 1_003.0, 3, 0.0, True, 2, "commit")
        )
        await self.store.advance_epoch(2, "advance-again")
        stale_release = await self.store.release_quota("reservation", now=1_004.0, fencing_epoch=2)

        self.assertTrue(committed.committed)
        self.assertTrue(replay.idempotent)
        self.assertFalse(conflict.committed)
        self.assertFalse(stale_release)

    async def test_capacity_exhaustion_is_a_closed_admission_decision(self) -> None:
        store = InMemoryStateStore(clock=self.clock, _quota_record_limit_for_testing=2)

        self.assertTrue((await store.reserve_quota(_reservation("one"))).accepted)
        self.assertTrue((await store.reserve_quota(_reservation("two"))).accepted)
        exhausted = await store.reserve_quota(_reservation("three"))

        self.assertFalse(exhausted.accepted)
        self.assertEqual(exhausted.reason, "capacity")

    async def test_cleanup_backlog_fails_closed_without_unbounded_pruning(self) -> None:
        store = InMemoryStateStore(clock=self.clock, _quota_record_limit_for_testing=300)
        for index in range(257):
            decision = await store.reserve_quota(_reservation(f"expired-{index}"))
            self.assertTrue(decision.accepted)

        backlog = await store.reserve_quota(_reservation("after-expiry", now=1_002.0))

        self.assertFalse(backlog.accepted)
        self.assertEqual(backlog.reason, "reconciliation_required")

    async def test_cas_cleanup_backlog_raises_a_typed_fail_closed_error(self) -> None:
        for index in range(257):
            result = await self.store.compare_and_set(
                CasRequest(f"expired-cas-{index}", 0, b"value", 1.0, 1, f"cas-{index}")
            )
            self.assertTrue(result.applied)
        self.clock.advance(2.0)

        with self.assertRaises(CoordinationReconciliationRequiredError):
            await self.store.compare_and_set(
                CasRequest("after-expiry", 0, b"value", 1.0, 1, "after-expiry")
            )


if __name__ == "__main__":
    unittest.main()
