"""Versioned W4.13 durable-record inventory and migration domain contract.

The module is deliberately side-effect free. It defines strict records, checkpoint invariants,
and keyed content verification without selecting a backend or switching runtime authority.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import re
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

MIGRATION_SCHEMA_VERSION = 1
MAX_COPY_CURSOR_LENGTH = 512
_PLAN_ID = re.compile(r"dmg_[0-9a-f]{32}")
_LOGICAL_ID = re.compile(r"[a-z]{3}_[0-9a-f]{16,64}")
_OPAQUE_CURSOR = re.compile(r"[A-Za-z0-9_-]{1,512}")
_FAILURE_CODE = re.compile(r"[a-z][a-z0-9_]{0,63}")
_CHECKSUM = re.compile(r"[0-9a-f]{64}")


class DurableBackend(StrEnum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"


class DurableFamily(StrEnum):
    CONFIGURATION = "configuration"
    PROVIDER_CREDENTIAL = "provider_credential"
    PRIMARY_CREDENTIAL = "primary_credential"
    VIRTUAL_KEY = "virtual_key"
    IDENTITY = "identity"
    ROLE_BINDING = "role_binding"
    OIDC_POLICY_REVISION = "oidc_policy_revision"
    IDENTITY_SCHEMA_EVIDENCE = "identity_schema_evidence"
    AUDIT_EVENT = "audit_event"
    REQUEST_TRACE = "request_trace"
    USAGE_LEDGER = "usage_ledger"
    HARD_BUDGET_RESERVATION = "hard_budget_reservation"
    MIGRATION_CHECKPOINT = "migration_checkpoint"


class MigrationPhase(StrEnum):
    PLANNED = "planned"
    COPYING = "copying"
    VERIFYING = "verifying"
    READY_TO_SWITCH = "ready_to_switch"
    TARGET_AUTHORITATIVE = "target_authoritative"
    ROLLBACK_READY = "rollback_ready"
    ROLLED_BACK = "rolled_back"


class AuthoritySide(StrEnum):
    SOURCE = "source"
    TARGET = "target"


@dataclass(frozen=True, slots=True)
class DurableInventoryEntry:
    family: DurableFamily
    current_owner: str
    switch_ready: bool
    contains_sensitive_payload: bool
    implementation_note: str

    def __post_init__(self) -> None:
        if type(self.family) is not DurableFamily:
            raise ValueError("Durable family is invalid.")
        if not isinstance(self.current_owner, str) or not self.current_owner.strip():
            raise ValueError("Durable owner is invalid.")
        if type(self.switch_ready) is not bool:
            raise ValueError("Durable readiness is invalid.")
        if type(self.contains_sensitive_payload) is not bool:
            raise ValueError("Durable sensitivity is invalid.")
        if not isinstance(self.implementation_note, str) or not self.implementation_note.strip():
            raise ValueError("Durable implementation note is invalid.")


DURABLE_INVENTORY = (
    DurableInventoryEntry(
        DurableFamily.CONFIGURATION,
        "selected_backend.config",
        True,
        True,
        "Versioned configuration and internal key material.",
    ),
    DurableInventoryEntry(
        DurableFamily.PROVIDER_CREDENTIAL,
        "selected_backend.credentials",
        True,
        True,
        "Provider-pool credential payload and current stored state.",
    ),
    DurableInventoryEntry(
        DurableFamily.PRIMARY_CREDENTIAL,
        "selected_backend.primary_credentials",
        True,
        True,
        "Primary credential payload and current stored state.",
    ),
    DurableInventoryEntry(
        DurableFamily.VIRTUAL_KEY,
        "selected_backend.config.virtual_keys",
        True,
        True,
        "Authorization and billing metadata currently stored as a versioned config document.",
    ),
    DurableInventoryEntry(
        DurableFamily.IDENTITY,
        "identity_repository.identities",
        True,
        True,
        "Management identities and authorization epochs.",
    ),
    DurableInventoryEntry(
        DurableFamily.ROLE_BINDING,
        "identity_repository.role_bindings",
        True,
        True,
        "Explicit role bindings and revisions.",
    ),
    DurableInventoryEntry(
        DurableFamily.OIDC_POLICY_REVISION,
        "identity_repository.oidc_policy_revision",
        True,
        False,
        "OIDC policy and authorization epoch only; client secrets are environment-owned.",
    ),
    DurableInventoryEntry(
        DurableFamily.IDENTITY_SCHEMA_EVIDENCE,
        "identity_repository.identity_migrations",
        True,
        False,
        "Additive management-identity schema evidence.",
    ),
    DurableInventoryEntry(
        DurableFamily.AUDIT_EVENT,
        "audit_repository",
        True,
        False,
        "Append-only redacted management evidence.",
    ),
    DurableInventoryEntry(
        DurableFamily.REQUEST_TRACE,
        "request_trace_repository",
        True,
        False,
        "Bounded request decision evidence without prompts or bodies.",
    ),
    DurableInventoryEntry(
        DurableFamily.USAGE_LEDGER,
        "standalone_usage_stats_db",
        False,
        True,
        "Selected-backend repository parity is deferred to W4.14.",
    ),
    DurableInventoryEntry(
        DurableFamily.HARD_BUDGET_RESERVATION,
        "not_implemented",
        False,
        True,
        "Durable reservation journal is deferred to W4.14/W4.17.",
    ),
    DurableInventoryEntry(
        DurableFamily.MIGRATION_CHECKPOINT,
        "migration_checkpoint_repository",
        True,
        False,
        "Versioned metadata-only resumability evidence.",
    ),
)


def _strict_non_negative_int(value: object, label: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(f"{label} is invalid.")
    return value


def _strict_positive_int(value: object, label: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{label} is invalid.")
    return value


def _timestamp(value: object, label: str) -> datetime:
    if not isinstance(value, str) or not value or len(value) > 40:
        raise ValueError(f"{label} is invalid.")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{label} is invalid.") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timezone.utc.utcoffset(parsed):
        raise ValueError(f"{label} must be UTC.")
    return parsed


def _json_compatible(value: object) -> object:
    if value is None or type(value) in {str, bool, int}:
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("Durable payload contains a non-finite number.")
        return value
    if isinstance(value, Mapping):
        result: dict[str, object] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("Durable payload keys must be strings.")
            result[key] = _json_compatible(item)
        return result
    if isinstance(value, (list, tuple)):
        return [_json_compatible(item) for item in value]
    raise ValueError("Durable payload contains an unsupported value.")


def _freeze_json(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    return value


def _thaw_json(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: _thaw_json(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_thaw_json(item) for item in value]
    return value


def _canonical_record(record: DurableRecord) -> bytes:
    return json.dumps(
        {
            "family": record.family.value,
            "logical_id": record.logical_id,
            "schema_version": record.schema_version,
            "payload": _thaw_json(record.payload),
        },
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class DurableRecord:
    family: DurableFamily
    logical_id: str
    schema_version: int
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        if type(self.family) is not DurableFamily:
            raise ValueError("Durable record family is invalid.")
        if not isinstance(self.logical_id, str) or not _LOGICAL_ID.fullmatch(self.logical_id):
            raise ValueError("Durable logical ID is invalid.")
        _strict_positive_int(self.schema_version, "Durable record schema version")
        if not isinstance(self.payload, Mapping):
            raise ValueError("Durable record payload is invalid.")
        normalized = _json_compatible(self.payload)
        object.__setattr__(self, "payload", _freeze_json(normalized))

    def __repr__(self) -> str:
        return (
            "DurableRecord("
            f"family={self.family!r}, logical_id={self.logical_id!r}, "
            f"schema_version={self.schema_version!r}, payload=<redacted>)"
        )


def compute_records_digest(
    records: tuple[DurableRecord, ...] | list[DurableRecord], *, integrity_key: bytes
) -> str:
    if not isinstance(integrity_key, bytes) or len(integrity_key) < 32:
        raise ValueError("Migration integrity key is too short.")
    ordered = sorted(records, key=lambda item: (item.family.value, item.logical_id))
    seen: set[tuple[DurableFamily, str]] = set()
    digest = hmac.new(integrity_key, digestmod=hashlib.sha256)
    for record in ordered:
        if type(record) is not DurableRecord:
            raise ValueError("Migration digest record is invalid.")
        identity = (record.family, record.logical_id)
        if identity in seen:
            raise ValueError("Migration digest contains a duplicate logical record.")
        seen.add(identity)
        encoded = _canonical_record(record)
        digest.update(len(encoded).to_bytes(8, "big"))
        digest.update(encoded)
    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class FamilyProgress:
    family: DurableFamily
    copy_cursor: str | None
    copied_count: int
    copy_complete: bool
    source_count: int | None
    target_count: int | None
    source_checksum: str | None
    target_checksum: str | None
    verified: bool

    def __post_init__(self) -> None:
        if type(self.family) is not DurableFamily:
            raise ValueError("Migration family is invalid.")
        if self.copy_cursor is not None and (
            not isinstance(self.copy_cursor, str) or not _OPAQUE_CURSOR.fullmatch(self.copy_cursor)
        ):
            raise ValueError("Migration copy cursor is invalid.")
        _strict_non_negative_int(self.copied_count, "Migration copied count")
        if type(self.copy_complete) is not bool or type(self.verified) is not bool:
            raise ValueError("Migration progress flag is invalid.")
        if self.copy_complete and self.copy_cursor is not None:
            raise ValueError("Completed migration copy cannot retain a cursor.")
        for count, label in (
            (self.source_count, "Migration source count"),
            (self.target_count, "Migration target count"),
        ):
            if count is not None:
                _strict_non_negative_int(count, label)
        for checksum in (self.source_checksum, self.target_checksum):
            if checksum is not None and (
                not isinstance(checksum, str) or not _CHECKSUM.fullmatch(checksum)
            ):
                raise ValueError("Migration checksum is invalid.")
        verification_values = (
            self.source_count,
            self.target_count,
            self.source_checksum,
            self.target_checksum,
        )
        if any(value is not None for value in verification_values) and any(
            value is None for value in verification_values
        ):
            raise ValueError("Migration verification evidence is incomplete.")
        if self.verified and (
            not self.copy_complete
            or self.source_count != self.target_count
            or self.source_checksum != self.target_checksum
            or self.source_count is None
        ):
            raise ValueError("Migration verification evidence does not match.")

    def to_record(self) -> dict[str, object]:
        return {
            "family": self.family.value,
            "copy_cursor": self.copy_cursor,
            "copied_count": self.copied_count,
            "copy_complete": self.copy_complete,
            "source_count": self.source_count,
            "target_count": self.target_count,
            "source_checksum": self.source_checksum,
            "target_checksum": self.target_checksum,
            "verified": self.verified,
        }


_SOURCE_PHASES = {
    MigrationPhase.PLANNED,
    MigrationPhase.COPYING,
    MigrationPhase.VERIFYING,
    MigrationPhase.READY_TO_SWITCH,
    MigrationPhase.ROLLED_BACK,
}
_TARGET_PHASES = {MigrationPhase.TARGET_AUTHORITATIVE, MigrationPhase.ROLLBACK_READY}
_VERIFIED_PHASES = {
    MigrationPhase.READY_TO_SWITCH,
    MigrationPhase.TARGET_AUTHORITATIVE,
    MigrationPhase.ROLLBACK_READY,
    MigrationPhase.ROLLED_BACK,
}


@dataclass(frozen=True, slots=True)
class MigrationCheckpoint:
    schema_version: int
    plan_id: str
    source_backend: DurableBackend
    target_backend: DurableBackend
    phase: MigrationPhase
    authority: AuthoritySide
    revision: int
    families: tuple[FamilyProgress, ...]
    failure_code: str | None
    created_at: str
    updated_at: str

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != MIGRATION_SCHEMA_VERSION:
            raise ValueError("Migration checkpoint schema version is unsupported.")
        if not isinstance(self.plan_id, str) or not _PLAN_ID.fullmatch(self.plan_id):
            raise ValueError("Migration plan ID is invalid.")
        if (
            type(self.source_backend) is not DurableBackend
            or type(self.target_backend) is not DurableBackend
        ):
            raise ValueError("Migration backend is invalid.")
        if self.source_backend is self.target_backend:
            raise ValueError("Migration source and target must differ.")
        if type(self.phase) is not MigrationPhase or type(self.authority) is not AuthoritySide:
            raise ValueError("Migration phase or authority is invalid.")
        if self.phase in _SOURCE_PHASES and self.authority is not AuthoritySide.SOURCE:
            raise ValueError("Migration source must be the sole authority in this phase.")
        if self.phase in _TARGET_PHASES and self.authority is not AuthoritySide.TARGET:
            raise ValueError("Migration target must be the sole authority in this phase.")
        _strict_positive_int(self.revision, "Migration checkpoint revision")
        if not isinstance(self.families, tuple) or not self.families:
            raise ValueError("Migration families are invalid.")
        if any(type(progress) is not FamilyProgress for progress in self.families):
            raise ValueError("Migration family progress is invalid.")
        family_names = [progress.family for progress in self.families]
        if len(set(family_names)) != len(family_names):
            raise ValueError("Migration families contain a duplicate.")
        if self.phase in _VERIFIED_PHASES and not all(
            progress.verified for progress in self.families
        ):
            raise ValueError("Migration phase requires complete verification.")
        if self.failure_code is not None and (
            not isinstance(self.failure_code, str) or not _FAILURE_CODE.fullmatch(self.failure_code)
        ):
            raise ValueError("Migration failure code is invalid.")
        created_at = _timestamp(self.created_at, "Migration creation timestamp")
        updated_at = _timestamp(self.updated_at, "Migration update timestamp")
        if updated_at < created_at:
            raise ValueError("Migration update precedes creation.")

    def to_record(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "plan_id": self.plan_id,
            "source_backend": self.source_backend.value,
            "target_backend": self.target_backend.value,
            "phase": self.phase.value,
            "authority": self.authority.value,
            "revision": self.revision,
            "families": [progress.to_record() for progress in self.families],
            "failure_code": self.failure_code,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


def _exact_record(record: object, expected_fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(record, Mapping) or set(record) != expected_fields:
        raise ValueError(f"Stored {label} is invalid.")
    return dict(record)


def _progress_from_record(record: object) -> FamilyProgress:
    expected = {field.name for field in fields(FamilyProgress)}
    values = _exact_record(record, expected, "migration family progress")
    try:
        values["family"] = DurableFamily(values["family"])
        return FamilyProgress(**values)
    except (TypeError, ValueError) as exc:
        raise ValueError("Stored migration family progress is invalid.") from exc


def checkpoint_from_record(record: object) -> MigrationCheckpoint:
    expected = {field.name for field in fields(MigrationCheckpoint)}
    values = _exact_record(record, expected, "migration checkpoint")
    try:
        raw_families = values["families"]
        if not isinstance(raw_families, list):
            raise ValueError
        values["source_backend"] = DurableBackend(values["source_backend"])
        values["target_backend"] = DurableBackend(values["target_backend"])
        values["phase"] = MigrationPhase(values["phase"])
        values["authority"] = AuthoritySide(values["authority"])
        values["families"] = tuple(_progress_from_record(item) for item in raw_families)
        return MigrationCheckpoint(**values)
    except (TypeError, ValueError) as exc:
        raise ValueError("Stored migration checkpoint is invalid.") from exc
