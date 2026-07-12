"""Tests for non-blocking log-file helper behavior."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.logs import (
    _clear_log_file,
    _log_file_size,
    _read_log_chunk,
    _read_recent_log_lines,
)


class LogFileHelperTests(unittest.TestCase):
    def test_clear_log_file_truncates_existing_file(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp_dir:
            path = Path(temp_dir) / "runtime.log"
            path.write_text("sensitive line\n", encoding="utf-8")

            self.assertTrue(_clear_log_file(str(path)))
            self.assertEqual(_log_file_size(str(path)), 0)
            self.assertEqual(path.read_text(encoding="utf-8"), "")

    def test_missing_log_file_is_reported_without_creation(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp_dir:
            path = Path(temp_dir) / "missing.log"

            self.assertFalse(_clear_log_file(str(path)))
            self.assertIsNone(_log_file_size(str(path)))
            self.assertEqual(_read_recent_log_lines(str(path), 50), [])

    def test_recent_lines_and_binary_offsets_are_stable(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp_dir:
            path = Path(temp_dir) / "runtime.log"
            path.write_bytes(b"first\nsecond\nthird\n")

            self.assertEqual(_read_recent_log_lines(str(path), 2), ["second\n", "third\n"])
            content, bytes_read = _read_log_chunk(str(path), len("first\n"), len("second\n"))
            self.assertEqual(content, "second\n")
            self.assertEqual(bytes_read, len("second\n"))


if __name__ == "__main__":
    unittest.main()
