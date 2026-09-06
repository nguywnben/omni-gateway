"""Bounded direct-replica HTTP workload for external HA evidence."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import math
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Final, Iterable

from .contract import CorrectnessCounters, EvidenceVerificationError
from .scenarios import loopback_opener, require_loopback_http_url

MAX_ATTEMPTS: Final = 100_000


@dataclass(frozen=True, slots=True)
class RequestSample:
    sequence: int
    replica: str
    status_code: int
    duration_ms: float
    success: bool
    transport_failure: bool
    request_id: str = ""
    operation_digest: str = ""
    delivery_digest: str = ""

    def __post_init__(self) -> None:
        if type(self.sequence) is not int or self.sequence < 0:
            raise EvidenceVerificationError("Request sample sequence is invalid.")
        if self.replica not in {"app-a", "app-b"}:
            raise EvidenceVerificationError("Request sample replica is invalid.")
        if type(self.status_code) is not int or not 0 <= self.status_code <= 599:
            raise EvidenceVerificationError("Request sample status is invalid.")
        if not self.request_id and not self.operation_digest and not self.delivery_digest:
            fallback = hashlib.sha256(f"test:{self.sequence}".encode("ascii")).hexdigest()
            object.__setattr__(self, "request_id", "w4e-" + fallback[:32])
            object.__setattr__(self, "operation_digest", fallback)
            object.__setattr__(
                self,
                "delivery_digest",
                hashlib.sha256(f"delivery:{self.sequence}".encode("ascii")).hexdigest(),
            )
        if (
            type(self.duration_ms) not in (int, float)
            or not math.isfinite(self.duration_ms)
            or self.duration_ms < 0
            or type(self.success) is not bool
            or type(self.transport_failure) is not bool
            or (self.success and (self.status_code != 200 or self.transport_failure))
            or (self.transport_failure and self.status_code != 0)
        ):
            raise EvidenceVerificationError("Request sample result is invalid.")
        if (
            not isinstance(self.request_id, str)
            or not self.request_id.startswith("w4e-")
            or len(self.request_id) != 36
            or not isinstance(self.operation_digest, str)
            or len(self.operation_digest) != 64
            or any(character not in "0123456789abcdef" for character in self.operation_digest)
            or not isinstance(self.delivery_digest, str)
            or len(self.delivery_digest) != 64
            or any(character not in "0123456789abcdef" for character in self.delivery_digest)
        ):
            raise EvidenceVerificationError("Request sample operation identity is invalid.")

    def safe_dict(self, *, include_request_id: bool = False) -> dict[str, object]:
        value = asdict(self)
        if not include_request_id:
            value.pop("request_id")
        return value


@dataclass(frozen=True, slots=True)
class WorkloadResult:
    samples: tuple[RequestSample, ...]
    elapsed_ms: float

    @property
    def p95_ms(self) -> float:
        successful = sorted(sample.duration_ms for sample in self.samples if sample.success)
        if not successful:
            return 0.0
        return successful[max(0, math.ceil(len(successful) * 0.95) - 1)]

    @property
    def successful_throughput_rps(self) -> float:
        successes = sum(sample.success for sample in self.samples)
        return successes / max(self.elapsed_ms / 1000.0, 0.001)

    @property
    def counters(self) -> CorrectnessCounters:
        successes = sum(sample.success for sample in self.samples)
        failures = len(self.samples) - successes
        transport = sum(sample.transport_failure for sample in self.samples)
        return CorrectnessCounters(
            attempted=len(self.samples),
            admitted=successes,
            upstream_started=successes + transport,
            upstream_completed=successes,
            client_success=successes,
            client_unknown=transport,
            rejected=failures - transport,
            durable_committed=successes,
        )


def _send_request(
    sequence: int,
    request_sequence: int,
    operation_sequence: int,
    replica: str,
    base_url: str,
    api_key: str,
    deadline_seconds: float,
    operation_key: bytes,
) -> RequestSample:
    logical_operation = str(operation_sequence).encode("ascii")
    request_id = (
        "w4e-"
        + hmac.digest(
            operation_key,
            b"omni-ha-evidence-request-v1\x00" + logical_operation,
            hashlib.sha256,
        ).hex()[:32]
    )
    operation_digest = hmac.digest(
        operation_key,
        b"omni-ha-evidence-operation-v1\x00" + request_id.encode("ascii"),
        hashlib.sha256,
    ).hex()
    delivery_digest = hmac.digest(
        operation_key,
        b"omni-ha-evidence-delivery-v1\x00" + str(sequence).encode("ascii"),
        hashlib.sha256,
    ).hex()
    body = json.dumps(
        {
            "model": "omni-evidence-model",
            "messages": [
                {
                    "role": "user",
                    "content": f"synthetic-evidence-operation-{request_sequence:08d}",
                }
            ],
            "max_tokens": 4,
            "temperature": 0.0,
            "generationConfig": {"temperature": 0.0},
            "stream": False,
        },
        separators=(",", ":"),
    ).encode("ascii")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        method="POST",
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Omni-Evidence-Sequence": str(request_sequence),
            "X-Request-ID": request_id,
        },
    )
    started = time.perf_counter_ns()
    status = 0
    success = False
    transport_failure = False
    try:
        with loopback_opener().open(request, timeout=deadline_seconds) as response:
            status = response.status
            payload = response.read(1_048_577)
            success = status == 200 and len(payload) <= 1_048_576
    except urllib.error.HTTPError as exc:
        status = exc.code
        exc.read(1_048_577)
    except (OSError, TimeoutError, urllib.error.URLError):
        transport_failure = True
    elapsed = (time.perf_counter_ns() - started) / 1_000_000
    return RequestSample(
        sequence=sequence,
        replica=replica,
        status_code=status,
        duration_ms=elapsed,
        success=success,
        transport_failure=transport_failure,
        request_id=request_id,
        operation_digest=operation_digest,
        delivery_digest=delivery_digest,
    )


async def run_workload(
    endpoints: Iterable[tuple[str, str]],
    *,
    api_key: str,
    attempts: int,
    concurrency: int,
    offered_rps: int,
    request_deadline_ms: int,
    sequence_offset: int = 0,
    request_sequence_offset: int | None = None,
    operation_sequence_offset: int | None = None,
    schedule_seed: int = 0,
) -> WorkloadResult:
    selected = tuple(endpoints)
    if (
        not selected
        or any(name not in {"app-a", "app-b"} for name, _ in selected)
        or type(attempts) is not int
        or not 1 <= attempts <= MAX_ATTEMPTS
        or type(concurrency) is not int
        or not 1 <= concurrency <= 256
        or type(offered_rps) is not int
        or not 1 <= offered_rps <= 10_000
        or type(request_deadline_ms) is not int
        or not 100 <= request_deadline_ms <= 120_000
        or not isinstance(api_key, str)
        or not api_key.startswith("sk-ogw-")
        or type(schedule_seed) is not int
        or not 0 <= schedule_seed <= 2_147_483_647
        or (
            request_sequence_offset is not None
            and (type(request_sequence_offset) is not int or request_sequence_offset < 0)
        )
        or (
            operation_sequence_offset is not None
            and (type(operation_sequence_offset) is not int or operation_sequence_offset < 0)
        )
    ):
        raise EvidenceVerificationError("Evidence workload configuration is invalid.")
    for _, url in selected:
        require_loopback_http_url(url)
    operation_key = hashlib.sha256(api_key.encode("utf-8")).digest()
    semaphore = asyncio.Semaphore(concurrency)
    start = time.perf_counter_ns()

    async def one(index: int) -> RequestSample:
        due = start / 1_000_000_000 + index / offered_rps
        delay = due - time.perf_counter()
        if delay > 0:
            await asyncio.sleep(delay)
        schedule_slot = ((index * 1_103_515_245 + schedule_seed) >> 16) % len(selected)
        name, url = selected[schedule_slot]
        sample_sequence = sequence_offset + index
        request_sequence = (
            sample_sequence if request_sequence_offset is None else request_sequence_offset + index
        )
        operation_sequence = (
            sample_sequence
            if operation_sequence_offset is None
            else operation_sequence_offset + index
        )
        async with semaphore:
            return await asyncio.to_thread(
                _send_request,
                sample_sequence,
                request_sequence,
                operation_sequence,
                name,
                url,
                api_key,
                request_deadline_ms / 1000.0,
                operation_key,
            )

    samples = await asyncio.gather(*(one(index) for index in range(attempts)))
    elapsed = (time.perf_counter_ns() - start) / 1_000_000
    return WorkloadResult(tuple(samples), elapsed)
