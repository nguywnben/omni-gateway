"""Static Access lifecycle and secret-lifetime contracts for W3.9."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"


class AccessVirtualKeyFrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fragment = (FRONTEND / "fragments/pages/access.html").read_text(encoding="utf-8")
        cls.feature = (FRONTEND / "js/features/virtual-keys.js").read_text(encoding="utf-8")
        cls.navigation = (FRONTEND / "js/core/navigation.js").read_text(encoding="utf-8")
        cls.root = (ROOT / "backend/core/panel/root.py").read_text(encoding="utf-8")

    def test_access_page_exposes_complete_lifecycle_controls(self):
        for control_id in (
            "virtualKeySearch",
            "virtualKeyStatusFilter",
            "virtualKeyList",
            "virtualKeyEmptyState",
        ):
            self.assertIn(f'id="{control_id}"', self.fragment)
        for action in ("create", "refresh", "edit", "usage", "rotate", "revoke"):
            self.assertIn(f"virtual-key-{action}", self.fragment + self.feature)

    def test_form_covers_policy_and_governance_inputs(self):
        for field in (
            "name",
            "enabled",
            "expires_at",
            "budget_daily_usd",
            "budget_monthly_usd",
            "rpm_limit",
            "tpm_limit",
            "allowed_models",
            "scopes",
            "unknown_pricing_policy",
            "fallback_price_usd_per_million",
        ):
            self.assertIn(field, self.feature)

    def test_secret_is_ephemeral_and_never_uses_browser_storage(self):
        self.assertIn("clearVirtualKeySecret", self.feature)
        self.assertIn("showVirtualKeySecret", self.feature)
        self.assertIn("secretInput.value = ''", self.feature)
        self.assertNotIn("localStorage", self.feature)
        self.assertNotIn("sessionStorage", self.feature)

    def test_access_loader_fetches_root_and_virtual_keys_together(self):
        self.assertIn("access: () => loadAccessPage()", self.navigation)
        self.assertIn("js/features/virtual-keys.js", self.root)
        self.assertIn("Promise.all([updateEndpointUrls(), loadVirtualKeys()])", self.feature)

    def test_lifecycle_mutations_send_optimistic_revision(self):
        self.assertIn("expected_revision: record.revision", self.feature)
        self.assertIn("/${encodeURIComponent(record.id)}/rotate", self.feature)
        self.assertIn("/${encodeURIComponent(record.id)}/revoke", self.feature)
        self.assertIn("error.status === 409", self.feature)


if __name__ == "__main__":
    unittest.main()
