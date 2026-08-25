"""Distributed State Store Interface & Implementation.

Enables seamless transition from in-memory single worker state
to distributed Redis / Valkey state management for multi-worker scaling.
"""

from __future__ import annotations

import abc
import asyncio
import math
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

QUOTA_RATE_WINDOW_SECONDS = 60.0
QUOTA_DAILY_WINDOW_SECONDS = 86_400.0
QUOTA_MONTHLY_WINDOW_SECONDS = 30 * QUOTA_DAILY_WINDOW_SECONDS


@dataclass(frozen=True)
class QuotaReservationRequest:
    """One atomic request against a virtual key's active quota windows."""

    reservation_id: str
    key_id: str
    now: float
    ttl_seconds: float
    estimated_tokens: int
    estimated_cost_usd: float
    rpm_limit: Optional[int]
    tpm_limit: Optional[int]
    daily_budget_usd: Optional[float]
    monthly_budget_usd: Optional[float]
    daily_spend_usd: float
    monthly_spend_usd: float
    daily_snapshot_started_at: float
    monthly_snapshot_started_at: float


@dataclass(frozen=True)
class QuotaReservationDecision:
    accepted: bool
    reservation_id: str
    reason: str = ""
    retry_after_seconds: int = 0
    idempotent: bool = False


@dataclass(frozen=True)
class QuotaCommitRequest:
    reservation_id: str
    now: float
    actual_tokens: int
    actual_cost_usd: float
    durable_cost_recorded: bool


