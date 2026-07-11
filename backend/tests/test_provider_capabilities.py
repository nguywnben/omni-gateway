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
    get_provider_capabilities,
    list_provider_capabilities,
)


class ProviderCapabilityTests(unittest.TestCase):
    def test_catalog_has_stable_unique_provider_ids(self):
        providers = list_provider_capabilities()

        self.assertEqual(
            {provider["provider_id"] for provider in providers},
            {GOOGLE_ANTIGRAVITY, GOOGLE_AI_STUDIO},
        )

    def test_ai_studio_only_accepts_declared_model_families(self):
        capabilities = get_provider_capabilities(GOOGLE_AI_STUDIO)

        self.assertTrue(capabilities.supports_model("models/gemini-2.5-flash"))
        self.assertTrue(capabilities.supports_model("gemma-3-27b-it"))
        self.assertFalse(capabilities.supports_model("claude-sonnet-4-6"))

    def test_antigravity_declares_oauth_credentials(self):
        capabilities = get_provider_capabilities(GOOGLE_ANTIGRAVITY)

        self.assertEqual(capabilities.credential_types, ("oauth",))


if __name__ == "__main__":
    unittest.main()
