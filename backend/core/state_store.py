"""Distributed State Store Interface & Implementation.

Enables seamless transition from in-memory single worker state
to distributed Redis / Valkey state management for multi-worker scaling.
"""

from __future__ import annotations

import abc
import asyncio
import heapq
import math
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Literal, Optional, Tuple

from core.coordination import (
    MAX_COORDINATION_INTEGER,
    MAX_IDENTIFIER_LENGTH,
    CasRequest,
    CasResult,
    CoordinationReconciliationRequiredError,
    CoordinationUnavailableError,
    Epoch,
    EpochState,
    InvalidationGeneration,
    InvalidationRequest,
    InvalidationResult,
    QuotaCommitRequest,
    QuotaCommitResult,
    QuotaReservationDecision,
    QuotaReservationRequest,
    validate_epoch,
    validate_operation_id,
)

QUOTA_RATE_WINDOW_SECONDS = 60.0
QUOTA_DAILY_WINDOW_SECONDS = 86_400.0
QUOTA_MONTHLY_WINDOW_SECONDS = 30 * QUOTA_DAILY_WINDOW_SECONDS


@dataclass
class _CommittedQuotaReservation:
    reservation_id: str
    key_id: str
    committed_at: float
    actual_tokens: int
    actual_cost_usd: float
    durable_cost_recorded: bool
    daily_reconciled: bool
    monthly_reconciled: bool
    expires_at: float


@dataclass
class _QuotaLifecycleRecord:
    request: QuotaReservationRequest
    reserve_fingerprint: tuple[object, ...]
    reserve_result: QuotaReservationDecision
    state: Literal["active", "committed", "released", "expired"]
    active_expires_at: float
    retained_until: float
    next_expiry_at: float
    committed: _CommittedQuotaReservation | None = None


@dataclass(frozen=True)
class _CasRecord:
    revision: int
    payload: bytes
    expires_at: float


@dataclass(frozen=True)
class _Replay:
    fingerprint: object
    result: object
    expires_at: float


@dataclass(frozen=True)
class _QuotaReplay:
    key_id: object
    fingerprint: object
    result: object
    expires_at: float


