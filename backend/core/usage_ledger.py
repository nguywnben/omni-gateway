"""Strict W4.14 usage/cost ledger and durable hard-budget journal domain."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, fields
from decimal import ROUND_CEILING, Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, Mapping

from core.quality_decision import COMPRESSION_REASONS, MAX_POLICY_REVISION, QUALITY_PROFILES

USAGE_LEDGER_SCHEMA_VERSION = 1
NANOS_PER_USD = 1_000_000_000
MAX_COST_NANOS = 9_000_000_000_000_000_000
MAX_RESERVATION_TTL_SECONDS = 86_400.0

_EVENT_ID = re.compile(r"use_[0-9a-f]{32}")
_RESERVATION_ID = re.compile(r"qrs_[0-9a-f]{32}")
_KEY_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")
_SAFE_REQUEST_ID = re.compile(r"[A-Za-z0-9._:-]{0,128}")
_QUALITY_PROFILES = frozenset(QUALITY_PROFILES)
_COMPRESSION_REASONS = frozenset(COMPRESSION_REASONS) | {"unknown"}


def _strict_int(value: object, label: str, *, minimum: int = 0, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(f"{label} is invalid.")
    return value


def _timestamp(value: object, label: str) -> float:
    if type(value) not in {int, float}:
        raise ValueError(f"{label} is invalid.")
    timestamp = float(value)
    if not math.isfinite(timestamp) or timestamp < 0:
        raise ValueError(f"{label} is invalid.")
    return timestamp


def _bounded_text(value: object, label: str, *, maximum: int, required: bool = False) -> str:
    if not isinstance(value, str) or len(value) > maximum or (required and not value):
        raise ValueError(f"{label} is invalid.")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise ValueError(f"{label} is invalid.")
    return value


def _optional_cost(value: object, label: str) -> int | None:
    if value is None:
        return None
    return _strict_int(value, label, maximum=MAX_COST_NANOS)


def usd_to_nanos(value: object) -> int:
    """Convert a non-negative USD value conservatively to integer nano-USD."""

    if isinstance(value, bool):
        raise ValueError("USD cost is invalid.")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError("USD cost is invalid.") from exc
    if not amount.is_finite() or amount < 0:
        raise ValueError("USD cost is invalid.")
    nanos = int((amount * NANOS_PER_USD).to_integral_value(rounding=ROUND_CEILING))
    if nanos > MAX_COST_NANOS:
        raise ValueError("USD cost is invalid.")
    return nanos


def nanos_to_usd(value: int) -> float:
    nanos = _strict_int(value, "Nano-USD cost", maximum=MAX_COST_NANOS)
    return float(Decimal(nanos) / NANOS_PER_USD)


@dataclass(frozen=True, slots=True)
class UsageLedgerEntry:
    schema_version: int
    event_id: str
    occurred_at: float
    credential_ref: str
    request_id: str
    model: str
    provider: str
    status_code: int
    success: bool
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cached_tokens: int
    reasoning_tokens: int
    estimated_input_tokens: int
    estimated_tokens_saved: int
    compressed_messages: int
    quality_profile: str
    quality_policy_revision: int
    compression_reason: str
    latency_ms: int
    retry_count: int
    cost_nanos: int
    api_key_id: str

    def __post_init__(self) -> None:
        if (
            type(self.schema_version) is not int
            or self.schema_version != USAGE_LEDGER_SCHEMA_VERSION
        ):
            raise ValueError("Usage ledger schema version is unsupported.")
        if not isinstance(self.event_id, str) or not _EVENT_ID.fullmatch(self.event_id):
            raise ValueError("Usage event ID is invalid.")
        object.__setattr__(self, "occurred_at", _timestamp(self.occurred_at, "Usage timestamp"))
        credential_ref = _bounded_text(
            self.credential_ref, "Usage credential reference", maximum=255, required=True
        )
        if credential_ref in {".", ".."} or "/" in credential_ref or "\\" in credential_ref:
            raise ValueError("Usage credential reference is invalid.")
        if not isinstance(self.request_id, str) or not _SAFE_REQUEST_ID.fullmatch(self.request_id):
            raise ValueError("Usage request ID is invalid.")
        _bounded_text(self.model, "Usage model", maximum=256)
        _bounded_text(self.provider, "Usage provider", maximum=64)
        _strict_int(self.status_code, "Usage status code", minimum=100, maximum=599)
        if type(self.success) is not bool:
            raise ValueError("Usage success flag is invalid.")
        for value, label in (
            (self.input_tokens, "Usage input tokens"),
            (self.output_tokens, "Usage output tokens"),
            (self.total_tokens, "Usage total tokens"),
            (self.cached_tokens, "Usage cached tokens"),
            (self.reasoning_tokens, "Usage reasoning tokens"),
            (self.estimated_input_tokens, "Usage estimated input tokens"),
            (self.estimated_tokens_saved, "Usage estimated tokens saved"),
            (self.compressed_messages, "Usage compressed messages"),
            (self.latency_ms, "Usage latency"),
            (self.retry_count, "Usage retry count"),
        ):
            _strict_int(value, label, maximum=9_223_372_036_854_775_807)
        if self.quality_profile not in _QUALITY_PROFILES:
            raise ValueError("Usage quality profile is invalid.")
        _strict_int(
            self.quality_policy_revision,
            "Usage quality policy revision",
            maximum=MAX_POLICY_REVISION,
        )
        if self.compression_reason not in _COMPRESSION_REASONS:
            raise ValueError("Usage compression reason is invalid.")
        _strict_int(self.cost_nanos, "Usage cost", maximum=MAX_COST_NANOS)
        if self.api_key_id and (
            not isinstance(self.api_key_id, str) or not _KEY_ID.fullmatch(self.api_key_id)
        ):
            raise ValueError("Usage virtual-key ID is invalid.")

    def __repr__(self) -> str:
        return (
            "UsageLedgerEntry("
            f"schema_version={self.schema_version!r}, event_id={self.event_id!r}, "
            f"occurred_at={self.occurred_at!r}, attribution=<redacted>, "
            f"success={self.success!r}, total_tokens={self.total_tokens!r}, "
            f"cost_nanos={self.cost_nanos!r})"
        )

    def to_record(self) -> dict[str, object]:
        return {field.name: getattr(self, field.name) for field in fields(self)}


class BudgetReservationState(StrEnum):
    ACTIVE = "active"
    COMMITTED = "committed"
    RELEASED = "released"
    EXPIRED = "expired"


@dataclass(frozen=True, slots=True)
class BudgetReservationRequest:
    schema_version: int
    reservation_id: str
    key_id: str
    created_at: float
    expires_at: float
    estimated_tokens: int
    estimated_cost_nanos: int
    daily_budget_nanos: int | None
    monthly_budget_nanos: int | None

    def __post_init__(self) -> None:
        if (
            type(self.schema_version) is not int
            or self.schema_version != USAGE_LEDGER_SCHEMA_VERSION
        ):
            raise ValueError("Budget reservation schema version is unsupported.")
        if not isinstance(self.reservation_id, str) or not _RESERVATION_ID.fullmatch(
            self.reservation_id
        ):
            raise ValueError("Budget reservation ID is invalid.")
        if not isinstance(self.key_id, str) or not _KEY_ID.fullmatch(self.key_id):
            raise ValueError("Budget reservation virtual-key ID is invalid.")
        created_at = _timestamp(self.created_at, "Budget reservation creation timestamp")
        expires_at = _timestamp(self.expires_at, "Budget reservation expiry timestamp")
        if not created_at < expires_at <= created_at + MAX_RESERVATION_TTL_SECONDS:
            raise ValueError("Budget reservation expiry is invalid.")
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "expires_at", expires_at)
        _strict_int(
            self.estimated_tokens,
            "Budget reservation estimated tokens",
            maximum=9_223_372_036_854_775_807,
        )
        _strict_int(
            self.estimated_cost_nanos,
            "Budget reservation estimated cost",
            maximum=MAX_COST_NANOS,
        )
        daily = _optional_cost(self.daily_budget_nanos, "Budget reservation daily limit")
        monthly = _optional_cost(self.monthly_budget_nanos, "Budget reservation monthly limit")
        if daily is None and monthly is None:
            raise ValueError("Budget reservation requires a hard budget.")

    def to_record(self) -> dict[str, object]:
        return {field.name: getattr(self, field.name) for field in fields(self)}


@dataclass(frozen=True, slots=True)
class BudgetReservation:
    schema_version: int
    reservation_id: str
    key_id: str
    created_at: float
    expires_at: float
    estimated_tokens: int
    estimated_cost_nanos: int
    daily_budget_nanos: int | None
    monthly_budget_nanos: int | None
    state: BudgetReservationState
    revision: int
    transitioned_at: float | None
    usage: UsageLedgerEntry | None

    def __post_init__(self) -> None:
        request = BudgetReservationRequest(
            schema_version=self.schema_version,
            reservation_id=self.reservation_id,
            key_id=self.key_id,
            created_at=self.created_at,
            expires_at=self.expires_at,
            estimated_tokens=self.estimated_tokens,
            estimated_cost_nanos=self.estimated_cost_nanos,
            daily_budget_nanos=self.daily_budget_nanos,
            monthly_budget_nanos=self.monthly_budget_nanos,
        )
        if type(self.state) is not BudgetReservationState:
            raise ValueError("Budget reservation state is invalid.")
        if self.state is BudgetReservationState.ACTIVE:
            if self.revision != 1 or self.transitioned_at is not None or self.usage is not None:
                raise ValueError("Active budget reservation evidence is invalid.")
            return
        if self.revision != 2 or self.transitioned_at is None:
            raise ValueError("Terminal budget reservation evidence is invalid.")
        transitioned_at = _timestamp(
            self.transitioned_at, "Budget reservation transition timestamp"
        )
        if transitioned_at < request.created_at:
            raise ValueError("Budget reservation transition timestamp is invalid.")
        object.__setattr__(self, "transitioned_at", transitioned_at)
        if self.state is BudgetReservationState.COMMITTED:
            if type(self.usage) is not UsageLedgerEntry or self.usage.api_key_id != self.key_id:
                raise ValueError("Committed budget reservation usage is invalid.")
            if not request.created_at <= self.usage.occurred_at <= transitioned_at:
                raise ValueError("Committed budget reservation usage timestamp is invalid.")
        elif self.usage is not None:
            raise ValueError("Uncommitted budget reservation cannot contain usage.")
        if self.state is BudgetReservationState.EXPIRED and transitioned_at < request.expires_at:
            raise ValueError("Budget reservation expired before its deadline.")

    @classmethod
    def active(cls, request: BudgetReservationRequest) -> BudgetReservation:
        return cls(
            **request.to_record(),
            state=BudgetReservationState.ACTIVE,
            revision=1,
            transitioned_at=None,
            usage=None,
        )

    def to_record(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "reservation_id": self.reservation_id,
            "key_id": self.key_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "estimated_tokens": self.estimated_tokens,
            "estimated_cost_nanos": self.estimated_cost_nanos,
            "daily_budget_nanos": self.daily_budget_nanos,
            "monthly_budget_nanos": self.monthly_budget_nanos,
            "state": self.state.value,
            "revision": self.revision,
            "transitioned_at": self.transitioned_at,
            "usage": None if self.usage is None else self.usage.to_record(),
        }


def _exact_record(record: object, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(record, Mapping) or set(record) != expected:
        raise ValueError(f"Stored {label} is invalid.")
    return dict(record)


def usage_entry_from_record(record: object) -> UsageLedgerEntry:
    values = _exact_record(
        record, {field.name for field in fields(UsageLedgerEntry)}, "usage entry"
    )
    try:
        return UsageLedgerEntry(**values)
    except (TypeError, ValueError) as exc:
        raise ValueError("Stored usage entry is invalid.") from exc


def budget_reservation_from_record(record: object) -> BudgetReservation:
    values = _exact_record(
        record,
        {field.name for field in fields(BudgetReservation)},
        "budget reservation",
    )
    try:
        values["state"] = BudgetReservationState(values["state"])
        if values["usage"] is not None:
            values["usage"] = usage_entry_from_record(values["usage"])
        return BudgetReservation(**values)
    except (TypeError, ValueError) as exc:
        raise ValueError("Stored budget reservation is invalid.") from exc
