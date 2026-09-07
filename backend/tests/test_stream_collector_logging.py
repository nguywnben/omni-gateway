"""Regression tests for bounded stream-collector observability."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.api.utils import collect_streaming_response


class StreamCollectorLoggingTests(unittest.IsolatedAsyncioTestCase):
    async def test_success_summary_is_debug_not_per_request_info(self) -> None:
        async def stream():
            yield (
                'data: {"response":{"candidates":[{"content":{"parts":'
                '[{"text":"ok"}]},"finishReason":"STOP"}]}}'
            )

        summary = (
            "[STREAM COLLECTOR] Collected 1 text chunks, 0 thought chunks, "
            "0 other parts (tool parts: 0)"
        )
        with (
            patch("core.api.utils.log.debug") as debug,
            patch("core.api.utils.log.info") as info,
        ):
            response = await collect_streaming_response(stream())

        self.assertEqual(response.status_code, 200)
        debug.assert_any_call(summary)
        info.assert_not_called()


if __name__ == "__main__":
    unittest.main()
