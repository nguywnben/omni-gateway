"""Runtime behavior tests for shared outbound HTTP clients."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.httpx_client import HttpxClientManager


class HttpxClientManagerTests(unittest.IsolatedAsyncioTestCase):
    async def test_reuses_the_client_for_matching_request_settings(self):
        manager = HttpxClientManager()
        try:
            async with manager.get_client(timeout=15.0) as first:
                async with manager.get_client(timeout=15.0) as second:
                    self.assertIs(first, second)
        finally:
            await manager.close()

    async def test_close_releases_runtime_clients(self):
        manager = HttpxClientManager()
        async with manager.get_client(timeout=15.0) as client:
            self.assertFalse(client.is_closed)

        await manager.close()
        self.assertTrue(client.is_closed)

    async def test_does_not_share_clients_with_different_client_options(self):
        manager = HttpxClientManager()
        try:
            async with manager.get_client(timeout=15.0) as default_client:
                async with manager.get_client(
                    timeout=15.0, follow_redirects=True
                ) as redirect_client:
                    self.assertIsNot(default_client, redirect_client)
        finally:
            await manager.close()


if __name__ == "__main__":
    unittest.main()
