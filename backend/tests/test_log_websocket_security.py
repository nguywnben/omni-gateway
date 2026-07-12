"""Authentication contracts for the runtime-log WebSocket."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.logs import _websocket_origin_matches_host, websocket_logs
from core.utils import PANEL_SESSION_COOKIE


class FakeWebSocket:
    def __init__(
        self,
        *,
        cookie_token: str | None = None,
        query_token: str | None = None,
        origin: str = "http://testserver",
        host: str = "testserver",
    ):
        self.cookies = {PANEL_SESSION_COOKIE: cookie_token} if cookie_token else {}
        self.query_params = {"token": query_token} if query_token else {}
        self.headers = {"origin": origin, "host": host}
        self.close_calls = []

    async def close(self, **kwargs):
        self.close_calls.append(kwargs)


class LogWebSocketSecurityTests(unittest.IsolatedAsyncioTestCase):
    def test_websocket_origin_must_match_the_console_host(self):
        self.assertTrue(_websocket_origin_matches_host(FakeWebSocket()))
        self.assertFalse(
            _websocket_origin_matches_host(
                FakeWebSocket(origin="https://attacker.example", host="testserver")
            )
        )

    async def test_cross_origin_websocket_is_rejected(self):
        websocket = FakeWebSocket(
            cookie_token="session-token",
            origin="https://attacker.example",
        )

        await websocket_logs(websocket)

        self.assertEqual(websocket.close_calls, [{"code": 4403, "reason": "Origin not allowed"}])

    async def test_query_string_tokens_are_rejected(self):
        websocket = FakeWebSocket(query_token="legacy-query-token")

        await websocket_logs(websocket)

        self.assertEqual(len(websocket.close_calls), 1)
        self.assertEqual(websocket.close_calls[0]["code"], 4401)
        self.assertEqual(websocket.close_calls[0]["reason"], "Authentication required")


if __name__ == "__main__":
    unittest.main()
