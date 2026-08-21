"""Tests for the model pricing table and cost ledger integration."""

from __future__ import annotations

import json
import sqlite3
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

from core import pricing, usage_stats
from support import workspace_temp_directory


class ModelPricingLookupTests(unittest.TestCase):
    def test_exact_match_returns_pricing(self):
        entry = pricing.find_model_pricing("gemini-2.5-pro")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.input_per_million, 1.25)
        self.assertEqual(entry.output_per_million, 10.00)

    def test_dated_variant_inherits_base_pricing_via_longest_prefix(self):
        base = pricing.find_model_pricing("gpt-5")
        dated = pricing.find_model_pricing("gpt-5-2026-01-12")
        mini = pricing.find_model_pricing("gpt-5-mini-2026-01-12")
        self.assertIsNotNone(base)
        self.assertIsNotNone(dated)
        self.assertIsNotNone(mini)
        self.assertEqual(dated.input_per_million, base.input_per_million)
        # Longest prefix must win: gpt-5-mini variant maps to mini pricing.
        self.assertEqual(mini.input_per_million, 0.25)

    def test_models_prefix_and_tag_suffixes_are_normalized(self):
        self.assertIsNotNone(pricing.find_model_pricing("models/gemini-2.5-flash"))
        self.assertIsNone(pricing.find_model_pricing("llama3:8b"))

    def test_unknown_model_returns_none(self):
        self.assertIsNone(pricing.find_model_pricing("totally-unknown-model"))
        self.assertIsNone(pricing.find_model_pricing(""))


class CalculateCostTests(unittest.TestCase):
    def test_cost_combines_all_token_classes(self):
        # gemini-2.5-pro: in 1.25, out 10.0, cache 0.31 per 1M tokens.
        cost = pricing.calculate_cost_usd(
            "gemini-2.5-pro",
            input_tokens=1_000_000,
            output_tokens=100_000,
            cached_tokens=200_000,
            reasoning_tokens=50_000,
        )
        expected = (
            800_000 * 1.25 + 200_000 * 0.31 + 100_000 * 10.0 + 50_000 * 10.0
        ) / 1_000_000
        self.assertAlmostEqual(cost, expected, places=8)

    def test_cached_tokens_clamped_to_input(self):
        cost_normal = pricing.calculate_cost_usd(
            "gpt-4o", input_tokens=100, cached_tokens=100
        )
        cost_overflow = pricing.calculate_cost_usd(
            "gpt-4o", input_tokens=100, cached_tokens=5_000
        )
        self.assertAlmostEqual(cost_normal, cost_overflow, places=10)

    def test_zero_cost_provider_short_circuits(self):
        cost = pricing.calculate_cost_usd(
            "gpt-4o", input_tokens=1_000_000, output_tokens=1_000_000, provider="ollama"
        )
        self.assertEqual(cost, 0.0)

    def test_unknown_model_costs_zero(self):
        self.assertEqual(
            pricing.calculate_cost_usd("mystery-model", input_tokens=1_000_000), 0.0
        )

    def test_negative_token_counts_are_sanitized(self):
        self.assertEqual(
            pricing.calculate_cost_usd("gpt-4o", input_tokens=-50, output_tokens=-10),
            0.0,
        )


class PricingOverridesTests(unittest.TestCase):
    def test_overrides_file_extends_and_replaces_builtin_entries(self):
        with workspace_temp_directory() as temp_dir:
            overrides_path = Path(temp_dir) / pricing.PRICING_OVERRIDES_FILENAME
            overrides_path.write_text(
                json.dumps(
                    {
                        "gpt-4o": {"input": 99.0, "output": 199.0},
                        "custom-house-model": {
                            "input": 1.0,
                            "output": 2.0,
                            "cache_read": 0.5,
                        },
                    }
                ),
                encoding="utf-8",
            )
            table = pricing._PricingTable()
            with patch.object(
                pricing, "_pricing_overrides_path", return_value=overrides_path
            ):
                overridden = table.lookup("gpt-4o")
                custom = table.lookup("custom-house-model")
            self.assertEqual(overridden.input_per_million, 99.0)
            self.assertEqual(custom.cache_read_per_million, 0.5)

    def test_malformed_overrides_are_ignored(self):
        with workspace_temp_directory() as temp_dir:
            overrides_path = Path(temp_dir) / pricing.PRICING_OVERRIDES_FILENAME
            overrides_path.write_text("not-json", encoding="utf-8")
            table = pricing._PricingTable()
            with patch.object(
                pricing, "_pricing_overrides_path", return_value=overrides_path
            ):
                entry = table.lookup("gpt-4o")
            # Falls back to the built-in table.
            self.assertEqual(entry.input_per_million, 2.50)


