"""Independent bounded oracle for durable and coordination acceptance evidence."""

from __future__ import annotations

import hashlib
import hmac
import json
from dataclasses import asdict, dataclass
from typing import Final, Iterable

import asyncpg
from core.redis_state_store import RedisStateStore
from core.routing_coordination import VALID_INVALIDATION_SCOPES
from core.security_coordination import SessionListRequest

_OPERATION_DOMAIN: Final = b"omni-ha-evidence-operation-v1\x00"
_DURABLE_USAGE_PREDICATE: Final = (
    "(kind = 'usage' OR (kind = 'reservation' AND state = 'committed'))"
)
_DURABLE_USAGE_REQUEST: Final = (
    "CASE WHEN kind = 'usage' THEN payload->>'request_id' "
    "WHEN kind = 'reservation' AND state = 'committed' "
    "THEN payload->'usage'->>'request_id' END"
)


def opaque_operation_digest(operation_id: str, key: bytes) -> str:
    if not isinstance(operation_id, str) or not 1 <= len(operation_id) <= 128:
        raise ValueError("Oracle operation identity is invalid.")
    if not isinstance(key, bytes) or len(key) < 32:
        raise ValueError("Oracle digest key is invalid.")
    return hmac.digest(key, _OPERATION_DOMAIN + operation_id.encode("utf-8"), hashlib.sha256).hex()


@dataclass(frozen=True, slots=True)
class DurableOracleSnapshot:
    audit_events: int
    request_traces: int
    usage_records: int
    usage_events: int
    successful_usage_events: int
    active_reservations: int
    active_liability_nanos: int
    identities: int
    role_bindings: int
    migration_checkpoints: int
    usage_checksum: str

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if name == "usage_checksum":
                if not isinstance(value, str) or len(value) != 64:
                    raise ValueError("Oracle checksum is invalid.")
            elif type(value) is not int or not 0 <= value <= 9_223_372_036_854_775_807:
                raise ValueError("Oracle counter is invalid.")


@dataclass(frozen=True, slots=True)
class CoordinationOracleSnapshot:
    epoch: int
    state: str
    session_count: int
    invalidation_generations: tuple[tuple[str, int], ...]


@dataclass(frozen=True, slots=True)
class OperationOracleEvidence:
    operation_digest: str
    deliveries: int
    client_successes: int
    transport_failures: int
    audit_events: int
    request_traces: int
    usage_events: int
    successful_usage_events: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.operation_digest, str)
            or len(self.operation_digest) != 64
            or any(character not in "0123456789abcdef" for character in self.operation_digest)
            or any(
                type(value) is not int or not 0 <= value <= 100_000
                for value in (
                    self.deliveries,
                    self.client_successes,
                    self.transport_failures,
                    self.audit_events,
                    self.request_traces,
                    self.usage_events,
                    self.successful_usage_events,
                )
            )
            or self.deliveries < 1
            or self.client_successes + self.transport_failures > self.deliveries
        ):
            raise ValueError("Operation oracle evidence is invalid.")

    def safe_dict(self) -> dict[str, object]:
        return asdict(self)


