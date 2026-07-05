"""Internal implementation detail."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

import config
from log import log
from omni_gateway.keeplive import keepalive_service
from omni_gateway.models import ConfigSaveRequest
from omni_gateway.storage_adapter import get_storage_adapter
from omni_gateway.utils import verify_panel_token
from .utils import get_env_locked_keys



router = APIRouter(prefix="/ogw/config", tags=["config"])


@router.get("/get")
async def get_config(token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:



        current_config = {}


        current_config["ogw_code_assist_endpoint"] = await config.get_code_assist_endpoint()
        current_config["ogw_credentials_dir"] = await config.get_credentials_dir()
        current_config["ogw_proxy"] = await config.get_proxy_config() or ""


        current_config["ogw_oauth_url"] = await config.get_oauth_proxy_url()
        current_config["ogw_google_apis_url"] = await config.get_googleapis_proxy_url()
        current_config["ogw_resource_manager_url"] = await config.get_resource_manager_api_url()
        current_config["ogw_service_usage_url"] = await config.get_service_usage_api_url()
        current_config["ogw_api_url"] = await config.get_ogw_api_url()


        current_config["ogw_auto_disable_enabled"] = await config.get_auto_disable_enabled()
        current_config["ogw_auto_disable_error_codes"] = await config.get_auto_disable_error_codes()


        current_config["ogw_retry_429_max_retries"] = await config.get_retry_429_max_retries()
        current_config["ogw_retry_429_enabled"] = await config.get_retry_429_enabled()
        current_config["ogw_retry_429_interval"] = await config.get_retry_429_interval()

        current_config["ogw_anti_truncation_max_attempts"] = await config.get_anti_truncation_max_attempts()


        current_config["ogw_compatibility_mode_enabled"] = await config.get_compatibility_mode_enabled()


        current_config["ogw_return_thoughts_to_frontend"] = await config.get_return_thoughts_to_frontend()


        current_config["ogw_stream_to_nonstream"] = await config.get_ogw_stream_to_nonstream()
        current_config["ogw_switch_credential_enabled"] = await config.get_ogw_switch_credential_enabled()


        current_config["ogw_keepalive_url"] = await config.get_keepalive_url()
        current_config["ogw_keepalive_interval"] = await config.get_keepalive_interval()


        current_config["ogw_host"] = await config.get_server_host()
        current_config["ogw_port"] = await config.get_server_port()
        current_config["ogw_api_password"] = await config.get_api_password()
        current_config["ogw_panel_password"] = await config.get_panel_password()
        current_config["ogw_password"] = await config.get_server_password()


        storage_adapter = await get_storage_adapter()
        storage_config = await storage_adapter.get_all_config()


        env_locked_keys = get_env_locked_keys()


        for key, value in storage_config.items():
            if key.startswith("ogw_") and key not in env_locked_keys:
                current_config[key] = value

        return JSONResponse(content={"config": current_config, "env_locked": list(env_locked_keys)})

    except Exception as e:
        log.error(f"Failed to retrieve configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save")
async def save_config(request: ConfigSaveRequest, token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:

        new_config = request.config

        log.debug(f"Received configuration data: {list(new_config.keys())}")
        log.debug(f"Received gateway password value: {new_config.get('ogw_password', 'NOT_FOUND')}")

        invalid_keys = [key for key in new_config if not key.startswith("ogw_")]
        if invalid_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Configuration keys must start with ogw_: {', '.join(invalid_keys)}",
            )


        if "ogw_retry_429_max_retries" in new_config:
            if (
                not isinstance(new_config["ogw_retry_429_max_retries"], int)
                or new_config["ogw_retry_429_max_retries"] < 0
            ):
                raise HTTPException(status_code=400, detail="Maximum 429 retries must be an integer greater than or equal to 0")

        if "ogw_retry_429_enabled" in new_config:
            if not isinstance(new_config["ogw_retry_429_enabled"], bool):
                raise HTTPException(status_code=400, detail="429 Retry switch must be a boolean")


        if "ogw_retry_429_interval" in new_config:
            try:
                interval = float(new_config["ogw_retry_429_interval"])
                if interval < 0.01 or interval > 10:
                    raise HTTPException(status_code=400, detail="429 Retry interval must be between 0.01 -10 seconds")
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="429 Retry interval must be a valid number")

        if "ogw_anti_truncation_max_attempts" in new_config:
            if (
                not isinstance(new_config["ogw_anti_truncation_max_attempts"], int)
                or new_config["ogw_anti_truncation_max_attempts"] < 1
                or new_config["ogw_anti_truncation_max_attempts"] > 10
            ):
                raise HTTPException(
                    status_code=400, detail="Anti-truncation max retries must be an integer between 1 and 10"
                )

        if "ogw_compatibility_mode_enabled" in new_config:
            if not isinstance(new_config["ogw_compatibility_mode_enabled"], bool):
                raise HTTPException(status_code=400, detail="Compatibility mode switch must be a boolean")

        if "ogw_return_thoughts_to_frontend" in new_config:
            if not isinstance(new_config["ogw_return_thoughts_to_frontend"], bool):
                raise HTTPException(status_code=400, detail="Chain-of-thought return switch must be a boolean")

        if "ogw_stream_to_nonstream" in new_config:
            if not isinstance(new_config["ogw_stream_to_nonstream"], bool):
                raise HTTPException(status_code=400, detail="Omni flow to non flow switch must be a boolean")

        if "ogw_switch_credential_enabled" in new_config:
            if not isinstance(new_config["ogw_switch_credential_enabled"], bool):
                raise HTTPException(status_code=400, detail="Omni toggle voucher switch must be a boolean")


        if "ogw_keepalive_url" in new_config:
            if not isinstance(new_config["ogw_keepalive_url"], str):
                raise HTTPException(status_code=400, detail="Keep-alive URL must be a string")

        if "ogw_keepalive_interval" in new_config:
            try:
                interval = int(new_config["ogw_keepalive_interval"])
                if interval < 5 or interval > 86400:
                    raise HTTPException(status_code=400, detail="Keep-alive interval must be between 5 and 86400 seconds")
                new_config["ogw_keepalive_interval"] = interval
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="Keep-alive interval must be a valid integer")

        if "ogw_host" in new_config:
            if not isinstance(new_config["ogw_host"], str) or not new_config["ogw_host"].strip():
                raise HTTPException(status_code=400, detail="Server host address cannot be empty")

        if "ogw_port" in new_config:
            if (
                not isinstance(new_config["ogw_port"], int)
                or new_config["ogw_port"] < 1
                or new_config["ogw_port"] > 65535
            ):
                raise HTTPException(status_code=400, detail="Port number must be an integer between 1 and 65535")

        if "ogw_api_password" in new_config:
            if not isinstance(new_config["ogw_api_password"], str):
                raise HTTPException(status_code=400, detail="API access password must be a string")

        if "ogw_panel_password" in new_config:
            if not isinstance(new_config["ogw_panel_password"], str):
                raise HTTPException(status_code=400, detail="Control panel password must be a string")

        if "ogw_password" in new_config:
            if not isinstance(new_config["ogw_password"], str):
                raise HTTPException(status_code=400, detail="Access password must be a string")


        env_locked_keys = get_env_locked_keys()


        storage_adapter = await get_storage_adapter()
        for key, value in new_config.items():
            if key not in env_locked_keys:
                await storage_adapter.set_config(key, value)
                if key in ("ogw_password", "ogw_api_password", "ogw_panel_password"):
                    log.debug(f"Setting field {key} to: {value}")


        await config.reload_config()


        keepalive_keys = {"ogw_keepalive_url", "ogw_keepalive_interval"}
        if keepalive_keys & set(new_config.keys()):
            try:
                await keepalive_service.restart()
            except Exception as e:
                log.warning(f"Failed to restart keep-alive service: {e}")


        test_api_password = await config.get_api_password()
        test_panel_password = await config.get_panel_password()
        test_password = await config.get_server_password()
        log.debug(f"API password read immediately after saving: {test_api_password}")
        log.debug(f"Panel password read immediately after saving: {test_panel_password}")
        log.debug(f"General password read immediately after saving: {test_password}")

        # Build response message
        response_data = {
            "message": "Configuration saved successfully",
            "saved_config": {k: v for k, v in new_config.items() if k not in env_locked_keys},
        }

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to save configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))
