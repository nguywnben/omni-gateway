"""Static audit tests for the declarative provider form contract."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROVIDER_HTML = (ROOT / "frontend/fragments/pages/providers.html").read_text(encoding="utf-8")
CONTRACT_SOURCE = (ROOT / "frontend/js/features/provider-settings-shared.js").read_text(
    encoding="utf-8"
)
LOCALE_SOURCE = (ROOT / "frontend/js/core/page-locales.js").read_text(encoding="utf-8")

EXPECTED_FIELDS = {
    "xaiAuthorizationCode",
    "xaiClientId",
    "xaiOauthIssuer",
    "xaiApiKey",
    "xaiApiUrl",
    "xaiUserAgent",
    "googleAiStudioApiKey",
    "googleAiStudioApiUrl",
    "codexApiUrl",
    "codexUsageUrl",
    "codexAuthBase",
    "codexClientId",
    "codexUserAgent",
    "openaiPlatformApiKey",
    "openaiApiUrl",
    "claudeAuthorizationCode",
    "anthropicApiUrlCode",
    "claudeAuthorizeUrl",
    "claudeTokenUrl",
    "claudeClientId",
    "claudeUserAgent",
    "claudePlatformApiKey",
    "anthropicApiUrlPlatform",
    "ollamaBaseUrl",
    "ollamaApiKey",
    "primaryCallbackUrlInput",
    "antigravityOauthClientId",
    "antigravityOauthClientSecret",
    "antigravityApiUrl",
    "antigravityOauthUrl",
    "antigravityGoogleApisUrl",
    "antigravityResourceManagerUrl",
    "antigravityServiceUsageUrl",
    "antigravityUserAgent",
    "antigravityPayloadUserAgent",
    "antigravityStreamToNonstream",
    "antigravitySwitchCredential",
}

SECRET_FIELDS = {
    "xaiAuthorizationCode",
    "xaiApiKey",
    "googleAiStudioApiKey",
    "openaiPlatformApiKey",
    "claudeAuthorizationCode",
    "claudePlatformApiKey",
    "ollamaApiKey",
    "primaryCallbackUrlInput",
    "antigravityOauthClientSecret",
}


class ProviderFormContractTests(unittest.TestCase):
    def test_manifest_covers_every_supported_provider_field(self):
        self.assertIn("const PROVIDER_FORM_CONTRACT", CONTRACT_SOURCE)
        for field_id in EXPECTED_FIELDS:
            with self.subTest(field_id=field_id):
                self.assertIn(f"id: '{field_id}'", CONTRACT_SOURCE)
                self.assertRegex(PROVIDER_HTML, rf'id="{re.escape(field_id)}"')

    def test_every_visible_contract_field_has_an_explicit_label(self):
        for field_id in EXPECTED_FIELDS - {
            "antigravityStreamToNonstream",
            "antigravitySwitchCredential",
        }:
            with self.subTest(field_id=field_id):
                self.assertRegex(PROVIDER_HTML, rf'<label[^>]+for="{re.escape(field_id)}"')

    def test_contract_declares_all_required_enterprise_behaviors(self):
        for property_name in (
            "type",
            "required",
            "minLength",
            "maxLength",
            "autocomplete",
            "secretLifetime",
            "environmentLock",
            "helpKey",
            "advanced",
            "validation",
            "resetBehavior",
        ):
            with self.subTest(property_name=property_name):
                self.assertIn(f"{property_name}:", CONTRACT_SOURCE)

        for helper_name in (
            "applyProviderFormContract",
            "applyProviderEnvironmentLocks",
            "validateProviderFormScope",
            "resetProviderTransientSecrets",
        ):
            with self.subTest(helper_name=helper_name):
                self.assertIn(f"function {helper_name}", CONTRACT_SOURCE)

    def test_secret_fields_are_never_plain_text_and_have_bounded_lifetimes(self):
        for field_id in SECRET_FIELDS:
            with self.subTest(field_id=field_id):
                field_entry = CONTRACT_SOURCE.split(f"id: '{field_id}'", 1)[1].split("}", 1)[0]
                expected_type = "textarea" if field_id == "primaryCallbackUrlInput" else "password"
                self.assertIn(f"type: '{expected_type}'", field_entry)
                self.assertRegex(field_entry, r"maxLength:\s*[1-9][0-9]*")
                self.assertRegex(field_entry, r"secretLifetime:\s*'(submit|edit-session)'")
                self.assertIn("resetBehavior: 'clear'", field_entry)

    def test_runtime_enforces_contract_without_persisting_form_state(self):
        self.assertIn("document.addEventListener('DOMContentLoaded', applyProviderFormContract", CONTRACT_SOURCE)
        self.assertIn("field.dataset.secretLifetime", CONTRACT_SOURCE)
        self.assertIn("field.setCustomValidity", CONTRACT_SOURCE)
        self.assertNotIn("localStorage", CONTRACT_SOURCE)
        self.assertNotIn("sessionStorage", CONTRACT_SOURCE)

    def test_form_guidance_is_curated_for_every_supported_locale(self):
        block = LOCALE_SOURCE.split("const PROVIDER_FORM_VALUES = {", 1)[1].split("\n};", 1)[0]
        locales = {
            left or right
            for left, right in re.findall(
                r"^    (?:'([^']+)'|([a-z]{2})):\s*\[", block, re.MULTILINE
            )
        }
        self.assertEqual(
            locales,
            {
                "en", "zh-CN", "zh-TW", "de", "es", "fr", "id", "it",
                "ja", "ko", "pt", "ru", "th", "tr", "vi",
            },
        )
        self.assertIn("values.length !== PROVIDER_FORM_KEYS.length", LOCALE_SOURCE)


if __name__ == "__main__":
    unittest.main()
