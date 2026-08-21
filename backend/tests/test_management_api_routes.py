"""Contracts for the stable management API routes."""

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
    def test_openapi_operation_ids_are_unique(self):
        operation_ids = [
            operation["operationId"]
            for path_item in main.app.openapi()["paths"].values()
            for method, operation in path_item.items()
            if method
            in {
                "delete",
                "get",
                "head",
                "options",
                "patch",
                "post",
                "put",
                "trace",
            }
        ]

        duplicates = sorted(
            operation_id
            for operation_id in set(operation_ids)
            if operation_ids.count(operation_id) > 1
        )
        self.assertEqual(duplicates, [])

    def test_credentials_use_the_canonical_route_in_openapi(self):
        paths = set(main.app.openapi()["paths"])

        self.assertIn("/api/credentials/status", paths)
        self.assertIn("/api/credentials/action", paths)
        self.assertIn("/api/credentials/verify/{filename}", paths)
        self.assertNotIn("/api/credentials/verify-project/{filename}", paths)
        self.assertFalse(any(path.startswith("/api/creds") for path in paths))

    async def test_beta_credential_route_is_removed_from_the_stable_api(self):
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            canonical = await client.get("/api/credentials/status")
            legacy = await client.get("/api/creds/status")

        self.assertEqual(canonical.status_code, 401)
        self.assertEqual(legacy.status_code, 404)

    async def test_management_api_negotiates_and_reports_the_console_locale(self):
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/api/route-that-does-not-exist",
                headers={"Accept-Language": "vi-VN,vi;q=0.9,en;q=0.7"},
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers["Content-Language"], "vi")
        self.assertEqual(
            response.json()["detail"],
            "Thông tin được yêu cầu đang thiếu hoặc hiện không khả dụng.",
        )

    async def test_public_protocol_routes_do_not_localize_error_contracts(self):
        transport = httpx.ASGITransport(app=main.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(
                "/v1/route-that-does-not-exist",
                headers={"Accept-Language": "vi"},
            )

        self.assertEqual(response.status_code, 404)
        self.assertNotIn("Content-Language", response.headers)
        self.assertNotIn("Thông tin được yêu cầu", response.text)


if __name__ == "__main__":
    unittest.main()
