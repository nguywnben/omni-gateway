"""Tests for provider-specific credential quota responses."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.credentials import get_credential_quota
from core.xai import XaiError


class CredentialQuotaRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_grok_build_oauth_returns_account_billing_quota(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "xai",
            "credential_type": "oauth",
            "access_token": "active-token",
            "refresh_token": "refresh-token",
        }
        billing = {
            "quota_type": "account_billing",
            "monthly": {
                "limit": 4000,
                "used": 1000,
                "remaining": 3000,
                "used_percentage": 25,
                "remaining_percentage": 75,
                "reset_time": "2026-08-01T00:00:00+00:00",
            },
            "weekly": None,
        }

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.fetch_xai_billing_usage",
                AsyncMock(return_value=billing),
            ),
        ):
            response = await get_credential_quota(
                "grok-account.json",
                token="panel-token",
                mode="provider",
            )

        payload = json.loads(response.body)
        self.assertEqual(payload["provider"], "xai")
        self.assertEqual(payload["quota_type"], "account_billing")
        self.assertEqual(payload["monthly"]["remaining"], 3000)
        self.assertNotIn("access_token", payload)

    async def test_xai_console_api_key_reports_quota_as_unsupported(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "xai",
            "credential_type": "api_key",
            "api_key": "xai-secret",
        }

        with patch(
            "core.panel.credentials.get_storage_adapter",
            AsyncMock(return_value=storage),
        ):
            response = await get_credential_quota(
                "xai-console-key.json",
                token="panel-token",
                mode="provider",
            )

        payload = json.loads(response.body)
        self.assertTrue(payload["success"])
        self.assertFalse(payload["supported"])
        self.assertEqual(payload["provider"], "xai")
        self.assertNotIn("api_key", payload)

    async def test_expired_grok_build_token_is_refreshed_once_before_retry(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "xai",
            "credential_type": "oauth",
            "access_token": "expired-token",
            "refresh_token": "refresh-token",
        }
        refreshed = {
            **storage.get_credential.return_value,
            "access_token": "fresh-token",
            "token": "fresh-token",
        }
        billing = AsyncMock(
            side_effect=[
                XaiError("Grok Build rejected this OAuth credential.", 401),
                {
                    "quota_type": "account_billing",
                    "monthly": {
                        "limit": 4000,
                        "used": 1000,
                        "remaining": 3000,
                        "used_percentage": 25,
                        "remaining_percentage": 75,
                        "reset_time": "2026-08-01T00:00:00+00:00",
                    },
                    "weekly": None,
                },
            ]
        )
        refresh = AsyncMock(return_value=refreshed)

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch("core.panel.credentials.fetch_xai_billing_usage", billing),
            patch("core.panel.credentials.refresh_xai_oauth_credential", refresh),
        ):
            response = await get_credential_quota(
                "grok-account.json",
                token="panel-token",
                mode="provider",
            )

        payload = json.loads(response.body)
        self.assertTrue(payload["success"])
        self.assertEqual(
            [call.args[0] for call in billing.await_args_list], ["expired-token", "fresh-token"]
        )
        refresh.assert_awaited_once()
        storage.store_credential.assert_awaited_once_with(
            "grok-account.json",
            refreshed,
            mode="primary",
        )


if __name__ == "__main__":
    unittest.main()
