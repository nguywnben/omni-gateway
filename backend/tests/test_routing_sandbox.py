"""Tests for Routing Sandbox Module."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.routing_sandbox import simulate_sandbox_inspection


class RoutingSandboxTests(unittest.TestCase):
    def test_sandbox_simulation_analysis(self) -> None:
        creds = [
            {"filename": "acc1.json", "provider": "openai_codex", "tier": "pro"},
            {"filename": "acc2.json", "provider": "google_ai_studio", "tier": "free"},
        ]
        payload = {"messages": [{"role": "user", "content": "hello test"}]}
        
        res = simulate_sandbox_inspection(
            request_format="openai",
            target_model="gpt-5.4",
            payload=payload,
            available_credentials=creds,
        )

        self.assertEqual(res["format"], "openai")
        self.assertEqual(res["model"], "gpt-5.4")
        self.assertEqual(res["routing_simulation"]["eligible_candidates_count"], 2)
        self.assertEqual(res["routing_simulation"]["selected_candidate"]["filename"], "acc1.json")


if __name__ == "__main__":
    unittest.main()
