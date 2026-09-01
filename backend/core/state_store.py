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
from typing import Any, Callable, Dict, Optional, Tuple

from core.coordination import (
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
)

QUOTA_RATE_WINDOW_SECONDS = 60.0
QUOTA_DAILY_WINDOW_SECONDS = 86_400.0
QUOTA_MONTHLY_WINDOW_SECONDS = 30 * QUOTA_DAILY_WINDOW_SECONDS


@dataclass
class _ActiveQuotaReservation:
    request: QuotaReservationRequest
    expires_at: float


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
    _DEFAULT_QUOTA_RECORD_LIMIT = 100_000

    def __init__(
        self,
        *,
        clock: Callable[[], float] = time.monotonic,
        _quota_record_limit_for_testing: int | None = None,
    ) -> None:
        self._clock = clock
        self._store: Dict[str, Tuple[Optional[float], Any]] = {}
        self._locks: Dict[str, float] = {}
        self._epoch = Epoch(1, EpochState.READY)
        self._epoch_advances: Dict[str, Epoch] = {}
        self._epoch_ready: Dict[str, Epoch] = {}
        self._cas: Dict[str, _CasRecord] = {}
        self._cas_replays: Dict[str, _Replay] = {}
        self._cas_expiries: list[tuple[float, str]] = []
        self._cas_replay_expiries: list[tuple[float, str]] = []
        self._invalidation_generations: Dict[str, int] = {}
        self._invalidation_replays: Dict[str, _Replay] = {}
        self._invalidation_replay_expiries: list[tuple[float, str]] = []
        self._quota_reservations: Dict[str, _ActiveQuotaReservation] = {}
        self._quota_committed: Dict[str, _CommittedQuotaReservation] = {}
        self._quota_reservation_expiries: list[tuple[float, str]] = []
        self._quota_committed_expiries: list[tuple[float, str]] = []
        self._quota_replays: Dict[str, _Replay] = {}
        self._quota_record_counts: Dict[str, int] = {}
        self._quota_record_limit = (
            self._DEFAULT_QUOTA_RECORD_LIMIT
            if _quota_record_limit_for_testing is None
            else _quota_record_limit_for_testing
        )
        self._closed = False
        self._async_lock = asyncio.Lock()

    def _ensure_open_locked(self) -> None:
        if self._closed:
            raise CoordinationUnavailableError("Coordination store is closed.")

    def _prune_heap_locked(
        self, heap: list[tuple[float, str]], mapping: Dict[str, Any], now: float, budget: int
    ) -> int:
        pruned = 0
        while heap and heap[0][0] <= now:
            if pruned == budget:
                raise CoordinationReconciliationRequiredError("Reconciliation is required.")
            expires_at, identifier = heapq.heappop(heap)
            record = mapping.get(identifier)
            if record is not None and record.expires_at == expires_at:
                mapping.pop(identifier, None)
                pruned += 1
        return pruned

    def _prune_coordination_locked(self) -> None:
        now = self._clock()
        budget = self._MAX_PRUNED_PER_MUTATION
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
            self._prune_coordination_locked()
            if operation_id in self._epoch_advances:
                return self._epoch_advances[operation_id]
            if self._epoch.epoch == expected_epoch and self._epoch.state is EpochState.READY:
                self._epoch = Epoch(expected_epoch + 1, EpochState.RECONCILING)
                self._epoch_advances[operation_id] = self._epoch
            return self._epoch

    async def mark_epoch_ready(self, epoch: int, operation_id: str) -> Epoch:
        async with self._async_lock:
            self._ensure_open_locked()
            self._prune_coordination_locked()
            if operation_id in self._epoch_ready:
                return self._epoch_ready[operation_id]
            if self._epoch.epoch == epoch and self._epoch.state is EpochState.RECONCILING:
                self._epoch = Epoch(epoch, EpochState.READY)
                self._epoch_ready[operation_id] = self._epoch
            return self._epoch

    async def compare_and_set(self, request: CasRequest) -> CasResult:
        async with self._async_lock:
            self._ensure_open_locked()
            self._prune_coordination_locked()
            fingerprint = self._cas_fingerprint(request)
            replay = self._cas_replays.get(request.operation_id)
            if replay is not None:
                if replay.fingerprint == fingerprint:
                    result = replay.result
                    assert isinstance(result, CasResult)
                    return CasResult(result.applied, result.revision, idempotent=True)
                return CasResult(False, None)
            if not self._is_ready_locked(request.epoch):
                return CasResult(False, None)
            existing = self._cas.get(request.key)
            revision = 1 if existing is None else existing.revision + 1
            if (existing is None and request.expected_revision != 0) or (
                existing is not None and existing.revision != request.expected_revision
            ):
                return CasResult(False, None)
            expires_at = self._clock() + request.ttl_seconds
            result = CasResult(True, revision)
            self._cas[request.key] = _CasRecord(revision, request.payload, expires_at)
            self._cas_replays[request.operation_id] = _Replay(fingerprint, result, expires_at)
            heapq.heappush(self._cas_expiries, (expires_at, request.key))
            heapq.heappush(self._cas_replay_expiries, (expires_at, request.operation_id))
            return result

    async def invalidate(self, request: InvalidationRequest) -> InvalidationResult:
        async with self._async_lock:
            self._ensure_open_locked()
            self._prune_coordination_locked()
            replay = self._invalidation_replays.get(request.operation_id)
            fingerprint = (request.scope, request.epoch, request.replay_ttl_seconds)
            if replay is not None:
                if replay.fingerprint == fingerprint:
                    result = replay.result
                    assert isinstance(result, InvalidationResult)
                    return InvalidationResult(result.applied, result.generation, idempotent=True)
                return InvalidationResult(False, None)
            if not self._is_ready_locked(request.epoch):
                return InvalidationResult(False, None)
            generation = self._invalidation_generations.get(request.scope, 0) + 1
            result = InvalidationResult(True, generation)
            expires_at = self._clock() + request.replay_ttl_seconds
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

    def _prune_quota_locked(self, now: float) -> bool:
        pruned = 0
        while self._quota_reservation_expiries and self._quota_reservation_expiries[0][0] <= now:
            if pruned == self._MAX_PRUNED_PER_MUTATION:
                return False
            expires_at, reservation_id = heapq.heappop(self._quota_reservation_expiries)
            active = self._quota_reservations.get(reservation_id)
            if active is not None and active.expires_at == expires_at:
                self._quota_reservations.pop(reservation_id, None)
                self._quota_replays.pop(f"reserve:{reservation_id}", None)
                self._quota_record_counts[active.request.key_id] -= 1
                pruned += 1
        while self._quota_committed_expiries and self._quota_committed_expiries[0][0] <= now:
            if pruned == self._MAX_PRUNED_PER_MUTATION:
                return False
            expires_at, reservation_id = heapq.heappop(self._quota_committed_expiries)
            committed = self._quota_committed.get(reservation_id)
            if committed is not None and committed.expires_at == expires_at:
                self._quota_committed.pop(reservation_id, None)
                self._quota_record_counts[committed.key_id] -= 1
                pruned += 1
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
        for committed in self._quota_committed.values():
            if committed.key_id != key_id or not committed.durable_cost_recorded:
                continue
            if daily_snapshot_started_at >= committed.committed_at:
                committed.daily_reconciled = True
            if monthly_snapshot_started_at >= committed.committed_at:
                committed.monthly_reconciled = True
            expires_at = self._committed_expiry(committed)
            if expires_at < committed.expires_at:
                committed.expires_at = expires_at
                heapq.heappush(
                    self._quota_committed_expiries, (expires_at, committed.reservation_id)
                )

    def _active_for_key_locked(self, key_id: str) -> list[_ActiveQuotaReservation]:
        return [item for item in self._quota_reservations.values() if item.request.key_id == key_id]

    def _committed_for_key_locked(self, key_id: str) -> list[_CommittedQuotaReservation]:
        return [item for item in self._quota_committed.values() if item.key_id == key_id]

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
            if not self._prune_quota_locked(request.now):
                return QuotaReservationDecision(
                    False, request.reservation_id, "reconciliation_required"
                )
            self._reconcile_committed_for_key_locked(
                request.key_id,
                request.daily_snapshot_started_at,
                request.monthly_snapshot_started_at,
            )
            if not self._is_ready_locked(request.fencing_epoch):
                reason = (
                    "reconciling" if self._epoch.state is EpochState.RECONCILING else "stale_epoch"
                )
                return QuotaReservationDecision(False, request.reservation_id, reason)
            fingerprint = self._quota_reserve_fingerprint(request)
            replay = self._quota_replays.get(f"reserve:{request.reservation_id}")
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
            active = self._active_for_key_locked(request.key_id)
            committed = self._committed_for_key_locked(request.key_id)
            if self._quota_record_counts.get(request.key_id, 0) >= self._quota_record_limit:
                return QuotaReservationDecision(False, request.reservation_id, "capacity")
            rate_cutoff = request.now - QUOTA_RATE_WINDOW_SECONDS
            active_rate = [item for item in active if item.request.now > rate_cutoff]
            committed_rate = [item for item in committed if item.committed_at > rate_cutoff]
            timestamps = [item.request.now for item in active_rate] + [
                item.committed_at for item in committed_rate
            ]
            if request.rpm_limit is not None and len(timestamps) >= request.rpm_limit:
                return QuotaReservationDecision(
                    False, request.reservation_id, "rpm", self._retry_after(request.now, timestamps)
                )
            reserved_tokens = sum(item.request.estimated_tokens for item in active_rate)
            committed_tokens = sum(item.actual_tokens for item in committed_rate)
            if (
                request.tpm_limit is not None
                and reserved_tokens + committed_tokens + request.estimated_tokens
                > request.tpm_limit
            ):
                return QuotaReservationDecision(
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
                request.daily_budget_usd is not None
                and request.daily_spend_usd
                + daily_unreconciled
                + active_cost
                + request.estimated_cost_usd
                > request.daily_budget_usd
            ):
                return QuotaReservationDecision(False, request.reservation_id, "daily_budget")
            if (
                request.monthly_budget_usd is not None
                and request.monthly_spend_usd
                + monthly_unreconciled
                + active_cost
                + request.estimated_cost_usd
                > request.monthly_budget_usd
            ):
                return QuotaReservationDecision(False, request.reservation_id, "monthly_budget")
            expires_at = request.now + max(1.0, request.ttl_seconds)
            result = QuotaReservationDecision(True, request.reservation_id)
            self._quota_reservations[request.reservation_id] = _ActiveQuotaReservation(
                request, expires_at
            )
            self._quota_replays[f"reserve:{request.reservation_id}"] = _Replay(
                fingerprint, result, expires_at
            )
            self._quota_record_counts[request.key_id] = (
                self._quota_record_counts.get(request.key_id, 0) + 1
            )
            heapq.heappush(self._quota_reservation_expiries, (expires_at, request.reservation_id))
            return result

    async def commit_quota(self, request: QuotaCommitRequest) -> QuotaCommitResult:
        async with self._async_lock:
            self._ensure_open_locked()
            if not self._prune_quota_locked(request.now):
                raise CoordinationReconciliationRequiredError("Reconciliation is required.")
            if not self._is_ready_locked(request.fencing_epoch):
                return QuotaCommitResult(False)
            replay_key = f"commit:{request.operation_id or request.reservation_id}"
            fingerprint = self._quota_commit_fingerprint(request)
            replay = self._quota_replays.get(replay_key)
            if replay is not None:
                if replay.fingerprint != fingerprint:
                    return QuotaCommitResult(False)
                result = replay.result
                assert isinstance(result, QuotaCommitResult)
                return QuotaCommitResult(result.committed, result.overspent, True)
            active = self._quota_reservations.pop(request.reservation_id, None)
            if active is None or active.expires_at <= request.now:
                return QuotaCommitResult(False)
            source = active.request
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
            self._quota_committed[request.reservation_id] = committed
            heapq.heappush(
                self._quota_committed_expiries,
                (committed.expires_at, request.reservation_id),
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
            self._quota_replays[replay_key] = _Replay(
                fingerprint, result, request.now + QUOTA_MONTHLY_WINDOW_SECONDS
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
            if not self._prune_quota_locked(now):
                raise CoordinationReconciliationRequiredError("Reconciliation is required.")
            if not self._is_ready_locked(fencing_epoch):
                return False
            identifier = str(reservation_id or "")
            replay_key = f"release:{operation_id or identifier}"
            fingerprint = (identifier, fencing_epoch)
            replay = self._quota_replays.get(replay_key)
            if replay is not None:
                return False
            active = self._quota_reservations.pop(identifier, None)
            result = active is not None and active.expires_at > now
            if active is not None:
                self._quota_record_counts[active.request.key_id] -= 1
            self._quota_replays[replay_key] = _Replay(
                fingerprint, result, now + QUOTA_MONTHLY_WINDOW_SECONDS
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
