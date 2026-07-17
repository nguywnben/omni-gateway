"""Integration tests for durable usage accounting."""

from __future__ import annotations

import sqlite3
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from core import usage_stats
from support import workspace_temp_directory


class UsageStatsTests(unittest.TestCase):
    def test_provider_display_names_preserve_google_ai_capitalization(self):
        self.assertEqual(
            usage_stats._provider_display_name("google_ai_studio"),
            "Google AI Studio",
        )
        self.assertEqual(
            usage_stats._provider_display_name("Google Antigravity"),
            "Google Antigravity",
        )
        self.assertEqual(usage_stats._provider_display_name("xai"), "Grok")

    def test_credential_display_names_distinguish_grok_from_xai_console(self):
        self.assertEqual(
            usage_stats._credential_provider_display_name("xai", "oauth"),
            "Grok",
        )
        self.assertEqual(
            usage_stats._credential_provider_display_name("xai", "api_key"),
            "xAI Console",
        )

    def test_record_call_persists_provider_and_compression_metrics(self):
        original_db_path = usage_stats.db_path
        with workspace_temp_directory() as temp_dir:
            try:
                usage_stats.db_path = str(Path(temp_dir) / "usage.db")
                usage_stats.record_call(
                    "credential.json",
                    model="model-a",
                    provider="primary",
                    token_usage={
                        "promptTokenCount": 120,
                        "candidatesTokenCount": 30,
                        "totalTokenCount": 150,
                    },
                    request_metrics={
                        "estimated_input_tokens": 100,
                        "estimated_tokens_saved": 40,
                        "compressed_messages": 6,
                        "latency_ms": 125,
                        "retry_count": 2,
                    },
                )

                connection = sqlite3.connect(usage_stats.db_path)
                try:
                    row = connection.execute(
                        """
                        SELECT input_tokens, output_tokens, total_tokens,
                               estimated_input_tokens, estimated_tokens_saved,
                               compressed_messages, latency_ms, retry_count
                        FROM usage_logs
                        """
                    ).fetchone()
                finally:
                    connection.close()

                self.assertEqual(row, (120, 30, 150, 100, 40, 6, 125, 2))
            finally:
                usage_stats.db_path = original_db_path


