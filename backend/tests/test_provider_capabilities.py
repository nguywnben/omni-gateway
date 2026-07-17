"""Provider capability contract tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.provider_registry import (
    GOOGLE_AI_STUDIO,
    GOOGLE_ANTIGRAVITY,
    GROK,
    MODEL_SUPPORT_DECLARED,
    MODEL_SUPPORT_INFERRED,
    MODEL_SUPPORT_UNSUPPORTED,
    XAI,
    XAI_CONSOLE,
    credential_model_support_level,
    credential_supports_model,
    get_credential_provider_display_name,
    get_credential_provider_variant,
    get_declared_credential_models,
    get_provider_capabilities,
    list_provider_capabilities,
)


class ProviderCapabilityTests(unittest.TestCase):
    def test_catalog_has_stable_unique_provider_ids(self):
        providers = list_provider_capabilities()

        self.assertEqual(
            {provider["provider_id"] for provider in providers},
            {GOOGLE_ANTIGRAVITY, GOOGLE_AI_STUDIO, XAI},
        )

    def test_ai_studio_only_accepts_declared_model_families(self):
        capabilities = get_provider_capabilities(GOOGLE_AI_STUDIO)

        self.assertTrue(capabilities.supports_model("models/gemini-2.5-flash"))
        self.assertTrue(capabilities.supports_model("gemma-3-27b-it"))
        self.assertFalse(capabilities.supports_model("claude-sonnet-4-6"))

    def test_antigravity_declares_oauth_credentials(self):
        capabilities = get_provider_capabilities(GOOGLE_ANTIGRAVITY)

        self.assertEqual(capabilities.credential_types, ("oauth",))

    def test_xai_declares_dual_auth_and_grok_models(self):
        capabilities = get_provider_capabilities(XAI)

        self.assertEqual(capabilities.display_name, "Grok")
        self.assertEqual(capabilities.credential_types, ("oauth", "api_key"))
        self.assertTrue(capabilities.supports_model("grok-4"))
        self.assertFalse(capabilities.supports_model("gemini-2.5-flash"))

    def test_xai_credentials_use_precise_user_facing_provider_names(self):
        oauth_credential = {"provider": XAI, "credential_type": "oauth"}
        api_key_credential = {"provider": XAI, "credential_type": "api_key"}

        self.assertEqual(get_credential_provider_variant(oauth_credential), GROK)
        self.assertEqual(get_credential_provider_display_name(oauth_credential), "Grok")
        self.assertEqual(get_credential_provider_variant(api_key_credential), XAI_CONSOLE)
        self.assertEqual(
            get_credential_provider_display_name(api_key_credential),
            "xAI Console",
        )
        self.assertEqual(
            get_credential_provider_display_name({"provider": XAI, "api_key": "legacy-api-key"}),
            "xAI Console",
        )

    def test_credential_model_catalog_restricts_individual_api_keys(self):
        credential = {
            "provider": GOOGLE_AI_STUDIO,
            "credential_type": "api_key",
            "api_key": "example-key",
            "model_ids": ["gemini-2.5-flash"],
        }

        self.assertTrue(credential_supports_model(credential, "gemini-2.5-flash"))
        self.assertFalse(credential_supports_model(credential, "gemini-2.5-pro"))

    def test_model_support_level_distinguishes_declared_inferred_and_unsupported(self):
        declared = {
            "provider": GOOGLE_AI_STUDIO,
            "credential_type": "api_key",
            "api_key": "example-key",
            "model_ids": ["gemini-2.5-flash"],
        }
        inferred = {
            "provider": GOOGLE_ANTIGRAVITY,
            "token": "example-token",
        }

        self.assertEqual(
            credential_model_support_level(declared, "gemini-2.5-flash"),
            MODEL_SUPPORT_DECLARED,
        )
        self.assertEqual(
            credential_model_support_level(inferred, "gemini-2.5-flash"),
            MODEL_SUPPORT_INFERRED,
        )
        self.assertEqual(
            credential_model_support_level(declared, "grok-4"),
            MODEL_SUPPORT_UNSUPPORTED,
        )

    def test_credential_model_catalog_preserves_non_google_namespaces(self):
        credential = {
            "provider": "google_ai_studio",
            "api_key": "test-key",
            "model_ids": ["models/gemini-2.5-flash"],
        }

        self.assertFalse(credential_supports_model(credential, "other/gemini-2.5-flash"))

    def test_declared_model_catalog_is_normalized_and_deduplicated(self):
        credential = {
            "model_ids": [
                " models/gemini-2.5-flash ",
                "gemini-2.5-flash",
                "gemini-2.5-pro",
                "",
                None,
            ]
        }

        self.assertEqual(
            get_declared_credential_models(credential),
            ["gemini-2.5-flash", "gemini-2.5-pro"],
        )


if __name__ == "__main__":
    unittest.main()
