"""Storage backend selection must be explicit and fail closed."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.storage_adapter import StorageAdapter


class StorageBackendSelectionTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_ambiguous_external_storage_configuration(self):
        adapter = StorageAdapter()
        with patch.dict(
            os.environ,
            {
                "POSTGRESQL_URI": "postgresql://database",
                "MONGODB_URI": "mongodb://database",
            },
        ):
            with self.assertRaisesRegex(RuntimeError, "Configure only one external storage"):
                await adapter.initialize()

    async def test_postgresql_failure_does_not_fallback_to_sqlite(self):
        from core.storage import postgresql_manager

        adapter = StorageAdapter()
        backend = AsyncMock()
        backend.initialize.side_effect = RuntimeError("connection failed")

        with (
            patch.dict(os.environ, {"POSTGRESQL_URI": "postgresql://database", "MONGODB_URI": ""}),
            patch.object(postgresql_manager, "PostgreSQLManager", return_value=backend),
            patch("core.storage.sqlite_manager.SQLiteManager") as sqlite_manager,
        ):
            with self.assertRaisesRegex(RuntimeError, "PostgreSQL storage backend is unavailable"):
                await adapter.initialize()

        backend.close.assert_awaited_once_with()
        sqlite_manager.assert_not_called()
        self.assertIsNone(adapter._backend)
        self.assertFalse(adapter._initialized)

    async def test_mongodb_failure_does_not_fallback_to_sqlite(self):
        from core.storage import mongodb_manager

        adapter = StorageAdapter()
        backend = AsyncMock()
        backend.initialize.side_effect = RuntimeError("connection failed")

        with (
            patch.dict(os.environ, {"POSTGRESQL_URI": "", "MONGODB_URI": "mongodb://database"}),
            patch.object(mongodb_manager, "MongoDBManager", return_value=backend),
            patch("core.storage.sqlite_manager.SQLiteManager") as sqlite_manager,
        ):
            with self.assertRaisesRegex(RuntimeError, "MongoDB storage backend is unavailable"):
                await adapter.initialize()

        backend.close.assert_awaited_once_with()
        sqlite_manager.assert_not_called()
        self.assertIsNone(adapter._backend)
        self.assertFalse(adapter._initialized)


if __name__ == "__main__":
    unittest.main()
