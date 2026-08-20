"""Tests for request-scoped telemetry metadata."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.request_context import get_request_elapsed_ms, get_request_id, request_scope


class RequestContextTests(unittest.TestCase):
    def test_scope_exposes_and_resets_request_metadata(self):
        self.assertEqual(get_request_id(), "")
        with request_scope("request-123"):
            self.assertEqual(get_request_id(), "request-123")
            self.assertGreaterEqual(get_request_elapsed_ms(), 0)
        self.assertEqual(get_request_id(), "")


if __name__ == "__main__":
    unittest.main()
