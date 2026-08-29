"""Resumable one-page W4.13 migration runner behavior."""

from __future__ import annotations

import dataclasses
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.durable_migration import (
    AuthoritySide,
    DurableBackend,
    DurableFamily,
    DurableInventoryEntry,
    DurableRecord,
    MigrationPhase,
)
from core.durable_migration_runner import (
    CheckpointRevisionConflict,
    MigrationDuplicateConflict,
    MigrationRecordPage,
    MigrationRunner,
)

NOW = datetime(2026, 8, 29, 10, 0, tzinfo=timezone.utc)
PLAN_ID = "dmg_0123456789abcdef0123456789abcdef"
KEY = b"migration-integrity-key-32-bytes!!"
FAMILY = DurableFamily.CONFIGURATION


def _record(suffix: str, value: int) -> DurableRecord:
    return DurableRecord(
        family=FAMILY,
        logical_id=f"cfg_{suffix * 16}",
        schema_version=1,
        payload={"value": value},
    )


READY_INVENTORY = (DurableInventoryEntry(FAMILY, "test.source", True, True, "Test family."),)
BLOCKED_INVENTORY = (DurableInventoryEntry(FAMILY, "test.source", False, True, "Not ready."),)


class MemoryRecords:
    def __init__(self, records=()):
        self.records = {(record.family, record.logical_id): record for record in records}
        self.interrupt_after: int | None = None
        self.upsert_calls = 0

    async def read_page(self, *, family, cursor, limit):
        records = sorted(
            (record for (kind, _), record in self.records.items() if kind is family),
            key=lambda record: record.logical_id,
        )
        offset = int(cursor.removeprefix("cur_") or "0") if cursor else 0
        page = tuple(records[offset : offset + limit])
        next_offset = offset + len(page)
        next_cursor = f"cur_{next_offset:016d}" if next_offset < len(records) else None
        return MigrationRecordPage(records=page, next_cursor=next_cursor)

    async def upsert(self, record):
        self.upsert_calls += 1
        if self.interrupt_after is not None and self.upsert_calls > self.interrupt_after:
            self.interrupt_after = None
            raise RuntimeError("simulated interruption")
        identity = (record.family, record.logical_id)
        existing = self.records.get(identity)
        if existing is not None and existing != record:
            raise MigrationDuplicateConflict("Conflicting durable record.")
        self.records[identity] = record


class MemoryCheckpoints:
    def __init__(self):
        self.records = {}

    async def create(self, checkpoint):
        if checkpoint.plan_id in self.records:
            raise CheckpointRevisionConflict("Checkpoint already exists.")
        self.records[checkpoint.plan_id] = checkpoint
        return checkpoint

    async def get(self, plan_id):
        return self.records.get(plan_id)

    async def compare_and_set(self, checkpoint, *, expected_revision):
        current = self.records.get(checkpoint.plan_id)
        if current is None or current.revision != expected_revision:
            raise CheckpointRevisionConflict("Checkpoint revision conflict.")
        self.records[checkpoint.plan_id] = checkpoint
        return checkpoint


def _runner(source, target, checkpoints, *, inventory=READY_INVENTORY, batch_size=2):
    return MigrationRunner(
        source=source,
        target=target,
        checkpoints=checkpoints,
        integrity_key=KEY,
        inventory=inventory,
        batch_size=batch_size,
    )


class MigrationCopyTests(unittest.IsolatedAsyncioTestCase):
    async def test_interruption_leaves_source_authoritative_and_replays_page_idempotently(self):
        source = MemoryRecords((_record("1", 1), _record("2", 2)))
        target = MemoryRecords()
        target.interrupt_after = 1
        checkpoints = MemoryCheckpoints()
        runner = _runner(source, target, checkpoints)
        await runner.start(
            plan_id=PLAN_ID,
            source_backend=DurableBackend.SQLITE,
            target_backend=DurableBackend.POSTGRESQL,
            families=(FAMILY,),
            now=NOW,
        )

        with self.assertRaisesRegex(RuntimeError, "simulated interruption"):
            await runner.copy_next(PLAN_ID, now=NOW + timedelta(seconds=1))

        interrupted = await checkpoints.get(PLAN_ID)
        self.assertIs(interrupted.authority, AuthoritySide.SOURCE)
        self.assertIs(interrupted.phase, MigrationPhase.COPYING)
        self.assertEqual(interrupted.families[0].copied_count, 0)
        self.assertEqual(len(target.records), 1)

        resumed = await runner.copy_next(PLAN_ID, now=NOW + timedelta(seconds=2))
        self.assertIs(resumed.phase, MigrationPhase.VERIFYING)
        self.assertEqual(resumed.families[0].copied_count, 2)
        self.assertEqual(len(target.records), 2)
        self.assertEqual(target.upsert_calls, 4)

    async def test_conflicting_duplicate_stops_without_advancing_checkpoint(self):
        source = MemoryRecords((_record("1", 1),))
        target = MemoryRecords((_record("1", 999),))
        checkpoints = MemoryCheckpoints()
        runner = _runner(source, target, checkpoints)
        await runner.start(
            plan_id=PLAN_ID,
            source_backend=DurableBackend.SQLITE,
            target_backend=DurableBackend.MONGODB,
            families=(FAMILY,),
            now=NOW,
        )

        with self.assertRaises(MigrationDuplicateConflict):
            await runner.copy_next(PLAN_ID, now=NOW + timedelta(seconds=1))

        checkpoint = await checkpoints.get(PLAN_ID)
        self.assertIs(checkpoint.phase, MigrationPhase.COPYING)
        self.assertIs(checkpoint.authority, AuthoritySide.SOURCE)
        self.assertEqual(checkpoint.families[0].copied_count, 0)

    async def test_restart_resumes_from_persisted_opaque_cursor(self):
        source = MemoryRecords((_record("1", 1), _record("2", 2), _record("3", 3)))
        target = MemoryRecords()
        checkpoints = MemoryCheckpoints()
        first_process = _runner(source, target, checkpoints, batch_size=1)
        await first_process.start(
            plan_id=PLAN_ID,
            source_backend=DurableBackend.SQLITE,
            target_backend=DurableBackend.POSTGRESQL,
            families=(FAMILY,),
            now=NOW,
        )
        first_page = await first_process.copy_next(PLAN_ID, now=NOW + timedelta(seconds=1))
        self.assertEqual(first_page.families[0].copy_cursor, "cur_0000000000000001")

        restarted = _runner(source, target, checkpoints, batch_size=1)
        second_page = await restarted.copy_next(PLAN_ID, now=NOW + timedelta(seconds=2))
        self.assertEqual(second_page.families[0].copy_cursor, "cur_0000000000000002")
        completed = await restarted.copy_next(PLAN_ID, now=NOW + timedelta(seconds=3))
        self.assertIs(completed.phase, MigrationPhase.VERIFYING)
        self.assertEqual(completed.families[0].copied_count, 3)


