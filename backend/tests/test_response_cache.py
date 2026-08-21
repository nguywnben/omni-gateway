"""Tests for Response Caching Layer."""

from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.response_cache import ResponseCache, generate_cache_key


class ResponseCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cache = ResponseCache(default_ttl_seconds=2, max_entries=5)

    def test_cache_key_generation_deterministic(self) -> None:
        payload1 = {"messages": [{"role": "user", "content": "hello"}], "temperature": 0.7}
        payload2 = {"temperature": 0.7, "messages": [{"role": "user", "content": "hello"}]}
        
        key1 = generate_cache_key("gpt-4o", payload1)
        key2 = generate_cache_key("gpt-4o", payload2)
        key_stream = generate_cache_key("gpt-4o", payload1, stream=True)
        
        self.assertEqual(key1, key2)
        self.assertNotEqual(key1, key_stream)

    def test_cache_set_and_get(self) -> None:
        key = "test-hash-1"
        data = {"response": "world", "status_code": 200}
        self.cache.set(key, data)
        
        cached = self.cache.get(key)
        self.assertEqual(cached, data)

    def test_cache_expiration(self) -> None:
        key = "test-hash-exp"
        self.cache.set(key, {"value": 123}, ttl_seconds=1)
        self.assertEqual(self.cache.get(key), {"value": 123})
        
        time.sleep(1.1)
        self.assertIsNone(self.cache.get(key))

    def test_cache_lru_capacity(self) -> None:
        for i in range(5):
            self.cache.set(f"k{i}", f"v{i}")
            
        self.assertEqual(self.cache.size(), 5)
        # Adding 6th element should evict the oldest (k0)
        self.cache.set("k5", "v5")
        self.assertIsNone(self.cache.get("k0"))
        self.assertEqual(self.cache.get("k5"), "v5")


if __name__ == "__main__":
    unittest.main()
