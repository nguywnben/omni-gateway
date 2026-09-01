"""Lifecycle and safe operation evidence for one supplied coordination store.

This module deliberately does not select or construct a backend.  Runtime
activation belongs to a later deployment phase; callers supply the store they
already selected.
"""

from __future__ import annotations

import asyncio
import threading
import time
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from core.coordination import (
    CasRequest,
    CasResult,
    CoordinationCorruptError,
    CoordinationReconciliationRequiredError,
    CoordinationUnavailableError,
    Epoch,
    InvalidationGeneration,
    InvalidationRequest,
    InvalidationResult,
    QuotaCommitRequest,
    QuotaCommitResult,
    QuotaReservationDecision,
    QuotaReservationRequest,
)

_Result = TypeVar("_Result")

_BACKENDS = frozenset({"in_memory", "redis", "unknown"})
_OPERATIONS = frozenset(
    {
        "get",
        "set",
        "delete",
        "increment",
        "acquire_lock",
        "release_lock",
        "read_epoch",
        "advance_epoch",
        "mark_epoch_ready",
        "compare_and_set",
        "invalidate",
        "read_invalidation_generation",
        "reserve_quota",
        "commit_quota",
        "release_quota",
        "close",
    }
)
_RESULTS = frozenset(
    {
        "success",
        "rejected",
        "idempotent",
        "unavailable",
        "corrupt",
        "reconciliation_required",
        "unexpected",
    }
)
_METRICS_LOCK = threading.Lock()
_OPERATION_METRICS: dict[tuple[str, str, str], int] = {}


def _backend_name(store: object) -> str:
    name = type(store).__name__.lower()
    if "inmemory" in name:
        return "in_memory"
    if "redis" in name:
        return "redis"
    return "unknown"


def _bounded_backend(value: object) -> str:
    return value if isinstance(value, str) and value in _BACKENDS else "unknown"


def _bounded_operation(value: object) -> str:
    return value if isinstance(value, str) and value in _OPERATIONS else "close"


def _bounded_result(value: object) -> str:
    return value if isinstance(value, str) and value in _RESULTS else "unexpected"


def _increment_operation_metric(backend: object, operation: object, result: object) -> None:
    key = (_bounded_backend(backend), _bounded_operation(operation), _bounded_result(result))
    with _METRICS_LOCK:
        _OPERATION_METRICS[key] = _OPERATION_METRICS.get(key, 0) + 1


def render_coordination_operation_metrics() -> str:
    """Render fixed-cardinality coordination operation counters."""

    with _METRICS_LOCK:
        snapshot = dict(_OPERATION_METRICS)
    lines = [
        "# HELP omni_coordination_operations_total Coordination store operations.",
        "# TYPE omni_coordination_operations_total counter",
    ]
    for (backend, operation, result), count in sorted(snapshot.items()):
        lines.append(
            "omni_coordination_operations_total"
            f'{{backend="{backend}",operation="{operation}",result="{result}"}} {count}'
        )
    return "\n".join(lines) + "\n"


def clear_coordination_operation_metrics_for_testing() -> None:
    with _METRICS_LOCK:
        _OPERATION_METRICS.clear()


def record_coordination_operation_for_testing(
    backend: object, operation: object, result: object
) -> None:
    """Exercise normalization through the public renderer tests."""

    _increment_operation_metric(backend, operation, result)


def _error_category(exc: BaseException) -> str:
    if isinstance(exc, CoordinationReconciliationRequiredError):
        return "reconciliation_required"
    if isinstance(exc, CoordinationUnavailableError):
        return "unavailable"
    if isinstance(exc, CoordinationCorruptError):
        return "corrupt"
    return "unexpected"


def _result_category(result: object) -> str:
    if bool(getattr(result, "idempotent", False)):
        return "idempotent"
    if hasattr(result, "accepted") and not bool(getattr(result, "accepted")):
        return "rejected"
    if hasattr(result, "applied") and not bool(getattr(result, "applied")):
        return "rejected"
    if isinstance(result, bool) and not result:
        return "rejected"
    return "success"


