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

    def test_external_evidence_topology_is_isolated_bounded_and_closed(self) -> None:
        path = ROOT / "deploy" / "evidence" / "compose.ha.yml"
        source = path.read_text(encoding="utf-8")
        data = yaml.safe_load(source)
        services = data["services"]
        self.assertEqual(
            set(services),
            {"app-a", "app-b", "redis-primary", "redis-standby", "postgres", "fixture"},
        )
        self.assertTrue(data["networks"]["evidence"]["internal"])
        self.assertEqual(
            data["networks"]["control"]["driver_opts"][
                "com.docker.network.bridge.enable_ip_masquerade"
            ],
            "false",
        )
        self.assertNotIn("docker.sock", source)
        self.assertNotIn("/opt/omni-gateway", source)
        self.assertIn("${REDIS_IMAGE:?", source)
        self.assertIn("${POSTGRES_IMAGE:?", source)
        self.assertIn("${EVIDENCE_IMAGE:?", source)
        self.assertIn("${OMNI_EVIDENCE_IMAGE:?", source)
        dockerfile = (ROOT / "deploy" / "evidence" / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn("ARG PRODUCTION_IMAGE_ID", dockerfile)
        self.assertIn("com.omni-gateway.evidence.production-image", dockerfile)
        self.assertIn("com.omni-gateway.evidence.launcher-digest", dockerfile)

        production_dockerfile = (ROOT / "deploy" / "Dockerfile").read_text(encoding="utf-8")
        self.assertIn(
            "FROM python:3.12-slim@sha256:"
            "78387bc3881b8273120a12ebe6c1ab22b018ccc2c9adf565ae1ac9b536e184ea",
            production_dockerfile,
        )
        self.assertLess(
            production_dockerfile.index("RUN pip install --no-cache-dir --require-hashes"),
            production_dockerfile.index('ARG REVISION="unknown"'),
        )

        for name, service in services.items():
            self.assertEqual(set(service["networks"]), {"evidence", "control"}, name)
            self.assertTrue(service["read_only"], name)
            self.assertEqual(service["restart"], "no", name)
            self.assertIn("ALL", service["cap_drop"], name)
            self.assertIn("no-new-privileges:true", service["security_opt"], name)
            self.assertGreater(service["pids_limit"], 0, name)
            self.assertTrue(service["mem_limit"], name)
            self.assertGreater(service["cpus"], 0, name)
            for published in service.get("ports", []):
                self.assertTrue(str(published).startswith("127.0.0.1:"), (name, published))

        for name in ("app-a", "app-b"):
            environment = services[name]["environment"]
            self.assertEqual(environment["WORKERS"], "1")
            self.assertEqual(environment["OMNI_RUNTIME_MODE"], "coordinated")
        self.assertEqual(environment["RETRY_429_ENABLED"], "false")
        self.assertEqual(environment["RETRY_429_MAX_RETRIES"], "0")
        self.assertEqual(environment["RESPONSE_CACHE_ENABLED"], "true")
        self.assertIn("${EVIDENCE_METRICS_TOKEN:?", source)
        for name in ("redis-primary", "redis-standby"):
            self.assertEqual(services[name]["user"], "999:1000")
            self.assertEqual(services[name]["cap_drop"], ["ALL"])
        self.assertEqual(services["postgres"]["user"], "70:70")
        self.assertEqual(services["postgres"]["cap_drop"], ["ALL"])

    def test_external_rollback_is_one_standalone_process_on_the_same_postgresql_history(
        self,
    ) -> None:
        path = ROOT / "deploy" / "evidence" / "compose.rollback.yml"
        source = path.read_text(encoding="utf-8")
        data = yaml.safe_load(source)
        self.assertEqual(set(data["services"]), {"app-a"})
        service = data["services"]["app-a"]
        self.assertIn("${PRODUCTION_IMAGE:?", service["image"])
        self.assertEqual(service["environment"]["WORKERS"], "1")
        self.assertEqual(service["environment"]["OMNI_RUNTIME_MODE"], "standalone")
        self.assertEqual(service["environment"]["OMNI_REPLICA_COUNT"], "1")
        self.assertEqual(service["environment"]["REDIS_URL"], "")
        self.assertIn("postgresql://omni@fixture:", service["environment"]["POSTGRESQL_URI"])
        self.assertNotIn("depends_on", service)
        self.assertTrue(data["networks"]["evidence"]["external"])


if __name__ == "__main__":
    unittest.main()
