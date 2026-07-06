"""Internal implementation detail."""

import os
from typing import Any, Optional

from paths import DEFAULT_CREDENTIALS_DIR


_config_cache: dict[str, Any] = {}
_config_initialized = False

# Client Configuration


AUTO_DISABLE_ERROR_CODES = [403]
API_KEY_PREFIX = "sk-ogw-"




ENV_MAPPINGS = {
    "CODE_ASSIST_ENDPOINT": "code_assist_endpoint",
    "CREDENTIALS_DIR": "credentials_dir",
    "PROXY": "proxy",
    "OAUTH_URL": "oauth_url",
    "GOOGLE_APIS_URL": "google_apis_url",
    "RESOURCE_MANAGER_URL": "resource_manager_url",
    "SERVICE_USAGE_URL": "service_usage_url",
    "API_URL": "api_url",
    "AUTO_DISABLE": "auto_disable_enabled",
    "AUTO_DISABLE_ERROR_CODES": "auto_disable_error_codes",
    "RETRY_429_MAX_RETRIES": "retry_429_max_retries",
    "RETRY_429_ENABLED": "retry_429_enabled",
    "RETRY_429_INTERVAL": "retry_429_interval",
    "ANTI_TRUNCATION_MAX_ATTEMPTS": "anti_truncation_max_attempts",
    "COMPATIBILITY_MODE": "compatibility_mode_enabled",
    "RETURN_THOUGHTS_TO_FRONTEND": "return_thoughts_to_frontend",
    "STREAM_TO_NONSTREAM": "stream_to_nonstream",
    "SWITCH_CREDENTIAL_ENABLED": "switch_credential_enabled",
    "HOST": "host",
    "PORT": "port",
    "API_KEY": "api_key",
    "API_PASSWORD": "api_password",
    "PANEL_PASSWORD": "panel_password",
    "PASSWORD": "password",
    "KEEPALIVE_URL": "keepalive_url",
    "KEEPALIVE_INTERVAL": "keepalive_interval",
}




async def init_config():
    """Internal implementation detail."""
    global _config_cache, _config_initialized

    if _config_initialized:
        return

    try:
        from core.storage_adapter import get_storage_adapter
        storage_adapter = await get_storage_adapter()
        _config_cache = await storage_adapter.get_all_config()
        _config_initialized = True
    except Exception:

        _config_cache = {}
        _config_initialized = True


async def reload_config():
    """Internal implementation detail."""
    global _config_cache, _config_initialized

    try:
        from core.storage_adapter import get_storage_adapter
        storage_adapter = await get_storage_adapter()


        if hasattr(storage_adapter._backend, 'reload_config_cache'):
            await storage_adapter._backend.reload_config_cache()


        _config_cache = await storage_adapter.get_all_config()
        _config_initialized = True
    except Exception:
        pass


def _get_cached_config(key: str, default: Any = None) -> Any:
    """Internal implementation detail."""
    return _config_cache.get(key, default)


async def get_config_value(key: str, default: Any = None, env_var: Optional[str] = None) -> Any:
    """Get configuration value with priority: ENV > Storage > default."""

    if not _config_initialized:
        await init_config()

    # Priority 1: Environment variable
    if env_var and os.getenv(env_var):
        return os.getenv(env_var)

    # Priority 2: Memory cache
    value = _get_cached_config(key)
    if value is not None:
        return value

    return default


async def has_password_configured() -> bool:
    """Return True when any panel/API password source has been configured."""
    if not _config_initialized:
        await init_config()

    password_env_vars = ("PANEL_PASSWORD", "API_PASSWORD", "PASSWORD")
    if any(os.getenv(name) for name in password_env_vars):
        return True

    password_keys = ("panel_password", "api_password", "password")
    return any(bool(_get_cached_config(key)) for key in password_keys)


# Configuration getters - all async
async def get_proxy_config():
    """Get proxy configuration."""
    proxy_url = await get_config_value("proxy", env_var="PROXY")
    return proxy_url if proxy_url else None


