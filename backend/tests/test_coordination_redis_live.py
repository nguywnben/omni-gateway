"""Opt-in execution evidence for the fixed Redis coordination Lua scripts.

Set ``OMNI_TEST_REDIS_URI`` to a dedicated or shared Redis endpoint.  Each
test class uses a unique validated namespace and teardown removes only keys
under its derived deployment prefix.  This suite never flushes the server.
"""

from __future__ import annotations

import asyncio
import base64
import os
import sys
import time
import unittest
import uuid
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import redis.asyncio as redis_asyncio

BACKEND_DIR = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from coordination_store_contract import CoordinationStoreContract
from core.coordination import (
    CoordinationCorruptError,
    CoordinationUninitializedError,
    QuotaCommitRequest,
    QuotaReservationRequest,
    validate_deployment_namespace,
)
from core.ha_coordination_binding import (
    CoordinationBinding,
    CoordinationBindingManager,
    HaBindingError,
)
from core.ha_runtime_policy import HaRuntimePolicy
from core.redis_state_store import RedisStateStore
from core.redis_state_store import _fingerprint as _redis_fingerprint
from core.routing_coordination import VALID_INVALIDATION_SCOPES
from core.security_coordination import (
    SecurityPrincipalType,
    SessionIssueRequest,
    SessionListRequest,
)

REDIS_URI = os.getenv("OMNI_TEST_REDIS_URI", "").strip()
_CONNECT_TIMEOUT_SECONDS = 5.0


def _namespace() -> str:
    return validate_deployment_namespace(f"w415-live-{uuid.uuid4().hex}")


def _reservation(
    reservation_id: str, *, now: float | None = None, **overrides: object
) -> QuotaReservationRequest:
    current = time.time() if now is None else now
    values: dict[str, object] = {
        "reservation_id": reservation_id,
        "key_id": "live-key",
        "now": current,
        "ttl_seconds": 61.0,
        "estimated_tokens": 10,
        "estimated_cost_usd": 0.1,
        "rpm_limit": None,
        "tpm_limit": None,
        "daily_budget_usd": None,
        "monthly_budget_usd": None,
        "daily_spend_usd": 0.0,
        "monthly_spend_usd": 0.0,
        "daily_snapshot_started_at": current,
        "monthly_snapshot_started_at": current,
    }
    values.update(overrides)
    return QuotaReservationRequest(**values)  # type: ignore[arg-type]


async def _run_live_cleanup_steps(*steps: Callable[[], Awaitable[None]]) -> BaseException | None:
    """Run every bounded cleanup step and retain only the first failure."""

    first_failure: BaseException | None = None
    for step in steps:
        try:
            await step()
        except BaseException as exc:
            if first_failure is None:
                first_failure = exc
    return first_failure


async def _close_setup_resources(store: Any | None, cleanup_client: Any | None) -> None:
    """Best-effort setup rollback: never mask the setup failure with cleanup failures."""

    steps: list[Callable[[], Awaitable[None]]] = []
    if store is not None:
        steps.append(store.close)
    if cleanup_client is not None:
        steps.append(cleanup_client.aclose)
    await _run_live_cleanup_steps(*steps)


async def _clear_live_prefix(cleanup_client: Any, prefix: str) -> None:
    cursor = 0
    while True:
        cursor, keys = await cleanup_client.scan(cursor, match=prefix, count=128)
        if keys:
            await cleanup_client.unlink(*keys)
        if cursor == 0:
            return


async def _teardown_live_resources(store: Any, cleanup_client: Any, prefix: str) -> None:
    """Attempt prefix cleanup and both closes independently, preserving the first failure."""

    failure = await _run_live_cleanup_steps(
        lambda: _clear_live_prefix(cleanup_client, prefix), store.close, cleanup_client.aclose
    )
    if failure is not None:
        raise failure


