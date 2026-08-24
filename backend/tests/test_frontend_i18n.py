"""Static coverage checks for the management console translation contract."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"
LOCALE_SOURCE = (FRONTEND / "js" / "core" / "locales.js").read_text(encoding="utf-8")
PAGE_LOCALE_SOURCE = (FRONTEND / "js" / "core" / "page-locales.js").read_text(encoding="utf-8")
I18N_SOURCE = (FRONTEND / "js" / "core" / "i18n.js").read_text(encoding="utf-8")


def _extract_array(source: str, variable: str) -> str:
    match = re.search(rf"const\s+{re.escape(variable)}\s*=\s*\[(.*?)\];", source, re.DOTALL)
    return match.group(1) if match else ""


def _frontend_sources() -> list[Path]:
    return sorted((FRONTEND / "fragments").rglob("*.html")) + sorted(
        (FRONTEND / "js").rglob("*.js")
    )


class FrontendLocaleContractTests(unittest.TestCase):
    def test_quality_policy_catalog_is_complete_for_every_locale(self):
        block = PAGE_LOCALE_SOURCE.split(
            "const QUALITY_POLICY_EXTENDED_MESSAGES = {", 1
        )[1].split("\n};", 1)[0]
        locale_matches = list(
            re.finditer(
                r"^    (?:'([^']+)'|([a-z]{2})): \{",
                block,
                re.MULTILINE,
            )
        )
        catalogs = {}
        for index, match in enumerate(locale_matches):
            locale = match.group(1) or match.group(2)
            end = locale_matches[index + 1].start() if index + 1 < len(locale_matches) else len(block)
            catalogs[locale] = set(re.findall(r"'((?:quality)\.[a-z0-9_]+)'\s*:", block[match.start():end]))

        expected_locales = {
            "en", "zh-CN", "zh-TW", "de", "es", "fr", "id", "it",
            "ja", "ko", "pt", "ru", "th", "tr", "vi",
        }
        self.assertEqual(set(catalogs), expected_locales)
        for locale in expected_locales:
            with self.subTest(locale=locale):
                self.assertEqual(catalogs[locale], catalogs["en"])

    def test_language_control_only_appears_in_settings(self):
        locations = []
        for path in _frontend_sources():
            source = path.read_text(encoding="utf-8")
            if 'class="lang-switcher"' in source:
                locations.append(path.relative_to(ROOT).as_posix())

        self.assertEqual(locations, ["frontend/fragments/pages/settings.html"])

    def test_every_referenced_translation_key_has_an_english_source(self):
        references: set[str] = set()
        patterns = (
            re.compile(r"\bt\(\s*['\"]([^'\"]+)['\"]"),
            re.compile(r"data-i18n(?:-(?:title|alt|placeholder|aria-label))?=['\"]([^'\"]+)['\"]"),
        )
        for path in _frontend_sources():
            source = path.read_text(encoding="utf-8")
            for pattern in patterns:
                references.update(pattern.findall(source))

        combined_catalog = LOCALE_SOURCE + PAGE_LOCALE_SOURCE + I18N_SOURCE
        generated_keys: set[str] = set()
        for variable in (
            "SETTINGS_PAGE_KEYS",
            "PROVIDER_CATALOG_KEYS",
            "CONSOLE_CHROME_KEYS",
            "RUNTIME_UI_KEYS",
            "PROVIDER_ACTION_KEYS",
            "PROVIDER_DIALOG_KEYS",
            "PROVIDER_AUTHORIZATION_KEYS",
            "DASHBOARD_METRICS_ENHANCEMENT_KEYS",
            "ROUTING_STRATEGY_KEYS",
            "OPERATION_COPY_KEYS",
            "CREDENTIAL_CARD_KEYS",
            "CREDENTIAL_MODAL_KEYS",
            "UPDATE_GUIDE_KEYS",
            "CREDENTIAL_FLEET_KEYS",
            "CREDENTIAL_OPERATION_KEYS",
            "CREDENTIAL_TIER_KEYS",
        ):
            generated_keys.update(
                re.findall(
                    r"['\"]([a-z][a-z0-9_.-]+)['\"]", _extract_array(PAGE_LOCALE_SOURCE, variable)
                )
            )
        missing = sorted(
            key
            for key in references
            if key not in generated_keys
            and not re.search(
                rf"(?:['\"]{re.escape(key)}['\"]|\b{re.escape(key)})\s*:", combined_catalog
            )
        )
        self.assertEqual(missing, [], f"Missing English translations: {missing}")

    def test_locale_selector_covers_every_supported_locale(self):
        expected = {
            "en",
            "zh-CN",
            "zh-TW",
            "de",
            "es",
            "fr",
            "id",
            "it",
            "ja",
            "ko",
            "pt",
            "ru",
            "th",
            "tr",
            "vi",
        }
        locale_blocks = set(
            re.findall(r"^\s{4}(?:'([^']+)'|([a-z]{2})):\s*\{", LOCALE_SOURCE, re.MULTILINE)
        )
        discovered = {left or right for left, right in locale_blocks}
        self.assertTrue(expected.issubset(discovered))

    def test_management_requests_include_the_active_locale(self):
        self.assertIn("function installLocalizedFetch()", I18N_SOURCE)
        self.assertIn("headers.set('Accept-Language', getActiveLocale()", I18N_SOURCE)
        self.assertIn("requestUrl.pathname.startsWith('/api/')", I18N_SOURCE)

    def test_legacy_dynamic_messages_have_curated_locale_fallbacks(self):
        self.assertIn("const LEGACY_UI_FALLBACKS", I18N_SOURCE)
        self.assertIn("function resolveLegacyFallback", I18N_SOURCE)

    def test_automatic_copy_can_be_restored_when_language_changes(self):
        self.assertIn("const AUTO_TRANSLATED_TEXT = new WeakMap()", I18N_SOURCE)
        self.assertIn("locale === 'en'", I18N_SOURCE)

    def test_runtime_ui_does_not_embed_known_english_copy(self):
        runtime_source = "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((FRONTEND / "js").rglob("*.js"))
            if path.name not in {"i18n.js", "locales.js", "page-locales.js"}
        )
        forbidden_literals = {
            "Close navigation",
            "Open navigation",
            "Credential file",
            "Credential import",
            "Import completed.",
            "Provider Summary",
            "Check for updates",
            "Test Model",
            "Select a model",
            "The selected model test could not be completed.",
            "The credential completed a live model test successfully.",
            "The credential responded, but the provider reported a temporary rate limit. The router can continue with another available credential.",
            "Failure summary",
            "Test summary",
            "Rate limited",
            "Successful",
            "Verification failed.",
            "Credential verified.",
            "Verified",
            "Details",
            "Error details",
            "Summary",
            "Setting ID",
            "Binding ID",
            "provider credential",
            "credential files",
            "email addresses",
        }
        offenders = sorted(
            literal
            for literal in forbidden_literals
            if re.search(rf"(['\"`]){re.escape(literal)}\1", runtime_source)
        )

        self.assertEqual(offenders, [], f"Unlocalized runtime UI copy: {offenders}")

    def test_pre_state_factories_do_not_translate_during_app_state_initialization(self):
        upload_source = (FRONTEND / "js" / "core" / "upload-manager.js").read_text(encoding="utf-8")
        factory_prelude = upload_source.split("return {", 1)[0]

        self.assertNotIn(
            "t(",
            factory_prelude,
            "createUploadManager runs while AppState is in its temporal dead zone",
        )


if __name__ == "__main__":
    unittest.main()
