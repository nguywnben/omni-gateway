"""Contracts for the asynchronous MongoDB storage driver."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.storage.mongodb_manager import AsyncMongoClient, MongoDBManager


class MongoDBDriverTests(unittest.IsolatedAsyncioTestCase):
    def test_uses_pymongo_async_client(self):
        self.assertEqual(AsyncMongoClient.__module__, "pymongo.asynchronous.mongo_client")

    async def test_close_awaits_async_client_shutdown(self):
        manager = MongoDBManager()
        client = AsyncMock()
        manager._client = client
        manager._db = object()
        manager._initialized = True

        await manager.close()

        client.close.assert_awaited_once_with()
        self.assertIsNone(manager._client)
        self.assertIsNone(manager._db)
        self.assertFalse(manager._initialized)


if __name__ == "__main__":
    unittest.main()