class _FakeLiveResource:
    def __init__(self, events: list[str], name: str, failure: BaseException | None = None) -> None:
        self.events = events
        self.name = name
        self.failure = failure

    async def close(self) -> None:
        self.events.append(f"{self.name}.close")
        if self.failure is not None:
            raise self.failure

    async def aclose(self) -> None:
        self.events.append(f"{self.name}.aclose")
        if self.failure is not None:
            raise self.failure

    async def scan(self, *_args: Any, **_kwargs: Any) -> tuple[int, list[bytes]]:
        self.events.append(f"{self.name}.scan")
        if self.failure is not None:
            raise self.failure
        return 0, []

    async def unlink(self, *_keys: bytes) -> None:
        self.events.append(f"{self.name}.unlink")


class LiveRedisResourceCleanupTests(unittest.IsolatedAsyncioTestCase):
    async def test_setup_rollback_closes_store_when_cleanup_client_was_not_constructed(
        self,
    ) -> None:
        events: list[str] = []
        store = _FakeLiveResource(events, "store")

        await _close_setup_resources(store, None)

        self.assertEqual(events, ["store.close"])

    async def test_setup_rollback_closes_each_constructed_resource_independently(self) -> None:
        events: list[str] = []
        store = _FakeLiveResource(events, "store", RuntimeError("store close failed"))
        client = _FakeLiveResource(events, "client")

        await _close_setup_resources(store, client)

        self.assertEqual(events, ["store.close", "client.aclose"])

    async def test_teardown_attempts_all_bounded_cleanup_after_cancellation(self) -> None:
        events: list[str] = []
        store = _FakeLiveResource(events, "store", RuntimeError("store close failed"))
        client = _FakeLiveResource(events, "client", asyncio.CancelledError())

        with self.assertRaises(asyncio.CancelledError):
            await _teardown_live_resources(store, client, "omni:{test}:v1:*")

        self.assertEqual(events, ["client.scan", "store.close", "client.aclose"])