class CoordinationService:
    """Observe one supplied coordination store without selecting its backend."""

    def __init__(self, store: Any) -> None:
        self._store = store
        self._backend = _backend_name(store)
        self._available = True
        self._closed = False
        self._failure_count = 0
        self._last_error_category = ""
        self._last_failure_at: float | None = None
        self._recovered_at: float | None = None
        self._lifecycle_lock = asyncio.Lock()

    def health_snapshot(self) -> dict[str, object]:
        """Return attribution-free lifecycle evidence suitable for diagnostics."""

        return {
            "backend": self._backend,
            "available": self._available,
            "closed": self._closed,
            "failure_count": self._failure_count,
            "last_error_category": self._last_error_category,
            "last_failure_at": self._last_failure_at,
            "recovered_at": self._recovered_at,
        }

    async def _run(
        self,
        operation_name: str,
        operation: Callable[..., Awaitable[_Result]],
        *args: object,
        **kwargs: object,
    ) -> _Result:
        if self._closed:
            error = CoordinationUnavailableError("Coordination service is closed.")
            self._record_failure(operation_name, error)
            raise error
        try:
            result = await operation(*args, **kwargs)
        except Exception as exc:
            self._record_failure(operation_name, exc)
            raise
        if not self._available:
            self._recovered_at = time.time()
        self._available = True
        _increment_operation_metric(self._backend, operation_name, _result_category(result))
        return result

    def _record_failure(self, operation_name: str, exc: BaseException) -> None:
        category = _error_category(exc)
        self._available = False
        self._failure_count += 1
        self._last_error_category = category
        self._last_failure_at = time.time()
        _increment_operation_metric(self._backend, operation_name, category)

    async def get(self, key: str) -> Any:
        return await self._run("get", self._store.get, key)

    async def set(self, key: str, value: Any, ttl_seconds: float | None = None) -> None:
        await self._run("set", self._store.set, key, value, ttl_seconds)

    async def delete(self, key: str) -> None:
        await self._run("delete", self._store.delete, key)

    async def increment(self, key: str, amount: int = 1, ttl_seconds: float | None = None) -> int:
        return await self._run("increment", self._store.increment, key, amount, ttl_seconds)

    async def acquire_lock(self, lock_key: str, ttl_seconds: float = 10.0) -> bool:
        return await self._run("acquire_lock", self._store.acquire_lock, lock_key, ttl_seconds)

    async def release_lock(self, lock_key: str) -> None:
        await self._run("release_lock", self._store.release_lock, lock_key)

    async def read_epoch(self) -> Epoch:
        return await self._run("read_epoch", self._store.read_epoch)

    async def advance_epoch(self, expected_epoch: int, operation_id: str) -> Epoch:
        return await self._run(
            "advance_epoch", self._store.advance_epoch, expected_epoch, operation_id
        )

    async def mark_epoch_ready(self, epoch: int, operation_id: str) -> Epoch:
        return await self._run(
            "mark_epoch_ready", self._store.mark_epoch_ready, epoch, operation_id
        )

    async def compare_and_set(self, request: CasRequest) -> CasResult:
        return await self._run("compare_and_set", self._store.compare_and_set, request)

    async def invalidate(self, request: InvalidationRequest) -> InvalidationResult:
        return await self._run("invalidate", self._store.invalidate, request)

    async def read_invalidation_generation(self, scope: str) -> InvalidationGeneration:
        return await self._run(
            "read_invalidation_generation", self._store.read_invalidation_generation, scope
        )

    async def reserve_quota(self, request: QuotaReservationRequest) -> QuotaReservationDecision:
        return await self._run("reserve_quota", self._store.reserve_quota, request)

    async def commit_quota(self, request: QuotaCommitRequest) -> QuotaCommitResult:
        return await self._run("commit_quota", self._store.commit_quota, request)

    async def release_quota(self, reservation_id: str, **kwargs: object) -> bool:
        return await self._run("release_quota", self._store.release_quota, reservation_id, **kwargs)

    async def close(self) -> None:
        async with self._lifecycle_lock:
            if self._closed:
                _increment_operation_metric(self._backend, "close", "idempotent")
                return
            self._closed = True
            try:
                await self._store.close()
            except Exception as exc:
                self._record_failure("close", exc)
                raise
            _increment_operation_metric(self._backend, "close", "success")
