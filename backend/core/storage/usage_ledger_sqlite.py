"""SQLite W4.14 durable usage ledger and hard-budget journal repository."""

from __future__ import annotations

import json
import sqlite3
from contextlib import asynccontextmanager
from dataclasses import replace
from pathlib import Path

import aiosqlite
from core.usage_ledger import (
    BudgetCommitResult,
    BudgetReleaseResult,
    BudgetReservation,
    BudgetReservationDecision,
    BudgetReservationRequest,
    BudgetReservationState,
    SpendSnapshot,
    UsageAppendResult,
    UsageLedgerConflict,
    UsageLedgerCorrupt,
    UsageLedgerEntry,
    UsageLedgerStateConflict,
    budget_reservation_from_record,
    usage_entry_from_record,
)

DAILY_WINDOW_SECONDS = 86_400.0
MONTHLY_WINDOW_SECONDS = 30 * DAILY_WINDOW_SECONDS
MAX_RECONCILE_BATCH = 1_000

_COLUMNS = (
    "record_id",
    "kind",
    "state",
    "revision",
    "key_id",
    "created_at",
    "expires_at",
    "transitioned_at",
    "estimated_cost_nanos",
    "daily_budget_nanos",
    "monthly_budget_nanos",
    "event_id",
    "occurred_at",
    "credential_ref",
    "provider",
    "success",
    "total_tokens",
    "cost_nanos",
    "api_key_id",
    "payload",
)


