"""Liveness and readiness probes for production runtimes."""

from __future__ import annotations

from core.storage_adapter import get_storage_adapter
from core.usage_ledger_service import get_usage_ledger_service
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from log import log

router = APIRouter(tags=["Health"])


@router.get("/health", include_in_schema=True)
async def health() -> JSONResponse:
    """Return process liveness without touching external dependencies."""
    return JSONResponse(content={"status": "ok"})


@router.get("/ready", include_in_schema=True)
async def ready() -> JSONResponse:
    """Return whether the configured storage backend is available."""
    try:
        storage = await get_storage_adapter()
        await storage.get_all_config()
    except Exception:
        log.warning("Readiness check failed because storage is unavailable.")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "storage": "unavailable",
                "usage_ledger": "unavailable",
            },
        )
    try:
        ledger = get_usage_ledger_service().health_snapshot()
        if not ledger["available"]:
            raise RuntimeError("Usage ledger is unavailable.")
    except Exception:
        log.warning("Readiness check failed because the usage ledger is unavailable.")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "storage": "available",
                "usage_ledger": "unavailable",
            },
        )
    return JSONResponse(
        content={"status": "ok", "storage": "available", "usage_ledger": "available"}
    )
