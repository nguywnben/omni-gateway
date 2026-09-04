"""Dry-run-first, bounded HA lifecycle transitions without data deletion."""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, Final

from core.coordination import EpochState
from core.ha_coordination_binding import (
    CoordinationBinding,
    CoordinationBindingManager,
    HaBindingError,
)
from core.ha_runtime_policy import HaRuntimePolicy, RuntimeMode


class HaRuntimeOperator:
    """Operate one coordinated epoch while preserving durable authority."""

    DRAIN_KEY: Final = "ha-runtime-drain-v1"

    def __init__(
        self,
        policy: HaRuntimePolicy,
        storage: Any,
        store: Any,
        *,
        activation_verifier: Callable[[str], bool] | None = None,
    ) -> None:
        if policy.mode is not RuntimeMode.COORDINATED:
            raise ValueError("HA operator requires coordinated mode.")
        self.policy = policy
        self._storage = storage
        self._store = store
        self._activation_verifier = activation_verifier or (lambda _record: False)
        self._bindings = CoordinationBindingManager(storage, store)

    def _activation_required(self, record: str) -> None:
        if not self._activation_verifier(record):
            raise RuntimeError("The coordinated activation record is not accepted.")

    async def _durable_binding(self) -> CoordinationBinding:
        value = await self._storage.get_config(self._bindings.DURABLE_KEY, None)
        if value is None:
            raise HaBindingError("durable_binding_missing")
        try:
            return CoordinationBinding.from_dict(value)
        except ValueError:
            raise HaBindingError("durable_binding_corrupt") from None

    async def _shared_binding(self) -> CoordinationBinding:
        value = await self._store.get(self._bindings.STORE_KEY)
        if value is None:
            raise HaBindingError("namespace_missing")
        try:
            return CoordinationBinding.from_dict(value)
        except ValueError:
            raise HaBindingError("coordination_binding_corrupt") from None

    async def _drain_record(self) -> dict[str, object] | None:
        value = await self._store.get(self.DRAIN_KEY)
        if value is None:
            return None
        if (
            not isinstance(value, dict)
            or set(value) != {"schema_version", "namespace_digest", "epoch"}
            or value.get("schema_version") != 1
            or not isinstance(value.get("namespace_digest"), str)
            or type(value.get("epoch")) is not int
            or value["epoch"] < 1
        ):
            raise RuntimeError("The drain record is corrupt.")
        return value

    async def status(self) -> dict[str, object]:
        durable = await self._durable_binding()
        shared = await self._shared_binding()
        epoch = await self._store.read_epoch()
        drain = await self._drain_record()
        expected = CoordinationBinding.for_policy(self.policy, durable.activation_record)
        accepted = {expected}
        if expected.fencing_epoch > 1:
            accepted.add(replace(expected, fencing_epoch=expected.fencing_epoch - 1))
        if durable not in accepted or shared not in accepted:
            raise RuntimeError("The coordination bindings do not match this deployment.")
        state = (
            "draining"
            if drain is not None and epoch.state is EpochState.READY
            else epoch.state.value
        )
        return {
            "mode": "coordinated",
            "state": state,
            "epoch": epoch.epoch,
            "drain": drain is not None,
            "activation_accepted": self._activation_verifier(durable.activation_record),
        }

    async def drain(self, *, apply: bool = False) -> dict[str, object]:
        binding = await self._bindings.verify(self.policy)
        self._activation_required(binding.activation_record)
        record = {
            "schema_version": 1,
            "namespace_digest": binding.namespace_digest,
            "epoch": binding.fencing_epoch,
        }
        existing = await self._drain_record()
        if existing is not None and existing != record:
            raise RuntimeError("The drain record does not match the active binding.")
        if apply and existing is None:
            await self._store.set(self.DRAIN_KEY, record)
        return {"applied": bool(apply), "state": "draining", "epoch": binding.fencing_epoch}

    async def advance_epoch(self, operation_id: str, *, apply: bool = False) -> dict[str, object]:
        binding = await self._durable_binding()
        shared = await self._shared_binding()
        expected = CoordinationBinding.for_policy(self.policy, binding.activation_record)
        if binding != expected or shared != expected:
            raise RuntimeError("Matching bindings are required before advancing the epoch.")
        self._activation_required(binding.activation_record)
        drain = await self._drain_record()
        if drain is None or drain["epoch"] != binding.fencing_epoch:
            raise RuntimeError("A matching drain is required before advancing the epoch.")
        current = await self._store.read_epoch()
        if not (
            (current.epoch == binding.fencing_epoch and current.state is EpochState.READY)
            or (
                current.epoch == binding.fencing_epoch + 1
                and current.state is EpochState.RECONCILING
            )
        ):
            raise RuntimeError("The coordination epoch cannot be advanced from its current state.")
        if not apply:
            return {
                "applied": False,
                "epoch": current.epoch,
                "next_epoch": binding.fencing_epoch + 1,
            }
        result = await self._store.advance_epoch(binding.fencing_epoch, operation_id)
        if result.epoch != binding.fencing_epoch + 1 or result.state is not EpochState.RECONCILING:
            raise RuntimeError("Epoch advance did not enter the expected reconciliation state.")
        return {"applied": True, "epoch": result.epoch, "state": result.state.value}

    async def reconcile(self, *, apply: bool = False) -> dict[str, object]:
        durable = await self._durable_binding()
        shared = await self._shared_binding()
        self._activation_required(durable.activation_record)
        expected = CoordinationBinding.for_policy(self.policy, durable.activation_record)
        prior = replace(expected, fencing_epoch=expected.fencing_epoch - 1)
        if (
            expected.fencing_epoch <= 1
            or durable not in {prior, expected}
            or shared not in {prior, expected}
        ):
            raise RuntimeError("Binding reconciliation is not an exact one-epoch transition.")
        if durable == expected and shared == prior:
            raise RuntimeError("Binding reconciliation order is invalid.")
        drain = await self._drain_record()
        if drain is None or drain["epoch"] != prior.fencing_epoch:
            raise RuntimeError("A matching drain is required before reconciliation.")
        epoch = await self._store.read_epoch()
        if epoch.epoch != expected.fencing_epoch or epoch.state is not EpochState.RECONCILING:
            raise RuntimeError("The expected reconciling epoch is unavailable.")
        if apply:
            if shared == prior:
                await self._store.set(self._bindings.STORE_KEY, expected.to_dict())
            if durable == prior and not await self._storage.set_config(
                self._bindings.DURABLE_KEY, expected.to_dict()
            ):
                raise RuntimeError("The durable binding update failed.")
        return {"applied": bool(apply), "epoch": expected.fencing_epoch, "state": "reconciling"}

    async def mark_ready(self, operation_id: str, *, apply: bool = False) -> dict[str, object]:
        epoch = await self._store.read_epoch()
        if epoch.epoch == self.policy.fencing_epoch and epoch.state is EpochState.READY:
            binding = await self._bindings.verify(self.policy)
            self._activation_required(binding.activation_record)
            return {"applied": bool(apply), "epoch": epoch.epoch, "state": "ready"}
        durable = await self._durable_binding()
        shared = await self._shared_binding()
        expected = CoordinationBinding.for_policy(self.policy, durable.activation_record)
        self._activation_required(durable.activation_record)
        if durable != expected or shared != expected:
            raise RuntimeError("Reconciled bindings are required before marking ready.")
        drain = await self._drain_record()
        if drain is None or drain["epoch"] != self.policy.fencing_epoch - 1:
            raise RuntimeError("A matching drain is required before marking ready.")
        if epoch.epoch != self.policy.fencing_epoch or epoch.state is not EpochState.RECONCILING:
            raise RuntimeError("The expected reconciling epoch is unavailable.")
        if apply:
            epoch = await self._store.mark_epoch_ready(self.policy.fencing_epoch, operation_id)
            if epoch.state is not EpochState.READY:
                raise RuntimeError("The coordination epoch did not become ready.")
            await self._store.delete(self.DRAIN_KEY)
        return {"applied": bool(apply), "epoch": self.policy.fencing_epoch, "state": "ready"}

    async def rollback_plan(self) -> dict[str, object]:
        status = await self.status()
        return {
            "schema_version": 1,
            "source_mode": "coordinated",
            "source_state": status["state"],
            "target_mode": "standalone",
            "workers": 1,
            "replicas": 1,
            "steps": (
                "drain coordinated admission",
                "preserve durable authority and evidence",
                "deploy one standalone process",
                "verify health, readiness, audit, and usage",
            ),
            "automatic_mutation": False,
        }
