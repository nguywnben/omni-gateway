"""Provider-specific control-panel configuration and credential routes."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

import config
from core.credential_manager import credential_manager
from core.google_ai_studio import (
    GoogleAIStudioError,
    normalize_api_base_url,
    validate_api_key,
)
from core.models import ConfigSaveRequest, GoogleAIStudioCredentialRequest
from core.provider_registry import (
    GOOGLE_AI_STUDIO,
    api_key_fingerprint,
)
from core.storage_adapter import get_storage_adapter
from core.utils import verify_panel_token
from log import log

from .utils import get_env_locked_keys


router = APIRouter(tags=["provider-settings"])

ANTIGRAVITY_CONFIG_KEYS = {
    "antigravity_client_id",
    "antigravity_client_secret",
    "api_url",
    "oauth_url",
    "google_apis_url",
    "resource_manager_url",
    "service_usage_url",
    "antigravity_user_agent",
    "antigravity_payload_user_agent",
    "stream_to_nonstream",
    "switch_credential_enabled",
}

STRING_KEYS = {
    "antigravity_client_id",
    "antigravity_client_secret",
    "api_url",
    "oauth_url",
    "google_apis_url",
    "resource_manager_url",
    "service_usage_url",
    "antigravity_user_agent",
    "antigravity_payload_user_agent",
}

BOOLEAN_KEYS = {
    "stream_to_nonstream",
    "switch_credential_enabled",
}


async def _current_antigravity_config() -> dict:
    client_id, client_secret = await config.get_antigravity_oauth_client_config()
    return {
        "antigravity_client_id": client_id,
        "antigravity_client_secret": client_secret,
        "api_url": await config.get_antigravity_api_url(),
        "oauth_url": await config.get_oauth_proxy_url(),
        "google_apis_url": await config.get_googleapis_proxy_url(),
        "resource_manager_url": await config.get_resource_manager_api_url(),
        "service_usage_url": await config.get_service_usage_api_url(),
        "antigravity_user_agent": await config.get_antigravity_user_agent(),
        "antigravity_payload_user_agent": await config.get_antigravity_payload_user_agent(),
        "stream_to_nonstream": await config.get_antigravity_stream_to_nonstream(),
        "switch_credential_enabled": await config.get_antigravity_switch_credential_enabled(),
    }


@router.get("/api/providers/antigravity/config")
async def get_antigravity_config(token: str = Depends(verify_panel_token)):
    """Return Google Antigravity provider settings for the provider setup UI."""
    try:
        env_locked = get_env_locked_keys() & ANTIGRAVITY_CONFIG_KEYS
        return JSONResponse(
            content={
                "config": await _current_antigravity_config(),
                "env_locked": sorted(env_locked),
            }
        )
    except Exception as e:
        log.error(f"Failed to retrieve Google Antigravity configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/providers/antigravity/config")
async def save_antigravity_config(request: ConfigSaveRequest, token: str = Depends(verify_panel_token)):
    """Save Google Antigravity provider settings from the provider setup UI."""
    try:
        new_config = request.config or {}
        unknown_keys = sorted(set(new_config) - ANTIGRAVITY_CONFIG_KEYS)
        if unknown_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported Google Antigravity setting(s): {', '.join(unknown_keys)}.",
            )

        for key in STRING_KEYS & set(new_config):
            if not isinstance(new_config[key], str):
                raise HTTPException(status_code=400, detail=f"Google Antigravity setting '{key}' must be a string.")

        for key in BOOLEAN_KEYS & set(new_config):
            if not isinstance(new_config[key], bool):
                raise HTTPException(status_code=400, detail=f"Google Antigravity setting '{key}' must be a boolean.")

        env_locked = get_env_locked_keys() & ANTIGRAVITY_CONFIG_KEYS
        storage_adapter = await get_storage_adapter()

        saved_config = {}
        for key, value in new_config.items():
            if key in env_locked:
                continue
            await storage_adapter.set_config(key, value)
            saved_config[key] = value

        await config.reload_config()

        return JSONResponse(
            content={
                "message": "Google Antigravity settings saved.",
                "saved_config": saved_config,
                "env_locked": sorted(env_locked),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to save Google Antigravity configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/providers/antigravity/config/reset")
async def reset_antigravity_config(token: str = Depends(verify_panel_token)):
    """Reset Google Antigravity provider settings to built-in or environment defaults."""
    try:
        env_locked = get_env_locked_keys() & ANTIGRAVITY_CONFIG_KEYS
        storage_adapter = await get_storage_adapter()

        deleted_keys = []
        for key in sorted(ANTIGRAVITY_CONFIG_KEYS - env_locked):
            if await storage_adapter.delete_config(key):
                deleted_keys.append(key)

        await config.reload_config()

        return JSONResponse(
            content={
                "message": "Google Antigravity settings reset to defaults.",
                "config": await _current_antigravity_config(),
                "reset_config": deleted_keys,
                "env_locked": sorted(env_locked),
            }
        )
    except Exception as e:
        log.error(f"Failed to reset Google Antigravity configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


GOOGLE_AI_STUDIO_CONFIG_KEYS = {"google_ai_studio_api_url"}


async def _current_google_ai_studio_config() -> dict:
    return {"google_ai_studio_api_url": await config.get_google_ai_studio_api_url()}


@router.get("/api/providers/google-ai-studio/config")
async def get_google_ai_studio_config(token: str = Depends(verify_panel_token)):
    """Return Google AI Studio provider settings."""
    env_locked = get_env_locked_keys() & GOOGLE_AI_STUDIO_CONFIG_KEYS
    return JSONResponse(
        content={
            "config": await _current_google_ai_studio_config(),
            "env_locked": sorted(env_locked),
        }
    )


@router.post("/api/providers/google-ai-studio/config")
async def save_google_ai_studio_config(
    request: ConfigSaveRequest,
    token: str = Depends(verify_panel_token),
):
    """Save the Google AI Studio upstream endpoint."""
    new_config = request.config or {}
    unknown_keys = sorted(set(new_config) - GOOGLE_AI_STUDIO_CONFIG_KEYS)
    if unknown_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported Google AI Studio setting(s): {', '.join(unknown_keys)}.",
        )

    try:
        api_url = normalize_api_base_url(
            str(new_config.get("google_ai_studio_api_url") or "")
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    env_locked = get_env_locked_keys() & GOOGLE_AI_STUDIO_CONFIG_KEYS
    if "google_ai_studio_api_url" not in env_locked:
        storage_adapter = await get_storage_adapter()
        await storage_adapter.set_config("google_ai_studio_api_url", api_url)
        await config.reload_config()

    return JSONResponse(
        content={
            "message": "Google AI Studio settings saved.",
            "config": await _current_google_ai_studio_config(),
            "env_locked": sorted(env_locked),
        }
    )


@router.post("/api/providers/google-ai-studio/config/reset")
async def reset_google_ai_studio_config(token: str = Depends(verify_panel_token)):
    """Reset the Google AI Studio endpoint to its environment or built-in value."""
    env_locked = get_env_locked_keys() & GOOGLE_AI_STUDIO_CONFIG_KEYS
    if "google_ai_studio_api_url" not in env_locked:
        storage_adapter = await get_storage_adapter()
        await storage_adapter.delete_config("google_ai_studio_api_url")
        await config.reload_config()
    return JSONResponse(
        content={
            "message": "Google AI Studio settings reset to defaults.",
            "config": await _current_google_ai_studio_config(),
            "env_locked": sorted(env_locked),
        }
    )


@router.post("/api/providers/google-ai-studio/credentials")
async def add_google_ai_studio_credential(
    request: GoogleAIStudioCredentialRequest,
    token: str = Depends(verify_panel_token),
):
    """Validate and add one Google AI Studio API key to the provider pool."""
    api_key = request.api_key.strip()
    label = " ".join(str(request.label or "").split())[:80]

    try:
        validation = await validate_api_key(api_key)
    except GoogleAIStudioError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    fingerprint = api_key_fingerprint(api_key)
    credential_label = label or f"API key ending {api_key[-4:]}"
    credential_data = {
        "provider": GOOGLE_AI_STUDIO,
        "credential_type": "api_key",
        "api_key": api_key,
        "credential_label": credential_label,
        "key_fingerprint": fingerprint,
        "model_ids": validation.model_ids,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    filename = f"google-ai-studio-{fingerprint}.json"
    result = await credential_manager.add_primary_credential(filename, credential_data)

    action = result.get("action", "created")
    saved_filename = result.get("filename", filename)
    message = (
        "Google AI Studio API key revalidated and updated in the provider pool."
        if action == "updated"
        else "Google AI Studio API key added to the provider pool."
    )
    return JSONResponse(
        status_code=200 if action == "updated" else 201,
        content={
            "success": True,
            "credential_saved": True,
            "credential_action": action,
            "filename": saved_filename,
            "provider": GOOGLE_AI_STUDIO,
            "label": credential_label,
            "model_count": validation.model_count,
            "message": message,
        },
    )
