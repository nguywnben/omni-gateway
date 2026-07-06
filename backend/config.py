"""Internal implementation detail."""

import os
from typing import Any, Optional

from paths import DEFAULT_CREDENTIALS_DIR


_config_cache: dict[str, Any] = {}
_config_initialized = False

# Client Configuration


AUTO_DISABLE_ERROR_CODES = [403]
API_KEY_PREFIX = "sk-ogw-"
DEFAULT_CODE_ASSIST_CLIENT_ID = "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com"
DEFAULT_CODE_ASSIST_CLIENT_SECRET = "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"
DEFAULT_ANTIGRAVITY_CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
DEFAULT_ANTIGRAVITY_CLIENT_SECRET = "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"
DEFAULT_ANTIGRAVITY_API_URL = "https://daily-cloudcode-pa.googleapis.com"
DEFAULT_ANTIGRAVITY_USER_AGENT = "antigravity/cli/1.0.1 windows/amd64"
DEFAULT_ANTIGRAVITY_PAYLOAD_USER_AGENT = "antigravity"




ENV_MAPPINGS = {
    "CODE_ASSIST_ENDPOINT": "code_assist_endpoint",
    "CREDENTIALS_DIR": "credentials_dir",
    "PROXY": "proxy",
    "OAUTH_URL": "oauth_url",
    "OAUTH_PROXY_URL": "oauth_url",
    "GOOGLE_APIS_URL": "google_apis_url",
    "GOOGLEAPIS_PROXY_URL": "google_apis_url",
    "RESOURCE_MANAGER_URL": "resource_manager_url",
    "RESOURCE_MANAGER_API_URL": "resource_manager_url",
    "SERVICE_USAGE_URL": "service_usage_url",
    "SERVICE_USAGE_API_URL": "service_usage_url",
    "API_URL": "api_url",
    "ANTIGRAVITY_API_URL": "api_url",
    "CODE_ASSIST_CLIENT_ID": "code_assist_client_id",
    "CODE_ASSIST_CLIENT_SECRET": "code_assist_client_secret",
    "ANTIGRAVITY_CLIENT_ID": "antigravity_client_id",
    "ANTIGRAVITY_CLIENT_SECRET": "antigravity_client_secret",
    "ANTIGRAVITY_USER_AGENT": "antigravity_user_agent",
    "USER_AGENT": "antigravity_user_agent",
    "ANTIGRAVITY_PAYLOAD_USER_AGENT": "antigravity_payload_user_agent",
    "CLIENT_ID": "client_id",
    "CLIENT_SECRET": "client_secret",
    "AUTO_DISABLE": "auto_disable_enabled",
    "AUTO_DISABLE_ERROR_CODES": "auto_disable_error_codes",
    "RETRY_429_MAX_RETRIES": "retry_429_max_retries",
    "RETRY_429_ENABLED": "retry_429_enabled",
    "RETRY_429_INTERVAL": "retry_429_interval",
    "ANTI_TRUNCATION_MAX_ATTEMPTS": "anti_truncation_max_attempts",
    "COMPATIBILITY_MODE": "compatibility_mode_enabled",
    "RETURN_THOUGHTS_TO_FRONTEND": "return_thoughts_to_frontend",
    "STREAM_TO_NONSTREAM": "stream_to_nonstream",
    "ANTIGRAVITY_STREAM2NOSTREAM": "stream_to_nonstream",
    "SWITCH_CREDENTIAL_ENABLED": "switch_credential_enabled",
    "ANTIGRAVITY_SWITCH_CREDENTIAL": "switch_credential_enabled",
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
    env_value = os.getenv("ANTIGRAVITY_STREAM2NOSTREAM") or os.getenv("STREAM_TO_NONSTREAM")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("stream_to_nonstream", True))


async def get_antigravity_stream_to_nonstream() -> bool:
    """Return whether Antigravity non-stream requests should collect stream responses."""
    return await get_stream_to_nonstream()


async def get_switch_credential_enabled() -> bool:
    """Internal implementation detail."""
    env_value = os.getenv("ANTIGRAVITY_SWITCH_CREDENTIAL") or os.getenv("SWITCH_CREDENTIAL_ENABLED")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("switch_credential_enabled", False))


async def get_antigravity_switch_credential_enabled() -> bool:
    """Return whether Antigravity retries may switch to another credential."""
    return await get_switch_credential_enabled()


