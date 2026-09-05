"""Dry-run-first, bounded HA lifecycle transitions without data deletion."""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from typing import Any, Callable, Final

from core.coordination import ADMISSION_FENCE_KEY, AdmissionFence, EpochState
from core.ha_coordination_binding import (
    CoordinationBinding,
    CoordinationBindingManager,
    HaBindingError,
)
from core.ha_runtime_policy import HaRuntimePolicy, RuntimeMode


class HaRuntimeOperator:
    """Operate one coordinated epoch while preserving durable authority."""

    DRAIN_KEY: Final = ADMISSION_FENCE_KEY

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
        return self._bindings.decode_record(value, "durable_binding_corrupt")

    async def _shared_binding(self) -> CoordinationBinding:
        value = await self._store.get(self._bindings.STORE_KEY)
        if value is None:
            raise HaBindingError("namespace_missing")
        return self._bindings.decode_record(value, "coordination_binding_corrupt")

    async def _drain_record(self) -> dict[str, object] | None:
        value = await self._store.get(self.DRAIN_KEY)
        if value is None:
            return None
        return asdict(AdmissionFence.decode(value))

    @staticmethod
    def _encode_record(value: dict[str, object]) -> str:
        return json.dumps(value, separators=(",", ":"), sort_keys=True)

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
            "quota_reconciliation_complete": bool(
                drain is not None and drain["quota_reconciliation_complete"]
            ),
            "quota_cursor_present": bool(
                drain is not None and drain["quota_reconciliation_cursor"] is not None
            ),
            "activation_accepted": self._activation_verifier(durable.activation_record),
        }

    async def drain(self, *, apply: bool = False) -> dict[str, object]:
        binding = await self._bindings.verify(self.policy)
        self._activation_required(binding.activation_record)
        record = {
            "schema_version": 2,
            "namespace_digest": binding.namespace_digest,
            "epoch": binding.fencing_epoch,
            "quota_reconciliation_cursor": "pending",
            "quota_reconciliation_complete": False,
        }
        existing = await self._drain_record()
        if existing is not None and existing != record:
            raise RuntimeError("The drain record does not match the active binding.")
        if apply and existing is None:
            await self._store.set(self.DRAIN_KEY, self._encode_record(record))
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

    async def reconcile(
        self, *, apply: bool = False, quota_page_size: int = 256
    ) -> dict[str, object]:
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
                await self._store.set(
                    self._bindings.STORE_KEY,
                    self._bindings.encode_record(expected),
                )
            if durable == prior and not await self._storage.set_config(
                self._bindings.DURABLE_KEY, expected.to_dict()
            ):
                raise RuntimeError("The durable binding update failed.")
        quota = await self._store.reconcile_quota_state(
            epoch=expected.fencing_epoch,
            cursor=None
            if drain["quota_reconciliation_cursor"] == "pending"
            else drain["quota_reconciliation_cursor"],
            limit=quota_page_size,
            apply=apply,
        )
        if apply:
            updated_drain = {
                **drain,
                "quota_reconciliation_cursor": quota.cursor,
                "quota_reconciliation_complete": quota.complete,
            }
            await self._store.set(self.DRAIN_KEY, self._encode_record(updated_drain))
        return {
            "applied": bool(apply),
            "epoch": expected.fencing_epoch,
            "state": "reconciling",
            "quota_scanned": quota.scanned,
            "quota_complete": quota.complete,
            "quota_cursor_present": quota.cursor is not None,
        }

    async def mark_ready(self, operation_id: str, *, apply: bool = False) -> dict[str, object]:
        epoch = await self._store.read_epoch()
        if epoch.epoch == self.policy.fencing_epoch and epoch.state is EpochState.READY:
            binding = await self._bindings.verify(self.policy)
            self._activation_required(binding.activation_record)
            drain = await self._drain_record()
            if drain is not None:
                if (
                    drain["epoch"] != epoch.epoch - 1
                    or drain["namespace_digest"] != binding.namespace_digest
                    or not drain["quota_reconciliation_complete"]
                ):
                    raise RuntimeError(
                        "A matching completed drain is required before marking ready."
                    )
                if apply:
                    await self._store.complete_admission_drain(
                        AdmissionFence.decode(drain), epoch=epoch.epoch, operation_id=operation_id
                    )
            return {"applied": bool(apply), "epoch": epoch.epoch, "state": "ready"}
        durable = await self._durable_binding()
        shared = await self._shared_binding()
        expected = CoordinationBinding.for_policy(self.policy, durable.activation_record)
        self._activation_required(durable.activation_record)
        if durable != expected or shared != expected:
            raise RuntimeError("Reconciled bindings are required before marking ready.")
        drain = await self._drain_record()
        if (
            drain is None
            or drain["epoch"] != self.policy.fencing_epoch - 1
            or drain["namespace_digest"] != expected.namespace_digest
        ):
            raise RuntimeError("A matching drain is required before marking ready.")
        if not drain["quota_reconciliation_complete"]:
            raise RuntimeError("Complete quota reconciliation is required before marking ready.")
        if epoch.epoch != self.policy.fencing_epoch or epoch.state is not EpochState.RECONCILING:
            raise RuntimeError("The expected reconciling epoch is unavailable.")
        confirmation = await self._store.reconcile_quota_state(
            epoch=self.policy.fencing_epoch,
            cursor=None,
            limit=1,
            apply=apply,
        )
        if apply:
            drain = {
                **drain,
                "quota_reconciliation_cursor": confirmation.cursor,
                "quota_reconciliation_complete": confirmation.complete,
            }
            await self._store.set(self.DRAIN_KEY, self._encode_record(drain))
        if not confirmation.complete:
            raise RuntimeError("Complete quota reconciliation is required before marking ready.")
        if apply:
            epoch = await self._store.mark_epoch_ready(self.policy.fencing_epoch, operation_id)
            if epoch.state is not EpochState.READY:
                raise RuntimeError("The coordination epoch did not become ready.")
            await self._store.complete_admission_drain(
                AdmissionFence.decode(drain), epoch=epoch.epoch, operation_id=operation_id
            )
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
