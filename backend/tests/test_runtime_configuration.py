"""Runtime configuration safety contracts."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from main import _get_worker_count


class WorkerConfigurationTests(unittest.TestCase):
    def test_single_worker_is_supported(self):
        with patch.dict(os.environ, {"WORKERS": "1"}):
            self.assertEqual(_get_worker_count(), 1)

    def test_multiple_workers_fail_with_an_actionable_message(self):
        with patch.dict(os.environ, {"WORKERS": "2"}):
            with self.assertRaisesRegex(RuntimeError, "supports WORKERS=1 only"):
                _get_worker_count()

    def test_non_numeric_workers_are_rejected(self):
        with patch.dict(os.environ, {"WORKERS": "many"}):
            with self.assertRaisesRegex(RuntimeError, "must be the integer 1"):
                _get_worker_count()


if __name__ == "__main__":
    unittest.main()
