import asyncio
import os
from typing import Any, Optional

from dotenv import load_dotenv
from log import log
from paths import DEFAULT_CREDENTIALS_DIR, PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env", override=False)


_config_cache: dict[str, Any] = {}
_config_initialized = False
_config_lock = asyncio.Lock()

LEGACY_ENV_RENAMES = {
    "API_URL": "ANTIGRAVITY_API_URL",
    "USER_AGENT": "ANTIGRAVITY_USER_AGENT",
    "CLIENT_ID": "ANTIGRAVITY_CLIENT_ID",
    "CLIENT_SECRET": "ANTIGRAVITY_CLIENT_SECRET",
    "OAUTH_PROXY_URL": "OAUTH_URL",
    "GOOGLEAPIS_PROXY_URL": "GOOGLE_APIS_URL",
    "RESOURCE_MANAGER_API_URL": "RESOURCE_MANAGER_URL",
    "SERVICE_USAGE_API_URL": "SERVICE_USAGE_URL",
    "ANTIGRAVITY_STREAM2NOSTREAM": "STREAM_TO_NONSTREAM",
    "ANTIGRAVITY_SWITCH_CREDENTIAL": "SWITCH_CREDENTIAL_ENABLED",
}

# Client Configuration


AUTO_DISABLE_ERROR_CODES = [403]
API_KEY_PREFIX = "sk-ogw-"
DEFAULT_CODE_ASSIST_CLIENT_ID = (
    "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com"
)
DEFAULT_CODE_ASSIST_CLIENT_SECRET = "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"
DEFAULT_ANTIGRAVITY_CLIENT_ID = (
    "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"
)
DEFAULT_ANTIGRAVITY_CLIENT_SECRET = "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"
DEFAULT_ANTIGRAVITY_API_URL = "https://daily-cloudcode-pa.googleapis.com"
DEFAULT_ANTIGRAVITY_USER_AGENT = "antigravity/cli/1.0.1 windows/amd64"
DEFAULT_ANTIGRAVITY_PAYLOAD_USER_AGENT = "antigravity"
DEFAULT_GOOGLE_AI_STUDIO_API_URL = "https://generativelanguage.googleapis.com"
DEFAULT_XAI_API_URL = "https://api.x.ai/v1"
DEFAULT_XAI_OAUTH_ISSUER = "https://auth.x.ai"
DEFAULT_XAI_CLIENT_ID = "b1a00492-073a-47ea-816f-4c329264a828"
DEFAULT_XAI_USER_AGENT = "grok-cli/omni-gateway"
DEFAULT_OPENAI_API_URL = "https://api.openai.com/v1"
DEFAULT_CODEX_API_URL = "https://chatgpt.com/backend-api/codex"
DEFAULT_CODEX_AUTH_BASE = "https://auth.openai.com"
DEFAULT_CODEX_CLIENT_ID = "app_EMoamEEZ73f0CkXaXp7hrann"
DEFAULT_CODEX_USER_AGENT = "codex_cli_rs/0.0.0 (Unknown 0; unknown)"


