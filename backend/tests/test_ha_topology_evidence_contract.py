from __future__ import annotations

import dataclasses
import hashlib
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.durable_migration import DURABLE_COPY_FAMILIES

from backend.tests.support import workspace_temp_directory
from tools.ha_topology_evidence.contract import (
    RECOVERY_CLOCK_SCENARIOS,
    REQUIRED_SCENARIOS,
    CandidateTopology,
    CandidateVerifier,
    CorrectnessCounters,
    EvidenceVerificationError,
    RecoveryClock,
    RunManifest,
    ScenarioResult,
    ScenarioState,
    canonical_bytes,
    expected_challenged_operations,
    expected_fault_milestones,
    expected_sample_partitions,
    load_json,
    verify_run_manifest,
    write_atomic_manifest,
)
from tools.ha_topology_evidence.report import EvidenceReportWriter, load_jsonl


def candidate() -> CandidateTopology:
    image = "sha256:" + ("d" * 64)
    redis = "redis:8.2.1@sha256:" + ("e" * 64)
    return CandidateTopology(
        profile="redis8-postgres17-two-replicas",
        source_revision="a" * 40,
        source_tree_digest="b" * 64,
        production_image=image,
        evidence_image="sha256:" + ("2" * 64),
        evidence_launcher_digest="c" * 64,
        redis_primary_image=redis,
        redis_standby_image=redis,
        postgresql_image="postgres:17.6@sha256:" + ("f" * 64),
        migration_manifest_checksum="1" * 64,
    )


