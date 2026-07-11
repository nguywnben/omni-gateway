"""Tests for production health probes."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.health import health, ready


class HealthProbeTests(unittest.IsolatedAsyncioTestCase):
    async def test_liveness_is_dependency_free(self):
        response = await health()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body), {"status": "ok"})

    async def test_readiness_reports_available_storage(self):
        storage = AsyncMock()
        storage.get_all_config.return_value = {}
        with patch(
            "core.health.get_storage_adapter",
            new=AsyncMock(return_value=storage),
        ):
            response = await ready()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body)["storage"], "available")

    async def test_readiness_returns_503_without_exposing_exception(self):
        with patch(
            "core.health.get_storage_adapter",
            new=AsyncMock(side_effect=RuntimeError("database password leaked")),
        ):
            response = await ready()

        self.assertEqual(response.status_code, 503)
        body = response.body.decode()
        self.assertNotIn("database password leaked", body)
        self.assertEqual(json.loads(body)["storage"], "unavailable")
