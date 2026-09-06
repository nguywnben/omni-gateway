"""Private process-death worker for the external HA bootstrap evidence."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from core.durable_migration_runner import MigrationRunner
from core.redis_state_store import RedisStateStore
from core.storage.durable_family_barrier import SQLiteSourceMutationBarrier
from core.storage.durable_family_postgresql import PostgreSQLDurableFamilyAdapter
from core.storage.durable_family_sqlite import SQLiteDurableFamilyAdapter
from core.storage.migration_postgresql import PostgreSQLMigrationCheckpointRepository
from core.storage.postgresql_manager import PostgreSQLManager

from .admin import CandidateAdmin, experimental_policy
from .contract import (
    CandidateTopology,
    CandidateVerifier,
    EvidenceVerificationError,
    _read_bounded_regular_file,
)


def _load_spec(path: Path) -> dict[str, object]:
    if not path.is_absolute():
        raise EvidenceVerificationError("Bootstrap worker spec must be absolute.")
    try:
        value = json.loads(_read_bounded_regular_file(path, 64 * 1024))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceVerificationError("Bootstrap worker spec is invalid.") from exc
    if not isinstance(value, dict):
        raise EvidenceVerificationError("Bootstrap worker spec is invalid.")
    return value


def _publish_milestone(spec_path: Path, value: object) -> None:
    milestone_value = str(value)
    milestone = Path(milestone_value)
    if (
        not milestone.is_absolute()
        or milestone.parent.resolve(strict=True) != spec_path.parent.resolve(strict=True)
        or milestone.exists()
    ):
        raise EvidenceVerificationError("Bootstrap worker milestone is invalid.")
    temporary = milestone.with_name(milestone.name + ".tmp")
    if temporary.exists():
        raise EvidenceVerificationError("Bootstrap worker milestone is invalid.")
    with temporary.open("xb") as handle:
        handle.write(b"durable-write-complete\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, milestone)


async def _migration(spec_path: Path, spec: dict[str, object]) -> None:
    required = {
        "source_path",
        "source_id",
        "target_id",
        "plan_id",
        "candidate_digest",
        "batch_size",
        "postgresql_uri",
        "milestone",
    }
    if set(spec) != required:
        raise EvidenceVerificationError("Migration interruption spec is invalid.")
    previous = os.environ.get("POSTGRESQL_URI")
    os.environ["POSTGRESQL_URI"] = str(spec["postgresql_uri"])
    manager = PostgreSQLManager()
    try:
        await manager.initialize()
        if manager._pool is None:
            raise EvidenceVerificationError("Migration interruption target is unavailable.")
        checkpoints = PostgreSQLMigrationCheckpointRepository(manager._pool)
        await checkpoints.initialize()
        runner = MigrationRunner(
            source=SQLiteDurableFamilyAdapter(
                Path(str(spec["source_path"])),
                instance_id=str(spec["source_id"]),
                revision=1,
            ),
            target=PostgreSQLDurableFamilyAdapter(
                manager._pool,
                instance_id=str(spec["target_id"]),
                revision=1,
            ),
            checkpoints=checkpoints,
            source_barrier=SQLiteSourceMutationBarrier(Path(str(spec["source_path"]))),
            integrity_key=hashlib.sha256(str(spec["candidate_digest"]).encode("ascii")).digest(),
            batch_size=int(spec["batch_size"]),
        )
        await runner.copy_next(str(spec["plan_id"]), now=datetime.now(timezone.utc))
        _publish_milestone(spec_path, spec["milestone"])
        await asyncio.Event().wait()
    finally:
        await manager.close()
        if previous is None:
            os.environ.pop("POSTGRESQL_URI", None)
        else:
            os.environ["POSTGRESQL_URI"] = previous


async def _bootstrap(spec_path: Path, spec: dict[str, object]) -> None:
    required = {
        "candidate",
        "environment",
        "plan_id",
        "postgresql_uri",
        "redis_url",
        "milestone",
    }
    if set(spec) != required or not isinstance(spec.get("environment"), dict):
        raise EvidenceVerificationError("Bootstrap interruption spec is invalid.")
    candidate = CandidateTopology.from_dict(spec["candidate"])
    environment = {str(key): str(value) for key, value in spec["environment"].items()}
    previous = os.environ.get("POSTGRESQL_URI")
    os.environ["POSTGRESQL_URI"] = str(spec["postgresql_uri"])
    manager = PostgreSQLManager()
    store: RedisStateStore | None = None
    try:
        await manager.initialize()
        policy = experimental_policy(environment, candidate, replica_count=2)
        store = RedisStateStore(
            str(spec["redis_url"]), deployment_namespace=policy.coordination_namespace
        )
        result = await CandidateAdmin(
            policy,
            manager,
            store,
            CandidateVerifier.exact(candidate, replica_count=2),
        ).bootstrap(str(spec["plan_id"]), apply=True)
        if not result.applied or result.binding is None:
            raise EvidenceVerificationError("Bootstrap interruption write did not apply.")
        _publish_milestone(spec_path, spec["milestone"])
        await asyncio.Event().wait()
    finally:
        if store is not None:
            await store.close()
        await manager.close()
        if previous is None:
            os.environ.pop("POSTGRESQL_URI", None)
        else:
            os.environ["POSTGRESQL_URI"] = previous


async def _main(spec_path: Path, phase: str) -> None:
    spec = _load_spec(spec_path)
    if phase == "migration":
        await _migration(spec_path, spec)
    elif phase == "bootstrap":
        await _bootstrap(spec_path, spec)
    else:
        raise EvidenceVerificationError("Bootstrap worker phase is invalid.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--phase", choices=("migration", "bootstrap"), required=True)
    arguments = parser.parse_args()
    asyncio.run(_main(arguments.spec, arguments.phase))