class UsageAggregationTests(unittest.IsolatedAsyncioTestCase):
    async def test_deleted_credential_usage_is_retained_anonymously(self):
        original_db_path = usage_stats.db_path
        with workspace_temp_directory() as temp_dir:
            try:
                usage_stats.db_path = str(Path(temp_dir) / "usage.db")
                usage_stats.record_call(
                    "google-ai-studio-private-fingerprint.json",
                    provider="google_ai_studio",
                    token_usage={
                        "promptTokenCount": 40,
                        "candidatesTokenCount": 10,
                        "totalTokenCount": 50,
                    },
                )

                changed = usage_stats.retire_credential_usage(
                    "google-ai-studio-private-fingerprint.json",
                    "google_ai_studio",
                )

                self.assertEqual(changed, 1)
                with (
                    patch.object(
                        usage_stats,
                        "get_credential_usage_metadata",
                        AsyncMock(return_value={}),
                    ),
                    patch.object(
                        usage_stats,
                        "get_all_credential_filenames",
                        AsyncMock(return_value=[]),
                    ),
                ):
                    result = await usage_stats.get_stats_for_period("all")

                deleted_filename = usage_stats.deleted_usage_filename("google_ai_studio")
                self.assertEqual(list(result), [deleted_filename])
                self.assertEqual(result[deleted_filename]["credential_label"], "Deleted credential")
                self.assertEqual(result[deleted_filename]["user_email"], "")
                self.assertTrue(result[deleted_filename]["is_deleted"])
                self.assertEqual(result[deleted_filename]["provider"], "google_ai_studio")
                self.assertEqual(result[deleted_filename]["calls"], 1)
                self.assertEqual(result[deleted_filename]["total_tokens"], 50)
            finally:
                usage_stats.db_path = original_db_path

    async def test_readded_credential_does_not_reclaim_deleted_history(self):
        original_db_path = usage_stats.db_path
        with workspace_temp_directory() as temp_dir:
            try:
                usage_stats.db_path = str(Path(temp_dir) / "usage.db")
                filename = "google-antigravity-account.json"
                usage_stats.record_call(filename, provider="google_antigravity")
                usage_stats.retire_credential_usage(filename, "google_antigravity")

                with (
                    patch.object(
                        usage_stats,
                        "get_credential_usage_metadata",
                        AsyncMock(
                            return_value={
                                filename: {
                                    "user_email": "readded@example.com",
                                    "provider": "google_antigravity",
                                    "provider_name": "Google Antigravity",
                                }
                            }
                        ),
                    ),
                    patch.object(
                        usage_stats,
                        "get_all_credential_filenames",
                        AsyncMock(return_value=[filename]),
                    ),
                ):
                    result = await usage_stats.get_stats_for_period("all")

                self.assertEqual(result[filename]["calls"], 0)
                self.assertEqual(result[filename]["user_email"], "readded@example.com")
                deleted_filename = usage_stats.deleted_usage_filename("google_antigravity")
                self.assertEqual(result[deleted_filename]["calls"], 1)
                self.assertTrue(result[deleted_filename]["is_deleted"])
            finally:
                usage_stats.db_path = original_db_path

    async def test_deleted_credentials_are_aggregated_by_provider(self):
        original_db_path = usage_stats.db_path
        with workspace_temp_directory() as temp_dir:
            try:
                usage_stats.db_path = str(Path(temp_dir) / "usage.db")
                usage_stats.record_call("account-a.json", provider="google_antigravity")
                usage_stats.record_call("account-b.json", provider="google_antigravity")
                usage_stats.retire_credential_usage(
                    "account-a.json",
                    "google_antigravity",
                )
                usage_stats.retire_credential_usage(
                    "account-b.json",
                    "google_antigravity",
                )

                with (
                    patch.object(
                        usage_stats,
                        "get_credential_usage_metadata",
                        AsyncMock(return_value={}),
                    ),
                    patch.object(
                        usage_stats,
                        "get_all_credential_filenames",
                        AsyncMock(return_value=[]),
                    ),
                ):
                    result = await usage_stats.get_stats_for_period("all")

                deleted_filename = usage_stats.deleted_usage_filename("google_antigravity")
                self.assertEqual(list(result), [deleted_filename])
                self.assertEqual(result[deleted_filename]["calls"], 2)
            finally:
                usage_stats.db_path = original_db_path

    async def test_usage_records_return_stable_provider_identity(self):
        original_db_path = usage_stats.db_path
        with workspace_temp_directory() as temp_dir:
            try:
                usage_stats.db_path = str(Path(temp_dir) / "usage.db")
                usage_stats.record_call(
                    "ai-studio.json",
                    provider="Google AI Studio",
                )

                with (
                    patch.object(
                        usage_stats,
                        "get_credential_usage_metadata",
                        AsyncMock(
                            return_value={
                                "ai-studio.json": {
                                    "user_email": "API key ending 1234",
                                    "credential_label": "API key ending 1234",
                                    "provider": "google_ai_studio",
                                    "provider_name": "Google AI Studio",
                                }
                            }
                        ),
                    ),
                    patch.object(
                        usage_stats,
                        "get_all_credential_filenames",
                        AsyncMock(return_value=["ai-studio.json"]),
                    ),
                ):
                    result = await usage_stats.get_stats_for_period("all")

                self.assertEqual(result["ai-studio.json"]["provider"], "google_ai_studio")
                self.assertEqual(result["ai-studio.json"]["provider_name"], "Google AI Studio")
                self.assertEqual(
                    result["ai-studio.json"]["credential_label"],
                    "API key ending 1234",
                )
            finally:
                usage_stats.db_path = original_db_path

    async def test_period_aggregation_returns_compression_metrics(self):
        original_db_path = usage_stats.db_path
        with workspace_temp_directory() as temp_dir:
            try:
                usage_stats.db_path = str(Path(temp_dir) / "usage.db")
                usage_stats.record_call(
                    "credential.json",
                    request_metrics={
                        "estimated_input_tokens": 100,
                        "estimated_tokens_saved": 40,
                        "compressed_messages": 6,
                        "latency_ms": 125,
                        "retry_count": 2,
                    },
                )

                with (
                    patch.object(
                        usage_stats,
                        "get_credential_usage_metadata",
                        AsyncMock(
                            return_value={
                                "credential.json": {
                                    "user_email": "user@example.com",
                                    "provider": "Antigravity",
                                }
                            }
                        ),
                    ),
                    patch.object(
                        usage_stats,
                        "get_all_credential_filenames",
                        AsyncMock(return_value=["credential.json"]),
                    ),
                ):
                    result = await usage_stats.get_stats_for_period("all")

                self.assertEqual(result["credential.json"]["estimated_tokens_saved"], 40)
                self.assertEqual(result["credential.json"]["compressed_messages"], 6)
                self.assertEqual(result["credential.json"]["average_latency_ms"], 125)
                self.assertEqual(result["credential.json"]["retry_count"], 2)
            finally:
                usage_stats.db_path = original_db_path


if __name__ == "__main__":
    unittest.main()