async def get_auto_disable_enabled() -> bool:
    """Get credential auto-disable setting."""
    env_value = os.getenv("AUTO_DISABLE")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("auto_disable_enabled", False))


async def get_auto_disable_error_codes() -> list:
    """
    Get credential auto-disable error codes.

    Environment variable: AUTO_DISABLE_ERROR_CODES (comma-separated, e.g., "400,403")
    Database config key: auto_disable_error_codes
    Default: [403]
    """
    env_value = os.getenv("AUTO_DISABLE_ERROR_CODES")
    if env_value:
        try:
            return [int(code.strip()) for code in env_value.split(",") if code.strip()]
        except ValueError:
            pass

    codes = await get_config_value("auto_disable_error_codes")
    if codes and isinstance(codes, list):
        return codes
    return AUTO_DISABLE_ERROR_CODES


async def get_retry_429_max_retries() -> int:
    """Get max retries for 429 errors."""
    env_value = os.getenv("RETRY_429_MAX_RETRIES")
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass

    return int(await get_config_value("retry_429_max_retries", 5))


async def get_retry_429_enabled() -> bool:
    """Get 429 retry enabled setting."""
    env_value = os.getenv("RETRY_429_ENABLED")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("retry_429_enabled", True))


async def get_retry_429_interval() -> float:
    """Get 429 retry interval in seconds."""
    env_value = os.getenv("RETRY_429_INTERVAL")
    if env_value:
        try:
            return float(env_value)
        except ValueError:
            pass

    return float(await get_config_value("retry_429_interval", 1))


async def get_anti_truncation_max_attempts() -> int:
    """
    Get maximum attempts for anti-truncation continuation.

    Environment variable: ANTI_TRUNCATION_MAX_ATTEMPTS
    Database config key: anti_truncation_max_attempts
    Default: 3
    """
    env_value = os.getenv("ANTI_TRUNCATION_MAX_ATTEMPTS")
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass

    return int(await get_config_value("anti_truncation_max_attempts", 3))


# Server Configuration
async def get_server_host() -> str:
    """
    Get server host setting.

    Environment variable: HOST
    Database config key: host
    Default: 0.0.0.0
    """
    return str(await get_config_value("host", "0.0.0.0", "HOST"))


async def get_server_port() -> int:
    """
    Get server port setting.

    Environment variable: PORT
    Database config key: port
    Default: 7861
    """
    env_value = os.getenv("PORT")
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass

    return int(await get_config_value("port", 7861))


async def get_api_password() -> str:
    """
    Get API password setting for chat endpoints.

    Environment variable: API_PASSWORD
    Database config key: api_password
    Default: Empty string until the first-run setup creates a password.
    """
    # Prefer API_PASSWORD before falling back to PASSWORD.
    api_password = await get_config_value("api_password", None, "API_PASSWORD")
    if api_password is not None:
        return str(api_password)


    return str(await get_config_value("password", "", "PASSWORD") or "")


async def get_panel_password() -> str:
    """
    Get panel password setting for web interface.

    Environment variable: PANEL_PASSWORD
    Database config key: panel_password
    Default: Empty string until the first-run setup creates a password.
    """
    # Prefer PANEL_PASSWORD before falling back to PASSWORD.
    panel_password = await get_config_value("panel_password", None, "PANEL_PASSWORD")
    if panel_password is not None:
        return str(panel_password)


    return str(await get_config_value("password", "", "PASSWORD") or "")


async def get_server_password() -> str:
    """
    Get server password setting (deprecated, use get_api_password or get_panel_password).

    Environment variable: PASSWORD
    Database config key: password
    Default: empty until first-run setup.
    """
    return str(await get_config_value("password", "", "PASSWORD") or "")


