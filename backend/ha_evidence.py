"""Reproducible synthetic HA semantics/load evidence; never an activation record."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.coordination import CoordinationUnavailableError  # noqa: E402
from core.coordination_service import CoordinationService  # noqa: E402
from core.primary_session_coordination import PrimarySessionCoordinator  # noqa: E402
from core.state_store import InMemoryStateStore  # noqa: E402


def _percentile(samples: list[float], fraction: float) -> float:
    ordered = sorted(samples)
    index = max(0, min(len(ordered) - 1, int((len(ordered) * fraction) + 0.999999) - 1))
    return round(ordered[index], 6)


async def _measure(operations: int, clients: int) -> dict[str, object]:
    store = InMemoryStateStore()
    service = CoordinationService(store)
    coordinators = [
        PrimarySessionCoordinator(service, identifier_key=b"e" * 32, fencing_epoch=1)
        for _ in range(clients)
    ]
    latencies: list[float] = []

    async def invoke(index: int) -> None:
        started = time.perf_counter_ns()
        await coordinators[index % clients].next_state(f"evidence:{index}", "synthetic")
        latencies.append((time.perf_counter_ns() - started) / 1_000_000)

    started = time.perf_counter()
    if clients == 1:
        for index in range(operations):
            await invoke(index)
    else:
        await asyncio.gather(*(invoke(index) for index in range(operations)))
    elapsed = max(time.perf_counter() - started, 0.000001)
    await service.close()
    return {
        "operations": operations,
        "logical_clients": clients,
        "p50_ms": _percentile(latencies, 0.50),
        "p95_ms": _percentile(latencies, 0.95),
        "p99_ms": _percentile(latencies, 0.99),
        "throughput_per_second": round(operations / elapsed, 3),
    }


class _FaultStore:
    def __init__(self, store: InMemoryStateStore) -> None:
        self.store = store
        self.available = True

    def __getattr__(self, name: str) -> Any:
        return getattr(self.store, name)

    def _require_available(self) -> None:
        if not self.available:
            raise CoordinationUnavailableError("Synthetic coordination interruption.")

    async def read_cas(self, key: str, *, epoch: int):
        self._require_available()
        return await self.store.read_cas(key, epoch=epoch)

    async def read_coordination_time(self, *, epoch: int):
        self._require_available()
        return await self.store.read_coordination_time(epoch=epoch)

    async def compare_and_set(self, request):
        self._require_available()
        return await self.store.compare_and_set(request)


async def _correctness_matrix() -> dict[str, object]:
    shared = InMemoryStateStore()
    service = CoordinationService(shared)
    replicas = [
        PrimarySessionCoordinator(service, identifier_key=b"m" * 32, fencing_epoch=1)
        for _ in range(2)
    ]
    states = await asyncio.gather(
        *(replicas[index % 2].next_state("matrix:shared", "synthetic") for index in range(12))
    )
    steps = [state.step_index for state in states]
    duplicate_state_transitions = len(steps) - len(set(steps))

    await shared.advance_epoch(1, "evidence-advance-epoch-0001")
    stale_epoch_denied = False
    try:
        await replicas[0].next_state("matrix:stale", "synthetic")
    except CoordinationUnavailableError:
        stale_epoch_denied = True

    await shared.mark_epoch_ready(2, "evidence-mark-ready-0001")
    epoch_two = PrimarySessionCoordinator(service, identifier_key=b"m" * 32, fencing_epoch=2)
    recovery_after_reconciliation = (
        await epoch_two.next_state("matrix:recovered", "synthetic")
    ).step_index == 1
    await service.close()

    fault = _FaultStore(InMemoryStateStore())
    fault_service = CoordinationService(fault)
    fault_coordinator = PrimarySessionCoordinator(
        fault_service, identifier_key=b"f" * 32, fencing_epoch=1
    )
    fault.available = False
    dependency_failure_closed = False
    try:
        await fault_coordinator.next_state("matrix:dependency", "synthetic")
    except CoordinationUnavailableError:
        dependency_failure_closed = True
    fault.available = True
    await fault_service.close()

    return {
        "duplicate_state_transitions": duplicate_state_transitions,
        "stale_epoch_denied": stale_epoch_denied,
        "dependency_failure_closed": dependency_failure_closed,
        "recovery_after_reconciliation": recovery_after_reconciliation,
    }


async def run_synthetic_evidence(*, operations: int = 256) -> dict[str, object]:
    if type(operations) is not int or not 16 <= operations <= 2_000:
        raise ValueError("Synthetic operation count must be between 16 and 2000.")
    baseline, target, correctness = await asyncio.gather(
        _measure(operations, 1),
        _measure(operations, 2),
        _correctness_matrix(),
    )
    return {
        "schema_version": 1,
        "scope": "synthetic_in_process",
        "not_activation_evidence": True,
        "activation_eligible": False,
        "activation_blockers": [
            "required external Redis/shared-database/two-replica "
            "failure/load/rollback topology was not exercised",
        ],
        "load": {
            "one_logical_client": baseline,
            "two_logical_clients": target,
        },
        "correctness": correctness,
        "unmeasured": [
            "live Redis failover and restart",
            "external durable database outage and recovery",
            "two application replicas and container loss",
            "network partition and production latency",
            "durable audit and usage commit completeness under failure",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operations", type=int, default=256)
    arguments = parser.parse_args()
    print(
        json.dumps(
            asyncio.run(run_synthetic_evidence(operations=arguments.operations)), sort_keys=True
        )
    )


if __name__ == "__main__":
    main()
