"""Static contracts for symptom alerts and linked operational runbooks."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class ObservabilityAssetTests(unittest.TestCase):
    def test_alert_rules_are_bounded_and_link_existing_runbooks(self):
        path = ROOT / "deploy" / "observability" / "prometheus-alerts.yml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        rules = data["groups"][0]["rules"]
        self.assertEqual(len(rules), 5)
        for rule in rules:
            self.assertIn(rule["labels"]["severity"], {"warning", "critical"})
            self.assertRegex(rule["for"], r"^\d+[ms]$")
            link = rule["annotations"]["runbook_url"]
            relative = re.search(r"/docs/(runbooks/[^?#]+)$", link).group(1)
            self.assertTrue((ROOT / "docs" / relative).is_file(), rule["alert"])

    def test_alert_expressions_never_use_high_cardinality_labels(self):
        source = (ROOT / "deploy" / "observability" / "prometheus-alerts.yml").read_text(
            encoding="utf-8"
        )
        for forbidden in ("request_id", "trace_id", "model=", "credential"):
            self.assertNotIn(forbidden, source)

    def test_helm_alert_copy_matches_reference_contract(self):
        reference = yaml.safe_load(
            (ROOT / "deploy" / "observability" / "prometheus-alerts.yml").read_text(
                encoding="utf-8"
            )
        )
        chart = yaml.safe_load(
            (
                ROOT
                / "deploy"
                / "helm"
                / "omni-gateway"
                / "observability"
                / "prometheus-alerts.yml"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(chart, reference)
