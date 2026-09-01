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

    async def test_stale_reserve_does_not_reconcile_committed_evidence(self) -> None:
        accepted = await self.store.reserve_quota(
            _reservation("committed", daily_budget_usd=1.0, ttl_seconds=10.0)
        )
        self.assertTrue(accepted.accepted)
        self.assertTrue(
            (
                await self.store.commit_quota(
                    QuotaCommitRequest("committed", 1_001.0, 1, 0.1, True)
                )
            ).committed
        )
        committed = self.store._quota_records["committed"].committed
        assert committed is not None
        self.assertFalse(committed.daily_reconciled)
        await self.store.advance_epoch(1, "advance-for-stale")

        denied = await self.store.reserve_quota(
            _reservation("stale", fencing_epoch=1, daily_snapshot_started_at=2_000.0)
        )

        self.assertFalse(denied.accepted)
        self.assertFalse(committed.daily_reconciled)

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
            QuotaCommitRequest("reservation", 1_001.0, 2, 0.0, True, 2, "commit")
        )
        conflict = await self.store.commit_quota(
            QuotaCommitRequest("reservation", 1_003.0, 3, 0.0, True, 2, "commit")
        )
        self.assertTrue(
            (
                await self.store.reserve_quota(
                    _reservation("active-release", fencing_epoch=2, ttl_seconds=10.0)
                )
            ).accepted
        )
        await self.store.advance_epoch(2, "advance-again")
        stale_release = await self.store.release_quota(
            "active-release", now=1_004.0, fencing_epoch=2
        )
        await self.store.mark_epoch_ready(3, "ready-again")
        still_active = await self.store.release_quota(
            "active-release", now=1_004.0, fencing_epoch=3
        )

        self.assertTrue(committed.committed)
        self.assertTrue(replay.idempotent)
        self.assertFalse(conflict.committed)
        self.assertFalse(stale_release)
        self.assertTrue(still_active)

    async def test_ready_denied_cas_replays_until_its_ttl_without_flipping(self) -> None:
        self.assertTrue(
            (
                await self.store.compare_and_set(
                    CasRequest("denied-cas", 0, b"initial", 1.0, 1, "create")
                )
            ).applied
        )
        denied_request = CasRequest("denied-cas", 0, b"denied", 10.0, 1, "denied")
        self.assertFalse((await self.store.compare_and_set(denied_request)).applied)

        self.clock.advance(2.0)
        replay = await self.store.compare_and_set(denied_request)
        conflict = await self.store.compare_and_set(
            CasRequest("denied-cas", 0, b"changed", 10.0, 1, "denied")
        )

        self.assertFalse(replay.applied)
        self.assertTrue(replay.idempotent)
        self.assertFalse(conflict.applied)

        self.clock.advance(8.1)
        after_replay_expiry = await self.store.compare_and_set(denied_request)
        self.assertTrue(after_replay_expiry.applied)
        self.assertFalse(after_replay_expiry.idempotent)

    async def test_ready_denied_reserve_replays_after_capacity_changes(self) -> None:
        self.assertTrue(
            (await self.store.reserve_quota(_reservation("holder", rpm_limit=1))).accepted
        )
        denied_request = _reservation("denied", ttl_seconds=10.0, rpm_limit=1)
        denied = await self.store.reserve_quota(denied_request)
        self.assertEqual(denied.reason, "rpm")
        self.assertTrue(await self.store.release_quota("holder", now=1_000.5))

        replay = await self.store.reserve_quota(denied_request)
        conflict = await self.store.reserve_quota(
            _reservation("denied", ttl_seconds=10.0, rpm_limit=1, estimated_tokens=2)
        )

        self.assertEqual(replay.reason, "rpm")
        self.assertTrue(replay.idempotent)
        self.assertEqual(conflict.reason, "conflict")

    async def test_accepted_id_cannot_reactivate_until_expired_tombstone_is_pruned(self) -> None:
        original = _reservation("expires", ttl_seconds=1.0)
        self.assertTrue((await self.store.reserve_quota(original)).accepted)

        exact_replay = await self.store.reserve_quota(original)
        changed_during_retention = await self.store.reserve_quota(
            _reservation("expires", now=1_002.0, ttl_seconds=1.0)
        )

        self.assertTrue(exact_replay.accepted)
        self.assertTrue(exact_replay.idempotent)
        self.assertEqual(changed_during_retention.reason, "conflict")

        after_retention = await self.store.reserve_quota(
            _reservation("expires", now=1_062.0, ttl_seconds=1.0)
        )
        self.assertTrue(after_retention.accepted)

    async def test_released_and_committed_ids_remain_tombstoned_until_retention(self) -> None:
        self.assertTrue(
            (await self.store.reserve_quota(_reservation("released", ttl_seconds=10.0))).accepted
        )
        self.assertTrue(await self.store.release_quota("released", now=1_001.0))
        self.assertEqual(
            (
                await self.store.reserve_quota(
                    _reservation("released", now=1_002.0, ttl_seconds=10.0)
                )
            ).reason,
            "conflict",
        )

        self.assertTrue(
            (await self.store.reserve_quota(_reservation("committed", ttl_seconds=10.0))).accepted
        )
        self.assertTrue(
            (
                await self.store.commit_quota(
                    QuotaCommitRequest("committed", 1_001.0, 1, 0.0, True, 1, "commit")
                )
            ).committed
        )
        self.assertEqual(
            (
                await self.store.reserve_quota(
                    _reservation("committed", now=1_002.0, ttl_seconds=10.0)
                )
            ).reason,
            "conflict",
        )

        self.assertTrue(
            (
                await self.store.reserve_quota(
                    _reservation("released", now=1_062.0, ttl_seconds=10.0)
                )
            ).accepted
        )
        self.assertTrue(
            (
                await self.store.reserve_quota(
                    _reservation("committed", now=1_062.0, ttl_seconds=10.0)
                )
            ).accepted
        )

    async def test_terminal_records_count_toward_capacity_without_cross_key_leakage(self) -> None:
        store = InMemoryStateStore(
            clock=self.clock,
            _quota_record_limit_for_testing=1,
            _quota_replay_limit_for_testing=4,
        )
        self.assertTrue((await store.reserve_quota(_reservation("first", key_id="key-a"))).accepted)
        self.assertTrue(await store.release_quota("first", now=1_000.5))

        retained_capacity = await store.reserve_quota(
            _reservation("same-key", key_id="key-a", now=1_002.0)
        )
        other_key = await store.reserve_quota(
            _reservation("other-key", key_id="key-b", now=1_002.0)
        )

        self.assertEqual(retained_capacity.reason, "capacity")
        self.assertTrue(other_key.accepted)

    async def test_operation_replay_capacity_fails_closed_without_mutating(self) -> None:
        store = InMemoryStateStore(
            clock=self.clock,
            _quota_record_limit_for_testing=4,
            _quota_replay_limit_for_testing=1,
        )
        self.assertTrue(
            (
                await store.reserve_quota(_reservation("holder", rpm_limit=1, ttl_seconds=20.0))
            ).accepted
        )
        first_denial = await store.reserve_quota(_reservation("denied-1", rpm_limit=1))
        second_denial = await store.reserve_quota(_reservation("denied-2", rpm_limit=1))

        self.assertEqual(first_denial.reason, "rpm")
        self.assertEqual(second_denial.reason, "reconciliation_required")
        with self.assertRaises(CoordinationReconciliationRequiredError):
            await store.release_quota("holder", now=1_000.5, operation_id="release")
        self.assertTrue(await store.release_quota("holder", now=1_002.0, operation_id="release"))

    async def test_explicit_success_replay_uses_the_accepted_retention_window(self) -> None:
        store = InMemoryStateStore(
            clock=self.clock,
            _quota_record_limit_for_testing=4,
            _quota_replay_limit_for_testing=1,
        )
        accepted = await store.reserve_quota(_reservation("accepted", operation_id="accepted-op"))
        blocked = await store.reserve_quota(_reservation("blocked", now=1_002.0))
        after_retention = await store.reserve_quota(_reservation("after-retention", now=1_062.0))

        self.assertTrue(accepted.accepted)
        self.assertEqual(blocked.reason, "reconciliation_required")
        self.assertTrue(after_retention.accepted)

    async def test_stale_quota_heap_nodes_consume_the_cleanup_budget(self) -> None:
        store = InMemoryStateStore(
            clock=self.clock,
            _quota_record_limit_for_testing=300,
            _quota_replay_limit_for_testing=300,
        )
        for index in range(257):
            reservation_id = f"stale-node-{index}"
            self.assertTrue(
                (await store.reserve_quota(_reservation(reservation_id, ttl_seconds=1.0))).accepted
            )
            self.assertTrue(
                await store.release_quota(
                    reservation_id, now=1_000.5, operation_id=f"release-{index}"
                )
            )

        backlog = await store.reserve_quota(_reservation("after-stale", now=1_002.0))
        self.assertEqual(backlog.reason, "reconciliation_required")

    async def test_commit_and_release_operation_ids_are_retained_and_conflict(self) -> None:
        for reservation_id in ("commit-a", "commit-b", "release-a", "release-b"):
            self.assertTrue(
                (
                    await self.store.reserve_quota(_reservation(reservation_id, ttl_seconds=10.0))
                ).accepted
            )

        commit_request = QuotaCommitRequest("commit-a", 1_000.5, 1, 0.0, True, 1, "commit-op")
        self.assertTrue((await self.store.commit_quota(commit_request)).committed)
        commit_replay = await self.store.commit_quota(commit_request)
        commit_conflict = await self.store.commit_quota(
            QuotaCommitRequest("commit-b", 1_000.5, 1, 0.0, True, 1, "commit-op")
        )
        self.assertTrue(commit_replay.idempotent)
        self.assertFalse(commit_conflict.committed)
        self.assertTrue(
            (
                await self.store.commit_quota(
                    QuotaCommitRequest("commit-b", 1_000.5, 1, 0.0, True, 1, "commit-b-op")
                )
            ).committed
        )

        self.assertTrue(
            await self.store.release_quota("release-a", now=1_000.5, operation_id="release-op")
        )
        self.assertFalse(
            await self.store.release_quota("release-a", now=1_001.0, operation_id="release-op")
        )
        self.assertFalse(
            await self.store.release_quota("release-b", now=1_000.5, operation_id="release-op")
        )
        self.assertTrue(
            await self.store.release_quota("release-b", now=1_000.5, operation_id="release-b-op")
        )

    async def test_release_rejects_malformed_untyped_arguments(self) -> None:
        with self.assertRaises(ValueError):
            await self.store.release_quota("release", now=1_000.0, fencing_epoch=True)
        with self.assertRaises(ValueError):
            await self.store.release_quota("", now=1_000.0)
        with self.assertRaises(ValueError):
            await self.store.release_quota("release", now=float("nan"))
        with self.assertRaises(ValueError):
            await self.store.release_quota("release", now=1_000.0, operation_id="bad\n")

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
