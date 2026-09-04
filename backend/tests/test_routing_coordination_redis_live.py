from __future__ import annotations

import asyncio
import os
import sys
import unittest
import uuid
from pathlib import Path
from typing import Any

import redis.asyncio as redis_asyncio

BACKEND_DIR = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from core.redis_state_store import RedisStateStore
from core.routing_coordination import (
    CACHE_SCOPE_EXACT,
    CacheKind,
    RoutingCoordinationAdapter,
)
from test_coordination_redis_live import _close_setup_resources, _teardown_live_resources

REDIS_URI = os.getenv("OMNI_TEST_REDIS_URI", "").strip()


@unittest.skipUnless(REDIS_URI, "OMNI_TEST_REDIS_URI is not configured")
class RoutingCoordinationRedisLiveTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.store: RedisStateStore | None = None
        self.cleanup_client: Any | None = None
        try:
            self.namespace = f"w417-live-{uuid.uuid4().hex}"
            self.store = RedisStateStore(REDIS_URI, deployment_namespace=self.namespace)
            self.cleanup_client = redis_asyncio.from_url(REDIS_URI, decode_responses=False)
            await asyncio.wait_for(self.store.read_epoch(), timeout=5)
        except BaseException:
            await _close_setup_resources(self.store, self.cleanup_client)
            raise
        self.first = RoutingCoordinationAdapter(
            self.store, identifier_key=b"l" * 32, fencing_epoch=1
        )
        self.second = RoutingCoordinationAdapter(
            self.store, identifier_key=b"l" * 32, fencing_epoch=1
        )

    async def asyncTearDown(self) -> None:
        assert self.store is not None
        assert self.cleanup_client is not None
        await _teardown_live_resources(
            self.store,
            self.cleanup_client,
            f"{self.store._prefix}:*",
        )

    async def test_live_exclusive_cooldown_and_invalidation_parity(self) -> None:
        first, second = await asyncio.gather(
            self.first.acquire_credential(
                "primary", "live-private.json", ttl_seconds=5, max_concurrency=1
            ),
            self.second.acquire_credential(
                "primary", "live-private.json", ttl_seconds=5, max_concurrency=1
            ),
        )
        self.assertEqual(sum(item is not None for item in (first, second)), 1)

        await self.first.record_route_outcome(
            "primary",
            "live-private.json",
            "live-model",
            success=False,
            failure_kind="rate_limited",
            retry_after_seconds=5,
            latency_ms=None,
        )
        self.assertGreater(
            (
                await self.second.read_route_outcome("primary", "live-private.json", "live-model")
            ).retry_after_seconds,
            0,
        )

        generation = await self.first.current_generation(CACHE_SCOPE_EXACT)
        await self.first.publish_cache_metadata(
            CacheKind.EXACT,
            "live-cache-key",
            content_digest="e" * 64,
            media_kind="json",
            generation=generation,
            ttl_seconds=5,
        )
        self.assertIsNotNone(
            await self.second.resolve_cache_metadata(
                CacheKind.EXACT, "live-cache-key", generation=generation
            )
        )
        invalidated = await self.second.invalidate(CACHE_SCOPE_EXACT)
        self.assertIsNone(
            await self.first.resolve_cache_metadata(
                CacheKind.EXACT, "live-cache-key", generation=invalidated
            )
        )


if __name__ == "__main__":
    unittest.main()
