"""Persistent durable-to-coordination binding and namespace-loss defense."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Final

from core.coordination import CoordinationUninitializedError, EpochState
from core.durable_migration import (
    DURABLE_COPY_FAMILIES,
    DURABLE_MANIFEST_CHECKSUM,
    MigrationCheckpoint,
    binding_eligible_checkpoint,
    checkpoint_evidence_checksum,
)
from core.ha_runtime_policy import HaRuntimePolicy, RuntimeMode

_ACTIVATION_RECORD = re.compile(r"act_[0-9a-f]{32}")
_HEX_DIGEST = re.compile(r"[0-9a-f]{64}")
_PLAN_ID = re.compile(r"dmg_[0-9a-f]{32}")
_BINDING_KEYS: Final = frozenset(
    {
        "schema_version",
        "deployment_id",
        "namespace_digest",
        "identifier_key_fingerprint",
        "fencing_epoch",
        "manifest_checksum",
        "activation_record",
        "migration_plan_id",
        "migration_checkpoint_revision",
        "migration_source_revision",
        "migration_target_revision",
        "migration_checkpoint_checksum",
    }
)


class HaBindingError(RuntimeError):
    """Content-free binding failure safe for readiness and operator output."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class CoordinationBinding:
    deployment_id: str = field(repr=False)
    namespace_digest: str
    identifier_key_fingerprint: str
    fencing_epoch: int
    manifest_checksum: str
    activation_record: str
    migration_plan_id: str
    migration_checkpoint_revision: int
    migration_source_revision: int
    migration_target_revision: int
    migration_checkpoint_checksum: str
    schema_version: int = 2

    def __post_init__(self) -> None:
        if (
            self.schema_version != 2
            or not isinstance(self.deployment_id, str)
            or not 8 <= len(self.deployment_id) <= 64
            or not _HEX_DIGEST.fullmatch(self.namespace_digest)
            or not _HEX_DIGEST.fullmatch(self.identifier_key_fingerprint)
            or type(self.fencing_epoch) is not int
            or self.fencing_epoch < 1
            or not _HEX_DIGEST.fullmatch(self.manifest_checksum)
            or not _ACTIVATION_RECORD.fullmatch(self.activation_record)
            or not _PLAN_ID.fullmatch(self.migration_plan_id)
            or type(self.migration_checkpoint_revision) is not int
            or self.migration_checkpoint_revision < 1
            or type(self.migration_source_revision) is not int
            or self.migration_source_revision < 1
            or type(self.migration_target_revision) is not int
            or self.migration_target_revision < 1
            or not _HEX_DIGEST.fullmatch(self.migration_checkpoint_checksum)
        ):
            raise ValueError("Coordination binding is invalid.")

    @classmethod
    def for_policy(
        cls,
        policy: HaRuntimePolicy,
        activation_record: str,
        checkpoint: MigrationCheckpoint,
    ) -> CoordinationBinding:
        if (
            policy.mode is not RuntimeMode.COORDINATED
            or policy.coordination_namespace is None
            or policy.coordination_key is None
            or policy.deployment_id is None
        ):
            raise ValueError("A coordinated runtime policy is required.")
        if not binding_eligible_checkpoint(checkpoint):
            raise ValueError("A completed canonical migration checkpoint is required.")
        return cls(
            policy.deployment_id,
            hashlib.sha256(policy.coordination_namespace.encode("utf-8")).hexdigest(),
            hashlib.sha256(policy.coordination_key).hexdigest(),
            policy.fencing_epoch,
            DURABLE_MANIFEST_CHECKSUM,
            activation_record,
            checkpoint.plan_id,
            checkpoint.revision,
            checkpoint.source_revision,
            checkpoint.target_revision,
            checkpoint_evidence_checksum(checkpoint),
        )

    @classmethod
    def from_dict(cls, value: object) -> CoordinationBinding:
        if not isinstance(value, dict) or set(value) != _BINDING_KEYS:
            raise ValueError("Coordination binding is invalid.")
        return cls(
            value["deployment_id"],
            value["namespace_digest"],
            value["identifier_key_fingerprint"],
            value["fencing_epoch"],
            value["manifest_checksum"],
            value["activation_record"],
            value["migration_plan_id"],
            value["migration_checkpoint_revision"],
            value["migration_source_revision"],
            value["migration_target_revision"],
            value["migration_checkpoint_checksum"],
            value["schema_version"],
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "deployment_id": self.deployment_id,
            "namespace_digest": self.namespace_digest,
            "identifier_key_fingerprint": self.identifier_key_fingerprint,
            "fencing_epoch": self.fencing_epoch,
            "manifest_checksum": self.manifest_checksum,
            "activation_record": self.activation_record,
            "migration_plan_id": self.migration_plan_id,
            "migration_checkpoint_revision": self.migration_checkpoint_revision,
            "migration_source_revision": self.migration_source_revision,
            "migration_target_revision": self.migration_target_revision,
            "migration_checkpoint_checksum": self.migration_checkpoint_checksum,
        }


