"""Backend test suite with an isolated credential store."""

from __future__ import annotations

import atexit
import os
import shutil
from pathlib import Path

_TEST_DATA_DIRECTORY = (
    Path(__file__).resolve().parents[2] / "temp" / "tests" / f"session-{os.getpid()}"
)


def _configure_test_storage() -> None:
    if os.environ.get("CREDENTIALS_DIR"):
        return

    _TEST_DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    os.environ["CREDENTIALS_DIR"] = str(_TEST_DATA_DIRECTORY)
    atexit.register(shutil.rmtree, _TEST_DATA_DIRECTORY, ignore_errors=True)


_configure_test_storage()
