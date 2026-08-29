"""Real SQLite W4.14 usage-ledger repository contract."""

from __future__ import annotations

import asyncio
import dataclasses
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.storage.sqlite_manager import SQLiteManager
from core.storage.usage_ledger_sqlite import SQLiteUsageLedgerRepository
from core.storage_adapter import StorageAdapter
from core.usage_ledger import (
    USAGE_LEDGER_SCHEMA_VERSION,
    BudgetReservationRequest,
    UsageLedgerConflict,
    UsageLedgerEntry,
    UsageLedgerStateConflict,
    usd_to_nanos,
)

from backend.tests.support import workspace_temp_directory

NOW = 1_777_777_700.0
KEY_ID = "vk_enterprise"


def _usage(suffix: str = "a", **overrides) -> UsageLedgerEntry:
    values = {
        "schema_version": USAGE_LEDGER_SCHEMA_VERSION,
        "event_id": "use_" + (suffix * 32),
        "occurred_at": NOW + 10,
        "credential_ref": "account.json",
        "request_id": f"request-{suffix}",
        "model": "gpt-5.6",
        "provider": "openai",
        "status_code": 200,
        "success": True,
        "input_tokens": 100,
        "output_tokens": 20,
        "total_tokens": 120,
        "cached_tokens": 5,
        "reasoning_tokens": 3,
        "estimated_input_tokens": 110,
        "estimated_tokens_saved": 10,
        "compressed_messages": 2,
        "quality_profile": "balanced",
        "quality_policy_revision": 4,
        "compression_reason": "target_reached",
        "latency_ms": 250,
        "retry_count": 1,
        "cost_nanos": usd_to_nanos("0.25"),
        "api_key_id": KEY_ID,
    }
    values.update(overrides)
    return UsageLedgerEntry(**values)


def _reservation(suffix: str, **overrides) -> BudgetReservationRequest:
    values = {
        "schema_version": USAGE_LEDGER_SCHEMA_VERSION,
        "reservation_id": "qrs_" + (suffix * 32),
        "key_id": KEY_ID,
        "created_at": NOW,
        "expires_at": NOW + 60,
        "estimated_tokens": 1_000,
        "estimated_cost_nanos": usd_to_nanos("0.60"),
        "daily_budget_nanos": usd_to_nanos("1.00"),
        "monthly_budget_nanos": usd_to_nanos("10.00"),
    }
    values.update(overrides)
    return BudgetReservationRequest(**values)


class SQLiteUsageLedgerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp_dir = workspace_temp_directory()
        self.database_path = str(Path(self.temp_dir.__enter__()) / "credentials.db")
        self.repository = SQLiteUsageLedgerRepository(self.database_path)
        await self.repository.initialize()

    async def asyncTearDown(self):
        self.temp_dir.__exit__(None, None, None)

    async def test_append_is_exactly_idempotent_and_conflict_safe(self):
        entry = _usage()
        first = await self.repository.append_usage(entry)
        repeated = await self.repository.append_usage(entry)
        self.assertTrue(first.inserted)
        self.assertFalse(first.idempotent)
        self.assertFalse(repeated.inserted)
        self.assertTrue(repeated.idempotent)

        with self.assertRaises(UsageLedgerConflict):
            await self.repository.append_usage(dataclasses.replace(entry, cost_nanos=1))

        spend = await self.repository.get_spend(since=0, api_key_id=KEY_ID)
        self.assertTrue(spend.available)
        self.assertEqual(spend.calls, 1)
        self.assertEqual(spend.total_tokens, 120)
        self.assertEqual(spend.cost_nanos, usd_to_nanos("0.25"))

    async def test_concurrent_reservations_cannot_knowingly_overspend(self):
        first, second = await asyncio.gather(
            self.repository.reserve_budget(_reservation("a")),
            self.repository.reserve_budget(_reservation("b")),
        )
        accepted = [decision for decision in (first, second) if decision.accepted]
        rejected = [decision for decision in (first, second) if not decision.accepted]
        self.assertEqual(len(accepted), 1)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0].reason, "daily_budget")

    async def test_reserve_commit_restart_and_replay_count_once(self):
        request = _reservation("a")
        accepted = await self.repository.reserve_budget(request)
        repeated = await self.repository.reserve_budget(request)
        self.assertTrue(accepted.accepted)
        self.assertTrue(repeated.accepted)
        self.assertTrue(repeated.idempotent)

        entry = _usage(occurred_at=NOW + 20, cost_nanos=usd_to_nanos("0.70"))
        committed = await self.repository.commit_reservation(
            request.reservation_id,
            entry,
            transitioned_at=NOW + 20,
        )
        replayed = await self.repository.commit_reservation(
            request.reservation_id,
            entry,
            transitioned_at=NOW + 20,
        )
        self.assertTrue(committed.committed)
        self.assertTrue(committed.overspent)
        self.assertFalse(replayed.committed)
        self.assertTrue(replayed.idempotent)

        restarted = SQLiteUsageLedgerRepository(self.database_path)
        await restarted.initialize()
        spend = await restarted.get_spend(since=0, api_key_id=KEY_ID)
        self.assertEqual(spend.calls, 1)
        self.assertEqual(spend.cost_nanos, usd_to_nanos("0.70"))

        with self.assertRaises(UsageLedgerConflict):
            await restarted.commit_reservation(
                request.reservation_id,
                dataclasses.replace(entry, cost_nanos=usd_to_nanos("0.71")),
                transitioned_at=NOW + 20,
            )

    async def test_release_and_expiry_are_terminal_and_idempotent(self):
        released_request = _reservation("a")
        await self.repository.reserve_budget(released_request)
        first_release = await self.repository.release_reservation(
            released_request.reservation_id,
            transitioned_at=NOW + 10,
        )
        repeated_release = await self.repository.release_reservation(
            released_request.reservation_id,
            transitioned_at=NOW + 10,
        )
        self.assertTrue(first_release.released)
        self.assertTrue(repeated_release.idempotent)
        with self.assertRaises(UsageLedgerStateConflict):
            await self.repository.commit_reservation(
                released_request.reservation_id,
                _usage(occurred_at=NOW + 20),
                transitioned_at=NOW + 20,
            )

        expired_request = _reservation("b", created_at=NOW + 20, expires_at=NOW + 30)
        await self.repository.reserve_budget(expired_request)
        reconciled = await self.repository.reconcile_expired(now=NOW + 31, limit=100)
        repeated = await self.repository.reconcile_expired(now=NOW + 31, limit=100)
        self.assertEqual(reconciled, 1)
        self.assertEqual(repeated, 0)

    async def test_conflicting_reservation_replay_and_expired_commit_fail_closed(self):
        request = _reservation("a")
        await self.repository.reserve_budget(request)
        with self.assertRaises(UsageLedgerConflict):
            await self.repository.reserve_budget(
                dataclasses.replace(request, estimated_cost_nanos=usd_to_nanos("0.50"))
            )
        with self.assertRaises(UsageLedgerStateConflict):
            await self.repository.commit_reservation(
                request.reservation_id,
                _usage(occurred_at=NOW + 61),
                transitioned_at=NOW + 61,
            )


class UsageLedgerSelectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_adapter_forwards_creation_to_selected_backend(self):
        expected = object()
        backend = Mock()
        backend.create_usage_ledger_repository = AsyncMock(return_value=expected)
        adapter = StorageAdapter()
        adapter._backend = backend
        adapter._initialized = True

        selected = await adapter.create_usage_ledger_repository()

        self.assertIs(selected, expected)
        backend.create_usage_ledger_repository.assert_awaited_once_with()

    async def test_sqlite_manager_constructs_and_initializes_repository(self):
        manager = SQLiteManager()
        manager._db_path = "credentials.db"
        manager._initialized = True
        repository = Mock()
        repository.initialize = AsyncMock()

        with patch(
            "core.storage.usage_ledger_sqlite.SQLiteUsageLedgerRepository",
            return_value=repository,
        ) as repository_class:
            selected = await manager.create_usage_ledger_repository()

        repository_class.assert_called_once_with("credentials.db")
        repository.initialize.assert_awaited_once_with()
        self.assertIs(selected, repository)


if __name__ == "__main__":
    unittest.main()
