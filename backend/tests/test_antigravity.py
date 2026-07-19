"""Google Antigravity provider metadata contracts."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.antigravity import (
    AntigravityError,
    fetch_antigravity_model_ids,
    parse_antigravity_model_ids,
)


class FakeResponse:
    status_code = 200
    text = ""

    def json(self):
        return {
            "models": {
                "gemini-3-flash-preview": {},
                "claude-sonnet-4-6": {},
                "claude-opus-4-6-thinking": {},
            }
        }


class InvalidJsonResponse(FakeResponse):
    def json(self):
        raise ValueError("invalid json")


class AntigravityModelTests(unittest.IsolatedAsyncioTestCase):
    def test_model_parser_normalizes_catalog_and_supported_aliases(self):
        self.assertEqual(
            parse_antigravity_model_ids(FakeResponse().json()),
            [
                "claude-opus-4-6",
                "claude-opus-4-6-thinking",
                "claude-sonnet-4-6",
                "claude-sonnet-4-6-thinking",
                "gemini-3-flash-preview",
            ],
        )

    async def test_model_discovery_uses_the_configured_provider_endpoint(self):
        with patch(
            "core.antigravity.post_async",
            AsyncMock(return_value=FakeResponse()),
        ) as post_mock:
            model_ids = await fetch_antigravity_model_ids(
                "access-token",
                api_base_url="https://provider.example/",
                user_agent="test-agent",
            )

        self.assertIn("gemini-3-flash-preview", model_ids)
        self.assertEqual(
            post_mock.await_args.kwargs["url"],
            "https://provider.example/v1internal:fetchAvailableModels",
        )
        self.assertEqual(
            post_mock.await_args.kwargs["headers"]["Authorization"],
            "Bearer access-token",
        )

    async def test_model_discovery_sanitizes_invalid_upstream_json(self):
        with patch(
            "core.antigravity.post_async",
            AsyncMock(return_value=InvalidJsonResponse()),
        ):
            with self.assertRaisesRegex(
                AntigravityError,
                "Google Antigravity returned an invalid model response",
            ) as context:
                await fetch_antigravity_model_ids("access-token")

        self.assertEqual(context.exception.status_code, 502)

    async def test_model_discovery_sanitizes_network_failures(self):
        with patch(
            "core.antigravity.post_async",
            AsyncMock(side_effect=OSError("network unavailable")),
        ):
            with self.assertRaisesRegex(
                AntigravityError,
                "Unable to reach Google Antigravity",
            ) as context:
                await fetch_antigravity_model_ids("access-token")

        self.assertEqual(context.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
