"""Global request-body limit contracts."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.request_limits import RequestBodyLimitMiddleware, get_max_request_body_bytes


def build_test_app(max_body_bytes: int) -> FastAPI:
    app = FastAPI()
    app.add_middleware(RequestBodyLimitMiddleware, max_body_bytes=max_body_bytes)

    @app.post("/{path:path}")
    async def consume_body(request: Request, path: str):
        return {"received": len(await request.body()), "path": path}

    return app


class RequestBodyLimitTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_fixed_length_openai_request_with_native_error(self):
        transport = ASGITransport(app=build_test_app(32), raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/v1/chat/completions",
                content=b"x" * 33,
                headers={"content-type": "application/json"},
            )

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["error"]["code"], "request_too_large")

    async def test_rejects_chunked_anthropic_request_with_native_error(self):
        async def body_chunks():
            yield b"x" * 20
            yield b"y" * 20

        transport = ASGITransport(app=build_test_app(32), raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/v1/messages",
                content=body_chunks(),
                headers={"content-type": "application/json"},
            )

        self.assertEqual(response.status_code, 413)
        self.assertEqual(response.json()["error"]["type"], "request_too_large")

    async def test_allows_request_at_the_limit(self):
        transport = ASGITransport(app=build_test_app(32))
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/example", content=b"x" * 32)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["received"], 32)

    def test_validates_environment_configuration(self):
        with patch.dict(os.environ, {"MAX_REQUEST_BODY_MB": "2"}):
            self.assertEqual(get_max_request_body_bytes(), 2 * 1024 * 1024)
        with patch.dict(os.environ, {"MAX_REQUEST_BODY_MB": "0"}):
            with self.assertRaisesRegex(RuntimeError, "between 1 and 512"):
                get_max_request_body_bytes()
        with patch.dict(os.environ, {"MAX_REQUEST_BODY_MB": "invalid"}):
            with self.assertRaisesRegex(RuntimeError, "must be an integer"):
                get_max_request_body_bytes()


if __name__ == "__main__":
    unittest.main()
