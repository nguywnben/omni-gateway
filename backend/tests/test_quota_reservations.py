"""Atomic quota-reservation contract for W3.7."""

from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.state_store import (
    InMemoryStateStore,
    QuotaCommitRequest,
    QuotaReservationRequest,
)


def _reservation(reservation_id: str, **overrides) -> QuotaReservationRequest:
    values = {
        "reservation_id": reservation_id,
        "key_id": "vk_customer",
        "now": 1_000.0,
        "ttl_seconds": 900.0,
        "estimated_tokens": 100,
        "estimated_cost_usd": 0.1,
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
    return QuotaReservationRequest(**values)


class AtomicQuotaReservationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.store = InMemoryStateStore()

    async def test_concurrent_rpm_reservations_admit_only_one_request(self):
        first, second = await asyncio.gather(
            self.store.reserve_quota(_reservation("res_a", rpm_limit=1)),
            self.store.reserve_quota(_reservation("res_b", rpm_limit=1)),
        )

        self.assertEqual(sum(decision.accepted for decision in (first, second)), 1)
        rejected = first if not first.accepted else second
        self.assertEqual(rejected.reason, "rpm")
        self.assertGreaterEqual(rejected.retry_after_seconds, 1)

    async def test_release_is_idempotent_and_returns_capacity(self):
        accepted = await self.store.reserve_quota(_reservation("res_a", rpm_limit=1))
        released = await self.store.release_quota("res_a", now=1_001.0)
        released_again = await self.store.release_quota("res_a", now=1_001.0)
        replacement = await self.store.reserve_quota(
            _reservation("res_b", now=1_001.0, rpm_limit=1)
        )

        self.assertTrue(accepted.accepted)
        self.assertTrue(released)
        self.assertFalse(released_again)
        self.assertTrue(replacement.accepted)

    async def test_committed_actual_tokens_remain_in_the_sliding_window(self):
        accepted = await self.store.reserve_quota(
            _reservation("res_a", estimated_tokens=200, tpm_limit=1_000)
        )
        committed = await self.store.commit_quota(
            QuotaCommitRequest(
                reservation_id="res_a",
                now=1_001.0,
                actual_tokens=900,
                actual_cost_usd=0.0,
                durable_cost_recorded=True,
            )
        )
        rejected = await self.store.reserve_quota(
            _reservation("res_b", now=1_002.0, estimated_tokens=200, tpm_limit=1_000)
        )
        after_window = await self.store.reserve_quota(
            _reservation("res_c", now=1_062.0, estimated_tokens=200, tpm_limit=1_000)
        )

        self.assertTrue(accepted.accepted)
        self.assertTrue(committed.committed)
        self.assertEqual(rejected.reason, "tpm")
        self.assertTrue(after_window.accepted)

    async def test_concurrent_budget_reservations_cannot_knowingly_overspend(self):
        first, second = await asyncio.gather(
            self.store.reserve_quota(
                _reservation("res_a", estimated_cost_usd=0.6, daily_budget_usd=1.0)
            ),
            self.store.reserve_quota(
                _reservation("res_b", estimated_cost_usd=0.6, daily_budget_usd=1.0)
            ),
        )

        self.assertEqual(sum(decision.accepted for decision in (first, second)), 1)
        rejected = first if not first.accepted else second
        self.assertEqual(rejected.reason, "daily_budget")

    async def test_ledger_reconciliation_does_not_double_count_committed_cost(self):
        await self.store.reserve_quota(
            _reservation("res_a", estimated_cost_usd=0.4, daily_budget_usd=1.0)
        )
        await self.store.commit_quota(
            QuotaCommitRequest(
                reservation_id="res_a",
                now=1_001.0,
                actual_tokens=100,
                actual_cost_usd=0.4,
                durable_cost_recorded=True,
            )
        )

        decision = await self.store.reserve_quota(
            _reservation(
                "res_b",
                now=1_002.0,
                estimated_cost_usd=0.6,
                daily_budget_usd=1.0,
                daily_spend_usd=0.4,
                daily_snapshot_started_at=1_001.5,
            )
        )

        self.assertTrue(decision.accepted)

    async def test_snapshot_started_before_commit_cannot_hide_committed_cost(self):
        await self.store.reserve_quota(
            _reservation("res_a", estimated_cost_usd=0.7, daily_budget_usd=1.0)
        )
        await self.store.commit_quota(
            QuotaCommitRequest(
                reservation_id="res_a",
                now=1_001.0,
                actual_tokens=100,
                actual_cost_usd=0.7,
                durable_cost_recorded=True,
            )
        )

        decision = await self.store.reserve_quota(
            _reservation(
                "res_b",
                now=1_002.0,
                estimated_cost_usd=0.4,
                daily_budget_usd=1.0,
                daily_spend_usd=0.0,
                daily_snapshot_started_at=1_000.5,
            )
        )

        self.assertFalse(decision.accepted)
        self.assertEqual(decision.reason, "daily_budget")

    async def test_expired_reservation_is_reconciled(self):
        await self.store.reserve_quota(_reservation("res_a", rpm_limit=1, ttl_seconds=5.0))

        decision = await self.store.reserve_quota(_reservation("res_b", now=1_006.0, rpm_limit=1))

        self.assertTrue(decision.accepted)

    async def test_same_reservation_id_is_idempotent(self):
        first = await self.store.reserve_quota(_reservation("res_same", rpm_limit=1))
        repeated = await self.store.reserve_quota(_reservation("res_same", rpm_limit=1))

        self.assertTrue(first.accepted)
        self.assertTrue(repeated.accepted)
        self.assertTrue(repeated.idempotent)

    async def test_actual_usage_above_reservation_reports_overspend(self):
        await self.store.reserve_quota(
            _reservation("res_a", estimated_cost_usd=0.4, daily_budget_usd=1.0)
        )

        result = await self.store.commit_quota(
            QuotaCommitRequest(
                reservation_id="res_a",
                now=1_001.0,
                actual_tokens=100,
                actual_cost_usd=1.1,
                durable_cost_recorded=True,
            )
        )

        self.assertTrue(result.committed)
        self.assertTrue(result.overspent)


if __name__ == "__main__":
    unittest.main()
