"""Credential status contracts for public provider model metadata."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.model_pool import ModelCatalogEntry
from core.models import CredentialModelTestRequest
from core.panel.credential_operations import get_creds_status_common, verify_credential_common
from core.panel.credentials import get_credential_models, test_credential
from fastapi import HTTPException


class FakeCredentialBackend:
    async def get_credentials_summary(self, **_kwargs):
        return {
            "items": [
                {
                    "filename": "google-ai-studio-example.json",
                    "user_email": None,
                    "disabled": False,
                    "error_codes": [],
                    "last_success": None,
                    "model_cooldowns": {},
                    "tier": "pro",
                }
            ],
            "total": 1,
            "stats": {"total": 1, "normal": 1, "disabled": 0},
        }


class FakeCredentialStorage:
    def __init__(self):
        self._backend = FakeCredentialBackend()

    async def get_backend_info(self):
        return {"backend_type": "sqlite"}

    async def get_credential(self, _filename, mode="primary"):
        self.requested_mode = mode
        return {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "must-not-be-exposed",
            "model_ids": [
                "models/gemini-2.5-flash",
                "gemini-2.5-pro",
                "gemini-2.5-flash",
            ],
        }

    async def update_credential_state(self, filename, state, mode="primary"):
        self.updated_state = (filename, state, mode)


class FakeUpstreamResponse:
    status_code = 200
    text = '{"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}'


class FakeAntigravityStorage(FakeCredentialStorage):
    def __init__(self, *, expired: bool = False):
        super().__init__()
        self.expired = expired

    async def get_credential(self, _filename, mode="primary"):
        self.requested_mode = mode
        return {
            "provider": "google_antigravity",
            "credential_type": "oauth",
            "token": "example-access-token",
            "refresh_token": "example-refresh-token",
            "client_id": "example-client-id",
            "client_secret": "example-client-secret",
            "project_id": "example-project",
            "user_email": "developer@example.com",
            "expiry": "2000-01-01T00:00:00+00:00" if self.expired else "2099-01-01T00:00:00+00:00",
        }

    async def store_credential(self, filename, data, mode="primary"):
        self.stored_credential = (filename, dict(data), mode)


class CredentialStatusModelTests(unittest.IsolatedAsyncioTestCase):
    async def test_status_exposes_model_count_without_repeating_the_catalog(self):
        storage = FakeCredentialStorage()

        with (
            patch(
                "core.panel.credential_operations.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credential_operations.deduplicate_credentials_by_account_email",
                AsyncMock(return_value={"deleted_count": 0}),
            ),
        ):
            response = await get_creds_status_common(
                offset=0,
                limit=50,
                status_filter="all",
                mode="primary",
            )

        payload = json.loads(response.body)
        credential = payload["items"][0]
        self.assertEqual(credential["model_count"], 2)
        self.assertNotIn("model_ids", credential)
        self.assertNotIn("api_key", credential)

    async def test_model_endpoint_returns_normalized_catalog_without_secrets(self):
        storage = FakeCredentialStorage()

        with patch(
            "core.panel.credentials.get_storage_adapter",
            AsyncMock(return_value=storage),
        ):
            response = await get_credential_models(
                "google-ai-studio-example.json",
                token="test-session",
                mode="primary",
            )

        payload = json.loads(response.body)
        self.assertEqual(payload["model_count"], 2)
        self.assertEqual(
            payload["model_ids"],
            ["gemini-2.5-flash", "gemini-2.5-pro"],
        )
        self.assertNotIn("api_key", payload)

    async def test_credential_test_uses_the_explicitly_selected_model(self):
        storage = FakeCredentialStorage()

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.get_google_ai_studio_api_url",
                AsyncMock(return_value="https://generativelanguage.googleapis.com"),
            ),
            patch(
                "core.httpx_client.post_async",
                AsyncMock(return_value=FakeUpstreamResponse()),
            ) as post_mock,
        ):
            response = await test_credential(
                "google-ai-studio-example.json",
                request=CredentialModelTestRequest(model="gemini-2.5-pro"),
                mode="primary",
                _token="test-session",
            )

        payload = json.loads(response.body)
        self.assertEqual(payload["model"], "gemini-2.5-pro")
        self.assertEqual(payload["provider"], "google_ai_studio")
        self.assertEqual(payload["credential_type"], "api_key")
        self.assertEqual(payload["message"], "Model test completed successfully.")
        self.assertIn("gemini-2.5-pro:generateContent", post_mock.await_args.kwargs["url"])

    async def test_model_endpoint_uses_provider_catalog_when_models_are_not_stored(self):
        storage = FakeAntigravityStorage()
        catalog = [
            ModelCatalogEntry("claude-sonnet-4-6", ("google_antigravity",)),
            ModelCatalogEntry("gemini-3-flash-preview", ("google_antigravity",)),
            ModelCatalogEntry("gemini-2.5-pro", ("google_ai_studio",)),
        ]

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.model_catalog_service.get_catalog",
                AsyncMock(return_value=catalog),
            ),
        ):
            response = await get_credential_models(
                "google-antigravity-example.json",
                token="test-session",
                mode="primary",
            )

        payload = json.loads(response.body)
        self.assertEqual(
            payload["model_ids"],
            ["claude-sonnet-4-6", "gemini-3-flash-preview"],
        )

    async def test_credential_test_rejects_a_model_outside_its_catalog(self):
        storage = FakeCredentialStorage()

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch("core.httpx_client.post_async", new_callable=AsyncMock) as post_mock,
        ):
            with self.assertRaises(HTTPException) as context:
                await test_credential(
                    "google-ai-studio-example.json",
                    request=CredentialModelTestRequest(model="gemini-3-flash-preview"),
                    mode="primary",
                    _token="test-session",
                )

        self.assertEqual(context.exception.status_code, 400)
        post_mock.assert_not_awaited()

    async def test_antigravity_verification_persists_the_credential_model_catalog(self):
        storage = FakeAntigravityStorage()

        with (
            patch(
                "core.panel.credential_operations.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credential_operations.get_antigravity_api_url",
                AsyncMock(return_value="https://provider.example"),
            ),
            patch(
                "core.panel.credential_operations.get_antigravity_user_agent",
                AsyncMock(return_value="test-agent"),
            ),
            patch(
                "core.panel.credential_operations.fetch_project_id_and_tier",
                AsyncMock(return_value=("example-project", "pro", None)),
            ),
            patch(
                "core.panel.credential_operations.fetch_antigravity_model_ids",
                AsyncMock(return_value=["claude-sonnet-4-6", "gemini-3-flash-preview"]),
            ),
        ):
            response = await verify_credential_common(
                "google-antigravity-example.json", mode="primary"
            )

        payload = json.loads(response.body)
        stored = storage.stored_credential[1]
        self.assertEqual(payload["model_count"], 2)
        self.assertEqual(
            stored["model_ids"],
            ["claude-sonnet-4-6", "gemini-3-flash-preview"],
        )
        self.assertEqual(stored["user_email"], "developer@example.com")

    async def test_antigravity_token_refresh_preserves_credential_metadata(self):
        storage = FakeAntigravityStorage(expired=True)

        with (
            patch(
                "core.panel.credential_operations.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credential_operations.Credentials.refresh_if_needed",
                AsyncMock(return_value=True),
            ),
            patch(
                "core.panel.credential_operations.get_antigravity_api_url",
                AsyncMock(return_value="https://provider.example"),
            ),
            patch(
                "core.panel.credential_operations.get_antigravity_user_agent",
                AsyncMock(return_value="test-agent"),
            ),
            patch(
                "core.panel.credential_operations.fetch_project_id_and_tier",
                AsyncMock(return_value=("example-project", "pro", None)),
            ),
            patch(
                "core.panel.credential_operations.fetch_antigravity_model_ids",
                AsyncMock(return_value=["gemini-3-flash-preview"]),
            ),
        ):
            await verify_credential_common("google-antigravity-example.json", mode="primary")

        stored = storage.stored_credential[1]
        self.assertEqual(stored["provider"], "google_antigravity")
        self.assertEqual(stored["credential_type"], "oauth")
        self.assertEqual(stored["user_email"], "developer@example.com")


if __name__ == "__main__":
    unittest.main()
