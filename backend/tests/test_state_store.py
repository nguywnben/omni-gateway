"""Tests for Distributed State Store Module."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.state_store import InMemoryStateStore


class StateStoreTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.store = InMemoryStateStore()

    async def test_get_set_delete(self) -> None:
        await self.store.set("test_k", "hello_val", ttl_seconds=10)
        self.assertEqual(await self.store.get("test_k"), "hello_val")

        await self.store.delete("test_k")
        self.assertIsNone(await self.store.get("test_k"))

    async def test_atomic_increment(self) -> None:
        v1 = await self.store.increment("counter_1")
        self.assertEqual(v1, 1)

        v2 = await self.store.increment("counter_1", amount=5)
        self.assertEqual(v2, 6)

    async def test_lock_acquire_and_release(self) -> None:
        acquired = await self.store.acquire_lock("resource_x", ttl_seconds=5)
        self.assertTrue(acquired)

        # Second acquire should fail
        acquired_second = await self.store.acquire_lock("resource_x", ttl_seconds=5)
        self.assertFalse(acquired_second)

        # Release and reacquire
        await self.store.release_lock("resource_x")
        acquired_again = await self.store.acquire_lock("resource_x", ttl_seconds=5)
        self.assertTrue(acquired_again)


if __name__ == "__main__":
    unittest.main()
