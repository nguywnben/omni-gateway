"""Strict, deterministic contracts for isolated external HA evidence."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import stat
from dataclasses import asdict, dataclass, replace
from enum import StrEnum
from pathlib import Path
from typing import Final

SCHEMA_VERSION: Final = 1
REQUIRED_SCENARIOS: Final = (
    "migration-interruption-resume",
    "bootstrap-interruption",
    "coordinated-baseline",
    "coordinated-target",
    "app-a-loss",
    "app-b-loss",
    "redis-app-a-interruption",
    "redis-app-b-interruption",
    "redis-both-paths-interruption",
    "redis-restart",
    "redis-standby-promotion",
    "stale-epoch",
    "partial-namespace",
    "postgresql-outage",
    "cancellation-unknown-outcome",
    "duplicate-delivery",
    "drain-reconcile-mark-ready",
    "standalone-rollback",
)
_PERFORMANCE_SCENARIOS: Final = frozenset({"coordinated-baseline", "coordinated-target"})
_HEX64 = re.compile(r"[0-9a-f]{64}")
_REVISION = re.compile(r"[0-9a-f]{40}")
_IMAGE = re.compile(r"(?:[a-z0-9][a-z0-9./:_-]*@)?sha256:[0-9a-f]{64}")
_PROFILE = re.compile(r"[a-z0-9](?:[a-z0-9-]{2,62}[a-z0-9])")
_RUN_ID = re.compile(r"w4c_[0-9a-f]{32}")
_ARTIFACT = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._/-]{0,127}")
_MAX_JSON_BYTES: Final = 64 * 1024 * 1024


class EvidenceVerificationError(ValueError):
    """A bounded evidence contract or artifact failed closed."""


class ScenarioState(StrEnum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETE_PASS = "complete_pass"
    COMPLETE_FAIL = "complete_fail"
    SKIPPED = "skipped"
    UNAVAILABLE = "unavailable"
    INTERRUPTED = "interrupted"
    NOT_EXERCISED = "not_exercised"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _closed(value: object, keys: frozenset[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != keys:
        raise EvidenceVerificationError(f"{label} has an invalid schema.")
    return value


def _integer(value: object, label: str, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise EvidenceVerificationError(f"{label} is invalid.")
    return value


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not _HEX64.fullmatch(value):
        raise EvidenceVerificationError(f"{label} is invalid.")
    return value


def _image(value: object, label: str) -> str:
    if not isinstance(value, str) or not _IMAGE.fullmatch(value):
        raise EvidenceVerificationError(f"{label} is not pinned by digest.")
    return value


def _image_id(value: str) -> str:
    """Return the immutable content ID from either an ID or name@digest reference."""

    return value.rsplit("@", 1)[-1]


def _artifact_name(value: object) -> str:
    if (
        not isinstance(value, str)
        or not _ARTIFACT.fullmatch(value)
        or value.startswith("/")
        or ".." in Path(value).parts
        or "\\" in value
    ):
        raise EvidenceVerificationError("Artifact name is invalid.")
    return value


@dataclass(frozen=True, slots=True)
class CandidateTopology:
    profile: str
    source_revision: str
    source_tree_digest: str
    production_image: str
    evidence_image: str
    evidence_launcher_digest: str
    redis_primary_image: str
    redis_standby_image: str
    postgresql_image: str
    migration_manifest_checksum: str
    activation_record: str | None = None
    required_scenarios: tuple[str, ...] = REQUIRED_SCENARIOS
    workers_per_replica: int = 1
    experimental_replica_counts: tuple[int, ...] = (1, 2)
    warmup_requests: int = 256
    measured_attempts: int = 4096
    concurrency: int = 16
    offered_rps: int = 32
    request_deadline_ms: int = 5000
    correctness_attempts: int = 256
    reconciliation_page_size: int = 256
    reconciliation_page_limit: int = 64
    scenario_timeout_seconds: int = 120
    total_timeout_seconds: int = 2700
    pair_repetitions: int = 3
    pair_seeds: tuple[int, ...] = (104_729, 130_363, 155_921)
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION or type(self.schema_version) is not int:
            raise EvidenceVerificationError("Candidate schema version is invalid.")
        if not isinstance(self.profile, str) or not _PROFILE.fullmatch(self.profile):
            raise EvidenceVerificationError("Candidate profile is invalid.")
        if not isinstance(self.source_revision, str) or not _REVISION.fullmatch(
            self.source_revision
        ):
            raise EvidenceVerificationError("Source revision is invalid.")
        _digest(self.source_tree_digest, "Source tree digest")
        _image(self.production_image, "Production image")
        _image(self.evidence_image, "Evidence image")
        _digest(self.evidence_launcher_digest, "Evidence launcher digest")
        primary = _image(self.redis_primary_image, "Redis primary image")
        standby = _image(self.redis_standby_image, "Redis standby image")
        if primary != standby:
            raise EvidenceVerificationError("Redis primary and standby images must be identical.")
        _image(self.postgresql_image, "PostgreSQL image")
        _digest(self.migration_manifest_checksum, "Migration manifest checksum")
        if self.activation_record is not None and (
            not isinstance(self.activation_record, str)
            or not re.fullmatch(r"act_[0-9a-f]{32}", self.activation_record)
        ):
            raise EvidenceVerificationError("Candidate activation record is invalid.")
        if self.required_scenarios != REQUIRED_SCENARIOS:
            raise EvidenceVerificationError("Required scenario inventory is invalid.")
        exact = {
            "workers_per_replica": (self.workers_per_replica, 1),
            "experimental_replica_counts": (self.experimental_replica_counts, (1, 2)),
            "warmup_requests": (self.warmup_requests, 256),
            "measured_attempts": (self.measured_attempts, 4096),
            "concurrency": (self.concurrency, 16),
            "offered_rps": (self.offered_rps, 32),
            "request_deadline_ms": (self.request_deadline_ms, 5000),
            "correctness_attempts": (self.correctness_attempts, 256),
            "reconciliation_page_size": (self.reconciliation_page_size, 256),
            "reconciliation_page_limit": (self.reconciliation_page_limit, 64),
            "scenario_timeout_seconds": (self.scenario_timeout_seconds, 120),
            "total_timeout_seconds": (self.total_timeout_seconds, 2700),
            "pair_repetitions": (self.pair_repetitions, 3),
            "pair_seeds": (self.pair_seeds, (104_729, 130_363, 155_921)),
        }
        if any(
            type(value) is not type(expected) or value != expected
            for value, expected in exact.values()
        ):
            raise EvidenceVerificationError("Candidate workload is not the frozen profile.")

    def to_dict(self) -> dict[str, object]:
        value = asdict(self)
        value["required_scenarios"] = list(self.required_scenarios)
        value["experimental_replica_counts"] = list(self.experimental_replica_counts)
        value["pair_seeds"] = list(self.pair_seeds)
        return value

    @classmethod
    def from_dict(cls, value: object) -> CandidateTopology:
        fields = frozenset(cls.__dataclass_fields__)
        raw = _closed(value, fields, "Candidate topology")
        try:
            return cls(
                **{
                    **raw,
                    "required_scenarios": tuple(raw["required_scenarios"]),
                    "experimental_replica_counts": tuple(raw["experimental_replica_counts"]),
                    "pair_seeds": tuple(raw["pair_seeds"]),
                }
            )
        except (TypeError, ValueError) as exc:
            raise EvidenceVerificationError("Candidate topology is invalid.") from exc

    @property
    def digest(self) -> str:
        return hashlib.sha256(
            b"omni-ha-candidate-v1\x00" + canonical_bytes(self.to_dict())
        ).hexdigest()

    @property
    def candidate_id(self) -> str:
        return "act_" + self.digest[:32]

    @property
    def expected_sample_count(self) -> int:
        """Return the exact HTTP-sample inventory implied by the frozen matrix."""

        return sum(
            sum(expected_sample_partitions(self, scenario).values())
            * (self.pair_repetitions if scenario in _PERFORMANCE_SCENARIOS else 1)
            for scenario in self.required_scenarios
        )


@dataclass(frozen=True, slots=True)
class CandidateVerifier:
    candidate: CandidateTopology
    source_revision: str
    source_tree_digest: str
    production_image: str
    evidence_image: str
    evidence_launcher_digest: str
    migration_manifest_checksum: str
    redis_primary_image: str
    redis_standby_image: str
    postgresql_image: str
    workers_per_replica: int
    replica_count: int

    @classmethod
    def exact(cls, candidate: CandidateTopology, *, replica_count: int) -> CandidateVerifier:
        return cls(
            candidate,
            candidate.source_revision,
            candidate.source_tree_digest,
            candidate.production_image,
            candidate.evidence_image,
            candidate.evidence_launcher_digest,
            candidate.migration_manifest_checksum,
            candidate.redis_primary_image,
            candidate.redis_standby_image,
            candidate.postgresql_image,
            candidate.workers_per_replica,
            replica_count,
        )

    @classmethod
    def from_environment(
        cls,
        candidate: CandidateTopology,
        environment: dict[str, str],
    ) -> CandidateVerifier:
        required = {
            "OMNI_EVIDENCE_SOURCE_REVISION",
            "OMNI_EVIDENCE_SOURCE_TREE_DIGEST",
            "OMNI_EVIDENCE_PRODUCTION_IMAGE",
            "OMNI_EVIDENCE_IMAGE",
            "OMNI_EVIDENCE_LAUNCHER_DIGEST",
            "OMNI_EVIDENCE_MIGRATION_MANIFEST_CHECKSUM",
            "OMNI_EVIDENCE_REDIS_IMAGE",
            "OMNI_EVIDENCE_POSTGRES_IMAGE",
            "WORKERS",
            "OMNI_REPLICA_COUNT",
        }
        if not isinstance(environment, dict) or any(
            not isinstance(environment.get(name), str) for name in required
        ):
            raise EvidenceVerificationError("Observed candidate environment is incomplete.")
        try:
            workers = int(environment["WORKERS"])
            replicas = int(environment["OMNI_REPLICA_COUNT"])
        except ValueError as exc:
            raise EvidenceVerificationError("Observed topology counts are invalid.") from exc
        return cls(
            candidate,
            environment["OMNI_EVIDENCE_SOURCE_REVISION"],
            environment["OMNI_EVIDENCE_SOURCE_TREE_DIGEST"],
            environment["OMNI_EVIDENCE_PRODUCTION_IMAGE"],
            environment["OMNI_EVIDENCE_IMAGE"],
            environment["OMNI_EVIDENCE_LAUNCHER_DIGEST"],
            environment["OMNI_EVIDENCE_MIGRATION_MANIFEST_CHECKSUM"],
            environment["OMNI_EVIDENCE_REDIS_IMAGE"],
            environment["OMNI_EVIDENCE_REDIS_IMAGE"],
            environment["OMNI_EVIDENCE_POSTGRES_IMAGE"],
            workers,
            replicas,
        )

    def __post_init__(self) -> None:
        if type(self.candidate) is not CandidateTopology:
            raise EvidenceVerificationError("Candidate verifier is invalid.")
        if not isinstance(self.source_revision, str) or not _REVISION.fullmatch(
            self.source_revision
        ):
            raise EvidenceVerificationError("Observed source revision is invalid.")
        _digest(self.source_tree_digest, "Observed source tree digest")
        _image(self.production_image, "Observed production image")
        _image(self.evidence_image, "Observed evidence image")
        _digest(self.evidence_launcher_digest, "Observed launcher digest")
        _digest(self.migration_manifest_checksum, "Observed migration manifest checksum")
        _image(self.redis_primary_image, "Observed Redis primary image")
        _image(self.redis_standby_image, "Observed Redis standby image")
        _image(self.postgresql_image, "Observed PostgreSQL image")
        _integer(self.workers_per_replica, "Observed worker count", 1, 64)
        if type(self.replica_count) is not int or self.replica_count not in (1, 2):
            raise EvidenceVerificationError("Observed replica count is invalid.")

    def __call__(self, record: str) -> bool:
        candidate = self.candidate
        return bool(
            record == candidate.candidate_id
            and self.source_revision == candidate.source_revision
            and self.source_tree_digest == candidate.source_tree_digest
            and self.production_image == candidate.production_image
            and self.evidence_image == candidate.evidence_image
            and self.evidence_launcher_digest == candidate.evidence_launcher_digest
            and self.migration_manifest_checksum == candidate.migration_manifest_checksum
            and self.redis_primary_image == candidate.redis_primary_image
            and self.redis_standby_image == candidate.redis_standby_image
            and self.postgresql_image == candidate.postgresql_image
            and self.workers_per_replica == 1
            and self.replica_count in candidate.experimental_replica_counts
        )


_COUNTER_FIELDS: Final = (
    "attempted",
    "admitted",
    "upstream_started",
    "upstream_completed",
    "client_success",
    "client_cancelled",
    "client_unknown",
    "rejected",
    "durable_committed",
    "released_or_expired",
    "unauthorized_management_success",
    "duplicate_durable_commits",
    "hard_budget_overshoot_nanos",
    "successful_missing_audit",
    "successful_missing_usage",
    "replay_success",
    "cross_replica_revoke_failures",
    "credential_overlap",
    "invalidated_cache_hits",
    "unresolved_reservations",
    "outstanding_unknown_results",
)
_FAILURE_COUNTERS: Final = _COUNTER_FIELDS[10:15] + _COUNTER_FIELDS[16:]
RECOVERY_CLOCK_SCENARIOS: Final = frozenset(
    {
        "redis-app-a-interruption",
        "redis-app-b-interruption",
        "redis-both-paths-interruption",
        "redis-restart",
        "redis-standby-promotion",
        "postgresql-outage",
    }
)


def expected_challenged_operations(candidate: CandidateTopology, scenario_id: str) -> int:
    if scenario_id not in REQUIRED_SCENARIOS:
        raise EvidenceVerificationError("Scenario identity is invalid.")
    if scenario_id in _PERFORMANCE_SCENARIOS:
        return candidate.measured_attempts
    if scenario_id in {"migration-interruption-resume", "bootstrap-interruption"}:
        return 1
    if scenario_id in {"app-a-loss", "app-b-loss", "standalone-rollback"}:
        return candidate.correctness_attempts
    if scenario_id in RECOVERY_CLOCK_SCENARIOS - {"redis-standby-promotion"}:
        return candidate.correctness_attempts + 2
    if scenario_id == "redis-standby-promotion":
        return candidate.correctness_attempts + 4
    if scenario_id in {"stale-epoch", "partial-namespace"}:
        return 4
    if scenario_id == "cancellation-unknown-outcome":
        return 5
    if scenario_id == "duplicate-delivery":
        return 2
    return candidate.correctness_attempts + 11


def expected_fault_milestones(scenario_id: str) -> int:
    exact = {
        "migration-interruption-resume": 1,
        "bootstrap-interruption": 1,
        "coordinated-baseline": 0,
        "coordinated-target": 0,
        "app-a-loss": 2,
        "app-b-loss": 2,
        "redis-app-a-interruption": 2,
        "redis-app-b-interruption": 2,
        "redis-both-paths-interruption": 2,
        "redis-restart": 2,
        "redis-standby-promotion": 4,
        "stale-epoch": 3,
        "partial-namespace": 3,
        "postgresql-outage": 2,
        "cancellation-unknown-outcome": 2,
        "duplicate-delivery": 2,
        "drain-reconcile-mark-ready": 5,
        "standalone-rollback": 3,
    }
    try:
        return exact[scenario_id]
    except (KeyError, TypeError):
        raise EvidenceVerificationError("Scenario identity is invalid.") from None


def expected_sample_partitions(candidate: CandidateTopology, scenario_id: str) -> dict[str, int]:
    """Return the exact HTTP evidence partitions for one scenario execution."""

    if scenario_id in _PERFORMANCE_SCENARIOS:
        return {"warmup": candidate.warmup_requests, "measured": candidate.measured_attempts}
    if scenario_id in {"migration-interruption-resume", "bootstrap-interruption"}:
        return {}
    if scenario_id in {"app-a-loss", "app-b-loss"}:
        return {"measured": candidate.correctness_attempts}
    if scenario_id in RECOVERY_CLOCK_SCENARIOS - {"redis-standby-promotion"}:
        return {
            "fault": candidate.correctness_attempts // 2,
            "recovery-probe": 2,
            "recovered": candidate.correctness_attempts // 2,
        }
    if scenario_id == "redis-standby-promotion":
        return {
            "fault": 1,
            "promotion-probe": 2,
            "measured": candidate.correctness_attempts - 1,
            "restoration-probe": 2,
        }
    exact = {
        "stale-epoch": {"lifecycle": 4},
        "partial-namespace": {"lifecycle": 4},
        "cancellation-unknown-outcome": {"lifecycle": 5},
        "duplicate-delivery": {"lifecycle": 2},
        "drain-reconcile-mark-ready": {"lifecycle": candidate.correctness_attempts + 5},
        "standalone-rollback": {"lifecycle": candidate.correctness_attempts},
    }
    try:
        return exact[scenario_id]
    except (KeyError, TypeError):
        raise EvidenceVerificationError("Scenario identity is invalid.") from None


@dataclass(frozen=True, slots=True)
class CorrectnessCounters:
    attempted: int = 0
    admitted: int = 0
    upstream_started: int = 0
    upstream_completed: int = 0
    client_success: int = 0
    client_cancelled: int = 0
    client_unknown: int = 0
    rejected: int = 0
    durable_committed: int = 0
    released_or_expired: int = 0
    unauthorized_management_success: int = 0
    duplicate_durable_commits: int = 0
    hard_budget_overshoot_nanos: int = 0
    successful_missing_audit: int = 0
    successful_missing_usage: int = 0
    replay_success: int = 0
    cross_replica_revoke_failures: int = 0
    credential_overlap: int = 0
    invalidated_cache_hits: int = 0
    unresolved_reservations: int = 0
    outstanding_unknown_results: int = 0

    def __post_init__(self) -> None:
        for name in _COUNTER_FIELDS:
            _integer(getattr(self, name), f"Counter {name}", 0, 9_223_372_036_854_775_807)

    @classmethod
    def from_dict(cls, value: object) -> CorrectnessCounters:
        raw = _closed(value, frozenset(_COUNTER_FIELDS), "Correctness counters")
        try:
            return cls(**raw)
        except (TypeError, ValueError) as exc:
            raise EvidenceVerificationError("Correctness counters are invalid.") from exc

    @property
    def safe(self) -> bool:
        return all(getattr(self, name) == 0 for name in _FAILURE_COUNTERS)


@dataclass(frozen=True, slots=True)
class RecoveryClock:
    fault_started_ns: int
    fault_observed_ns: int
    dependency_restored_ns: int
    reconciliation_started_ns: int
    reconciliation_completed_ns: int
    mark_ready_ns: int
    sustained_ready_ns: int

    def __post_init__(self) -> None:
        values = tuple(getattr(self, name) for name in self.__dataclass_fields__)
        if any(type(value) is not int or value < 1 for value in values) or values != tuple(
            sorted(values)
        ):
            raise EvidenceVerificationError("Recovery clock chronology is invalid.")

    @property
    def recovery_ms(self) -> float:
        return (self.sustained_ready_ns - self.fault_started_ns) / 1_000_000

    def to_dict(self) -> dict[str, int]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: object) -> RecoveryClock:
        raw = _closed(value, frozenset(cls.__dataclass_fields__), "Recovery clock")
        try:
            return cls(**raw)
        except (TypeError, ValueError) as exc:
            raise EvidenceVerificationError("Recovery clock is invalid.") from exc


@dataclass(frozen=True, slots=True)
class ScenarioResult:
    scenario_id: str
    repetition: int
    state: ScenarioState
    challenged_operations: int
    fault_milestones: int
    duration_ms: float
    counters: CorrectnessCounters
    artifact_name: str
    artifact_digest: str
    p95_ms: float = 0.0
    successful_throughput_rps: float = 0.0
    recovery_clock: RecoveryClock | None = None
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != SCHEMA_VERSION:
            raise EvidenceVerificationError("Scenario schema version is invalid.")
        if self.scenario_id not in REQUIRED_SCENARIOS or type(self.state) is not ScenarioState:
            raise EvidenceVerificationError("Scenario identity or state is invalid.")
        _integer(self.repetition, "Scenario repetition", 1, 3)
        _integer(self.challenged_operations, "Challenged operations", 0, 1_000_000)
        _integer(self.fault_milestones, "Fault milestones", 0, 1_000_000)
        if type(self.duration_ms) not in (int, float) or not math.isfinite(self.duration_ms):
            raise EvidenceVerificationError("Scenario duration is invalid.")
        if not 0 <= self.duration_ms <= 2_700_000:
            raise EvidenceVerificationError("Scenario duration is invalid.")
        for value in (self.p95_ms, self.successful_throughput_rps):
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise EvidenceVerificationError("Scenario performance result is invalid.")
        if self.scenario_id in _PERFORMANCE_SCENARIOS and (
            self.p95_ms <= 0 or self.successful_throughput_rps <= 0
        ):
            raise EvidenceVerificationError("Performance scenario result is incomplete.")
        if type(self.counters) is not CorrectnessCounters:
            raise EvidenceVerificationError("Scenario counters are invalid.")
        if self.scenario_id in RECOVERY_CLOCK_SCENARIOS:
            if type(self.recovery_clock) is not RecoveryClock:
                raise EvidenceVerificationError("Recovery scenario clock is missing.")
            if self.recovery_clock.recovery_ms > 60_000:
                raise EvidenceVerificationError("Recovery scenario exceeded its objective.")
        elif self.recovery_clock is not None:
            raise EvidenceVerificationError("Unexpected recovery scenario clock.")
        _artifact_name(self.artifact_name)
        _digest(self.artifact_digest, "Scenario artifact digest")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "scenario_id": self.scenario_id,
            "repetition": self.repetition,
            "state": self.state.value,
            "challenged_operations": self.challenged_operations,
            "fault_milestones": self.fault_milestones,
            "duration_ms": self.duration_ms,
            "counters": asdict(self.counters),
            "artifact_name": self.artifact_name,
            "artifact_digest": self.artifact_digest,
            "p95_ms": self.p95_ms,
            "successful_throughput_rps": self.successful_throughput_rps,
            "recovery_clock": (
                None if self.recovery_clock is None else self.recovery_clock.to_dict()
            ),
        }

    @classmethod
    def from_dict(cls, value: object) -> ScenarioResult:
        raw = _closed(value, frozenset(cls.__dataclass_fields__), "Scenario result")
        try:
            return cls(
                **{
                    **raw,
                    "state": ScenarioState(raw["state"]),
                    "counters": CorrectnessCounters.from_dict(raw["counters"]),
                    "recovery_clock": (
                        None
                        if raw["recovery_clock"] is None
                        else RecoveryClock.from_dict(raw["recovery_clock"])
                    ),
                }
            )
        except (TypeError, ValueError) as exc:
            raise EvidenceVerificationError("Scenario result is invalid.") from exc


@dataclass(frozen=True, slots=True)
class RunManifest:
    run_id: str
    candidate_id: str
    candidate_digest: str
    source_revision: str
    source_tree_digest: str
    production_image: str
    evidence_launcher_digest: str
    status: ScenarioState
    results: tuple[ScenarioResult, ...]
    artifacts: tuple[tuple[str, str], ...]
    complete: bool
    schema_version: int = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != SCHEMA_VERSION:
            raise EvidenceVerificationError("Run manifest schema is invalid.")
        if not isinstance(self.run_id, str) or not _RUN_ID.fullmatch(self.run_id):
            raise EvidenceVerificationError("Run identifier is invalid.")
        if not isinstance(self.candidate_id, str) or not re.fullmatch(
            r"act_[0-9a-f]{32}", self.candidate_id
        ):
            raise EvidenceVerificationError("Candidate identifier is invalid.")
        _digest(self.candidate_digest, "Candidate digest")
        if not isinstance(self.source_revision, str) or not _REVISION.fullmatch(
            self.source_revision
        ):
            raise EvidenceVerificationError("Run source revision is invalid.")
        _digest(self.source_tree_digest, "Run source tree digest")
        _image(self.production_image, "Run production image")
        _digest(self.evidence_launcher_digest, "Run evidence launcher digest")
        if type(self.status) is not ScenarioState or type(self.complete) is not bool:
            raise EvidenceVerificationError("Run completion state is invalid.")
        if not isinstance(self.results, tuple) or len(self.results) > 128:
            raise EvidenceVerificationError("Run scenario results are invalid.")
        if not isinstance(self.artifacts, tuple) or len(self.artifacts) > 256:
            raise EvidenceVerificationError("Run artifact inventory is invalid.")
        names: list[str] = []
        for item in self.artifacts:
            if not isinstance(item, tuple) or len(item) != 2:
                raise EvidenceVerificationError("Run artifact inventory is invalid.")
            names.append(_artifact_name(item[0]))
            _digest(item[1], "Run artifact digest")
        if names != sorted(set(names)):
            raise EvidenceVerificationError("Run artifact inventory is not canonical.")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "candidate_id": self.candidate_id,
            "candidate_digest": self.candidate_digest,
            "source_revision": self.source_revision,
            "source_tree_digest": self.source_tree_digest,
            "production_image": self.production_image,
            "evidence_launcher_digest": self.evidence_launcher_digest,
            "status": self.status.value,
            "results": [item.to_dict() for item in self.results],
            "artifacts": [{"name": name, "digest": digest} for name, digest in self.artifacts],
            "complete": self.complete,
        }

    @classmethod
    def from_dict(cls, value: object) -> RunManifest:
        raw = _closed(value, frozenset(cls.__dataclass_fields__), "Run manifest")
        artifacts = raw["artifacts"]
        if not isinstance(artifacts, list):
            raise EvidenceVerificationError("Run artifact inventory is invalid.")
        decoded_artifacts: list[tuple[str, str]] = []
        for item in artifacts:
            entry = _closed(item, frozenset({"name", "digest"}), "Run artifact")
            decoded_artifacts.append((entry["name"], entry["digest"]))
        try:
            return cls(
                **{
                    **raw,
                    "status": ScenarioState(raw["status"]),
                    "results": tuple(ScenarioResult.from_dict(item) for item in raw["results"]),
                    "artifacts": tuple(decoded_artifacts),
                }
            )
        except (TypeError, ValueError) as exc:
            raise EvidenceVerificationError("Run manifest is invalid.") from exc

    @property
    def digest(self) -> str:
        return hashlib.sha256(
            b"omni-ha-run-manifest-v1\x00" + canonical_bytes(self.to_dict())
        ).hexdigest()


def _expected_scenario_keys(candidate: CandidateTopology) -> set[tuple[str, int]]:
    return {
        (scenario, repetition)
        for scenario in candidate.required_scenarios
        for repetition in (
            range(1, candidate.pair_repetitions + 1) if scenario in _PERFORMANCE_SCENARIOS else (1,)
        )
    }


def verify_run_manifest(
    manifest: RunManifest,
    candidate: CandidateTopology,
    artifact_root: Path,
    *,
    expected_manifest_digest: str | None = None,
) -> bool:
    if type(manifest) is not RunManifest or type(candidate) is not CandidateTopology:
        raise EvidenceVerificationError("Evidence verification input is invalid.")
    if expected_manifest_digest is not None and (
        _digest(expected_manifest_digest, "Expected manifest digest") != manifest.digest
    ):
        raise EvidenceVerificationError("Run manifest does not match its pinned digest.")
    if (
        not manifest.complete
        or manifest.status is not ScenarioState.COMPLETE_PASS
        or manifest.candidate_id != candidate.candidate_id
        or manifest.candidate_digest != candidate.digest
        or manifest.source_revision != candidate.source_revision
        or manifest.source_tree_digest != candidate.source_tree_digest
        or manifest.production_image != candidate.production_image
        or manifest.evidence_launcher_digest != candidate.evidence_launcher_digest
    ):
        raise EvidenceVerificationError("Run does not match the complete candidate.")
    expected = _expected_scenario_keys(candidate)
    actual = {(result.scenario_id, result.repetition) for result in manifest.results}
    if len(actual) != len(manifest.results) or actual != expected:
        raise EvidenceVerificationError("Scenario inventory is missing or duplicated.")
    inventory = dict(manifest.artifacts)
    if len(inventory) != len(manifest.artifacts):
        raise EvidenceVerificationError("Artifact inventory is duplicated.")
    if set(inventory) != {
        "candidate.json",
        "events.jsonl",
        "oracle.jsonl",
        "samples.jsonl",
        "scenarios.json",
        "summary.json",
    }:
        raise EvidenceVerificationError("Artifact inventory is incomplete or unexpected.")
    root = artifact_root.resolve(strict=True)
    for result in manifest.results:
        if (
            result.state is not ScenarioState.COMPLETE_PASS
            or result.challenged_operations
            != expected_challenged_operations(candidate, result.scenario_id)
            or result.fault_milestones != expected_fault_milestones(result.scenario_id)
            or result.counters.attempted != result.challenged_operations
            or (result.scenario_id not in _PERFORMANCE_SCENARIOS and result.duration_ms > 60_000)
            or not result.counters.safe
            or inventory.get(result.artifact_name) != result.artifact_digest
        ):
            raise EvidenceVerificationError("A scenario is not eligible.")
    by_key = {(result.scenario_id, result.repetition): result for result in manifest.results}
    for repetition in range(1, candidate.pair_repetitions + 1):
        baseline = by_key[("coordinated-baseline", repetition)]
        target = by_key[("coordinated-target", repetition)]
        if (
            target.p95_ms > baseline.p95_ms * 1.20
            or target.successful_throughput_rps < baseline.successful_throughput_rps * 0.85
        ):
            raise EvidenceVerificationError("A performance pair is not eligible.")
    for name, expected_digest in manifest.artifacts:
        try:
            unresolved = root / name
            if unresolved.is_symlink():
                raise EvidenceVerificationError("Artifact symlinks are prohibited.")
            path = unresolved.resolve(strict=True)
            if path.parent != root and root not in path.parents:
                raise EvidenceVerificationError("Artifact escapes the run directory.")
            if not os.path.isfile(path):
                raise EvidenceVerificationError("Artifact is not a regular file.")
            payload = _read_bounded_regular_file(path, _MAX_JSON_BYTES)
            from .report import scan_secret_free

            scan_secret_free(payload)
            digest = hashlib.sha256(payload).hexdigest()
        except OSError as exc:
            raise EvidenceVerificationError("Artifact content is missing or unreadable.") from exc
        if digest != expected_digest:
            raise EvidenceVerificationError("Artifact content is missing or tampered.")
    from .report import load_jsonl

    archived_candidate = CandidateTopology.from_dict(load_json(root / "candidate.json"))
    if archived_candidate != candidate:
        raise EvidenceVerificationError("Archived candidate does not match verification input.")
    scenarios = load_json(root / "scenarios.json")
    if (
        not isinstance(scenarios, dict)
        or set(scenarios) != {"schema_version", "results"}
        or scenarios.get("schema_version") != SCHEMA_VERSION
        or scenarios.get("results") != [result.to_dict() for result in manifest.results]
    ):
        raise EvidenceVerificationError("Scenario artifact semantic binding is invalid.")
    events = load_jsonl(root / "events.jsonl", limit=128)
    if len(events) != len(manifest.results):
        raise EvidenceVerificationError("Event artifact semantic inventory is invalid.")
    event_keys = {
        "schema_version",
        "scenario_id",
        "repetition",
        "started_monotonic_ns",
        "completed_monotonic_ns",
        "challenged_operations",
        "fault_milestones",
        "counters",
        "p95_ms",
        "successful_throughput_rps",
        "recovery_clock",
    }
    for event, result in zip(events, manifest.results, strict=True):
        if not isinstance(event, dict) or set(event) != event_keys:
            raise EvidenceVerificationError("Event artifact schema is invalid.")
        started = event.get("started_monotonic_ns")
        completed = event.get("completed_monotonic_ns")
        if type(started) is not int or type(completed) is not int or completed < started:
            raise EvidenceVerificationError("Event artifact chronology is invalid.")
        if (
            event.get("schema_version") != SCHEMA_VERSION
            or event.get("scenario_id") != result.scenario_id
            or event.get("repetition") != result.repetition
            or event.get("challenged_operations") != result.challenged_operations
            or event.get("fault_milestones") != result.fault_milestones
            or event.get("counters") != asdict(result.counters)
            or event.get("p95_ms") != result.p95_ms
            or event.get("successful_throughput_rps") != result.successful_throughput_rps
            or event.get("recovery_clock")
            != (None if result.recovery_clock is None else result.recovery_clock.to_dict())
            or (completed - started) / 1_000_000 != result.duration_ms
        ):
            raise EvidenceVerificationError("Event artifact semantic binding is invalid.")
    samples = load_jsonl(root / "samples.jsonl")
    sample_keys = {
        "sequence",
        "replica",
        "status_code",
        "duration_ms",
        "success",
        "transport_failure",
        "operation_digest",
        "delivery_digest",
        "scenario_id",
        "repetition",
        "phase",
        "attempt",
        "schedule_seed",
    }
    sequences: set[int] = set()
    for sample in samples:
        if not isinstance(sample, dict) or set(sample) != sample_keys:
            raise EvidenceVerificationError("Sample artifact schema is invalid.")
        sequence = sample.get("sequence")
        duration = sample.get("duration_ms")
        if (
            type(sequence) is not int
            or sequence < 0
            or sequence in sequences
            or sample.get("replica") not in {"app-a", "app-b"}
            or type(sample.get("status_code")) is not int
            or not 0 <= sample["status_code"] <= 599
            or type(duration) not in (int, float)
            or not math.isfinite(duration)
            or duration < 0
            or type(sample.get("success")) is not bool
            or type(sample.get("transport_failure")) is not bool
            or not isinstance(sample.get("operation_digest"), str)
            or not _HEX64.fullmatch(sample["operation_digest"])
            or not isinstance(sample.get("delivery_digest"), str)
            or not _HEX64.fullmatch(sample["delivery_digest"])
            or sample.get("scenario_id") not in REQUIRED_SCENARIOS
            or type(sample.get("repetition")) is not int
            or type(sample.get("phase")) is not str
            or type(sample.get("attempt")) is not int
            or sample["attempt"] < 1
            or type(sample.get("schedule_seed")) is not int
            or (
                sample.get("success") is True
                and (sample.get("status_code") != 200 or sample.get("transport_failure") is True)
            )
            or (sample.get("transport_failure") is True and sample.get("status_code") != 0)
        ):
            raise EvidenceVerificationError("Sample artifact value is invalid.")
        sequences.add(sequence)
    if len(samples) != candidate.expected_sample_count:
        raise EvidenceVerificationError("Sample artifact inventory is incomplete.")
    operation_digests = [sample["operation_digest"] for sample in samples]
    delivery_digests = [sample["delivery_digest"] for sample in samples]
    if len(set(delivery_digests)) != len(delivery_digests):
        raise EvidenceVerificationError("Sample delivery identities are duplicated.")
    operation_groups: dict[str, list[dict[str, object]]] = {}
    for sample in samples:
        operation_groups.setdefault(str(sample["operation_digest"]), []).append(sample)
    duplicated_groups = [group for group in operation_groups.values() if len(group) > 1]
    if (
        len(duplicated_groups) != 1
        or len(duplicated_groups[0]) != 2
        or {sample["scenario_id"] for sample in duplicated_groups[0]} != {"duplicate-delivery"}
    ):
        raise EvidenceVerificationError("Duplicate-delivery operation identity is invalid.")
    for result in manifest.results:
        selected_samples = [
            sample
            for sample in samples
            if sample["scenario_id"] == result.scenario_id
            and sample["repetition"] == result.repetition
        ]
        actual_partitions: dict[str, list[dict[str, object]]] = {}
        for sample in selected_samples:
            actual_partitions.setdefault(str(sample["phase"]), []).append(sample)
        expected_partitions = expected_sample_partitions(candidate, result.scenario_id)
        if {name: len(values) for name, values in actual_partitions.items()} != expected_partitions:
            raise EvidenceVerificationError("Sample scenario partition is incomplete.")
        for phase, partition in actual_partitions.items():
            if sorted(int(sample["attempt"]) for sample in partition) != list(
                range(1, len(partition) + 1)
            ):
                raise EvidenceVerificationError("Sample attempt partition is invalid.")
            expected_seed = (
                candidate.pair_seeds[result.repetition - 1]
                if result.scenario_id in _PERFORMANCE_SCENARIOS
                else 0
            )
            if any(sample["schedule_seed"] != expected_seed for sample in partition):
                raise EvidenceVerificationError("Sample schedule seed is invalid.")
            if phase == "warmup" and not all(sample["success"] for sample in partition):
                raise EvidenceVerificationError("Performance warm-up did not pass.")
            if phase == "fault" and any(sample["success"] for sample in partition):
                raise EvidenceVerificationError("Fault partition admitted a request.")
        if result.scenario_id == "cancellation-unknown-outcome":
            lifecycle = sorted(actual_partitions["lifecycle"], key=lambda sample: sample["attempt"])
            outcomes = tuple(
                (
                    sample["status_code"],
                    sample["success"],
                    sample["transport_failure"],
                )
                for sample in lifecycle
            )
            if (
                outcomes
                != (
                    (500, False, False),
                    (503, False, False),
                    (503, False, False),
                    (200, True, False),
                    (200, True, False),
                )
                or {sample["replica"] for sample in lifecycle[1:3]} != {"app-a", "app-b"}
                or {sample["replica"] for sample in lifecycle[3:5]} != {"app-a", "app-b"}
            ):
                raise EvidenceVerificationError("Unknown-outcome lifecycle progression is invalid.")
        counted = [sample for sample in selected_samples if sample["phase"] != "warmup"]
        sample_success = sum(bool(sample["success"]) for sample in counted)
        sample_transport = sum(bool(sample["transport_failure"]) for sample in counted)
        if (
            result.counters.client_success != sample_success
            or result.counters.client_unknown != sample_transport
            or result.counters.rejected != len(counted) - sample_success - sample_transport
        ):
            raise EvidenceVerificationError("Sample outcomes do not match scenario counters.")
    from .oracle import OperationOracleEvidence, counters_from_operation_evidence

    oracle_records = load_jsonl(root / "oracle.jsonl")
    oracle_keys = frozenset(OperationOracleEvidence.__dataclass_fields__)
    try:
        oracle_rows = tuple(
            OperationOracleEvidence(**_closed(row, oracle_keys, "Oracle evidence"))
            for row in oracle_records
        )
    except (TypeError, ValueError) as exc:
        raise EvidenceVerificationError("Oracle evidence is invalid.") from exc
    oracle_by_digest = {row.operation_digest: row for row in oracle_rows}
    if len(oracle_by_digest) != len(oracle_rows) or set(oracle_by_digest) != set(operation_digests):
        raise EvidenceVerificationError("Oracle evidence does not cover every sample exactly once.")
    for digest, grouped_samples in operation_groups.items():
        row = oracle_by_digest[digest]
        if (
            row.deliveries != len(grouped_samples)
            or row.client_successes != sum(bool(sample["success"]) for sample in grouped_samples)
            or row.transport_failures
            != sum(bool(sample["transport_failure"]) for sample in grouped_samples)
        ):
            raise EvidenceVerificationError("Oracle evidence contradicts a client sample.")
    for result in manifest.results:
        counted = [
            sample
            for sample in samples
            if sample["scenario_id"] == result.scenario_id
            and sample["repetition"] == result.repetition
            and sample["phase"] != "warmup"
        ]
        counted_digests = dict.fromkeys(str(sample["operation_digest"]) for sample in counted)
        derived = counters_from_operation_evidence(
            oracle_by_digest[digest] for digest in counted_digests
        )
        derived = replace(derived, attempted=result.challenged_operations)
        if derived != result.counters or not derived.safe:
            raise EvidenceVerificationError(
                "Scenario counters are not derived from oracle evidence."
            )
    summary = load_json(root / "summary.json")
    summary_keys = {
        "schema_version",
        "state",
        "candidate_id",
        "preflight",
        "bootstrap",
        "resources",
        "completed_unix_ns",
        "scenario_count",
        "sample_count",
        "oracle_count",
    }
    if (
        not isinstance(summary, dict)
        or set(summary) != summary_keys
        or summary.get("schema_version") != SCHEMA_VERSION
        or summary.get("state") != ScenarioState.COMPLETE_PASS.value
        or summary.get("candidate_id") != candidate.candidate_id
        or type(summary.get("completed_unix_ns")) is not int
        or summary["completed_unix_ns"] < 1
        or summary.get("scenario_count") != len(manifest.results)
        or summary.get("sample_count") != len(samples)
        or summary.get("oracle_count") != len(oracle_rows)
        or any(
            not isinstance(summary.get(name), dict)
            for name in ("preflight", "bootstrap", "resources")
        )
    ):
        raise EvidenceVerificationError("Summary artifact semantic binding is invalid.")
    preflight = _closed(
        summary["preflight"],
        frozenset(
            {
                "schema_version",
                "docker_server_version",
                "compose_version",
                "source_revision",
                "source_tree_digest",
                "production_image_id",
                "evidence_image_id",
                "redis_image_id",
                "postgresql_image_id",
                "free_disk_bytes",
            }
        ),
        "Preflight summary",
    )
    if (
        preflight["schema_version"] != SCHEMA_VERSION
        or preflight["source_revision"] != candidate.source_revision
        or preflight["source_tree_digest"] != candidate.source_tree_digest
        or preflight["production_image_id"] != _image_id(candidate.production_image)
        or preflight["evidence_image_id"] != _image_id(candidate.evidence_image)
        or preflight["redis_image_id"] != _image_id(candidate.redis_primary_image)
        or preflight["postgresql_image_id"] != _image_id(candidate.postgresql_image)
        or any(
            not isinstance(preflight[name], str) or not 1 <= len(preflight[name]) <= 128
            for name in ("docker_server_version", "compose_version")
        )
        or any(
            not isinstance(preflight[name], str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", preflight[name])
            for name in (
                "production_image_id",
                "evidence_image_id",
                "redis_image_id",
                "postgresql_image_id",
            )
        )
        or type(preflight["free_disk_bytes"]) is not int
        or preflight["free_disk_bytes"] < 10 * 1024**3
    ):
        raise EvidenceVerificationError("Preflight summary is not eligible.")
    bootstrap = _closed(
        summary["bootstrap"],
        frozenset(
            {
                "schema_version",
                "migration_plan_id",
                "migration_checkpoint_revision",
                "source_nonempty_families",
                "target_epoch",
                "migration_resumed",
                "bootstrap_previewed",
                "bootstrap_replayed",
                "redis_replica_acknowledged",
                "migration_duration_ms",
                "bootstrap_duration_ms",
                "redis_server_version",
                "postgresql_server_version",
            }
        ),
        "Bootstrap summary",
    )
    migration = by_key[("migration-interruption-resume", 1)]
    binding_bootstrap = by_key[("bootstrap-interruption", 1)]
    families = bootstrap["source_nonempty_families"]
    from core.durable_migration import DURABLE_COPY_FAMILIES

    expected_families = sorted(family.value for family in DURABLE_COPY_FAMILIES)
    if (
        bootstrap["schema_version"] != SCHEMA_VERSION
        or not isinstance(bootstrap["migration_plan_id"], str)
        or not re.fullmatch(r"dmg_[0-9a-f]{32}", bootstrap["migration_plan_id"])
        or type(bootstrap["migration_checkpoint_revision"]) is not int
        or bootstrap["migration_checkpoint_revision"] < 1
        or not isinstance(families, list)
        or families != expected_families
        or bootstrap["target_epoch"] != 1
        or any(
            bootstrap[name] is not True
            for name in (
                "migration_resumed",
                "bootstrap_previewed",
                "bootstrap_replayed",
                "redis_replica_acknowledged",
            )
        )
        or bootstrap["migration_duration_ms"] != migration.duration_ms
        or bootstrap["bootstrap_duration_ms"] != binding_bootstrap.duration_ms
        or not isinstance(bootstrap["redis_server_version"], str)
        or not bootstrap["redis_server_version"].startswith("8.")
        or not isinstance(bootstrap["postgresql_server_version"], str)
        or not bootstrap["postgresql_server_version"].startswith("17")
    ):
        raise EvidenceVerificationError("Bootstrap summary is not eligible.")
    from .scenarios import ProjectResources

    ProjectResources.from_dict(summary["resources"])
    return True


def _read_bounded_regular_file(path: Path, maximum_bytes: int) -> bytes:
    """Read one exact regular-file snapshot without following a swapped symlink."""

    if type(maximum_bytes) is not int or maximum_bytes < 1:
        raise EvidenceVerificationError("Evidence file limit is invalid.")
    before = os.lstat(path)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISREG(before.st_mode):
        raise EvidenceVerificationError("Evidence file is not a regular file.")
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path, flags)
    try:
        opened = os.fstat(descriptor)
        if (
            not stat.S_ISREG(opened.st_mode)
            or opened.st_size > maximum_bytes
            or (before.st_dev, before.st_ino) != (opened.st_dev, opened.st_ino)
        ):
            raise EvidenceVerificationError("Evidence file changed while opening.")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            payload = handle.read(maximum_bytes + 1)
        after = os.fstat(descriptor)
        if len(payload) > maximum_bytes or opened.st_size != after.st_size:
            raise EvidenceVerificationError("Evidence file is invalid or oversized.")
        return payload
    finally:
        os.close(descriptor)


def load_json(path: Path) -> object:
    try:
        payload = _read_bounded_regular_file(path, _MAX_JSON_BYTES)
        from .report import scan_secret_free

        scan_secret_free(payload)
        return json.loads(
            payload.decode("utf-8"),
            parse_constant=lambda value: (_ for _ in ()).throw(
                EvidenceVerificationError(f"Invalid JSON number: {value}.")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceVerificationError("Evidence JSON is invalid or interrupted.") from exc


def write_atomic_manifest(path: Path, manifest: RunManifest) -> None:
    if path.exists() or path.suffix != ".json" or not path.parent.is_dir():
        raise EvidenceVerificationError("Manifest destination must be a new JSON file.")
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical_bytes(manifest.to_dict()).decode("ascii") + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            pass
        raise
