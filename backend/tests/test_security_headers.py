"""Security header regression tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from starlette.requests import Request
from starlette.responses import JSONResponse

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import add_security_headers


def build_request(path: str, *, forwarded_proto: str = "") -> Request:
    headers = []
    if forwarded_proto:
        headers.append((b"x-forwarded-proto", forwarded_proto.encode()))
    return Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "headers": headers,
            "client": ("127.0.0.1", 50000),
            "server": ("localhost", 4283),
        }
    )


class SecurityHeaderTests(unittest.IsolatedAsyncioTestCase):
    async def test_dynamic_api_responses_are_not_cached(self):
        async def next_handler(_request):
            return JSONResponse({"ok": True})

        response = await add_security_headers(
            build_request("/api/config/get"),
            next_handler,
        )

        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(response.headers["x-frame-options"], "DENY")

    async def test_https_proxy_requests_receive_hsts(self):
        async def next_handler(_request):
            return JSONResponse({"ok": True})

        response = await add_security_headers(
            build_request("/health", forwarded_proto="https"),
            next_handler,
        )

        self.assertIn("max-age=31536000", response.headers["strict-transport-security"])


if __name__ == "__main__":
    unittest.main()
