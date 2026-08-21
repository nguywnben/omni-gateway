"""Tests for Advanced Load Balancing and Routing Policies."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.advanced_routing import (
    select_cost_minimized_candidate,
    select_lowest_latency_candidate,
    select_weighted_candidate,
)


class AdvancedRoutingTests(unittest.TestCase):
    def test_select_lowest_latency(self) -> None:
        candidates = [{"filename": "fast.json"}, {"filename": "slow.json"}]
        latency_map = {"fast.json": 120.5, "slow.json": 850.0}

        selected = select_lowest_latency_candidate(candidates, latency_map)
        self.assertEqual(selected["filename"], "fast.json")

    def test_select_cost_minimized(self) -> None:
        candidates = [
            {"filename": "paid-openai.json", "provider": "openai_platform"},
            {"filename": "free-gemini.json", "provider": "google_ai_studio", "tier": "free"},
        ]
        selected = select_cost_minimized_candidate(candidates)
        self.assertEqual(selected["filename"], "free-gemini.json")

    def test_select_weighted(self) -> None:
        candidates = [{"filename": "heavy.json"}, {"filename": "light.json"}]
        weights = {"heavy.json": 1000.0, "light.json": 0.0001}

        selected = select_weighted_candidate(candidates, weights)
        self.assertEqual(selected["filename"], "heavy.json")


if __name__ == "__main__":
    unittest.main()
