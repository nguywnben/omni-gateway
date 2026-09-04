"""Reusable semantic assertions for every CoordinationStore implementation."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from core.coordination import (
    CasRequest,
    CoordinationUnavailableError,
    EpochState,
    InvalidationRequest,
    QuotaCommitRequest,
    QuotaReservationRequest,
)

if TYPE_CHECKING:
    from core.coordination import CoordinationStore


class CoordinationStoreContract:
    """Mixin for async tests; implementations provide ``self.store``."""

    store: CoordinationStore

    @staticmethod
    def _quota_request(
        reservation_id: str, *, key_id: str, operation_id: str, **changes: object
    ) -> QuotaReservationRequest:
        values: dict[str, object] = {
            "reservation_id": reservation_id,
            "key_id": key_id,
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
            "operation_id": operation_id,
        }
        values.update(changes)
        return QuotaReservationRequest(**values)  # type: ignore[arg-type]

    async def assert_quota_lifecycle_replay_expiry_and_capacity_contract(
        self, *, advance_quota_clock: Callable[[float], Awaitable[None]]
    ) -> None:
        """Assert the quota semantics shared by the reference and registered Lua."""

        replay_request = self._quota_request(
            "quota-replay", key_id="quota-replay-key", operation_id="quota-replay-operation"
        )
        first = await self.store.reserve_quota(replay_request)
        replay = await self.store.reserve_quota(replay_request)
        conflict = await self.store.reserve_quota(
            self._quota_request(
                "quota-replay",
                key_id="quota-replay-key",
                operation_id="quota-replay-operation",
                estimated_tokens=2,
            )
        )
        self.assertTrue(first.accepted)
        self.assertTrue(replay.idempotent)
        self.assertEqual(conflict.reason, "conflict")

        for suffix in ("a", "b"):
            self.assertTrue(
                (
                    await self.store.reserve_quota(
                        self._quota_request(
                            f"capacity-{suffix}",
                            key_id="quota-capacity-key",
                            operation_id=f"capacity-{suffix}",
                        )
                    )
                ).accepted
            )
        capacity = await self.store.reserve_quota(
            self._quota_request(
                "capacity-c", key_id="quota-capacity-key", operation_id="capacity-c"
            )
        )
        self.assertEqual(capacity.reason, "capacity")

        self.assertTrue(
            (
                await self.store.reserve_quota(
                    self._quota_request(
                        "large-token-a",
                        key_id="quota-large-token-key",
                        operation_id="large-token-a",
                        estimated_tokens=2**53 + 1,
                        tpm_limit=2**53 + 1,
                    )
                )
            ).accepted
        )
        exact_token_denial = await self.store.reserve_quota(
            self._quota_request(
                "large-token-b",
                key_id="quota-large-token-key",
                operation_id="large-token-b",
                estimated_tokens=1,
                tpm_limit=2**53 + 1,
            )
        )
        self.assertEqual(exact_token_denial.reason, "tpm")

        self.assertTrue(
            (
                await self.store.reserve_quota(
                    self._quota_request(
                        "quota-commit",
                        key_id="quota-commit-key",
                        operation_id="quota-commit-reserve",
                        ttl_seconds=60.0,
                    )
                )
            ).accepted
        )
        commit_request = QuotaCommitRequest(
            "quota-commit", 1_001.0, 2, 0.0, False, operation_id="quota-commit-operation"
        )
        committed = await self.store.commit_quota(commit_request)
        committed_replay = await self.store.commit_quota(commit_request)
        self.assertTrue(committed.committed)
        self.assertTrue(committed_replay.idempotent)
        self.assertFalse(await self.store.release_quota("quota-commit", now=1_002.0))

        self.assertTrue(
            (
                await self.store.reserve_quota(
                    self._quota_request(
                        "quota-release",
                        key_id="quota-release-key",
                        operation_id="quota-release-reserve",
                        ttl_seconds=60.0,
                    )
                )
            ).accepted
        )
        self.assertTrue(
            await self.store.release_quota(
                "quota-release", now=1_001.0, operation_id="quota-release-operation"
            )
        )
        self.assertFalse(
            await self.store.release_quota(
                "quota-release", now=1_001.0, operation_id="quota-release-operation"
            )
        )

        identical_expiry = self._quota_request(
            "quota-expiry-identical",
            key_id="quota-expiry-identical-key",
            operation_id="quota-expiry-identical-operation",
        )
        changed_expiry = self._quota_request(
            "quota-expiry-changed",
            key_id="quota-expiry-changed-key",
            operation_id="quota-expiry-changed-operation",
        )
        self.assertTrue((await self.store.reserve_quota(identical_expiry)).accepted)
        self.assertTrue((await self.store.reserve_quota(changed_expiry)).accepted)
        await advance_quota_clock(60.1)

        identical_after_retention = await self.store.reserve_quota(identical_expiry)
        changed_after_retention = await self.store.reserve_quota(
            self._quota_request(
                "quota-expiry-changed",
                key_id="quota-expiry-changed-key",
                operation_id="quota-expiry-changed-operation",
                estimated_tokens=2,
            )
        )
        self.assertTrue(identical_after_retention.accepted)
        self.assertFalse(identical_after_retention.idempotent)
        self.assertTrue(changed_after_retention.accepted)
        self.assertFalse(changed_after_retention.idempotent)

    async def assert_epoch_cas_and_invalidation_contract(
        self, *, advance_cas_clock: Callable[[float], Awaitable[None]]
    ) -> None:
        """Assert parity with an implementation-supplied clock/server-time advance hook."""
        epoch = await self.store.read_epoch()
        self.assertEqual(epoch.epoch, 1)
        self.assertEqual(epoch.state, EpochState.READY)
        first_clock = await self.store.read_coordination_time(epoch=1)
        self.assertGreaterEqual(first_clock.milliseconds, 0)

        advanced = await self.store.advance_epoch(1, "advance-1")
        self.assertEqual(advanced.epoch, 2)
        self.assertEqual(advanced.state, EpochState.RECONCILING)
        self.assertEqual(await self.store.advance_epoch(1, "advance-1"), advanced)
        self.assertEqual(await self.store.advance_epoch(2, "advance-1"), advanced)
        self.assertEqual(await self.store.advance_epoch(1, "advance-conflict"), advanced)

        stale_cas = await self.store.compare_and_set(
            CasRequest("contract-key", 0, b"value", 1.0, 2, "cas-1")
        )
        self.assertFalse(stale_cas.applied)
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.read_cas("contract-key", epoch=2)
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.read_coordination_time(epoch=2)
        reconciling_invalidation = await self.store.invalidate(
            InvalidationRequest("reconciling-scope", 2, "reconciling-invalidate")
        )
        self.assertFalse(reconciling_invalidation.applied)

        self.assertEqual(await self.store.mark_epoch_ready(1, "ready-stale"), advanced)
        ready = await self.store.mark_epoch_ready(2, "ready-1")
        self.assertEqual(ready.state, EpochState.READY)
        ready_clock = await self.store.read_coordination_time(epoch=2)
        self.assertGreaterEqual(ready_clock.milliseconds, first_clock.milliseconds)
        self.assertEqual(await self.store.mark_epoch_ready(2, "ready-1"), ready)
        self.assertEqual(await self.store.mark_epoch_ready(1, "ready-1"), ready)
        self.assertEqual(await self.store.mark_epoch_ready(1, "ready-conflict"), ready)

        stale_epoch_cas = await self.store.compare_and_set(
            CasRequest("stale-epoch-key", 0, b"value", 1.0, 1, "stale-epoch-cas")
        )
        self.assertFalse(stale_epoch_cas.applied)
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.read_cas("stale-epoch-key", epoch=1)
        stale_epoch_invalidation = await self.store.invalidate(
            InvalidationRequest("stale-epoch-scope", 1, "stale-epoch-invalidate")
        )
        self.assertFalse(stale_epoch_invalidation.applied)

        cas = await self.store.compare_and_set(
            CasRequest("contract-key", 0, b"value", 1.0, 2, "cas-1")
        )
        self.assertTrue(cas.applied)
        self.assertEqual(cas.revision, 1)
        snapshot = await self.store.read_cas("contract-key", epoch=2)
        self.assertEqual((snapshot.revision, snapshot.payload), (1, b"value"))
        wrong_revision = await self.store.compare_and_set(
            CasRequest("contract-key", 0, b"different", 1.0, 2, "wrong-revision")
        )
        self.assertFalse(wrong_revision.applied)
        replayed_cas = await self.store.compare_and_set(
            CasRequest("contract-key", 0, b"value", 1.0, 2, "cas-1")
        )
        self.assertEqual(replayed_cas.revision, 1)
        self.assertTrue(replayed_cas.idempotent)
        conflicting_cas = await self.store.compare_and_set(
            CasRequest("contract-key", 1, b"different", 1.0, 2, "cas-1")
        )
        self.assertFalse(conflicting_cas.applied)
        updated_cas = await self.store.compare_and_set(
            CasRequest("contract-key", 1, b"updated", 1.0, 2, "cas-2")
        )
        self.assertEqual(updated_cas.revision, 2)
        updated_snapshot = await self.store.read_cas("contract-key", epoch=2)
        self.assertEqual((updated_snapshot.revision, updated_snapshot.payload), (2, b"updated"))

        expiring_cas = await self.store.compare_and_set(
            CasRequest("expiry-key", 0, b"value", 2.0, 2, "expiry-1")
        )
        self.assertEqual(expiring_cas.revision, 1)
        await advance_cas_clock(1.0)
        replayed_expiring_cas = await self.store.compare_and_set(
            CasRequest("expiry-key", 0, b"value", 2.0, 2, "expiry-1")
        )
        self.assertTrue(replayed_expiring_cas.idempotent)
        await advance_cas_clock(1.1)
        expired_snapshot = await self.store.read_cas("expiry-key", epoch=2)
        self.assertEqual((expired_snapshot.revision, expired_snapshot.payload), (None, None))
        expired_cas = await self.store.compare_and_set(
            CasRequest("expiry-key", 0, b"replacement", 2.0, 2, "expiry-2")
        )
        self.assertEqual(expired_cas.revision, 1)

        self.assertIsNone(
            (await self.store.read_invalidation_generation("contract-scope")).generation
        )
        invalidation = await self.store.invalidate(
            InvalidationRequest("contract-scope", 2, "invalidate-1")
        )
        self.assertTrue(invalidation.applied)
        self.assertEqual(invalidation.generation, 1)
        replayed_invalidation = await self.store.invalidate(
            InvalidationRequest("contract-scope", 2, "invalidate-1")
        )
        self.assertEqual(replayed_invalidation.generation, 1)
        self.assertTrue(replayed_invalidation.idempotent)
        conflicting_invalidation = await self.store.invalidate(
            InvalidationRequest("contract-scope", 2, "invalidate-1", replay_ttl_seconds=2.0)
        )
        self.assertFalse(conflicting_invalidation.applied)
        incremented_invalidation = await self.store.invalidate(
            InvalidationRequest("contract-scope", 2, "invalidate-2")
        )
        self.assertEqual(incremented_invalidation.generation, 2)
        self.assertEqual(
            (await self.store.read_invalidation_generation("contract-scope")).generation, 2
        )

        await self.store.close()
        await self.store.close()
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.read_epoch()
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.advance_epoch(2, "after-close-advance")
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.mark_epoch_ready(2, "after-close-ready")
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.compare_and_set(
                CasRequest("after-close-key", 0, b"value", 1.0, 2, "after-close-cas")
            )
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.read_cas("after-close-key", epoch=2)
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.read_coordination_time(epoch=2)
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.invalidate(
                InvalidationRequest("after-close-scope", 2, "after-close-invalidate")
            )
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.read_invalidation_generation("after-close-scope")
