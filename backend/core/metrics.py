"""Prometheus text-format metrics endpoint (no external dependencies).

Exposes gateway-level counters derived from the durable usage ledger plus
in-process cache statistics. Protect the endpoint by setting ``METRICS_TOKEN``
(then scrape with ``Authorization: Bearer <token>``); leave it unset for
unauthenticated scraping inside trusted networks.
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Dict, List, Optional

from core.credential_operation_evidence import render_credential_operation_metrics
from core.response_cache import response_cache
from core.usage_stats import get_provider_metrics
from fastapi import APIRouter, Header, Response, status

router = APIRouter(tags=["Metrics"])

_PROCESS_STARTED_AT = time.time()


def _escape_label_value(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def render_prometheus_metrics(provider_rows: List[Dict]) -> str:
    """Render gateway metrics in the Prometheus text exposition format."""
    lines: List[str] = []

    def emit(name: str, metric_type: str, help_text: str) -> None:
        lines.append(f"# HELP {name} {help_text}")
        lines.append(f"# TYPE {name} {metric_type}")

    emit("omni_uptime_seconds", "gauge", "Seconds since the gateway process started.")
    lines.append(f"omni_uptime_seconds {max(0.0, time.time() - _PROCESS_STARTED_AT):.0f}")

    emit(
        "omni_requests_total",
        "counter",
        "Total upstream requests recorded in the usage ledger.",
    )
    emit_success = []
    emit_failed = []
    emit_tokens = []
    emit_cost = []
    emit_latency = []
    for row in provider_rows:
        provider = _escape_label_value(str(row.get("provider") or "unknown"))
        label = f'{{provider="{provider}"}}'
        lines.append(f"omni_requests_total{label} {int(row.get('calls') or 0)}")
        emit_success.append(
            f"omni_requests_success_total{label} {int(row.get('successful_calls') or 0)}"
        )
        emit_failed.append(f"omni_requests_failed_total{label} {int(row.get('failed_calls') or 0)}")
        emit_tokens.append(f"omni_tokens_total{label} {int(row.get('total_tokens') or 0)}")
        emit_cost.append(f"omni_cost_usd_total{label} {float(row.get('cost_usd') or 0.0):.6f}")
        emit_latency.append(
            f"omni_latency_milliseconds_total{label} {int(row.get('total_latency_ms') or 0)}"
        )

    emit(
        "omni_requests_success_total",
        "counter",
        "Successful upstream requests per provider.",
    )
    lines.extend(emit_success)
    emit("omni_requests_failed_total", "counter", "Failed upstream requests per provider.")
    lines.extend(emit_failed)
    emit("omni_tokens_total", "counter", "Total tokens processed per provider.")
    lines.extend(emit_tokens)
    emit(
        "omni_cost_usd_total",
        "counter",
        "Estimated USD spend per provider from the pricing table.",
    )
    lines.extend(emit_cost)
    emit(
        "omni_latency_milliseconds_total",
        "counter",
        "Cumulative successful-request latency per provider; divide by "
        "omni_requests_success_total for the average.",
    )
    lines.extend(emit_latency)

    emit(
        "omni_response_cache_hits_total",
        "counter",
        "Exact-match response cache hits since process start.",
    )
    lines.append(f"omni_response_cache_hits_total {int(response_cache.hits)}")
    emit(
        "omni_response_cache_misses_total",
        "counter",
        "Exact-match response cache misses since process start.",
    )
    lines.append(f"omni_response_cache_misses_total {int(response_cache.misses)}")
    emit(
        "omni_response_cache_entries",
        "gauge",
        "Unexpired entries currently held by the response cache.",
    )
    lines.append(f"omni_response_cache_entries {int(response_cache.size())}")

    lines.extend(render_credential_operation_metrics().rstrip().splitlines())

    return "\n".join(lines) + "\n"


@router.get("/metrics", include_in_schema=True)
async def metrics(authorization: Optional[str] = Header(None)) -> Response:
    expected_token = os.getenv("METRICS_TOKEN", "").strip()
    if expected_token:
        provided = ""
        if authorization and authorization.startswith("Bearer "):
            provided = authorization[7:]
        if provided != expected_token:
            return Response(
                content="unauthorized\n",
                status_code=status.HTTP_401_UNAUTHORIZED,
                media_type="text/plain",
            )

    provider_rows = await asyncio.to_thread(get_provider_metrics)
    return Response(
        content=render_prometheus_metrics(provider_rows),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
