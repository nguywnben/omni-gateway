"""Contracts for canonical and transitional management API routes."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import httpx
import main


class ManagementApiRouteTests(unittest.IsolatedAsyncioTestCase):
    def test_credentials_use_the_canonical_route_in_openapi(self):
        paths = set(main.app.openapi()["paths"])

        self.assertIn("/api/credentials/status", paths)
        self.assertIn("/api/credentials/action", paths)
        self.assertFalse(any(path.startswith("/api/creds") for path in paths))

    async def test_legacy_credential_routes_remain_registered_for_beta_migration(self):
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            canonical = await client.get("/api/credentials/status")
            legacy = await client.get("/api/creds/status")

        self.assertEqual(canonical.status_code, 401)
        self.assertEqual(legacy.status_code, 401)


if __name__ == "__main__":
    unittest.main()
