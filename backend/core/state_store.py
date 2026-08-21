"""Distributed State Store Interface & Implementation.

Enables seamless transition from in-memory single worker state
to distributed Redis / Valkey state management for multi-worker scaling.
"""

from __future__ import annotations

import abc
import asyncio
import time
from typing import Any, Dict, List, Optional


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
    async def increment(self, key: str, amount: int = 1, ttl_seconds: Optional[float] = None) -> int:
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


class InMemoryStateStore(BaseStateStore):
    """Zero-dependency thread/task safe in-memory state store."""

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[Optional[float], Any]] = {}
        self._locks: Dict[str, float] = {}
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

    async def increment(self, key: str, amount: int = 1, ttl_seconds: Optional[float] = None) -> int:
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

    async def increment(self, key: str, amount: int = 1, ttl_seconds: Optional[float] = None) -> int:
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
