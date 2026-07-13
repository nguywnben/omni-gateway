"""Shared filesystem helpers for deterministic test isolation."""

from __future__ import annotations

import shutil
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

PROJECT_DIR = Path(__file__).resolve().parents[2]
TEST_TEMP_ROOT = PROJECT_DIR / "temp" / "tests"


@contextmanager
def workspace_temp_directory() -> Iterator[str]:
    """Create a writable temporary directory without Windows mode-0700 ACLs."""
    TEST_TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    path = TEST_TEMP_ROOT / f"case-{uuid.uuid4().hex}"
    path.mkdir()
    try:
        yield str(path)
    finally:
        shutil.rmtree(path)
