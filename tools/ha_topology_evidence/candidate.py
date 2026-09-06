"""Create one immutable external-evidence candidate from a clean committed tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from pathlib import Path

from core.durable_migration import DURABLE_MANIFEST_CHECKSUM

from .contract import (
    CandidateTopology,
    EvidenceVerificationError,
    _read_bounded_regular_file,
    canonical_bytes,
)
from .scenarios import source_tree_digest


def launcher_digest(repository: Path) -> str:
    roots = (repository / "tools" / "ha_topology_evidence",)
    paths = sorted(
        path
        for root in roots
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )
    resolved_repository = repository.resolve(strict=True)
    if not paths or any(
        path.is_symlink() or resolved_repository not in path.resolve(strict=True).parents
        for path in paths
    ):
        raise EvidenceVerificationError("Evidence launcher inventory is invalid.")
    digest = hashlib.sha256(b"omni-ha-evidence-launcher-v1\x00")
    for path in paths:
        relative = path.relative_to(repository).as_posix().encode("utf-8")
        payload = _read_bounded_regular_file(path, 16 * 1024 * 1024)
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def verify_launcher_package(candidate: CandidateTopology, repository: Path) -> None:
    """Fail unless the executing launcher package matches the frozen candidate."""

    if type(candidate) is not CandidateTopology or launcher_digest(repository) != (
        candidate.evidence_launcher_digest
    ):
        raise EvidenceVerificationError("Executing evidence launcher does not match candidate.")


def freeze_candidate(
    repository: Path,
    *,
    production_image: str,
    evidence_image: str,
    redis_image: str,
    postgresql_image: str,
    activation_record: str | None = None,
) -> CandidateTopology:
    if not repository.is_absolute() or not repository.is_dir():
        raise EvidenceVerificationError("Candidate repository is invalid.")
    try:
        revision = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repository,
            check=True,
            capture_output=True,
            text=True,
            timeout=30,
            shell=False,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise EvidenceVerificationError("Candidate revision is unavailable.") from exc
    return CandidateTopology(
        profile="redis8-postgres17-two-replicas",
        source_revision=revision,
        source_tree_digest=source_tree_digest(repository, revision),
        production_image=production_image,
        evidence_image=evidence_image,
        evidence_launcher_digest=launcher_digest(repository),
        redis_primary_image=redis_image,
        redis_standby_image=redis_image,
        postgresql_image=postgresql_image,
        migration_manifest_checksum=DURABLE_MANIFEST_CHECKSUM,
        activation_record=activation_record,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--production-image", required=True)
    parser.add_argument("--evidence-image", required=True)
    parser.add_argument("--redis-image", required=True)
    parser.add_argument("--postgresql-image", required=True)
    parser.add_argument("--activation-record")
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        output = arguments.output.resolve()
        if output.name != "candidate.json" or output.exists() or not output.parent.is_dir():
            raise EvidenceVerificationError("Candidate output must be a new candidate.json file.")
        candidate = freeze_candidate(
            arguments.repository.resolve(),
            production_image=arguments.production_image,
            evidence_image=arguments.evidence_image,
            redis_image=arguments.redis_image,
            postgresql_image=arguments.postgresql_image,
            activation_record=arguments.activation_record,
        )
        payload = canonical_bytes(candidate.to_dict()) + b"\n"
        with output.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        print(
            json.dumps(
                {"candidate_id": candidate.candidate_id, "state": "frozen"},
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 0
    except EvidenceVerificationError as exc:
        print(
            json.dumps(
                {"state": "rejected", "reason": str(exc)},
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
