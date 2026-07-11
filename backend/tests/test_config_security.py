"""Security contracts for control-panel configuration."""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
from starlette.requests import Request

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.models import AccessCredentialsUpdateRequest
import config
from core.passwords import is_password_hash, verify_password_value
from core.panel.config_routes import (
    ACCESS_SECRET_KEYS,
    ALLOWED_CONFIG_KEYS,
    PROVIDER_SPECIFIC_CONFIG_KEYS,
    _classify_config_updates,
    _redact_access_secrets,
    update_access_credentials,
)


class FakeStorageAdapter:
    def __init__(self):
        self.values = {}

    async def set_config(self, key, value):
        self.values[key] = value


def build_http_request() -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "scheme": "http",
            "path": "/api/config/access",
            "headers": [],
            "client": ("127.0.0.1", 50000),
            "server": ("localhost", 4283),
        }
    )


class ConfigResponseSecurityTests(unittest.TestCase):
    def test_global_config_contract_excludes_access_and_provider_secrets(self):
        self.assertFalse(ALLOWED_CONFIG_KEYS & ACCESS_SECRET_KEYS)
        self.assertFalse(ALLOWED_CONFIG_KEYS & PROVIDER_SPECIFIC_CONFIG_KEYS)

    def test_redacts_password_values_and_reports_configuration_state(self):
        config = {
            "host": "0.0.0.0",
            "api_password": "api-secret-value",
            "panel_password": "panel-secret-value",
            "password": "legacy-secret-value",
        }

        public_config = _redact_access_secrets(config)

        self.assertEqual(public_config["host"], "0.0.0.0")
        self.assertTrue(public_config["panel_password_configured"])
        self.assertNotIn("api_password", public_config)
        self.assertNotIn("panel_password", public_config)
        self.assertNotIn("password", public_config)
        self.assertNotIn("api-secret-value", json.dumps(public_config))
        self.assertNotIn("panel-secret-value", json.dumps(public_config))

    def test_classifies_listener_and_storage_changes_as_restart_required(self):
        classification = _classify_config_updates(
            {"host", "port", "credentials_dir", "proxy", "retry_429_enabled"}
        )

        self.assertEqual(
            classification["restart_required"],
            ["credentials_dir", "host", "port"],
        )
        self.assertEqual(
            classification["hot_updated"],
            ["proxy", "retry_429_enabled"],
        )


class RuntimePolicyConfigTests(unittest.IsolatedAsyncioTestCase):
    async def test_upstream_timeout_is_bounded(self):
        with patch.dict(os.environ, {"UPSTREAM_TIMEOUT_SECONDS": "1"}):
            self.assertEqual(await config.get_upstream_timeout_seconds(), 5.0)

        with patch.dict(os.environ, {"UPSTREAM_TIMEOUT_SECONDS": "120"}):
            self.assertEqual(await config.get_upstream_timeout_seconds(), 120.0)

    async def test_invalid_routing_strategy_falls_back_to_balanced(self):
        with patch.dict(os.environ, {"ROUTING_STRATEGY": "unknown"}):
            policy = await config.get_routing_policy()

        self.assertEqual(policy["strategy"], "balanced")

    async def test_log_retention_settings_are_bounded(self):
        with patch.dict(
            os.environ,
            {
                "LOG_LEVEL": "verbose",
                "LOG_MAX_MB": "0",
                "LOG_BACKUP_COUNT": "99",
            },
        ):
            log_config = await config.get_log_config()

        self.assertEqual(log_config["level"], "info")
        self.assertEqual(log_config["max_mb"], 1)
        self.assertEqual(log_config["backup_count"], 20)


class AccessCredentialUpdateTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_an_incorrect_current_password(self):
        request = AccessCredentialsUpdateRequest(
            current_password="incorrect-password",
            panel_password="new-panel-password",
            panel_password_confirm="new-panel-password",
        )

        with patch(
            "core.panel.config_routes.verify_password",
            new=AsyncMock(return_value=False),
        ):
            with self.assertRaises(HTTPException) as context:
                await update_access_credentials(
                    request,
                    build_http_request(),
                    token="session",
                )

        self.assertEqual(context.exception.status_code, 401)

    async def test_updates_passwords_without_returning_them(self):
        storage = FakeStorageAdapter()
        request = AccessCredentialsUpdateRequest(
            current_password="current-password",
            panel_password="new-panel-password",
            panel_password_confirm="new-panel-password",
        )

        with (
            patch(
                "core.panel.config_routes.verify_password",
                new=AsyncMock(return_value=True),
            ),
            patch(
                "core.panel.config_routes.get_storage_adapter",
                new=AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.config_routes.config.reload_config",
                new=AsyncMock(),
            ),
            patch(
                "core.panel.config_routes.create_panel_session_token",
                new=AsyncMock(return_value="replacement-session"),
            ),
        ):
            response = await update_access_credentials(
                request,
                build_http_request(),
                token="session",
            )

        body = json.loads(response.body)
        self.assertTrue(is_password_hash(storage.values["panel_password"]))
        self.assertTrue(
            verify_password_value(
                "new-panel-password", storage.values["panel_password"]
            )
        )
        self.assertEqual(body["updated"], ["panel_password"])
        self.assertNotIn("new-panel-password", response.body.decode())
        self.assertIn("panel_session=replacement-session", response.headers["set-cookie"])
        self.assertIn("HttpOnly", response.headers["set-cookie"])

    async def test_rejects_confirmation_mismatch(self):
        request = AccessCredentialsUpdateRequest(
            current_password="current-password",
            panel_password="new-panel-password",
            panel_password_confirm="different-password",
        )

        with patch(
            "core.panel.config_routes.verify_password",
            new=AsyncMock(return_value=True),
        ):
            with self.assertRaises(HTTPException) as context:
                await update_access_credentials(
                    request,
                    build_http_request(),
                    token="session",
                )

        self.assertEqual(context.exception.status_code, 400)