class SQLiteUsageLedgerRepository:
    """One-row-per-event/reservation repository with atomic per-database writes."""

    def __init__(self, database_path: str) -> None:
        if not isinstance(database_path, str) or not database_path.strip():
            raise ValueError("Usage ledger database path is invalid.")
        self._database_path = database_path
        self._initialized = False

    async def initialize(self) -> None:
        Path(self._database_path).parent.mkdir(parents=True, exist_ok=True)
        async with self._connection(allow_initializing=True) as db:
            await db.execute("PRAGMA journal_mode=WAL")
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS durable_usage_ledger (
                    record_id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL CHECK (kind IN ('usage', 'reservation')),
                    state TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    key_id TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL,
                    transitioned_at REAL,
                    estimated_cost_nanos INTEGER,
                    daily_budget_nanos INTEGER,
                    monthly_budget_nanos INTEGER,
                    event_id TEXT,
                    occurred_at REAL,
                    credential_ref TEXT,
                    provider TEXT,
                    success INTEGER,
                    total_tokens INTEGER,
                    cost_nanos INTEGER,
                    api_key_id TEXT,
                    payload TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_durable_usage_event
                ON durable_usage_ledger(event_id)
                WHERE event_id IS NOT NULL
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_durable_usage_spend
                ON durable_usage_ledger(api_key_id, occurred_at)
                WHERE cost_nanos IS NOT NULL
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_durable_usage_active_budget
                ON durable_usage_ledger(key_id, state, expires_at)
                WHERE kind = 'reservation'
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_durable_usage_credential
                ON durable_usage_ledger(credential_ref, occurred_at)
                WHERE occurred_at IS NOT NULL
                """
            )
            await db.commit()
        self._initialized = True

    async def append_usage(self, entry: UsageLedgerEntry) -> UsageAppendResult:
        self._require_entry(entry)
        async with self._connection() as db:
            await db.execute("BEGIN IMMEDIATE")
            try:
                existing = await self._get_locked(db, entry.event_id)
                if existing is not None:
                    decoded = self._decode_row(existing)
                    if decoded != entry:
                        raise UsageLedgerConflict("Usage event idempotency conflict.")
                    await db.rollback()
                    return UsageAppendResult(False, True)
                await self._insert_usage_locked(db, entry)
                await db.commit()
                return UsageAppendResult(True, False)
            except Exception:
                await db.rollback()
                raise

    async def reserve_budget(self, request: BudgetReservationRequest) -> BudgetReservationDecision:
        if type(request) is not BudgetReservationRequest:
            raise ValueError("Budget reservation request is invalid.")
        async with self._connection() as db:
            await db.execute("BEGIN IMMEDIATE")
            try:
                await self._expire_locked(db, now=request.created_at, limit=MAX_RECONCILE_BATCH)
                existing = await self._get_locked(db, request.reservation_id)
                if existing is not None:
                    decoded = self._decode_reservation(existing)
                    if self._request_from_reservation(decoded) != request:
                        raise UsageLedgerConflict("Budget reservation idempotency conflict.")
                    await db.rollback()
                    return BudgetReservationDecision(
                        True,
                        request.reservation_id,
                        idempotent=True,
                    )

                active_cost = await self._active_cost_locked(
                    db,
                    key_id=request.key_id,
                    now=request.created_at,
                )
                if request.daily_budget_nanos is not None:
                    committed = await self._committed_cost_locked(
                        db,
                        key_id=request.key_id,
                        since=request.created_at - DAILY_WINDOW_SECONDS,
                    )
                    if (
                        committed + active_cost + request.estimated_cost_nanos
                        > request.daily_budget_nanos
                    ):
                        await db.rollback()
                        return BudgetReservationDecision(
                            False,
                            request.reservation_id,
                            reason="daily_budget",
                        )
                if request.monthly_budget_nanos is not None:
                    committed = await self._committed_cost_locked(
                        db,
                        key_id=request.key_id,
                        since=request.created_at - MONTHLY_WINDOW_SECONDS,
                    )
                    if (
                        committed + active_cost + request.estimated_cost_nanos
                        > request.monthly_budget_nanos
                    ):
                        await db.rollback()
                        return BudgetReservationDecision(
                            False,
                            request.reservation_id,
                            reason="monthly_budget",
                        )
                await self._insert_reservation_locked(db, BudgetReservation.active(request))
                await db.commit()
                return BudgetReservationDecision(True, request.reservation_id)
            except Exception:
                await db.rollback()
                raise

    async def commit_reservation(
        self,
        reservation_id: str,
        usage: UsageLedgerEntry,
        *,
        transitioned_at: float,
    ) -> BudgetCommitResult:
        self._require_entry(usage)
        async with self._connection() as db:
            await db.execute("BEGIN IMMEDIATE")
            try:
                row = await self._get_locked(db, reservation_id)
                if row is None:
                    raise UsageLedgerStateConflict("Budget reservation state conflict.")
                reservation = self._decode_reservation(row)
                if reservation.state is BudgetReservationState.COMMITTED:
                    if reservation.usage != usage:
                        raise UsageLedgerConflict("Budget commit idempotency conflict.")
                    await db.rollback()
                    return BudgetCommitResult(False, idempotent=True)
                if reservation.state is not BudgetReservationState.ACTIVE:
                    raise UsageLedgerStateConflict("Budget reservation state conflict.")
                if usage.api_key_id != reservation.key_id:
                    raise UsageLedgerConflict("Budget commit attribution conflict.")
                if transitioned_at >= reservation.expires_at:
                    expired = replace(
                        reservation,
                        state=BudgetReservationState.EXPIRED,
                        revision=2,
                        transitioned_at=transitioned_at,
                    )
                    await self._update_reservation_locked(db, expired)
                    await db.commit()
                    raise UsageLedgerStateConflict("Budget reservation expired before commit.")
                event_row = await self._get_by_event_locked(db, usage.event_id)
                if event_row is not None:
                    raise UsageLedgerConflict("Usage event idempotency conflict.")

                other_active = await self._active_cost_locked(
                    db,
                    key_id=reservation.key_id,
                    now=transitioned_at,
                    exclude_record_id=reservation.reservation_id,
                )
                overspent = usage.cost_nanos > reservation.estimated_cost_nanos
                if reservation.daily_budget_nanos is not None:
                    daily = await self._committed_cost_locked(
                        db,
                        key_id=reservation.key_id,
                        since=transitioned_at - DAILY_WINDOW_SECONDS,
                    )
                    overspent = overspent or (
                        daily + other_active + usage.cost_nanos > reservation.daily_budget_nanos
                    )
                if reservation.monthly_budget_nanos is not None:
                    monthly = await self._committed_cost_locked(
                        db,
                        key_id=reservation.key_id,
                        since=transitioned_at - MONTHLY_WINDOW_SECONDS,
                    )
                    overspent = overspent or (
                        monthly + other_active + usage.cost_nanos > reservation.monthly_budget_nanos
                    )
                committed = replace(
                    reservation,
                    state=BudgetReservationState.COMMITTED,
                    revision=2,
                    transitioned_at=transitioned_at,
                    usage=usage,
                )
                await self._update_reservation_locked(db, committed)
                await db.commit()
                return BudgetCommitResult(True, overspent=overspent)
            except UsageLedgerStateConflict:
                if db.in_transaction:
                    await db.rollback()
                raise
            except Exception:
                await db.rollback()
                raise

    async def release_reservation(
        self,
        reservation_id: str,
        *,
        transitioned_at: float,
    ) -> BudgetReleaseResult:
        async with self._connection() as db:
            await db.execute("BEGIN IMMEDIATE")
            try:
                row = await self._get_locked(db, reservation_id)
                if row is None:
                    raise UsageLedgerStateConflict("Budget reservation state conflict.")
                reservation = self._decode_reservation(row)
                if reservation.state is BudgetReservationState.RELEASED:
                    await db.rollback()
                    return BudgetReleaseResult(False, idempotent=True)
                if reservation.state is not BudgetReservationState.ACTIVE:
                    raise UsageLedgerStateConflict("Budget reservation state conflict.")
                released = replace(
                    reservation,
                    state=BudgetReservationState.RELEASED,
                    revision=2,
                    transitioned_at=transitioned_at,
                )
                await self._update_reservation_locked(db, released)
                await db.commit()
                return BudgetReleaseResult(True)
            except Exception:
                await db.rollback()
                raise

    async def reconcile_expired(self, *, now: float, limit: int) -> int:
        if type(limit) is not int or not 1 <= limit <= MAX_RECONCILE_BATCH:
            raise ValueError("Usage reconciliation limit is invalid.")
        async with self._connection() as db:
            await db.execute("BEGIN IMMEDIATE")
            try:
                changed = await self._expire_locked(db, now=now, limit=limit)
                await db.commit()
                return changed
            except Exception:
                await db.rollback()
                raise

    async def get_spend(self, *, since: float, api_key_id: str = "") -> SpendSnapshot:
        self._ensure_initialized()
        where = "occurred_at >= ? AND cost_nanos IS NOT NULL"
        parameters: list[object] = [float(since)]
        if api_key_id:
            where += " AND api_key_id = ?"
            parameters.append(api_key_id)
        async with self._connection() as db:
            row = await (
                await db.execute(
                    f"""
                    SELECT COALESCE(SUM(cost_nanos), 0),
                           COALESCE(SUM(total_tokens), 0),
                           COUNT(*)
                    FROM durable_usage_ledger
                    WHERE {where}
                    """,
                    tuple(parameters),
                )
            ).fetchone()
        return SpendSnapshot(
            cost_nanos=int(row[0] or 0),
            total_tokens=int(row[1] or 0),
            calls=int(row[2] or 0),
            available=True,
        )

    @asynccontextmanager
    async def _connection(self, *, allow_initializing: bool = False):
        self._ensure_initialized(allow_initializing=allow_initializing)
        connection = await aiosqlite.connect(self._database_path, isolation_level=None)
        connection.row_factory = aiosqlite.Row
        await connection.execute("PRAGMA busy_timeout=5000")
        try:
            yield connection
        finally:
            await connection.close()

    def _ensure_initialized(self, *, allow_initializing: bool = False) -> None:
        if not self._initialized and not allow_initializing:
            raise RuntimeError("Usage ledger repository is not initialized.")

    @staticmethod
    def _require_entry(entry: UsageLedgerEntry) -> None:
        if type(entry) is not UsageLedgerEntry:
            raise ValueError("Usage ledger entry is invalid.")

    @staticmethod
    def _payload(value: UsageLedgerEntry | BudgetReservation) -> str:
        return json.dumps(
            value.to_record(),
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    async def _get_locked(self, db: aiosqlite.Connection, record_id: str):
        return await (
            await db.execute(
                f"SELECT {', '.join(_COLUMNS)} FROM durable_usage_ledger WHERE record_id = ?",
                (record_id,),
            )
        ).fetchone()

    async def _get_by_event_locked(self, db: aiosqlite.Connection, event_id: str):
        return await (
            await db.execute(
                f"SELECT {', '.join(_COLUMNS)} FROM durable_usage_ledger WHERE event_id = ?",
                (event_id,),
            )
        ).fetchone()

    @staticmethod
    def _request_from_reservation(
        reservation: BudgetReservation,
    ) -> BudgetReservationRequest:
        return BudgetReservationRequest(
            schema_version=reservation.schema_version,
            reservation_id=reservation.reservation_id,
            key_id=reservation.key_id,
            created_at=reservation.created_at,
            expires_at=reservation.expires_at,
            estimated_tokens=reservation.estimated_tokens,
            estimated_cost_nanos=reservation.estimated_cost_nanos,
            daily_budget_nanos=reservation.daily_budget_nanos,
            monthly_budget_nanos=reservation.monthly_budget_nanos,
        )

    async def _insert_usage_locked(self, db: aiosqlite.Connection, entry: UsageLedgerEntry) -> None:
        try:
            await db.execute(
                """
                INSERT INTO durable_usage_ledger (
                    record_id, kind, state, revision, key_id, created_at,
                    event_id, occurred_at, credential_ref, provider, success,
                    total_tokens, cost_nanos, api_key_id, payload
                ) VALUES (?, 'usage', 'committed', 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.event_id,
                    entry.api_key_id,
                    entry.occurred_at,
                    entry.event_id,
                    entry.occurred_at,
                    entry.credential_ref,
                    entry.provider,
                    1 if entry.success else 0,
                    entry.total_tokens,
                    entry.cost_nanos,
                    entry.api_key_id,
                    self._payload(entry),
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise UsageLedgerConflict("Usage event idempotency conflict.") from exc

    async def _insert_reservation_locked(
        self, db: aiosqlite.Connection, reservation: BudgetReservation
    ) -> None:
        try:
            await db.execute(
                """
                INSERT INTO durable_usage_ledger (
                    record_id, kind, state, revision, key_id, created_at, expires_at,
                    estimated_cost_nanos, daily_budget_nanos, monthly_budget_nanos, payload
                ) VALUES (?, 'reservation', ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    reservation.reservation_id,
                    reservation.state.value,
                    reservation.revision,
                    reservation.key_id,
                    reservation.created_at,
                    reservation.expires_at,
                    reservation.estimated_cost_nanos,
                    reservation.daily_budget_nanos,
                    reservation.monthly_budget_nanos,
                    self._payload(reservation),
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise UsageLedgerConflict("Budget reservation idempotency conflict.") from exc

    async def _update_reservation_locked(
        self, db: aiosqlite.Connection, reservation: BudgetReservation
    ) -> None:
        usage = reservation.usage
        try:
            cursor = await db.execute(
                """
                UPDATE durable_usage_ledger
                SET state = ?, revision = ?, transitioned_at = ?,
                    event_id = ?, occurred_at = ?, credential_ref = ?, provider = ?,
                    success = ?, total_tokens = ?, cost_nanos = ?, api_key_id = ?, payload = ?
                WHERE record_id = ? AND kind = 'reservation' AND revision = 1
                """,
                (
                    reservation.state.value,
                    reservation.revision,
                    reservation.transitioned_at,
                    None if usage is None else usage.event_id,
                    None if usage is None else usage.occurred_at,
                    None if usage is None else usage.credential_ref,
                    None if usage is None else usage.provider,
                    None if usage is None else (1 if usage.success else 0),
                    None if usage is None else usage.total_tokens,
                    None if usage is None else usage.cost_nanos,
                    None if usage is None else usage.api_key_id,
                    self._payload(reservation),
                    reservation.reservation_id,
                ),
            )
        except sqlite3.IntegrityError as exc:
            raise UsageLedgerConflict("Usage event idempotency conflict.") from exc
        if cursor.rowcount != 1:
            raise UsageLedgerStateConflict("Budget reservation revision conflict.")

    async def _expire_locked(self, db: aiosqlite.Connection, *, now: float, limit: int) -> int:
        rows = await (
            await db.execute(
                f"""
                SELECT {", ".join(_COLUMNS)}
                FROM durable_usage_ledger
                WHERE kind = 'reservation' AND state = 'active' AND expires_at <= ?
                ORDER BY expires_at, record_id
                LIMIT ?
                """,
                (float(now), limit),
            )
        ).fetchall()
        for row in rows:
            reservation = self._decode_reservation(row)
            expired = replace(
                reservation,
                state=BudgetReservationState.EXPIRED,
                revision=2,
                transitioned_at=max(float(now), reservation.expires_at),
            )
            await self._update_reservation_locked(db, expired)
        return len(rows)

    async def _active_cost_locked(
        self,
        db: aiosqlite.Connection,
        *,
        key_id: str,
        now: float,
        exclude_record_id: str = "",
    ) -> int:
        where = "kind = 'reservation' AND state = 'active' AND key_id = ? AND expires_at > ?"
        parameters: list[object] = [key_id, float(now)]
        if exclude_record_id:
            where += " AND record_id <> ?"
            parameters.append(exclude_record_id)
        row = await (
            await db.execute(
                f"""
                SELECT COALESCE(SUM(estimated_cost_nanos), 0)
                FROM durable_usage_ledger WHERE {where}
                """,
                tuple(parameters),
            )
        ).fetchone()
        return int(row[0] or 0)

    async def _committed_cost_locked(
        self, db: aiosqlite.Connection, *, key_id: str, since: float
    ) -> int:
        row = await (
            await db.execute(
                """
                SELECT COALESCE(SUM(cost_nanos), 0)
                FROM durable_usage_ledger
                WHERE api_key_id = ? AND occurred_at >= ? AND cost_nanos IS NOT NULL
                """,
                (key_id, float(since)),
            )
        ).fetchone()
        return int(row[0] or 0)

    def _decode_row(self, row: aiosqlite.Row) -> UsageLedgerEntry | BudgetReservation:
        try:
            payload = json.loads(row["payload"])
            if row["kind"] == "usage":
                entry = usage_entry_from_record(payload)
                expected = (
                    entry.event_id,
                    "usage",
                    "committed",
                    1,
                    entry.api_key_id,
                    entry.occurred_at,
                    entry.event_id,
                    entry.occurred_at,
                    entry.credential_ref,
                    entry.provider,
                    1 if entry.success else 0,
                    entry.total_tokens,
                    entry.cost_nanos,
                    entry.api_key_id,
                )
                actual = (
                    row["record_id"],
                    row["kind"],
                    row["state"],
                    row["revision"],
                    row["key_id"],
                    row["created_at"],
                    row["event_id"],
                    row["occurred_at"],
                    row["credential_ref"],
                    row["provider"],
                    row["success"],
                    row["total_tokens"],
                    row["cost_nanos"],
                    row["api_key_id"],
                )
                if actual != expected:
                    raise ValueError
                return entry
            if row["kind"] == "reservation":
                reservation = budget_reservation_from_record(payload)
                usage = reservation.usage
                expected = (
                    reservation.reservation_id,
                    reservation.state.value,
                    reservation.revision,
                    reservation.key_id,
                    reservation.created_at,
                    reservation.expires_at,
                    reservation.transitioned_at,
                    reservation.estimated_cost_nanos,
                    reservation.daily_budget_nanos,
                    reservation.monthly_budget_nanos,
                    None if usage is None else usage.event_id,
                    None if usage is None else usage.occurred_at,
                    None if usage is None else usage.credential_ref,
                    None if usage is None else usage.provider,
                    None if usage is None else (1 if usage.success else 0),
                    None if usage is None else usage.total_tokens,
                    None if usage is None else usage.cost_nanos,
                    None if usage is None else usage.api_key_id,
                )
                actual = (
                    row["record_id"],
                    row["state"],
                    row["revision"],
                    row["key_id"],
                    row["created_at"],
                    row["expires_at"],
                    row["transitioned_at"],
                    row["estimated_cost_nanos"],
                    row["daily_budget_nanos"],
                    row["monthly_budget_nanos"],
                    row["event_id"],
                    row["occurred_at"],
                    row["credential_ref"],
                    row["provider"],
                    row["success"],
                    row["total_tokens"],
                    row["cost_nanos"],
                    row["api_key_id"],
                )
                if actual != expected:
                    raise ValueError
                return reservation
            raise ValueError
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise UsageLedgerCorrupt("Stored usage ledger record is invalid.") from exc

    def _decode_reservation(self, row: aiosqlite.Row) -> BudgetReservation:
        decoded = self._decode_row(row)
        if type(decoded) is not BudgetReservation:
            raise UsageLedgerConflict("Usage ledger record kind conflict.")
        return decoded
