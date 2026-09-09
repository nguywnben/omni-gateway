"""Deterministic lifecycle tests for public streaming responses."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from fastapi import Response
from starlette.requests import ClientDisconnect

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.httpx_client import UpstreamStreamProtocolError, iter_bounded_lines
from core.router.stream_passthrough import (
    ManagedStreamingResponse,
    build_streaming_response_or_error,
)


class StreamingLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_bounded_line_reader_preserves_split_crlf_frames(self):
        class FakeResponse:
            async def aiter_bytes(self, chunk_size):
                self.chunk_size = chunk_size
                for chunk in (b"data: one\r", b"\ndata: two\n", b"tail"):
                    yield chunk

        response = FakeResponse()

        lines = [line async for line in iter_bounded_lines(response, max_line_bytes=16)]

        self.assertEqual(lines, ["data: one", "data: two", "tail"])
        self.assertGreater(response.chunk_size, 0)

    async def test_bounded_line_reader_rejects_oversized_frame(self):
        class FakeResponse:
            async def aiter_bytes(self, chunk_size):
                del chunk_size
                yield b"12345"
                yield b"67890"

        with self.assertRaisesRegex(UpstreamStreamProtocolError, "exceeds"):
            _ = [
                line
                async for line in iter_bounded_lines(
                    FakeResponse(), max_line_bytes=8
                )
            ]

    async def test_prefetched_error_closes_source_iterator(self):
        closed = False

        async def source():
            nonlocal closed
            try:
                yield Response(status_code=502)
            finally:
                closed = True

        response = await build_streaming_response_or_error(source())

        self.assertEqual(response.status_code, 502)
        self.assertTrue(closed)

    async def test_downstream_disconnect_closes_source_iterator(self):
        closed = False

        async def source():
            nonlocal closed
            try:
                yield b"first"
                yield b"second"
            finally:
                closed = True

        response = ManagedStreamingResponse(source())
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/v1/chat/completions",
            "headers": [],
            "asgi": {"spec_version": "2.4"},
        }

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            if message["type"] == "http.response.body" and message.get("body"):
                raise OSError("client disconnected")

        with self.assertRaises(ClientDisconnect):
            await response(scope, receive, send)

        self.assertTrue(closed)


if __name__ == "__main__":
    unittest.main()
