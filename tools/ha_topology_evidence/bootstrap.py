"""Synthetic SQLite-to-PostgreSQL migration and candidate binding bootstrap."""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
import shutil
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Mapping
from urllib.parse import urlsplit

import redis.asyncio as redis_asyncio
from core.audit import create_audit_event
from core.durable_migration import DURABLE_COPY_FAMILIES, MigrationPhase
from core.durable_migration_runner import MigrationRunner
from core.identity import ManagementRole
from core.redis_state_store import RedisStateStore
from core.request_trace_service import RequestTraceCollector
from core.storage.audit_postgresql import PostgreSQLAuditRepository
from core.storage.audit_sqlite import SQLiteAuditRepository
from core.storage.durable_family_barrier import SQLiteSourceMutationBarrier
from core.storage.durable_family_postgresql import PostgreSQLDurableFamilyAdapter
from core.storage.durable_family_sqlite import SQLiteDurableFamilyAdapter
from core.storage.identity_postgresql import PostgreSQLIdentityRepository
from core.storage.identity_sqlite import SQLiteIdentityRepository
from core.storage.migration_postgresql import PostgreSQLMigrationCheckpointRepository
from core.storage.migration_sqlite import SQLiteMigrationCheckpointRepository
from core.storage.postgresql_manager import PostgreSQLManager
from core.storage.request_trace_postgresql import PostgreSQLRequestTraceRepository
from core.storage.request_trace_sqlite import SQLiteRequestTraceRepository
from core.storage.sqlite_manager import SQLiteManager
from core.storage.usage_ledger_postgresql import PostgreSQLUsageLedgerRepository
from core.storage.usage_ledger_sqlite import SQLiteUsageLedgerRepository
from core.usage_ledger import (
    USAGE_LEDGER_SCHEMA_VERSION,
    BudgetReservationRequest,
    UsageLedgerEntry,
)
from core.virtual_keys import VirtualKey

from .admin import CandidateAdmin, experimental_policy
from .contract import CandidateTopology, CandidateVerifier, EvidenceVerificationError

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


async def _interrupt_after_durable_write(
    phase: str,
    directory: Path,
    spec: dict[str, object],
) -> None:
    """Terminate a separate owner only after it confirms its authoritative write."""

    if phase not in {"migration", "bootstrap"}:
        raise EvidenceVerificationError("Process interruption phase is invalid.")
    spec_path = directory / f"{phase}-worker-spec.json"
    milestone = directory / f"{phase}-durable-write.milestone"
    if spec_path.exists() or milestone.exists():
        raise EvidenceVerificationError("Process interruption artifacts already exist.")
    payload = {**spec, "milestone": str(milestone.resolve())}
    with spec_path.open("xb") as handle:
        handle.write(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(spec_path, 0o600)
    process = await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "tools.ha_topology_evidence.bootstrap_worker",
        "--spec",
        str(spec_path.resolve()),
        "--phase",
        phase,
        cwd=str(_REPOSITORY_ROOT),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
    )
    try:
        deadline = time.monotonic() + 60.0
        while time.monotonic() < deadline:
            if milestone.exists():
                if milestone.read_bytes() != b"durable-write-complete\n":
                    raise EvidenceVerificationError("Process interruption milestone is invalid.")
                break
            if process.returncode is not None:
                raise EvidenceVerificationError(
                    "Process interruption owner exited before its durable-write boundary."
                )
            await asyncio.sleep(0.05)
        else:
            raise EvidenceVerificationError("Process interruption milestone timed out.")
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=10.0)
        except TimeoutError:
            process.kill()
            await asyncio.wait_for(process.wait(), timeout=10.0)
        if process.returncode == 0:
            raise EvidenceVerificationError("Process interruption did not terminate the owner.")
    finally:
        if process.returncode is None:
            process.kill()
            await process.wait()
        spec_path.unlink(missing_ok=True)
        milestone.unlink(missing_ok=True)


