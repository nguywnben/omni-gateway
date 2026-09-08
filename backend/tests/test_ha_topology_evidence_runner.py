from __future__ import annotations

import asyncio
import dataclasses
import hashlib
import json
import os
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.durable_migration import DURABLE_COPY_FAMILIES
from core.storage.durable_family_sqlite import SQLiteDurableFamilyAdapter

from backend.tests.support import workspace_temp_directory
from tools.ha_topology_evidence.bootstrap import (
    _initialize_sqlite_source,
    _interrupt_after_durable_write,
)
from tools.ha_topology_evidence.candidate import launcher_digest, verify_launcher_package
from tools.ha_topology_evidence.contract import (
    CorrectnessCounters,
    EvidenceVerificationError,
    RecoveryClock,
)
from tools.ha_topology_evidence.fixture import FaultAction, FixtureState
from tools.ha_topology_evidence.lifecycle import LifecycleScenarioDriver
from tools.ha_topology_evidence.load import RequestSample, WorkloadResult, run_workload
from tools.ha_topology_evidence.oracle import (
    DurableOracle,
    DurableOracleSnapshot,
    OperationOracleEvidence,
    assert_conservation,
    opaque_operation_digest,
)
from tools.ha_topology_evidence.report import EvidenceReportWriter, scan_secret_free
from tools.ha_topology_evidence.runner import (
    MatrixRunner,
    ScenarioObservation,
    _outcome_summary,
    opaque_run_id,
    require_milestone_delta,
)
from tools.ha_topology_evidence.scenarios import (
    SCENARIO_SPECS,
    CleanupScope,
    ComposeAction,
    HostController,
    ProjectResources,
    _labeled_names,
    cleanup_project_resources,
    create_cleanup_scope,
    require_immutable_image_reference,
    require_loopback_http_url,
    verify_cleanup_scope,
)

ROOT = Path(__file__).resolve().parents[2]


def snapshot(*, traces: int = 1, usage: int = 1) -> DurableOracleSnapshot:
    return DurableOracleSnapshot(1, traces, usage, usage, usage, 0, 0, 1, 1, 1, "a" * 64)


class FixtureTests(unittest.IsolatedAsyncioTestCase):
    async def test_process_death_boundary_terminates_owner_after_atomic_milestone(self) -> None:
        class Process:
            def __init__(self) -> None:
                self.returncode = None
                self.terminated = False

            def terminate(self) -> None:
                self.terminated = True
                self.returncode = -15

            def kill(self) -> None:
                self.returncode = -9

            async def wait(self) -> int:
                return int(self.returncode or 0)

        process = Process()

        async def spawn(*arguments, **_kwargs):
            spec_path = Path(arguments[arguments.index("--spec") + 1])
            spec = json.loads(await asyncio.to_thread(spec_path.read_text, encoding="utf-8"))
            await asyncio.to_thread(
                Path(spec["milestone"]).write_bytes,
                b"durable-write-complete\n",
            )
            return process

        with (
            workspace_temp_directory() as directory,
            patch(
                "tools.ha_topology_evidence.bootstrap.asyncio.create_subprocess_exec",
                side_effect=spawn,
            ),
        ):
            await _interrupt_after_durable_write("migration", Path(directory), {"synthetic": True})
        self.assertTrue(process.terminated)

    async def test_fault_surface_is_closed_and_state_transitions_are_exact(self) -> None:
        state = FixtureState()
        await state.apply(FaultAction.REDIS_APP_A_BLOCK)
        self.assertEqual(state.redis_enabled, {"app-a": False, "app-b": True})
        self.assertEqual(state.fault_revision, 1)
        await state.apply(FaultAction.POSTGRES_ALL_BLOCK)
        self.assertEqual(state.postgres_enabled, {"app-a": False, "app-b": False})
        await state.apply(FaultAction.RESET)
        self.assertEqual(state.redis_enabled, {"app-a": True, "app-b": True})
        self.assertEqual(state.postgres_enabled, {"app-a": True, "app-b": True})


