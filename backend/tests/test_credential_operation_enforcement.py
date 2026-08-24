"""Server-side credential operation capability enforcement tests."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.models import CredentialModelTestRequest, CredFileActionRequest
from core.panel.credential_operations import verify_credential_common
from core.panel.credentials import creds_action, download_cred_file, test_credential


class CredentialOperationEnforcementTests(unittest.IsolatedAsyncioTestCase):
    async def test_unknown_provider_cannot_be_deleted_by_a_crafted_request(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "must-not-leak-provider",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.credential_manager.remove_credential",
                new=AsyncMock(),
            ) as remove,
        ):
            response = await creds_action(
                CredFileActionRequest(filename="unknown.json", action="delete"),
                token="session",
                mode="provider",
            )

        body = json.loads(response.body)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(body["error"]["code"], "credential_operation_unsupported")
        self.assertEqual(body["error"]["operation"], "delete")
        self.assertEqual(body["error"]["variant_id"], "unknown")
        self.assertNotIn("api_key", body)
        self.assertNotIn("must-not-leak-provider", response.body.decode())
        remove.assert_not_awaited()

    async def test_api_key_variant_cannot_enable_antigravity_credit_mode(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        with patch(
            "core.panel.credentials.get_storage_adapter",
            AsyncMock(return_value=storage),
        ):
            response = await creds_action(
                CredFileActionRequest(filename="studio.json", action="enable_credit"),
                token="session",
                mode="provider",
            )

        body = json.loads(response.body)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(body["error"]["operation"], "credit_mode")
        storage.update_credential_state.assert_not_awaited()

    async def test_unknown_provider_credential_cannot_be_exported(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "unregistered-provider",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        with patch(
            "core.panel.credentials.get_storage_adapter",
            AsyncMock(return_value=storage),
        ):
            response = await download_cred_file(
                "unknown.json", token="session", mode="provider"
            )

        body = json.loads(response.body)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(body["error"]["operation"], "export")
        self.assertNotIn("must-not-leak", response.body.decode())

    async def test_unknown_provider_cannot_reach_verification_network_calls(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "unregistered-provider",
            "credential_type": "oauth",
            "access_token": "must-not-leak",
        }

        with (
            patch(
                "core.panel.credential_operations.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credential_operations.validate_api_key",
                new=AsyncMock(),
            ) as validate,
        ):
            response = await verify_credential_common("unknown.json", mode="provider")

        body = json.loads(response.body)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(body["error"]["operation"], "verify")
        self.assertNotIn("must-not-leak", response.body.decode())
        validate.assert_not_awaited()

    async def test_unknown_provider_cannot_reach_model_test_network_calls(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "unregistered-provider",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch("core.httpx_client.post_async", new=AsyncMock()) as post,
        ):
            response = await test_credential(
                "unknown.json",
                CredentialModelTestRequest(model="crafted-model"),
                mode="provider",
                _token="session",
            )

        body = json.loads(response.body)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(body["error"]["operation"], "test")
        self.assertNotIn("must-not-leak", response.body.decode())
        post.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
