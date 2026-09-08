"""Contract tests for the reproducible P0.4 maintainability baseline."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

from tools.maintainability_inventory import INVENTORY_CATEGORIES, build_inventory

ROOT = Path(__file__).resolve().parents[2]
BASELINE_PATH = ROOT / "docs" / "audits" / "maintainability-baseline.json"


class MaintainabilityBaselineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    def test_saved_inventory_matches_current_repository(self) -> None:
        self.assertEqual(self.baseline["inventory"], build_inventory(ROOT))

    def test_all_required_categories_have_inventory_and_risk_ownership(self) -> None:
        self.assertEqual(set(self.baseline["inventory"]), set(INVENTORY_CATEGORIES))
        covered = {risk["category"] for risk in self.baseline["risks"]}
        self.assertEqual(covered, set(INVENTORY_CATEGORIES))

    def test_every_risk_has_an_existing_plan_owner(self) -> None:
        plan = (ROOT / "tasks" / "plan.md").read_text(encoding="utf-8")
        valid_owners = set(re.findall(r"^### (P[0-5]\.[1-6])\b", plan, flags=re.MULTILINE))
        valid_owners.add("POST-R1")

        high_risks = 0
        for risk in self.baseline["risks"]:
            owners = risk.get("owners", [])
            self.assertTrue(owners, risk["id"])
            self.assertTrue(set(owners).issubset(valid_owners), risk["id"])
            if risk["severity"] in {"critical", "high"}:
                high_risks += 1
        self.assertGreater(high_risks, 0)

    def test_file_size_does_not_authorize_refactoring(self) -> None:
        large_module_risks = [
            risk for risk in self.baseline["risks"] if risk["category"] == "large_modules"
        ]
        self.assertTrue(large_module_risks)
        for risk in large_module_risks:
            self.assertFalse(risk["file_size_refactor_authorized"], risk["id"])

    def test_cli_check_reproduces_the_saved_inventory(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "tools" / "maintainability_inventory.py"),
                "--check",
                str(BASELINE_PATH),
            ],
            cwd=ROOT,
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Maintainability inventory matches", completed.stdout)


if __name__ == "__main__":
    unittest.main()
