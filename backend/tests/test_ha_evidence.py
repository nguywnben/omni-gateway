"""Contracts for the reproducible, non-activation HA evidence harness."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from ha_evidence import run_synthetic_evidence


class HaEvidenceTests(unittest.IsolatedAsyncioTestCase):
    async def test_synthetic_evidence_is_correct_bounded_and_never_activates(self) -> None:
        evidence = await run_synthetic_evidence(operations=48)

        self.assertEqual(evidence["schema_version"], 1)
        self.assertEqual(evidence["scope"], "synthetic_in_process")
        self.assertTrue(evidence["not_activation_evidence"])
        self.assertFalse(evidence["activation_eligible"])
        self.assertEqual(len(evidence["activation_blockers"]), 4)
        self.assertEqual(evidence["correctness"]["duplicate_state_transitions"], 0)
        self.assertTrue(evidence["correctness"]["stale_epoch_denied"])
        self.assertTrue(evidence["correctness"]["dependency_failure_closed"])
        self.assertTrue(evidence["correctness"]["recovery_after_reconciliation"])
        for topology in ("one_logical_client", "two_logical_clients"):
            sample = evidence["load"][topology]
            self.assertEqual(sample["operations"], 48)
            self.assertGreaterEqual(sample["p95_ms"], sample["p50_ms"])
            self.assertGreaterEqual(sample["p99_ms"], sample["p95_ms"])
            self.assertGreater(sample["throughput_per_second"], 0)


class HaEvidenceCliTests(unittest.TestCase):
    def test_module_entrypoint_runs_from_the_repository_root(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "backend.ha_evidence", "--operations", "16"],
            cwd=BACKEND_DIR.parent,
            capture_output=True,
            check=False,
            text=True,
            timeout=30,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        evidence = __import__("json").loads(completed.stdout)
        self.assertTrue(evidence["not_activation_evidence"])
        self.assertFalse(evidence["activation_eligible"])


if __name__ == "__main__":
    unittest.main()
