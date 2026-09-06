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
from core.ha_reconciliation import (
    HaReconciliationCoordinator,
    ReconciliationReceipt,
    advance_reconciliation_receipt,
    new_reconciliation_receipt,
    reconciliation_receipt_checksum,
    sign_reconciliation_receipt,
    verify_reconciliation_receipt,
    verify_reconciliation_receipt_signature,
)
from core.ha_runtime_policy import HaRuntimePolicy, RuntimeMode


class HaRuntimeOperator:
    """Operate one coordinated epoch while preserving durable authority."""

    DRAIN_KEY: Final = ADMISSION_FENCE_KEY
    RECEIPT_KEY: Final = "ha_reconciliation_receipt_v1"
    RECONCILIATION_LOCK_KEY: Final = "ha-reconciliation-transition-v1"
    RECONCILIATION_FENCE_KEY: Final = "ha-reconciliation-fence-v1"
    RECONCILIATION_LOCK_TTL_SECONDS: Final = 120.0
    RECONCILIATION_RECEIPT_SEARCH_LIMIT: Final = 512

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
        self._reconciliation = HaReconciliationCoordinator(storage, store)

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

    @classmethod
    def _receipt_storage_key(cls, transition_fence: int) -> str:
        if type(transition_fence) is not int or transition_fence < 1:
            raise ValueError("Reconciliation transition fence is invalid.")
        return f"{cls.RECEIPT_KEY}:{transition_fence}"

    async def _current_transition_fence(self) -> int:
        value = await self._store.get(self.RECONCILIATION_FENCE_KEY)
        if value is None:
            return 0
        if isinstance(value, bool) or not isinstance(value, (int, str)) or not str(value).isdigit():
            raise RuntimeError("Reconciliation transition fence is invalid.")
        fence = int(value)
        if fence < 1:
            raise RuntimeError("Reconciliation transition fence is invalid.")
        return fence

    async def _assert_transition_fence(self, transition_fence: int) -> None:
        if await self._current_transition_fence() != transition_fence:
            raise RuntimeError("Reconciliation transition ownership is stale.")

    async def _receipt(self) -> ReconciliationReceipt | None:
        current = await self._current_transition_fence()
        for transition_fence in range(
            current,
            max(0, current - self.RECONCILIATION_RECEIPT_SEARCH_LIMIT),
            -1,
        ):
            value = await self._storage.get_config(
                self._receipt_storage_key(transition_fence), None
            )
            if value is None:
                continue
            try:
                receipt = ReconciliationReceipt.from_dict(value)
            except ValueError as exc:
                raise RuntimeError("Stored reconciliation evidence is invalid.") from exc
            if receipt.transition_fence != transition_fence:
                raise RuntimeError("Stored reconciliation evidence fence is invalid.")
            return receipt
        return None

    async def _write_internal(self, key: str, value: object) -> None:
        writer = getattr(self._storage, "set_internal_config", None)
        if writer is None:
            writer = self._storage.set_config
        if not await writer(key, value):
            raise RuntimeError("Durable reconciliation evidence could not be stored.")

    def _validate_receipt(
        self,
        receipt: ReconciliationReceipt | None,
        binding: CoordinationBinding,
    ) -> ReconciliationReceipt:
        if (
            receipt is None
            or not self._receipt_matches_binding(receipt, binding)
            or self.policy.coordination_key is None
            or not verify_reconciliation_receipt(receipt, self.policy.coordination_key)
        ):
            raise RuntimeError("Complete matching reconciliation evidence is required.")
        return receipt

    @staticmethod
    def _receipt_matches_binding(
        receipt: ReconciliationReceipt,
        binding: CoordinationBinding,
    ) -> bool:
        return (
            receipt.deployment_id == binding.deployment_id
            and receipt.namespace_digest == binding.namespace_digest
            and receipt.prior_epoch == binding.fencing_epoch - 1
            and receipt.target_epoch == binding.fencing_epoch
            and receipt.manifest_checksum == binding.manifest_checksum
            and receipt.migration_plan_id == binding.migration_plan_id
            and receipt.migration_checkpoint_revision == binding.migration_checkpoint_revision
            and receipt.migration_checkpoint_checksum == binding.migration_checkpoint_checksum
        )

    @staticmethod
    def _encode_record(value: dict[str, object]) -> str:
        return json.dumps(value, separators=(",", ":"), sort_keys=True)

    async def status(self) -> dict[str, object]:
        durable = await self._durable_binding()
        shared = await self._shared_binding()
        epoch = await self._store.read_epoch()
        drain = await self._drain_record()
        expected = await self._bindings.expected_for_binding(self.policy, durable)
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
            "reconciliation_complete": bool(drain is not None and drain["reconciliation_complete"]),
            "reconciliation_receipt_present": (await self._receipt()) is not None,
            "activation_accepted": self._activation_verifier(durable.activation_record),
        }

    async def drain(self, *, apply: bool = False) -> dict[str, object]:
        binding = await self._bindings.verify(self.policy)
        self._activation_required(binding.activation_record)
        record = {
            "schema_version": 3,
            "namespace_digest": binding.namespace_digest,
            "epoch": binding.fencing_epoch,
            "reconciliation_receipt_checksum": None,
            "reconciliation_complete": False,
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
        expected = await self._bindings.expected_for_binding(self.policy, binding)
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
        self,
        operation_id: str,
        *,
        apply: bool = False,
        page_size: int = 256,
    ) -> dict[str, object]:
        if not apply:
            return await self._reconcile_locked(operation_id, apply=False, page_size=page_size)
        if not await self._store.acquire_lock(
            self.RECONCILIATION_LOCK_KEY,
            ttl_seconds=self.RECONCILIATION_LOCK_TTL_SECONDS,
        ):
            raise RuntimeError("Another reconciliation transition is in progress.")
        try:
            transition_fence = await self._store.increment(self.RECONCILIATION_FENCE_KEY)
            return await self._reconcile_locked(
                operation_id,
                apply=True,
                page_size=page_size,
                transition_fence=transition_fence,
            )
        finally:
            await self._store.release_lock(self.RECONCILIATION_LOCK_KEY)

    async def _reconcile_locked(
        self,
        operation_id: str,
        *,
        apply: bool,
        page_size: int,
        transition_fence: int | None = None,
    ) -> dict[str, object]:
        durable = await self._durable_binding()
        shared = await self._shared_binding()
        self._activation_required(durable.activation_record)
        expected = await self._bindings.expected_for_binding(self.policy, durable)
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
            if durable == prior:
                await self._write_internal(self._bindings.DURABLE_KEY, expected.to_dict())
        receipt = await self._receipt()
        if receipt is not None and receipt.target_epoch != expected.fencing_epoch:
            if (
                receipt.complete
                and receipt.target_epoch == prior.fencing_epoch
                and receipt.deployment_id == expected.deployment_id
                and receipt.namespace_digest == expected.namespace_digest
                and self.policy.coordination_key is not None
                and verify_reconciliation_receipt(receipt, self.policy.coordination_key)
            ):
                receipt = None
            else:
                raise RuntimeError("Stored reconciliation evidence is stale or incomplete.")
        if receipt is None:
            receipt = new_reconciliation_receipt(
                deployment_id=expected.deployment_id,
                namespace_digest=expected.namespace_digest,
                prior_epoch=prior.fencing_epoch,
                target_epoch=expected.fencing_epoch,
                operation_id=operation_id,
                manifest_checksum=expected.manifest_checksum,
                migration_plan_id=expected.migration_plan_id,
                migration_checkpoint_revision=expected.migration_checkpoint_revision,
                migration_checkpoint_checksum=expected.migration_checkpoint_checksum,
                transition_fence=transition_fence or max(1, await self._current_transition_fence()),
            )
        elif self.policy.coordination_key is None or not verify_reconciliation_receipt_signature(
            receipt,
            self.policy.coordination_key,
        ):
            raise RuntimeError("Stored reconciliation evidence is not authentic.")
        elif not self._receipt_matches_binding(receipt, expected):
            raise RuntimeError("Stored reconciliation evidence does not match the binding.")
        elif receipt.operation_id != operation_id:
            raise RuntimeError("Reconciliation operation identity does not match.")
        if receipt.complete:
            self._validate_receipt(receipt, expected)
            if apply:
                if transition_fence is None or self.policy.coordination_key is None:
                    raise RuntimeError("Reconciliation transition fence is unavailable.")
                await self._assert_transition_fence(transition_fence)
                receipt = sign_reconciliation_receipt(
                    replace(receipt, transition_fence=transition_fence, signature=""),
                    self.policy.coordination_key,
                )
            page = None
        else:
            if apply:
                if transition_fence is None:
                    raise RuntimeError("Reconciliation transition fence is unavailable.")
                await self._assert_transition_fence(transition_fence)
                receipt = replace(receipt, transition_fence=transition_fence, signature="")
            page = await self._reconciliation.next_page(
                receipt,
                limit=page_size,
                apply=apply,
            )
            receipt = advance_reconciliation_receipt(receipt, page)
            if apply:
                await self._assert_transition_fence(transition_fence)
            if self.policy.coordination_key is None:
                raise RuntimeError("Reconciliation signing key is unavailable.")
            receipt = sign_reconciliation_receipt(receipt, self.policy.coordination_key)
        if apply:
            if transition_fence is None or receipt.transition_fence != transition_fence:
                raise RuntimeError("Reconciliation transition fence is unavailable.")
            await self._assert_transition_fence(transition_fence)
            await self._write_internal(
                self._receipt_storage_key(transition_fence), receipt.to_dict()
            )
            await self._assert_transition_fence(transition_fence)
            checksum = reconciliation_receipt_checksum(receipt) if receipt.complete else None
            if receipt.complete:
                updated_drain = {
                    **drain,
                    "reconciliation_receipt_checksum": checksum,
                    "reconciliation_complete": True,
                }
                await self._store.set(self.DRAIN_KEY, self._encode_record(updated_drain))
        active = next((item for item in receipt.components if not item.complete), None)
        return {
            "applied": bool(apply),
            "epoch": expected.fencing_epoch,
            "state": "reconciling",
            "component": None if page is None else page.component.value,
            "scanned": 0 if page is None else page.scanned,
            "reconciliation_complete": receipt.complete,
            "next_component": None if active is None else active.component.value,
            "cursor_present": bool(active is not None and active.cursor is not None),
        }

    async def mark_ready(self, operation_id: str, *, apply: bool = False) -> dict[str, object]:
        if not apply:
            return await self._mark_ready_locked(operation_id, apply=False)
        if not await self._store.acquire_lock(
            self.RECONCILIATION_LOCK_KEY,
            ttl_seconds=self.RECONCILIATION_LOCK_TTL_SECONDS,
        ):
            raise RuntimeError("Another reconciliation transition is in progress.")
        try:
            transition_fence = await self._store.increment(self.RECONCILIATION_FENCE_KEY)
            return await self._mark_ready_locked(
                operation_id, apply=True, transition_fence=transition_fence
            )
        finally:
            await self._store.release_lock(self.RECONCILIATION_LOCK_KEY)

    async def _mark_ready_locked(
        self,
        operation_id: str,
        *,
        apply: bool,
        transition_fence: int | None = None,
    ) -> dict[str, object]:
        epoch = await self._store.read_epoch()
        if epoch.epoch == self.policy.fencing_epoch and epoch.state is EpochState.READY:
            binding = await self._bindings.verify(self.policy)
            self._activation_required(binding.activation_record)
            receipt = self._validate_receipt(await self._receipt(), binding)
            drain = await self._drain_record()
            if drain is not None:
                if (
                    drain["epoch"] != epoch.epoch - 1
                    or drain["namespace_digest"] != binding.namespace_digest
                    or not drain["reconciliation_complete"]
                    or drain["reconciliation_receipt_checksum"]
                    != reconciliation_receipt_checksum(receipt)
                ):
                    raise RuntimeError(
                        "A matching completed drain is required before marking ready."
                    )
                if apply:
                    if transition_fence is None:
                        raise RuntimeError("Reconciliation transition fence is unavailable.")
                    await self._assert_transition_fence(transition_fence)
                    await self._store.complete_admission_drain(
                        AdmissionFence.decode(drain), epoch=epoch.epoch, operation_id=operation_id
                    )
            return {"applied": bool(apply), "epoch": epoch.epoch, "state": "ready"}
        durable = await self._durable_binding()
        shared = await self._shared_binding()
        expected = await self._bindings.expected_for_binding(self.policy, durable)
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
        receipt = self._validate_receipt(await self._receipt(), expected)
        if not drain["reconciliation_complete"] or drain[
            "reconciliation_receipt_checksum"
        ] != reconciliation_receipt_checksum(receipt):
            raise RuntimeError("Complete reconciliation is required before marking ready.")
        if epoch.epoch != self.policy.fencing_epoch or epoch.state is not EpochState.RECONCILING:
            raise RuntimeError("The expected reconciling epoch is unavailable.")
        if apply:
            if transition_fence is None:
                raise RuntimeError("Reconciliation transition fence is unavailable.")
            await self._assert_transition_fence(transition_fence)
            epoch = await self._store.mark_epoch_ready(self.policy.fencing_epoch, operation_id)
            if epoch.state is not EpochState.READY:
                raise RuntimeError("The coordination epoch did not become ready.")
            await self._store.complete_admission_drain(
                AdmissionFence.decode(drain), epoch=epoch.epoch, operation_id=operation_id
            )
        return {"applied": bool(apply), "epoch": self.policy.fencing_epoch, "state": "ready"}

    async def rollback_plan(self) -> dict[str, object]:
        binding = await self._durable_binding()
        shared = await self._shared_binding()
        expected = await self._bindings.expected_for_binding(self.policy, binding)
        self._activation_required(binding.activation_record)
        if binding != expected or shared != expected:
            raise RuntimeError("Reconciled bindings are required before rollback.")
        epoch = await self._store.read_epoch()
        if epoch.epoch != expected.fencing_epoch or epoch.state is not EpochState.RECONCILING:
            raise RuntimeError("Rollback requires an active completed drain.")
        receipt = self._validate_receipt(await self._receipt(), expected)
        drain = await self._drain_record()
        if (
            drain is None
            or drain["epoch"] != expected.fencing_epoch - 1
            or drain["namespace_digest"] != expected.namespace_digest
            or not drain["reconciliation_complete"]
            or drain["reconciliation_receipt_checksum"] != reconciliation_receipt_checksum(receipt)
        ):
            raise RuntimeError("Rollback requires an active completed drain.")
        return {
            "schema_version": 2,
            "source_mode": "coordinated",
            "source_state": "reconciling",
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
            "reconciliation_receipt_checksum": reconciliation_receipt_checksum(receipt),
        }
