"""Regression tests for the management console entry point and asset names."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.root import serve_control_panel


class ControlPanelAssetTests(unittest.TestCase):
    def test_console_entry_point_references_versioned_assets(self):
        response = serve_control_panel()
        body = response.body.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertRegex(body, r"/frontend/control-panel\.css\?v=\d+")
        for asset in (
            "core",
            "ui",
            "console",
            "credentials",
            "settings",
            "dashboard",
        ):
            self.assertRegex(body, rf"/frontend/js/{asset}\.js\?v=\d+")
        self.assertNotIn("/frontend/control-panel.js", body)
        self.assertNotIn("control_panel", body)
        self.assertNotIn("common.js", body)

    def test_sidebar_active_state_uses_data_tab_contract(self):
        response = serve_control_panel()
        body = response.body.decode("utf-8")
        core_script = (BACKEND_DIR.parent / "frontend" / "js" / "core.js").read_text(
            encoding="utf-8"
        )

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
            core_script,
        )
        self.assertNotIn(".tab[onclick*=", core_script)

    def test_xai_provider_ui_references_existing_assets_and_endpoints(self):
        response = serve_control_panel()
        body = response.body.decode("utf-8")
        settings_script = (BACKEND_DIR.parent / "frontend" / "js" / "settings.js").read_text(
            encoding="utf-8"
        )
        core_script = (BACKEND_DIR.parent / "frontend" / "js" / "core.js").read_text(
            encoding="utf-8"
        )
        provider_assets = BACKEND_DIR.parent / "frontend" / "assets" / "providers"
        self.assertTrue((provider_assets / "xai-grok-logo.png").is_file())
        self.assertTrue((provider_assets / "xai-console-logo.png").is_file())
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
        self.assertIn("/frontend/assets/providers/xai-console-logo.png", body)
        self.assertIn('<strong class="provider-name">Grok</strong>', body)
        self.assertIn('<strong class="provider-name">xAI Console</strong>', body)
        self.assertIn(
            "./api/providers/xai/credentials/import?credential_type=oauth",
            core_script,
        )
        self.assertIn(
            "./api/providers/xai/credentials/import?credential_type=api_key",
            core_script,
        )
        for endpoint in (
            "./api/providers/xai/config",
            "./api/providers/xai/config/reset",
            "./api/providers/xai/credentials",
            "./api/providers/xai/oauth/start",
            "./api/providers/xai/oauth/callback",
        ):
            self.assertIn(endpoint, settings_script)
        self.assertIn(
            "authorizationLink.textContent = data.auth_url || 'Authorization unavailable'",
            settings_script,
        )
        self.assertNotIn("Open xAI authorization", body)
        self.assertNotIn("Open xAI authorization", settings_script)

    def test_credential_verification_uses_provider_neutral_route(self):
        core_script = (BACKEND_DIR.parent / "frontend" / "js" / "core.js").read_text(
            encoding="utf-8"
        )
        credential_script = (BACKEND_DIR.parent / "frontend" / "js" / "credentials.js").read_text(
            encoding="utf-8"
        )

        self.assertIn("./api/credentials/verify", core_script)
        self.assertIn("./api/credentials/verify/", credential_script)
        self.assertNotIn("./api/credentials/verify-project", core_script)
        self.assertNotIn("./api/credentials/verify-project", credential_script)


if __name__ == "__main__":
    unittest.main()