@dataclass(frozen=True, slots=True)
class BootstrapResult:
    migration_plan_id: str
    migration_checkpoint_revision: int
    source_nonempty_families: tuple[str, ...]
    target_epoch: int
    migration_resumed: bool
    bootstrap_previewed: bool
    bootstrap_replayed: bool
    redis_replica_acknowledged: bool
    migration_started_ns: int
    migration_completed_ns: int
    bootstrap_started_ns: int
    bootstrap_completed_ns: int
    redis_server_version: str
    postgresql_server_version: str

    def __post_init__(self) -> None:
        if not (
            0
            < self.migration_started_ns
            <= self.migration_completed_ns
            <= self.bootstrap_started_ns
            <= self.bootstrap_completed_ns
        ):
            raise EvidenceVerificationError("Bootstrap evidence chronology is invalid.")
        for version in (self.redis_server_version, self.postgresql_server_version):
            if (
                not isinstance(version, str)
                or not 1 <= len(version) <= 128
                or any(ord(character) < 32 or ord(character) > 126 for character in version)
            ):
                raise EvidenceVerificationError("Dependency server version is invalid.")

    def safe_summary(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "migration_plan_id": self.migration_plan_id,
            "migration_checkpoint_revision": self.migration_checkpoint_revision,
            "source_nonempty_families": sorted(self.source_nonempty_families),
            "target_epoch": self.target_epoch,
            "migration_resumed": self.migration_resumed,
            "bootstrap_previewed": self.bootstrap_previewed,
            "bootstrap_replayed": self.bootstrap_replayed,
            "redis_replica_acknowledged": self.redis_replica_acknowledged,
            "migration_duration_ms": (self.migration_completed_ns - self.migration_started_ns)
            / 1_000_000,
            "bootstrap_duration_ms": (self.bootstrap_completed_ns - self.bootstrap_started_ns)
            / 1_000_000,
            "redis_server_version": self.redis_server_version,
            "postgresql_server_version": self.postgresql_server_version,
        }


def _identifier(prefix: str, candidate: CandidateTopology, label: str) -> str:
    digest = hashlib.sha256(
        b"omni-ha-evidence-bootstrap-v1\x00"
        + candidate.digest.encode("ascii")
        + b"\x00"
        + label.encode("ascii")
    ).hexdigest()
    return f"{prefix}_{digest[:32]}"