@unittest.skipUnless(REDIS_URI, "OMNI_TEST_REDIS_URI is not configured")
class LiveRedisCoordinationTests(CoordinationStoreContract, unittest.IsolatedAsyncioTestCase):
    """Execute the registered source against Redis; configured outages are failures."""

    async def asyncSetUp(self) -> None:
        self.store: RedisStateStore | None = None
        self.cleanup_client: Any | None = None
        try:
            self.namespace = _namespace()
            self.store = RedisStateStore(
                REDIS_URI,
                deployment_namespace=self.namespace,
                _quota_record_limit_for_testing=2,
            )
            self.cleanup_client = redis_asyncio.from_url(REDIS_URI, decode_responses=False)
            await asyncio.wait_for(self.store.initialize_epoch(), timeout=_CONNECT_TIMEOUT_SECONDS)
        except BaseException as exc:
            await _close_setup_resources(self.store, self.cleanup_client)
            if isinstance(exc, asyncio.CancelledError):
                raise asyncio.CancelledError() from None
            raise RuntimeError(
                "OMNI_TEST_REDIS_URI is configured but Redis coordination could not be reached "
                "or initialized."
            ) from None

    async def asyncTearDown(self) -> None:
        assert self.store is not None
        assert self.cleanup_client is not None
        prefix = f"{self.store._prefix}:*"  # Test-only derived deployment boundary.
        await _teardown_live_resources(self.store, self.cleanup_client, prefix)

    async def test_shared_coordination_contract_against_registered_lua(self) -> None:
        async def advance_server_clock(seconds: float) -> None:
            # Redis owns TTL time.  Keep the wait bounded so a stalled local event loop cannot hang CI.
            await asyncio.wait_for(asyncio.sleep(seconds), timeout=seconds + 1.0)

        await self.assert_epoch_cas_and_invalidation_contract(
            advance_cas_clock=advance_server_clock
        )

    async def test_expired_cas_replay_backlog_is_drained_in_bounded_batches(self) -> None:
        from core.coordination import CasRequest

        requests = [
            CasRequest(
                f"live-replay-backlog-record-{index}",
                0,
                b"value",
                300,
                1,
                f"live-replay-backlog-operation-{index}",
                replay_ttl_seconds=5,
            )
            for index in range(257)
        ]
        results = []
        for request in requests:
            results.append(await self.store.compare_and_set(request))
        self.assertTrue(all(result.applied for result in results))

        await asyncio.wait_for(asyncio.sleep(5.1), timeout=6.1)
        after_backlog = await self.store.compare_and_set(
            CasRequest(
                "live-replay-after-backlog",
                0,
                b"value",
                300,
                1,
                "live-replay-after-backlog-operation",
                replay_ttl_seconds=5,
            )
        )

        self.assertTrue(after_backlog.applied)
        replay_key = self.store._key("replay:cas")
        expiry_key = self.store._key("expiry:cas")
        self.assertEqual(await self.cleanup_client.hlen(replay_key), 2)
        self.assertEqual(await self.cleanup_client.zcard(expiry_key), 2)

    async def test_epoch_advance_atomically_invalidates_authority_and_sessions(self) -> None:
        before = {
            scope: (await self.store.read_invalidation_generation(scope)).generation or 0
            for scope in VALID_INVALIDATION_SCOPES
        }
        issued = await self.store.issue_security_session(
            SessionIssueRequest(
                session_digest="a" * 64,
                session_reference="ssr_" + ("b" * 32),
                principal_index="c" * 64,
                principal_type=SecurityPrincipalType.LOCAL_OWNER,
                payload=b"opaque-session-payload",
                idle_ttl_seconds=300.0,
                absolute_ttl_seconds=900.0,
                fencing_epoch=1,
                operation_id="live-session-before-advance",
            )
        )
        self.assertTrue(issued.applied)

        await self.store.advance_epoch(1, "live-authority-advance")

        after = {
            scope: (await self.store.read_invalidation_generation(scope)).generation or 0
            for scope in VALID_INVALIDATION_SCOPES
        }
        self.assertEqual(after, {scope: value + 1 for scope, value in before.items()})
        snapshot = await self.store.read_session_reconciliation(epoch=2)
        self.assertEqual(snapshot.active_count, 0)
        await self.store.mark_epoch_ready(2, "live-authority-ready")
        sessions = await self.store.list_security_sessions(SessionListRequest(10, 2))
        self.assertEqual(sessions.sessions, ())

    async def test_existing_namespace_missing_invalidation_authority_fails_closed(self) -> None:
        scope = sorted(VALID_INVALIDATION_SCOPES)[0]
        self.assertEqual(
            await self.cleanup_client.delete(self.store._key("invalidation", scope)), 1
        )

        with self.assertRaises(CoordinationCorruptError):
            await self.store.initialize_epoch()

    async def test_empty_epoch_namespace_never_self_initializes_on_read(self) -> None:
        epoch_key = self.store._key("epoch")
        initialization_key = self.store._key("initialization")
        self.assertEqual(await self.cleanup_client.delete(epoch_key, initialization_key), 2)

        with self.assertRaises(CoordinationUninitializedError):
            await self.store.read_epoch()

        self.assertEqual(await self.cleanup_client.exists(epoch_key, initialization_key), 0)

    async def test_durable_binding_prevents_lost_epoch_namespace_rebootstrap(self) -> None:
        from backend.tests.durable_migration_fixtures import (
            MemoryMigrationCheckpoints,
            completed_migration_checkpoint,
        )

        class Storage:
            async def get_config(self, key, default=None):
                return self.values.get(key, default)

            async def create_migration_checkpoint_repository(self):
                return self.checkpoints

        policy = HaRuntimePolicy.from_environment(
            {
                "OMNI_RUNTIME_MODE": "coordinated",
                "WORKERS": "1",
                "OMNI_REPLICA_COUNT": "1",
                "POSTGRESQL_URI": "postgresql://database/omni",
                "REDIS_URL": REDIS_URI,
                "OMNI_COORDINATION_NAMESPACE": self.namespace,
                "OMNI_DEPLOYMENT_ID": "gateway-live-01",
                "OMNI_COORDINATION_KEY": base64.urlsafe_b64encode(b"k" * 32).decode("ascii"),
                "OMNI_COORDINATION_EPOCH": "1",
            }
        )
        checkpoint = completed_migration_checkpoint()
        expected = CoordinationBinding.for_policy(policy, "act_" + ("a" * 32), checkpoint)
        storage = Storage()
        storage.values = {CoordinationBindingManager.DURABLE_KEY: expected.to_dict()}
        storage.checkpoints = MemoryMigrationCheckpoints(checkpoint)
        await self.store.set(
            CoordinationBindingManager.STORE_KEY,
            CoordinationBindingManager.encode_record(expected),
        )
        epoch_key = self.store._key("epoch")
        initialization_key = self.store._key("initialization")
        self.assertEqual(await self.cleanup_client.delete(epoch_key, initialization_key), 2)

        with self.assertRaises(HaBindingError) as raised:
            await CoordinationBindingManager(storage, self.store).verify(policy)

        self.assertEqual(raised.exception.code, "epoch_namespace_missing")
        self.assertEqual(await self.cleanup_client.exists(epoch_key, initialization_key), 0)
        with self.assertRaises(CoordinationCorruptError):
            await self.store.initialize_epoch()
        self.assertEqual(await self.cleanup_client.exists(epoch_key, initialization_key), 0)

    async def test_admission_fence_all_families_against_registered_lua(self) -> None:
        await self.assert_admission_fence_contract()

    async def test_admission_fence_linearization_and_settlement_against_registered_lua(
        self,
    ) -> None:
        await self.assert_fence_linearization_and_settlement_contract()

    async def test_device_authorization_settlement_during_drain(self) -> None:
        async def advance(seconds: float) -> None:
            await asyncio.wait_for(asyncio.sleep(seconds), timeout=seconds + 1.0)

        await self.assert_device_authorization_settlement_contract(advance_device_clock=advance)

    async def test_legacy_cas_replay_is_idempotent_before_and_during_drain(self) -> None:
        from dataclasses import replace

        from core.coordination import (
            CasRequest,
            CasSettlementProof,
            CasSettlementTarget,
            CasSettlementTransition,
            CoordinationUnavailableError,
        )

        request = CasRequest("legacy-cas", 0, b"value", 300, 1, "legacy-cas-operation")
        fingerprint = _redis_fingerprint(
            request.key,
            request.expected_revision,
            request.payload,
            float(request.ttl_seconds),
            request.epoch,
        )
        seconds, microseconds = await self.cleanup_client.time()
        expires_at = seconds * 1_000 + microseconds // 1_000 + 300_000
        operation = request.operation_id.encode("ascii")
        await self.cleanup_client.hset(
            self.store._key("replay:cas"),
            operation,
            b"|".join(
                (
                    b"1",
                    fingerprint,
                    b"applied",
                    b"1",
                    str(expires_at).encode("ascii"),
                )
            ),
        )
        await self.cleanup_client.zadd(self.store._key("expiry:cas"), {operation: expires_at})
        self.assertEqual(
            await self.cleanup_client.zscore(self.store._key("expiry:cas"), operation),
            float(expires_at),
        )

        before = await self.store.compare_and_set(request)
        self.assertTrue(before.applied)
        self.assertTrue(before.idempotent)
        await self.install_admission_fence()
        during = await self.store.compare_and_set(request)
        self.assertTrue(during.applied)
        self.assertTrue(during.idempotent)

        target = CasSettlementTarget(request.key, CasSettlementTransition.UPDATE)
        proof_admission = replace(request, settlement_targets=(target,))
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.compare_and_set(
                CasRequest(
                    request.key,
                    1,
                    b"settled",
                    300,
                    1,
                    "legacy-cas-settlement",
                    settlement=CasSettlementProof(proof_admission, target),
                )
            )

    async def test_cas_settlement_proof_against_registered_lua(self) -> None:
        await self.assert_cas_settlement_proof_contract()

    async def test_cas_settlement_proof_rejects_cross_key_and_wrong_transition_reuse(
        self,
    ) -> None:
        await self.assert_cas_settlement_proof_cannot_be_reused_for_other_work()

    async def test_unknown_settlement_does_not_admit_replays(self) -> None:
        async def retained_count() -> int:
            total = 0
            async for key in self.cleanup_client.scan_iter(match=f"{self.store._prefix}:*"):
                if (
                    b":quota:replay:" in key
                    or key == self.store._key("security:oidc-replay").encode()
                ):
                    total += await self.cleanup_client.hlen(key)
            return total

        await self.assert_unknown_settlement_does_not_admit_replays(retained_count)

    async def test_batch_settlement_during_drain_against_registered_lua(self) -> None:
        await self.assert_batch_settlement_during_drain_contract()

    async def test_batch_partial_settlement_retry_against_registered_lua(self) -> None:
        await self.assert_batch_partial_settlement_retry_contract()

    async def test_settlement_replay_outlives_its_admission_proof(self) -> None:
        async def advance(seconds: float) -> None:
            await asyncio.wait_for(asyncio.sleep(seconds), timeout=seconds + 1)

        await self.assert_settlement_replay_after_proof_expiry(advance)

    async def test_corrupt_fence_blocks_settlement_against_registered_lua(self) -> None:
        await self.assert_corrupt_fence_blocks_settlement_contract()

    async def test_ambiguous_fence_json_blocks_settlement(self) -> None:
        await self.assert_ambiguous_fence_json_blocks_settlement()

    async def test_drain_completion_identity_against_registered_lua(self) -> None:
        await self.assert_drain_completion_identity_contract()

    async def test_corrupt_admission_fence_against_registered_lua(self) -> None:
        for changes in (
            {"epoch": 2},
            {"namespace_digest": "f" * 64},
            {"epoch": True},
            {"schema_version": 2},
            {"unexpected": "value"},
        ):
            with self.subTest(changes=changes):
                await self.install_admission_fence(**changes)
                with self.assertRaises(CoordinationCorruptError):
                    await self.store.reserve_quota(_reservation("corrupt-fence"))

    async def test_shared_quota_contract_against_registered_lua(self) -> None:
        async def advance_server_clock(seconds: float) -> None:
            await asyncio.wait_for(asyncio.sleep(seconds), timeout=seconds + 1.0)

        await self.assert_quota_lifecycle_replay_expiry_and_capacity_contract(
            advance_quota_clock=advance_server_clock
        )

    async def test_quota_rate_limits_are_atomic_and_budget_fields_are_neutral(self) -> None:
        now = time.time()
        first, second = await asyncio.gather(
            self.store.reserve_quota(_reservation("rpm-a", now=now, rpm_limit=1)),
            self.store.reserve_quota(_reservation("rpm-b", now=now, rpm_limit=1)),
        )
        self.assertEqual(sum(item.accepted for item in (first, second)), 1)
        self.assertEqual([item.reason for item in (first, second) if not item.accepted], ["rpm"])

        self.assertTrue(
            (
                await self.store.reserve_quota(
                    _reservation("tpm-a", now=now, key_id="tpm", estimated_tokens=60, tpm_limit=100)
                )
            ).accepted
        )
        tpm = await self.store.reserve_quota(
            _reservation("tpm-b", now=now, key_id="tpm", estimated_tokens=60, tpm_limit=100)
        )
        self.assertEqual(tpm.reason, "tpm")

        self.assertTrue(
            (
                await self.store.reserve_quota(
                    _reservation(
                        "daily-a",
                        now=now,
                        key_id="daily",
                        estimated_cost_usd=0.6,
                        daily_budget_usd=1.0,
                    )
                )
            ).accepted
        )
        daily = await self.store.reserve_quota(
            _reservation(
                "daily-b", now=now, key_id="daily", estimated_cost_usd=0.6, daily_budget_usd=1.0
            )
        )
        self.assertTrue(daily.accepted)

        self.assertTrue(
            (
                await self.store.reserve_quota(
                    _reservation(
                        "monthly-a",
                        now=now,
                        key_id="monthly",
                        estimated_cost_usd=0.6,
                        monthly_budget_usd=1.0,
                    )
                )
            ).accepted
        )
        monthly = await self.store.reserve_quota(
            _reservation(
                "monthly-b",
                now=now,
                key_id="monthly",
                estimated_cost_usd=0.6,
                monthly_budget_usd=1.0,
            )
        )
        self.assertTrue(monthly.accepted)

    async def test_quota_signed_63_bit_token_boundaries_execute_in_lua(self) -> None:
        now = time.time()
        for boundary in (2**53 - 1, 2**53, 2**53 + 1, 2**63 - 1):
            with self.subTest(boundary=boundary):
                key_id = f"token-{boundary}"
                self.assertTrue(
                    (
                        await self.store.reserve_quota(
                            _reservation(
                                f"token-first-{boundary}",
                                now=now,
                                key_id=key_id,
                                estimated_tokens=boundary,
                                tpm_limit=boundary,
                            )
                        )
                    ).accepted
                )
                denied = await self.store.reserve_quota(
                    _reservation(
                        f"token-second-{boundary}",
                        now=now,
                        key_id=key_id,
                        estimated_tokens=1,
                        tpm_limit=boundary,
                    )
                )
                self.assertEqual(denied.reason, "tpm")

    async def test_quota_touched_record_and_chronology_corruption_fails_closed(self) -> None:
        assert self.cleanup_client is not None
        now = time.time()

        async def stored_record(reservation_id: str) -> tuple[str, list[bytes]]:
            locator = await self.cleanup_client.get(
                self.store._key("quota:locator", reservation_id)
            )
            assert isinstance(locator, bytes)
            key_digest = locator.split(b"|")[1]
            records_key = self.store._quota_bucket_key("quota:records", key_digest)
            encoded = await self.cleanup_client.hget(records_key, reservation_id)
            assert isinstance(encoded, bytes)
            return records_key, encoded.split(b"|")

        for suffix, corrupt_cost in (
            ("infinite", b"1e999"),
            ("negative", b"-1"),
            ("above-range", b"9.2233720368547779e+18"),
        ):
            with self.subTest(corruption=suffix):
                reservation_id = f"corrupt-{suffix}"
                key_id = f"corrupt-key-{suffix}"
                self.assertTrue(
                    (
                        await self.store.reserve_quota(
                            _reservation(reservation_id, now=now, key_id=key_id)
                        )
                    ).accepted
                )
                records_key, fields = await stored_record(reservation_id)
                fields[8] = corrupt_cost
                await self.cleanup_client.hset(records_key, reservation_id, b"|".join(fields))
                with self.assertRaises(CoordinationCorruptError):
                    await self.store.commit_quota(
                        QuotaCommitRequest(reservation_id, now, 1, 0.0, False)
                    )

        boundary_id = "decimal-boundary"
        boundary_key = "decimal-boundary-key"
        self.assertTrue(
            (
                await self.store.reserve_quota(
                    _reservation(boundary_id, now=now, key_id=boundary_key)
                )
            ).accepted
        )
        records_key, fields = await stored_record(boundary_id)
        fields[8] = b"9.2233720368547758e+18"
        await self.cleanup_client.hset(records_key, boundary_id, b"|".join(fields))
        self.assertTrue(
            (
                await self.store.reserve_quota(
                    _reservation("decimal-boundary-next", now=now, key_id=boundary_key)
                )
            ).accepted
        )

        chronology_id = "corrupt-chronology"
        chronology_key = "corrupt-chronology-key"
        self.assertTrue(
            (
                await self.store.reserve_quota(
                    _reservation(
                        chronology_id,
                        now=now,
                        key_id=chronology_key,
                        ttl_seconds=61.0,
                    )
                )
            ).accepted
        )
        self.assertTrue(
            (
                await self.store.commit_quota(QuotaCommitRequest(chronology_id, now, 1, 0.0, False))
            ).committed
        )
        records_key, fields = await stored_record(chronology_id)
        fields[6] = str(int(fields[8]) + 1).encode("ascii")
        await self.cleanup_client.hset(records_key, chronology_id, b"|".join(fields))
        with self.assertRaises(CoordinationCorruptError):
            await self.store.reserve_quota(
                _reservation(
                    chronology_id,
                    now=now,
                    key_id=chronology_key,
                    operation_id="chronology-corruption-probe",
                )
            )

    async def test_quota_replay_terminal_retention_commit_fallback_and_overspend(self) -> None:
        now = time.time()
        request = _reservation("replay", now=now, ttl_seconds=300.0, daily_budget_usd=1.0)
        first = await self.store.reserve_quota(request)
        replay = await self.store.reserve_quota(request)
        conflict = await self.store.reserve_quota(
            _reservation(
                "replay", now=now, ttl_seconds=300.0, estimated_tokens=11, daily_budget_usd=1.0
            )
        )
        committed = await self.store.commit_quota(
            QuotaCommitRequest("replay", now + 1.0, 20, 1.2, True, operation_id="replay-commit")
        )
        committed_replay = await self.store.commit_quota(
            QuotaCommitRequest("replay", now + 1.0, 20, 1.2, True, operation_id="replay-commit")
        )

        self.assertTrue(first.accepted)
        self.assertTrue(replay.idempotent)
        self.assertEqual(conflict.reason, "conflict")
        self.assertTrue(committed.committed)
        self.assertFalse(committed.overspent)
        self.assertTrue(committed_replay.idempotent)

        fallback = _reservation("fallback", now=now, key_id="fallback", ttl_seconds=300.0)
        self.assertTrue((await self.store.reserve_quota(fallback)).accepted)
        self.assertTrue(
            (
                await self.store.commit_quota(
                    QuotaCommitRequest("fallback", now + 1.0, None, None, False)
                )
            ).committed
        )
        self.assertFalse(await self.store.release_quota("fallback", now=now + 2.0))

        terminal = _reservation("terminal", now=now, ttl_seconds=300.0)
        self.assertTrue((await self.store.reserve_quota(terminal)).accepted)
        self.assertTrue(await self.store.release_quota("terminal", now=now + 1.0))
        reactivation = await self.store.reserve_quota(
            _reservation("terminal", now=now + 2.0, ttl_seconds=300.0)
        )
        self.assertEqual(reactivation.reason, "conflict")

    async def test_snapshot_reconciliation_long_ttl_corruption_and_reopen(self) -> None:
        now = time.time()
        initial = _reservation(
            "snapshot",
            now=now,
            key_id="snapshot",
            ttl_seconds=3600.0,
            daily_budget_usd=2.0,
            monthly_budget_usd=2.0,
        )
        self.assertTrue((await self.store.reserve_quota(initial)).accepted)
        self.assertTrue(
            (
                await self.store.commit_quota(
                    QuotaCommitRequest("snapshot", now + 0.1, 10, 0.4, True)
                )
            ).committed
        )
        reconciled = await self.store.reserve_quota(
            _reservation(
                "snapshot-next",
                now=now + 2.0,
                key_id="snapshot",
                ttl_seconds=3600.0,
                estimated_cost_usd=0.4,
                daily_budget_usd=2.0,
                monthly_budget_usd=2.0,
                daily_spend_usd=0.4,
                monthly_spend_usd=0.4,
                daily_snapshot_started_at=now + 1.0,
                monthly_snapshot_started_at=now + 1.0,
            )
        )
        self.assertTrue(reconciled.accepted)

        await self.store.close()
        self.store = RedisStateStore(REDIS_URI, deployment_namespace=self.namespace)
        self.assertEqual((await self.store.read_epoch()).epoch, 1)
        self.assertTrue(await self.store.release_quota("snapshot-next", now=now + 3.0))

        await self.cleanup_client.set(self.store._key("quota:locator", "corrupt"), b"bad")
        with self.assertRaises(CoordinationCorruptError):
            await self.store.commit_quota(QuotaCommitRequest("corrupt", now + 4.0, 1, 0.0, True))


if __name__ == "__main__":
    unittest.main()