@dataclass(frozen=True, slots=True)
class BindingBootstrapResult:
    applied: bool
    binding: CoordinationBinding | None
    prerequisite: MigrationPrerequisiteReport


@dataclass(frozen=True, slots=True)
class MigrationPrerequisiteReport:
    eligible: bool
    code: str
    manifest_version: int | None
    checkpoint_revision: int | None
    missing_families: tuple[str, ...] = ()
    mismatched_families: tuple[str, ...] = ()


class CoordinationBindingManager:
    """Verify or explicitly bootstrap one permanent cross-backend binding."""

    DURABLE_KEY: Final = "ha_coordination_binding_v1"
    STORE_KEY: Final = "ha-runtime-binding-v1"
    LOCK_KEY: Final = "ha-runtime-binding-bootstrap-v1"

    def __init__(
        self,
        storage: Any,
        store: Any,
        *,
        activation_verifier: Callable[[str], bool] | None = None,
        migration_checkpoints: Any | None = None,
    ) -> None:
        if storage is None or store is None:
            raise ValueError("Binding storage is required.")
        self._storage = storage
        self._store = store
        self._activation_verifier = activation_verifier or (lambda _record: False)
        self._migration_checkpoints = migration_checkpoints

    async def _set_durable_record(self, key: str, value: object) -> bool:
        writer = getattr(self._storage, "set_internal_config", None)
        if writer is None:
            writer = self._storage.set_config
        return bool(await writer(key, value))

    @staticmethod
    def decode_record(value: object, code: str) -> CoordinationBinding:
        try:
            if isinstance(value, str):
                value = json.loads(value)
            return CoordinationBinding.from_dict(value)
        except (TypeError, ValueError, json.JSONDecodeError):
            raise HaBindingError(code) from None

    @staticmethod
    def encode_record(value: CoordinationBinding) -> str:
        return json.dumps(value.to_dict(), separators=(",", ":"), sort_keys=True)

    @staticmethod
    def _expected(
        policy: HaRuntimePolicy,
        activation_record: str,
        checkpoint: MigrationCheckpoint,
    ) -> CoordinationBinding:
        try:
            return CoordinationBinding.for_policy(policy, activation_record, checkpoint)
        except ValueError:
            raise HaBindingError("binding_policy_invalid") from None

    async def _checkpoint_repository(self) -> Any:
        if self._migration_checkpoints is None:
            factory = getattr(self._storage, "create_migration_checkpoint_repository", None)
            if factory is None:
                raise HaBindingError("migration_checkpoint_store_missing")
            self._migration_checkpoints = await factory()
        return self._migration_checkpoints

    async def _checkpoint(self, plan_id: str) -> MigrationCheckpoint:
        checkpoint, report = await self.inspect_migration_prerequisite(plan_id)
        if not report.eligible or type(checkpoint) is not MigrationCheckpoint:
            raise HaBindingError(report.code)
        return checkpoint

    async def inspect_migration_prerequisite(
        self, plan_id: str
    ) -> tuple[object | None, MigrationPrerequisiteReport]:
        """Return bounded dry-run evidence without record payloads or backend error text."""

        repository = await self._checkpoint_repository()
        try:
            checkpoint = await repository.get(plan_id)
        except Exception:
            return None, MigrationPrerequisiteReport(
                False, "migration_checkpoint_unavailable", None, None
            )
        if checkpoint is None:
            return None, MigrationPrerequisiteReport(
                False, "migration_checkpoint_missing", None, None
            )
        manifest_version = getattr(checkpoint, "manifest_version", None)
        revision = getattr(checkpoint, "revision", None)
        if type(checkpoint) is not MigrationCheckpoint:
            return checkpoint, MigrationPrerequisiteReport(
                False,
                "migration_checkpoint_ineligible",
                manifest_version if type(manifest_version) is int else None,
                revision if type(revision) is int else None,
            )
        expected = {family.value for family in DURABLE_COPY_FAMILIES}
        actual = {progress.family.value for progress in checkpoint.families}
        missing = tuple(sorted(expected - actual))
        mismatched = tuple(
            progress.family.value
            for progress in checkpoint.families
            if not (
                progress.verified
                and progress.copy_complete
                and progress.source_count == progress.target_count
                and progress.source_checksum == progress.target_checksum
            )
        )
        eligible = binding_eligible_checkpoint(checkpoint)
        return checkpoint, MigrationPrerequisiteReport(
            eligible,
            "ready" if eligible else "migration_checkpoint_ineligible",
            checkpoint.manifest_version,
            checkpoint.revision,
            missing,
            mismatched,
        )

    async def _verify_migration(self, binding: CoordinationBinding) -> MigrationCheckpoint:
        checkpoint = await self._checkpoint(binding.migration_plan_id)
        if (
            checkpoint.revision != binding.migration_checkpoint_revision
            or checkpoint.source_revision != binding.migration_source_revision
            or checkpoint.target_revision != binding.migration_target_revision
            or checkpoint_evidence_checksum(checkpoint) != binding.migration_checkpoint_checksum
        ):
            raise HaBindingError("migration_checkpoint_mismatch")
        return checkpoint

    async def expected_for_binding(
        self, policy: HaRuntimePolicy, binding: CoordinationBinding
    ) -> CoordinationBinding:
        """Rebuild the exact expected binding from current immutable migration evidence."""

        checkpoint = await self._verify_migration(binding)
        return self._expected(policy, binding.activation_record, checkpoint)

    async def verify(self, policy: HaRuntimePolicy) -> CoordinationBinding:
        if policy.mode is not RuntimeMode.COORDINATED:
            raise HaBindingError("binding_policy_invalid")
        durable_value = await self._storage.get_config(self.DURABLE_KEY, None)
        if durable_value is None:
            raise HaBindingError("durable_binding_missing")
        durable = self.decode_record(durable_value, "durable_binding_corrupt")
        checkpoint = await self._verify_migration(durable)
        expected = self._expected(policy, durable.activation_record, checkpoint)
        if durable != expected:
            raise HaBindingError("binding_mismatch")

        shared_value = await self._store.get(self.STORE_KEY)
        if shared_value is None:
            raise HaBindingError("namespace_missing")
        shared = self.decode_record(shared_value, "coordination_binding_corrupt")
        if shared != durable:
            raise HaBindingError("binding_mismatch")
        try:
            epoch = await self._store.read_epoch()
        except CoordinationUninitializedError:
            raise HaBindingError("epoch_namespace_missing") from None
        if epoch.epoch != policy.fencing_epoch or epoch.state is not EpochState.READY:
            raise HaBindingError("epoch_not_ready")
        return durable

    async def bootstrap(
        self,
        policy: HaRuntimePolicy,
        *,
        activation_record: str,
        migration_plan_id: str,
        apply: bool = False,
    ) -> BindingBootstrapResult:
        checkpoint, prerequisite = await self.inspect_migration_prerequisite(migration_plan_id)
        if not prerequisite.eligible or type(checkpoint) is not MigrationCheckpoint:
            if not apply:
                return BindingBootstrapResult(False, None, prerequisite)
            raise HaBindingError(prerequisite.code)
        expected = self._expected(policy, activation_record, checkpoint)
        if not apply:
            return BindingBootstrapResult(False, expected, prerequisite)
        if not self._activation_verifier(activation_record):
            raise HaBindingError("activation_gate_closed")

        if not await self._store.acquire_lock(self.LOCK_KEY, ttl_seconds=30):
            raise HaBindingError("bootstrap_busy")
        try:
            durable_value = await self._storage.get_config(self.DURABLE_KEY, None)
            shared_value = await self._store.get(self.STORE_KEY)
            if durable_value is not None:
                durable = self.decode_record(durable_value, "durable_binding_corrupt")
                if durable != expected:
                    raise HaBindingError("binding_mismatch")
                if shared_value is None:
                    raise HaBindingError("namespace_missing")
                shared = self.decode_record(shared_value, "coordination_binding_corrupt")
                if shared != expected:
                    raise HaBindingError("binding_mismatch")
                try:
                    epoch = await self._store.read_epoch()
                except CoordinationUninitializedError:
                    raise HaBindingError("epoch_namespace_missing") from None
                if epoch.epoch != policy.fencing_epoch or epoch.state is not EpochState.READY:
                    raise HaBindingError("epoch_not_ready")
                return BindingBootstrapResult(True, expected, prerequisite)

            if shared_value is None:
                try:
                    epoch = await self._store.read_epoch()
                except CoordinationUninitializedError:
                    epoch = await self._store.initialize_epoch()
                await self._store.set(self.STORE_KEY, self.encode_record(expected))
            else:
                shared = self.decode_record(shared_value, "coordination_binding_corrupt")
                if shared != expected:
                    raise HaBindingError("binding_mismatch")
                try:
                    epoch = await self._store.read_epoch()
                except CoordinationUninitializedError:
                    raise HaBindingError("epoch_namespace_missing") from None
            if epoch.epoch != policy.fencing_epoch or epoch.state is not EpochState.READY:
                raise HaBindingError("epoch_not_ready")
            if not await self._set_durable_record(self.DURABLE_KEY, expected.to_dict()):
                raise HaBindingError("durable_write_failed")
            return BindingBootstrapResult(True, expected, prerequisite)
        finally:
            await self._store.release_lock(self.LOCK_KEY)