class BaseStateStore(abc.ABC):
    """Abstract interface for cluster state, rate limits, and cooldown tracking."""

    @abc.abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """Retrieve a value by key."""
        pass

    @abc.abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        """Set a value with an optional expiration time in seconds."""
        pass

    @abc.abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a key."""
        pass

    @abc.abstractmethod
    async def increment(
        self, key: str, amount: int = 1, ttl_seconds: Optional[float] = None
    ) -> int:
        """Atomically increment a counter."""
        pass

    @abc.abstractmethod
    async def acquire_lock(self, lock_key: str, ttl_seconds: float = 10.0) -> bool:
        """Acquire a distributed lock."""
        pass

    @abc.abstractmethod
    async def release_lock(self, lock_key: str) -> None:
        """Release a distributed lock."""
        pass

    @abc.abstractmethod
    async def reserve_quota(self, request: QuotaReservationRequest) -> QuotaReservationDecision:
        """Atomically reserve RPM, TPM, and budget capacity."""
        pass

    @abc.abstractmethod
    async def commit_quota(self, request: QuotaCommitRequest) -> QuotaCommitResult:
        """Replace an active estimate with actual completed usage."""
        pass

    @abc.abstractmethod
    async def release_quota(self, reservation_id: str, *, now: float) -> bool:
        """Idempotently release one active reservation."""
        pass


class InMemoryStateStore(BaseStateStore):
    """Bounded, deterministic reference implementation of coordination semantics."""

    _MAX_PRUNED_PER_MUTATION = 256
    _DEFAULT_COORDINATION_REPLAY_LIMIT = 100_000
    _DEFAULT_QUOTA_RECORD_LIMIT = 100_000
    _DEFAULT_QUOTA_REPLAY_LIMIT = 100_000
    _UNKNOWN_QUOTA_KEY = ("unknown-reservation",)

    def __init__(
        self,
        *,
        clock: Callable[[], float] = time.monotonic,
        _coordination_replay_limit_for_testing: int | None = None,
        _quota_record_limit_for_testing: int | None = None,
        _quota_replay_limit_for_testing: int | None = None,
    ) -> None:
        self._clock = clock
        self._store: Dict[str, Tuple[Optional[float], Any]] = {}
        self._locks: Dict[str, float] = {}
        self._epoch = Epoch(1, EpochState.READY)
        self._epoch_advances: Dict[str, _Replay] = {}
        self._epoch_ready: Dict[str, _Replay] = {}
        self._epoch_advance_expiries: list[tuple[float, str]] = []
        self._epoch_ready_expiries: list[tuple[float, str]] = []
        self._cas: Dict[str, _CasRecord] = {}
        self._cas_replays: Dict[str, _Replay] = {}
        self._cas_expiries: list[tuple[float, str]] = []
        self._cas_replay_expiries: list[tuple[float, str]] = []
        self._invalidation_generations: Dict[str, int] = {}
        self._invalidation_replays: Dict[str, _Replay] = {}
        self._invalidation_replay_expiries: list[tuple[float, str]] = []
        self._quota_records: Dict[str, _QuotaLifecycleRecord] = {}
        self._quota_ids_by_key: Dict[str, set[str]] = {}
        self._quota_lifecycle_expiries: Dict[str, list[tuple[float, str]]] = {}
        self._quota_replays: Dict[str, _QuotaReplay] = {}
        self._quota_replay_expiries: Dict[object, list[tuple[float, str]]] = {}
        self._quota_replay_counts: Dict[object, int] = {}
        self._coordination_replay_limit = (
            self._DEFAULT_COORDINATION_REPLAY_LIMIT
            if _coordination_replay_limit_for_testing is None
            else _coordination_replay_limit_for_testing
        )
        self._quota_record_limit = (
            self._DEFAULT_QUOTA_RECORD_LIMIT
            if _quota_record_limit_for_testing is None
            else _quota_record_limit_for_testing
        )
        self._quota_replay_limit = (
            self._DEFAULT_QUOTA_REPLAY_LIMIT
            if _quota_replay_limit_for_testing is None
            else _quota_replay_limit_for_testing
        )
        self._closed = False
        self._async_lock = asyncio.Lock()

    def _ensure_open_locked(self) -> None:
        if self._closed:
            raise CoordinationUnavailableError("Coordination store is closed.")

    def _prune_heap_locked(
        self, heap: list[tuple[float, str]], mapping: Dict[str, Any], now: float, budget: int
    ) -> int:
        work = 0
        while heap and heap[0][0] <= now:
            if work == budget:
                raise CoordinationReconciliationRequiredError("Reconciliation is required.")
            expires_at, identifier = heapq.heappop(heap)
            work += 1
            record = mapping.get(identifier)
            if record is not None and record.expires_at == expires_at:
                mapping.pop(identifier, None)
        return work

    def _prune_coordination_locked(self, now: float | None = None) -> None:
        now = self._clock() if now is None else now
        budget = self._MAX_PRUNED_PER_MUTATION
        budget -= self._prune_heap_locked(
            self._epoch_advance_expiries, self._epoch_advances, now, budget
        )
        budget -= self._prune_heap_locked(
            self._epoch_ready_expiries, self._epoch_ready, now, budget
        )
        budget -= self._prune_heap_locked(self._cas_expiries, self._cas, now, budget)
        budget -= self._prune_heap_locked(self._cas_replay_expiries, self._cas_replays, now, budget)
        self._prune_heap_locked(
            self._invalidation_replay_expiries, self._invalidation_replays, now, budget
        )

    def _is_ready_locked(self, epoch: int) -> bool:
        return self._epoch.epoch == epoch and self._epoch.state is EpochState.READY

    @staticmethod
    def _cas_fingerprint(request: CasRequest) -> tuple[object, ...]:
        return (
            request.key,
            request.expected_revision,
            request.payload,
            request.ttl_seconds,
            request.epoch,
        )

    @staticmethod
    def _quota_reserve_fingerprint(request: QuotaReservationRequest) -> tuple[object, ...]:
        return (
            request.reservation_id,
            request.key_id,
            request.now,
            request.ttl_seconds,
            request.estimated_tokens,
            request.estimated_cost_usd,
            request.rpm_limit,
            request.tpm_limit,
            request.daily_budget_usd,
            request.monthly_budget_usd,
            request.daily_spend_usd,
            request.monthly_spend_usd,
            request.daily_snapshot_started_at,
            request.monthly_snapshot_started_at,
            request.fencing_epoch,
        )

    @staticmethod
    def _quota_commit_fingerprint(request: QuotaCommitRequest) -> tuple[object, ...]:
        return (
            request.reservation_id,
            request.now,
            request.actual_tokens,
            request.actual_cost_usd,
            request.durable_cost_recorded,
            request.fencing_epoch,
        )

    async def get(self, key: str) -> Optional[Any]:
        async with self._async_lock:
            self._ensure_open_locked()
            expires_at, value = self._store.get(key, (None, None))
            if key not in self._store:
                return None
            if expires_at is not None and self._clock() > expires_at:
                self._store.pop(key, None)
                return None
            return value

    async def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        async with self._async_lock:
            self._ensure_open_locked()
            self._store[key] = (
                self._clock() + ttl_seconds if ttl_seconds is not None else None,
                value,
            )

    async def delete(self, key: str) -> None:
        async with self._async_lock:
            self._ensure_open_locked()
            self._store.pop(key, None)

    async def increment(
        self, key: str, amount: int = 1, ttl_seconds: Optional[float] = None
    ) -> int:
        async with self._async_lock:
            self._ensure_open_locked()
            expires_at, value = self._store.get(key, (None, 0))
            current = (
                int(value)
                if (expires_at is None or self._clock() <= expires_at)
                and isinstance(value, (int, str))
                and str(value).isdigit()
                else 0
            )
            new_value = current + amount
            self._store[key] = (
                self._clock() + ttl_seconds if ttl_seconds is not None else None,
                new_value,
            )
            return new_value

    async def acquire_lock(self, lock_key: str, ttl_seconds: float = 10.0) -> bool:
        async with self._async_lock:
            self._ensure_open_locked()
            now = self._clock()
            if self._locks.get(lock_key, 0.0) > now:
                return False
            self._locks[lock_key] = now + ttl_seconds
            return True

    async def release_lock(self, lock_key: str) -> None:
        async with self._async_lock:
            self._ensure_open_locked()
            self._locks.pop(lock_key, None)

    async def read_epoch(self) -> Epoch:
        async with self._async_lock:
            self._ensure_open_locked()
            return self._epoch

    async def advance_epoch(self, expected_epoch: int, operation_id: str) -> Epoch:
        async with self._async_lock:
            self._ensure_open_locked()
            expected_epoch = validate_epoch(expected_epoch)
            operation_id = validate_operation_id(operation_id)
            fingerprint = (expected_epoch,)
            now = self._clock()
            replay = self._epoch_advances.get(operation_id)
            if replay is not None and replay.expires_at > now:
                if replay.fingerprint == fingerprint:
                    result = replay.result
                    assert isinstance(result, Epoch)
                    return result
                return self._epoch
            self._prune_coordination_locked(now)
            if self._epoch.epoch == expected_epoch and self._epoch.state is EpochState.READY:
                if len(self._epoch_advances) >= self._coordination_replay_limit:
                    raise CoordinationReconciliationRequiredError("Reconciliation is required.")
                self._epoch = Epoch(expected_epoch + 1, EpochState.RECONCILING)
                expires_at = now + QUOTA_MONTHLY_WINDOW_SECONDS
                self._epoch_advances[operation_id] = _Replay(fingerprint, self._epoch, expires_at)
                heapq.heappush(self._epoch_advance_expiries, (expires_at, operation_id))
            return self._epoch

    async def mark_epoch_ready(self, epoch: int, operation_id: str) -> Epoch:
        async with self._async_lock:
            self._ensure_open_locked()
            epoch = validate_epoch(epoch)
            operation_id = validate_operation_id(operation_id)
            fingerprint = (epoch,)
            now = self._clock()
            replay = self._epoch_ready.get(operation_id)
            if replay is not None and replay.expires_at > now:
                if replay.fingerprint == fingerprint:
                    result = replay.result
                    assert isinstance(result, Epoch)
                    return result
                return self._epoch
            self._prune_coordination_locked(now)
            if self._epoch.epoch == epoch and self._epoch.state is EpochState.RECONCILING:
                if len(self._epoch_ready) >= self._coordination_replay_limit:
                    raise CoordinationReconciliationRequiredError("Reconciliation is required.")
                self._epoch = Epoch(epoch, EpochState.READY)
                expires_at = now + QUOTA_MONTHLY_WINDOW_SECONDS
                self._epoch_ready[operation_id] = _Replay(fingerprint, self._epoch, expires_at)
                heapq.heappush(self._epoch_ready_expiries, (expires_at, operation_id))
            return self._epoch

    async def compare_and_set(self, request: CasRequest) -> CasResult:
        async with self._async_lock:
            self._ensure_open_locked()
            if not self._is_ready_locked(request.epoch):
                return CasResult(False, None)
            fingerprint = self._cas_fingerprint(request)
            now = self._clock()
            replay = self._cas_replays.get(request.operation_id)
            if replay is not None and replay.expires_at > now:
                if replay.fingerprint == fingerprint:
                    result = replay.result
                    assert isinstance(result, CasResult)
                    return CasResult(result.applied, result.revision, idempotent=True)
                return CasResult(False, None)
            self._prune_coordination_locked(now)
            if len(self._cas_replays) >= self._coordination_replay_limit:
                raise CoordinationReconciliationRequiredError("Reconciliation is required.")
            existing = self._cas.get(request.key)
            revision = 1 if existing is None else existing.revision + 1
            if (existing is None and request.expected_revision != 0) or (
                existing is not None and existing.revision != request.expected_revision
            ):
                result = CasResult(False, None)
                expires_at = now + request.ttl_seconds
                self._cas_replays[request.operation_id] = _Replay(fingerprint, result, expires_at)
                heapq.heappush(self._cas_replay_expiries, (expires_at, request.operation_id))
                return result
            expires_at = now + request.ttl_seconds
            result = CasResult(True, revision)
            self._cas[request.key] = _CasRecord(revision, request.payload, expires_at)
            self._cas_replays[request.operation_id] = _Replay(fingerprint, result, expires_at)
            heapq.heappush(self._cas_expiries, (expires_at, request.key))
            heapq.heappush(self._cas_replay_expiries, (expires_at, request.operation_id))
            return result

    async def invalidate(self, request: InvalidationRequest) -> InvalidationResult:
        async with self._async_lock:
            self._ensure_open_locked()
            if not self._is_ready_locked(request.epoch):
                return InvalidationResult(False, None)
            fingerprint = (request.scope, request.epoch, request.replay_ttl_seconds)
            now = self._clock()
            replay = self._invalidation_replays.get(request.operation_id)
            if replay is not None and replay.expires_at > now:
                if replay.fingerprint == fingerprint:
                    result = replay.result
                    assert isinstance(result, InvalidationResult)
                    return InvalidationResult(result.applied, result.generation, idempotent=True)
                return InvalidationResult(False, None)
            self._prune_coordination_locked(now)
            if len(self._invalidation_replays) >= self._coordination_replay_limit:
                raise CoordinationReconciliationRequiredError("Reconciliation is required.")
            generation = self._invalidation_generations.get(request.scope, 0) + 1
            result = InvalidationResult(True, generation)
            expires_at = now + request.replay_ttl_seconds
            self._invalidation_generations[request.scope] = generation
            self._invalidation_replays[request.operation_id] = _Replay(
                fingerprint, result, expires_at
            )
            heapq.heappush(self._invalidation_replay_expiries, (expires_at, request.operation_id))
            return result

    async def read_invalidation_generation(self, scope: str) -> InvalidationGeneration:
        async with self._async_lock:
            self._ensure_open_locked()
            self._prune_coordination_locked()
            return InvalidationGeneration(self._invalidation_generations.get(scope))

    @staticmethod
    def _quota_evidence_retention_seconds(request: QuotaReservationRequest) -> float:
        windows = [QUOTA_RATE_WINDOW_SECONDS]
        if request.daily_budget_usd is not None:
            windows.append(QUOTA_DAILY_WINDOW_SECONDS)
        if request.monthly_budget_usd is not None:
            windows.append(QUOTA_MONTHLY_WINDOW_SECONDS)
        return min(max(windows), QUOTA_MONTHLY_WINDOW_SECONDS)

    @staticmethod
    def _validate_quota_release(
        reservation_id: object,
        now: object,
        fencing_epoch: object,
        operation_id: object,
    ) -> tuple[str, float, int, str | None]:
        for value, label in (
            (reservation_id, "Reservation ID"),
            (operation_id, "Operation ID"),
        ):
            if value is None and label == "Operation ID":
                continue
            if (
                not isinstance(value, str)
                or not 1 <= len(value) <= MAX_IDENTIFIER_LENGTH
                or any(ord(character) < 32 or ord(character) > 126 for character in value)
            ):
                raise ValueError(f"{label} is invalid.")
        if (
            isinstance(now, bool)
            or not isinstance(now, (int, float))
            or not math.isfinite(float(now))
            or not 0.0 <= float(now) <= MAX_COORDINATION_INTEGER
        ):
            raise ValueError("Quota time is invalid.")
        if (
            isinstance(fencing_epoch, bool)
            or not isinstance(fencing_epoch, int)
            or not 1 <= fencing_epoch <= MAX_COORDINATION_INTEGER
        ):
            raise ValueError("Epoch is invalid.")
        assert isinstance(reservation_id, str)
        assert operation_id is None or isinstance(operation_id, str)
        return reservation_id, float(now), fencing_epoch, operation_id

    def _remove_quota_record_locked(self, reservation_id: str) -> None:
        record = self._quota_records.pop(reservation_id, None)
        if record is None:
            return
        identifiers = self._quota_ids_by_key.get(record.request.key_id)
        if identifiers is not None:
            identifiers.discard(reservation_id)
            if not identifiers:
                self._quota_ids_by_key.pop(record.request.key_id, None)

    def _apply_quota_lifecycle_expiry_locked(
        self, key_id: str, reservation_id: str, expires_at: float
    ) -> None:
        record = self._quota_records.get(reservation_id)
        if record is None or record.request.key_id != key_id or record.next_expiry_at != expires_at:
            return
        if expires_at >= record.retained_until:
            self._remove_quota_record_locked(reservation_id)
            return
        if record.state == "active" and expires_at == record.active_expires_at:
            record.state = "expired"
        record.next_expiry_at = record.retained_until
        heapq.heappush(
            self._quota_lifecycle_expiries.setdefault(key_id, []),
            (record.retained_until, reservation_id),
        )

    def _apply_quota_replay_expiry_locked(
        self, key_id: object, replay_key: str, expires_at: float
    ) -> None:
        replay = self._quota_replays.get(replay_key)
        if replay is None or replay.key_id != key_id or replay.expires_at != expires_at:
            return
        self._quota_replays.pop(replay_key, None)
        remaining = self._quota_replay_counts.get(key_id, 0) - 1
        if remaining:
            self._quota_replay_counts[key_id] = remaining
        else:
            self._quota_replay_counts.pop(key_id, None)

    def _remove_empty_quota_expiry_heaps_locked(
        self,
        key_id: object,
        lifecycle_heap: list[tuple[float, str]],
        replay_heap: list[tuple[float, str]],
    ) -> None:
        if isinstance(key_id, str) and not lifecycle_heap:
            self._quota_lifecycle_expiries.pop(key_id, None)
        if not replay_heap:
            self._quota_replay_expiries.pop(key_id, None)

    def _prune_quota_key_locked(self, key_id: object, now: float, budget: int) -> int | None:
        lifecycle_heap = (
            self._quota_lifecycle_expiries.get(key_id, []) if isinstance(key_id, str) else []
        )
        replay_heap = self._quota_replay_expiries.get(key_id, [])
        while budget:
            lifecycle_due = bool(lifecycle_heap and lifecycle_heap[0][0] <= now)
            replay_due = bool(replay_heap and replay_heap[0][0] <= now)
            if not lifecycle_due and not replay_due:
                self._remove_empty_quota_expiry_heaps_locked(key_id, lifecycle_heap, replay_heap)
                return budget
            if lifecycle_due and (not replay_due or lifecycle_heap[0][0] <= replay_heap[0][0]):
                expires_at, reservation_id = heapq.heappop(lifecycle_heap)
                self._apply_quota_lifecycle_expiry_locked(str(key_id), reservation_id, expires_at)
            else:
                expires_at, replay_key = heapq.heappop(replay_heap)
                self._apply_quota_replay_expiry_locked(key_id, replay_key, expires_at)
            budget -= 1
        self._remove_empty_quota_expiry_heaps_locked(key_id, lifecycle_heap, replay_heap)
        if (lifecycle_heap and lifecycle_heap[0][0] <= now) or (
            replay_heap and replay_heap[0][0] <= now
        ):
            return None
        return budget

    def _prune_quota_keys_locked(self, key_ids: list[object], now: float) -> bool:
        budget = self._MAX_PRUNED_PER_MUTATION
        seen: set[object] = set()
        for key_id in key_ids:
            if key_id in seen:
                continue
            seen.add(key_id)
            remaining = self._prune_quota_key_locked(key_id, now, budget)
            if remaining is None:
                return False
            budget = remaining
        return True

    def _store_quota_replay_locked(
        self,
        replay_key: str,
        key_id: object,
        fingerprint: object,
        result: object,
        expires_at: float,
    ) -> bool:
        if self._quota_replay_counts.get(key_id, 0) >= self._quota_replay_limit:
            return False
        self._quota_replays[replay_key] = _QuotaReplay(key_id, fingerprint, result, expires_at)
        self._quota_replay_counts[key_id] = self._quota_replay_counts.get(key_id, 0) + 1
        heapq.heappush(self._quota_replay_expiries.setdefault(key_id, []), (expires_at, replay_key))
        return True

    @staticmethod
    def _committed_expiry(committed: _CommittedQuotaReservation) -> float:
        return max(
            committed.committed_at + QUOTA_RATE_WINDOW_SECONDS,
            committed.committed_at
            if committed.daily_reconciled
            else committed.committed_at + QUOTA_DAILY_WINDOW_SECONDS,
            committed.committed_at
            if committed.monthly_reconciled
            else committed.committed_at + QUOTA_MONTHLY_WINDOW_SECONDS,
        )

    def _reconcile_committed_for_key_locked(
        self, key_id: str, daily_snapshot_started_at: float, monthly_snapshot_started_at: float
    ) -> None:
        for reservation_id in self._quota_ids_by_key.get(key_id, ()):
            record = self._quota_records[reservation_id]
            committed = record.committed
            if (
                record.state != "committed"
                or committed is None
                or not committed.durable_cost_recorded
            ):
                continue
            if daily_snapshot_started_at >= committed.committed_at:
                committed.daily_reconciled = True
            if monthly_snapshot_started_at >= committed.committed_at:
                committed.monthly_reconciled = True
            expires_at = self._committed_expiry(committed)
            if expires_at < committed.expires_at:
                committed.expires_at = expires_at
                record.next_expiry_at = min(expires_at, record.retained_until)
                heapq.heappush(
                    self._quota_lifecycle_expiries.setdefault(key_id, []),
                    (record.next_expiry_at, committed.reservation_id),
                )

    def _active_for_key_locked(self, key_id: str) -> list[_QuotaLifecycleRecord]:
        return [
            record
            for reservation_id in self._quota_ids_by_key.get(key_id, ())
            if (record := self._quota_records[reservation_id]).state == "active"
        ]

    def _committed_for_key_locked(self, key_id: str) -> list[_CommittedQuotaReservation]:
        return [
            committed
            for reservation_id in self._quota_ids_by_key.get(key_id, ())
            if (record := self._quota_records[reservation_id]).state == "committed"
            and (committed := record.committed) is not None
        ]

    @staticmethod
    def _retry_after(now: float, timestamps: list[float]) -> int:
        return (
            max(
                1,
                math.ceil(
                    min(timestamp + QUOTA_RATE_WINDOW_SECONDS for timestamp in timestamps) - now
                ),
            )
            if timestamps
            else 1
        )

    async def reserve_quota(self, request: QuotaReservationRequest) -> QuotaReservationDecision:
        async with self._async_lock:
            self._ensure_open_locked()
            if not self._is_ready_locked(request.fencing_epoch):
                reason = (
                    "reconciling" if self._epoch.state is EpochState.RECONCILING else "stale_epoch"
                )
                return QuotaReservationDecision(False, request.reservation_id, reason)
            fingerprint = self._quota_reserve_fingerprint(request)
            replay_key = f"reserve:{request.operation_id or request.reservation_id}"
            record = self._quota_records.get(request.reservation_id)
            replay = self._quota_replays.get(replay_key)
            cleanup_keys = [
                replay.key_id if replay is not None else request.key_id,
                record.request.key_id if record is not None else request.key_id,
                request.key_id,
            ]
            if not self._prune_quota_keys_locked(cleanup_keys, request.now):
                return QuotaReservationDecision(
                    False, request.reservation_id, "reconciliation_required"
                )
            replay = self._quota_replays.get(replay_key)
            if replay is not None:
                if replay.fingerprint != fingerprint:
                    return QuotaReservationDecision(False, request.reservation_id, "conflict")
                result = replay.result
                assert isinstance(result, QuotaReservationDecision)
                return QuotaReservationDecision(
                    result.accepted,
                    result.reservation_id,
                    result.reason,
                    result.retry_after_seconds,
                    True,
                )
            record = self._quota_records.get(request.reservation_id)
            if record is not None:
                if record.reserve_fingerprint != fingerprint:
                    return QuotaReservationDecision(False, request.reservation_id, "conflict")
                result = record.reserve_result
                return QuotaReservationDecision(
                    result.accepted,
                    result.reservation_id,
                    result.reason,
                    result.retry_after_seconds,
                    True,
                )
            if self._quota_replay_counts.get(request.key_id, 0) >= self._quota_replay_limit:
                return QuotaReservationDecision(
                    False, request.reservation_id, "reconciliation_required"
                )
            self._reconcile_committed_for_key_locked(
                request.key_id,
                request.daily_snapshot_started_at,
                request.monthly_snapshot_started_at,
            )
            active = self._active_for_key_locked(request.key_id)
            committed = self._committed_for_key_locked(request.key_id)
            result: QuotaReservationDecision | None = None
            if len(self._quota_ids_by_key.get(request.key_id, ())) >= self._quota_record_limit:
                result = QuotaReservationDecision(False, request.reservation_id, "capacity")
            rate_cutoff = request.now - QUOTA_RATE_WINDOW_SECONDS
            active_rate = [item for item in active if item.request.now > rate_cutoff]
            committed_rate = [item for item in committed if item.committed_at > rate_cutoff]
            timestamps = [item.request.now for item in active_rate] + [
                item.committed_at for item in committed_rate
            ]
            if (
                result is None
                and request.rpm_limit is not None
                and len(timestamps) >= request.rpm_limit
            ):
                result = QuotaReservationDecision(
                    False, request.reservation_id, "rpm", self._retry_after(request.now, timestamps)
                )
            reserved_tokens = sum(item.request.estimated_tokens for item in active_rate)
            committed_tokens = sum(item.actual_tokens for item in committed_rate)
            if (
                result is None
                and request.tpm_limit is not None
                and reserved_tokens + committed_tokens + request.estimated_tokens
                > request.tpm_limit
            ):
                result = QuotaReservationDecision(
                    False, request.reservation_id, "tpm", self._retry_after(request.now, timestamps)
                )
            active_cost = sum(item.request.estimated_cost_usd for item in active)
            daily_unreconciled = sum(
                item.actual_cost_usd for item in committed if not item.daily_reconciled
            )
            monthly_unreconciled = sum(
                item.actual_cost_usd for item in committed if not item.monthly_reconciled
            )
            if (
                result is None
                and request.daily_budget_usd is not None
                and request.daily_spend_usd
                + daily_unreconciled
                + active_cost
                + request.estimated_cost_usd
                > request.daily_budget_usd
            ):
                result = QuotaReservationDecision(False, request.reservation_id, "daily_budget")
            if (
                result is None
                and request.monthly_budget_usd is not None
                and request.monthly_spend_usd
                + monthly_unreconciled
                + active_cost
                + request.estimated_cost_usd
                > request.monthly_budget_usd
            ):
                result = QuotaReservationDecision(False, request.reservation_id, "monthly_budget")
            if result is not None:
                if not self._store_quota_replay_locked(
                    replay_key,
                    request.key_id,
                    fingerprint,
                    result,
                    request.now + request.ttl_seconds,
                ):
                    return QuotaReservationDecision(
                        False, request.reservation_id, "reconciliation_required"
                    )
                return result

            result = QuotaReservationDecision(True, request.reservation_id)
            active_expires_at = request.now + request.ttl_seconds
            retained_until = max(
                active_expires_at,
                request.now + self._quota_evidence_retention_seconds(request),
            )
            if request.operation_id is not None and not self._store_quota_replay_locked(
                replay_key,
                request.key_id,
                fingerprint,
                result,
                retained_until,
            ):
                return QuotaReservationDecision(
                    False, request.reservation_id, "reconciliation_required"
                )
            lifecycle = _QuotaLifecycleRecord(
                request,
                fingerprint,
                result,
                "active",
                active_expires_at,
                retained_until,
                min(active_expires_at, retained_until),
            )
            self._quota_records[request.reservation_id] = lifecycle
            self._quota_ids_by_key.setdefault(request.key_id, set()).add(request.reservation_id)
            heapq.heappush(
                self._quota_lifecycle_expiries.setdefault(request.key_id, []),
                (lifecycle.next_expiry_at, request.reservation_id),
            )
            return result

    async def commit_quota(self, request: QuotaCommitRequest) -> QuotaCommitResult:
        async with self._async_lock:
            self._ensure_open_locked()
            if not self._is_ready_locked(request.fencing_epoch):
                return QuotaCommitResult(False)
            replay_key = f"commit:{request.operation_id or request.reservation_id}"
            fingerprint = self._quota_commit_fingerprint(request)
            record = self._quota_records.get(request.reservation_id)
            replay = self._quota_replays.get(replay_key)
            target_key: object = (
                record.request.key_id if record is not None else self._UNKNOWN_QUOTA_KEY
            )
            cleanup_keys = [replay.key_id if replay is not None else target_key, target_key]
            if not self._prune_quota_keys_locked(cleanup_keys, request.now):
                raise CoordinationReconciliationRequiredError("Reconciliation is required.")
            replay = self._quota_replays.get(replay_key)
            if replay is not None:
                if replay.fingerprint != fingerprint:
                    return QuotaCommitResult(False)
                result = replay.result
                assert isinstance(result, QuotaCommitResult)
                return QuotaCommitResult(result.committed, result.overspent, True)
            record = self._quota_records.get(request.reservation_id)
            target_key = record.request.key_id if record is not None else self._UNKNOWN_QUOTA_KEY
            if self._quota_replay_counts.get(target_key, 0) >= self._quota_replay_limit:
                raise CoordinationReconciliationRequiredError("Reconciliation is required.")
            if record is None or record.state != "active":
                result = QuotaCommitResult(False)
                self._store_quota_replay_locked(
                    replay_key,
                    target_key,
                    fingerprint,
                    result,
                    record.retained_until
                    if record is not None
                    else request.now + QUOTA_MONTHLY_WINDOW_SECONDS,
                )
                return result
            source = record.request
            tokens = (
                source.estimated_tokens
                if request.actual_tokens is None
                else max(0, int(request.actual_tokens))
            )
            cost = (
                source.estimated_cost_usd
                if request.actual_cost_usd is None
                else max(0.0, float(request.actual_cost_usd))
            )
            committed = _CommittedQuotaReservation(
                request.reservation_id,
                source.key_id,
                request.now,
                tokens,
                cost,
                bool(request.durable_cost_recorded),
                source.daily_budget_usd is None,
                source.monthly_budget_usd is None,
                request.now + QUOTA_MONTHLY_WINDOW_SECONDS,
            )
            committed.expires_at = self._committed_expiry(committed)
            record.state = "committed"
            record.committed = committed
            record.retained_until = request.now + self._quota_evidence_retention_seconds(source)
            record.next_expiry_at = min(committed.expires_at, record.retained_until)
            heapq.heappush(
                self._quota_lifecycle_expiries.setdefault(source.key_id, []),
                (record.next_expiry_at, request.reservation_id),
            )
            active_for_key = self._active_for_key_locked(source.key_id)
            committed_for_key = self._committed_for_key_locked(source.key_id)
            cutoff = request.now - QUOTA_RATE_WINDOW_SECONDS
            overspent = bool(
                (
                    source.tpm_limit is not None
                    and sum(
                        item.request.estimated_tokens
                        for item in active_for_key
                        if item.request.now > cutoff
                    )
                    + sum(
                        item.actual_tokens
                        for item in committed_for_key
                        if item.committed_at > cutoff
                    )
                    > source.tpm_limit
                )
                or (
                    source.daily_budget_usd is not None
                    and source.daily_spend_usd
                    + sum(item.request.estimated_cost_usd for item in active_for_key)
                    + sum(
                        item.actual_cost_usd
                        for item in committed_for_key
                        if not item.daily_reconciled
                    )
                    > source.daily_budget_usd
                )
                or (
                    source.monthly_budget_usd is not None
                    and source.monthly_spend_usd
                    + sum(item.request.estimated_cost_usd for item in active_for_key)
                    + sum(
                        item.actual_cost_usd
                        for item in committed_for_key
                        if not item.monthly_reconciled
                    )
                    > source.monthly_budget_usd
                )
            )
            result = QuotaCommitResult(True, overspent)
            self._store_quota_replay_locked(
                replay_key,
                source.key_id,
                fingerprint,
                result,
                record.retained_until,
            )
            return result

    async def release_quota(
        self,
        reservation_id: str,
        *,
        now: float,
        fencing_epoch: int = 1,
        operation_id: str | None = None,
    ) -> bool:
        async with self._async_lock:
            self._ensure_open_locked()
            identifier, now, fencing_epoch, operation_id = self._validate_quota_release(
                reservation_id, now, fencing_epoch, operation_id
            )
            if not self._is_ready_locked(fencing_epoch):
                return False
            replay_key = f"release:{operation_id or identifier}"
            fingerprint = (identifier, fencing_epoch)
            record = self._quota_records.get(identifier)
            replay = self._quota_replays.get(replay_key)
            target_key: object = (
                record.request.key_id if record is not None else self._UNKNOWN_QUOTA_KEY
            )
            cleanup_keys = [replay.key_id if replay is not None else target_key, target_key]
            if not self._prune_quota_keys_locked(cleanup_keys, now):
                raise CoordinationReconciliationRequiredError("Reconciliation is required.")
            replay = self._quota_replays.get(replay_key)
            if replay is not None:
                return False
            record = self._quota_records.get(identifier)
            target_key = record.request.key_id if record is not None else self._UNKNOWN_QUOTA_KEY
            if self._quota_replay_counts.get(target_key, 0) >= self._quota_replay_limit:
                raise CoordinationReconciliationRequiredError("Reconciliation is required.")
            result = record is not None and record.state == "active"
            expires_at = (
                record.retained_until if record is not None else now + QUOTA_MONTHLY_WINDOW_SECONDS
            )
            if result:
                record.state = "released"
                record.retained_until = max(
                    now,
                    record.request.now + self._quota_evidence_retention_seconds(record.request),
                )
                record.next_expiry_at = record.retained_until
                expires_at = record.retained_until
                heapq.heappush(
                    self._quota_lifecycle_expiries.setdefault(record.request.key_id, []),
                    (record.next_expiry_at, identifier),
                )
            self._store_quota_replay_locked(
                replay_key,
                target_key,
                fingerprint,
                result,
                expires_at,
            )
            return result

    async def close(self) -> None:
        async with self._async_lock:
            self._closed = True


class RedisStateStore(BaseStateStore):
    """Distributed state store utilizing Redis or Valkey."""

    def __init__(self, redis_url: str) -> None:
        self.redis_url = redis_url
        self._client: Any = None

    async def _get_client(self) -> Any:
        if self._client is None:
            import redis.asyncio as redis

            self._client = redis.from_url(self.redis_url, decode_responses=True)
        return self._client

    async def get(self, key: str) -> Optional[Any]:
        client = await self._get_client()
        return await client.get(key)

    async def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        client = await self._get_client()
        if ttl_seconds is not None:
            await client.set(key, str(value), ex=int(ttl_seconds))
        else:
            await client.set(key, str(value))

    async def delete(self, key: str) -> None:
        client = await self._get_client()
        await client.delete(key)

    async def increment(
        self, key: str, amount: int = 1, ttl_seconds: Optional[float] = None
    ) -> int:
        client = await self._get_client()
        val = await client.incrby(key, amount)
        if ttl_seconds is not None:
            await client.expire(key, int(ttl_seconds))
        return val

    async def acquire_lock(self, lock_key: str, ttl_seconds: float = 10.0) -> bool:
        client = await self._get_client()
        res = await client.set(f"lock:{lock_key}", "1", nx=True, ex=int(ttl_seconds))
        return bool(res)

    async def release_lock(self, lock_key: str) -> None:
        client = await self._get_client()
        await client.delete(f"lock:{lock_key}")

    async def reserve_quota(self, request: QuotaReservationRequest) -> QuotaReservationDecision:
        raise RuntimeError(
            "Redis quota reservations are not available until distributed HA is activated."
        )

    async def commit_quota(self, request: QuotaCommitRequest) -> QuotaCommitResult:
        raise RuntimeError(
            "Redis quota reservations are not available until distributed HA is activated."
        )

    async def release_quota(self, reservation_id: str, *, now: float) -> bool:
        raise RuntimeError(
            "Redis quota reservations are not available until distributed HA is activated."
        )
