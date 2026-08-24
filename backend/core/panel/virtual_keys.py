"""Panel API routes for managing virtual API keys."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.i18n import LocalizedJSONResponse as JSONResponse
from core.utils import verify_panel_token
from core.virtual_keys import (
    DEFAULT_INFERENCE_SCOPES,
    MAX_FALLBACK_PRICE_USD_PER_MILLION,
    MAX_MODEL_PATTERNS,
    normalize_model_patterns,
    normalize_unknown_pricing_policy,
    normalize_virtual_key_scopes,
    virtual_key_manager,
)
from fastapi import APIRouter, Depends
from log import log
from pydantic import BaseModel, Field, field_validator, model_validator

from .utils import INTERNAL_SERVER_ERROR_DETAIL

router = APIRouter(prefix="/api/virtual-keys", tags=["virtual-keys"])


class CreateVirtualKeyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    budget_daily_usd: Optional[float] = Field(default=None, ge=0)
    budget_monthly_usd: Optional[float] = Field(default=None, ge=0)
    rpm_limit: Optional[int] = Field(default=None, ge=1)
    tpm_limit: Optional[int] = Field(default=None, ge=1)
    expires_at: Optional[float] = Field(default=None, ge=0)
    allowed_models: List[str] = Field(default_factory=list, max_length=MAX_MODEL_PATTERNS)
    scopes: List[str] = Field(
        default_factory=lambda: list(DEFAULT_INFERENCE_SCOPES),
        min_length=1,
        max_length=5,
    )
    unknown_pricing_policy: str = "deny"
    fallback_price_usd_per_million: Optional[float] = Field(
        default=None,
        ge=0,
        le=MAX_FALLBACK_PRICE_USD_PER_MILLION,
    )

    @field_validator("scopes")
    @classmethod
    def validate_scopes(cls, value: List[str]) -> List[str]:
        return list(normalize_virtual_key_scopes(value))

    @field_validator("allowed_models")
    @classmethod
    def validate_allowed_models(cls, value: List[str]) -> List[str]:
        return normalize_model_patterns(value)

    @model_validator(mode="after")
    def validate_pricing_policy(self) -> "CreateVirtualKeyRequest":
        policy, fallback = normalize_unknown_pricing_policy(
            self.unknown_pricing_policy,
            self.fallback_price_usd_per_million,
        )
        self.unknown_pricing_policy = policy
        self.fallback_price_usd_per_million = fallback
        return self


class UpdateVirtualKeyRequest(BaseModel):
    name: Optional[str] = Field(default=None, max_length=128)
    enabled: Optional[bool] = None
    budget_daily_usd: Optional[float] = Field(default=None, ge=0)
    budget_monthly_usd: Optional[float] = Field(default=None, ge=0)
    rpm_limit: Optional[int] = Field(default=None, ge=0)
    tpm_limit: Optional[int] = Field(default=None, ge=0)
    expires_at: Optional[float] = Field(default=None, ge=0)
    allowed_models: Optional[List[str]] = Field(
        default=None, max_length=MAX_MODEL_PATTERNS
    )
    scopes: Optional[List[str]] = Field(default=None, min_length=1, max_length=5)
    unknown_pricing_policy: Optional[str] = None
    fallback_price_usd_per_million: Optional[float] = Field(
        default=None,
        ge=0,
        le=MAX_FALLBACK_PRICE_USD_PER_MILLION,
    )

    @field_validator("scopes")
    @classmethod
    def validate_scopes(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        return list(normalize_virtual_key_scopes(value))

    @field_validator("allowed_models")
    @classmethod
    def validate_allowed_models(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        return normalize_model_patterns(value)

    @model_validator(mode="after")
    def validate_pricing_policy(self) -> "UpdateVirtualKeyRequest":
        fields_set = self.model_fields_set
        if "unknown_pricing_policy" not in fields_set:
            return self
        policy, fallback = normalize_unknown_pricing_policy(
            self.unknown_pricing_policy,
            self.fallback_price_usd_per_million,
        )
        self.unknown_pricing_policy = policy
        self.fallback_price_usd_per_million = fallback
        return self


@router.get("")
async def list_virtual_keys(token: str = Depends(verify_panel_token)):
    try:
        keys = await virtual_key_manager.list_keys()
        return {"success": True, "data": keys}
    except Exception as exc:
        log.error(f"Failed to list virtual keys: {exc}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": INTERNAL_SERVER_ERROR_DETAIL},
        )


@router.post("")
async def create_virtual_key(
    payload: CreateVirtualKeyRequest, token: str = Depends(verify_panel_token)
):
    try:
        record, plaintext = await virtual_key_manager.create_key(
            payload.name,
            budget_daily_usd=payload.budget_daily_usd,
            budget_monthly_usd=payload.budget_monthly_usd,
            rpm_limit=payload.rpm_limit,
            tpm_limit=payload.tpm_limit,
            expires_at=payload.expires_at,
            allowed_models=payload.allowed_models,
            scopes=payload.scopes,
            unknown_pricing_policy=payload.unknown_pricing_policy,
            fallback_price_usd_per_million=payload.fallback_price_usd_per_million,
        )
        # The plaintext secret is returned exactly once at creation time.
        return {"success": True, "data": record, "key": plaintext}
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"success": False, "detail": str(exc)})
    except Exception as exc:
        log.error(f"Failed to create virtual key: {exc}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": INTERNAL_SERVER_ERROR_DETAIL},
        )


@router.patch("/{key_id}")
async def update_virtual_key(
    key_id: str,
    payload: UpdateVirtualKeyRequest,
    token: str = Depends(verify_panel_token),
):
    try:
        patch: Dict[str, Any] = payload.model_dump(exclude_unset=True)
        record = await virtual_key_manager.update_key(key_id, patch)
        if record is None:
            return JSONResponse(
                status_code=404,
                content={"success": False, "detail": "Virtual key not found."},
            )
        return {"success": True, "data": record}
    except ValueError as exc:
        return JSONResponse(status_code=400, content={"success": False, "detail": str(exc)})
    except Exception as exc:
        log.error(f"Failed to update virtual key {key_id}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": INTERNAL_SERVER_ERROR_DETAIL},
        )


@router.delete("/{key_id}")
async def delete_virtual_key(key_id: str, token: str = Depends(verify_panel_token)):
    try:
        deleted = await virtual_key_manager.delete_key(key_id)
        if not deleted:
            return JSONResponse(
                status_code=404,
                content={"success": False, "detail": "Virtual key not found."},
            )
        return {"success": True}
    except Exception as exc:
        log.error(f"Failed to delete virtual key {key_id}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": INTERNAL_SERVER_ERROR_DETAIL},
        )


@router.get("/{key_id}/usage")
async def get_virtual_key_usage(key_id: str, token: str = Depends(verify_panel_token)):
    try:
        keys = await virtual_key_manager.list_keys()
        if not any(record["id"] == key_id for record in keys):
            return JSONResponse(
                status_code=404,
                content={"success": False, "detail": "Virtual key not found."},
            )
        usage = await virtual_key_manager.get_key_usage(key_id)
        return {"success": True, "data": usage}
    except Exception as exc:
        log.error(f"Failed to fetch usage for virtual key {key_id}: {exc}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "detail": INTERNAL_SERVER_ERROR_DETAIL},
        )