class MigrationVerificationAndAuthorityTests(unittest.IsolatedAsyncioTestCase):
    async def _copied(self, *, inventory=READY_INVENTORY):
        source = MemoryRecords((_record("1", 1), _record("2", 2)))
        target = MemoryRecords()
        checkpoints = MemoryCheckpoints()
        runner = _runner(source, target, checkpoints, inventory=inventory)
        await runner.start(
            plan_id=PLAN_ID,
            source_backend=DurableBackend.SQLITE,
            target_backend=DurableBackend.POSTGRESQL,
            families=(FAMILY,),
            now=NOW,
        )
        await runner.copy_next(PLAN_ID, now=NOW + timedelta(seconds=1))
        return runner, source, target, checkpoints

    async def test_checksum_mismatch_stays_in_verification_with_source_authoritative(self):
        runner, _source, target, _checkpoints = await self._copied()
        target.records[(FAMILY, _record("2", 2).logical_id)] = _record("2", 7)

        checkpoint = await runner.verify(PLAN_ID, now=NOW + timedelta(seconds=2))

        self.assertIs(checkpoint.phase, MigrationPhase.VERIFYING)
        self.assertIs(checkpoint.authority, AuthoritySide.SOURCE)
        self.assertEqual(checkpoint.failure_code, "verification_mismatch")
        self.assertFalse(checkpoint.families[0].verified)
        self.assertNotEqual(
            checkpoint.families[0].source_checksum,
            checkpoint.families[0].target_checksum,
        )

    async def test_readiness_gap_blocks_switch_even_when_checksums_match(self):
        runner, _source, _target, _checkpoints = await self._copied(inventory=BLOCKED_INVENTORY)

        checkpoint = await runner.verify(PLAN_ID, now=NOW + timedelta(seconds=2))

        self.assertIs(checkpoint.phase, MigrationPhase.VERIFYING)
        self.assertIs(checkpoint.authority, AuthoritySide.SOURCE)
        self.assertEqual(checkpoint.failure_code, "inventory_not_ready")
        self.assertTrue(checkpoint.families[0].verified)

    async def test_verified_plan_switches_only_explicitly_and_rolls_back_through_barrier(self):
        runner, _source, _target, _checkpoints = await self._copied()
        ready = await runner.verify(PLAN_ID, now=NOW + timedelta(seconds=2))
        self.assertIs(ready.phase, MigrationPhase.READY_TO_SWITCH)
        self.assertIs(ready.authority, AuthoritySide.SOURCE)

        target = await runner.activate_target(
            PLAN_ID,
            expected_revision=ready.revision,
            now=NOW + timedelta(seconds=3),
        )
        self.assertIs(target.phase, MigrationPhase.TARGET_AUTHORITATIVE)
        self.assertIs(target.authority, AuthoritySide.TARGET)

        rollback = await runner.prepare_rollback(
            PLAN_ID,
            expected_revision=target.revision,
            now=NOW + timedelta(seconds=4),
        )
        self.assertIs(rollback.phase, MigrationPhase.ROLLBACK_READY)
        self.assertIs(rollback.authority, AuthoritySide.TARGET)
        with self.assertRaises(ValueError):
            await runner.complete_rollback(
                PLAN_ID,
                expected_revision=rollback.revision,
                reconciliation_complete=False,
                now=NOW + timedelta(seconds=5),
            )
        completed = await runner.complete_rollback(
            PLAN_ID,
            expected_revision=rollback.revision,
            reconciliation_complete=True,
            now=NOW + timedelta(seconds=5),
        )
        self.assertIs(completed.phase, MigrationPhase.ROLLED_BACK)
        self.assertIs(completed.authority, AuthoritySide.SOURCE)

    async def test_checkpoint_compare_and_set_prevents_stale_authority_switch(self):
        runner, _source, _target, checkpoints = await self._copied()
        ready = await runner.verify(PLAN_ID, now=NOW + timedelta(seconds=2))
        checkpoints.records[PLAN_ID] = dataclasses.replace(
            ready,
            revision=ready.revision + 1,
            updated_at=(NOW + timedelta(seconds=3)).isoformat(),
        )

        with self.assertRaises(CheckpointRevisionConflict):
            await runner.activate_target(
                PLAN_ID,
                expected_revision=ready.revision,
                now=NOW + timedelta(seconds=4),
            )


if __name__ == "__main__":
    unittest.main()
