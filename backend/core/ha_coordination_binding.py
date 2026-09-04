"""Persistent durable-to-coordination binding and namespace-loss defense."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any, Callable, Final

from core.coordination import EpochState
from core.durable_migration import DURABLE_MANIFEST_CHECKSUM
from core.ha_runtime_policy import HaRuntimePolicy, RuntimeMode

_ACTIVATION_RECORD = re.compile(r"act_[0-9a-f]{32}")
_HEX_DIGEST = re.compile(r"[0-9a-f]{64}")
_BINDING_KEYS: Final = frozenset(
    {
        "schema_version",
        "deployment_id",
        "namespace_digest",
        "identifier_key_fingerprint",
        "fencing_epoch",
        "manifest_checksum",
        "activation_record",
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
    schema_version: int = 1

    def __post_init__(self) -> None:
        if (
            self.schema_version != 1
            or not isinstance(self.deployment_id, str)
            or not 8 <= len(self.deployment_id) <= 64
            or not _HEX_DIGEST.fullmatch(self.namespace_digest)
            or not _HEX_DIGEST.fullmatch(self.identifier_key_fingerprint)
            or type(self.fencing_epoch) is not int
            or self.fencing_epoch < 1
            or not _HEX_DIGEST.fullmatch(self.manifest_checksum)
            or not _ACTIVATION_RECORD.fullmatch(self.activation_record)
        ):
            raise ValueError("Coordination binding is invalid.")

    @classmethod
    def for_policy(cls, policy: HaRuntimePolicy, activation_record: str) -> CoordinationBinding:
        if (
            policy.mode is not RuntimeMode.COORDINATED
            or policy.coordination_namespace is None
            or policy.coordination_key is None
            or policy.deployment_id is None
        ):
            raise ValueError("A coordinated runtime policy is required.")
        return cls(
            policy.deployment_id,
            hashlib.sha256(policy.coordination_namespace.encode("utf-8")).hexdigest(),
            hashlib.sha256(policy.coordination_key).hexdigest(),
            policy.fencing_epoch,
            DURABLE_MANIFEST_CHECKSUM,
            activation_record,
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
        }


@dataclass(frozen=True, slots=True)
class BindingBootstrapResult:
    applied: bool
    binding: CoordinationBinding


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
    ) -> None:
        if storage is None or store is None:
            raise ValueError("Binding storage is required.")
        self._storage = storage
        self._store = store
        self._activation_verifier = activation_verifier or (lambda _record: False)

    @staticmethod
    def _decode(value: object, code: str) -> CoordinationBinding:
        try:
            return CoordinationBinding.from_dict(value)
        except (TypeError, ValueError):
            raise HaBindingError(code) from None

    @staticmethod
    def _expected(policy: HaRuntimePolicy, activation_record: str) -> CoordinationBinding:
        try:
            return CoordinationBinding.for_policy(policy, activation_record)
        except ValueError:
            raise HaBindingError("binding_policy_invalid") from None

    async def verify(self, policy: HaRuntimePolicy) -> CoordinationBinding:
        if policy.mode is not RuntimeMode.COORDINATED:
            raise HaBindingError("binding_policy_invalid")
        durable_value = await self._storage.get_config(self.DURABLE_KEY, None)
        if durable_value is None:
            raise HaBindingError("durable_binding_missing")
        durable = self._decode(durable_value, "durable_binding_corrupt")
        expected = self._expected(policy, durable.activation_record)
        if durable != expected:
            raise HaBindingError("binding_mismatch")

        epoch = await self._store.read_epoch()
        if epoch.epoch != policy.fencing_epoch or epoch.state is not EpochState.READY:
            raise HaBindingError("epoch_not_ready")
        shared_value = await self._store.get(self.STORE_KEY)
        if shared_value is None:
            raise HaBindingError("namespace_missing")
        shared = self._decode(shared_value, "coordination_binding_corrupt")
        if shared != durable:
            raise HaBindingError("binding_mismatch")
        return durable

    async def bootstrap(
        self,
        policy: HaRuntimePolicy,
        *,
        activation_record: str,
        apply: bool = False,
    ) -> BindingBootstrapResult:
        expected = self._expected(policy, activation_record)
        if not apply:
            return BindingBootstrapResult(False, expected)
        if not self._activation_verifier(activation_record):
            raise HaBindingError("activation_gate_closed")

        epoch = await self._store.read_epoch()
        if epoch.epoch != policy.fencing_epoch or epoch.state is not EpochState.READY:
            raise HaBindingError("epoch_not_ready")
        if not await self._store.acquire_lock(self.LOCK_KEY, ttl_seconds=30):
            raise HaBindingError("bootstrap_busy")
        try:
            durable_value = await self._storage.get_config(self.DURABLE_KEY, None)
            shared_value = await self._store.get(self.STORE_KEY)
            if durable_value is not None:
                durable = self._decode(durable_value, "durable_binding_corrupt")
                if durable != expected:
                    raise HaBindingError("binding_mismatch")
                if shared_value is None:
                    raise HaBindingError("namespace_missing")
                shared = self._decode(shared_value, "coordination_binding_corrupt")
                if shared != expected:
                    raise HaBindingError("binding_mismatch")
                return BindingBootstrapResult(True, expected)

            if shared_value is None:
                await self._store.set(self.STORE_KEY, expected.to_dict())
            else:
                shared = self._decode(shared_value, "coordination_binding_corrupt")
                if shared != expected:
                    raise HaBindingError("binding_mismatch")
            if not await self._storage.set_config(self.DURABLE_KEY, expected.to_dict()):
                raise HaBindingError("durable_write_failed")
            return BindingBootstrapResult(True, expected)
        finally:
            await self._store.release_lock(self.LOCK_KEY)