ENV_MAPPINGS = {
    "CODE_ASSIST_ENDPOINT": "code_assist_endpoint",
    "CREDENTIALS_DIR": "credentials_dir",
    "PROXY": "proxy",
    "OAUTH_URL": "oauth_url",
    "GOOGLE_APIS_URL": "google_apis_url",
    "RESOURCE_MANAGER_URL": "resource_manager_url",
    "SERVICE_USAGE_URL": "service_usage_url",
    "ANTIGRAVITY_API_URL": "antigravity_api_url",
    "GOOGLE_AI_STUDIO_API_URL": "google_ai_studio_api_url",
    "XAI_API_URL": "xai_api_url",
    "XAI_OAUTH_ISSUER": "xai_oauth_issuer",
    "XAI_CLIENT_ID": "xai_client_id",
    "XAI_USER_AGENT": "xai_user_agent",
    "OPENAI_API_URL": "openai_api_url",
    "CODEX_API_URL": "codex_api_url",
    "CODEX_AUTH_BASE": "codex_auth_base",
    "CODEX_CLIENT_ID": "codex_client_id",
    "CODEX_USER_AGENT": "codex_user_agent",
    "CODE_ASSIST_CLIENT_ID": "code_assist_client_id",
    "CODE_ASSIST_CLIENT_SECRET": "code_assist_client_secret",
    "ANTIGRAVITY_CLIENT_ID": "antigravity_client_id",
    "ANTIGRAVITY_CLIENT_SECRET": "antigravity_client_secret",
    "ANTIGRAVITY_USER_AGENT": "antigravity_user_agent",
    "ANTIGRAVITY_PAYLOAD_USER_AGENT": "antigravity_payload_user_agent",
    "AUTO_DISABLE": "auto_disable_enabled",
    "AUTO_DISABLE_ERROR_CODES": "auto_disable_error_codes",
    "RETRY_429_MAX_RETRIES": "retry_429_max_retries",
    "RETRY_429_ENABLED": "retry_429_enabled",
    "RETRY_429_INTERVAL": "retry_429_interval",
    "ANTI_TRUNCATION_MAX_ATTEMPTS": "anti_truncation_max_attempts",
    "TOKEN_COMPRESSION_ENABLED": "token_compression_enabled",
    "TOKEN_COMPRESSION_THRESHOLD": "token_compression_threshold",
    "TOKEN_COMPRESSION_TARGET": "token_compression_target",
    "TOKEN_COMPRESSION_MIN_RECENT_TURNS": "token_compression_min_recent_turns",
    "ROUTING_STRATEGY": "routing_strategy",
    "PREFERRED_PROVIDER": "preferred_provider",
    "UPSTREAM_TIMEOUT_SECONDS": "upstream_timeout_seconds",
    "LOG_LEVEL": "log_level",
    "LOG_MAX_MB": "log_max_mb",
    "LOG_BACKUP_COUNT": "log_backup_count",
    "COMPATIBILITY_MODE": "compatibility_mode_enabled",
    "RETURN_THOUGHTS_TO_FRONTEND": "return_thoughts_to_frontend",
    "STREAM_TO_NONSTREAM": "stream_to_nonstream",
    "SWITCH_CREDENTIAL_ENABLED": "switch_credential_enabled",
    "HOST": "host",
    "PORT": "port",
    "API_KEY": "api_key",
    "PANEL_PASSWORD": "panel_password",
    "KEEPALIVE_URL": "keepalive_url",
    "KEEPALIVE_INTERVAL": "keepalive_interval",
}


async def init_config():
    global _config_cache, _config_initialized

    if _config_initialized:
        return

    async with _config_lock:
        if _config_initialized:
            return
        if os.getenv("PASSWORD") and not os.getenv("PANEL_PASSWORD"):
            raise RuntimeError(
                "PASSWORD is no longer supported. Rename it to PANEL_PASSWORD before startup."
            )

        for legacy_name, replacement in LEGACY_ENV_RENAMES.items():
            if os.getenv(legacy_name) and not os.getenv(replacement):
                log.warning(
                    f"Ignoring removed environment variable {legacy_name}; "
                    f"rename it to {replacement}."
                )

        try:
            from core.storage_adapter import get_storage_adapter

            storage_adapter = await get_storage_adapter()
            values = await storage_adapter.get_all_config()

            stored_migrations = {
                "password": "panel_password",
                "client_id": "antigravity_client_id",
                "client_secret": "antigravity_client_secret",
                "api_url": "antigravity_api_url",
            }
            migrated = False
            for legacy_key, canonical_key in stored_migrations.items():
                legacy_value = values.get(legacy_key)
                if legacy_value and not values.get(canonical_key):
                    saved = await storage_adapter.set_config(canonical_key, legacy_value)
                    if not saved:
                        raise RuntimeError(
                            "Failed to migrate legacy configuration key "
                            f"{legacy_key} to {canonical_key}."
                        )
                    log.info(f"Migrated legacy configuration key {legacy_key} to {canonical_key}.")
                    migrated = True

            legacy_keys = [
                key
                for key in (
                    "password",
                    "api_password",
                    "client_id",
                    "client_secret",
                    "api_url",
                )
                if key in values
            ]
            for key in legacy_keys:
                deleted = await storage_adapter.delete_config(key)
                if not deleted:
                    raise RuntimeError(f"Failed to remove legacy configuration key: {key}.")

            if migrated or legacy_keys:
                values = await storage_adapter.get_all_config()

            _config_cache = values
            _config_initialized = True
        except Exception:
            _config_cache = {}
            _config_initialized = False
            raise