async def _initialize_sqlite_source(directory: Path) -> tuple[SQLiteManager, Path]:
    previous = os.environ.get("CREDENTIALS_DIR")
    os.environ["CREDENTIALS_DIR"] = str(directory)
    manager = SQLiteManager()
    try:
        await manager.initialize()
    finally:
        if previous is None:
            os.environ.pop("CREDENTIALS_DIR", None)
        else:
            os.environ["CREDENTIALS_DIR"] = previous
    path = directory / "credentials.db"
    bootstrap_now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    identity = SQLiteIdentityRepository(path, clock=lambda: bootstrap_now)
    audit = SQLiteAuditRepository(path, cursor_signing_key=b"a" * 32)
    traces = SQLiteRequestTraceRepository(path, cursor_signing_key=b"t" * 32)
    usage = SQLiteUsageLedgerRepository(str(path))
    for repository in (
        identity,
        audit,
        traces,
        usage,
        SQLiteMigrationCheckpointRepository(path),
    ):
        await repository.initialize()
    await identity.create_oidc_identity(
        issuer="https://synthetic-idp.invalid",
        subject="migration-user",
        role=ManagementRole.VIEWER,
    )
    await manager.set_config("evidence_migration_seed", {"schema_version": 1, "synthetic": True})
    virtual_key = VirtualKey(
        id="vk_migration",
        name="synthetic-migration",
        key_hash=hashlib.sha256(b"synthetic-migration-key").hexdigest(),
        key_preview="synthetic...tion",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp(),
        budget_daily_usd=1.0,
        allowed_models=["omni-evidence-model"],
    )
    await manager.set_config("virtual_keys", [virtual_key.to_storage_dict()])
    credential = {
        "provider": "ollama",
        "credential_type": "connection",
        "base_url": "http://fixture:8080",
        "api_key": "",
        "credential_label": "synthetic-migration-source",
        "connection_fingerprint": hashlib.sha256(b"synthetic-migration-source").hexdigest(),
        "model_ids": ["omni-evidence-model"],
        "created_at": "2026-01-01T00:00:00+00:00",
    }
    if not await manager.store_credential(
        "synthetic-provider.json", credential, mode="code_assist"
    ) or not await manager.store_credential("synthetic-primary.json", credential, mode="primary"):
        raise EvidenceVerificationError("Synthetic source credentials could not be created.")
    now = bootstrap_now
    await audit.append(
        create_audit_event(
            request_id="evidence-migration-audit",
            actor_type="system",
            actor_identifier="synthetic-migration",
            action="config.update",
            target_type="configuration",
            target_identifier="synthetic-migration",
            outcome="succeeded",
            change_codes=("settings_changed",),
            fingerprint_key=b"a" * 32,
            occurred_at=now,
        )
    )
    collector = RequestTraceCollector("evidence-migration-trace", "openai_chat")
    collector.record(
        category="routing",
        action="selected",
        result="succeeded",
        reason="healthy_candidate",
        provider="ollama",
        model="omni-evidence-model",
    )
    await traces.append(collector.complete(status_code=200))
    timestamp = now.timestamp()
    await usage.append_usage(
        UsageLedgerEntry(
            schema_version=USAGE_LEDGER_SCHEMA_VERSION,
            event_id="use_" + "a" * 32,
            occurred_at=timestamp,
            credential_ref="synthetic-provider.json",
            request_id="evidence-migration-usage",
            model="omni-evidence-model",
            provider="ollama",
            status_code=200,
            success=True,
            input_tokens=8,
            output_tokens=4,
            total_tokens=12,
            cached_tokens=0,
            reasoning_tokens=0,
            estimated_input_tokens=8,
            estimated_tokens_saved=0,
            compressed_messages=0,
            quality_profile="quality",
            quality_policy_revision=1,
            compression_reason="disabled",
            latency_ms=1,
            retry_count=0,
            cost_nanos=0,
            api_key_id="vk_evidence",
        )
    )
    reservation = BudgetReservationRequest(
        schema_version=USAGE_LEDGER_SCHEMA_VERSION,
        reservation_id="qrs_" + "b" * 32,
        key_id="vk_evidence",
        created_at=timestamp,
        expires_at=timestamp + 60,
        estimated_tokens=12,
        estimated_cost_nanos=1,
        daily_budget_nanos=100,
        monthly_budget_nanos=1_000,
    )
    decision = await usage.reserve_budget(reservation)
    if not decision.accepted:
        raise EvidenceVerificationError("Synthetic budget reservation could not be created.")
    await usage.release_reservation(reservation.reservation_id, transitioned_at=timestamp + 1)
    return manager, path


