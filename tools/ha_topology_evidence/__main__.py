"""Closed command surface for isolated Omni Gateway HA evidence."""

from __future__ import annotations

import argparse
import asyncio
import base64
import json
import os
import secrets
import time
from pathlib import Path

from .bootstrap import bootstrap_candidate
from .contract import (
    CandidateTopology,
    EvidenceVerificationError,
    RunManifest,
    ScenarioResult,
    ScenarioState,
    _read_bounded_regular_file,
    load_json,
    verify_run_manifest,
)
from .lifecycle import LifecycleScenarioDriver
from .oracle import DurableOracle
from .report import EvidenceReportWriter
from .runner import MatrixRunner, opaque_run_id
from .scenarios import (
    CleanupScope,
    ComposeAction,
    HostController,
    cleanup_project_resources,
    create_cleanup_scope,
    run_preflight,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("preflight", "run"):
        command = commands.add_parser(name)
        command.add_argument("--candidate", type=Path, required=True)
        command.add_argument("--repository", type=Path, default=Path.cwd())
        command.add_argument("--project", required=True)
        command.add_argument("--evidence-image", required=True)
        if name == "run":
            command.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--candidate", type=Path, required=True)
    verify.add_argument("--manifest", type=Path, required=True)
    verify.add_argument("--expected-manifest-digest", required=True)
    cleanup = commands.add_parser("cleanup")
    cleanup.add_argument("--scope", type=Path, required=True)
    cleanup.add_argument("--cleanup-key", type=Path, required=True)
    return parser


def _candidate(path: Path) -> CandidateTopology:
    if (
        path.name != "candidate.json"
        or not path.is_absolute()
        or not path.is_file()
        or path.is_symlink()
    ):
        raise EvidenceVerificationError("Candidate must be an absolute candidate.json path.")
    return CandidateTopology.from_dict(load_json(path))


def _compose_environment(
    candidate: CandidateTopology,
    *,
    candidate_path: Path,
    evidence_image: str,
) -> dict[str, str]:
    def token(size: int) -> str:
        return base64.urlsafe_b64encode(secrets.token_bytes(size)).decode().rstrip("=")

    return {
        "EVIDENCE_IMAGE": evidence_image,
        "OMNI_EVIDENCE_IMAGE": candidate.evidence_image,
        "PRODUCTION_IMAGE": candidate.production_image,
        "REDIS_IMAGE": candidate.redis_primary_image,
        "POSTGRES_IMAGE": candidate.postgresql_image,
        "EVIDENCE_RUN_DIR": str(candidate_path.resolve().parent),
        "EVIDENCE_NAMESPACE": "w4c-evidence-" + candidate.digest[:16],
        "EVIDENCE_DEPLOYMENT_ID": "w4c-evidence-" + candidate.digest[:16],
        "EVIDENCE_COORDINATION_KEY": token(32),
        "EVIDENCE_PANEL_PASSWORD": token(24),
        "EVIDENCE_API_KEY": "sk-ogw-" + token(32),
        "EVIDENCE_SETUP_TOKEN": token(24),
        "EVIDENCE_CONTROL_TOKEN": token(32),
        "EVIDENCE_SOURCE_REVISION": candidate.source_revision,
        "EVIDENCE_SOURCE_TREE_DIGEST": candidate.source_tree_digest,
        "EVIDENCE_LAUNCHER_DIGEST": candidate.evidence_launcher_digest,
        "EVIDENCE_MIGRATION_MANIFEST_CHECKSUM": candidate.migration_manifest_checksum,
        "EVIDENCE_REPLICA_COUNT": "2",
        "APP_A_PORT": "14283",
        "APP_B_PORT": "14284",
        "FIXTURE_CONTROL_PORT": "18081",
        "REDIS_DIRECT_PORT": "16381",
        "REDIS_STANDBY_DIRECT_PORT": "16382",
        "POSTGRES_DIRECT_PORT": "15434",
    }


def _write_cleanup_authority(output: Path, project: str) -> tuple[Path, Path, CleanupScope, bytes]:
    parent = output.resolve().parent
    if not parent.is_dir():
        raise EvidenceVerificationError("Evidence output parent is unavailable.")
    scope_path = (parent / f".{project}.cleanup-scope.json").resolve()
    key_path = (parent / f".{project}.cleanup-key").resolve()
    if scope_path.exists() or key_path.exists():
        raise EvidenceVerificationError("Evidence cleanup authority already exists.")
    key = secrets.token_bytes(32)
    scope = create_cleanup_scope(project, key)
    try:
        with key_path.open("xb") as handle:
            handle.write(key)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(key_path, 0o600)
        with scope_path.open("xb") as handle:
            handle.write(
                json.dumps(scope.to_dict(), separators=(",", ":"), sort_keys=True).encode("ascii")
            )
            handle.write(b"\n")
            handle.flush()
            os.fsync(handle.fileno())
    except BaseException:
        key_path.unlink(missing_ok=True)
        scope_path.unlink(missing_ok=True)
        raise
    return scope_path, key_path, scope, key


def _load_cleanup_authority(scope_path: Path, key_path: Path) -> tuple[CleanupScope, bytes]:
    if not scope_path.is_absolute() or not key_path.is_absolute():
        raise EvidenceVerificationError("Cleanup authority paths must be absolute.")
    try:
        scope_value = json.loads(_read_bounded_regular_file(scope_path, 4096))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceVerificationError("Evidence cleanup scope is invalid.") from exc
    key = _read_bounded_regular_file(key_path, 32)
    if len(key) != 32:
        raise EvidenceVerificationError("Evidence cleanup key is invalid.")
    return CleanupScope.from_dict(scope_value), key


async def _execute_run(
    candidate: CandidateTopology,
    arguments: argparse.Namespace,
    controller: HostController,
    environment: dict[str, str],
    preflight,
) -> Path:
    repository = arguments.repository.resolve(strict=True)
    output = arguments.output.resolve()
    if repository != output and repository not in output.parents:
        raise EvidenceVerificationError("Evidence output must stay inside the source repository.")
    writer = EvidenceReportWriter(output)
    archived_candidate_digest = writer.write_json("candidate.json", candidate.to_dict())
    controller.compose(
        ComposeAction.UP,
        ("postgres", "redis-primary", "redis-standby", "fixture"),
    )
    bootstrap = await bootstrap_candidate(
        candidate,
        environment,
        host_postgresql_uri="postgresql://omni@127.0.0.1:15434/omni_evidence",
        host_redis_url="redis://127.0.0.1:16381/0",
    )
    controller.compose(ComposeAction.UP, ("app-a", "app-b"))
    app_a_url = "http://127.0.0.1:14283"
    app_b_url = "http://127.0.0.1:14284"
    for endpoint in (app_a_url, app_b_url):
        controller.wait_http(f"{endpoint}/ready")

    oracle = DurableOracle("postgresql://omni@127.0.0.1:15434/omni_evidence")
    lifecycle = LifecycleScenarioDriver(
        candidate,
        controller,
        environment,
        host_postgresql_uri="postgresql://omni@127.0.0.1:15434/omni_evidence",
        host_redis_url="redis://127.0.0.1:16381/0",
        app_a_url=app_a_url,
        app_b_url=app_b_url,
        api_key=environment["EVIDENCE_API_KEY"],
        oracle=oracle,
    )
    execution = await MatrixRunner(
        candidate,
        controller,
        oracle,
        app_a_url=app_a_url,
        app_b_url=app_b_url,
        api_key=environment["EVIDENCE_API_KEY"],
        lifecycle_hook=lifecycle.execute,
    ).execute(bootstrap)
    event_digest = writer.write_jsonl(
        "events.jsonl", (item.safe_event() for item in execution.observations)
    )
    sample_digest = writer.write_jsonl("samples.jsonl", execution.samples)
    oracle_digest = writer.write_jsonl("oracle.jsonl", execution.oracle_evidence)
    results = tuple(
        ScenarioResult(
            item.scenario_id,
            item.repetition,
            ScenarioState.COMPLETE_PASS,
            item.challenged_operations,
            item.fault_milestones,
            item.duration_ms,
            item.counters,
            "events.jsonl",
            event_digest,
            p95_ms=item.p95_ms,
            successful_throughput_rps=item.successful_throughput_rps,
            recovery_clock=item.recovery_clock,
        )
        for item in execution.observations
    )
    scenarios_digest = writer.write_json(
        "scenarios.json", {"schema_version": 1, "results": [item.to_dict() for item in results]}
    )
    resources = controller.project_resources()
    summary_digest = writer.write_json(
        "summary.json",
        {
            "schema_version": 1,
            "state": "complete_pass",
            "candidate_id": candidate.candidate_id,
            "preflight": preflight.safe_summary(),
            "bootstrap": bootstrap.safe_summary(),
            "resources": resources.safe_summary(),
            "completed_unix_ns": time.time_ns(),
            "scenario_count": len(results),
            "sample_count": len(execution.samples),
            "oracle_count": len(execution.oracle_evidence),
        },
    )
    artifacts = tuple(
        sorted(
            (
                ("candidate.json", archived_candidate_digest),
                ("events.jsonl", event_digest),
                ("oracle.jsonl", oracle_digest),
                ("samples.jsonl", sample_digest),
                ("scenarios.json", scenarios_digest),
                ("summary.json", summary_digest),
            )
        )
    )
    manifest = RunManifest(
        run_id=opaque_run_id(candidate),
        candidate_id=candidate.candidate_id,
        candidate_digest=candidate.digest,
        source_revision=candidate.source_revision,
        source_tree_digest=candidate.source_tree_digest,
        production_image=candidate.production_image,
        evidence_launcher_digest=candidate.evidence_launcher_digest,
        status=ScenarioState.COMPLETE_PASS,
        results=results,
        artifacts=artifacts,
        complete=True,
    )
    path = writer.complete(manifest, candidate)
    verify_run_manifest(manifest, candidate, path.parent)
    return path


async def _execute_with_total_timeout(
    candidate: CandidateTopology,
    arguments: argparse.Namespace,
    controller: HostController,
    environment: dict[str, str],
    preflight,
) -> Path:
    try:
        return await asyncio.wait_for(
            _execute_run(candidate, arguments, controller, environment, preflight),
            timeout=candidate.total_timeout_seconds,
        )
    except TimeoutError as exc:
        raise EvidenceVerificationError("Evidence run exceeded its total timeout.") from exc


def main(argv: list[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    try:
        if arguments.command == "cleanup":
            scope, key = _load_cleanup_authority(arguments.scope, arguments.cleanup_key)
            removed = cleanup_project_resources(scope, key)
            arguments.cleanup_key.unlink()
            arguments.scope.unlink()
            print(
                json.dumps(
                    {
                        "schema_version": 1,
                        "project": scope.project,
                        "removed": removed.safe_summary(),
                        "activation_eligible_for_review": False,
                        "state": "cleanup_complete",
                    },
                    separators=(",", ":"),
                    sort_keys=True,
                )
            )
            return 0
        candidate = _candidate(arguments.candidate)
        if arguments.command in {"preflight", "run"}:
            compose = Path(__file__).resolve().parents[2] / "deploy" / "evidence" / "compose.ha.yml"
            environment = _compose_environment(
                candidate,
                candidate_path=arguments.candidate,
                evidence_image=arguments.evidence_image,
            )
            controller = HostController(
                compose.resolve(),
                arguments.project,
                "http://127.0.0.1:18081",
                compose_environment=environment,
                control_token=environment["EVIDENCE_CONTROL_TOKEN"],
            )
            preflight = run_preflight(
                candidate,
                repository=arguments.repository.resolve(),
                controller=controller,
                evidence_image=arguments.evidence_image,
            )
            if arguments.command == "preflight":
                result = {
                    **preflight.safe_summary(),
                    "candidate_id": candidate.candidate_id,
                    "replica_count": 2,
                    "activation_eligible_for_review": False,
                    "state": "preflight_pass",
                }
            else:
                scope_path, key_path, cleanup_scope, cleanup_key = _write_cleanup_authority(
                    arguments.output, arguments.project
                )
                try:
                    manifest_path = asyncio.run(
                        _execute_with_total_timeout(
                            candidate,
                            arguments,
                            controller,
                            environment,
                            preflight,
                        )
                    )
                except BaseException:
                    try:
                        cleanup_project_resources(cleanup_scope, cleanup_key)
                    except BaseException as cleanup_error:
                        raise EvidenceVerificationError(
                            "Evidence run failed and authenticated cleanup also failed."
                        ) from cleanup_error
                    key_path.unlink(missing_ok=True)
                    scope_path.unlink(missing_ok=True)
                    raise
                result = {
                    "schema_version": 1,
                    "candidate_id": candidate.candidate_id,
                    "manifest": str(manifest_path),
                    "manifest_digest": RunManifest.from_dict(load_json(manifest_path)).digest,
                    "cleanup_scope": str(scope_path),
                    "cleanup_key": str(key_path),
                    "activation_eligible_for_review": True,
                    "state": "complete_pass",
                }
        else:
            manifest = (
                RunManifest.from_dict(load_json(arguments.manifest))
                if hasattr(arguments, "manifest")
                else None
            )
            if arguments.command == "verify":
                assert manifest is not None
                verify_run_manifest(
                    manifest,
                    candidate,
                    arguments.manifest.parent,
                    expected_manifest_digest=arguments.expected_manifest_digest,
                )
                result = {
                    "schema_version": 1,
                    "candidate_id": candidate.candidate_id,
                    "activation_eligible_for_review": True,
                    "manifest_digest": manifest.digest,
                    "state": "verified",
                }
        print(json.dumps(result, separators=(",", ":"), sort_keys=True))
        return 0
    except EvidenceVerificationError as exc:
        print(
            json.dumps(
                {"schema_version": 1, "state": "rejected", "reason": str(exc)},
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 2
    except Exception as exc:
        print(
            json.dumps(
                {"schema_version": 1, "state": "failed", "reason": type(exc).__name__},
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
