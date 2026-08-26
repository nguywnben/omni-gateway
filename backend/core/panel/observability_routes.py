"""Authenticated operational health and telemetry-control status API."""

from __future__ import annotations

from core.i18n import LocalizedJSONResponse as JSONResponse
from core.operational_health import get_operational_health_snapshot
from core.request_trace_service import get_request_trace_service
from core.telemetry_policy import TelemetryConfigurationError, get_telemetry_policy
from core.utils import verify_panel_token
from fastapi import APIRouter, Depends, Query
from log import log

router = APIRouter(prefix="/api/observability", tags=["observability"])


@router.get("/health")
async def get_operational_health(
    window_seconds: int = Query(default=900, ge=300, le=86_400),
    token: str = Depends(verify_panel_token),
):
    del token
    try:
        snapshot = await get_operational_health_snapshot(
            get_request_trace_service(), window_seconds=window_seconds
        )
        snapshot["telemetry"] = get_telemetry_policy().public_status()
        return JSONResponse(content=snapshot)
    except TelemetryConfigurationError:
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "telemetry_configuration_invalid",
                    "message": "External telemetry configuration is invalid.",
                }
            },
        )
    except Exception as exc:
        log.error(f"Operational health snapshot failed ({type(exc).__name__}).")
        return JSONResponse(
            status_code=503,
            content={
                "error": {
                    "code": "operational_health_unavailable",
                    "message": "Operational health is temporarily unavailable.",
                }
            },
        )