class ScenarioAndOracleTests(unittest.TestCase):
    def test_outcome_summary_contains_only_bounded_status_counts(self) -> None:
        samples = (
            RequestSample(1, "app-a", 200, 1.0, True, False),
            RequestSample(2, "app-b", 503, 1.0, False, False),
            RequestSample(3, "app-a", 0, 1.0, False, True, transport_error="timeout"),
        )
        self.assertEqual(
            _outcome_summary(samples),
            "statuses=0:1,200:1,503:1;transport_failures=1;transport_errors=timeout:1",
        )

    def test_fault_acknowledgement_requires_an_observed_data_path_milestone(self) -> None:
        require_milestone_delta(
            {"milestones": {"redis:app-a:blocked": 1}},
            {"milestones": {"redis:app-a:blocked": 2}},
            ("redis:app-a:blocked",),
        )
        with self.assertRaises(EvidenceVerificationError):
            require_milestone_delta(
                {"milestones": {"redis:app-a:blocked": 1}},
                {"milestones": {"redis:app-a:blocked": 1}},
                ("redis:app-a:blocked",),
            )

    def test_scenario_inventory_is_exact_and_every_safety_scenario_has_a_milestone(self) -> None:
        from tools.ha_topology_evidence.contract import REQUIRED_SCENARIOS

        self.assertEqual(tuple(item.scenario_id for item in SCENARIO_SPECS), REQUIRED_SCENARIOS)
        self.assertTrue(
            all(
                not item.requires_fault_milestone
                or item.scenario_id not in {"coordinated-baseline", "coordinated-target"}
                for item in SCENARIO_SPECS
            )
        )
        actions = {item.scenario_id: item.fault_action for item in SCENARIO_SPECS}
        self.assertIsNone(actions["app-a-loss"])
        self.assertIsNone(actions["app-b-loss"])
        self.assertIsNone(actions["redis-restart"])
        self.assertIs(actions["redis-app-a-interruption"], FaultAction.REDIS_APP_A_BLOCK)

    def test_host_controller_uses_only_argument_vectors_and_known_services(self) -> None:
        controller = HostController(
            (ROOT / "deploy" / "evidence" / "compose.ha.yml").resolve(),
            "w4c-123456789abc",
            "http://127.0.0.1:18081",
        )
        with patch("subprocess.run") as run:
            controller.compose(ComposeAction.KILL, ("app-a",))
        arguments = run.call_args.args[0]
        self.assertEqual(arguments[-3:], ["--signal", "SIGKILL", "app-a"])
        self.assertFalse(run.call_args.kwargs["shell"])
        with self.assertRaises(EvidenceVerificationError):
            controller.compose(ComposeAction.STOP, ("unknown",))
        with self.assertRaises(EvidenceVerificationError):
            controller.fault(FaultAction.RESET)
        with patch("subprocess.run") as run:
            controller.compose(ComposeAction.RECREATE, ("app-a",))
        self.assertIn("--force-recreate", run.call_args.args[0])

    def test_redis_restore_control_timeout_covers_the_bounded_replication_wait(self) -> None:
        timeouts: list[float] = []

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

            def read(self, _limit: int) -> bytes:
                return json.dumps({"action": FaultAction.REDIS_RESTORE_PRIMARY.value}).encode(
                    "ascii"
                )

        class Opener:
            def open(self, _request, *, timeout: float):
                timeouts.append(timeout)
                return Response()

        controller = HostController(
            (ROOT / "deploy" / "evidence" / "compose.ha.yml").resolve(),
            "w4c-123456789abc",
            "http://127.0.0.1:18081",
            control_token="s" * 32,
        )
        with patch(
            "tools.ha_topology_evidence.scenarios.loopback_opener",
            return_value=Opener(),
        ):
            controller.fault(FaultAction.REDIS_RESTORE_PRIMARY)
        self.assertEqual(timeouts, [30.0])

    def test_loopback_url_validation_rejects_userinfo_and_external_hosts(self) -> None:
        self.assertEqual(
            require_loopback_http_url("http://127.0.0.1:18081"),
            "http://127.0.0.1:18081",
        )
        for value in (
            "http://127.0.0.1:@external.example",
            "http://localhost:18081",
            "https://127.0.0.1:18081",
        ):
            with self.subTest(value=value):
                with self.assertRaises(EvidenceVerificationError):
                    require_loopback_http_url(value)

    def test_evidence_image_reference_must_equal_its_immutable_identity(self) -> None:
        identity = "sha256:" + "a" * 64
        self.assertEqual(require_immutable_image_reference(identity, identity), identity)
        named = "omni-gateway@" + identity
        self.assertEqual(require_immutable_image_reference(named, identity), named)
        for reference in ("omni-gateway:latest", "omni-gateway@sha256:" + "b" * 64):
            with self.subTest(reference=reference):
                with self.assertRaises(EvidenceVerificationError):
                    require_immutable_image_reference(reference, identity)

    def test_cleanup_inventory_rejects_resources_outside_the_project_prefix(self) -> None:
        resources = ProjectResources(
            "w4c-123456789abc",
            ("a" * 12,),
            ("w4c-123456789abc_postgres-data",),
            ("w4c-123456789abc_evidence",),
        )
        self.assertEqual(resources.safe_summary()["project"], "w4c-123456789abc")
        with self.assertRaises(EvidenceVerificationError):
            ProjectResources(
                "w4c-123456789abc",
                (),
                ("unrelated_postgres-data",),
                (),
            )

    def test_labeled_resource_inventory_reads_names_not_engine_ids(self) -> None:
        project = "w4c-123456789abc"
        with patch(
            "tools.ha_topology_evidence.scenarios._run_read_only",
            return_value=f"{project}_evidence\n",
        ) as run:
            self.assertEqual(_labeled_names("network", project), (f"{project}_evidence",))
        self.assertEqual(
            run.call_args.args[0],
            [
                "docker",
                "network",
                "ls",
                "--format",
                "{{.Name}}",
                "--filter",
                f"label=com.docker.compose.project={project}",
            ],
        )

    def test_cleanup_scope_is_create_only_authenticated_and_tamper_evident(self) -> None:
        empty = ProjectResources("w4c-123456789abc", (), (), ())
        with patch(
            "tools.ha_topology_evidence.scenarios._project_resources",
            return_value=empty,
        ):
            scope = create_cleanup_scope("w4c-123456789abc", b"k" * 32)
        self.assertTrue(verify_cleanup_scope(scope, b"k" * 32))
        self.assertFalse(verify_cleanup_scope(scope, b"z" * 32))
        self.assertFalse(
            verify_cleanup_scope(CleanupScope(scope.project, "1" * 32, scope.signature), b"k" * 32)
        )
        occupied = ProjectResources("w4c-123456789abc", ("a" * 12,), (), ())
        with (
            patch(
                "tools.ha_topology_evidence.scenarios._project_resources",
                return_value=occupied,
            ),
            self.assertRaisesRegex(EvidenceVerificationError, "already owns"),
        ):
            create_cleanup_scope("w4c-123456789abc", b"k" * 32)

    def test_cleanup_snapshots_once_and_deletes_only_that_exact_scope(self) -> None:
        empty = ProjectResources("w4c-123456789abc", (), (), ())
        with patch(
            "tools.ha_topology_evidence.scenarios._project_resources",
            return_value=empty,
        ):
            scope = create_cleanup_scope("w4c-123456789abc", b"k" * 32)
        resources = ProjectResources(
            scope.project,
            ("a" * 12,),
            (scope.project + "_postgres-data",),
            (scope.project + "_evidence",),
        )
        with (
            patch(
                "tools.ha_topology_evidence.scenarios._project_resources",
                return_value=resources,
            ) as snapshot_scope,
            patch("subprocess.run") as run,
        ):
            removed = cleanup_project_resources(scope, b"k" * 32)
        self.assertEqual(removed, resources)
        snapshot_scope.assert_called_once_with(scope.project)
        self.assertEqual(run.call_count, 3)
        self.assertEqual(run.call_args_list[0].args[0], ["docker", "rm", "-f", "a" * 12])

    def test_recovery_clock_is_monotonic_and_includes_whole_fault_window(self) -> None:
        clock = RecoveryClock(1, 2, 3, 4, 5, 6, 7_000_001)
        self.assertEqual(clock.recovery_ms, 7.0)
        with self.assertRaises(EvidenceVerificationError):
            RecoveryClock(2, 1, 3, 4, 5, 6, 7)

    def test_workload_summary_uses_successful_samples_and_never_contains_payloads(self) -> None:
        result = WorkloadResult(
            (
                RequestSample(1, "app-a", 200, 10.0, True, False),
                RequestSample(2, "app-b", 200, 20.0, True, False),
                RequestSample(3, "app-a", 503, 5.0, False, False),
            ),
            1000.0,
        )
        self.assertEqual(result.p95_ms, 20.0)
        self.assertEqual(result.successful_throughput_rps, 2.0)
        self.assertEqual(result.counters.client_success, 2)
        self.assertEqual(result.counters.rejected, 1)
        self.assertNotIn("content", result.samples[0].safe_dict())

    def test_request_sample_rejects_contradictory_or_non_boolean_outcomes(self) -> None:
        for values in (
            (200, 1, False),
            (503, True, False),
            (200, True, True),
            (503, False, True),
        ):
            with self.subTest(values=values):
                with self.assertRaises(EvidenceVerificationError):
                    RequestSample(1, "app-a", values[0], 1.0, values[1], values[2])

    def test_runner_observation_is_metadata_only_and_run_id_is_opaque(self) -> None:
        observation = ScenarioObservation(
            "stale-epoch", 1, 1, 2, 1, 1, CorrectnessCounters(attempted=1)
        )
        self.assertEqual(observation.duration_ms, 0.000001)
        self.assertNotIn("body", observation.safe_event())
        from backend.tests.test_ha_topology_evidence_contract import candidate

        self.assertRegex(opaque_run_id(candidate()), r"^w4c_[0-9a-f]{32}$")
        self.assertRegex(launcher_digest(ROOT), r"^[0-9a-f]{64}$")

    def test_launcher_package_must_match_the_frozen_digest(self) -> None:
        from backend.tests.test_ha_topology_evidence_contract import candidate

        topology = dataclasses.replace(
            candidate(),
            evidence_launcher_digest=launcher_digest(ROOT),
        )
        verify_launcher_package(topology, ROOT)
        with self.assertRaisesRegex(EvidenceVerificationError, "launcher"):
            verify_launcher_package(
                dataclasses.replace(topology, evidence_launcher_digest="9" * 64),
                ROOT,
            )

    def test_oracle_operation_digests_are_opaque_and_conservation_is_exact(self) -> None:
        first = opaque_operation_digest("operation-a", b"k" * 32)
        second = opaque_operation_digest("operation-b", b"k" * 32)
        self.assertNotEqual(first, second)
        self.assertNotIn("operation", first)
        assert_conservation(snapshot(), snapshot(traces=2, usage=2), successful_operations=1)
        with self.assertRaises(RuntimeError):
            assert_conservation(snapshot(), snapshot(traces=1, usage=2), successful_operations=1)