@dataclass(frozen=True)
class QuotaCommitResult:
    committed: bool
    overspent: bool = False
    idempotent: bool = False


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
    """Zero-dependency thread/task safe in-memory state store."""

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[Optional[float], Any]] = {}
        self._locks: Dict[str, float] = {}
        self._quota_reservations: Dict[str, _ActiveQuotaReservation] = {}
        self._quota_committed: Dict[str, _CommittedQuotaReservation] = {}
        self._async_lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self._async_lock:
            if key not in self._store:
                return None
            expires_at, val = self._store[key]
            if expires_at is not None and time.time() > expires_at:
                self._store.pop(key, None)
                return None
            return val

    async def set(self, key: str, value: Any, ttl_seconds: Optional[float] = None) -> None:
        async with self._async_lock:
            expires_at = time.time() + ttl_seconds if ttl_seconds is not None else None
            self._store[key] = (expires_at, value)

    async def delete(self, key: str) -> None:
        async with self._async_lock:
            self._store.pop(key, None)

    async def increment(
        self, key: str, amount: int = 1, ttl_seconds: Optional[float] = None
    ) -> int:
        async with self._async_lock:
            current = 0
            if key in self._store:
                expires_at, val = self._store[key]
                if expires_at is None or time.time() <= expires_at:
                    current = int(val) if isinstance(val, (int, str)) and str(val).isdigit() else 0
            new_val = current + amount
            expires_at = time.time() + ttl_seconds if ttl_seconds is not None else None
            self._store[key] = (expires_at, new_val)
            return new_val

    async def acquire_lock(self, lock_key: str, ttl_seconds: float = 10.0) -> bool:
        async with self._async_lock:
            now = time.time()
            if lock_key in self._locks:
                if self._locks[lock_key] > now:
                    return False
            self._locks[lock_key] = now + ttl_seconds
            return True

    async def release_lock(self, lock_key: str) -> None:
        async with self._async_lock:
            self._locks.pop(lock_key, None)

    def _reconcile_quota_locked(
        self,
        *,
        key_id: str,
        now: float,
        daily_snapshot_started_at: float = 0.0,
        monthly_snapshot_started_at: float = 0.0,
    ) -> None:
        for reservation_id, active in list(self._quota_reservations.items()):
            if active.expires_at <= now:
                self._quota_reservations.pop(reservation_id, None)

        for reservation_id, committed in list(self._quota_committed.items()):
            if committed.key_id != key_id:
                continue
            if committed.durable_cost_recorded:
                if daily_snapshot_started_at >= committed.committed_at:
                    committed.daily_reconciled = True
                if monthly_snapshot_started_at >= committed.committed_at:
                    committed.monthly_reconciled = True
            rate_expired = committed.committed_at + QUOTA_RATE_WINDOW_SECONDS <= now
            daily_expired = (
                committed.daily_reconciled
                or committed.committed_at + QUOTA_DAILY_WINDOW_SECONDS <= now
            )
            monthly_expired = (
                committed.monthly_reconciled
                or committed.committed_at + QUOTA_MONTHLY_WINDOW_SECONDS <= now
            )
            if rate_expired and daily_expired and monthly_expired:
                self._quota_committed.pop(reservation_id, None)

    def _active_for_key_locked(self, key_id: str) -> list[_ActiveQuotaReservation]:
        return [
            active
            for active in self._quota_reservations.values()
            if active.request.key_id == key_id
        ]

    def _committed_for_key_locked(self, key_id: str) -> list[_CommittedQuotaReservation]:
        return [
            committed for committed in self._quota_committed.values() if committed.key_id == key_id
        ]

    @staticmethod
    def _retry_after(now: float, timestamps: list[float]) -> int:
        if not timestamps:
            return 1
        next_slot = min(timestamp + QUOTA_RATE_WINDOW_SECONDS for timestamp in timestamps)
        return max(1, math.ceil(next_slot - now))

    async def reserve_quota(self, request: QuotaReservationRequest) -> QuotaReservationDecision:
        async with self._async_lock:
            self._reconcile_quota_locked(
                key_id=request.key_id,
                now=request.now,
                daily_snapshot_started_at=request.daily_snapshot_started_at,
                monthly_snapshot_started_at=request.monthly_snapshot_started_at,
            )
            if request.reservation_id in self._quota_reservations:
                return QuotaReservationDecision(
                    True,
                    request.reservation_id,
                    idempotent=True,
                )
            if request.reservation_id in self._quota_committed:
                return QuotaReservationDecision(
                    True,
                    request.reservation_id,
                    idempotent=True,
                )

            active = self._active_for_key_locked(request.key_id)
            committed = self._committed_for_key_locked(request.key_id)
            rate_cutoff = request.now - QUOTA_RATE_WINDOW_SECONDS
            active_rate = [item for item in active if item.request.now > rate_cutoff]
            committed_rate = [item for item in committed if item.committed_at > rate_cutoff]

            if request.rpm_limit is not None:
                timestamps = [item.request.now for item in active_rate] + [
                    item.committed_at for item in committed_rate
                ]
                if len(timestamps) >= request.rpm_limit:
                    return QuotaReservationDecision(
                        False,
                        request.reservation_id,
                        reason="rpm",
                        retry_after_seconds=self._retry_after(request.now, timestamps),
                    )

            if request.tpm_limit is not None:
                reserved_tokens = sum(item.request.estimated_tokens for item in active_rate)
                committed_tokens = sum(item.actual_tokens for item in committed_rate)
                if (
                    reserved_tokens + committed_tokens + request.estimated_tokens
                    > request.tpm_limit
                ):
                    timestamps = [item.request.now for item in active_rate] + [
                        item.committed_at for item in committed_rate
                    ]
                    return QuotaReservationDecision(
                        False,
                        request.reservation_id,
                        reason="tpm",
                        retry_after_seconds=self._retry_after(request.now, timestamps),
                    )

            active_cost = sum(item.request.estimated_cost_usd for item in active)
            daily_unreconciled = sum(
                item.actual_cost_usd for item in committed if not item.daily_reconciled
            )
            monthly_unreconciled = sum(
                item.actual_cost_usd for item in committed if not item.monthly_reconciled
            )
            if request.daily_budget_usd is not None:
                projected_daily = (
                    request.daily_spend_usd
                    + daily_unreconciled
                    + active_cost
                    + request.estimated_cost_usd
                )
                if projected_daily > request.daily_budget_usd:
                    return QuotaReservationDecision(
                        False,
                        request.reservation_id,
                        reason="daily_budget",
                    )
            if request.monthly_budget_usd is not None:
                projected_monthly = (
                    request.monthly_spend_usd
                    + monthly_unreconciled
                    + active_cost
                    + request.estimated_cost_usd
                )
                if projected_monthly > request.monthly_budget_usd:
                    return QuotaReservationDecision(
                        False,
                        request.reservation_id,
                        reason="monthly_budget",
                    )

            self._quota_reservations[request.reservation_id] = _ActiveQuotaReservation(
                request=request,
                expires_at=request.now + max(1.0, request.ttl_seconds),
            )
            return QuotaReservationDecision(True, request.reservation_id)

    async def commit_quota(self, request: QuotaCommitRequest) -> QuotaCommitResult:
        async with self._async_lock:
            if request.reservation_id in self._quota_committed:
                return QuotaCommitResult(False, idempotent=True)
            active = self._quota_reservations.pop(request.reservation_id, None)
            if active is None or active.expires_at <= request.now:
                return QuotaCommitResult(False)

            source = active.request
            committed = _CommittedQuotaReservation(
                reservation_id=request.reservation_id,
                key_id=source.key_id,
                committed_at=request.now,
                actual_tokens=max(0, int(request.actual_tokens)),
                actual_cost_usd=max(0.0, float(request.actual_cost_usd)),
                durable_cost_recorded=bool(request.durable_cost_recorded),
                daily_reconciled=source.daily_budget_usd is None,
                monthly_reconciled=source.monthly_budget_usd is None,
            )
            self._quota_committed[request.reservation_id] = committed

            active_for_key = self._active_for_key_locked(source.key_id)
            committed_for_key = self._committed_for_key_locked(source.key_id)
            rate_cutoff = request.now - QUOTA_RATE_WINDOW_SECONDS
            active_tokens = sum(
                item.request.estimated_tokens
                for item in active_for_key
                if item.request.now > rate_cutoff
            )
            committed_tokens = sum(
                item.actual_tokens for item in committed_for_key if item.committed_at > rate_cutoff
            )
            active_cost = sum(item.request.estimated_cost_usd for item in active_for_key)
            daily_cost = sum(
                item.actual_cost_usd for item in committed_for_key if not item.daily_reconciled
            )
            monthly_cost = sum(
                item.actual_cost_usd for item in committed_for_key if not item.monthly_reconciled
            )
            overspent = bool(
                (
                    source.tpm_limit is not None
                    and active_tokens + committed_tokens > source.tpm_limit
                )
                or (
                    source.daily_budget_usd is not None
                    and source.daily_spend_usd + active_cost + daily_cost > source.daily_budget_usd
                )
                or (
                    source.monthly_budget_usd is not None
                    and source.monthly_spend_usd + active_cost + monthly_cost
                    > source.monthly_budget_usd
                )
            )
            return QuotaCommitResult(True, overspent=overspent)

    async def release_quota(self, reservation_id: str, *, now: float) -> bool:
        async with self._async_lock:
            active = self._quota_reservations.pop(str(reservation_id or ""), None)
            return active is not None and active.expires_at > now


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
