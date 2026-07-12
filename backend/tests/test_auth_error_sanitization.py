"""Authentication failures must not expose internal exception details."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.models import LoginRequest, SetupRequest
from core.panel.auth import complete_setup, login, setup_status
from fastapi import HTTPException
from starlette.requests import Request


def _request(path: str) -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "path": path,
            "headers": [(b"host", b"localhost:4283")],
            "client": ("127.0.0.1", 50000),
            "server": ("localhost", 4283),
        }
    )


class AuthErrorSanitizationTests(unittest.IsolatedAsyncioTestCase):
    async def _assert_sanitized(self, operation, expected_detail: str) -> None:
        with patch(
            "core.panel.auth.config.has_password_configured",
            new=AsyncMock(side_effect=RuntimeError("postgresql://user:secret@database")),
        ):
            with self.assertRaises(HTTPException) as context:
                await operation()

        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, expected_detail)
        self.assertNotIn("secret", context.exception.detail)

    async def test_login_error_is_sanitized(self):
        await self._assert_sanitized(
            lambda: login(LoginRequest(password="not-used"), _request("/api/auth/login")),
            "Unable to sign in because of an internal service error.",
        )

    async def test_setup_status_error_is_sanitized(self):
        await self._assert_sanitized(
            lambda: setup_status(_request("/api/auth/setup/status")),
            "Unable to determine the initial setup status.",
        )

    async def test_setup_error_is_sanitized(self):
        await self._assert_sanitized(
            lambda: complete_setup(
                SetupRequest(password="password", confirm_password="password"),
                _request("/api/auth/setup"),
            ),
            "Unable to complete initial setup because of an internal service error.",
        )


if __name__ == "__main__":
    unittest.main()
