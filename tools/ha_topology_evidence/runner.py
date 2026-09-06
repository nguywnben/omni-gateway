"""Frozen external HA matrix executor with fail-closed observations."""

from __future__ import annotations

import asyncio
import hashlib
import time
from dataclasses import asdict, dataclass, replace
from typing import Awaitable, Callable, Final

from .bootstrap import BootstrapResult
from .contract import (
    CandidateTopology,
    CorrectnessCounters,
    EvidenceVerificationError,
    RecoveryClock,
    expected_challenged_operations,
    expected_fault_milestones,
)
from .fixture import FaultAction
from .load import RequestSample, WorkloadResult, run_workload
from .oracle import (
    DurableOracle,
    DurableOracleSnapshot,
    OperationOracleEvidence,
    assert_conservation,
    counters_from_operation_evidence,
)
from .scenarios import ComposeAction, HostController

LifecycleHook = Callable[[str], Awaitable[dict[str, object]]]


def _outcome_summary(samples: tuple[RequestSample, ...]) -> str:
    statuses: dict[int, int] = {}
    for sample in samples:
        statuses[sample.status_code] = statuses.get(sample.status_code, 0) + 1
    encoded = ",".join(f"{status}:{statuses[status]}" for status in sorted(statuses))
    transport = sum(sample.transport_failure for sample in samples)
    errors: dict[str, int] = {}
    for sample in samples:
        if sample.transport_error:
            errors[sample.transport_error] = errors.get(sample.transport_error, 0) + 1
    error_counts = ",".join(f"{name}:{errors[name]}" for name in sorted(errors)) or "none"
    return f"statuses={encoded};transport_failures={transport};transport_errors={error_counts}"


@dataclass(frozen=True, slots=True)
class ScenarioObservation:
    scenario_id: str
    repetition: int
    started_ns: int
    completed_ns: int
    challenged_operations: int
    fault_milestones: int
    counters: CorrectnessCounters
    p95_ms: float = 0.0
    successful_throughput_rps: float = 0.0
    recovery_clock: RecoveryClock | None = None

    @property
    def duration_ms(self) -> float:
        return (self.completed_ns - self.started_ns) / 1_000_000

    def safe_event(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "scenario_id": self.scenario_id,
            "repetition": self.repetition,
            "started_monotonic_ns": self.started_ns,
            "completed_monotonic_ns": self.completed_ns,
            "challenged_operations": self.challenged_operations,
            "fault_milestones": self.fault_milestones,
            "counters": asdict(self.counters),
            "p95_ms": self.p95_ms,
            "successful_throughput_rps": self.successful_throughput_rps,
            "recovery_clock": (
                None if self.recovery_clock is None else self.recovery_clock.to_dict()
            ),
        }


@dataclass(frozen=True, slots=True)
class MatrixExecution:
    observations: tuple[ScenarioObservation, ...]
    samples: tuple[dict[str, object], ...]
    oracle_evidence: tuple[dict[str, object], ...]


_RESTORES: Final = {
    FaultAction.REDIS_APP_A_BLOCK: FaultAction.REDIS_APP_A_RESTORE,
    FaultAction.REDIS_APP_B_BLOCK: FaultAction.REDIS_APP_B_RESTORE,
    FaultAction.REDIS_ALL_BLOCK: FaultAction.REDIS_ALL_RESTORE,
    FaultAction.POSTGRES_APP_A_BLOCK: FaultAction.POSTGRES_APP_A_RESTORE,
    FaultAction.POSTGRES_APP_B_BLOCK: FaultAction.POSTGRES_APP_B_RESTORE,
    FaultAction.POSTGRES_ALL_BLOCK: FaultAction.POSTGRES_ALL_RESTORE,
    FaultAction.PROVIDER_HOLD: FaultAction.PROVIDER_RELEASE,
}