class DurableOracle:
    """Query fixed production tables directly; never trusts HTTP health as correctness proof."""

    _COUNT_TABLES: Final = {
        "audit_events": "audit_events",
        "request_traces": "request_traces",
        "identities": "management_identities",
        "role_bindings": "management_role_bindings",
        "migration_checkpoints": "durable_migration_checkpoints",
    }

    def __init__(self, dsn: str) -> None:
        if not isinstance(dsn, str) or not dsn.startswith(("postgresql://", "postgres://")):
            raise ValueError("Oracle PostgreSQL endpoint is invalid.")
        self._dsn = dsn

    async def snapshot(self) -> DurableOracleSnapshot:
        connection = await asyncpg.connect(self._dsn, timeout=5.0)
        try:
            counters: dict[str, int] = {}
            for name, table in self._COUNT_TABLES.items():
                counters[name] = int(await connection.fetchval(f"SELECT COUNT(*) FROM {table}"))
            ledger = await connection.fetchrow(
                """
                SELECT COUNT(*) AS usage_records,
                       COUNT(*) FILTER (WHERE
                         kind = 'usage' OR (kind = 'reservation' AND state = 'committed')
                       ) AS usage_events,
                       COUNT(*) FILTER (WHERE (
                         kind = 'usage' OR (kind = 'reservation' AND state = 'committed')
                       ) AND success IS TRUE)
                         AS successful_usage_events,
                       COUNT(*) FILTER (WHERE kind = 'reservation' AND state = 'active')
                         AS active_reservations,
                       COALESCE(SUM(estimated_cost_nanos) FILTER (
                         WHERE kind = 'reservation' AND state = 'active'
                       ), 0) AS active_liability_nanos
                FROM durable_usage_ledger
                """
            )
            rows = await connection.fetch(
                "SELECT record_id, kind, state, revision, payload::text AS payload "
                "FROM durable_usage_ledger ORDER BY record_id LIMIT 100001"
            )
            if len(rows) > 100_000:
                raise RuntimeError("Oracle ledger verification limit is exceeded.")
            hasher = hashlib.sha256(b"omni-ha-evidence-usage-oracle-v1\x00")
            for row in rows:
                payload = json.dumps(
                    dict(row), ensure_ascii=True, separators=(",", ":"), sort_keys=True
                ).encode("ascii")
                hasher.update(len(payload).to_bytes(8, "big"))
                hasher.update(payload)
            return DurableOracleSnapshot(
                audit_events=counters["audit_events"],
                request_traces=counters["request_traces"],
                usage_records=int(ledger["usage_records"]),
                usage_events=int(ledger["usage_events"]),
                successful_usage_events=int(ledger["successful_usage_events"]),
                active_reservations=int(ledger["active_reservations"]),
                active_liability_nanos=int(ledger["active_liability_nanos"]),
                identities=counters["identities"],
                role_bindings=counters["role_bindings"],
                migration_checkpoints=counters["migration_checkpoints"],
                usage_checksum=hasher.hexdigest(),
            )
        finally:
            await connection.close()

    async def operation_evidence(
        self,
        samples: Iterable[object],
        *,
        operation_key: bytes,
    ) -> tuple[OperationOracleEvidence, ...]:
        """Correlate each client attempt to exact durable rows by opaque request identity."""

        selected = tuple(samples)
        request_ids = tuple(getattr(sample, "request_id", None) for sample in selected)
        if not selected or any(not isinstance(value, str) for value in request_ids):
            raise ValueError("Oracle sample identities are invalid.")
        unique_request_ids = tuple(dict.fromkeys(request_ids))
        connection = await asyncpg.connect(self._dsn, timeout=5.0)
        try:

            async def counts(
                table: str,
                extra: str = "",
                *,
                total_expression: str = "COUNT(*)",
                request_expression: str = "request_id",
            ) -> dict[str, tuple[int, int]]:
                rows = await connection.fetch(
                    f"SELECT {request_expression} AS request_id, "
                    f"{total_expression} AS total {extra} FROM {table} "
                    f"WHERE {request_expression} = ANY($1::text[]) "
                    f"GROUP BY {request_expression}",
                    list(unique_request_ids),
                )
                return {
                    str(row["request_id"]): (
                        int(row["total"]),
                        int(row.get("successful", 0)),
                    )
                    for row in rows
                }

            audits = await counts("audit_events")
            traces = await counts("request_traces")
            usage = await counts(
                "durable_usage_ledger",
                f", COUNT(*) FILTER (WHERE {_DURABLE_USAGE_PREDICATE} "
                "AND success IS TRUE) AS successful",
                total_expression=f"COUNT(*) FILTER (WHERE {_DURABLE_USAGE_PREDICATE})",
                request_expression=_DURABLE_USAGE_REQUEST,
            )
        finally:
            await connection.close()
        grouped: dict[str, list[object]] = {}
        for sample, request_id in zip(selected, request_ids, strict=True):
            assert isinstance(request_id, str)
            grouped.setdefault(request_id, []).append(sample)
        evidence: list[OperationOracleEvidence] = []
        for request_id, deliveries in grouped.items():
            digest = opaque_operation_digest(request_id, operation_key)
            if any(digest != getattr(sample, "operation_digest", None) for sample in deliveries):
                raise RuntimeError("Oracle operation digest does not match the client sample.")
            audit_total, _ = audits.get(request_id, (0, 0))
            trace_total, _ = traces.get(request_id, (0, 0))
            usage_total, usage_success = usage.get(request_id, (0, 0))
            evidence.append(
                OperationOracleEvidence(
                    digest,
                    len(deliveries),
                    sum(bool(getattr(sample, "success", False)) for sample in deliveries),
                    sum(bool(getattr(sample, "transport_failure", False)) for sample in deliveries),
                    audit_total,
                    trace_total,
                    usage_total,
                    usage_success,
                )
            )
        return tuple(evidence)


