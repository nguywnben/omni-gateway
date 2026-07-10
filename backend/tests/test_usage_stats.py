"""Integration tests for durable usage accounting."""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core import usage_stats


class UsageStatsTests(unittest.TestCase):
    def test_record_call_persists_provider_and_compression_metrics(self):
        original_db_path = usage_stats.db_path
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp_dir:
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
                    },
                )

                connection = sqlite3.connect(usage_stats.db_path)
                try:
                    row = connection.execute(
                        """
                        SELECT input_tokens, output_tokens, total_tokens,
                               estimated_input_tokens, estimated_tokens_saved,
                               compressed_messages
                        FROM usage_logs
                        """
                    ).fetchone()
                finally:
                    connection.close()

                self.assertEqual(row, (120, 30, 150, 100, 40, 6))
            finally:
                usage_stats.db_path = original_db_path


class UsageAggregationTests(unittest.IsolatedAsyncioTestCase):
    async def test_period_aggregation_returns_compression_metrics(self):
        original_db_path = usage_stats.db_path
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp_dir:
            try:
                usage_stats.db_path = str(Path(temp_dir) / "usage.db")
                usage_stats.record_call(
                    "credential.json",
                    request_metrics={
                        "estimated_input_tokens": 100,
                        "estimated_tokens_saved": 40,
                        "compressed_messages": 6,
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

                self.assertEqual(
                    result["credential.json"]["estimated_tokens_saved"], 40
                )
                self.assertEqual(
                    result["credential.json"]["compressed_messages"], 6
                )
            finally:
                usage_stats.db_path = original_db_path


if __name__ == "__main__":
    unittest.main()