_FAULT_DATA_PATH_MILESTONES: Final = {
    FaultAction.REDIS_APP_A_BLOCK: ("redis:app-a:blocked",),
    FaultAction.REDIS_APP_B_BLOCK: ("redis:app-b:blocked",),
    FaultAction.REDIS_ALL_BLOCK: ("redis:app-a:blocked", "redis:app-b:blocked"),
    FaultAction.POSTGRES_APP_A_BLOCK: ("postgres:app-a:blocked",),
    FaultAction.POSTGRES_APP_B_BLOCK: ("postgres:app-b:blocked",),
    FaultAction.POSTGRES_ALL_BLOCK: ("postgres:app-a:blocked", "postgres:app-b:blocked"),
}


def require_milestone_delta(
    before: dict[str, object],
    after: dict[str, object],
    names: tuple[str, ...],
) -> None:
    before_values = before.get("milestones") if isinstance(before, dict) else None
    after_values = after.get("milestones") if isinstance(after, dict) else None
    if not isinstance(before_values, dict) or not isinstance(after_values, dict):
        raise EvidenceVerificationError("Fixture milestone inventory is invalid.")
    if any(
        type(before_values.get(name, 0)) is not int
        or type(after_values.get(name, 0)) is not int
        or after_values.get(name, 0) <= before_values.get(name, 0)
        for name in names
    ):
        raise EvidenceVerificationError("Fault did not reach every challenged data path.")