def manifest(root: Path, topology: CandidateTopology | None = None) -> RunManifest:
    selected = topology or candidate()
    candidate_payload = canonical_bytes(selected.to_dict()) + b"\n"
    (root / "candidate.json").write_bytes(candidate_payload)
    event_records: list[dict[str, object]] = []
    sample_records: list[dict[str, object]] = []
    results: list[ScenarioResult] = []
    sequence = 0
    for scenario in REQUIRED_SCENARIOS:
        repetitions = range(1, 4) if scenario.startswith("coordinated-") else (1,)
        for repetition in repetitions:
            started = len(event_records) * 2 + 1
            challenged = expected_challenged_operations(selected, scenario)
            milestones = expected_fault_milestones(scenario)
            for phase, count in expected_sample_partitions(selected, scenario).items():
                for attempt in range(1, count + 1):
                    success = phase != "fault"
                    sample_records.append(
                        {
                            "sequence": sequence,
                            "replica": "app-a" if sequence % 2 == 0 else "app-b",
                            "status_code": 200 if success else 503,
                            "duration_ms": 1.0,
                            "success": success,
                            "transport_failure": False,
                            "operation_digest": hashlib.sha256(
                                (
                                    f"operation:{scenario}:{repetition}"
                                    if scenario == "duplicate-delivery"
                                    else f"operation:{sequence}"
                                ).encode("ascii")
                            ).hexdigest(),
                            "delivery_digest": hashlib.sha256(
                                f"delivery:{sequence}".encode("ascii")
                            ).hexdigest(),
                            "scenario_id": scenario,
                            "repetition": repetition,
                            "phase": phase,
                            "attempt": attempt,
                            "schedule_seed": (
                                selected.pair_seeds[repetition - 1]
                                if scenario.startswith("coordinated-")
                                else 0
                            ),
                        }
                    )
                    sequence += 1
            counted = [
                sample
                for sample in sample_records
                if sample["scenario_id"] == scenario
                and sample["repetition"] == repetition
                and sample["phase"] != "warmup"
            ]
            client_success = sum(bool(sample["success"]) for sample in counted)
            rejected = len(counted) - client_success
            counters = (
                CorrectnessCounters(
                    attempted=2,
                    admitted=1,
                    upstream_started=1,
                    upstream_completed=1,
                    client_success=2,
                    durable_committed=1,
                    replay_success=1,
                )
                if scenario == "duplicate-delivery"
                else CorrectnessCounters(
                    attempted=challenged,
                    admitted=client_success,
                    upstream_started=client_success,
                    upstream_completed=client_success,
                    client_success=client_success,
                    rejected=rejected,
                    durable_committed=client_success,
                )
            )
            recovery_clock = (
                RecoveryClock(
                    started,
                    started + 1,
                    started + 2,
                    started + 3,
                    started + 4,
                    started + 5,
                    started + 6,
                )
                if scenario in RECOVERY_CLOCK_SCENARIOS
                else None
            )
            event_records.append(
                {
                    "schema_version": 1,
                    "scenario_id": scenario,
                    "repetition": repetition,
                    "started_monotonic_ns": started,
                    "completed_monotonic_ns": started + 1_000_000,
                    "challenged_operations": challenged,
                    "fault_milestones": milestones,
                    "counters": dataclasses.asdict(counters),
                    "p95_ms": 1.0 if scenario.startswith("coordinated-") else 0.0,
                    "successful_throughput_rps": (
                        100.0 if scenario.startswith("coordinated-") else 0.0
                    ),
                    "recovery_clock": (
                        None if recovery_clock is None else recovery_clock.to_dict()
                    ),
                }
            )
    events_payload = b"".join(canonical_bytes(item) + b"\n" for item in event_records)
    (root / "events.jsonl").write_bytes(events_payload)
    events_digest = hashlib.sha256(events_payload).hexdigest()
    for item in event_records:
        results.append(
            ScenarioResult(
                str(item["scenario_id"]),
                int(item["repetition"]),
                ScenarioState.COMPLETE_PASS,
                int(item["challenged_operations"]),
                int(item["fault_milestones"]),
                1.0,
                CorrectnessCounters.from_dict(item["counters"]),
                "events.jsonl",
                events_digest,
                p95_ms=float(item["p95_ms"]),
                successful_throughput_rps=float(item["successful_throughput_rps"]),
                recovery_clock=(
                    None
                    if item["recovery_clock"] is None
                    else RecoveryClock.from_dict(item["recovery_clock"])
                ),
            )
        )
    samples_payload = b"".join(canonical_bytes(sample) + b"\n" for sample in sample_records)
    (root / "samples.jsonl").write_bytes(samples_payload)
    grouped_samples: dict[str, list[dict[str, object]]] = {}
    for sample in sample_records:
        grouped_samples.setdefault(str(sample["operation_digest"]), []).append(sample)
    oracle_payload = b"".join(
        canonical_bytes(
            {
                "operation_digest": digest,
                "deliveries": len(group),
                "client_successes": sum(bool(sample["success"]) for sample in group),
                "transport_failures": sum(bool(sample["transport_failure"]) for sample in group),
                "audit_events": sum(bool(sample["success"]) for sample in group),
                "request_traces": sum(bool(sample["success"]) for sample in group),
                "usage_events": 1 if any(sample["success"] for sample in group) else 0,
                "successful_usage_events": (1 if any(sample["success"] for sample in group) else 0),
            }
        )
        + b"\n"
        for digest, group in grouped_samples.items()
    )
    (root / "oracle.jsonl").write_bytes(oracle_payload)
    scenarios_payload = (
        canonical_bytes({"schema_version": 1, "results": [item.to_dict() for item in results]})
        + b"\n"
    )
    (root / "scenarios.json").write_bytes(scenarios_payload)
    summary_payload = (
        canonical_bytes(
            {
                "schema_version": 1,
                "state": "complete_pass",
                "candidate_id": selected.candidate_id,
                "preflight": {
                    "schema_version": 1,
                    "docker_server_version": "28.0.0",
                    "compose_version": "2.39.0",
                    "source_revision": selected.source_revision,
                    "source_tree_digest": selected.source_tree_digest,
                    "production_image_id": selected.production_image,
                    "evidence_image_id": selected.evidence_image,
                    "redis_image_id": selected.redis_primary_image.rsplit("@", 1)[-1],
                    "postgresql_image_id": selected.postgresql_image.rsplit("@", 1)[-1],
                    "free_disk_bytes": 10 * 1024**3,
                },
                "bootstrap": {
                    "schema_version": 1,
                    "migration_plan_id": "dmg_" + ("6" * 32),
                    "migration_checkpoint_revision": 1,
                    "source_nonempty_families": sorted(
                        family.value for family in DURABLE_COPY_FAMILIES
                    ),
                    "target_epoch": 1,
                    "migration_resumed": True,
                    "bootstrap_previewed": True,
                    "bootstrap_replayed": True,
                    "redis_replica_acknowledged": True,
                    "migration_duration_ms": 1.0,
                    "bootstrap_duration_ms": 1.0,
                    "redis_server_version": "8.2.1",
                    "postgresql_server_version": "17.6",
                },
                "resources": {
                    "project": "w4c-123456789abc",
                    "containers": [],
                    "volumes": [],
                    "networks": [],
                },
                "completed_unix_ns": 1,
                "scenario_count": len(results),
                "sample_count": selected.expected_sample_count,
                "oracle_count": len(grouped_samples),
            }
        )
        + b"\n"
    )
    (root / "summary.json").write_bytes(summary_payload)
    artifacts = tuple(
        sorted(
            (
                ("candidate.json", hashlib.sha256(candidate_payload).hexdigest()),
                ("events.jsonl", events_digest),
                ("oracle.jsonl", hashlib.sha256(oracle_payload).hexdigest()),
                ("samples.jsonl", hashlib.sha256(samples_payload).hexdigest()),
                ("scenarios.json", hashlib.sha256(scenarios_payload).hexdigest()),
                ("summary.json", hashlib.sha256(summary_payload).hexdigest()),
            )
        )
    )
    return RunManifest(
        run_id="w4c_" + ("2" * 32),
        candidate_id=selected.candidate_id,
        candidate_digest=selected.digest,
        source_revision=selected.source_revision,
        source_tree_digest=selected.source_tree_digest,
        production_image=selected.production_image,
        evidence_launcher_digest=selected.evidence_launcher_digest,
        status=ScenarioState.COMPLETE_PASS,
        results=tuple(results),
        artifacts=artifacts,
        complete=True,
    )


