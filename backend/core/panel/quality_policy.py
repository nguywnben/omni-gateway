"""Authenticated management API for the versioned AI quality policy."""

from __future__ import annotations

import asyncio
from typing import Any, Literal

import config
from core.i18n import LocalizedJSONResponse as JSONResponse
from core.quality_policy import (
    LOCKED_SETTING_PATHS,
    POLICY_STORAGE_KEY,
    QualityPolicyError,
    build_policy_document,
    changed_locked_fields,
    load_policy_document,
    preview_policy,
    settings_from_legacy,
)
from core.storage_adapter import get_storage_adapter
from core.utils import verify_panel_token
from fastapi import APIRouter, Depends
from log import log
from pydantic import BaseModel, Field

from .utils import get_env_locked_keys

router = APIRouter(prefix="/api/quality-policy", tags=["quality-policy"])
_policy_update_lock = asyncio.Lock()


class QualityPolicyUpdateRequest(BaseModel):
    revision: int = Field(ge=0)
    profile: Literal["quality", "balanced", "capacity", "custom"]
    settings: dict[str, Any] | None = None

    class Config:
        extra = "forbid"


class QualityPolicyPreviewRequest(QualityPolicyUpdateRequest):
    estimated_input_tokens: int = Field(ge=0, le=2_000_000)
    message_count: int = Field(ge=0, le=100_000)
    tool_count: int = Field(ge=0, le=10_000)
    has_system_instruction: bool
    has_tool_pairs: bool


def _error(status_code: int, code: str, message: str, **details) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, **details}},
    )


def _unavailable(operation: str, exc: Exception) -> JSONResponse:
    log.error(
        f"Quality policy {operation} failed ({type(exc).__name__}); "
        "the exception detail was withheld from the API response."
    )
    return _error(
        503,
        "quality_policy_unavailable",
        "The quality policy service is temporarily unavailable.",
    )


async def read_legacy_quality_settings() -> dict[str, Any]:
    compression = await config.get_token_compression_config()
    guardrails = await config.get_guardrails_config()
    response_cache = await config.get_response_cache_config()
    return {
        "compatibility_mode_enabled": await config.get_compatibility_mode_enabled(),
        "return_thoughts_to_frontend": await config.get_return_thoughts_to_frontend(),
        "anti_truncation_max_attempts": await config.get_anti_truncation_max_attempts(),
        "token_compression_enabled": compression["enabled"],
        "token_compression_threshold": compression["threshold_tokens"],
        "token_compression_target": compression["target_tokens"],
        "token_compression_min_recent_turns": compression["min_recent_turns"],
        "guardrails_enabled": guardrails["enabled"],
        "guardrails_pii_masking_enabled": guardrails["pii_masking_enabled"],
        "guardrails_injection_detection_enabled": guardrails["injection_detection_enabled"],
        "guardrails_blocked_keywords": guardrails["blocked_keywords"],
        "response_cache_enabled": response_cache["enabled"],
        "response_cache_ttl_seconds": response_cache["ttl_seconds"],
        "response_cache_max_entries": response_cache["max_entries"],
    }


async def _load_current_policy(storage, legacy: dict[str, Any]) -> dict[str, Any]:
    stored = await storage.get_config(POLICY_STORAGE_KEY, None)
    return load_policy_document(stored, legacy)


def _policy_response(policy: dict[str, Any], env_locked: set[str]) -> dict[str, Any]:
    return {
        "policy": policy,
        "env_locked": sorted(env_locked & set(LOCKED_SETTING_PATHS)),
        "runtime_active": False,
        "runtime_source": "legacy_compatibility_bridge",
    }


@router.get("")
async def get_quality_policy(token: str = Depends(verify_panel_token)):
    del token
    try:
        storage = await get_storage_adapter()
        legacy = await read_legacy_quality_settings()
        policy = await _load_current_policy(storage, legacy)
        return JSONResponse(content=_policy_response(policy, get_env_locked_keys()))
    except QualityPolicyError as exc:
        return _error(500, exc.code, str(exc))
    except Exception as exc:
        return _unavailable("read", exc)


@router.put("")
async def update_quality_policy(
    request: QualityPolicyUpdateRequest,
    token: str = Depends(verify_panel_token),
):
    del token
    try:
        desired = build_policy_document(
            profile=request.profile,
            revision=request.revision + 1,
            settings=request.settings,
        )
    except QualityPolicyError as exc:
        return _error(400, exc.code, str(exc))

    try:
        async with _policy_update_lock:
            storage = await get_storage_adapter()
            legacy = await read_legacy_quality_settings()
            current = await _load_current_policy(storage, legacy)

            if request.revision != current["revision"]:
                return _error(
                    409,
                    "quality_policy_revision_conflict",
                    "The quality policy changed after it was loaded.",
                    current_revision=current["revision"],
                )

            locked = changed_locked_fields(
                settings_from_legacy(legacy),
                desired["settings"],
                get_env_locked_keys(),
            )
            if locked:
                return _error(
                    423,
                    "quality_policy_environment_locked",
                    "The requested profile changes settings managed by the runtime environment.",
                    fields=locked,
                )

            if not await storage.set_config(POLICY_STORAGE_KEY, desired):
                return _error(
                    500, "quality_policy_write_failed", "The quality policy was not saved."
                )
    except QualityPolicyError as exc:
        return _error(500, exc.code, str(exc))
    except Exception as exc:
        return _unavailable("update", exc)

    return JSONResponse(content=_policy_response(desired, get_env_locked_keys()))


@router.post("/preview")
async def preview_quality_policy(
    request: QualityPolicyPreviewRequest,
    token: str = Depends(verify_panel_token),
):
    del token
    try:
        storage = await get_storage_adapter()
        legacy = await read_legacy_quality_settings()
        current = await _load_current_policy(storage, legacy)
        if request.revision != current["revision"]:
            return _error(
                409,
                "quality_policy_revision_conflict",
                "The quality policy changed after it was loaded.",
                current_revision=current["revision"],
            )
        proposed = build_policy_document(
            profile=request.profile,
            revision=request.revision,
            settings=request.settings,
            source="preview",
        )
        preview = preview_policy(
            proposed,
            {
                "estimated_input_tokens": request.estimated_input_tokens,
                "message_count": request.message_count,
                "tool_count": request.tool_count,
                "has_system_instruction": request.has_system_instruction,
                "has_tool_pairs": request.has_tool_pairs,
            },
        )
        env_locked = get_env_locked_keys()
        conflicts = changed_locked_fields(
            settings_from_legacy(legacy),
            proposed["settings"],
            env_locked,
        )
    except QualityPolicyError as exc:
        return _error(400, exc.code, str(exc))
    except Exception as exc:
        return _unavailable("preview", exc)

    return JSONResponse(
        content={
            "preview": preview,
            "can_apply": not conflicts,
            "environment_conflicts": conflicts,
            "env_locked": sorted(env_locked & set(LOCKED_SETTING_PATHS)),
        }
    )