async def get_oauth_proxy_url() -> str:
    """Internal implementation detail."""
    env_value = os.getenv("OAUTH_URL") or os.getenv("OAUTH_PROXY_URL")
    if env_value:
        return env_value

    return str(await get_config_value("oauth_url", "https://oauth2.googleapis.com"))


async def get_googleapis_proxy_url() -> str:
    """Internal implementation detail."""
    env_value = os.getenv("GOOGLE_APIS_URL") or os.getenv("GOOGLEAPIS_PROXY_URL")
    if env_value:
        return env_value

    return str(await get_config_value("google_apis_url", "https://www.googleapis.com"))


async def get_resource_manager_api_url() -> str:
    """Internal implementation detail."""
    env_value = os.getenv("RESOURCE_MANAGER_URL") or os.getenv("RESOURCE_MANAGER_API_URL")
    if env_value:
        return env_value

    return str(
        await get_config_value(
            "resource_manager_url",
            "https://cloudresourcemanager.googleapis.com",
        )
    )


async def get_service_usage_api_url() -> str:
    """Internal implementation detail."""
    env_value = os.getenv("SERVICE_USAGE_URL") or os.getenv("SERVICE_USAGE_API_URL")
    if env_value:
        return env_value

    return str(await get_config_value("service_usage_url", "https://serviceusage.googleapis.com"))


async def get_api_url() -> str:
    """Internal implementation detail."""
    env_value = os.getenv("ANTIGRAVITY_API_URL") or os.getenv("API_URL")
    if env_value:
        return env_value

    return str(await get_config_value("api_url", DEFAULT_ANTIGRAVITY_API_URL))


async def get_antigravity_api_url() -> str:
    """Return the Antigravity upstream API endpoint."""
    return await get_api_url()


async def get_antigravity_user_agent() -> str:
    """Return the Antigravity CLI user agent."""
    env_value = os.getenv("ANTIGRAVITY_USER_AGENT") or os.getenv("USER_AGENT")
    if env_value:
        return env_value

    return str(
        await get_config_value(
            "antigravity_user_agent",
            DEFAULT_ANTIGRAVITY_USER_AGENT,
        )
        or DEFAULT_ANTIGRAVITY_USER_AGENT
    )


async def get_antigravity_payload_user_agent() -> str:
    """Return the Antigravity payload userAgent value."""
    return str(
        await get_config_value(
            "antigravity_payload_user_agent",
            DEFAULT_ANTIGRAVITY_PAYLOAD_USER_AGENT,
            "ANTIGRAVITY_PAYLOAD_USER_AGENT",
        )
        or DEFAULT_ANTIGRAVITY_PAYLOAD_USER_AGENT
    )


async def get_code_assist_oauth_client_config() -> tuple[str, str]:
    """Return the OAuth client used for Code Assist credential creation."""
    client_id = str(
        await get_config_value(
            "code_assist_client_id",
            DEFAULT_CODE_ASSIST_CLIENT_ID,
            "CODE_ASSIST_CLIENT_ID",
        )
        or ""
    )
    client_secret = str(
        await get_config_value(
            "code_assist_client_secret",
            DEFAULT_CODE_ASSIST_CLIENT_SECRET,
            "CODE_ASSIST_CLIENT_SECRET",
        )
        or DEFAULT_CODE_ASSIST_CLIENT_SECRET
    )
    return client_id, client_secret


async def get_antigravity_oauth_client_config() -> tuple[str, str]:
    """Return the OAuth client used for Antigravity provider credential creation."""
    client_id = str(
        await get_config_value(
            "antigravity_client_id",
            "",
            "ANTIGRAVITY_CLIENT_ID",
        )
        or ""
    )
    if not client_id:
        client_id = str(
            await get_config_value("client_id", DEFAULT_ANTIGRAVITY_CLIENT_ID, "CLIENT_ID")
            or ""
        )

    client_secret = str(
        await get_config_value(
            "antigravity_client_secret",
            None,
            "ANTIGRAVITY_CLIENT_SECRET",
        )
        or ""
    )
    if not client_secret:
        client_secret = str(
            await get_config_value(
                "client_secret",
                DEFAULT_ANTIGRAVITY_CLIENT_SECRET,
                "CLIENT_SECRET",
            )
            or DEFAULT_ANTIGRAVITY_CLIENT_SECRET
        )

    return client_id, client_secret


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
