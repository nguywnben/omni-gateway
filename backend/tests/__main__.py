"""Run the backend test suite with repository-safe defaults."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


def main() -> int:
    tests_directory = Path(__file__).resolve().parent
    repository_root = tests_directory.parents[1]
    suite = unittest.defaultTestLoader.discover(
        start_dir=str(tests_directory),
        pattern="test_*.py",
        top_level_dir=str(repository_root),
    )
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
