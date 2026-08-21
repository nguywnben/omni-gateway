"""Configuration startup and pre-1.0 migration contracts."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import config


class FakeConfigStorage:
    def __init__(self, values: dict, *, fail_set_keys: set[str] | None = None):
        self.values = dict(values)
        self.fail_set_keys = fail_set_keys or set()

    async def get_all_config(self):
        return dict(self.values)

    async def set_config(self, key, value):
        if key in self.fail_set_keys:
            return False
        self.values[key] = value
        return True

    async def delete_config(self, key):
        return self.values.pop(key, None) is not None


class ConfigInitializationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.original_cache = dict(config._config_cache)
        self.original_initialized = config._config_initialized
        config._config_cache = {}
        config._config_initialized = False

    def tearDown(self):
        config._config_cache = self.original_cache
        config._config_initialized = self.original_initialized

    async def test_migrates_stored_beta_keys_and_removes_legacy_secrets(self):
        storage = FakeConfigStorage(
            {
                "password": "legacy-password-hash",
                "api_password": "unused-api-password",
                "client_id": "legacy-client-id",
                "client_secret": "legacy-client-secret",
                "api_url": "https://legacy.example.test",
                "host": "0.0.0.0",
            }
        )

        with (
            patch.dict(os.environ, {"PASSWORD": "", "PANEL_PASSWORD": ""}),
            patch(
                "core.storage_adapter.get_storage_adapter",
                new=AsyncMock(return_value=storage),
            ),
        ):
            await config.init_config()

        self.assertTrue(config._config_initialized)
        self.assertEqual(config._config_cache["panel_password"], "legacy-password-hash")
        self.assertEqual(config._config_cache["antigravity_client_id"], "legacy-client-id")
        self.assertEqual(config._config_cache["antigravity_client_secret"], "legacy-client-secret")
        self.assertEqual(config._config_cache["antigravity_api_url"], "https://legacy.example.test")
        self.assertNotIn("password", storage.values)
        self.assertNotIn("api_password", storage.values)
        self.assertNotIn("client_id", storage.values)
        self.assertNotIn("client_secret", storage.values)
        self.assertNotIn("api_url", storage.values)

    async def test_rejects_removed_password_environment_variable(self):
        with patch.dict(os.environ, {"PASSWORD": "legacy", "PANEL_PASSWORD": ""}):
            with self.assertRaisesRegex(RuntimeError, "Rename it to PANEL_PASSWORD"):
                await config.init_config()

        self.assertFalse(config._config_initialized)

    async def test_failed_migration_does_not_delete_the_legacy_value(self):
        storage = FakeConfigStorage(
            {"client_id": "legacy-client-id"},
            fail_set_keys={"antigravity_client_id"},
        )

        with (
            patch.dict(os.environ, {"PASSWORD": "", "PANEL_PASSWORD": ""}),
            patch(
                "core.storage_adapter.get_storage_adapter",
                new=AsyncMock(return_value=storage),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "Failed to migrate legacy configuration key"):
                await config.init_config()

        self.assertEqual(storage.values["client_id"], "legacy-client-id")
        self.assertNotIn("antigravity_client_id", storage.values)
        self.assertFalse(config._config_initialized)

    async def test_storage_failure_does_not_mark_configuration_initialized(self):
        with (
            patch.dict(os.environ, {"PASSWORD": "", "PANEL_PASSWORD": ""}),
            patch(
                "core.storage_adapter.get_storage_adapter",
                new=AsyncMock(side_effect=RuntimeError("storage unavailable")),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "storage unavailable"):
                await config.init_config()

        self.assertFalse(config._config_initialized)
        self.assertEqual(config._config_cache, {})


if __name__ == "__main__":
    unittest.main()
