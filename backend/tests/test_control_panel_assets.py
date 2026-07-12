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


if __name__ == "__main__":
    unittest.main()
