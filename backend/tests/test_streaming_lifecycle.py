"""Deterministic lifecycle tests for public streaming responses."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
from fastapi import Response
from starlette.requests import ClientDisconnect

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.api.primary import ProviderRequestContext, stream_request
from core.httpx_client import UpstreamStreamProtocolError, iter_bounded_lines
from core.router.stream_passthrough import (
    ManagedStreamingResponse,
    build_streaming_response_or_error,
)


async def _collect_primary_stream(fake_stream_post_async, *, max_retries=3):
    credential = {
        "provider": "google_ai_studio",
        "credential_type": "api_key",
        "api_key": "example-key",
    }
    context = ProviderRequestContext(
        provider_id="google_ai_studio",
        target_url="https://upstream.invalid",
        headers={},
        payload={"model": "gemini-test"},
        request_metrics={},
    )
    record_error = AsyncMock()
    record_success = AsyncMock()
    with (
        patch(
            "core.api.primary.credential_manager.get_valid_model_credential",
            AsyncMock(return_value=("gemini-test", "credential.json", credential)),
        ),
        patch(
            "core.api.primary.prepare_provider_request",
            AsyncMock(return_value=context),
        ),
        patch(
            "core.api.primary.get_retry_config",
            AsyncMock(
                return_value={
                    "retry_enabled": max_retries > 0,
                    "max_retries": max_retries,
                    "retry_interval": 0,
                }
            ),
        ),
        patch(
            "core.api.primary.get_antigravity_switch_credential_enabled",
            AsyncMock(return_value=False),
        ),
        patch(
            "core.api.primary.get_auto_disable_error_codes",
            AsyncMock(return_value=[]),
        ),
        patch(
            "core.api.primary.get_upstream_timeout_seconds",
            AsyncMock(return_value=30),
        ),
        patch("core.api.primary.stream_post_async", side_effect=fake_stream_post_async),
        patch("core.api.primary.record_api_call_error", record_error),
        patch("core.api.primary.record_api_call_success", record_success),
    ):
        chunks = [chunk async for chunk in stream_request(body={"model": "gemini-test"})]
    return chunks, record_error, record_success


class StreamingLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def test_primary_stream_does_not_retry_after_model_output(self):
        stream_calls = 0

        def fake_stream_post_async(**_kwargs):
            nonlocal stream_calls
            stream_calls += 1

            async def chunks():
                yield 'data: {"candidates":[{"content":{"parts":[{"text":"partial"}]}}]}'
                raise httpx.ReadTimeout("upstream stalled")

            return chunks()

        chunks, record_error, record_success = await _collect_primary_stream(
            fake_stream_post_async
        )

        self.assertEqual(stream_calls, 1)
        self.assertEqual(chunks[0][:5], "data:")
        self.assertIsInstance(chunks[-1], Response)
        self.assertEqual(chunks[-1].status_code, 504)
        record_error.assert_awaited_once()
        record_success.assert_not_awaited()

    async def test_primary_stream_rejects_eof_without_terminal_event(self):
        def fake_stream_post_async(**_kwargs):
            async def chunks():
                yield 'data: {"candidates":[{"content":{"parts":[{"text":"partial"}]}}]}'

            return chunks()

        chunks, record_error, record_success = await _collect_primary_stream(
            fake_stream_post_async, max_retries=0
        )

        self.assertIsInstance(chunks[-1], Response)
        self.assertEqual(chunks[-1].status_code, 502)
        record_error.assert_awaited_once()
        record_success.assert_not_awaited()

    async def test_primary_stream_heartbeat_does_not_suppress_safe_retry(self):
        stream_calls = 0

        def fake_stream_post_async(**_kwargs):
            nonlocal stream_calls
            stream_calls += 1

            async def chunks():
                if stream_calls == 1:
                    yield ": keep-alive"
                    raise httpx.ReadTimeout("upstream stalled")
                yield 'data: {"candidates":[{"finishReason":"STOP"}]}'

            return chunks()

        chunks, record_error, record_success = await _collect_primary_stream(
            fake_stream_post_async
        )

        self.assertEqual(stream_calls, 2)
        self.assertEqual(chunks, [": keep-alive", 'data: {"candidates":[{"finishReason":"STOP"}]}'])
        record_error.assert_awaited_once()
        record_success.assert_awaited_once()

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
