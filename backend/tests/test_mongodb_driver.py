"""Contracts for the asynchronous MongoDB storage driver."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.credential_pool_mutation import CredentialPoolMutation
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

    async def test_coordinated_runtime_never_reuses_coordination_redis_as_legacy_cache(self):
        manager = MongoDBManager()
        with patch.dict(
            "os.environ",
            {
                "OMNI_RUNTIME_MODE": "coordinated",
                "REDIS_URL": "redis://coordination-secret/0",
            },
            clear=False,
        ):
            await manager._init_redis()

        self.assertIsNone(manager._redis)
        self.assertFalse(manager._redis_enabled)

    async def test_coordinated_pool_mutation_uses_transactional_durable_gate(self):
        manager = MongoDBManager()
        manager._initialized = True
        manager._db = {"credential_pool_write_gates": AsyncMock()}
        session = AsyncMock()

        async def with_transaction(callback):
            return await callback(session)

        session.with_transaction = AsyncMock(side_effect=with_transaction)

        class SessionContext:
            async def __aenter__(self):
                return session

            async def __aexit__(self, exc_type, exc, traceback):
                return False

        client = MagicMock()
        client.start_session.return_value = SessionContext()
        manager._client = client
        manager._mutate_credential_pool_in_session = AsyncMock(
            return_value=CredentialPoolMutation((), (), {"action": "none"})
        )

        with patch.dict("os.environ", {"OMNI_RUNTIME_MODE": "coordinated"}, clear=False):
            result = await manager.mutate_credential_pool(
                "primary", lambda records: CredentialPoolMutation((), (), {"action": "none"})
            )

        self.assertEqual(result.result, {"action": "none"})
        session.with_transaction.assert_awaited_once()
        manager._db["credential_pool_write_gates"].update_one.assert_awaited_once()
        gate_filter = manager._db["credential_pool_write_gates"].update_one.await_args.args[0]
        self.assertEqual(gate_filter, {"_id": "primary"})

    async def test_standalone_pool_mutation_rebuilds_the_legacy_routing_cache(self):
        manager = MongoDBManager()
        manager._initialized = True
        mutation = CredentialPoolMutation((), (), {"action": "none"})
        manager._mutate_credential_pool_in_session = AsyncMock(return_value=mutation)
        manager._redis_enabled = True
        manager._rebuild_redis_cache = AsyncMock()

        with patch.dict("os.environ", {"OMNI_RUNTIME_MODE": "standalone"}, clear=False):
            result = await manager.mutate_credential_pool(
                "primary", lambda records: CredentialPoolMutation((), (), {"action": "none"})
            )

        self.assertIs(result, mutation)
        manager._rebuild_redis_cache.assert_awaited_once_with("primary")


if __name__ == "__main__":
    unittest.main()