class RecoveryTransitionTests(unittest.IsolatedAsyncioTestCase):
    async def test_unknown_outcome_proves_route_backoff_then_recovers(self) -> None:
        from backend.tests.test_ha_topology_evidence_contract import candidate

        class Controller:
            def __init__(self) -> None:
                self.dropped = 0

            def fault(self, action) -> None:
                self.asserted_action = action
                self.dropped += 1

            def fixture_state(self):
                return {"milestones": {"provider-response-dropped": self.dropped}}

        driver = object.__new__(LifecycleScenarioDriver)
        driver.candidate = candidate()
        driver.controller = Controller()
        driver.endpoints = (
            ("app-a", "http://127.0.0.1:14283"),
            ("app-b", "http://127.0.0.1:14284"),
        )
        driver.api_key = "sk-ogw-synthetic"
        driver.oracle = AsyncMock()
        driver.oracle.snapshot.return_value = snapshot()
        backoff_samples = (
            RequestSample(200_000, "app-a", 503, 1.0, False, False).safe_dict(
                include_request_id=True
            ),
            RequestSample(200_001, "app-b", 503, 1.0, False, False).safe_dict(
                include_request_id=True
            ),
        )
        recovered_samples = (
            RequestSample(200_002, "app-a", 200, 1.0, True, False).safe_dict(
                include_request_id=True
            ),
            RequestSample(200_003, "app-b", 200, 1.0, True, False).safe_dict(
                include_request_id=True
            ),
        )
        driver._probe = AsyncMock(side_effect=(backoff_samples, recovered_samples))
        failed = WorkloadResult(
            (RequestSample(90_000, "app-a", 500, 1.0, False, False),),
            1.0,
        )

        with (
            patch(
                "tools.ha_topology_evidence.lifecycle.run_workload",
                new=AsyncMock(return_value=failed),
            ),
            patch("tools.ha_topology_evidence.lifecycle.asyncio.sleep", new=AsyncMock()) as sleep,
        ):
            result = await driver.cancellation_unknown_outcome()

        self.assertEqual(result["challenged_operations"], 5)
        self.assertEqual(len(result["samples"]), 5)
        self.assertEqual(
            [sample["status_code"] for sample in result["samples"]],
            [500, 503, 503, 200, 200],
        )
        self.assertEqual(
            driver._probe.await_args_list,
            [unittest.mock.call(expect_success=False), unittest.mock.call(expect_success=True)],
        )
        sleep.assert_awaited_once_with(2.5)

    async def test_recovery_waits_for_restarted_coordination_before_transition(self) -> None:
        from core.coordination import CoordinationUnavailableError

        driver = object.__new__(LifecycleScenarioDriver)
        driver.epoch = 4
        expected = object()
        coordination = AsyncMock()
        coordination.snapshot.side_effect = (
            CoordinationUnavailableError("synthetic startup race"),
            expected,
        )
        with patch("tools.ha_topology_evidence.lifecycle.asyncio.sleep", new=AsyncMock()) as sleep:
            observed = await driver._initial_coordination_snapshot(coordination)
        self.assertIs(observed, expected)
        self.assertEqual(coordination.snapshot.await_count, 2)
        sleep.assert_awaited_once_with(0.1)

    async def test_recovery_fails_closed_when_coordination_never_restarts(self) -> None:
        from core.coordination import CoordinationUnavailableError

        driver = object.__new__(LifecycleScenarioDriver)
        driver.epoch = 4
        coordination = AsyncMock()
        coordination.snapshot.side_effect = CoordinationUnavailableError(
            "synthetic persistent outage"
        )
        with (
            patch(
                "tools.ha_topology_evidence.lifecycle.time.monotonic",
                side_effect=(100.0, 110.0),
            ),
            self.assertRaisesRegex(
                EvidenceVerificationError,
                "did not become available",
            ),
        ):
            await driver._initial_coordination_snapshot(coordination)
        coordination.snapshot.assert_awaited_once_with(expected_epoch=4)

    async def test_host_lifecycle_admin_isolates_legacy_usage_source(self) -> None:
        from backend.tests.test_ha_topology_evidence_contract import candidate

        class Policy:
            coordination_namespace = "isolated-admin"

        with workspace_temp_directory() as directory:
            root = Path(directory)
            host_credentials = root / "host-credentials"
            evidence_credentials = root / "evidence-credentials"
            host_credentials.mkdir()
            evidence_credentials.mkdir()
            driver = object.__new__(LifecycleScenarioDriver)
            driver.candidate = candidate()
            driver.environment = {
                "EVIDENCE_NAMESPACE": "w4c-evidence-isolated",
                "EVIDENCE_DEPLOYMENT_ID": "w4c-evidence-isolated",
                "EVIDENCE_COORDINATION_KEY": "a" * 43,
            }
            driver.host_postgresql_uri = "postgresql://omni@127.0.0.1:15434/test"
            driver.host_redis_url = "redis://127.0.0.1:16381/0"
            driver.host_credentials_dir = evidence_credentials
            storage = AsyncMock()
            storage.close.side_effect = RuntimeError("synthetic close failure")
            store = AsyncMock()

            with (
                patch.dict(os.environ, {"CREDENTIALS_DIR": str(host_credentials)}),
                patch(
                    "tools.ha_topology_evidence.lifecycle.PostgreSQLManager",
                    return_value=storage,
                ),
                patch(
                    "tools.ha_topology_evidence.lifecycle.RedisStateStore",
                    return_value=store,
                ),
                patch(
                    "tools.ha_topology_evidence.lifecycle.experimental_policy",
                    return_value=Policy(),
                ),
                patch(
                    "tools.ha_topology_evidence.lifecycle.CandidateVerifier.exact",
                    return_value=object(),
                ),
                patch(
                    "tools.ha_topology_evidence.lifecycle.CandidateAdmin",
                    return_value=object(),
                ),
            ):
                with self.assertRaisesRegex(RuntimeError, "synthetic close failure"):
                    async with driver._admin(1):
                        self.assertEqual(
                            Path(os.environ["CREDENTIALS_DIR"]),
                            evidence_credentials,
                        )
                self.assertEqual(Path(os.environ["CREDENTIALS_DIR"]), host_credentials)

    async def test_performance_baseline_removes_second_replica_without_cluster_drain(self) -> None:
        from backend.tests.test_ha_topology_evidence_contract import candidate

        class Controller:
            def __init__(self) -> None:
                self.actions = []

            def compose(self, action, services=()):
                self.actions.append((action, services))

            def wait_http(self, _url):
                return 200

        controller = Controller()
        runner = object.__new__(MatrixRunner)
        runner.candidate = candidate()
        runner.controller = controller
        runner.endpoints = (
            ("app-a", "http://127.0.0.1:14283"),
            ("app-b", "http://127.0.0.1:14284"),
        )
        observation = ScenarioObservation(
            "coordinated-baseline", 1, 1, 2, 1, 0, CorrectnessCounters(attempted=1)
        )
        with (
            patch.object(runner, "_warmup", AsyncMock()),
            patch.object(runner, "_observed_load", AsyncMock(return_value=observation)),
        ):
            await runner._performance_pair(1)

        self.assertEqual(
            controller.actions,
            [
                (ComposeAction.KILL, ("app-b",)),
                (ComposeAction.START, ("app-b",)),
            ],
        )

    async def test_durable_oracle_reads_usage_request_identity_from_json_payload(self) -> None:
        request_id = "w4e-" + "1" * 32
        operation_key = b"k" * 32
        sample = RequestSample(
            1,
            "app-a",
            200,
            1.0,
            True,
            False,
            request_id,
            opaque_operation_digest(request_id, operation_key),
            "d" * 64,
        )
        connection = AsyncMock()
        connection.fetch.side_effect = (
            [{"request_id": request_id, "total": 1}],
            [{"request_id": request_id, "total": 1}],
            [{"request_id": request_id, "total": 1, "successful": 1}],
        )
        with patch(
            "tools.ha_topology_evidence.oracle.asyncpg.connect",
            AsyncMock(return_value=connection),
        ):
            evidence = await DurableOracle(
                "postgresql://omni@127.0.0.1:15434/test"
            ).operation_evidence(
                (sample,),
                operation_key=operation_key,
            )

        usage_query = connection.fetch.await_args_list[2].args[0]
        self.assertIn("payload->>'request_id'", usage_query)
        self.assertIn("payload->'usage'->>'request_id'", usage_query)
        self.assertIn("kind = 'reservation' AND state = 'committed'", usage_query)
        self.assertEqual(evidence[0].usage_events, 1)
        self.assertEqual(evidence[0].successful_usage_events, 1)

    async def test_durable_oracle_snapshot_counts_committed_reservations_as_usage(self) -> None:
        connection = AsyncMock()
        connection.fetchval.return_value = 0
        connection.fetchrow.return_value = {
            "usage_records": 1,
            "usage_events": 1,
            "successful_usage_events": 1,
            "active_reservations": 0,
            "active_liability_nanos": 0,
        }
        connection.fetch.return_value = []
        with patch(
            "tools.ha_topology_evidence.oracle.asyncpg.connect",
            AsyncMock(return_value=connection),
        ):
            snapshot_value = await DurableOracle(
                "postgresql://omni@127.0.0.1:15434/test"
            ).snapshot()

        ledger_query = connection.fetchrow.await_args.args[0]
        self.assertIn("kind = 'reservation' AND state = 'committed'", ledger_query)
        self.assertEqual(snapshot_value.usage_events, 1)

    async def test_performance_warmup_requires_success_and_durable_conservation(self) -> None:
        from backend.tests.test_ha_topology_evidence_contract import candidate

        topology = candidate()
        oracle = AsyncMock()
        oracle.snapshot.return_value = snapshot()

        async def lifecycle(_scenario: str) -> dict[str, object]:
            return {"exercised": True, "safe": True}

        runner = MatrixRunner(
            topology,
            object(),
            oracle,
            app_a_url="http://127.0.0.1:14283",
            app_b_url="http://127.0.0.1:14284",
            api_key="sk-ogw-synthetic",
            lifecycle_hook=lifecycle,
        )
        successful = tuple(
            RequestSample(index, "app-a", 200, 1.0, True, False)
            for index in range(topology.warmup_requests)
        )
        with (
            patch.object(
                runner,
                "_load",
                AsyncMock(return_value=WorkloadResult(successful, 1.0)),
            ),
            patch.object(runner, "_wait_conservation", AsyncMock()) as conservation,
        ):
            await runner._warmup(runner.endpoints, schedule_seed=topology.pair_seeds[0])
            conservation.assert_awaited_once_with(snapshot(), topology.warmup_requests)

        failed = (*successful[:-1], RequestSample(999, "app-b", 503, 1.0, False, False))
        with patch.object(
            runner,
            "_load",
            AsyncMock(return_value=WorkloadResult(failed, 1.0)),
        ):
            with self.assertRaisesRegex(EvidenceVerificationError, "warm-up"):
                await runner._warmup(runner.endpoints, schedule_seed=topology.pair_seeds[0])

    async def test_synthetic_migration_source_populates_every_copy_family(self) -> None:
        with workspace_temp_directory() as directory:
            manager, path = await _initialize_sqlite_source(Path(directory))
            self.addAsyncCleanup(manager.close)
            adapter = SQLiteDurableFamilyAdapter(
                path,
                instance_id="ins_" + "1" * 32,
            )

            counts = {
                family: len(
                    (
                        await adapter.read_page(
                            family=family,
                            offset=0,
                            limit=10,
                        )
                    ).records
                )
                for family in DURABLE_COPY_FAMILIES
            }

            self.assertEqual(set(counts), set(DURABLE_COPY_FAMILIES))
            self.assertTrue(all(count > 0 for count in counts.values()), counts)

    async def test_cache_boundary_requires_hit_then_post_epoch_miss(self) -> None:
        from backend.tests.test_ha_topology_evidence_contract import candidate

        class Controller:
            def __init__(self):
                self.reads = 0

            def fixture_state(self):
                values = (10, 11, 13, 14)
                value = values[self.reads]
                self.reads += 1
                return {"provider_attempts": value}

        driver = object.__new__(LifecycleScenarioDriver)
        driver.controller = Controller()
        driver.endpoints = (
            ("app-a", "http://127.0.0.1:14283"),
            ("app-b", "http://127.0.0.1:14284"),
        )
        driver.api_key = "sk-ogw-synthetic"
        driver.candidate = candidate()
        driver._transition = AsyncMock(
            return_value={
                "samples": (
                    RequestSample(200_000, "app-a", 200, 1.0, True, False).safe_dict(),
                    RequestSample(200_001, "app-b", 200, 1.0, True, False).safe_dict(),
                )
            }
        )

        async def workload(*_args, **kwargs):
            sequence = kwargs["sequence_offset"]
            return WorkloadResult(
                (RequestSample(sequence, "app-a", 200, 1.0, True, False),),
                1.0,
            )

        with patch(
            "tools.ha_topology_evidence.lifecycle.run_workload",
            new=workload,
        ):
            samples = await driver._exercise_cache_epoch_boundary()

        self.assertEqual(
            [item["sequence"] for item in samples],
            [70_000, 70_001, 200_000, 200_001, 70_002],
        )
        driver._transition.assert_awaited_once_with(probe_stale=False)

    async def test_workload_can_bind_unique_samples_to_one_cache_request(self) -> None:
        seen: list[tuple[int, int]] = []
        clients = []

        async def send(sample_sequence, request_sequence, _operation_sequence, replica, *args):
            seen.append((sample_sequence, request_sequence))
            clients.append(args[-1])
            return RequestSample(sample_sequence, replica, 200, 1.0, True, False)

        with (
            patch("tools.ha_topology_evidence.load._send_request", side_effect=send),
            patch(
                "tools.ha_topology_evidence.load.asyncio.to_thread",
                side_effect=AssertionError("HTTP transport must stay on the event loop"),
            ),
        ):
            result = await run_workload(
                (("app-a", "http://127.0.0.1:14283"),),
                api_key="sk-ogw-synthetic",
                attempts=2,
                concurrency=2,
                offered_rps=10_000,
                request_deadline_ms=5_000,
                sequence_offset=10,
                request_sequence_offset=20,
            )

        self.assertEqual(seen, [(10, 20), (11, 21)])
        self.assertEqual([sample.sequence for sample in result.samples], [10, 11])
        self.assertTrue(all(isinstance(client, httpx.AsyncClient) for client in clients))
        self.assertIs(clients[0], clients[1])

    async def test_workload_identity_can_be_decoupled_from_authentication_key(self) -> None:
        identity_key = b"i" * 32
        observed_keys = []

        async def send(sample_sequence, _request_sequence, _operation_sequence, replica, *args):
            observed_keys.append(args[-2])
            return RequestSample(sample_sequence, replica, 200, 1.0, True, False)

        with patch("tools.ha_topology_evidence.load._send_request", side_effect=send):
            await run_workload(
                (("app-a", "http://127.0.0.1:14283"),),
                api_key="sk-ogw-different-authentication-key",
                operation_identity_key=identity_key,
                attempts=1,
                concurrency=1,
                offered_rps=1,
                request_deadline_ms=5_000,
            )

        self.assertEqual(observed_keys, [identity_key])

    async def test_workload_expires_idle_connections_before_hypercorn(self) -> None:
        captured = {}

        class Client:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *_args):
                return None

        def client_factory(**kwargs):
            captured.update(kwargs)
            return Client()

        async def send(sample_sequence, _request_sequence, _operation_sequence, replica, *_args):
            return RequestSample(sample_sequence, replica, 200, 1.0, True, False)

        with (
            patch("tools.ha_topology_evidence.load.httpx.AsyncClient", side_effect=client_factory),
            patch("tools.ha_topology_evidence.load._send_request", side_effect=send),
        ):
            await run_workload(
                (("app-a", "http://127.0.0.1:14283"),),
                api_key="sk-ogw-synthetic",
                attempts=1,
                concurrency=1,
                offered_rps=1,
                request_deadline_ms=5_000,
            )

        self.assertEqual(captured["limits"].keepalive_expiry, 4.0)

    async def test_predeclared_seed_changes_the_deterministic_replica_schedule(self) -> None:
        async def send(sample_sequence, _request_sequence, _operation_sequence, replica, *_args):
            return RequestSample(sample_sequence, replica, 200, 1.0, True, False)

        schedules = []
        with patch("tools.ha_topology_evidence.load._send_request", side_effect=send):
            for seed in (104_729, 130_363):
                result = await run_workload(
                    (
                        ("app-a", "http://127.0.0.1:14283"),
                        ("app-b", "http://127.0.0.1:14284"),
                    ),
                    api_key="sk-ogw-synthetic",
                    attempts=8,
                    concurrency=8,
                    offered_rps=10_000,
                    request_deadline_ms=5_000,
                    schedule_seed=seed,
                )
                schedules.append(tuple(sample.replica for sample in result.samples))

        self.assertNotEqual(schedules[0], schedules[1])
        self.assertEqual(set(schedules[0]), {"app-a", "app-b"})
        self.assertEqual(set(schedules[1]), {"app-a", "app-b"})

    async def test_workload_deadline_includes_concurrency_queue_time(self) -> None:
        async def send(sample_sequence, _request_sequence, _operation_sequence, replica, *args):
            await asyncio.sleep(0.2)
            return RequestSample(sample_sequence, replica, 200, 200.0, True, False)

        with patch("tools.ha_topology_evidence.load._send_request", side_effect=send) as mocked:
            result = await run_workload(
                (("app-a", "http://127.0.0.1:14283"),),
                api_key="sk-ogw-synthetic",
                attempts=2,
                concurrency=1,
                offered_rps=10_000,
                request_deadline_ms=100,
            )

        self.assertEqual(mocked.call_count, 1)
        self.assertTrue(result.samples[1].transport_failure)
        self.assertEqual(result.samples[1].transport_error, "timeout")
        self.assertEqual(result.samples[1].status_code, 0)
        self.assertLess(result.elapsed_ms, 1_000)

    async def test_correctness_scenario_timeout_fails_closed(self) -> None:
        from backend.tests.test_ha_topology_evidence_contract import candidate

        runner = object.__new__(MatrixRunner)
        runner.candidate = candidate()
        operation = AsyncMock(
            return_value=ScenarioObservation(
                "stale-epoch", 1, 1, 2, 1, 1, CorrectnessCounters(attempted=1)
            )
        )()
        with patch("tools.ha_topology_evidence.runner.asyncio.wait_for", side_effect=TimeoutError):
            with self.assertRaisesRegex(EvidenceVerificationError, "timeout"):
                await runner._bounded(operation)
        operation.close()

    async def test_positive_lifecycle_probe_requires_every_replica_to_succeed(self) -> None:
        from backend.tests.test_ha_topology_evidence_contract import candidate

        driver = object.__new__(LifecycleScenarioDriver)
        driver.endpoints = (
            ("app-a", "http://127.0.0.1:14283"),
            ("app-b", "http://127.0.0.1:14284"),
        )
        driver.api_key = "sk-ogw-synthetic"
        driver.candidate = candidate()
        driver._probe_sequence = 200_000
        app_a_result = WorkloadResult(
            (RequestSample(1, "app-a", 200, 1.0, True, False),),
            1.0,
        )
        app_b_result = WorkloadResult(
            (RequestSample(2, "app-b", 503, 1.0, False, False),),
            1.0,
        )
        with patch(
            "tools.ha_topology_evidence.lifecycle.run_workload",
            new=AsyncMock(side_effect=(app_a_result, app_b_result)),
        ):
            with self.assertRaises(EvidenceVerificationError):
                await driver._probe(expect_success=True)

    async def test_lifecycle_probe_addresses_each_replica_directly(self) -> None:
        from backend.tests.test_ha_topology_evidence_contract import candidate

        driver = object.__new__(LifecycleScenarioDriver)
        driver.endpoints = (
            ("app-a", "http://127.0.0.1:14283"),
            ("app-b", "http://127.0.0.1:14284"),
        )
        driver.api_key = "sk-ogw-synthetic"
        driver.candidate = candidate()
        driver._probe_sequence = 200_000
        calls = []

        async def workload(endpoints, **kwargs):
            calls.append((endpoints, kwargs))
            name, _url = endpoints[0]
            return WorkloadResult(
                (RequestSample(kwargs["sequence_offset"], name, 200, 1.0, True, False),),
                1.0,
            )

        with patch(
            "tools.ha_topology_evidence.lifecycle.run_workload",
            side_effect=workload,
        ):
            samples = await driver._probe(expect_success=True)

        self.assertEqual(
            [call[0] for call in calls], [(driver.endpoints[0],), (driver.endpoints[1],)]
        )
        self.assertTrue(all(call[1]["attempts"] == 1 for call in calls))
        self.assertEqual([sample["replica"] for sample in samples], ["app-a", "app-b"])

    async def test_dependency_recovery_requires_full_epoch_transition_before_reentry(self) -> None:
        from backend.tests.test_ha_topology_evidence_contract import candidate

        class Controller:
            def __init__(self):
                self.state_reads = 0

            def fault(self, action):
                return {"accepted": True, "action": action.value}

            def compose(self, action, services=()):
                return None

            def wait_http(self, url):
                return 200

            def fixture_state(self):
                self.state_reads += 1
                return {"milestones": {"redis:app-a:blocked": 0 if self.state_reads == 1 else 1}}

        class Oracle:
            async def snapshot(self):
                return snapshot()

            async def operation_evidence(self, samples, *, operation_key):
                del operation_key
                return tuple(
                    OperationOracleEvidence(
                        sample.operation_digest,
                        1,
                        int(sample.success),
                        int(sample.transport_failure),
                        int(sample.success),
                        int(sample.success),
                        int(sample.success),
                        int(sample.success),
                    )
                    for sample in samples
                )

        transitions: list[str] = []

        async def lifecycle_hook(scenario_id: str) -> dict[str, object]:
            transitions.append(scenario_id)
            now = time.monotonic_ns()
            return {
                "exercised": True,
                "safe": True,
                "reconciliation_started_ns": now,
                "reconciliation_completed_ns": now + 1,
                "mark_ready_ns": now + 2,
                "sustained_ready_ns": now + 3,
                "samples": (
                    RequestSample(200_000, "app-a", 200, 1.0, True, False).safe_dict(),
                    RequestSample(200_001, "app-b", 200, 1.0, True, False).safe_dict(),
                ),
            }

        runner = MatrixRunner(
            candidate(),
            Controller(),
            Oracle(),
            app_a_url="http://127.0.0.1:14283",
            app_b_url="http://127.0.0.1:14284",
            api_key="sk-ogw-synthetic",
            lifecycle_hook=lifecycle_hook,
        )
        failed = WorkloadResult(
            tuple(RequestSample(i, "app-a", 503, 1.0, False, False) for i in range(128)),
            1.0,
        )
        recovered = WorkloadResult(
            tuple(RequestSample(i + 128, "app-a", 200, 1.0, True, False) for i in range(128)),
            1.0,
        )
        runner._load = AsyncMock(side_effect=(failed, recovered))
        runner._wait_conservation = AsyncMock()

        await runner._fault_recovery(
            "redis-app-a-interruption",
            FaultAction.REDIS_APP_A_BLOCK,
            (("app-a", "http://127.0.0.1:14283"),),
        )

        self.assertEqual(transitions, ["recover-after-coordination-fault"])
        runner._wait_conservation.assert_awaited_once_with(snapshot(), 130)


