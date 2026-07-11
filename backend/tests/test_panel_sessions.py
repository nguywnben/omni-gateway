"""Security contracts for control-panel session cookies."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request
from starlette.responses import JSONResponse

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.utils import (
    PANEL_SESSION_COOKIE,
    clear_panel_session_cookie,
    set_panel_session_cookie,
    verify_panel_token,
)


def build_request(*, cookie: str = "", scheme: str = "http") -> Request:
    headers = []
    if cookie:
        headers.append((b"cookie", cookie.encode("ascii")))
    return Request(
        {
            "type": "http",
            "method": "GET",
            "scheme": scheme,
            "path": "/api/config/get",
            "headers": headers,
            "client": ("127.0.0.1", 50000),
            "server": ("localhost", 4283),
        }
    )


class PanelSessionCookieTests(unittest.IsolatedAsyncioTestCase):
    async def test_cookie_is_http_only_same_site_and_path_scoped(self):
        response = JSONResponse({"success": True})

        set_panel_session_cookie(response, "signed-session", build_request())

        cookie = response.headers["set-cookie"]
        self.assertIn(f"{PANEL_SESSION_COOKIE}=signed-session", cookie)
        self.assertIn("HttpOnly", cookie)
        self.assertIn("SameSite=lax", cookie)
        self.assertIn("Path=/", cookie)

    async def test_https_requests_receive_secure_cookie(self):
        response = JSONResponse({"success": True})

        set_panel_session_cookie(
            response,
            "signed-session",
            build_request(scheme="https"),
        )

        self.assertIn("Secure", response.headers["set-cookie"])

    async def test_cookie_token_is_accepted_without_authorization_header(self):
        request = build_request(cookie=f"{PANEL_SESSION_COOKIE}=cookie-session")

        with patch(
            "core.utils.verify_panel_token_value",
            new=AsyncMock(return_value="cookie-session"),
        ) as verifier:
            token = await verify_panel_token(request, credentials=None)

        self.assertEqual(token, "cookie-session")
        verifier.assert_awaited_once_with("cookie-session")

    async def test_bearer_token_remains_supported_for_non_browser_clients(self):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="legacy-session",
        )

        with patch(
            "core.utils.verify_panel_token_value",
            new=AsyncMock(return_value="legacy-session"),
        ):
            token = await verify_panel_token(build_request(), credentials=credentials)

        self.assertEqual(token, "legacy-session")

    async def test_missing_session_is_rejected(self):
        with self.assertRaises(HTTPException) as context:
            await verify_panel_token(build_request(), credentials=None)

        self.assertEqual(context.exception.status_code, 401)

    async def test_logout_cookie_expires_immediately(self):
        response = JSONResponse({"success": True})

        clear_panel_session_cookie(response)

        cookie = response.headers["set-cookie"]
        self.assertIn(f"{PANEL_SESSION_COOKIE}=", cookie)
        self.assertIn("Max-Age=0", cookie)
