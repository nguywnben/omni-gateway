"""Regression tests for the management console entry point and asset names."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.root import (
    CONSOLE_FRAGMENT_PATHS,
    CONSOLE_SCRIPT_ASSETS,
    CONSOLE_STYLE_ASSETS,
    _console_asset_version,
    _read_console_bundle,
    serve_control_panel,
)

FRONTEND_JS = BACKEND_DIR.parent / "frontend" / "js"


def read_scripts(*relative_paths: str) -> str:
    return "\n".join(
        (FRONTEND_JS / relative_path).read_text(encoding="utf-8")
        for relative_path in relative_paths
    )


class ControlPanelAssetTests(unittest.TestCase):
    def test_console_entry_point_references_versioned_assets(self):
        response = serve_control_panel()
        body = response.body.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertRegex(body, r"/frontend/console\.css\?v=\d+")
        self.assertRegex(body, r"/frontend/console\.js\?v=\d+")
        self.assertNotIn("/frontend/vendor/", body)
        self.assertNotIn("<!-- include:fragments/", body)
        self.assertNotIn("/frontend/control-panel.css", body)
        self.assertNotIn("/frontend/control-panel.js", body)
        self.assertNotIn("control_panel", body)
        self.assertNotIn("common.js", body)

    def test_console_manifest_covers_every_fragment_and_local_asset(self):
        response = serve_control_panel()
        body = response.body.decode("utf-8")
        frontend_dir = BACKEND_DIR.parent / "frontend"

        for relative_path in CONSOLE_FRAGMENT_PATHS:
            self.assertTrue((frontend_dir / "fragments" / relative_path).is_file())
        for relative_path in (
            *CONSOLE_STYLE_ASSETS,
            *CONSOLE_SCRIPT_ASSETS,
        ):
            self.assertTrue((frontend_dir / relative_path).is_file())

        asset_version = _console_asset_version()
        style_bundle = _read_console_bundle(CONSOLE_STYLE_ASSETS, asset_version, "\n")
        script_bundle = _read_console_bundle(CONSOLE_SCRIPT_ASSETS, asset_version, "\n;\n")
        self.assertIn(":root", style_bundle)
        self.assertIn("@media", style_bundle)
        self.assertIn("function applyLanguage", script_bundle)
        self.assertIn("function toggleMobileMenu", script_bundle)
        self.assertNotIn("/frontend/js/core/state.js", body)
        self.assertNotIn("/frontend/css/foundation.css", body)

        for legacy_path in (
            "control-panel.html",
            "control-panel.css",
            "js/core.js",
            "js/ui.js",
            "js/console.js",
            "js/credentials.js",
            "js/settings.js",
            "js/dashboard.js",
        ):
            self.assertFalse((frontend_dir / legacy_path).exists())

    def test_sidebar_active_state_uses_data_tab_contract(self):
        response = serve_control_panel()
        body = response.body.decode("utf-8")
        navigation_script = read_scripts("core/navigation.js")

        for tab_name in (
            "dashboard",
            "pool",
            "models",
            "providers",
            "config",
            "logs",
            "about",
        ):
            self.assertIn(
                f'data-ui-action="switch-tab" data-tab="{tab_name}"',
                body,
            )

        self.assertIn(
            'document.querySelector(`.tab[data-tab="${tabName}"]`)',
            navigation_script,
        )
        self.assertNotIn(".tab[onclick*=", navigation_script)
        self.assertIn("const TAB_DATA_CACHE_MS = 30000", navigation_script)
        self.assertIn("AppState.tabLoadPromises[tabName]", navigation_script)
        self.assertIn("void triggerTabDataLoad(tabName)", navigation_script)

        responsive_styles = (BACKEND_DIR.parent / "frontend" / "css" / "responsive.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("scrollbar-gutter: stable", responsive_styles)

    def test_xai_provider_ui_references_existing_assets_and_endpoints(self):
        response = serve_control_panel()
        body = response.body.decode("utf-8")
        settings_script = read_scripts(
            "features/provider-settings-shared.js",
            "features/google-ai-studio-settings.js",
            "features/xai-settings.js",
            "features/antigravity-settings.js",
        )
        upload_script = read_scripts("core/upload-manager.js", "core/state.js")
        provider_assets = BACKEND_DIR.parent / "frontend" / "assets" / "providers"
        self.assertTrue((provider_assets / "xai-grok-logo.png").is_file())
        self.assertTrue((provider_assets / "spacexai-console-logo.png").is_file())
        for element_id in (
            "providerSelectorGrok",
            "providerWorkspaceGrok",
            "providerSelectorXaiConsole",
            "providerWorkspaceXaiConsole",
            "grokUploadArea",
            "grokFileInput",
            "xaiConsoleUploadArea",
            "xaiConsoleFileInput",
        ):
            self.assertIn(f'id="{element_id}"', body)
        self.assertIn("/frontend/assets/providers/xai-grok-logo.png", body)
        self.assertIn("/frontend/assets/providers/spacexai-console-logo.png", body)
        self.assertIn('<strong class="provider-name">Grok Build</strong>', body)
        self.assertIn('<strong class="provider-name">SpaceXAI Console</strong>', body)
        self.assertIn(
            "./api/providers/xai/credentials/import?credential_type=oauth",
            upload_script,
        )
        self.assertIn(
            "./api/providers/xai/credentials/import?credential_type=api_key",
            upload_script,
        )
        for endpoint in (
            "./api/providers/xai/config",
            "./api/providers/xai/config/reset",
            "./api/providers/xai/credentials",
            "./api/providers/xai/oauth/start",
            "./api/providers/xai/oauth/complete",
        ):
            self.assertIn(endpoint, settings_script)
        self.assertNotIn("./api/providers/xai/oauth/callback", settings_script)
        self.assertIn('id="xaiAuthorizationCode"', body)
        self.assertIn("Authorization code", body)
        self.assertNotIn('id="xaiCallbackUrl"', body)
        self.assertIn(
            "authorizationLink.textContent = data.auth_url || 'Authorization unavailable'",
            settings_script,
        )
        self.assertNotIn("Open xAI authorization", body)
        self.assertNotIn("Open xAI authorization", settings_script)
        self.assertNotIn(">xAI<", body)
        self.assertNotIn("name: 'xAI'", upload_script)
        self.assertIn('<option value="xai">Grok Build</option>', body)

    def test_credential_verification_uses_provider_neutral_route(self):
        credential_manager_script = read_scripts("core/credential-manager.js")
        credential_script = read_scripts("features/credential-diagnostics.js")

        self.assertIn("./api/credentials/verify", credential_manager_script)
        self.assertIn("./api/credentials/verify/", credential_script)
        self.assertNotIn("./api/credentials/verify-project", credential_manager_script)
        self.assertNotIn("./api/credentials/verify-project", credential_script)

    def test_grok_build_oauth_uses_the_shared_quota_dialog(self):
        card_script = read_scripts("ui/credential-cards.js")
        dialog_script = read_scripts("ui/credential-dialogs.js")

        self.assertIn("isGrokOAuth", card_script)
        self.assertIn(
            "const supportsQuotaPreview = managerType === 'primary' && (isAntigravity || isGrokOAuth);",
            card_script,
        )
        self.assertIn("const quotaPreview = supportsQuotaPreview", card_script)
        self.assertIn("data?.quota_type === 'account_billing'", dialog_script)
        self.assertIn("Billing Periods", dialog_script)
        self.assertIn("active billing periods", dialog_script)


if __name__ == "__main__":
    unittest.main()
