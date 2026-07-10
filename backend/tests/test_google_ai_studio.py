"""Tests for Google AI Studio provider contracts."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.google_ai_studio import (
    GoogleAIStudioError,
    build_api_key_headers,
    build_generation_url,
    parse_model_ids,
    validate_api_key,
)
from core.provider_registry import (
    GOOGLE_AI_STUDIO,
    GOOGLE_ANTIGRAVITY,
    api_key_fingerprint,
    credential_supports_model,
    get_credential_provider,
    get_static_credential_identity,
)


class FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class ProviderRegistryTests(unittest.TestCase):
    def test_legacy_oauth_credentials_default_to_antigravity(self):
        credential = {"token": "access", "refresh_token": "refresh"}
        self.assertEqual(get_credential_provider(credential), GOOGLE_ANTIGRAVITY)

    def test_ai_studio_key_has_stable_non_secret_identity(self):
        credential = {
            "provider": GOOGLE_AI_STUDIO,
            "credential_type": "api_key",
            "api_key": "example-google-key-value",
        }
        identity = get_static_credential_identity(credential)
        self.assertEqual(
            identity,
            f"{GOOGLE_AI_STUDIO}:{api_key_fingerprint(credential['api_key'])}",
        )
        self.assertNotIn(credential["api_key"], identity)

    def test_ai_studio_only_accepts_gemini_and_gemma_models(self):
        credential = {
            "provider": GOOGLE_AI_STUDIO,
            "credential_type": "api_key",
            "api_key": "example-google-key-value",
        }
        self.assertTrue(credential_supports_model(credential, "gemini-2.5-flash"))
        self.assertTrue(credential_supports_model(credential, "gemma-3-27b-it"))
        self.assertFalse(credential_supports_model(credential, "claude-sonnet-4-6"))


class GoogleAIStudioTests(unittest.IsolatedAsyncioTestCase):
    def test_generation_url_encodes_untrusted_model_path(self):
        url = build_generation_url(
            "https://generativelanguage.googleapis.com",
            "gemini-2.5-flash/../../unsafe",
            streaming=True,
        )
        self.assertIn("gemini-2.5-flash%2F..%2F..%2Funsafe", url)
        self.assertTrue(url.endswith(":streamGenerateContent?alt=sse"))

    def test_api_key_is_sent_in_google_header(self):
        headers = build_api_key_headers("example-key")
        self.assertEqual(headers["x-goog-api-key"], "example-key")
        self.assertNotIn("Authorization", headers)

    def test_model_parser_only_keeps_generate_content_models(self):
        models = parse_model_ids(
            {
                "models": [
                    {
                        "name": "models/gemini-2.5-flash",
                        "supportedGenerationMethods": ["generateContent"],
                    },
                    {
                        "name": "models/gemini-embedding-001",
                        "supportedGenerationMethods": ["embedContent"],
                    },
                ]
            }
        )
        self.assertEqual(models, ["gemini-2.5-flash"])

    async def test_key_validation_returns_available_models(self):
        response = FakeResponse(
            200,
            {
                "models": [
                    {
                        "name": "models/gemini-2.5-flash",
                        "supportedGenerationMethods": ["generateContent"],
                    }
                ]
            },
        )
        with (
            patch(
                "core.google_ai_studio.get_google_ai_studio_api_url",
                AsyncMock(return_value="https://generativelanguage.googleapis.com"),
            ),
            patch(
                "core.google_ai_studio.get_async",
                AsyncMock(return_value=response),
            ),
        ):
            result = await validate_api_key("example-google-key-value")

        self.assertEqual(result.model_ids, ["gemini-2.5-flash"])
        self.assertEqual(result.model_count, 1)

    async def test_key_validation_sanitizes_rejected_key_error(self):
        response = FakeResponse(403, {"error": {"message": "sensitive upstream"}})
        with (
            patch(
                "core.google_ai_studio.get_google_ai_studio_api_url",
                AsyncMock(return_value="https://generativelanguage.googleapis.com"),
            ),
            patch(
                "core.google_ai_studio.get_async",
                AsyncMock(return_value=response),
            ),
        ):
            with self.assertRaises(GoogleAIStudioError) as context:
                await validate_api_key("example-google-key-value")

        self.assertNotIn("sensitive upstream", str(context.exception))


if __name__ == "__main__":
    unittest.main()
