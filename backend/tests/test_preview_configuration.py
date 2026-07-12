"""Regression tests for Preview channel configuration."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.credentials import configure_preview_channel


class PreviewConfigurationTests(unittest.IsolatedAsyncioTestCase):
    async def test_creates_one_setting_and_one_binding(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "access_token": "access-token",
            "project_id": "project-id",
        }
        credentials = MagicMock()
        credentials.refresh_if_needed = AsyncMock(return_value=False)
        post = AsyncMock(
            side_effect=[
                SimpleNamespace(status_code=201, text=""),
                SimpleNamespace(status_code=201, text=""),
            ]
        )

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                new=AsyncMock(return_value=storage),
            ),
            patch("core.panel.credentials.Credentials.from_dict", return_value=credentials),
            patch("core.httpx_client.post_async", new=post),
        ):
            response = await configure_preview_channel(
                "credential.json",
                token="session",
                mode="code_assist",
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(post.await_count, 2)
        self.assertIn("releaseChannelSettings", post.await_args_list[0].kwargs["url"])
        self.assertIn("settingBindings", post.await_args_list[1].kwargs["url"])


if __name__ == "__main__":
    unittest.main()
