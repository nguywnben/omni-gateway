"""Internal implementation detail."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

import config
from log import configure_logging, log
from core.auth import verify_password
from core.keeplive import keepalive_service
from core.models import AccessCredentialsUpdateRequest, ConfigSaveRequest
from core.passwords import hash_password
from core.storage_adapter import get_storage_adapter
from core.utils import create_panel_session_token, verify_panel_token
from .utils import get_env_locked_keys



router = APIRouter(prefix="/api/config", tags=["config"])

ACCESS_SECRET_KEYS = {"api_password", "panel_password", "password"}
RESTART_REQUIRED_CONFIG_KEYS = {"host", "port", "credentials_dir"}
PROVIDER_SPECIFIC_CONFIG_KEYS = {
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
    "google_ai_studio_api_url",
}
ALLOWED_CONFIG_KEYS = (
    set(config.ENV_MAPPINGS.values())
    - ACCESS_SECRET_KEYS
    - PROVIDER_SPECIFIC_CONFIG_KEYS
)
DEFAULT_BACKED_CONFIG_KEYS = {
    "code_assist_client_id",
    "code_assist_client_secret",
}
RESETTABLE_CONFIG_KEYS = {
    "host",
    "port",
    "credentials_dir",
    "proxy",
    "code_assist_endpoint",
    "code_assist_client_id",
    "code_assist_client_secret",
    "auto_disable_enabled",
    "auto_disable_error_codes",
    "retry_429_enabled",
    "retry_429_max_retries",
    "retry_429_interval",
    "compatibility_mode_enabled",
    "return_thoughts_to_frontend",
    "anti_truncation_max_attempts",
    "token_compression_enabled",
    "token_compression_threshold",
    "token_compression_target",
    "token_compression_min_recent_turns",
    "routing_strategy",
    "preferred_provider",
    "upstream_timeout_seconds",
    "log_level",
    "log_max_mb",
    "log_backup_count",
    "keepalive_url",
    "keepalive_interval",
}
PRESERVED_RESET_KEYS = {
    "api_key",
    "api_password",
    "panel_password",
    "password",
}


def _redact_access_secrets(current_config: dict) -> dict:
    """Return control-panel configuration without reusable access secrets."""
    public_config = dict(current_config)
    legacy_password = bool(public_config.get("password"))
    public_config["panel_password_configured"] = bool(
        public_config.get("panel_password") or legacy_password
    )
    for key in ACCESS_SECRET_KEYS:
        public_config.pop(key, None)
    return public_config


def _classify_config_updates(keys) -> dict:
    """Separate immediately applied settings from process startup settings."""
    normalized = set(keys)
    return {
        "hot_updated": sorted(normalized - RESTART_REQUIRED_CONFIG_KEYS),
        "restart_required": sorted(normalized & RESTART_REQUIRED_CONFIG_KEYS),
    }


@router.get("/get")
async def get_config(token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:



        current_config = {}


        current_config["code_assist_endpoint"] = await config.get_code_assist_endpoint()
        current_config["credentials_dir"] = await config.get_credentials_dir()
        current_config["proxy"] = await config.get_proxy_config() or ""


        code_assist_client_id, code_assist_client_secret = await config.get_code_assist_oauth_client_config()
        current_config["code_assist_client_id"] = code_assist_client_id
        current_config["code_assist_client_secret"] = code_assist_client_secret


        current_config["auto_disable_enabled"] = await config.get_auto_disable_enabled()
        current_config["auto_disable_error_codes"] = await config.get_auto_disable_error_codes()


        current_config["retry_429_max_retries"] = await config.get_retry_429_max_retries()
        current_config["retry_429_enabled"] = await config.get_retry_429_enabled()
        current_config["retry_429_interval"] = await config.get_retry_429_interval()

        current_config["anti_truncation_max_attempts"] = await config.get_anti_truncation_max_attempts()

        compression_config = await config.get_token_compression_config()
        current_config["token_compression_enabled"] = compression_config["enabled"]
        current_config["token_compression_threshold"] = compression_config["threshold_tokens"]
        current_config["token_compression_target"] = compression_config["target_tokens"]
        current_config["token_compression_min_recent_turns"] = compression_config["min_recent_turns"]

        routing_policy = await config.get_routing_policy()
        current_config["routing_strategy"] = routing_policy["strategy"]
        current_config["preferred_provider"] = routing_policy["preferred_provider"]
        current_config["upstream_timeout_seconds"] = await config.get_upstream_timeout_seconds()

        log_config = await config.get_log_config()
        current_config["log_level"] = log_config["level"]
        current_config["log_max_mb"] = log_config["max_mb"]
        current_config["log_backup_count"] = log_config["backup_count"]


        current_config["compatibility_mode_enabled"] = await config.get_compatibility_mode_enabled()


        current_config["return_thoughts_to_frontend"] = await config.get_return_thoughts_to_frontend()


        current_config["keepalive_url"] = await config.get_keepalive_url()
        current_config["keepalive_interval"] = await config.get_keepalive_interval()


        current_config["host"] = await config.get_server_host()
        current_config["port"] = await config.get_server_port()
        current_config["panel_password"] = await config.get_panel_password()
        current_config["password"] = await config.get_server_password()


        storage_adapter = await get_storage_adapter()
        storage_config = await storage_adapter.get_all_config()


        env_locked_keys = get_env_locked_keys()


        for key, value in storage_config.items():
            if key in DEFAULT_BACKED_CONFIG_KEYS and (value is None or (isinstance(value, str) and not value.strip())):
                continue
            if key in ALLOWED_CONFIG_KEYS and key not in env_locked_keys:
                current_config[key] = value

        return JSONResponse(
            content={
                "config": _redact_access_secrets(current_config),
                "env_locked": list(env_locked_keys),
            }
        )

    except Exception as e:
        log.error(f"Failed to retrieve configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save")
async def save_config(request: ConfigSaveRequest, token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:

        new_config = request.config

        log.debug(f"Received configuration data: {list(new_config.keys())}")

        if ACCESS_SECRET_KEYS & set(new_config):
            raise HTTPException(
                status_code=400,
                detail="Access passwords must be updated through the dedicated access endpoint.",
            )

        unknown_keys = sorted(set(new_config) - ALLOWED_CONFIG_KEYS)
        if unknown_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported configuration key(s): {', '.join(unknown_keys)}",
            )


        if "retry_429_max_retries" in new_config:
            if (
                not isinstance(new_config["retry_429_max_retries"], int)
                or new_config["retry_429_max_retries"] < 0
            ):
                raise HTTPException(status_code=400, detail="Maximum 429 retries must be an integer greater than or equal to 0.")

        if "retry_429_enabled" in new_config:
            if not isinstance(new_config["retry_429_enabled"], bool):
                raise HTTPException(status_code=400, detail="The 429 retry switch must be a boolean.")


        if "retry_429_interval" in new_config:
            try:
                interval = float(new_config["retry_429_interval"])
                if interval < 0.01 or interval > 10:
                    raise HTTPException(status_code=400, detail="The 429 retry interval must be between 0.01 and 10 seconds.")
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="The 429 retry interval must be a valid number.")

        if "anti_truncation_max_attempts" in new_config:
            if (
                not isinstance(new_config["anti_truncation_max_attempts"], int)
                or new_config["anti_truncation_max_attempts"] < 1
                or new_config["anti_truncation_max_attempts"] > 10
            ):
                raise HTTPException(
                    status_code=400, detail="Anti-truncation recovery attempts must be an integer between 1 and 10."
                )

        if "token_compression_enabled" in new_config:
            if not isinstance(new_config["token_compression_enabled"], bool):
                raise HTTPException(
                    status_code=400,
                    detail="The token compression switch must be a boolean.",
                )

        current_compression = await config.get_token_compression_config()
        compression_threshold = new_config.get(
            "token_compression_threshold",
            current_compression["threshold_tokens"],
        )
        compression_target = new_config.get(
            "token_compression_target",
            current_compression["target_tokens"],
        )
        if (
            not isinstance(compression_threshold, int)
            or isinstance(compression_threshold, bool)
            or compression_threshold < 128
            or compression_threshold > 2_000_000
        ):
            raise HTTPException(
                status_code=400,
                detail="The compression threshold must be an integer between 128 and 2000000 tokens.",
            )
        if (
            not isinstance(compression_target, int)
            or isinstance(compression_target, bool)
            or compression_target < 64
            or compression_target >= compression_threshold
        ):
            raise HTTPException(
                status_code=400,
                detail="The compression target must be an integer of at least 64 tokens and lower than the threshold.",
            )
        if "token_compression_min_recent_turns" in new_config:
            min_recent_turns = new_config["token_compression_min_recent_turns"]
            if (
                not isinstance(min_recent_turns, int)
                or isinstance(min_recent_turns, bool)
                or min_recent_turns < 1
                or min_recent_turns > 50
            ):
                raise HTTPException(
                    status_code=400,
                    detail="Recent turns to preserve must be an integer between 1 and 50.",
                )

        if "routing_strategy" in new_config:
            if new_config["routing_strategy"] not in {"balanced", "priority"}:
                raise HTTPException(
                    status_code=400,
                    detail="Routing strategy must be balanced or priority.",
                )
        if "preferred_provider" in new_config:
            preferred_provider = new_config["preferred_provider"]
            if not isinstance(preferred_provider, str) or len(preferred_provider) > 80:
                raise HTTPException(
                    status_code=400,
                    detail="Preferred provider must be a valid provider identifier.",
                )
        if "upstream_timeout_seconds" in new_config:
            try:
                upstream_timeout = float(new_config["upstream_timeout_seconds"])
            except (TypeError, ValueError):
                raise HTTPException(
                    status_code=400,
                    detail="Upstream timeout must be a valid number.",
                )
            if upstream_timeout < 5 or upstream_timeout > 900:
                raise HTTPException(
                    status_code=400,
                    detail="Upstream timeout must be between 5 and 900 seconds.",
                )
            new_config["upstream_timeout_seconds"] = upstream_timeout

        if "log_level" in new_config:
            if new_config["log_level"] not in {
                "debug", "info", "warning", "error", "critical"
            }:
                raise HTTPException(
                    status_code=400,
                    detail="Log level must be debug, info, warning, error, or critical.",
                )
        for key, label, minimum, maximum in (
            ("log_max_mb", "Maximum log file size", 1, 1024),
            ("log_backup_count", "Log backup count", 1, 20),
        ):
            if key not in new_config:
                continue
            value = new_config[key]
            if not isinstance(value, int) or isinstance(value, bool) or value < minimum or value > maximum:
                raise HTTPException(
                    status_code=400,
                    detail=f"{label} must be an integer between {minimum} and {maximum}.",
                )

        if "compatibility_mode_enabled" in new_config:
            if not isinstance(new_config["compatibility_mode_enabled"], bool):
                raise HTTPException(status_code=400, detail="The compatibility mode switch must be a boolean.")

        if "return_thoughts_to_frontend" in new_config:
            if not isinstance(new_config["return_thoughts_to_frontend"], bool):
                raise HTTPException(status_code=400, detail="The reasoning content switch must be a boolean.")

        if "stream_to_nonstream" in new_config:
            if not isinstance(new_config["stream_to_nonstream"], bool):
                raise HTTPException(status_code=400, detail="The stream-to-non-stream switch must be a boolean.")

        if "switch_credential_enabled" in new_config:
            if not isinstance(new_config["switch_credential_enabled"], bool):
                raise HTTPException(status_code=400, detail="The credential switching setting must be a boolean.")


        if "keepalive_url" in new_config:
            if not isinstance(new_config["keepalive_url"], str):
                raise HTTPException(status_code=400, detail="Keep-alive URL must be a string.")

        if "keepalive_interval" in new_config:
            try:
                interval = int(new_config["keepalive_interval"])
                if interval < 5 or interval > 86400:
                    raise HTTPException(status_code=400, detail="Keep-alive interval must be between 5 and 86400 seconds.")
                new_config["keepalive_interval"] = interval
            except (ValueError, TypeError):
                raise HTTPException(status_code=400, detail="Keep-alive interval must be a valid integer.")

        if "host" in new_config:
            if not isinstance(new_config["host"], str) or not new_config["host"].strip():
                raise HTTPException(status_code=400, detail="Server host address cannot be empty.")

        if "port" in new_config:
            if (
                not isinstance(new_config["port"], int)
                or new_config["port"] < 1
                or new_config["port"] > 65535
            ):
                raise HTTPException(status_code=400, detail="Port number must be an integer between 1 and 65535.")

        if "panel_password" in new_config:
            if not isinstance(new_config["panel_password"], str):
                raise HTTPException(status_code=400, detail="Control panel password must be a string.")

        if "password" in new_config:
            if not isinstance(new_config["password"], str):
                raise HTTPException(status_code=400, detail="Access password must be a string.")

        oauth_client_keys = {
            "code_assist_client_id",
            "code_assist_client_secret",
            "antigravity_client_id",
            "antigravity_client_secret",
            "client_id",
            "client_secret",
        }
        for key in oauth_client_keys & set(new_config):
            if not isinstance(new_config[key], str):
                raise HTTPException(status_code=400, detail=f"Configuration value '{key}' must be a string.")


        env_locked_keys = get_env_locked_keys()


        storage_adapter = await get_storage_adapter()
        saved_config = {}
        for key, value in new_config.items():
            if key not in env_locked_keys:
                await storage_adapter.set_config(key, value)
                saved_config[key] = value


        await config.reload_config()


        keepalive_keys = {"keepalive_url", "keepalive_interval"}
        if keepalive_keys & set(new_config.keys()):
            try:
                await keepalive_service.restart()
            except Exception as e:
                log.warning(f"Failed to restart keep-alive service: {e}")

        if {"log_level", "log_max_mb", "log_backup_count"} & set(saved_config):
            log_config = await config.get_log_config()
            configure_logging(
                log_config["level"],
                log_config["max_mb"],
                log_config["backup_count"],
            )

        # Build response message
        update_classification = _classify_config_updates(saved_config)
        response_data = {
            "message": "Configuration saved.",
            "saved_config": saved_config,
            **update_classification,
        }
        if update_classification["restart_required"]:
            response_data["restart_notice"] = (
                "Restart the application to apply listener or credential storage changes."
            )

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to save configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/access")
async def update_access_credentials(
    request: AccessCredentialsUpdateRequest,
    token: str = Depends(verify_panel_token),
):
    """Update the panel password without exposing its current value."""
    if not await verify_password(request.current_password):
        raise HTTPException(status_code=401, detail="The current console password is incorrect.")

    requested_updates = {
        "panel_password": (
            request.panel_password,
            request.panel_password_confirm,
            "Panel password",
        ),
    }
    updates = {}
    for key, (value, confirmation, label) in requested_updates.items():
        if value is None or value == "":
            continue
        if value != confirmation:
            raise HTTPException(status_code=400, detail=f"{label} confirmation does not match.")
        if len(value) < 8 or len(value) > 256:
            raise HTTPException(
                status_code=400,
                detail=f"{label} must contain between 8 and 256 characters.",
            )
        updates[key] = value

    if not updates:
        raise HTTPException(status_code=400, detail="Enter at least one new password.")

    env_locked_keys = get_env_locked_keys()
    locked_updates = sorted(set(updates) & env_locked_keys)
    if locked_updates:
        raise HTTPException(
            status_code=409,
            detail=(
                "The requested password is managed by the runtime environment and "
                "cannot be changed from the console."
            ),
        )

    try:
        storage_adapter = await get_storage_adapter()
        for key, value in updates.items():
            await storage_adapter.set_config(key, hash_password(value))
        await config.reload_config()

        response = {
            "message": "Console password updated.",
            "updated": sorted(updates),
        }
        if "panel_password" in updates:
            response["token"] = await create_panel_session_token()

        log.info("Control-panel password updated.")
        return JSONResponse(content=response)
    except HTTPException:
        raise
    except Exception as exc:
        log.error(f"Failed to update the control-panel password: {exc}")
        raise HTTPException(status_code=500, detail="Failed to update the console password.")


@router.post("/reset")
async def reset_config(token: str = Depends(verify_panel_token)):
    """Reset global configuration overrides while preserving access secrets."""
    try:
        env_locked_keys = get_env_locked_keys()
        resettable_keys = RESETTABLE_CONFIG_KEYS - env_locked_keys

        storage_adapter = await get_storage_adapter()
        deleted_keys = []
        for key in sorted(resettable_keys):
            if await storage_adapter.delete_config(key):
                deleted_keys.append(key)

        await config.reload_config()

        try:
            await keepalive_service.restart()
        except Exception as e:
            log.warning(f"Failed to restart keep-alive service after configuration reset: {e}")

        log_config = await config.get_log_config()
        configure_logging(
            log_config["level"],
            log_config["max_mb"],
            log_config["backup_count"],
        )

        return JSONResponse(
            content={
                "message": "System configuration reset to defaults. Access passwords and the generated API key were preserved.",
                "reset_config": deleted_keys,
                "env_locked": sorted(env_locked_keys & RESETTABLE_CONFIG_KEYS),
                "preserved": sorted(PRESERVED_RESET_KEYS),
                **_classify_config_updates(deleted_keys),
            }
        )

    except Exception as e:
        log.error(f"Failed to reset configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))
