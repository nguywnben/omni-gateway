"""End-to-end reservation lifecycle contracts around request execution."""

from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.api.utils import record_api_call_success
from core.request_context import request_scope, set_api_key_id, set_virtual_key_reservation_id
from core.state_store import QuotaCommitResult
from main import add_security_headers
from starlette.requests import Request
from starlette.responses import StreamingResponse


def _request(path: str = "/v1/chat/completions") -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "path": path,
            "query_string": b"",
            "headers": [(b"host", b"localhost:4283")],
            "client": ("127.0.0.1", 50000),
            "server": ("localhost", 4283),
        }
    )


class QuotaRequestCleanupTests(unittest.IsolatedAsyncioTestCase):
    async def test_provider_exception_releases_active_reservation(self):
        request = _request()

        async def next_handler(current_request):
            current_request.state.virtual_key_reservation_id = "reservation-failed"
            raise RuntimeError("provider failed")

        release = AsyncMock(return_value=True)
        with patch("core.virtual_keys.virtual_key_manager.release_reservation", release):
            with self.assertRaisesRegex(RuntimeError, "provider failed"):
                await add_security_headers(request, next_handler)

        release.assert_awaited_once_with("reservation-failed")

    async def test_request_cancellation_releases_active_reservation(self):
        request = _request()

        async def next_handler(current_request):
            current_request.state.virtual_key_reservation_id = "reservation-cancelled"
            raise asyncio.CancelledError()

        release = AsyncMock(return_value=True)
        with patch("core.virtual_keys.virtual_key_manager.release_reservation", release):
            with self.assertRaises(asyncio.CancelledError):
                await add_security_headers(request, next_handler)

        release.assert_awaited_once_with("reservation-cancelled")

    async def test_stream_completion_releases_only_after_iterator_finishes(self):
        request = _request()

        async def chunks():
            yield b"first"
            yield b"second"

        async def next_handler(current_request):
            current_request.state.virtual_key_reservation_id = "reservation-stream"
            return StreamingResponse(chunks())

        release = AsyncMock(return_value=False)
        with patch("core.virtual_keys.virtual_key_manager.release_reservation", release):
            response = await add_security_headers(request, next_handler)
            self.assertEqual(release.await_count, 0)
            body = b"".join([chunk async for chunk in response.body_iterator])

        self.assertEqual(body, b"firstsecond")
        release.assert_awaited_once_with("reservation-stream")


class QuotaSuccessCommitTests(unittest.IsolatedAsyncioTestCase):
    async def test_success_persists_policy_cost_before_committing_actual_usage(self):
        credential_manager = AsyncMock()
        cost = AsyncMock(return_value=0.125)
        commit = AsyncMock(return_value=QuotaCommitResult(True))
        ledger = Mock(return_value=True)

        with (
            request_scope("request-success"),
            patch("core.api.utils.virtual_key_manager.calculate_actual_cost", cost),
            patch("core.api.utils.virtual_key_manager.commit_reservation", commit),
            patch("core.api.utils.record_call", ledger),
        ):
            set_api_key_id("vk_success")
            set_virtual_key_reservation_id("reservation-success")
            await record_api_call_success(
                credential_manager,
                "credential.json",
                model_name="unpriced-enterprise-model",
                token_usage={"input_tokens": 80, "output_tokens": 20, "total_tokens": 100},
                provider="primary",
            )

        self.assertEqual(ledger.call_args.kwargs["cost_override_usd"], 0.125)
        commit.assert_awaited_once_with(
            "reservation-success",
            actual_tokens=100,
            actual_cost_usd=0.125,
            durable_cost_recorded=True,
        )


if __name__ == "__main__":
    unittest.main()
