"""Tests for the Prometheus /metrics endpoint and telemetry export wiring."""

from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from core import metrics as metrics_module
from core import usage_stats
from core.credential_operation_evidence import (
    clear_credential_operation_evidence_for_testing,
    record_credential_mutation,
)
from core.metrics import metrics, render_prometheus_metrics
from support import workspace_temp_directory


def _run(coro):
    return asyncio.get_event_loop_policy().new_event_loop().run_until_complete(coro)


SAMPLE_ROWS = [
    {
        "provider": "google_ai_studio",
        "calls": 10,
        "successful_calls": 9,
        "failed_calls": 1,
        "total_tokens": 12345,
        "cost_usd": 0.5,
        "total_latency_ms": 4500,
    },
    {
        "provider": "openai_platform",
        "calls": 3,
        "successful_calls": 3,
        "failed_calls": 0,
        "total_tokens": 900,
        "cost_usd": 0.01,
        "total_latency_ms": 300,
    },
]


class RenderPrometheusMetricsTests(unittest.TestCase):
    def setUp(self):
        clear_credential_operation_evidence_for_testing()

    def test_renders_per_provider_counters(self):
        output = render_prometheus_metrics(SAMPLE_ROWS)
        self.assertIn('omni_requests_total{provider="google_ai_studio"} 10', output)
        self.assertIn('omni_requests_success_total{provider="google_ai_studio"} 9', output)
        self.assertIn('omni_requests_failed_total{provider="google_ai_studio"} 1', output)
        self.assertIn('omni_tokens_total{provider="openai_platform"} 900', output)
        self.assertIn('omni_cost_usd_total{provider="google_ai_studio"} 0.500000', output)
        self.assertIn("omni_uptime_seconds", output)
        self.assertIn("omni_response_cache_hits_total", output)

    def test_help_and_type_lines_present(self):
        output = render_prometheus_metrics(SAMPLE_ROWS)
        self.assertIn("# HELP omni_requests_total", output)
        self.assertIn("# TYPE omni_requests_total counter", output)
        self.assertIn("# TYPE omni_uptime_seconds gauge", output)

    def test_label_values_are_escaped(self):
        rows = [dict(SAMPLE_ROWS[0], provider='weird"provider\\name')]
        output = render_prometheus_metrics(rows)
        self.assertIn('provider="weird\\"provider\\\\name"', output)

    def test_empty_rows_still_render_process_metrics(self):
        output = render_prometheus_metrics([])
        self.assertIn("omni_uptime_seconds", output)
        self.assertIn("omni_response_cache_entries", output)

    def test_credential_operation_metrics_are_exposed_with_bounded_labels(self):
        with patch("core.credential_operation_evidence.log.info"):
            record_credential_mutation(
                action="disable",
                operation="toggle",
                mode="primary",
                filename="must-not-appear.json",
                variant_id="google_ai_studio",
                outcome="succeeded",
                duration_ms=25,
                summary_code="operation_succeeded",
            )

        output = render_prometheus_metrics([])
        self.assertIn("# TYPE omni_credential_operations_total counter", output)
        self.assertIn(
            'operation="toggle",outcome="succeeded",mode="provider",variant="google_ai_studio"',
            output,
        )
        self.assertIn("# TYPE omni_credential_operation_duration_seconds histogram", output)
        self.assertNotIn("must-not-appear", output)


class MetricsEndpointTests(unittest.TestCase):
    def test_endpoint_returns_text_format(self):
        with patch.object(metrics_module, "get_provider_metrics", return_value=SAMPLE_ROWS):
            response = _run(metrics(authorization=None))
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response.media_type)
        self.assertIn(b"omni_requests_total", response.body)

    def test_token_protection_rejects_missing_bearer(self):
        with patch.dict("os.environ", {"METRICS_TOKEN": "secret-token"}):
            response = _run(metrics(authorization=None))
            self.assertEqual(response.status_code, 401)

            response_bad = _run(metrics(authorization="Bearer wrong"))
            self.assertEqual(response_bad.status_code, 401)

    def test_token_protection_accepts_valid_bearer(self):
        with patch.dict("os.environ", {"METRICS_TOKEN": "secret-token"}):
            with patch.object(metrics_module, "get_provider_metrics", return_value=[]):
                response = _run(metrics(authorization="Bearer secret-token"))
        self.assertEqual(response.status_code, 200)


class ProviderMetricsLedgerTests(unittest.TestCase):
    def test_get_provider_metrics_groups_by_provider(self):
        original_db_path = usage_stats.db_path
        with workspace_temp_directory() as temp_dir:
            try:
                usage_stats.db_path = str(Path(temp_dir) / "usage.db")
                usage_stats.record_call(
                    "a.json",
                    model="gpt-4o-mini",
                    provider="openai_platform",
                    token_usage={"prompt_tokens": 100, "completion_tokens": 10},
                )
                usage_stats.record_call(
                    "a.json",
                    model="gpt-4o-mini",
                    provider="openai_platform",
                    status_code=500,
                    success=False,
                )
                usage_stats.record_call(
                    "b.json",
                    model="gemini-2.5-flash",
                    provider="google_ai_studio",
                    token_usage={"promptTokenCount": 50, "candidatesTokenCount": 5},
                )

                rows = usage_stats.get_provider_metrics()
                by_provider = {row["provider"]: row for row in rows}

                self.assertEqual(by_provider["openai_platform"]["calls"], 2)
                self.assertEqual(by_provider["openai_platform"]["successful_calls"], 1)
                self.assertEqual(by_provider["openai_platform"]["failed_calls"], 1)
                self.assertEqual(by_provider["google_ai_studio"]["calls"], 1)
                self.assertGreater(by_provider["google_ai_studio"]["total_tokens"], 0)
            finally:
                usage_stats.db_path = original_db_path


class TelemetryConfigTests(unittest.TestCase):
    def test_disabled_without_keys(self):
        import config as config_module

        async def fake_get_config_value(key, default=None, env_var=None):
            return default

        async def scenario():
            with patch.object(config_module, "get_config_value", new=fake_get_config_value):
                return await config_module.get_telemetry_config()

        settings = _run(scenario())
        self.assertFalse(settings["enabled"])
        self.assertEqual(settings["langfuse_host"], "https://cloud.langfuse.com")

    def test_enabled_with_env_keys(self):
        import config as config_module

        with patch.dict(
            "os.environ",
            {
                "LANGFUSE_PUBLIC_KEY": "pk-test",
                "LANGFUSE_SECRET_KEY": "sk-test",
                "LANGFUSE_HOST": "https://langfuse.internal",
            },
        ):
            settings = _run(config_module.get_telemetry_config())
        self.assertTrue(settings["enabled"])
        self.assertEqual(settings["langfuse_host"], "https://langfuse.internal")


if __name__ == "__main__":
    unittest.main()