class CandidateContractTests(unittest.TestCase):
    def test_candidate_is_deterministic_strict_and_never_self_activates(self) -> None:
        topology = candidate()
        decoded = CandidateTopology.from_dict(topology.to_dict())
        self.assertEqual(decoded.digest, topology.digest)
        self.assertRegex(topology.candidate_id, r"^act_[0-9a-f]{32}$")
        self.assertTrue(CandidateVerifier.exact(topology, replica_count=2)(topology.candidate_id))
        self.assertFalse(CandidateVerifier.exact(topology, replica_count=2)("act_" + ("0" * 32)))
        self.assertEqual(topology.expected_sample_count, 28_704)

        raw = topology.to_dict()
        raw["unknown"] = True
        with self.assertRaises(EvidenceVerificationError):
            CandidateTopology.from_dict(raw)

        activated = dataclasses.replace(topology, activation_record=topology.candidate_id)
        self.assertNotEqual(activated.candidate_id, topology.candidate_id)
        self.assertEqual(
            CandidateTopology.from_dict(activated.to_dict()).activation_record,
            topology.candidate_id,
        )
        with self.assertRaisesRegex(EvidenceVerificationError, "activation"):
            dataclasses.replace(topology, activation_record="unverified")

    def test_invalid_enums_non_finite_numbers_and_zero_challenges_fail_closed(self) -> None:
        counters = CorrectnessCounters()
        with self.assertRaises(EvidenceVerificationError):
            ScenarioResult(
                REQUIRED_SCENARIOS[0], 1, "pass", 1, 1, 1.0, counters, "a.json", "a" * 64
            )
        with self.assertRaises(EvidenceVerificationError):
            ScenarioResult(
                REQUIRED_SCENARIOS[0],
                1,
                ScenarioState.COMPLETE_PASS,
                1,
                1,
                float("nan"),
                counters,
                "a.json",
                "a" * 64,
            )
        with self.assertRaisesRegex(EvidenceVerificationError, "clock"):
            ScenarioResult(
                "redis-restart",
                1,
                ScenarioState.COMPLETE_PASS,
                1,
                1,
                1.0,
                counters,
                "a.json",
                "a" * 64,
            )

        with workspace_temp_directory() as directory:
            root = Path(directory)
            run = manifest(root)
            first = dataclasses.replace(run.results[0], challenged_operations=0)
            invalid = dataclasses.replace(run, results=(first, *run.results[1:]))
            with self.assertRaisesRegex(EvidenceVerificationError, "scenario"):
                verify_run_manifest(invalid, candidate(), root)

    def test_missing_duplicate_failed_and_candidate_mismatch_deny_eligibility(self) -> None:
        with workspace_temp_directory() as directory:
            root = Path(directory)
            topology = candidate()
            run = manifest(root, topology)
            for changed in (
                dataclasses.replace(run, results=run.results[:-1]),
                dataclasses.replace(run, results=(*run.results[:-1], run.results[0])),
                dataclasses.replace(
                    run,
                    results=(
                        dataclasses.replace(run.results[0], state=ScenarioState.SKIPPED),
                        *run.results[1:],
                    ),
                ),
                dataclasses.replace(run, source_tree_digest="9" * 64),
                dataclasses.replace(
                    run,
                    results=(
                        dataclasses.replace(run.results[0], duration_ms=60_001),
                        *run.results[1:],
                    ),
                ),
            ):
                with self.assertRaises(EvidenceVerificationError):
                    verify_run_manifest(changed, topology, root)

    def test_performance_pair_regression_denies_eligibility(self) -> None:
        with workspace_temp_directory() as directory:
            root = Path(directory)
            topology = candidate()
            run = manifest(root, topology)
            results = list(run.results)
            index = next(
                index
                for index, result in enumerate(results)
                if result.scenario_id == "coordinated-target" and result.repetition == 1
            )
            results[index] = dataclasses.replace(
                results[index], p95_ms=1.21, successful_throughput_rps=84.9
            )
            with self.assertRaisesRegex(EvidenceVerificationError, "performance"):
                verify_run_manifest(
                    dataclasses.replace(run, results=tuple(results)), topology, root
                )

    def test_artifact_tampering_and_interrupted_atomic_reports_are_rejected(self) -> None:
        with workspace_temp_directory() as directory:
            root = Path(directory)
            topology = candidate()
            run = manifest(root, topology)
            self.assertTrue(verify_run_manifest(run, topology, root))
            self.assertTrue(
                verify_run_manifest(
                    run,
                    topology,
                    root,
                    expected_manifest_digest=run.digest,
                )
            )
            with self.assertRaisesRegex(EvidenceVerificationError, "pinned digest"):
                verify_run_manifest(
                    run,
                    topology,
                    root,
                    expected_manifest_digest="0" * 64,
                )
            (root / run.results[0].artifact_name).write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(EvidenceVerificationError, "tampered"):
                verify_run_manifest(run, topology, root)

            interrupted = root / "interrupted.json"
            interrupted.write_text('{"schema_version":', encoding="utf-8")
            with self.assertRaisesRegex(EvidenceVerificationError, "interrupted"):
                load_json(interrupted)

    def test_verifier_rejects_secret_artifact_even_when_its_digest_matches(self) -> None:
        with workspace_temp_directory() as directory:
            root = Path(directory)
            topology = candidate()
            run = manifest(root, topology)
            first = run.results[0]
            payload = b'{"password":"not-a-test-secret"}'
            (root / first.artifact_name).write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            results = tuple(
                dataclasses.replace(result, artifact_digest=digest) for result in run.results
            )
            artifacts = tuple(
                (name, digest if name == first.artifact_name else value)
                for name, value in run.artifacts
            )
            with self.assertRaisesRegex(EvidenceVerificationError, "secret"):
                verify_run_manifest(
                    dataclasses.replace(run, results=results, artifacts=artifacts),
                    topology,
                    root,
                )

    def test_verifier_cross_checks_scenario_artifact_semantics(self) -> None:
        with workspace_temp_directory() as directory:
            root = Path(directory)
            topology = candidate()
            run = manifest(root, topology)
            payload = canonical_bytes({"schema_version": 1, "results": []}) + b"\n"
            (root / "scenarios.json").write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            artifacts = tuple(
                (name, digest if name == "scenarios.json" else value)
                for name, value in run.artifacts
            )
            with self.assertRaisesRegex(EvidenceVerificationError, "semantic"):
                verify_run_manifest(
                    dataclasses.replace(run, artifacts=artifacts),
                    topology,
                    root,
                )

    def test_verifier_cross_checks_the_archived_candidate_semantics(self) -> None:
        with workspace_temp_directory() as directory:
            root = Path(directory)
            topology = candidate()
            run = manifest(root, topology)
            archived = dataclasses.replace(
                topology,
                activation_record="act_" + "9" * 32,
            )
            payload = canonical_bytes(archived.to_dict()) + b"\n"
            (root / "candidate.json").write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            artifacts = tuple(
                (name, digest if name == "candidate.json" else value)
                for name, value in run.artifacts
            )

            with self.assertRaisesRegex(EvidenceVerificationError, "Archived candidate"):
                verify_run_manifest(
                    dataclasses.replace(run, artifacts=artifacts),
                    topology,
                    root,
                )

    def test_verifier_rejects_semantically_forged_dependency_summary(self) -> None:
        with workspace_temp_directory() as directory:
            root = Path(directory)
            topology = candidate()
            run = manifest(root, topology)
            summary = load_json(root / "summary.json")
            assert isinstance(summary, dict) and isinstance(summary["bootstrap"], dict)
            summary["bootstrap"]["redis_server_version"] = "7.9.9"
            payload = canonical_bytes(summary) + b"\n"
            (root / "summary.json").write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            artifacts = tuple(
                (name, digest if name == "summary.json" else value) for name, value in run.artifacts
            )

            with self.assertRaisesRegex(EvidenceVerificationError, "Bootstrap"):
                verify_run_manifest(
                    dataclasses.replace(run, artifacts=artifacts),
                    topology,
                    root,
                )

    def test_verifier_binds_dependency_image_ids_to_candidate(self) -> None:
        with workspace_temp_directory() as directory:
            root = Path(directory)
            topology = candidate()
            run = manifest(root, topology)
            summary = load_json(root / "summary.json")
            assert isinstance(summary, dict) and isinstance(summary["preflight"], dict)
            summary["preflight"]["redis_image_id"] = "sha256:" + "9" * 64
            payload = canonical_bytes(summary) + b"\n"
            (root / "summary.json").write_bytes(payload)
            digest = hashlib.sha256(payload).hexdigest()
            artifacts = tuple(
                (name, digest if name == "summary.json" else value) for name, value in run.artifacts
            )

            with self.assertRaisesRegex(EvidenceVerificationError, "Preflight"):
                verify_run_manifest(
                    dataclasses.replace(run, artifacts=artifacts),
                    topology,
                    root,
                )

    def test_atomic_manifest_is_new_complete_and_round_trips_exactly(self) -> None:
        with workspace_temp_directory() as directory:
            root = Path(directory)
            run = manifest(root)
            path = root / "manifest.json"
            write_atomic_manifest(path, run)
            self.assertEqual(RunManifest.from_dict(load_json(path)), run)
            with self.assertRaises(EvidenceVerificationError):
                write_atomic_manifest(path, run)

    def test_report_writer_never_publishes_a_manifest_before_eligibility_passes(self) -> None:
        with workspace_temp_directory() as directory:
            base = Path(directory)
            scratch = base / "scratch"
            scratch.mkdir()
            topology = candidate()
            run = manifest(scratch, topology)
            writer = EvidenceReportWriter((base / "report").resolve())
            writer.write_json("candidate.json", load_json(scratch / "candidate.json"))
            writer.write_jsonl("events.jsonl", load_jsonl(scratch / "events.jsonl"))
            writer.write_jsonl("oracle.jsonl", load_jsonl(scratch / "oracle.jsonl"))
            writer.write_jsonl("samples.jsonl", load_jsonl(scratch / "samples.jsonl"))
            writer.write_json("scenarios.json", load_json(scratch / "scenarios.json"))
            writer.write_json("summary.json", load_json(scratch / "summary.json"))
            invalid = dataclasses.replace(
                run,
                results=(
                    dataclasses.replace(run.results[0], state=ScenarioState.COMPLETE_FAIL),
                    *run.results[1:],
                ),
            )
            with self.assertRaises(EvidenceVerificationError):
                writer.complete(invalid, topology)
            self.assertFalse((writer.root / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
