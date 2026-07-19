"""Tests for provider-aware credential pool filtering."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.credential_operations import get_creds_status_common


class ProviderPoolFilterTests(unittest.IsolatedAsyncioTestCase):
    async def test_provider_filter_applies_before_pagination_and_stats(self):
        summaries = [
            {
                "filename": "antigravity.json",
                "user_email": "account@example.com",
                "disabled": False,
                "error_codes": [],
                "last_success": 1,
                "model_cooldowns": {},
                "tier": "pro",
                "enable_credit": False,
            },
            {
                "filename": "ai-studio.json",
                "user_email": None,
                "disabled": True,
                "error_codes": [429],
                "last_success": 1,
                "model_cooldowns": {},
                "tier": "pro",
                "enable_credit": False,
            },
        ]
        backend = SimpleNamespace(
            get_credentials_summary=AsyncMock(
                return_value={
                    "items": summaries,
                    "total": 2,
                    "stats": {"total": 2, "normal": 1, "disabled": 1},
                }
            )
        )
        adapter = SimpleNamespace(
            _backend=backend,
            get_backend_info=AsyncMock(return_value={"backend_type": "sqlite"}),
            get_credential=AsyncMock(
                side_effect=lambda filename, mode: {
                    "antigravity.json": {"provider": "google_antigravity"},
                    "ai-studio.json": {
                        "provider": "google_ai_studio",
                        "credential_type": "api_key",
                        "credential_label": "Production key",
                    },
                }[filename]
            ),
        )

        with (
            patch(
                "core.panel.credential_operations.deduplicate_credentials_by_account_email",
                new=AsyncMock(return_value={"deleted_count": 0}),
            ),
            patch(
                "core.panel.credential_operations.get_storage_adapter",
                new=AsyncMock(return_value=adapter),
            ),
        ):
            response = await get_creds_status_common(
                0,
                20,
                "all",
                mode="primary",
                provider_filter="google_ai_studio",
            )

        payload = json.loads(response.body)
        self.assertEqual(payload["total"], 1)
        self.assertEqual(payload["stats"], {"total": 1, "normal": 0, "disabled": 1})
        self.assertEqual(payload["items"][0]["provider"], "google_ai_studio")
        self.assertEqual(payload["items"][0]["credential_label"], "Production key")
        self.assertEqual(payload["items"][0]["credential_type"], "api_key")
        backend.get_credentials_summary.assert_awaited_once()
        call_kwargs = backend.get_credentials_summary.await_args.kwargs
        self.assertEqual(call_kwargs["offset"], 0)
        self.assertIsNone(call_kwargs["limit"])

    async def test_legacy_antigravity_credential_defaults_to_oauth(self):
        summary = {
            "filename": "antigravity.json",
            "user_email": "account@example.com",
            "disabled": False,
            "error_codes": [],
            "last_success": 1,
            "model_cooldowns": {},
            "tier": "pro",
            "enable_credit": False,
        }
        backend = SimpleNamespace(
            get_credentials_summary=AsyncMock(
                return_value={
                    "items": [summary],
                    "total": 1,
                    "stats": {"total": 1, "normal": 1, "disabled": 0},
                }
            )
        )
        adapter = SimpleNamespace(
            _backend=backend,
            get_backend_info=AsyncMock(return_value={"backend_type": "sqlite"}),
            get_credential=AsyncMock(return_value={"provider": "google_antigravity"}),
        )

        with (
            patch(
                "core.panel.credential_operations.deduplicate_credentials_by_account_email",
                new=AsyncMock(return_value={"deleted_count": 0}),
            ),
            patch(
                "core.panel.credential_operations.get_storage_adapter",
                new=AsyncMock(return_value=adapter),
            ),
        ):
            response = await get_creds_status_common(0, 20, "all", mode="primary")

        payload = json.loads(response.body)
        self.assertEqual(payload["items"][0]["provider"], "google_antigravity")
        self.assertEqual(payload["items"][0]["credential_type"], "oauth")


if __name__ == "__main__":
    unittest.main()