class CostLedgerIntegrationTests(unittest.TestCase):
    def test_record_call_persists_cost_and_api_key_id(self):
        original_db_path = usage_stats.db_path
        with workspace_temp_directory() as temp_dir:
            try:
                usage_stats.db_path = str(Path(temp_dir) / "usage.db")
                usage_stats.record_call(
                    "credential.json",
                    model="gemini-2.5-flash",
                    provider="google_ai_studio",
                    token_usage={
                        "promptTokenCount": 1_000_000,
                        "candidatesTokenCount": 100_000,
                        "totalTokenCount": 1_100_000,
                    },
                    request_id="request-cost-1",
                    api_key_id="vk_test123",
                )

                connection = sqlite3.connect(usage_stats.db_path)
                try:
                    row = connection.execute(
                        "SELECT cost_usd, api_key_id FROM usage_logs"
                    ).fetchone()
                finally:
                    connection.close()

                # gemini-2.5-flash: 1M input * $0.30/1M + 0.1M output * $2.50/1M
                self.assertAlmostEqual(row[0], 0.30 + 0.25, places=6)
                self.assertEqual(row[1], "vk_test123")
            finally:
                usage_stats.db_path = original_db_path

    def test_get_spend_since_filters_by_api_key(self):
        original_db_path = usage_stats.db_path
        with workspace_temp_directory() as temp_dir:
            try:
                usage_stats.db_path = str(Path(temp_dir) / "usage.db")
                for key_id in ("vk_a", "vk_a", "vk_b"):
                    usage_stats.record_call(
                        "credential.json",
                        model="gpt-4o-mini",
                        provider="openai_platform",
                        token_usage={
                            "prompt_tokens": 1_000_000,
                            "completion_tokens": 0,
                            "total_tokens": 1_000_000,
                        },
                        api_key_id=key_id,
                    )

                spend_all = usage_stats.get_spend_since(0)
                spend_a = usage_stats.get_spend_since(0, api_key_id="vk_a")
                spend_b = usage_stats.get_spend_since(0, api_key_id="vk_b")

                self.assertEqual(spend_all["calls"], 3)
                self.assertEqual(spend_a["calls"], 2)
                self.assertEqual(spend_b["calls"], 1)
                self.assertAlmostEqual(spend_all["cost_usd"], 0.45, places=6)
                self.assertAlmostEqual(spend_a["cost_usd"], 0.30, places=6)
                self.assertGreater(spend_a["total_tokens"], 0)
            finally:
                usage_stats.db_path = original_db_path

    def test_spend_since_future_timestamp_returns_zero(self):
        original_db_path = usage_stats.db_path
        with workspace_temp_directory() as temp_dir:
            try:
                usage_stats.db_path = str(Path(temp_dir) / "usage.db")
                usage_stats.record_call(
                    "credential.json",
                    model="gpt-4o",
                    provider="openai_platform",
                    token_usage={"prompt_tokens": 1000, "completion_tokens": 100},
                )
                spend = usage_stats.get_spend_since(9_999_999_999)
                self.assertEqual(spend["calls"], 0)
                self.assertEqual(spend["cost_usd"], 0.0)
            finally:
                usage_stats.db_path = original_db_path


if __name__ == "__main__":
    unittest.main()
