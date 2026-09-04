"""Static deployment contracts for the W4.18 HA safety boundary."""

from __future__ import annotations

import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


class HaDeploymentAssetTests(unittest.TestCase):
    def test_environment_example_defaults_to_one_standalone_replica(self) -> None:
        source = (ROOT / ".env.example").read_text(encoding="utf-8")
        self.assertIn("OMNI_RUNTIME_MODE=standalone", source)
        self.assertIn("OMNI_REPLICA_COUNT=1", source)
        self.assertIn("# OMNI_COORDINATION_KEY=", source)

    def test_compose_is_standalone_by_default_and_allows_drain(self) -> None:
        source = (ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(source)
        service = data["services"]["app"]
        environment = service["environment"]
        self.assertIn("OMNI_RUNTIME_MODE=${OMNI_RUNTIME_MODE:-standalone}", environment)
        self.assertIn("OMNI_REPLICA_COUNT=${OMNI_REPLICA_COUNT:-1}", environment)
        self.assertIn("OMNI_COORDINATION_KEY=${OMNI_COORDINATION_KEY:-}", environment)
        self.assertEqual(service["stop_grace_period"], "45s")

    def test_helm_keeps_w418_replica_ceiling_and_secret_references(self) -> None:
        values = yaml.safe_load(
            (ROOT / "deploy" / "helm" / "omni-gateway" / "values.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(values["replicaCount"], 1)
        self.assertEqual(values["env"]["OMNI_RUNTIME_MODE"], "standalone")
        self.assertEqual(values["env"]["OMNI_REPLICA_COUNT"], "1")
        self.assertIn("redisUrl", values["secrets"])
        self.assertIn("coordinationKey", values["secrets"])

        deployment = (
            ROOT / "deploy" / "helm" / "omni-gateway" / "templates" / "deployment.yaml"
        ).read_text(encoding="utf-8")
        self.assertIn('fail "W4.18 supports exactly one application replica"', deployment)
        self.assertIn("replicas: {{ .Values.replicaCount }}", deployment)
        self.assertIn("terminationGracePeriodSeconds: 45", deployment)
        self.assertIn('"REDIS_URL" "OMNI_COORDINATION_KEY"', deployment)

    def test_ha_alerts_link_the_lifecycle_runbook(self) -> None:
        data = yaml.safe_load(
            (ROOT / "deploy" / "observability" / "prometheus-alerts.yml").read_text(
                encoding="utf-8"
            )
        )
        rules = {rule["alert"]: rule for rule in data["groups"][0]["rules"]}
        for name in ("OmniGatewayHARuntimeUnavailable", "OmniGatewayCoordinationUnavailable"):
            self.assertIn(name, rules)
            self.assertTrue(rules[name]["annotations"]["runbook_url"].endswith("ha-lifecycle.md"))


if __name__ == "__main__":
    unittest.main()
