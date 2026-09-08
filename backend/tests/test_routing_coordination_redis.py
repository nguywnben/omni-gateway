from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

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
from test_redis_state_store import FakeRedisModule, StatefulRedisClient


class RoutingCoordinationRedisParityTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.client = StatefulRedisClient()
        module = FakeRedisModule(self.client)
        first_store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="routing-parity",
            _redis_module_for_testing=module,
        )
        second_store = RedisStateStore(
            "redis://redis.example/0",
            deployment_namespace="routing-parity",
            _redis_module_for_testing=module,
        )
        self.client.epoch_exists = False
        self.client.initialization_exists = False
        await first_store.initialize_epoch()
        self.first = RoutingCoordinationAdapter(
            first_store, identifier_key=b"p" * 32, fencing_epoch=1
        )
        self.second = RoutingCoordinationAdapter(
            second_store, identifier_key=b"p" * 32, fencing_epoch=1
        )

    async def test_exclusive_lease_cooldown_and_cache_invalidation_match_reference(self) -> None:
        first, second = await asyncio.gather(
            self.first.acquire_credential(
                "primary", "private.json", ttl_seconds=10, max_concurrency=1
            ),
            self.second.acquire_credential(
                "primary", "private.json", ttl_seconds=10, max_concurrency=1
            ),
        )
        self.assertEqual(sum(item is not None for item in (first, second)), 1)

        await self.first.record_route_outcome(
            "primary",
            "private.json",
            "private-model",
            success=False,
            failure_kind="transient",
            retry_after_seconds=5,
            latency_ms=None,
        )
        outcome = await self.second.read_route_outcome("primary", "private.json", "private-model")
        self.assertEqual((outcome.failure_count, outcome.failure_kind), (1, "transient"))

        generation = await self.first.current_generation(CACHE_SCOPE_EXACT)
        self.assertTrue(
            await self.first.publish_cache_metadata(
                CacheKind.EXACT,
                "private-cache-key",
                content_digest="d" * 64,
                media_kind="json",
                generation=generation,
                ttl_seconds=10,
            )
        )
        self.assertIsNotNone(
            await self.second.resolve_cache_metadata(
                CacheKind.EXACT, "private-cache-key", generation=generation
            )
        )
        invalidated = await self.second.invalidate(CACHE_SCOPE_EXACT)
        self.assertIsNone(
            await self.first.resolve_cache_metadata(
                CacheKind.EXACT, "private-cache-key", generation=invalidated
            )
        )

        transcript = repr(self.client.script_calls)
        self.assertNotIn("private.json", transcript)
        self.assertNotIn("private-model", transcript)
        self.assertNotIn("private-cache-key", transcript)

    async def test_cancelled_unknown_acquire_remains_safe_until_bounded_expiry(self) -> None:
        self.client.cancel_after_response_boundary.add("cas")
        with self.assertRaises(asyncio.CancelledError):
            await self.first.acquire_credential(
                "primary", "cancelled.json", ttl_seconds=1, max_concurrency=1
            )

        self.assertIsNone(
            await self.second.acquire_credential(
                "primary", "cancelled.json", ttl_seconds=1, max_concurrency=1
            )
        )
        self.client.advance(1_001)
        self.assertIsNotNone(
            await self.second.acquire_credential(
                "primary", "cancelled.json", ttl_seconds=1, max_concurrency=1
            )
        )


if __name__ == "__main__":
    unittest.main()
