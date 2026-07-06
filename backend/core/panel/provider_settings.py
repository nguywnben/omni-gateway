"""Provider-specific control-panel configuration routes."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

import config
from core.models import ConfigSaveRequest
from core.storage_adapter import get_storage_adapter
from core.utils import verify_panel_token
from log import log

from .utils import get_env_locked_keys


router = APIRouter(prefix="/api/providers/antigravity", tags=["provider-settings"])

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


@router.get("/config")
async def get_antigravity_config(token: str = Depends(verify_panel_token)):
    """Return Antigravity provider settings for the provider setup UI."""
    try:
        env_locked = get_env_locked_keys() & ANTIGRAVITY_CONFIG_KEYS
        return JSONResponse(
            content={
                "config": await _current_antigravity_config(),
                "env_locked": sorted(env_locked),
            }
        )
    except Exception as e:
        log.error(f"Failed to retrieve Antigravity configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config")
async def save_antigravity_config(request: ConfigSaveRequest, token: str = Depends(verify_panel_token)):
    """Save Antigravity provider settings from the provider setup UI."""
    try:
        new_config = request.config or {}
        unknown_keys = sorted(set(new_config) - ANTIGRAVITY_CONFIG_KEYS)
        if unknown_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported Antigravity configuration key(s): {', '.join(unknown_keys)}",
            )

        for key in STRING_KEYS & set(new_config):
            if not isinstance(new_config[key], str):
                raise HTTPException(status_code=400, detail=f"{key} must be a string.")

        for key in BOOLEAN_KEYS & set(new_config):
            if not isinstance(new_config[key], bool):
                raise HTTPException(status_code=400, detail=f"{key} must be a boolean.")

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
                "message": "Antigravity settings saved successfully.",
                "saved_config": saved_config,
                "env_locked": sorted(env_locked),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to save Antigravity configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))
