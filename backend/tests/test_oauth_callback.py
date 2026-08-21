"""Tests for provider-aware OAuth callback dispatch."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch
from urllib.parse import urlencode

from starlette.requests import Request

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel import root


def _callback_request(**query: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": "http",
            "path": "/callback",
            "raw_path": b"/callback",
            "query_string": urlencode(query).encode("ascii"),
            "headers": [],
            "client": ("127.0.0.1", 50000),
            "server": ("localhost", 4283),
        }
    )


class OAuthCallbackTests(unittest.IsolatedAsyncioTestCase):
    async def test_claude_callback_is_completed_by_the_anthropic_handler(self):
        complete = AsyncMock(
            return_value={
                "action": "created",
                "filename": "claude-code-account.json",
                "label": "user@example.com",
                "model_count": 3,
            }
        )
        with (
            patch.object(root, "is_claude_oauth_state", return_value=True, create=True),
            patch.object(root, "complete_claude_oauth", complete, create=True),
            patch.object(root, "accept_oauth_callback") as accept_google,
        ):
            response = await root.serve_oauth_callback(
                _callback_request(code="claude-code", state="claude-state")
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Claude Code Authentication Successful", response.body.decode("utf-8"))
        complete.assert_awaited_once_with("claude-code", "claude-state")
        accept_google.assert_not_called()

    async def test_google_callback_still_uses_the_existing_handler(self):
        with (
            patch.object(root, "is_claude_oauth_state", return_value=False, create=True),
            patch.object(
                root,
                "accept_oauth_callback",
                return_value=(True, "OAuth authentication successful."),
            ) as accept_google,
        ):
            response = await root.serve_oauth_callback(
                _callback_request(code="google-code", state="google-state")
            )

        self.assertEqual(response.status_code, 200)
        accept_google.assert_called_once_with("google-code", "google-state")


if __name__ == "__main__":
    unittest.main()