async def get_credentials_dir() -> str:
    """
    Get credentials directory setting.

    Environment variable: CREDENTIALS_DIR
    Database config key: credentials_dir
    Default: backend/data/creds
    """
    env_value = os.getenv("CREDENTIALS_DIR")
    if env_value:
        return env_value

    value = await get_config_value("credentials_dir", str(DEFAULT_CREDENTIALS_DIR))
    if str(value) in {"./creds", ".\\creds", "creds"}:
        return str(DEFAULT_CREDENTIALS_DIR)
    return str(value)


async def get_code_assist_endpoint() -> str:
    """
    Get Code Assist endpoint setting.

    Environment variable: CODE_ASSIST_ENDPOINT
    Database config key: code_assist_endpoint
    Default: https://cloudcode-pa.googleapis.com
    """
    return str(
        await get_config_value(
            "code_assist_endpoint", "https://cloudcode-pa.googleapis.com", "CODE_ASSIST_ENDPOINT"
        )
    )


async def get_compatibility_mode_enabled() -> bool:
    """Internal implementation detail."""
    env_value = os.getenv("COMPATIBILITY_MODE")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("compatibility_mode_enabled", False))


async def get_return_thoughts_to_frontend() -> bool:
    """Internal implementation detail."""
    env_value = os.getenv("RETURN_THOUGHTS_TO_FRONTEND")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("return_thoughts_to_frontend", True))


async def get_stream_to_nonstream() -> bool:
    """Internal implementation detail."""
    env_value = os.getenv("STREAM_TO_NONSTREAM")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("stream_to_nonstream", True))


async def get_switch_credential_enabled() -> bool:
    """Internal implementation detail."""
    env_value = os.getenv("SWITCH_CREDENTIAL_ENABLED")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("switch_credential_enabled", False))


async def get_oauth_proxy_url() -> str:
    """Internal implementation detail."""
    return str(
        await get_config_value(
            "oauth_url", "https://oauth2.googleapis.com", "OAUTH_URL"
        )
    )


async def get_googleapis_proxy_url() -> str:
    """Internal implementation detail."""
    return str(
        await get_config_value(
            "google_apis_url", "https://www.googleapis.com", "GOOGLE_APIS_URL"
        )
    )


async def get_resource_manager_api_url() -> str:
    """Internal implementation detail."""
    return str(
        await get_config_value(
            "resource_manager_url",
            "https://cloudresourcemanager.googleapis.com",
            "RESOURCE_MANAGER_URL",
        )
    )


async def get_service_usage_api_url() -> str:
    """Internal implementation detail."""
    return str(
        await get_config_value(
            "service_usage_url", "https://serviceusage.googleapis.com", "SERVICE_USAGE_URL"
        )
    )


async def get_api_url() -> str:
    """Internal implementation detail."""
    return str(
        await get_config_value(
            "api_url",
            "https://daily-cloudcode-pa.googleapis.com",
            "API_URL",
        )
    )


async def get_keepalive_url() -> str:
    """Internal implementation detail."""
    return str(await get_config_value("keepalive_url", "", "KEEPALIVE_URL"))


async def get_keepalive_interval() -> int:
    """Internal implementation detail."""
    env_value = os.getenv("KEEPALIVE_INTERVAL")
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass

    return int(await get_config_value("keepalive_interval", 60))


async def get_api_key() -> str:
    """Internal implementation detail."""
    from core.storage_adapter import get_storage_adapter

    env_key = os.getenv("API_KEY", "").strip()
    if env_key:
        if not env_key.startswith(API_KEY_PREFIX):
            raise RuntimeError(f"API_KEY must start with {API_KEY_PREFIX}")
        return env_key

    storage_adapter = await get_storage_adapter()
    key = await get_config_value("api_key")
    if not key or not str(key).startswith(API_KEY_PREFIX):
        import secrets
        key = f"{API_KEY_PREFIX}{secrets.token_hex(20)}"
        await storage_adapter.set_config("api_key", key)
        # Update cache
        global _config_cache
        _config_cache["api_key"] = key
    return key