class MatrixRunner:
    def __init__(
        self,
        candidate: CandidateTopology,
        controller: HostController,
        oracle: DurableOracle,
        *,
        app_a_url: str,
        app_b_url: str,
        api_key: str,
        lifecycle_hook: LifecycleHook,
    ) -> None:
        if not app_a_url.startswith("http://127.0.0.1:") or not app_b_url.startswith(
            "http://127.0.0.1:"
        ):
            raise EvidenceVerificationError("Application evidence endpoints must be loopback-only.")
        self.candidate = candidate
        self.controller = controller
        self.oracle = oracle
        self.endpoints = (("app-a", app_a_url), ("app-b", app_b_url))
        self.api_key = api_key
        self.lifecycle_hook = lifecycle_hook
        self._samples: list[dict[str, object]] = []
        self._oracle_evidence: dict[str, OperationOracleEvidence] = {}
        self._operation_key = hashlib.sha256(api_key.encode("utf-8")).digest()
        self._sequence = 0

    @staticmethod
    def _recovery_clock(
        recovery: dict[str, object],
        *,
        fault_started_ns: int,
        fault_observed_ns: int,
        dependency_restored_ns: int,
    ) -> RecoveryClock:
        required = (
            "reconciliation_started_ns",
            "reconciliation_completed_ns",
            "mark_ready_ns",
            "sustained_ready_ns",
        )
        if any(type(recovery.get(name)) is not int for name in required):
            raise EvidenceVerificationError("Lifecycle recovery clock is incomplete.")
        return RecoveryClock(
            fault_started_ns,
            fault_observed_ns,
            dependency_restored_ns,
            *(int(recovery[name]) for name in required),
        )

    async def _load(
        self,
        endpoints: tuple[tuple[str, str], ...],
        attempts: int,
        *,
        offered_rps: int | None = None,
        schedule_seed: int = 0,
        scenario_id: str,
        repetition: int,
        phase: str,
    ) -> WorkloadResult:
        result = await run_workload(
            endpoints,
            api_key=self.api_key,
            attempts=attempts,
            concurrency=self.candidate.concurrency,
            offered_rps=offered_rps or self.candidate.offered_rps,
            request_deadline_ms=self.candidate.request_deadline_ms,
            sequence_offset=self._sequence,
            schedule_seed=schedule_seed,
        )
        self._sequence += attempts
        self._record_samples(
            result.samples,
            scenario_id=scenario_id,
            repetition=repetition,
            phase=phase,
            schedule_seed=schedule_seed,
        )
        return result

    def _record_samples(
        self,
        samples: tuple[RequestSample, ...],
        *,
        scenario_id: str,
        repetition: int,
        phase: str,
        schedule_seed: int = 0,
    ) -> None:
        for attempt, sample in enumerate(samples, start=1):
            self._samples.append(
                {
                    **sample.safe_dict(),
                    "scenario_id": scenario_id,
                    "repetition": repetition,
                    "phase": phase,
                    "attempt": attempt,
                    "schedule_seed": schedule_seed,
                }
            )

    async def _bounded(self, operation: Awaitable[ScenarioObservation]) -> ScenarioObservation:
        try:
            return await asyncio.wait_for(
                operation,
                timeout=self.candidate.scenario_timeout_seconds,
            )
        except TimeoutError as exc:
            raise EvidenceVerificationError("Correctness scenario exceeded its timeout.") from exc

    async def _verified_counters(self, samples: tuple[RequestSample, ...]) -> CorrectnessCounters:
        evidence = await self.oracle.operation_evidence(
            samples,
            operation_key=self._operation_key,
        )
        for row in evidence:
            if row.operation_digest in self._oracle_evidence:
                raise EvidenceVerificationError("Oracle operation evidence is duplicated.")
            self._oracle_evidence[row.operation_digest] = row
        counters = counters_from_operation_evidence(evidence)
        if not counters.safe:
            raise EvidenceVerificationError("Durable operation evidence is incomplete or unsafe.")
        return counters

    @staticmethod
    def _merge_counters(*values: CorrectnessCounters) -> CorrectnessCounters:
        fields = asdict(CorrectnessCounters())
        return CorrectnessCounters(
            **{name: sum(getattr(value, name) for value in values) for name in fields}
        )

    async def _warmup(
        self,
        endpoints: tuple[tuple[str, str], ...],
        *,
        schedule_seed: int,
        scenario_id: str = "coordinated-baseline",
        repetition: int = 1,
    ) -> None:
        before = await self.oracle.snapshot()
        result = await self._load(
            endpoints,
            self.candidate.warmup_requests,
            schedule_seed=schedule_seed,
            scenario_id=scenario_id,
            repetition=repetition,
            phase="warmup",
        )
        if not all(sample.success for sample in result.samples):
            raise EvidenceVerificationError(
                "Performance warm-up did not complete every request "
                f"({_outcome_summary(result.samples)})."
            )
        await self._wait_conservation(before, self.candidate.warmup_requests)
        await self._verified_counters(result.samples)

    def _accept_lifecycle_samples(
        self,
        result: dict[str, object],
        *,
        scenario_id: str,
        repetition: int = 1,
        phase: str = "lifecycle",
    ) -> tuple[RequestSample, ...]:
        raw = result.get("samples", ())
        if not isinstance(raw, (list, tuple)):
            raise EvidenceVerificationError("Lifecycle evidence samples are invalid.")
        try:
            samples = tuple(
                RequestSample(
                    **(
                        sample
                        if "request_id" in sample
                        else {
                            key: value
                            for key, value in sample.items()
                            if key not in {"operation_digest", "delivery_digest"}
                        }
                    )
                )
                for sample in raw
                if isinstance(sample, dict)
            )
        except (TypeError, ValueError) as exc:
            raise EvidenceVerificationError("Lifecycle evidence samples are invalid.") from exc
        if len(samples) != len(raw):
            raise EvidenceVerificationError("Lifecycle evidence samples are invalid.")
        self._record_samples(
            samples,
            scenario_id=scenario_id,
            repetition=repetition,
            phase=phase,
        )
        return samples

    async def _wait_conservation(
        self,
        before: DurableOracleSnapshot,
        successes: int,
    ) -> DurableOracleSnapshot:
        deadline = time.monotonic() + 30.0
        last: DurableOracleSnapshot | None = None
        while time.monotonic() < deadline:
            last = await self.oracle.snapshot()
            try:
                assert_conservation(before, last, successful_operations=successes)
                if last.active_reservations == 0 and last.active_liability_nanos == 0:
                    return last
            except RuntimeError:
                pass
            await asyncio.sleep(0.25)
        raise EvidenceVerificationError("Durable conservation did not settle within 30 seconds.")

    async def _observed_load(
        self,
        scenario_id: str,
        repetition: int,
        endpoints: tuple[tuple[str, str], ...],
        attempts: int,
        *,
        fault_milestones: int,
        require_all_success: bool,
        schedule_seed: int = 0,
    ) -> ScenarioObservation:
        before = await self.oracle.snapshot()
        started = time.monotonic_ns()
        result = await self._load(
            endpoints,
            attempts,
            schedule_seed=schedule_seed,
            scenario_id=scenario_id,
            repetition=repetition,
            phase="measured",
        )
        completed = time.monotonic_ns()
        successes = sum(sample.success for sample in result.samples)
        if require_all_success and successes != attempts:
            raise EvidenceVerificationError(
                f"Scenario {scenario_id} did not complete every request "
                f"({_outcome_summary(result.samples)})."
            )
        await self._wait_conservation(before, successes)
        counters = await self._verified_counters(result.samples)
        return ScenarioObservation(
            scenario_id,
            repetition,
            started,
            completed,
            attempts,
            fault_milestones,
            counters,
            result.p95_ms,
            result.successful_throughput_rps,
        )

    async def _fault_recovery(
        self,
        scenario_id: str,
        action: FaultAction,
        affected: tuple[tuple[str, str], ...],
    ) -> ScenarioObservation:
        restore = _RESTORES[action]
        before = await self.oracle.snapshot()
        fixture_before = self.controller.fixture_state()
        started = time.monotonic_ns()
        acknowledgement = self.controller.fault(action)
        if acknowledgement.get("accepted") is not True:
            raise EvidenceVerificationError("Fault milestone was not accepted.")
        half = self.candidate.correctness_attempts // 2
        failed = await self._load(
            affected,
            half,
            scenario_id=scenario_id,
            repetition=1,
            phase="fault",
        )
        if any(sample.success for sample in failed.samples):
            raise EvidenceVerificationError(
                f"Scenario {scenario_id} admitted work during the fault."
            )
        require_milestone_delta(
            fixture_before,
            self.controller.fixture_state(),
            _FAULT_DATA_PATH_MILESTONES[action],
        )
        fault_observed = time.monotonic_ns()
        self.controller.fault(restore)
        dependency_restored = time.monotonic_ns()
        recovery = await self.lifecycle_hook("recover-after-coordination-fault")
        if recovery.get("exercised") is not True or recovery.get("safe") is not True:
            raise EvidenceVerificationError("Coordination recovery transition did not pass.")
        probes = self._accept_lifecycle_samples(
            recovery, scenario_id=scenario_id, phase="recovery-probe"
        )
        if len(probes) != 2 or not all(sample.success for sample in probes):
            raise EvidenceVerificationError("Coordination recovery probes did not pass.")
        recovered = await self._load(
            affected,
            self.candidate.correctness_attempts - half,
            scenario_id=scenario_id,
            repetition=1,
            phase="recovered",
        )
        if not all(sample.success for sample in recovered.samples):
            raise EvidenceVerificationError(f"Scenario {scenario_id} did not recover.")
        await self._wait_conservation(
            before,
            sum(sample.success for sample in (*probes, *recovered.samples)),
        )
        combined = WorkloadResult(
            (*failed.samples, *probes, *recovered.samples),
            failed.elapsed_ms + recovered.elapsed_ms,
        )
        recovery_clock = self._recovery_clock(
            recovery,
            fault_started_ns=started,
            fault_observed_ns=fault_observed,
            dependency_restored_ns=dependency_restored,
        )
        return ScenarioObservation(
            scenario_id,
            1,
            started,
            time.monotonic_ns(),
            len(combined.samples),
            2,
            await self._verified_counters(combined.samples),
            recovery_clock=recovery_clock,
        )

    async def _performance_pair(self, repetition: int) -> tuple[ScenarioObservation, ...]:
        seed = self.candidate.pair_seeds[repetition - 1]
        # A graceful application shutdown is a cluster-wide drain transition,
        # not a neutral way to establish the one-replica performance baseline.
        self.controller.compose(ComposeAction.KILL, ("app-b",))
        self.controller.wait_http(f"{self.endpoints[0][1]}/ready")
        await self._warmup(
            (self.endpoints[0],),
            schedule_seed=seed,
            scenario_id="coordinated-baseline",
            repetition=repetition,
        )
        baseline = await self._observed_load(
            "coordinated-baseline",
            repetition,
            (self.endpoints[0],),
            self.candidate.measured_attempts,
            fault_milestones=0,
            require_all_success=True,
            schedule_seed=seed,
        )
        self.controller.compose(ComposeAction.START, ("app-b",))
        self.controller.wait_http(f"{self.endpoints[1][1]}/ready")
        await self._warmup(
            self.endpoints,
            schedule_seed=seed,
            scenario_id="coordinated-target",
            repetition=repetition,
        )
        target = await self._observed_load(
            "coordinated-target",
            repetition,
            self.endpoints,
            self.candidate.measured_attempts,
            fault_milestones=0,
            require_all_success=True,
            schedule_seed=seed,
        )
        return baseline, target

    async def _app_loss(self, lost: str, survivor: tuple[str, str]) -> ScenarioObservation:
        scenario_id = f"{lost}-loss"
        started = time.monotonic_ns()
        self.controller.compose(ComposeAction.KILL, (lost,))
        result = await self._observed_load(
            scenario_id,
            1,
            (survivor,),
            self.candidate.correctness_attempts,
            fault_milestones=1,
            require_all_success=True,
        )
        self.controller.compose(ComposeAction.UP, (lost,))
        endpoint = dict(self.endpoints)[lost]
        self.controller.wait_http(f"{endpoint}/ready")
        return ScenarioObservation(
            result.scenario_id,
            result.repetition,
            started,
            time.monotonic_ns(),
            result.challenged_operations,
            2,
            result.counters,
        )

    async def _redis_restart(self) -> ScenarioObservation:
        before = await self.oracle.snapshot()
        fixture_before = self.controller.fixture_state()
        started = time.monotonic_ns()
        self.controller.compose(ComposeAction.STOP, ("redis-primary",))
        failed = await self._load(
            self.endpoints,
            self.candidate.correctness_attempts // 2,
            scenario_id="redis-restart",
            repetition=1,
            phase="fault",
        )
        if any(sample.success for sample in failed.samples):
            raise EvidenceVerificationError(
                "Redis restart scenario admitted work without authority."
            )
        require_milestone_delta(
            fixture_before,
            self.controller.fixture_state(),
            ("redis:app-a:connect-failed", "redis:app-b:connect-failed"),
        )
        fault_observed = time.monotonic_ns()
        self.controller.compose(ComposeAction.START, ("redis-primary",))
        dependency_restored = time.monotonic_ns()
        recovery = await self.lifecycle_hook("recover-after-coordination-fault")
        if recovery.get("exercised") is not True or recovery.get("safe") is not True:
            raise EvidenceVerificationError("Redis restart recovery transition did not pass.")
        probes = self._accept_lifecycle_samples(
            recovery, scenario_id="redis-restart", phase="recovery-probe"
        )
        if len(probes) != 2 or not all(sample.success for sample in probes):
            raise EvidenceVerificationError("Redis restart recovery probes did not pass.")
        recovered = await self._load(
            self.endpoints,
            self.candidate.correctness_attempts - len(failed.samples),
            scenario_id="redis-restart",
            repetition=1,
            phase="recovered",
        )
        if not all(sample.success for sample in recovered.samples):
            raise EvidenceVerificationError("Redis restart scenario did not recover.")
        await self._wait_conservation(
            before,
            sum(sample.success for sample in (*probes, *recovered.samples)),
        )
        combined = WorkloadResult((*failed.samples, *probes, *recovered.samples), 1.0)
        recovery_clock = self._recovery_clock(
            recovery,
            fault_started_ns=started,
            fault_observed_ns=fault_observed,
            dependency_restored_ns=dependency_restored,
        )
        return ScenarioObservation(
            "redis-restart",
            1,
            started,
            time.monotonic_ns(),
            len(combined.samples),
            2,
            await self._verified_counters(combined.samples),
            recovery_clock=recovery_clock,
        )

    async def _standby_promotion(self) -> ScenarioObservation:
        before = await self.oracle.snapshot()
        started = time.monotonic_ns()
        self.controller.fault(FaultAction.REDIS_VERIFY_STANDBY_CAUGHT_UP)
        self.controller.compose(ComposeAction.STOP, ("redis-primary",))
        failed = await self._load(
            self.endpoints,
            1,
            scenario_id="redis-standby-promotion",
            repetition=1,
            phase="fault",
        )
        if any(sample.success for sample in failed.samples):
            raise EvidenceVerificationError("Former Redis primary isolation was not observed.")
        fault_observed = time.monotonic_ns()
        self.controller.fault(FaultAction.REDIS_PROMOTE_STANDBY)
        dependency_restored = time.monotonic_ns()
        recovery = await self.lifecycle_hook("recover-after-standby-promotion")
        if recovery.get("exercised") is not True or recovery.get("safe") is not True:
            raise EvidenceVerificationError("Standby promotion transition did not pass.")
        promotion_probes = self._accept_lifecycle_samples(
            recovery,
            scenario_id="redis-standby-promotion",
            phase="promotion-probe",
        )
        if len(promotion_probes) != 2 or not all(sample.success for sample in promotion_probes):
            raise EvidenceVerificationError("Standby promotion recovery probes did not pass.")
        result = await self._observed_load(
            "redis-standby-promotion",
            1,
            self.endpoints,
            self.candidate.correctness_attempts - 1,
            fault_milestones=2,
            require_all_success=True,
        )
        self.controller.compose(ComposeAction.START, ("redis-primary",))
        self.controller.fault(FaultAction.REDIS_RESTORE_PRIMARY)
        restored = await self.lifecycle_hook("recover-after-coordination-fault")
        if restored.get("exercised") is not True or restored.get("safe") is not True:
            raise EvidenceVerificationError("Primary restoration transition did not pass.")
        restoration_probes = self._accept_lifecycle_samples(
            restored,
            scenario_id="redis-standby-promotion",
            phase="restoration-probe",
        )
        if len(restoration_probes) != 2 or not all(sample.success for sample in restoration_probes):
            raise EvidenceVerificationError("Primary restoration probes did not pass.")
        probe_result = WorkloadResult(
            (*failed.samples, *promotion_probes, *restoration_probes), 1.0
        )
        all_successes = (
            sum(sample.success for sample in promotion_probes)
            + result.counters.client_success
            + sum(sample.success for sample in restoration_probes)
        )
        await self._wait_conservation(before, all_successes)
        recovery_clock = self._recovery_clock(
            recovery,
            fault_started_ns=started,
            fault_observed_ns=fault_observed,
            dependency_restored_ns=dependency_restored,
        )
        return ScenarioObservation(
            result.scenario_id,
            1,
            started,
            time.monotonic_ns(),
            result.challenged_operations
            + len(failed.samples)
            + len(promotion_probes)
            + len(restoration_probes),
            4,
            self._merge_counters(
                result.counters,
                await self._verified_counters(probe_result.samples),
            ),
            recovery_clock=recovery_clock,
        )

    async def _hook_observation(self, scenario_id: str) -> ScenarioObservation:
        started = time.monotonic_ns()
        result = await self.lifecycle_hook(scenario_id)
        if result.get("exercised") is not True or result.get("safe") is not True:
            raise EvidenceVerificationError(f"Lifecycle scenario {scenario_id} did not pass.")
        samples = self._accept_lifecycle_samples(result, scenario_id=scenario_id)
        challenged = int(result.get("challenged_operations", 1))
        sampled = await self._verified_counters(samples) if samples else CorrectnessCounters()
        return ScenarioObservation(
            scenario_id,
            1,
            started,
            time.monotonic_ns(),
            challenged,
            int(result.get("fault_milestones", 1)),
            replace(sampled, attempted=max(challenged, sampled.attempted)),
        )

    async def execute(self, bootstrap: BootstrapResult) -> MatrixExecution:
        observations: list[ScenarioObservation] = []
        for scenario_id, exercised, started, completed in (
            (
                "migration-interruption-resume",
                bootstrap.migration_resumed,
                bootstrap.migration_started_ns,
                bootstrap.migration_completed_ns,
            ),
            (
                "bootstrap-interruption",
                bootstrap.bootstrap_replayed,
                bootstrap.bootstrap_started_ns,
                bootstrap.bootstrap_completed_ns,
            ),
        ):
            if not exercised:
                raise EvidenceVerificationError(f"Setup scenario {scenario_id} was not exercised.")
            observations.append(
                ScenarioObservation(
                    scenario_id,
                    1,
                    started,
                    completed,
                    1,
                    1,
                    CorrectnessCounters(attempted=1),
                )
            )

        for repetition in range(1, self.candidate.pair_repetitions + 1):
            observations.extend(await self._performance_pair(repetition))
        observations.append(await self._bounded(self._app_loss("app-a", self.endpoints[1])))
        observations.append(await self._bounded(self._app_loss("app-b", self.endpoints[0])))
        observations.append(
            await self._bounded(
                self._fault_recovery(
                    "redis-app-a-interruption",
                    FaultAction.REDIS_APP_A_BLOCK,
                    (self.endpoints[0],),
                )
            )
        )
        observations.append(
            await self._bounded(
                self._fault_recovery(
                    "redis-app-b-interruption",
                    FaultAction.REDIS_APP_B_BLOCK,
                    (self.endpoints[1],),
                )
            )
        )
        observations.append(
            await self._bounded(
                self._fault_recovery(
                    "redis-both-paths-interruption",
                    FaultAction.REDIS_ALL_BLOCK,
                    self.endpoints,
                )
            )
        )
        observations.append(await self._bounded(self._redis_restart()))
        observations.append(await self._bounded(self._standby_promotion()))
        for scenario_id in ("stale-epoch", "partial-namespace"):
            observations.append(await self._bounded(self._hook_observation(scenario_id)))
        observations.append(
            await self._bounded(
                self._fault_recovery(
                    "postgresql-outage", FaultAction.POSTGRES_ALL_BLOCK, self.endpoints
                )
            )
        )
        observations.append(
            await self._bounded(self._hook_observation("cancellation-unknown-outcome"))
        )
        observations.append(await self._bounded(self._hook_observation("duplicate-delivery")))
        observations.append(
            await self._bounded(self._hook_observation("drain-reconcile-mark-ready"))
        )
        observations.append(await self._bounded(self._hook_observation("standalone-rollback")))
        expected = {
            (scenario, repetition)
            for scenario in self.candidate.required_scenarios
            for repetition in (
                range(1, self.candidate.pair_repetitions + 1)
                if scenario.startswith("coordinated-")
                else (1,)
            )
        }
        actual = {(item.scenario_id, item.repetition) for item in observations}
        if actual != expected or len(actual) != len(observations):
            raise EvidenceVerificationError("Matrix execution inventory is incomplete.")
        if any(
            item.challenged_operations
            != expected_challenged_operations(self.candidate, item.scenario_id)
            or item.fault_milestones != expected_fault_milestones(item.scenario_id)
            or item.counters.attempted != item.challenged_operations
            for item in observations
        ):
            raise EvidenceVerificationError("Matrix scenario workload is incomplete.")
        if len(self._samples) != self.candidate.expected_sample_count:
            raise EvidenceVerificationError("Matrix sample inventory is incomplete.")
        if set(self._oracle_evidence) != {
            str(sample["operation_digest"]) for sample in self._samples
        }:
            raise EvidenceVerificationError("Oracle evidence does not cover every HTTP sample.")
        return MatrixExecution(
            tuple(observations),
            tuple(self._samples),
            tuple(
                self._oracle_evidence[digest].safe_dict()
                for digest in sorted(self._oracle_evidence)
            ),
        )


def opaque_run_id(candidate: CandidateTopology) -> str:
    value = hashlib.sha256(
        b"omni-ha-evidence-run-v1\x00"
        + candidate.digest.encode("ascii")
        + time.time_ns().to_bytes(8, "big")
    ).hexdigest()
    return "w4c_" + value[:32]