async def bootstrap_candidate(
    candidate: CandidateTopology,
    environment: Mapping[str, str],
    *,
    host_postgresql_uri: str,
    host_redis_url: str,
) -> BootstrapResult:
    """Create only synthetic source state, migrate every family, and bind the real target."""

    postgresql = urlsplit(host_postgresql_uri)
    redis = urlsplit(host_redis_url)
    if (
        postgresql.scheme not in {"postgresql", "postgres"}
        or postgresql.hostname != "127.0.0.1"
        or postgresql.port is None
        or postgresql.username != "omni"
        or postgresql.password is not None
        or postgresql.path != "/omni_evidence"
        or postgresql.query
        or postgresql.fragment
    ):
        raise EvidenceVerificationError("Bootstrap PostgreSQL endpoint is invalid.")
    if (
        redis.scheme != "redis"
        or redis.hostname != "127.0.0.1"
        or redis.port is None
        or redis.username is not None
        or redis.password is not None
        or redis.path != "/0"
        or redis.query
        or redis.fragment
    ):
        raise EvidenceVerificationError("Bootstrap Redis endpoint must be loopback-only.")
    source_root = Path(tempfile.mkdtemp(prefix="omni-w4c-source-"))
    source_manager: SQLiteManager | None = None
    target_manager: PostgreSQLManager | None = None
    store: RedisStateStore | None = None
    try:
        source_manager, source_path = await _initialize_sqlite_source(source_root)
        target_environment = {
            **environment,
            "OMNI_RUNTIME_MODE": "coordinated",
            "WORKERS": "1",
            "OMNI_REPLICA_COUNT": "1",
            "POSTGRESQL_URI": host_postgresql_uri,
            "REDIS_URL": host_redis_url,
            "OMNI_COORDINATION_NAMESPACE": environment["EVIDENCE_NAMESPACE"],
            "OMNI_DEPLOYMENT_ID": environment["EVIDENCE_DEPLOYMENT_ID"],
            "OMNI_COORDINATION_KEY": environment["EVIDENCE_COORDINATION_KEY"],
            "OMNI_COORDINATION_EPOCH": environment.get("EVIDENCE_EPOCH", "1"),
        }
        previous_pg = os.environ.get("POSTGRESQL_URI")
        os.environ["POSTGRESQL_URI"] = host_postgresql_uri
        target_manager = PostgreSQLManager()
        try:
            await target_manager.initialize()
        finally:
            if previous_pg is None:
                os.environ.pop("POSTGRESQL_URI", None)
            else:
                os.environ["POSTGRESQL_URI"] = previous_pg
        pool = target_manager._pool
        if pool is None:
            raise EvidenceVerificationError("PostgreSQL target did not initialize.")
        async with pool.acquire() as connection:
            server_version_number = await connection.fetchval(
                "SELECT current_setting('server_version_num')"
            )
            postgresql_server_version = await connection.fetchval(
                "SELECT current_setting('server_version')"
            )
        if not str(server_version_number).startswith("17"):
            raise EvidenceVerificationError("PostgreSQL evidence topology must use major 17.")
        for repository in (
            PostgreSQLIdentityRepository(
                pool,
                clock=lambda: datetime(2026, 1, 1, tzinfo=timezone.utc),
            ),
            PostgreSQLAuditRepository(pool, cursor_signing_key=b"a" * 32),
            PostgreSQLRequestTraceRepository(pool, cursor_signing_key=b"t" * 32),
            PostgreSQLUsageLedgerRepository(pool),
            PostgreSQLMigrationCheckpointRepository(pool),
        ):
            await repository.initialize()

        source_id = _identifier("ins", candidate, "source")
        target_id = _identifier("ins", candidate, "target")
        plan_id = _identifier("dmg", candidate, "plan")
        barrier_id = _identifier("bar", candidate, "barrier")
        source = SQLiteDurableFamilyAdapter(source_path, instance_id=source_id, revision=1)
        target = PostgreSQLDurableFamilyAdapter(pool, instance_id=target_id, revision=1)
        empty_families = []
        for family in DURABLE_COPY_FAMILIES:
            first_page = await source.read_page(family=family, offset=0, limit=1)
            if first_page.is_complete and not first_page.records:
                empty_families.append(family)
        empty = tuple(empty_families)
        barrier = SQLiteSourceMutationBarrier(source_path)
        await barrier.activate(
            plan_id=plan_id,
            barrier_id=barrier_id,
            source_instance_id=source_id,
        )
        checkpoints = PostgreSQLMigrationCheckpointRepository(pool)
        await checkpoints.initialize()
        runner = MigrationRunner(
            source=source,
            target=target,
            checkpoints=checkpoints,
            source_barrier=barrier,
            integrity_key=hashlib.sha256(candidate.digest.encode("ascii")).digest(),
            batch_size=candidate.reconciliation_page_size,
        )
        now = datetime.now(timezone.utc)
        migration_started_ns = time.monotonic_ns()
        await runner.start(
            plan_id=plan_id,
            source_barrier_id=barrier_id,
            explicitly_empty_families=empty,
            now=now,
        )
        # A separate process commits one copy/checkpoint page, publishes only a
        # local milestone, and is then terminated before it can return to its caller.
        await _interrupt_after_durable_write(
            "migration",
            source_root,
            {
                "source_path": str(source_path.resolve()),
                "source_id": source_id,
                "target_id": target_id,
                "plan_id": plan_id,
                "candidate_digest": candidate.digest,
                "batch_size": candidate.reconciliation_page_size,
                "postgresql_uri": host_postgresql_uri,
            },
        )
        checkpoint = await checkpoints.get(plan_id)
        if checkpoint is None or checkpoint.revision <= 1:
            raise EvidenceVerificationError(
                "Migration process death did not leave a resumable checkpoint."
            )
        runner = MigrationRunner(
            source=source,
            target=target,
            checkpoints=checkpoints,
            source_barrier=barrier,
            integrity_key=hashlib.sha256(candidate.digest.encode("ascii")).digest(),
            batch_size=candidate.reconciliation_page_size,
        )
        for page in range(1, candidate.reconciliation_page_limit):
            if checkpoint.phase is MigrationPhase.VERIFYING:
                break
            checkpoint = await runner.copy_next(plan_id, now=now + timedelta(seconds=page + 1))
        else:
            raise EvidenceVerificationError("Synthetic migration exceeded its page limit.")
        checkpoint = await runner.verify(
            plan_id, now=now + timedelta(seconds=candidate.reconciliation_page_limit + 1)
        )
        checkpoint = await runner.activate_target(
            plan_id,
            expected_revision=checkpoint.revision,
            now=now + timedelta(seconds=candidate.reconciliation_page_limit + 2),
        )
        migration_completed_ns = time.monotonic_ns()

        policy = experimental_policy(target_environment, candidate, replica_count=2)
        verifier = CandidateVerifier.exact(candidate, replica_count=2)
        store = RedisStateStore(
            host_redis_url,
            deployment_namespace=policy.coordination_namespace,
        )
        admin = CandidateAdmin(policy, target_manager, store, verifier)
        bootstrap_started_ns = time.monotonic_ns()
        preview = await admin.bootstrap(plan_id, apply=False)
        if preview.applied or preview.binding is None or not preview.prerequisite.eligible:
            raise EvidenceVerificationError("Candidate bootstrap preview is invalid.")
        await store.close()
        store = None
        await _interrupt_after_durable_write(
            "bootstrap",
            source_root,
            {
                "candidate": candidate.to_dict(),
                "environment": target_environment,
                "plan_id": plan_id,
                "postgresql_uri": host_postgresql_uri,
                "redis_url": host_redis_url,
            },
        )
        store = RedisStateStore(
            host_redis_url,
            deployment_namespace=policy.coordination_namespace,
        )
        replay = await CandidateAdmin(policy, target_manager, store, verifier).bootstrap(
            plan_id, apply=True
        )
        if not replay.applied or replay.binding is None:
            raise EvidenceVerificationError("Candidate bootstrap replay did not converge.")
        result = replay
        primary = redis_asyncio.from_url(host_redis_url, decode_responses=False)
        standby = redis_asyncio.from_url("redis://127.0.0.1:16382/0", decode_responses=False)
        try:
            server = await primary.info("server")
            redis_server_version = str(server.get("redis_version", ""))
            if not redis_server_version.startswith("8."):
                raise EvidenceVerificationError("Redis evidence topology must use major 8.")
            if int(await primary.wait(1, 5_000)) < 1:
                raise EvidenceVerificationError(
                    "Redis standby did not acknowledge bootstrap state."
                )
            role = await standby.role()
            if not role or role[0] not in {b"slave", "slave"}:
                raise EvidenceVerificationError("Redis standby role is invalid before the run.")
        finally:
            await primary.aclose()
            await standby.aclose()
        bootstrap_completed_ns = time.monotonic_ns()
        return BootstrapResult(
            plan_id,
            checkpoint.revision,
            tuple(family.value for family in DURABLE_COPY_FAMILIES if family not in empty),
            result.binding.fencing_epoch,
            True,
            True,
            True,
            True,
            migration_started_ns,
            migration_completed_ns,
            bootstrap_started_ns,
            bootstrap_completed_ns,
            redis_server_version,
            str(postgresql_server_version),
        )
    finally:
        if store is not None:
            await store.close()
        if target_manager is not None:
            await target_manager.close()
        if source_manager is not None:
            await source_manager.close()
        shutil.rmtree(source_root, ignore_errors=True)
