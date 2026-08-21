"""Tests for Observability and TTFT Metrics Module."""

from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.observability import LLMRequestMetrics


class ObservabilityTests(unittest.TestCase):
    def test_metrics_ttft_and_throughput(self) -> None:
        metrics = LLMRequestMetrics(
            request_id="req-123",
            model="gpt-5.4",
            provider="openai_codex",
            credential_file="acc.json",
            input_tokens=100,
        )

        time.sleep(0.05)
        metrics.record_first_token()
        self.assertIsNotNone(metrics.ttft_ms)
        self.assertGreater(metrics.ttft_ms, 40.0)

        time.sleep(0.05)
        metrics.complete(output_tokens=50, status_code=200)

        self.assertGreater(metrics.tokens_per_second, 0.0)
        
        span = metrics.to_otel_span()
        self.assertEqual(span["attributes"]["gen_ai.request.model"], "gpt-5.4")
        self.assertEqual(span["status"], "OK")


if __name__ == "__main__":
    unittest.main()
