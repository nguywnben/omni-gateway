"""Bounded, resumable W4.13 durable-record copy and authority state machine."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Protocol

from core.durable_migration import (
    MIGRATION_SCHEMA_VERSION,
    AuthoritySide,
    DurableBackend,
    DurableFamily,
    DurableInventoryEntry,
    DurableRecord,
    FamilyProgress,
    MigrationCheckpoint,
    MigrationPhase,
    compute_records_digest,
)

MIN_BATCH_SIZE = 1
MAX_BATCH_SIZE = 1_000


class MigrationError(RuntimeError):
    """Generic migration failure that contains no durable record payload."""


class MigrationDuplicateConflict(MigrationError):
    """A target logical key exists with different canonical content."""


class CheckpointRevisionConflict(MigrationError):
    """The checkpoint changed since the caller read it."""


class CheckpointNotFound(MigrationError):
    """The requested migration checkpoint does not exist."""


@dataclass(frozen=True, slots=True)
class MigrationRecordPage:
    records: tuple[DurableRecord, ...]
    next_cursor: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.records, tuple) or any(
            type(record) is not DurableRecord for record in self.records
        ):
            raise ValueError("Migration record page is invalid.")
        if self.next_cursor is not None and not isinstance(self.next_cursor, str):
            raise ValueError("Migration record cursor is invalid.")


class MigrationRecordReader(Protocol):
    async def read_page(
        self,
        *,
        family: DurableFamily,
        cursor: str | None,
        limit: int,
    ) -> MigrationRecordPage: ...


class MigrationRecordWriter(Protocol):
    async def upsert(self, record: DurableRecord) -> None: ...


class MigrationCheckpointRepository(Protocol):
    async def create(self, checkpoint: MigrationCheckpoint) -> MigrationCheckpoint: ...

    async def get(self, plan_id: str) -> MigrationCheckpoint | None: ...

    async def compare_and_set(
        self,
        checkpoint: MigrationCheckpoint,
        *,
        expected_revision: int,
    ) -> MigrationCheckpoint: ...


class MigrationRunner:
    """Execute one bounded copy page per call and never switch authority automatically."""

    def __init__(
        self,
        *,
        source: MigrationRecordReader,
        target: MigrationRecordReader | MigrationRecordWriter,
        checkpoints: MigrationCheckpointRepository,
        integrity_key: bytes,
        inventory: tuple[DurableInventoryEntry, ...],
        batch_size: int = 100,
    ) -> None:
        if type(batch_size) is not int or not MIN_BATCH_SIZE <= batch_size <= MAX_BATCH_SIZE:
            raise ValueError("Migration batch size is invalid.")
        if not isinstance(integrity_key, bytes) or len(integrity_key) < 32:
            raise ValueError("Migration integrity key is too short.")
        if not isinstance(inventory, tuple) or not inventory:
            raise ValueError("Migration inventory is invalid.")
        if any(type(entry) is not DurableInventoryEntry for entry in inventory):
            raise ValueError("Migration inventory entry is invalid.")
        inventory_families = [entry.family for entry in inventory]
        if len(set(inventory_families)) != len(inventory_families):
            raise ValueError("Migration inventory contains a duplicate family.")
        if not hasattr(target, "read_page") or not hasattr(target, "upsert"):
            raise ValueError("Migration target does not satisfy the record contract.")
        self._source = source
        self._target = target
        self._checkpoints = checkpoints
        self._integrity_key = integrity_key
        self._inventory = {entry.family: entry for entry in inventory}
        self._batch_size = batch_size

    async def start(
        self,
        *,
        plan_id: str,
        source_backend: DurableBackend,
        target_backend: DurableBackend,
        families: tuple[DurableFamily, ...],
        now: datetime,
    ) -> MigrationCheckpoint:
        if not isinstance(families, tuple) or not families:
            raise ValueError("Migration plan families are invalid.")
        if any(type(family) is not DurableFamily for family in families):
            raise ValueError("Migration plan family is invalid.")
        if len(set(families)) != len(families):
            raise ValueError("Migration plan contains a duplicate family.")
        if set(families) != set(self._inventory):
            raise ValueError("Migration plan must cover the complete inventory.")
        timestamp = self._now(now)
        checkpoint = MigrationCheckpoint(
            schema_version=MIGRATION_SCHEMA_VERSION,
            plan_id=plan_id,
            source_backend=source_backend,
            target_backend=target_backend,
            phase=MigrationPhase.PLANNED,
            authority=AuthoritySide.SOURCE,
            revision=1,
            families=tuple(
                FamilyProgress(
                    family=family,
                    copy_cursor=None,
                    copied_count=0,
                    copy_complete=False,
                    source_count=None,
                    target_count=None,
                    source_checksum=None,
                    target_checksum=None,
                    verified=False,
                )
                for family in families
            ),
            failure_code=None,
            created_at=timestamp,
            updated_at=timestamp,
        )
        return await self._checkpoints.create(checkpoint)

    async def copy_next(self, plan_id: str, *, now: datetime) -> MigrationCheckpoint:
        checkpoint = await self._require_checkpoint(plan_id)
        if checkpoint.phase is MigrationPhase.PLANNED:
            checkpoint = await self._save(
                replace(
                    checkpoint,
                    phase=MigrationPhase.COPYING,
                    revision=checkpoint.revision + 1,
                    updated_at=self._now(now),
                ),
                expected_revision=checkpoint.revision,
            )
        if checkpoint.phase is not MigrationPhase.COPYING:
            raise ValueError("Migration is not in the copying phase.")

        index = next(
            (
                position
                for position, progress in enumerate(checkpoint.families)
                if not progress.copy_complete
            ),
            None,
        )
        if index is None:
            return await self._enter_verification(checkpoint, now=now)
        progress = checkpoint.families[index]
        page = await self._source.read_page(
            family=progress.family,
            cursor=progress.copy_cursor,
            limit=self._batch_size,
        )
        self._validate_page(page, family=progress.family, previous_cursor=progress.copy_cursor)
        for record in page.records:
            await self._target.upsert(record)

        copy_complete = page.next_cursor is None
        updated_progress = replace(
            progress,
            copy_cursor=page.next_cursor,
            copied_count=progress.copied_count + len(page.records),
            copy_complete=copy_complete,
        )
        families = list(checkpoint.families)
        families[index] = updated_progress
        all_complete = all(item.copy_complete for item in families)
        updated = replace(
            checkpoint,
            phase=(MigrationPhase.VERIFYING if all_complete else MigrationPhase.COPYING),
            revision=checkpoint.revision + 1,
            families=tuple(families),
            failure_code=None,
            updated_at=self._now(now),
        )
        return await self._save(updated, expected_revision=checkpoint.revision)

    async def verify(self, plan_id: str, *, now: datetime) -> MigrationCheckpoint:
        checkpoint = await self._require_checkpoint(plan_id)
        if checkpoint.phase is not MigrationPhase.VERIFYING:
            raise ValueError("Migration is not in the verification phase.")

        verified_progress: list[FamilyProgress] = []
        all_matching = True
        for progress in checkpoint.families:
            source_records = await self._read_all(self._source, progress.family)
            target_records = await self._read_all(self._target, progress.family)
            source_checksum = compute_records_digest(
                source_records, integrity_key=self._integrity_key
            )
            target_checksum = compute_records_digest(
                target_records, integrity_key=self._integrity_key
            )
            matches = len(source_records) == len(target_records) and hmac_compare(
                source_checksum, target_checksum
            )
            all_matching = all_matching and matches
            verified_progress.append(
                replace(
                    progress,
                    source_count=len(source_records),
                    target_count=len(target_records),
                    source_checksum=source_checksum,
                    target_checksum=target_checksum,
                    verified=matches,
                )
            )

        inventory_ready = all(entry.switch_ready for entry in self._inventory.values())
        ready = all_matching and inventory_ready
        failure_code = None
        if not all_matching:
            failure_code = "verification_mismatch"
        elif not inventory_ready:
            failure_code = "inventory_not_ready"
        updated = replace(
            checkpoint,
            phase=(MigrationPhase.READY_TO_SWITCH if ready else MigrationPhase.VERIFYING),
            revision=checkpoint.revision + 1,
            families=tuple(verified_progress),
            failure_code=failure_code,
            updated_at=self._now(now),
        )
        return await self._save(updated, expected_revision=checkpoint.revision)

    async def activate_target(
        self,
        plan_id: str,
        *,
        expected_revision: int,
        now: datetime,
    ) -> MigrationCheckpoint:
        checkpoint = await self._require_expected(plan_id, expected_revision)
        if checkpoint.phase is not MigrationPhase.READY_TO_SWITCH:
            raise ValueError("Migration is not ready to switch authority.")
        updated = replace(
            checkpoint,
            phase=MigrationPhase.TARGET_AUTHORITATIVE,
            authority=AuthoritySide.TARGET,
            revision=checkpoint.revision + 1,
            updated_at=self._now(now),
        )
        return await self._save(updated, expected_revision=expected_revision)

    async def prepare_rollback(
        self,
        plan_id: str,
        *,
        expected_revision: int,
        now: datetime,
    ) -> MigrationCheckpoint:
        checkpoint = await self._require_expected(plan_id, expected_revision)
        if checkpoint.phase is not MigrationPhase.TARGET_AUTHORITATIVE:
            raise ValueError("Migration target is not authoritative.")
        updated = replace(
            checkpoint,
            phase=MigrationPhase.ROLLBACK_READY,
            revision=checkpoint.revision + 1,
            updated_at=self._now(now),
        )
        return await self._save(updated, expected_revision=expected_revision)

    async def complete_rollback(
        self,
        plan_id: str,
        *,
        expected_revision: int,
        reconciliation_complete: bool,
        now: datetime,
    ) -> MigrationCheckpoint:
        if type(reconciliation_complete) is not bool or not reconciliation_complete:
            raise ValueError("Rollback reconciliation barrier is incomplete.")
        checkpoint = await self._require_expected(plan_id, expected_revision)
        if checkpoint.phase is not MigrationPhase.ROLLBACK_READY:
            raise ValueError("Migration is not ready to roll back.")
        updated = replace(
            checkpoint,
            phase=MigrationPhase.ROLLED_BACK,
            authority=AuthoritySide.SOURCE,
            revision=checkpoint.revision + 1,
            updated_at=self._now(now),
        )
        return await self._save(updated, expected_revision=expected_revision)

    async def _enter_verification(
        self, checkpoint: MigrationCheckpoint, *, now: datetime
    ) -> MigrationCheckpoint:
        updated = replace(
            checkpoint,
            phase=MigrationPhase.VERIFYING,
            revision=checkpoint.revision + 1,
            updated_at=self._now(now),
        )
        return await self._save(updated, expected_revision=checkpoint.revision)

    async def _read_all(
        self, reader: MigrationRecordReader, family: DurableFamily
    ) -> tuple[DurableRecord, ...]:
        cursor: str | None = None
        records: list[DurableRecord] = []
        seen_ids: set[str] = set()
        seen_cursors: set[str] = set()
        while True:
            page = await reader.read_page(
                family=family,
                cursor=cursor,
                limit=self._batch_size,
            )
            self._validate_page(page, family=family, previous_cursor=cursor)
            for record in page.records:
                if record.logical_id in seen_ids:
                    raise MigrationError("Migration scan returned a duplicate logical record.")
                seen_ids.add(record.logical_id)
                records.append(record)
            if page.next_cursor is None:
                return tuple(records)
            if page.next_cursor in seen_cursors:
                raise MigrationError("Migration scan cursor did not advance.")
            seen_cursors.add(page.next_cursor)
            cursor = page.next_cursor

    def _validate_page(
        self,
        page: MigrationRecordPage,
        *,
        family: DurableFamily,
        previous_cursor: str | None,
    ) -> None:
        if type(page) is not MigrationRecordPage or len(page.records) > self._batch_size:
            raise MigrationError("Migration reader violated the bounded page contract.")
        if any(record.family is not family for record in page.records):
            raise MigrationError("Migration reader returned the wrong durable family.")
        identities = [record.logical_id for record in page.records]
        if len(set(identities)) != len(identities):
            raise MigrationError("Migration page contains a duplicate logical record.")
        if page.next_cursor is not None and page.next_cursor == previous_cursor:
            raise MigrationError("Migration scan cursor did not advance.")
        if page.next_cursor is not None and not page.records:
            raise MigrationError("Migration reader returned an empty continuation page.")

    async def _require_checkpoint(self, plan_id: str) -> MigrationCheckpoint:
        checkpoint = await self._checkpoints.get(plan_id)
        if checkpoint is None:
            raise CheckpointNotFound("Migration checkpoint was not found.")
        if type(checkpoint) is not MigrationCheckpoint:
            raise MigrationError("Migration checkpoint repository returned invalid data.")
        return checkpoint

    async def _require_expected(self, plan_id: str, expected_revision: int) -> MigrationCheckpoint:
        checkpoint = await self._require_checkpoint(plan_id)
        if type(expected_revision) is not int or checkpoint.revision != expected_revision:
            raise CheckpointRevisionConflict("Migration checkpoint revision conflict.")
        return checkpoint

    async def _save(
        self, checkpoint: MigrationCheckpoint, *, expected_revision: int
    ) -> MigrationCheckpoint:
        return await self._checkpoints.compare_and_set(
            checkpoint, expected_revision=expected_revision
        )

    @staticmethod
    def _now(value: datetime) -> str:
        if not isinstance(value, datetime) or value.tzinfo is None:
            raise ValueError("Migration timestamp is invalid.")
        return value.astimezone(timezone.utc).isoformat()


def hmac_compare(left: str, right: str) -> bool:
    """Constant-time comparison kept local to avoid exposing digest implementation details."""

    from hmac import compare_digest

    return compare_digest(left, right)
