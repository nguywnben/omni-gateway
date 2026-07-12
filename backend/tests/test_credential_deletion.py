"""Credential deletion lifecycle tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.credential_manager import CredentialManager


class CredentialDeletionTests(unittest.IsolatedAsyncioTestCase):
    async def test_successful_delete_anonymizes_usage_history(self):
        manager = CredentialManager()
        manager._initialized = True
        manager._storage_adapter = AsyncMock()
        manager._storage_adapter.get_credential.return_value = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "private-key",
        }
        manager._storage_adapter.delete_credential.return_value = True

        with patch("core.credential_manager.retire_credential_usage") as retire_usage:
            deleted = await manager.remove_credential(
                "google-ai-studio-fingerprint.json",
                mode="primary",
            )

        self.assertTrue(deleted)
        retire_usage.assert_called_once_with(
            "google-ai-studio-fingerprint.json",
            "google_ai_studio",
        )

    async def test_failed_delete_keeps_usage_history_unchanged(self):
        manager = CredentialManager()
        manager._initialized = True
        manager._storage_adapter = AsyncMock()
        manager._storage_adapter.get_credential.return_value = {
            "provider": "google_antigravity",
            "refresh_token": "private-refresh-token",
        }
        manager._storage_adapter.delete_credential.return_value = False

        with patch("core.credential_manager.retire_credential_usage") as retire_usage:
            deleted = await manager.remove_credential(
                "google-antigravity-fingerprint.json",
                mode="primary",
            )

        self.assertFalse(deleted)
        retire_usage.assert_not_called()


if __name__ == "__main__":
    unittest.main()