class ReportTests(unittest.TestCase):
    def test_secret_scanner_rejects_credentials_and_connection_strings(self) -> None:
        scan_secret_free(b'{"state":"pass"}')
        for payload in (
            b"password=not-a-test-secret",
            b'{"password":"not-a-test-secret"}',
            b"{'api_key': 'not-a-test-secret'}",
            b"Authorization: Bearer-secret-value",
            b"postgresql://user:password@database/app",
            b"-----BEGIN PRIVATE KEY-----",
        ):
            with self.subTest(payload=payload):
                with self.assertRaises(EvidenceVerificationError):
                    scan_secret_free(payload)

    def test_report_writer_is_create_only_and_hashes_exact_bytes(self) -> None:
        with workspace_temp_directory() as directory:
            root = Path(directory) / "new-report"
            writer = EvidenceReportWriter(root.resolve())
            digest = writer.write_json("summary.json", {"state": "pass"})
            self.assertEqual(
                digest, hashlib.sha256((root / "summary.json").read_bytes()).hexdigest()
            )
            with self.assertRaises(FileExistsError):
                writer.write_json("summary.json", {"state": "different"})

        with workspace_temp_directory() as directory:
            writer = EvidenceReportWriter((Path(directory) / "bounded-report").resolve())
            with self.assertRaisesRegex(EvidenceVerificationError, "record limit"):
                writer.write_jsonl("events.jsonl", ({"n": value} for value in range(100_001)))


if __name__ == "__main__":
    unittest.main()
