"""Closed, authenticated reconciliation evidence for HA epoch transitions."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from dataclasses import asdict, dataclass, replace
from enum import StrEnum
from typing import Final

from core.coordination import validate_epoch, validate_operation_id

MAX_RECONCILIATION_PAGE_SIZE: Final = 256
MAX_RECONCILIATION_PAGES: Final = 64
MAX_RECONCILIATION_RECORDS: Final = MAX_RECONCILIATION_PAGE_SIZE * MAX_RECONCILIATION_PAGES
RECONCILIATION_SCHEMA_VERSION: Final = 1
_HEX_DIGEST = re.compile(r"[0-9a-f]{64}")
_PLAN_ID = re.compile(r"dmg_[0-9a-f]{32}")
_SIGNING_DOMAIN: Final = b"omni-ha-reconciliation-receipt-v1\x00"
_CHAIN_DOMAIN: Final = b"omni-ha-reconciliation-component-v1\x00"


class ReconciliationComponent(StrEnum):
    QUOTA = "quota_state"
    USAGE_LIABILITY = "usage_liability"
    IDENTITY_POLICY = "identity_policy"
    CACHE_INVALIDATION = "cache_invalidation"


RECONCILIATION_COMPONENTS: Final = tuple(ReconciliationComponent)


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or not _HEX_DIGEST.fullmatch(value):
        raise ValueError(f"{label} is invalid.")
    return value


def _cursor(value: object, *, required: bool) -> str | None:
    if value is None and not required:
        return None
    if (
        not isinstance(value, str)
        or not 1 <= len(value) <= 4096
        or any(ord(character) < 32 or ord(character) > 126 for character in value)
    ):
        raise ValueError("Reconciliation cursor is invalid.")
    return value


def _bounded_int(value: object, label: str, *, maximum: int) -> int:
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f"{label} is invalid.")
    return value


@dataclass(frozen=True, slots=True)
class ReconciliationPage:
    component: ReconciliationComponent
    input_cursor: str | None
    scanned: int
    complete: bool
    cursor: str | None
    snapshot_digest: str
    challenged_operations: int
    liability_nanos: int = 0
    active_reservations: int = 0

    def __post_init__(self) -> None:
        if type(self.component) is not ReconciliationComponent:
            raise ValueError("Reconciliation component is invalid.")
        _cursor(self.input_cursor, required=False)
        _bounded_int(
            self.scanned,
            "Reconciliation page count",
            maximum=MAX_RECONCILIATION_PAGE_SIZE,
        )
        if type(self.complete) is not bool or self.complete != (self.cursor is None):
            raise ValueError("Reconciliation page completion is invalid.")
        _cursor(self.cursor, required=not self.complete)
        _digest(self.snapshot_digest, "Reconciliation snapshot digest")
        if (
            type(self.challenged_operations) is not int
            or not 1 <= self.challenged_operations <= MAX_RECONCILIATION_PAGE_SIZE
        ):
            raise ValueError("Reconciliation challenge count is invalid.")
        _bounded_int(
            self.liability_nanos,
            "Reconciliation liability",
            maximum=9_223_372_036_854_775_807,
        )
        _bounded_int(
            self.active_reservations,
            "Reconciliation active reservation count",
            maximum=MAX_RECONCILIATION_PAGE_SIZE,
        )


@dataclass(frozen=True, slots=True)
class ReconciliationComponentProgress:
    component: ReconciliationComponent
    started: bool
    complete: bool
    cursor: str | None
    pages: int
    scanned: int
    challenged_operations: int
    liability_nanos: int
    active_reservations: int
    digest: str

    def __post_init__(self) -> None:
        if type(self.component) is not ReconciliationComponent:
            raise ValueError("Reconciliation component progress is invalid.")
        if type(self.started) is not bool or type(self.complete) is not bool:
            raise ValueError("Reconciliation component progress is invalid.")
        _cursor(self.cursor, required=self.started and not self.complete)
        if self.complete and self.cursor is not None:
            raise ValueError("Reconciliation component progress is invalid.")
        _bounded_int(self.pages, "Reconciliation page total", maximum=MAX_RECONCILIATION_PAGES)
        _bounded_int(
            self.scanned,
            "Reconciliation record total",
            maximum=MAX_RECONCILIATION_RECORDS,
        )
        _bounded_int(
            self.challenged_operations,
            "Reconciliation challenge total",
            maximum=MAX_RECONCILIATION_RECORDS,
        )
        _bounded_int(
            self.liability_nanos,
            "Reconciliation liability total",
            maximum=9_223_372_036_854_775_807,
        )
        _bounded_int(
            self.active_reservations,
            "Reconciliation active reservation total",
            maximum=MAX_RECONCILIATION_RECORDS,
        )
        _digest(self.digest, "Reconciliation component digest")
        if self.started != (self.pages > 0) or self.complete and not self.started:
            raise ValueError("Reconciliation component progress is invalid.")
        if not self.started and any(
            (
                self.cursor is not None,
                self.scanned,
                self.challenged_operations,
                self.liability_nanos,
                self.active_reservations,
            )
        ):
            raise ValueError("Reconciliation component progress is invalid.")

    @classmethod
    def initial(cls, component: ReconciliationComponent) -> ReconciliationComponentProgress:
        return cls(component, False, False, None, 0, 0, 0, 0, 0, "0" * 64)


_RECEIPT_KEYS: Final = frozenset(
    {
        "schema_version",
        "deployment_id",
        "namespace_digest",
        "prior_epoch",
        "target_epoch",
        "operation_id",
        "manifest_checksum",
        "migration_plan_id",
        "migration_checkpoint_revision",
        "migration_checkpoint_checksum",
        "transition_fence",
        "components",
        "signature",
    }
)
_PROGRESS_KEYS: Final = frozenset(
    {
        "component",
        "started",
        "complete",
        "cursor",
        "pages",
        "scanned",
        "challenged_operations",
        "liability_nanos",
        "active_reservations",
        "digest",
    }
)


@dataclass(frozen=True, slots=True)
class ReconciliationReceipt:
    deployment_id: str
    namespace_digest: str
    prior_epoch: int
    target_epoch: int
    operation_id: str
    manifest_checksum: str
    migration_plan_id: str
    migration_checkpoint_revision: int
    migration_checkpoint_checksum: str
    components: tuple[ReconciliationComponentProgress, ...]
    transition_fence: int = 1
    signature: str = ""
    schema_version: int = RECONCILIATION_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if (
            type(self.schema_version) is not int
            or self.schema_version != RECONCILIATION_SCHEMA_VERSION
            or not isinstance(self.deployment_id, str)
            or not 8 <= len(self.deployment_id) <= 64
        ):
            raise ValueError("Reconciliation receipt is invalid.")
        _digest(self.namespace_digest, "Reconciliation namespace digest")
        validate_epoch(self.prior_epoch)
        validate_epoch(self.target_epoch)
        if self.target_epoch != self.prior_epoch + 1:
            raise ValueError("Reconciliation receipt epoch transition is invalid.")
        validate_operation_id(self.operation_id)
        _digest(self.manifest_checksum, "Reconciliation manifest checksum")
        if not isinstance(self.migration_plan_id, str) or not _PLAN_ID.fullmatch(
            self.migration_plan_id
        ):
            raise ValueError("Reconciliation migration plan is invalid.")
        if (
            type(self.migration_checkpoint_revision) is not int
            or self.migration_checkpoint_revision < 1
        ):
            raise ValueError("Reconciliation migration checkpoint revision is invalid.")
        _digest(
            self.migration_checkpoint_checksum,
            "Reconciliation migration checkpoint checksum",
        )
        if type(self.transition_fence) is not int or self.transition_fence < 1:
            raise ValueError("Reconciliation transition fence is invalid.")
        if (
            type(self.components) is not tuple
            or tuple(item.component for item in self.components) != RECONCILIATION_COMPONENTS
        ):
            raise ValueError("Reconciliation receipt components are invalid.")
        if self.signature and not _HEX_DIGEST.fullmatch(self.signature):
            raise ValueError("Reconciliation receipt signature is invalid.")

    @property
    def complete(self) -> bool:
        return all(item.complete and item.challenged_operations > 0 for item in self.components)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "deployment_id": self.deployment_id,
            "namespace_digest": self.namespace_digest,
            "prior_epoch": self.prior_epoch,
            "target_epoch": self.target_epoch,
            "operation_id": self.operation_id,
            "manifest_checksum": self.manifest_checksum,
            "migration_plan_id": self.migration_plan_id,
            "migration_checkpoint_revision": self.migration_checkpoint_revision,
            "migration_checkpoint_checksum": self.migration_checkpoint_checksum,
            "transition_fence": self.transition_fence,
            "components": [
                {**asdict(component), "component": component.component.value}
                for component in self.components
            ],
            "signature": self.signature,
        }

    @classmethod
    def from_dict(cls, value: object) -> ReconciliationReceipt:
        if not isinstance(value, dict) or set(value) != _RECEIPT_KEYS:
            raise ValueError("Reconciliation receipt is invalid.")
        components = value["components"]
        if not isinstance(components, list):
            raise ValueError("Reconciliation receipt is invalid.")
        decoded: list[ReconciliationComponentProgress] = []
        for item in components:
            if not isinstance(item, dict) or set(item) != _PROGRESS_KEYS:
                raise ValueError("Reconciliation receipt is invalid.")
            try:
                decoded.append(
                    ReconciliationComponentProgress(
                        **{
                            **item,
                            "component": ReconciliationComponent(item["component"]),
                        }
                    )
                )
            except (TypeError, ValueError) as exc:
                raise ValueError("Reconciliation receipt is invalid.") from exc
        try:
            return cls(
                deployment_id=value["deployment_id"],
                namespace_digest=value["namespace_digest"],
                prior_epoch=value["prior_epoch"],
                target_epoch=value["target_epoch"],
                operation_id=value["operation_id"],
                manifest_checksum=value["manifest_checksum"],
                migration_plan_id=value["migration_plan_id"],
                migration_checkpoint_revision=value["migration_checkpoint_revision"],
                migration_checkpoint_checksum=value["migration_checkpoint_checksum"],
                components=tuple(decoded),
                transition_fence=value["transition_fence"],
                signature=value["signature"],
                schema_version=value["schema_version"],
            )
        except (TypeError, ValueError) as exc:
            raise ValueError("Reconciliation receipt is invalid.") from exc


def new_reconciliation_receipt(
    *,
    deployment_id: str,
    namespace_digest: str,
    prior_epoch: int,
    target_epoch: int,
    operation_id: str,
    manifest_checksum: str,
    migration_plan_id: str,
    migration_checkpoint_revision: int,
    migration_checkpoint_checksum: str,
    transition_fence: int = 1,
) -> ReconciliationReceipt:
    return ReconciliationReceipt(
        deployment_id=deployment_id,
        namespace_digest=namespace_digest,
        prior_epoch=prior_epoch,
        target_epoch=target_epoch,
        operation_id=operation_id,
        manifest_checksum=manifest_checksum,
        migration_plan_id=migration_plan_id,
        migration_checkpoint_revision=migration_checkpoint_revision,
        migration_checkpoint_checksum=migration_checkpoint_checksum,
        components=tuple(
            ReconciliationComponentProgress.initial(component)
            for component in RECONCILIATION_COMPONENTS
        ),
        transition_fence=transition_fence,
    )


def advance_reconciliation_receipt(
    receipt: ReconciliationReceipt,
    page: ReconciliationPage,
) -> ReconciliationReceipt:
    if type(receipt) is not ReconciliationReceipt or type(page) is not ReconciliationPage:
        raise ValueError("Reconciliation receipt update is invalid.")
    if page.component is ReconciliationComponent.USAGE_LIABILITY and (
        page.liability_nanos != 0 or page.active_reservations != 0
    ):
        raise ValueError("Outstanding durable liability prevents reconciliation progress.")
    active_index = next(
        (index for index, item in enumerate(receipt.components) if not item.complete),
        None,
    )
    if active_index is None or receipt.components[active_index].component is not page.component:
        raise ValueError("Reconciliation component order is invalid.")
    progress = receipt.components[active_index]
    if page.input_cursor != progress.cursor:
        raise ValueError("Reconciliation page cursor is invalid.")
    if progress.pages >= MAX_RECONCILIATION_PAGES:
        raise ValueError("Reconciliation page limit is exceeded.")
    payload = json.dumps(
        {
            "component": page.component.value,
            "input_cursor": page.input_cursor,
            "scanned": page.scanned,
            "complete": page.complete,
            "cursor": page.cursor,
            "snapshot_digest": page.snapshot_digest,
            "challenged_operations": page.challenged_operations,
            "liability_nanos": page.liability_nanos,
            "active_reservations": page.active_reservations,
        },
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    chain = hashlib.sha256(_CHAIN_DOMAIN + bytes.fromhex(progress.digest) + payload).hexdigest()
    updated = replace(
        progress,
        started=True,
        complete=page.complete,
        cursor=page.cursor,
        pages=progress.pages + 1,
        scanned=progress.scanned + page.scanned,
        challenged_operations=progress.challenged_operations + page.challenged_operations,
        liability_nanos=progress.liability_nanos + page.liability_nanos,
        active_reservations=progress.active_reservations + page.active_reservations,
        digest=chain,
    )
    components = list(receipt.components)
    components[active_index] = updated
    return replace(receipt, components=tuple(components), signature="")


def _unsigned_payload(receipt: ReconciliationReceipt) -> bytes:
    value = receipt.to_dict()
    value["signature"] = ""
    return json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")


def sign_reconciliation_receipt(
    receipt: ReconciliationReceipt, signing_key: bytes
) -> ReconciliationReceipt:
    if not isinstance(signing_key, bytes) or len(signing_key) < 32:
        raise ValueError("A reconciliation signing key is required.")
    signature = hmac.digest(
        signing_key,
        _SIGNING_DOMAIN + _unsigned_payload(receipt),
        hashlib.sha256,
    ).hex()
    return replace(receipt, signature=signature)


def verify_reconciliation_receipt_signature(
    receipt: ReconciliationReceipt,
    signing_key: bytes,
) -> bool:
    if (
        type(receipt) is not ReconciliationReceipt
        or not isinstance(signing_key, bytes)
        or len(signing_key) < 32
        or not _HEX_DIGEST.fullmatch(receipt.signature)
    ):
        return False
    expected = hmac.digest(
        signing_key,
        _SIGNING_DOMAIN + _unsigned_payload(receipt),
        hashlib.sha256,
    ).hex()
    return hmac.compare_digest(receipt.signature, expected)


def verify_reconciliation_receipt(receipt: ReconciliationReceipt, signing_key: bytes) -> bool:
    return receipt.complete and verify_reconciliation_receipt_signature(receipt, signing_key)


def reconciliation_receipt_checksum(receipt: ReconciliationReceipt) -> str:
    if type(receipt) is not ReconciliationReceipt or not receipt.complete or not receipt.signature:
        raise ValueError("Complete signed reconciliation evidence is required.")
    logical = receipt.to_dict()
    logical.pop("transition_fence")
    logical.pop("signature")
    return hashlib.sha256(
        b"omni-ha-reconciliation-checksum-v1\x00"
        + json.dumps(logical, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


class HaReconciliationCoordinator:
    """Collect exactly one bounded component page from production owners per call."""

    def __init__(self, storage: object, store: object) -> None:
        if storage is None or store is None:
            raise ValueError("Reconciliation owners are required.")
        self._storage = storage
        self._store = store

    async def next_page(
        self,
        receipt: ReconciliationReceipt,
        *,
        limit: int,
        apply: bool,
    ) -> ReconciliationPage:
        if type(limit) is not int or not 1 <= limit <= MAX_RECONCILIATION_PAGE_SIZE:
            raise ValueError("Reconciliation page size is invalid.")
        progress = next((item for item in receipt.components if not item.complete), None)
        if progress is None:
            raise ValueError("Reconciliation receipt is already complete.")
        if progress.component is ReconciliationComponent.QUOTA:
            quota_operation = (
                "qrc_"
                + hashlib.sha256(
                    b"omni-ha-quota-reconciliation-operation-v1\x00"
                    + receipt.operation_id.encode("utf-8")
                    + b"\x00"
                    + str(receipt.target_epoch).encode("ascii")
                    + b"\x00"
                    + (progress.cursor or "").encode("utf-8")
                    + b"\x00"
                    + str(progress.pages).encode("ascii")
                    + b"\x00"
                    + str(limit).encode("ascii")
                ).hexdigest()[:32]
            )
            result = await self._store.reconcile_quota_state(
                epoch=receipt.target_epoch,
                cursor=progress.cursor,
                limit=limit,
                apply=apply,
                operation_id=quota_operation,
            )
            return ReconciliationPage(
                progress.component,
                progress.cursor,
                result.scanned,
                result.complete,
                result.cursor,
                result.snapshot_digest,
                1,
            )
        if progress.component is ReconciliationComponent.USAGE_LIABILITY:
            repository = await self._storage.create_usage_ledger_repository()
            page = await repository.reconciliation_page(after=progress.cursor, limit=limit)
            return ReconciliationPage(
                progress.component,
                progress.cursor,
                page.scanned,
                page.complete,
                page.cursor,
                page.snapshot_digest,
                1,
                page.active_liability_nanos,
                page.active_reservations,
            )
        if progress.component is ReconciliationComponent.IDENTITY_POLICY:
            from core.identity.repository import IdentityPageCursor

            repository = await self._storage.create_identity_repository()
            after = None
            if progress.cursor is not None:
                try:
                    created_at, identity_id = progress.cursor.split("|", 1)
                    after = IdentityPageCursor(created_at, identity_id)
                except (TypeError, ValueError) as exc:
                    raise ValueError("Identity reconciliation cursor is invalid.") from exc
            page_limit = min(limit, 199)
            rows = await repository.list_identities(limit=page_limit + 1, after=after)
            identities = rows[:page_limit]
            complete = len(rows) <= page_limit
            cursor = None
            if not complete:
                last = identities[-1].identity
                cursor = f"{last.created_at}|{last.identity_id}"
            policy = await repository.get_oidc_policy_revision()
            sessions = await self._store.read_session_reconciliation(epoch=receipt.target_epoch)
            if sessions.active_count != 0:
                raise ValueError("Prior-epoch management sessions remain active.")
            payload = {
                "identities": [
                    {
                        "identity": item.identity.to_record(),
                        "binding": item.binding.to_record(),
                    }
                    for item in identities
                ],
                "oidc_policy": policy.to_record(),
                "session_digest": sessions.digest,
                "active_sessions": sessions.active_count,
            }
            return ReconciliationPage(
                progress.component,
                progress.cursor,
                len(identities),
                complete,
                cursor,
                self._snapshot_digest("identity", payload),
                1,
            )
        if progress.component is ReconciliationComponent.CACHE_INVALIDATION:
            if progress.started:
                raise ValueError("Cache reconciliation must complete in one bounded page.")
            from core.routing_coordination import VALID_INVALIDATION_SCOPES

            generations = {}
            for scope in sorted(VALID_INVALIDATION_SCOPES):
                generation = await self._store.read_invalidation_generation(scope)
                if generation.generation is None or generation.generation < 1:
                    raise ValueError("Cache invalidation authority is incomplete.")
                generations[scope] = generation.generation
            return ReconciliationPage(
                progress.component,
                None,
                len(generations),
                True,
                None,
                self._snapshot_digest("cache", generations),
                1,
            )
        raise ValueError("Reconciliation component is invalid.")

    @staticmethod
    def _snapshot_digest(domain: str, value: object) -> str:
        payload = json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
        return hashlib.sha256(
            b"omni-ha-reconciliation-snapshot-v1\x00" + domain.encode("ascii") + b"\x00" + payload
        ).hexdigest()
