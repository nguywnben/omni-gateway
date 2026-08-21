"""Security contracts for control-panel session cookies."""

from __future__ import annotations

import json
import os
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

from core.panel.auth import _client_identity, setup_status
from core.utils import (
    PANEL_SESSION_COOKIE,
    clear_panel_session_cookie,
    set_panel_session_cookie,
    verify_panel_token,
)


def build_request(
    *,
    cookie: str = "",
    scheme: str = "http",
    forwarded_for: str = "",
    forwarded_proto: str = "",
    client_host: str = "127.0.0.1",
    method: str = "GET",
    origin: str = "",
    sec_fetch_site: str = "",
) -> Request:
    headers = []
    if cookie:
        headers.append((b"cookie", cookie.encode("ascii")))
    if forwarded_for:
        headers.append((b"x-forwarded-for", forwarded_for.encode("ascii")))
    if forwarded_proto:
        headers.append((b"x-forwarded-proto", forwarded_proto.encode("ascii")))
    if origin:
        headers.append((b"origin", origin.encode("ascii")))
    if sec_fetch_site:
        headers.append((b"sec-fetch-site", sec_fetch_site.encode("ascii")))
    return Request(
        {
            "type": "http",
            "method": method,
            "scheme": scheme,
            "path": "/api/config/get",
            "headers": headers,
            "client": (client_host, 50000),
            "server": ("localhost", 4283),
        }
    )


class PanelSessionCookieTests(unittest.IsolatedAsyncioTestCase):
    async def test_setup_status_reports_a_valid_cookie_session_without_a_401_probe(self):
        request = build_request(cookie=f"{PANEL_SESSION_COOKIE}=cookie-session")

        with (
            patch(
                "core.panel.auth.config.has_password_configured", new=AsyncMock(return_value=True)
            ),
            patch(
                "core.panel.auth.verify_panel_token_value",
                new=AsyncMock(return_value="cookie-session"),
            ) as verifier,
        ):
            response = await setup_status(request)

        payload = json.loads(response.body)
        self.assertTrue(payload["authenticated"])
        verifier.assert_awaited_once_with("cookie-session")

    async def test_setup_status_reports_an_invalid_cookie_as_signed_out(self):
        request = build_request(cookie=f"{PANEL_SESSION_COOKIE}=expired-session")

        with (
            patch(
                "core.panel.auth.config.has_password_configured", new=AsyncMock(return_value=True)
            ),
            patch(
                "core.panel.auth.verify_panel_token_value",
                new=AsyncMock(side_effect=HTTPException(status_code=401)),
            ),
        ):
            response = await setup_status(request)

        self.assertFalse(json.loads(response.body)["authenticated"])

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

    async def test_untrusted_forwarded_proto_does_not_set_secure_cookie(self):
        response = JSONResponse({"success": True})

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TRUST_PROXY_HEADERS", None)
            set_panel_session_cookie(
                response,
                "signed-session",
                build_request(forwarded_proto="https"),
            )

        self.assertNotIn("Secure", response.headers["set-cookie"])

    async def test_trusted_forwarded_proto_sets_secure_cookie(self):
        response = JSONResponse({"success": True})

        with patch.dict(os.environ, {"TRUST_PROXY_HEADERS": "true"}):
            set_panel_session_cookie(
                response,
                "signed-session",
                build_request(forwarded_proto="https"),
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

    async def test_same_origin_cookie_request_is_accepted(self):
        request = build_request(
            cookie=f"{PANEL_SESSION_COOKIE}=cookie-session",
            method="POST",
            origin="http://localhost:4283",
            sec_fetch_site="same-origin",
        )

        with patch(
            "core.utils.verify_panel_token_value",
            new=AsyncMock(return_value="cookie-session"),
        ):
            token = await verify_panel_token(request, credentials=None)

        self.assertEqual(token, "cookie-session")

    async def test_cross_origin_cookie_request_is_rejected(self):
        request = build_request(
            cookie=f"{PANEL_SESSION_COOKIE}=cookie-session",
            method="POST",
            origin="https://attacker.example",
        )

        with self.assertRaises(HTTPException) as context:
            await verify_panel_token(request, credentials=None)

        self.assertEqual(context.exception.status_code, 403)

    async def test_cross_site_fetch_metadata_is_rejected_without_origin(self):
        request = build_request(
            cookie=f"{PANEL_SESSION_COOKIE}=cookie-session",
            method="DELETE",
            sec_fetch_site="cross-site",
        )

        with self.assertRaises(HTTPException) as context:
            await verify_panel_token(request, credentials=None)

        self.assertEqual(context.exception.status_code, 403)

    async def test_bearer_request_does_not_require_browser_origin(self):
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="automation-session",
        )
        request = build_request(
            method="POST",
            origin="https://automation.example",
            sec_fetch_site="cross-site",
        )

        with patch(
            "core.utils.verify_panel_token_value",
            new=AsyncMock(return_value="automation-session"),
        ):
            token = await verify_panel_token(request, credentials=credentials)

        self.assertEqual(token, "automation-session")

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


class ClientIdentityTests(unittest.TestCase):
    def test_forwarded_address_is_ignored_by_default(self):
        request = build_request(
            forwarded_for="198.51.100.20",
            client_host="192.0.2.10",
        )

        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("TRUST_PROXY_HEADERS", None)
            self.assertEqual(_client_identity(request), "192.0.2.10")

    def test_forwarded_address_can_be_enabled_for_a_trusted_proxy(self):
        request = build_request(
            forwarded_for="198.51.100.20, 192.0.2.10",
            client_host="192.0.2.10",
        )

        with patch.dict(os.environ, {"TRUST_PROXY_HEADERS": "true"}):
            self.assertEqual(_client_identity(request), "198.51.100.20")