async def reload_config():
    global _config_cache, _config_initialized

    async with _config_lock:
        from core.storage_adapter import get_storage_adapter

        storage_adapter = await get_storage_adapter()

        if hasattr(storage_adapter._backend, "reload_config_cache"):
            await storage_adapter._backend.reload_config_cache()

        values = await storage_adapter.get_all_config()
        _config_cache = values
        _config_initialized = True


def _get_cached_config(key: str, default: Any = None) -> Any:
    return _config_cache.get(key, default)


def trust_proxy_headers_enabled() -> bool:
    """Return whether forwarding headers from a trusted reverse proxy are accepted."""
    return os.getenv("TRUST_PROXY_HEADERS", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


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
    """Return True when a control-panel password source is configured."""
    if not _config_initialized:
        await init_config()

    if os.getenv("PANEL_PASSWORD"):
        return True

    return bool(_get_cached_config("panel_password"))


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


def _coerce_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("true", "1", "yes", "on"):
            return True
        if normalized in ("false", "0", "no", "off"):
            return False
    return default


def _coerce_bounded_int(value: Any, default: int, minimum: int, maximum: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return min(maximum, max(minimum, parsed))


async def get_token_compression_config() -> dict[str, Any]:
    """Return validated settings for bounded conversation-history compression."""
    enabled = _coerce_bool(
        await get_config_value("token_compression_enabled", True, "TOKEN_COMPRESSION_ENABLED"),
        True,
    )
    threshold = _coerce_bounded_int(
        await get_config_value(
            "token_compression_threshold", 32_000, "TOKEN_COMPRESSION_THRESHOLD"
        ),
        32_000,
        128,
        2_000_000,
    )
    target = _coerce_bounded_int(
        await get_config_value("token_compression_target", 24_000, "TOKEN_COMPRESSION_TARGET"),
        24_000,
        64,
        1_999_999,
    )
    if target >= threshold:
        target = max(64, threshold * 3 // 4)
    min_recent_turns = _coerce_bounded_int(
        await get_config_value(
            "token_compression_min_recent_turns",
            4,
            "TOKEN_COMPRESSION_MIN_RECENT_TURNS",
        ),
        4,
        1,
        50,
    )
    return {
        "enabled": enabled,
        "threshold_tokens": threshold,
        "target_tokens": target,
        "min_recent_turns": min_recent_turns,
    }


async def get_routing_policy() -> dict[str, str]:
    """Return the cross-provider credential selection policy."""
    strategy = (
        str(
            await get_config_value("routing_strategy", "balanced", "ROUTING_STRATEGY") or "balanced"
        )
        .strip()
        .lower()
    )
    if strategy not in {"balanced", "priority"}:
        strategy = "balanced"

    preferred_provider = (
        str(await get_config_value("preferred_provider", "", "PREFERRED_PROVIDER") or "")
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )
    return {
        "strategy": strategy,
        "preferred_provider": preferred_provider,
    }


async def get_upstream_timeout_seconds() -> float:
    """Return the bounded timeout used for provider inference requests."""
    raw_value = await get_config_value(
        "upstream_timeout_seconds", 300.0, "UPSTREAM_TIMEOUT_SECONDS"
    )
    try:
        timeout = float(raw_value)
    except (TypeError, ValueError):
        timeout = 300.0
    return min(900.0, max(5.0, timeout))


async def get_log_config() -> dict[str, Any]:
    """Return validated runtime log level and file retention settings."""
    level = str(await get_config_value("log_level", "info", "LOG_LEVEL") or "info").strip().lower()
    if level not in {"debug", "info", "warning", "error", "critical"}:
        level = "info"

    max_mb = _coerce_bounded_int(
        await get_config_value("log_max_mb", 10, "LOG_MAX_MB"),
        10,
        1,
        1024,
    )
    backup_count = _coerce_bounded_int(
        await get_config_value("log_backup_count", 3, "LOG_BACKUP_COUNT"),
        3,
        1,
        20,
    )
    return {
        "level": level,
        "max_mb": max_mb,
        "backup_count": backup_count,
    }


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
    Default: 4283
    """
    env_value = os.getenv("PORT")
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass

    return int(await get_config_value("port", 4283))


async def get_panel_password() -> str:
    """
    Get panel password setting for web interface.

    Environment variable: PANEL_PASSWORD
    Database config key: panel_password
    Default: Empty string until the first-run setup creates a password.
    """
    return str(await get_config_value("panel_password", "", "PANEL_PASSWORD") or "")


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
    env_value = os.getenv("COMPATIBILITY_MODE")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("compatibility_mode_enabled", False))


async def get_return_thoughts_to_frontend() -> bool:
    env_value = os.getenv("RETURN_THOUGHTS_TO_FRONTEND")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("return_thoughts_to_frontend", True))


async def get_stream_to_nonstream() -> bool:
    env_value = os.getenv("STREAM_TO_NONSTREAM")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("stream_to_nonstream", True))


async def get_antigravity_stream_to_nonstream() -> bool:
    """Return whether Antigravity non-stream requests should collect stream responses."""
    return await get_stream_to_nonstream()


async def get_switch_credential_enabled() -> bool:
    env_value = os.getenv("SWITCH_CREDENTIAL_ENABLED")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("switch_credential_enabled", True))


async def get_antigravity_switch_credential_enabled() -> bool:
    """Return whether Antigravity retries may switch to another credential."""
    return await get_switch_credential_enabled()


async def get_oauth_proxy_url() -> str:
    env_value = os.getenv("OAUTH_URL")
    if env_value:
        return env_value

    return str(await get_config_value("oauth_url", "https://oauth2.googleapis.com"))


async def get_googleapis_proxy_url() -> str:
    env_value = os.getenv("GOOGLE_APIS_URL")
    if env_value:
        return env_value

    return str(await get_config_value("google_apis_url", "https://www.googleapis.com"))


async def get_resource_manager_api_url() -> str:
    env_value = os.getenv("RESOURCE_MANAGER_URL")
    if env_value:
        return env_value

    return str(
        await get_config_value(
            "resource_manager_url",
            "https://cloudresourcemanager.googleapis.com",
        )
    )


async def get_service_usage_api_url() -> str:
    env_value = os.getenv("SERVICE_USAGE_URL")
    if env_value:
        return env_value

    return str(await get_config_value("service_usage_url", "https://serviceusage.googleapis.com"))


async def get_antigravity_api_url() -> str:
    """Return the Antigravity upstream API endpoint."""
    env_value = os.getenv("ANTIGRAVITY_API_URL")
    if env_value:
        return env_value

    return str(await get_config_value("antigravity_api_url", DEFAULT_ANTIGRAVITY_API_URL))


async def get_google_ai_studio_api_url() -> str:
    """Return the public Google Generative Language API endpoint."""
    return str(
        await get_config_value(
            "google_ai_studio_api_url",
            DEFAULT_GOOGLE_AI_STUDIO_API_URL,
            "GOOGLE_AI_STUDIO_API_URL",
        )
        or DEFAULT_GOOGLE_AI_STUDIO_API_URL
    ).rstrip("/")


async def get_xai_api_url() -> str:
    return (
        str(
            await get_config_value("xai_api_url", DEFAULT_XAI_API_URL, "XAI_API_URL")
            or DEFAULT_XAI_API_URL
        )
        .strip()
        .rstrip("/")
    )


async def get_xai_oauth_issuer() -> str:
    return (
        str(
            await get_config_value("xai_oauth_issuer", DEFAULT_XAI_OAUTH_ISSUER, "XAI_OAUTH_ISSUER")
            or DEFAULT_XAI_OAUTH_ISSUER
        )
        .strip()
        .rstrip("/")
    )


async def get_xai_client_id() -> str:
    return str(
        await get_config_value("xai_client_id", DEFAULT_XAI_CLIENT_ID, "XAI_CLIENT_ID")
        or DEFAULT_XAI_CLIENT_ID
    ).strip()


async def get_xai_user_agent() -> str:
    return str(
        await get_config_value("xai_user_agent", DEFAULT_XAI_USER_AGENT, "XAI_USER_AGENT")
        or DEFAULT_XAI_USER_AGENT
    ).strip()


async def get_openai_api_url() -> str:
    """Return the OpenAI Platform API base URL."""
    return (
        str(
            await get_config_value("openai_api_url", DEFAULT_OPENAI_API_URL, "OPENAI_API_URL")
            or DEFAULT_OPENAI_API_URL
        )
        .strip()
        .rstrip("/")
    )


async def get_codex_api_url() -> str:
    """Return the ChatGPT Codex upstream API base URL."""
    return (
        str(
            await get_config_value("codex_api_url", DEFAULT_CODEX_API_URL, "CODEX_API_URL")
            or DEFAULT_CODEX_API_URL
        )
        .strip()
        .rstrip("/")
    )


async def get_codex_auth_base() -> str:
    return (
        str(
            await get_config_value("codex_auth_base", DEFAULT_CODEX_AUTH_BASE, "CODEX_AUTH_BASE")
            or DEFAULT_CODEX_AUTH_BASE
        )
        .strip()
        .rstrip("/")
    )


async def get_codex_client_id() -> str:
    return str(
        await get_config_value("codex_client_id", DEFAULT_CODEX_CLIENT_ID, "CODEX_CLIENT_ID")
        or DEFAULT_CODEX_CLIENT_ID
    ).strip()


async def get_codex_user_agent() -> str:
    return str(
        await get_config_value("codex_user_agent", DEFAULT_CODEX_USER_AGENT, "CODEX_USER_AGENT")
        or DEFAULT_CODEX_USER_AGENT
    ).strip()


async def get_antigravity_user_agent() -> str:
    """Return the Antigravity CLI user agent."""
    env_value = os.getenv("ANTIGRAVITY_USER_AGENT")
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
            DEFAULT_ANTIGRAVITY_CLIENT_ID,
            "ANTIGRAVITY_CLIENT_ID",
        )
        or DEFAULT_ANTIGRAVITY_CLIENT_ID
    )

    client_secret = str(
        await get_config_value(
            "antigravity_client_secret",
            DEFAULT_ANTIGRAVITY_CLIENT_SECRET,
            "ANTIGRAVITY_CLIENT_SECRET",
        )
        or DEFAULT_ANTIGRAVITY_CLIENT_SECRET
    )

    return client_id, client_secret


async def get_keepalive_url() -> str:
    return str(await get_config_value("keepalive_url", "", "KEEPALIVE_URL"))


async def get_keepalive_interval() -> int:
    env_value = os.getenv("KEEPALIVE_INTERVAL")
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass

    return int(await get_config_value("keepalive_interval", 60))


async def get_api_key() -> str:
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
