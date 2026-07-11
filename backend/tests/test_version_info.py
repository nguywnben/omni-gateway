"""Tests for build metadata and update discovery."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.version import get_version_info


class FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class VersionInfoTests(unittest.IsolatedAsyncioTestCase):
    async def test_build_metadata_is_used_without_a_version_file(self):
        with patch.dict(
            "os.environ",
            {
                "BUILD_REVISION": "abcdef1234567890",
                "BUILD_VERSION": "0.2.0",
                "BUILD_DATE": "2026-07-11T10:00:00Z",
            },
            clear=False,
        ):
            response = await get_version_info()

        body = json.loads(response.body)
        self.assertTrue(body["success"])
        self.assertEqual(body["version"], "0.2.0")
        self.assertEqual(body["full_hash"], "abcdef1234567890")
        self.assertEqual(body["date"], "2026-07-11T10:00:00Z")

    async def test_update_check_uses_the_public_commit_api(self):
        remote = FakeResponse(
            200,
            {
                "sha": "fedcba9876543210",
                "commit": {
                    "message": "Release hardening\n\nDetails",
                    "committer": {"date": "2026-07-11T12:00:00Z"},
                },
            },
        )
        with (
            patch.dict(
                "os.environ",
                {"BUILD_REVISION": "abcdef1234567890", "BUILD_VERSION": "0.2.0"},
                clear=False,
            ),
            patch("core.httpx_client.get_async", new=AsyncMock(return_value=remote)) as get,
        ):
            response = await get_version_info(check_update=True)

        body = json.loads(response.body)
        self.assertTrue(body["check_update"])
        self.assertTrue(body["has_update"])
        self.assertEqual(body["latest_version"], "fedcba9")
        self.assertEqual(body["latest_message"], "Release hardening")
        requested_url = get.await_args.args[0]
        self.assertEqual(
            requested_url,
            "https://api.github.com/repos/nguywnben/omni-gateway/commits/main",
        )

    async def test_branch_builds_display_the_revision_instead_of_main(self):
        with patch.dict(
            "os.environ",
            {
                "BUILD_REVISION": "abcdef1234567890",
                "BUILD_VERSION": "main",
            },
            clear=False,
        ):
            response = await get_version_info()

        self.assertEqual(json.loads(response.body)["version"], "abcdef1")

    async def test_update_errors_are_sanitized(self):
        with (
            patch.dict(
                "os.environ",
                {"BUILD_REVISION": "abcdef1234567890", "BUILD_VERSION": "0.2.0"},
                clear=False,
            ),
            patch(
                "core.httpx_client.get_async",
                new=AsyncMock(side_effect=RuntimeError("proxy password leaked")),
            ),
        ):
            response = await get_version_info(check_update=True)

        body = json.loads(response.body)
        self.assertFalse(body["check_update"])
        self.assertEqual(body["update_error"], "Unable to check for updates.")
        self.assertNotIn("proxy password leaked", response.body.decode())


if __name__ == "__main__":
    unittest.main()
