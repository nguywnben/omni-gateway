"""Production-owner lifecycle scenarios for the external HA matrix."""

from __future__ import annotations

import asyncio
import hashlib
import http.cookiejar
import json
import os
import time
import urllib.error
import urllib.request
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Final, Mapping

from core.coordination import CoordinationUnavailableError
from core.ha_coordination_binding import CoordinationBindingManager
from core.redis_state_store import RedisStateStore
from core.smart_routing import (
    DEFAULT_ROUTE_STATE_CACHE_TTL_SECONDS,
    DEFAULT_ROUTE_TRANSIENT_BACKOFF_SECONDS,
)
from core.storage.postgresql_manager import PostgreSQLManager

from .admin import CandidateAdmin, experimental_policy
from .contract import CandidateTopology, CandidateVerifier, EvidenceVerificationError
from .fixture import FaultAction
from .load import run_workload
from .oracle import CoordinationOracle, CoordinationOracleSnapshot, DurableOracle
from .scenarios import ComposeAction, HostController, NoRedirect

ROLLBACK_COMPOSE_FILE: Final = (
    Path(__file__).resolve().parents[2] / "deploy" / "evidence" / "compose.rollback.yml"
)
ROUTE_RECOVERY_MARGIN_SECONDS: Final = 0.25


class LifecycleScenarioDriver:
    def __init__(
        self,
        candidate: CandidateTopology,
        controller: HostController,
        environment: Mapping[str, str],
        *,
        host_credentials_dir: Path,
        host_postgresql_uri: str,
        host_redis_url: str,
        app_a_url: str,
        app_b_url: str,
        api_key: str,
        oracle: DurableOracle,
    ) -> None:
        if (
            not isinstance(host_credentials_dir, Path)
            or not host_credentials_dir.is_absolute()
            or host_credentials_dir.is_symlink()
            or not host_credentials_dir.is_dir()
        ):
            raise EvidenceVerificationError(
                "Host evidence credentials directory must be an absolute regular directory."
            )
        if next(host_credentials_dir.iterdir(), None) is not None:
            raise EvidenceVerificationError("Host evidence credentials directory must start empty.")
        self.candidate = candidate
        self.controller = controller
        self.environment = dict(environment)
        self.host_credentials_dir = host_credentials_dir.resolve(strict=True)
        self.host_postgresql_uri = host_postgresql_uri
        self.host_redis_url = host_redis_url
        self.endpoints = (("app-a", app_a_url), ("app-b", app_b_url))
        self.api_key = api_key
        self.oracle = oracle
        self.epoch = int(self.environment.get("EVIDENCE_EPOCH", "1"))
        self._probe_sequence = 200_000

    def _policy_environment(self, epoch: int) -> dict[str, str]:
        return {
            **self.environment,
            "OMNI_RUNTIME_MODE": "coordinated",
            "WORKERS": "1",
            "OMNI_REPLICA_COUNT": "1",
            "POSTGRESQL_URI": self.host_postgresql_uri,
            "REDIS_URL": self.host_redis_url,
            "OMNI_COORDINATION_NAMESPACE": self.environment["EVIDENCE_NAMESPACE"],
            "OMNI_DEPLOYMENT_ID": self.environment["EVIDENCE_DEPLOYMENT_ID"],
            "OMNI_COORDINATION_KEY": self.environment["EVIDENCE_COORDINATION_KEY"],
            "OMNI_COORDINATION_EPOCH": str(epoch),
        }

    @asynccontextmanager
    async def _admin(
        self,
        epoch: int,
        *,
        redis_url: str | None = None,
    ) -> AsyncIterator[tuple[CandidateAdmin, RedisStateStore]]:
        previous_postgresql_uri = os.environ.get("POSTGRESQL_URI")
        previous_credentials_dir = os.environ.get("CREDENTIALS_DIR")
        os.environ["POSTGRESQL_URI"] = self.host_postgresql_uri
        os.environ["CREDENTIALS_DIR"] = str(self.host_credentials_dir)
        storage: PostgreSQLManager | None = None
        store: RedisStateStore | None = None
        try:
            storage = PostgreSQLManager()
            await storage.initialize()
            policy = experimental_policy(
                self._policy_environment(epoch), self.candidate, replica_count=2
            )
            store = RedisStateStore(
                redis_url or self.host_redis_url,
                deployment_namespace=policy.coordination_namespace,
            )
            verifier = CandidateVerifier.exact(self.candidate, replica_count=2)
            yield CandidateAdmin(policy, storage, store, verifier), store
        finally:
            try:
                if store is not None:
                    await store.close()
            finally:
                try:
                    if storage is not None:
                        await storage.close()
                finally:
                    if previous_postgresql_uri is None:
                        os.environ.pop("POSTGRESQL_URI", None)
                    else:
                        os.environ["POSTGRESQL_URI"] = previous_postgresql_uri
                    if previous_credentials_dir is None:
                        os.environ.pop("CREDENTIALS_DIR", None)
                    else:
                        os.environ["CREDENTIALS_DIR"] = previous_credentials_dir

    async def _probe(self, *, expect_success: bool) -> tuple[dict[str, object], ...]:
        sequence = self._probe_sequence
        self._probe_sequence += len(self.endpoints)
        samples = []
        for index, endpoint in enumerate(self.endpoints):
            result = await run_workload(
                (endpoint,),
                api_key=self.api_key,
                attempts=1,
                concurrency=1,
                offered_rps=32,
                request_deadline_ms=self.candidate.request_deadline_ms,
                sequence_offset=sequence + index,
            )
            samples.extend(result.samples)
        success = (
            all(sample.success for sample in samples)
            if expect_success
            else any(sample.success for sample in samples)
        )
        if success != expect_success:
            raise EvidenceVerificationError("Lifecycle admission probe had an unexpected outcome.")
        return tuple(sample.safe_dict(include_request_id=True) for sample in samples)

    def _restart_coordinated(self) -> None:
        if self.controller.compose_environment is None:
            raise EvidenceVerificationError("Compose environment is unavailable.")
        self.controller.compose_environment["EVIDENCE_EPOCH"] = str(self.epoch)
        self.controller.compose(ComposeAction.RECREATE, ("app-a", "app-b"))
        for _, endpoint in self.endpoints:
            self.controller.wait_http(f"{endpoint}/ready")

    async def _initial_coordination_snapshot(
        self, coordination: CoordinationOracle
    ) -> CoordinationOracleSnapshot:
        deadline = time.monotonic() + 10.0
        while True:
            try:
                return await coordination.snapshot(expected_epoch=self.epoch)
            except CoordinationUnavailableError:
                if time.monotonic() >= deadline:
                    raise EvidenceVerificationError(
                        "Coordination dependency did not become available for recovery."
                    ) from None
                await asyncio.sleep(0.1)

    async def _transition(
        self, *, probe_stale: bool, redis_url: str | None = None
    ) -> dict[str, object]:
        operation = f"evidence-epoch-{self.epoch + 1}"
        samples: list[dict[str, object]] = []
        coordination = CoordinationOracle(
            redis_url or self.host_redis_url, self.environment["EVIDENCE_NAMESPACE"]
        )
        try:
            before = await self._initial_coordination_snapshot(coordination)
            async with self._admin(self.epoch, redis_url=redis_url) as (admin, _):
                await admin.operator.drain(apply=True)
                await admin.operator.advance_epoch(operation, apply=True)
            if probe_stale:
                samples.extend(await self._probe(expect_success=False))
            target_epoch = self.epoch + 1
            reconciliation_started_ns = time.monotonic_ns()
            async with self._admin(target_epoch, redis_url=redis_url) as (admin, _):
                for _ in range(self.candidate.reconciliation_page_limit):
                    page = await admin.operator.reconcile(
                        operation,
                        apply=True,
                        page_size=self.candidate.reconciliation_page_size,
                    )
                    if page["reconciliation_complete"]:
                        break
                else:
                    raise EvidenceVerificationError(
                        "Lifecycle reconciliation exceeded its page limit."
                    )
                reconciliation_completed_ns = time.monotonic_ns()
                ready = await admin.operator.mark_ready(operation, apply=True)
                mark_ready_ns = time.monotonic_ns()
                replay = await admin.operator.mark_ready(operation, apply=True)
                if (
                    ready != replay
                    or ready.get("applied") is not True
                    or ready.get("epoch") != target_epoch
                    or ready.get("state") != "ready"
                ):
                    raise EvidenceVerificationError(
                        "Lifecycle ready transition is not idempotent under replay."
                    )
            after = await coordination.snapshot(expected_epoch=target_epoch)
        finally:
            await coordination.close()
        before_generations = dict(before.invalidation_generations)
        after_generations = dict(after.invalidation_generations)
        if after.session_count != 0 or any(
            after_generations[scope] != generation + 1
            for scope, generation in before_generations.items()
        ):
            raise EvidenceVerificationError(
                "Epoch transition did not invalidate sessions and cache generations."
            )
        self.epoch = target_epoch
        self._restart_coordinated()
        samples.extend(await self._probe(expect_success=True))
        return {
            "reconciliation_started_ns": reconciliation_started_ns,
            "reconciliation_completed_ns": reconciliation_completed_ns,
            "mark_ready_ns": mark_ready_ns,
            "sustained_ready_ns": time.monotonic_ns(),
            "samples": tuple(samples),
        }

    def _management_request(
        self,
        opener: urllib.request.OpenerDirector,
        endpoint: str,
        path: str,
        *,
        payload: dict[str, object] | None = None,
    ) -> tuple[int, dict[str, object]]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            endpoint.rstrip("/") + path,
            method="POST" if body is not None else "GET",
            data=body,
            headers={} if body is None else {"Content-Type": "application/json"},
        )
        try:
            with opener.open(request, timeout=5.0) as response:
                raw = response.read(1_048_577)
                if len(raw) > 1_048_576:
                    raise EvidenceVerificationError("Management scenario response is oversized.")
                return response.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as exc:
            raw = exc.read(1_048_577)
            if len(raw) > 1_048_576:
                raise EvidenceVerificationError("Management scenario response is oversized.")
            return exc.code, json.loads(raw) if raw else {}
        except (OSError, json.JSONDecodeError) as exc:
            raise EvidenceVerificationError("Management scenario request failed.") from exc

    def _login(self) -> urllib.request.OpenerDirector:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}),
            NoRedirect(),
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()),
        )
        status, _ = self._management_request(
            opener,
            self.endpoints[0][1],
            "/api/auth/login",
            payload={"password": self.environment["EVIDENCE_PANEL_PASSWORD"]},
        )
        if status != 200:
            raise EvidenceVerificationError("Management scenario login failed.")
        return opener

    def _provider_attempts(self) -> int:
        state = self.controller.fixture_state()
        attempts = state.get("provider_attempts") if isinstance(state, dict) else None
        if type(attempts) is not int or attempts < 0:
            raise EvidenceVerificationError("Provider fixture counter is invalid.")
        return attempts

    async def _exercise_cache_epoch_boundary(self) -> tuple[dict[str, object], ...]:
        before = self._provider_attempts()
        first = await run_workload(
            (self.endpoints[0],),
            api_key=self.api_key,
            attempts=1,
            concurrency=1,
            offered_rps=1,
            request_deadline_ms=self.candidate.request_deadline_ms,
            sequence_offset=70_000,
            request_sequence_offset=70_000,
        )
        second = await run_workload(
            (self.endpoints[0],),
            api_key=self.api_key,
            attempts=1,
            concurrency=1,
            offered_rps=1,
            request_deadline_ms=self.candidate.request_deadline_ms,
            sequence_offset=70_001,
            request_sequence_offset=70_000,
        )
        if (
            not all(sample.success for sample in (*first.samples, *second.samples))
            or self._provider_attempts() != before + 1
        ):
            raise EvidenceVerificationError("Response-cache hit was not positively exercised.")

        transition = await self._transition(probe_stale=False)
        transition_samples = transition.get("samples")
        if (
            not isinstance(transition_samples, tuple)
            or len(transition_samples) != 2
            or any(sample.get("success") is not True for sample in transition_samples)
            or self._provider_attempts() != before + 3
        ):
            raise EvidenceVerificationError("Epoch recovery probes were not positively exercised.")

        third = await run_workload(
            (self.endpoints[0],),
            api_key=self.api_key,
            attempts=1,
            concurrency=1,
            offered_rps=1,
            request_deadline_ms=self.candidate.request_deadline_ms,
            sequence_offset=70_002,
            request_sequence_offset=70_000,
        )
        if not third.samples[0].success or self._provider_attempts() != before + 4:
            raise EvidenceVerificationError("Invalidated response-cache entry remained usable.")
        return tuple(
            (
                *(
                    sample.safe_dict(include_request_id=True)
                    for sample in (*first.samples, *second.samples)
                ),
                *transition_samples,
                *(sample.safe_dict(include_request_id=True) for sample in third.samples),
            )
        )

    async def _exercise_hard_budget(
        self, opener: urllib.request.OpenerDirector
    ) -> tuple[dict[str, object], ...]:
        budget_usd = 0.05
        status, created = self._management_request(
            opener,
            self.endpoints[0][1],
            "/api/virtual-keys",
            payload={
                "name": "synthetic-ha-budget",
                "budget_daily_usd": budget_usd,
                "allowed_models": ["omni-evidence-model"],
                "unknown_pricing_policy": "fallback",
                "fallback_price_usd_per_million": 1_000.0,
            },
        )
        data = created.get("data") if isinstance(created, dict) else None
        plaintext = created.get("key") if isinstance(created, dict) else None
        if (
            status != 200
            or not isinstance(data, dict)
            or not isinstance(data.get("id"), str)
            or not isinstance(plaintext, str)
            or not plaintext.startswith("sk-ogw-")
        ):
            raise EvidenceVerificationError("Hard-budget evidence key could not be created.")
        result = await run_workload(
            self.endpoints,
            api_key=plaintext,
            operation_identity_key=hashlib.sha256(self.api_key.encode("utf-8")).digest(),
            attempts=self.candidate.correctness_attempts,
            concurrency=self.candidate.concurrency,
            offered_rps=self.candidate.offered_rps,
            request_deadline_ms=self.candidate.request_deadline_ms,
            sequence_offset=80_000,
        )
        successes = sum(sample.success for sample in result.samples)
        if successes < 1 or successes == len(result.samples):
            raise EvidenceVerificationError("Hard-budget boundary was not positively challenged.")
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            durable = await self.oracle.snapshot()
            if durable.active_reservations == 0 and durable.active_liability_nanos == 0:
                break
            await asyncio.sleep(0.25)
        else:
            raise EvidenceVerificationError("Hard-budget liability did not settle.")
        status, usage = self._management_request(
            opener,
            self.endpoints[1][1],
            f"/api/virtual-keys/{data['id']}/usage",
        )
        usage_data = usage.get("data") if isinstance(usage, dict) else None
        daily = usage_data.get("daily") if isinstance(usage_data, dict) else None
        spent = daily.get("cost_usd") if isinstance(daily, dict) else None
        if (
            status != 200
            or type(spent) not in (int, float)
            or spent < 0
            or spent > budget_usd + 1e-9
        ):
            raise EvidenceVerificationError("Hard-budget durable spend exceeded its ceiling.")
        return tuple(sample.safe_dict(include_request_id=True) for sample in result.samples)

    async def stale_epoch(self) -> dict[str, object]:
        transition = await self._transition(probe_stale=True)
        return {
            "exercised": True,
            "safe": True,
            "challenged_operations": 4,
            "fault_milestones": 3,
            "samples": transition["samples"],
        }

    async def partial_namespace(self) -> dict[str, object]:
        async with self._admin(self.epoch) as (_, store):
            binding = await store.get(CoordinationBindingManager.STORE_KEY)
            if binding is None:
                raise EvidenceVerificationError("Coordination binding is unavailable.")
            await store.delete(CoordinationBindingManager.STORE_KEY)
            for _, endpoint in self.endpoints:
                self.controller.wait_http(f"{endpoint}/ready", expected_status=503)
            namespace_samples = await self._probe(expect_success=False)
            await store.set(CoordinationBindingManager.STORE_KEY, binding)
        transition = await self._transition(probe_stale=False)
        return {
            "exercised": True,
            "safe": True,
            "challenged_operations": 4,
            "fault_milestones": 3,
            "samples": (*namespace_samples, *transition["samples"]),
        }

    async def recover_after_coordination_fault(self) -> dict[str, object]:
        clock = await self._transition(probe_stale=False)
        return {"exercised": True, "safe": True, **clock}

    async def recover_after_standby_promotion(self) -> dict[str, object]:
        clock = await self._transition(
            probe_stale=False,
            redis_url="redis://127.0.0.1:16382/0",
        )
        return {"exercised": True, "safe": True, **clock}

    async def cancellation_unknown_outcome(self) -> dict[str, object]:
        before = await self.oracle.snapshot()
        fixture_before = self.controller.fixture_state()
        self.controller.fault(FaultAction.PROVIDER_DROP_NEXT)
        result = await run_workload(
            (self.endpoints[0],),
            api_key=self.api_key,
            attempts=1,
            concurrency=1,
            offered_rps=1,
            request_deadline_ms=self.candidate.request_deadline_ms,
            sequence_offset=90_000,
        )
        if (
            result.samples[0].success
            or result.samples[0].status_code != 500
            or result.samples[0].transport_failure
        ):
            raise EvidenceVerificationError("Unknown-outcome response shape is invalid.")
        fixture_after = self.controller.fixture_state()
        before_milestones = fixture_before.get("milestones")
        after_milestones = fixture_after.get("milestones")
        if (
            not isinstance(before_milestones, dict)
            or not isinstance(after_milestones, dict)
            or type(before_milestones.get("provider-response-dropped", 0)) is not int
            or type(after_milestones.get("provider-response-dropped", 0)) is not int
            or after_milestones.get("provider-response-dropped", 0)
            <= before_milestones.get("provider-response-dropped", 0)
        ):
            raise EvidenceVerificationError(
                "Unknown-outcome fault did not reach the upstream response boundary."
            )
        backoff_samples = await self._probe(expect_success=False)
        if any(
            sample.get("status_code") != 503 or sample.get("transport_failure") is not False
            for sample in backoff_samples
        ):
            raise EvidenceVerificationError("Unknown-outcome route backoff is invalid.")
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            after = await self.oracle.snapshot()
            if after.active_reservations == 0 and after.active_liability_nanos == 0:
                break
            await asyncio.sleep(0.25)
        else:
            raise EvidenceVerificationError("Unknown-outcome liability did not settle.")
        if after.usage_records < before.usage_records:
            raise EvidenceVerificationError("Unknown-outcome durable history regressed.")
        # An upstream outcome that is unknown to the gateway deliberately applies
        # the production router's transient penalty. Prove admission fails closed during
        # that penalty, then wait beyond its bounded cache/backoff window and
        # prove both replicas recover without operator intervention.
        await asyncio.sleep(
            DEFAULT_ROUTE_TRANSIENT_BACKOFF_SECONDS
            + DEFAULT_ROUTE_STATE_CACHE_TTL_SECONDS
            + ROUTE_RECOVERY_MARGIN_SECONDS
        )
        probe_samples = await self._probe(expect_success=True)
        return {
            "exercised": True,
            "safe": True,
            "challenged_operations": 5,
            "fault_milestones": 2,
            "samples": (
                *(sample.safe_dict(include_request_id=True) for sample in result.samples),
                *backoff_samples,
                *probe_samples,
            ),
        }

    async def duplicate_delivery(self) -> dict[str, object]:
        """Replay one logical operation through both replicas and prove exactly-once effects."""

        opener = self._login()
        status, created = self._management_request(
            opener,
            self.endpoints[0][1],
            "/api/virtual-keys",
            payload={
                "name": "synthetic-ha-idempotency",
                "budget_daily_usd": 10.0,
                "allowed_models": ["omni-evidence-model"],
                "unknown_pricing_policy": "fallback",
                "fallback_price_usd_per_million": 1_000.0,
            },
        )
        plaintext = created.get("key") if isinstance(created, dict) else None
        if status != 200 or not isinstance(plaintext, str) or not plaintext.startswith("sk-ogw-"):
            raise EvidenceVerificationError("Duplicate-delivery evidence key could not be created.")
        before_provider = self._provider_attempts()
        before_durable = await self.oracle.snapshot()
        first = await run_workload(
            (self.endpoints[0],),
            api_key=plaintext,
            attempts=1,
            concurrency=1,
            offered_rps=1,
            request_deadline_ms=self.candidate.request_deadline_ms,
            sequence_offset=110_000,
            request_sequence_offset=110_000,
            operation_sequence_offset=110_000,
            operation_identity_key=hashlib.sha256(self.api_key.encode("utf-8")).digest(),
        )
        second = await run_workload(
            (self.endpoints[1],),
            api_key=plaintext,
            attempts=1,
            concurrency=1,
            offered_rps=1,
            request_deadline_ms=self.candidate.request_deadline_ms,
            sequence_offset=110_001,
            request_sequence_offset=110_000,
            operation_sequence_offset=110_000,
            operation_identity_key=hashlib.sha256(self.api_key.encode("utf-8")).digest(),
        )
        samples = (*first.samples, *second.samples)
        if (
            not all(sample.success for sample in samples)
            or samples[0].request_id != samples[1].request_id
            or samples[0].operation_digest != samples[1].operation_digest
            or samples[0].delivery_digest == samples[1].delivery_digest
            or self._provider_attempts() != before_provider + 1
        ):
            raise EvidenceVerificationError(
                "Duplicate delivery was not served by one upstream execution."
            )
        deadline = time.monotonic() + 30.0
        while time.monotonic() < deadline:
            after = await self.oracle.snapshot()
            if (
                after.successful_usage_events == before_durable.successful_usage_events + 1
                and after.active_reservations == 0
                and after.active_liability_nanos == 0
            ):
                break
            await asyncio.sleep(0.25)
        else:
            raise EvidenceVerificationError(
                "Duplicate delivery did not converge to one durable usage commit."
            )
        return {
            "exercised": True,
            "safe": True,
            "challenged_operations": 2,
            "fault_milestones": 2,
            "samples": tuple(sample.safe_dict(include_request_id=True) for sample in samples),
        }

    async def drain_reconcile_mark_ready(self) -> dict[str, object]:
        anonymous = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        status, _ = self._management_request(anonymous, self.endpoints[0][1], "/api/config/get")
        if status not in {401, 403}:
            raise EvidenceVerificationError("Unauthorized management request was accepted.")
        first_session = self._login()
        status, _ = self._management_request(first_session, self.endpoints[1][1], "/api/config/get")
        if status != 200:
            raise EvidenceVerificationError("Management session was not shared across replicas.")
        status, _ = self._management_request(
            first_session, self.endpoints[1][1], "/api/auth/logout", payload={}
        )
        if status != 200:
            raise EvidenceVerificationError("Cross-replica management logout failed.")
        status, _ = self._management_request(first_session, self.endpoints[0][1], "/api/config/get")
        if status not in {401, 403}:
            raise EvidenceVerificationError("Revoked management session was resurrected.")
        budget_session = self._login()
        budget_samples = await self._exercise_hard_budget(budget_session)
        epoch_session = self._login()
        cache_samples = await self._exercise_cache_epoch_boundary()
        status, _ = self._management_request(epoch_session, self.endpoints[0][1], "/api/config/get")
        if status not in {401, 403}:
            raise EvidenceVerificationError("Prior-epoch management session was resurrected.")
        return {
            "exercised": True,
            "safe": True,
            "challenged_operations": 11 + self.candidate.correctness_attempts,
            "fault_milestones": 5,
            "samples": (*budget_samples, *cache_samples),
        }

    async def standalone_rollback(self) -> dict[str, object]:
        before = await self.oracle.snapshot()
        prior_session = self._login()
        operation = f"evidence-rollback-{self.epoch + 1}"
        async with self._admin(self.epoch) as (admin, _):
            await admin.operator.drain(apply=True)
            await admin.operator.advance_epoch(operation, apply=True)
        target_epoch = self.epoch + 1
        async with self._admin(target_epoch) as (admin, _):
            for _ in range(self.candidate.reconciliation_page_limit):
                page = await admin.operator.reconcile(
                    operation,
                    apply=True,
                    page_size=self.candidate.reconciliation_page_size,
                )
                if page["reconciliation_complete"]:
                    break
            else:
                raise EvidenceVerificationError("Rollback reconciliation exceeded its page limit.")
            plan = await admin.operator.rollback_plan()
            if (
                plan.get("source_state") != "reconciling"
                or plan.get("target_mode") != "standalone"
                or plan.get("workers") != 1
                or plan.get("replicas") != 1
            ):
                raise EvidenceVerificationError("Rollback plan is not safe for handoff.")
        self.epoch = target_epoch
        self.controller.compose(ComposeAction.STOP, ("app-a", "app-b"))
        rollback = HostController(
            ROLLBACK_COMPOSE_FILE,
            self.controller.project,
            self.controller.fixture_url,
            compose_environment=self.environment,
        )
        rollback.compose(ComposeAction.RECREATE, ("app-a",))
        rollback.wait_http(f"{self.endpoints[0][1]}/health")
        rollback.wait_http(f"{self.endpoints[0][1]}/ready")
        status, _ = self._management_request(prior_session, self.endpoints[0][1], "/api/config/get")
        if status not in {401, 403}:
            raise EvidenceVerificationError("Coordinated session survived standalone rollback.")
        anonymous = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        status, _ = self._management_request(anonymous, self.endpoints[0][1], "/api/config/get")
        if status not in {401, 403}:
            raise EvidenceVerificationError("Standalone management policy failed closed.")
        rollback_session = self._login()
        status, _ = self._management_request(
            rollback_session, self.endpoints[0][1], "/api/config/get"
        )
        if status != 200:
            raise EvidenceVerificationError("Standalone owner recovery failed.")
        result = await run_workload(
            (self.endpoints[0],),
            api_key=self.api_key,
            attempts=self.candidate.correctness_attempts,
            concurrency=self.candidate.concurrency,
            offered_rps=self.candidate.offered_rps,
            request_deadline_ms=self.candidate.request_deadline_ms,
            sequence_offset=100_000,
        )
        if not all(sample.success for sample in result.samples):
            raise EvidenceVerificationError("Standalone rollback inference failed.")
        after = await self.oracle.snapshot()
        if (
            after.successful_usage_events - before.successful_usage_events
            != self.candidate.correctness_attempts
            or after.request_traces - before.request_traces < self.candidate.correctness_attempts
            or after.audit_events < before.audit_events
            or after.identities != before.identities
            or after.role_bindings != before.role_bindings
            or after.migration_checkpoints != before.migration_checkpoints
            or after.active_reservations != 0
            or after.active_liability_nanos != 0
        ):
            raise EvidenceVerificationError("Standalone rollback lost durable evidence.")
        return {
            "exercised": True,
            "safe": True,
            "challenged_operations": self.candidate.correctness_attempts,
            "fault_milestones": 3,
            "samples": tuple(
                sample.safe_dict(include_request_id=True) for sample in result.samples
            ),
        }

    async def execute(self, scenario_id: str) -> dict[str, object]:
        methods = {
            "stale-epoch": self.stale_epoch,
            "partial-namespace": self.partial_namespace,
            "cancellation-unknown-outcome": self.cancellation_unknown_outcome,
            "duplicate-delivery": self.duplicate_delivery,
            "drain-reconcile-mark-ready": self.drain_reconcile_mark_ready,
            "standalone-rollback": self.standalone_rollback,
            "recover-after-coordination-fault": self.recover_after_coordination_fault,
            "recover-after-standby-promotion": self.recover_after_standby_promotion,
        }
        try:
            method = methods[scenario_id]
        except KeyError:
            raise EvidenceVerificationError("Lifecycle scenario is not supported.") from None
        return await method()
