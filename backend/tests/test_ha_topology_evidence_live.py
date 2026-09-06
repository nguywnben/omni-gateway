"""Opt-in external HA evidence discovery; skips are never acceptance evidence."""

from __future__ import annotations

import os
import subprocess
import unittest
from pathlib import Path

from tools.ha_topology_evidence.contract import (
    CandidateTopology,
    RunManifest,
    load_json,
    verify_run_manifest,
)


def live_evidence_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
            shell=False,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0 and bool(result.stdout.strip())


@unittest.skipUnless(
    os.getenv("OMNI_HA_EVIDENCE_LIVE", "").strip() == "1",
    "external HA evidence is opt-in",
)
class LiveExternalTopologyEvidenceTests(unittest.TestCase):
    def test_acceptance_requires_an_independently_verified_exact_candidate(self) -> None:
        self.assertTrue(
            live_evidence_available(),
            "mandatory external HA evidence infrastructure is unavailable",
        )
        manifest = os.getenv("OMNI_HA_EVIDENCE_MANIFEST", "").strip()
        candidate = os.getenv("OMNI_HA_EVIDENCE_CANDIDATE", "").strip()
        self.assertTrue(manifest, "OMNI_HA_EVIDENCE_MANIFEST is required for acceptance invocation")
        self.assertTrue(
            candidate, "OMNI_HA_EVIDENCE_CANDIDATE is required for acceptance invocation"
        )
        self.assertTrue(os.path.isfile(manifest), "external HA evidence manifest does not exist")
        self.assertTrue(os.path.isfile(candidate), "external HA evidence candidate does not exist")
        manifest_path = Path(manifest).resolve(strict=True)
        topology = CandidateTopology.from_dict(load_json(Path(candidate).resolve(strict=True)))
        run = RunManifest.from_dict(load_json(manifest_path))
        self.assertTrue(verify_run_manifest(run, topology, manifest_path.parent))


if __name__ == "__main__":
    unittest.main()