def counters_from_operation_evidence(
    evidence: Iterable[OperationOracleEvidence],
):
    """Derive correctness counters only from correlated client and durable facts."""

    from .contract import CorrectnessCounters

    rows = tuple(evidence)
    client_success = sum(row.client_successes for row in rows)
    transport = sum(row.transport_failures for row in rows)
    attempted = sum(row.deliveries for row in rows)
    duplicates = sum(max(0, row.successful_usage_events - 1) for row in rows)
    missing_usage = sum(
        row.client_successes > 0 and row.successful_usage_events != 1 for row in rows
    )
    missing_audit = sum(
        row.client_successes > 0 and row.audit_events != row.client_successes for row in rows
    )
    missing_trace = sum(
        row.client_successes > 0 and row.request_traces != row.client_successes for row in rows
    )
    if any(
        row.audit_events > row.deliveries
        or row.request_traces > row.deliveries
        or row.usage_events > 1
        or row.successful_usage_events > row.usage_events
        for row in rows
    ):
        duplicates += 1
    return CorrectnessCounters(
        attempted=attempted,
        admitted=sum(row.successful_usage_events == 1 for row in rows),
        upstream_started=sum(row.successful_usage_events == 1 for row in rows) + transport,
        upstream_completed=sum(row.successful_usage_events == 1 for row in rows),
        client_success=client_success,
        client_unknown=transport,
        rejected=attempted - client_success - transport,
        durable_committed=sum(row.successful_usage_events == 1 for row in rows),
        duplicate_durable_commits=duplicates,
        successful_missing_audit=missing_audit + missing_trace,
        successful_missing_usage=missing_usage,
        replay_success=sum(
            max(0, row.client_successes - 1) for row in rows if row.successful_usage_events == 1
        ),
    )


class CoordinationOracle:
    def __init__(self, redis_url: str, namespace: str) -> None:
        self._store = RedisStateStore(redis_url, deployment_namespace=namespace)

    async def snapshot(self, *, expected_epoch: int) -> CoordinationOracleSnapshot:
        epoch = await self._store.read_epoch()
        if epoch.epoch != expected_epoch:
            raise RuntimeError("Oracle observed an unexpected coordination epoch.")
        if epoch.state.value == "reconciling":
            session_count = (
                await self._store.read_session_reconciliation(epoch=expected_epoch)
            ).active_count
        else:
            sessions = await self._store.list_security_sessions(
                SessionListRequest(limit=200, fencing_epoch=expected_epoch)
            )
            if sessions.next_reference is not None:
                raise RuntimeError("Oracle session verification limit is exceeded.")
            session_count = len(sessions.sessions)
        generations: list[tuple[str, int]] = []
        for scope in sorted(VALID_INVALIDATION_SCOPES):
            generation = await self._store.read_invalidation_generation(scope)
            if generation.generation is None:
                raise RuntimeError("Oracle observed missing invalidation authority.")
            generations.append((scope, generation.generation))
        return CoordinationOracleSnapshot(
            epoch.epoch,
            epoch.state.value,
            session_count,
            tuple(generations),
        )

    async def close(self) -> None:
        await self._store.close()


def assert_conservation(
    before: DurableOracleSnapshot,
    after: DurableOracleSnapshot,
    *,
    successful_operations: int,
) -> None:
    if type(successful_operations) is not int or successful_operations < 0:
        raise ValueError("Successful operation count is invalid.")
    if after.successful_usage_events - before.successful_usage_events != successful_operations:
        raise RuntimeError("Successful operations are not conserved in the usage ledger.")
    if after.request_traces - before.request_traces < successful_operations:
        raise RuntimeError("Successful operations are missing durable request-trace evidence.")
    if after.active_liability_nanos < 0 or after.active_reservations < 0:
        raise RuntimeError("Durable reservation liability is invalid.")
