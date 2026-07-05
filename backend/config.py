"""
Configuration constants for the Omni Gateway proxy server.
Centralizes all configuration to avoid duplication across modules.

- å¯å¨æ—¶å è½½ä¸€æ¬¡é…ç½®åˆ°å†…å­˜
- ä¿®æ”¹é…ç½®æ—¶è°ƒç”¨ reload_config() é‡æ–°ä»æ•°æ®åº“å è½½
"""

import os
from typing import Any, Optional

from paths import DEFAULT_CREDENTIALS_DIR

# å…¨å±€é…ç½®ç¼“å­˜
_config_cache: dict[str, Any] = {}
_config_initialized = False

# Client Configuration

# éœ€è¦è‡ªå¨å°ç¦ç„é”™è¯¯ç  (é»˜è®¤å€¼ï¼Œå¯é€è¿‡ç¯å¢ƒå˜é‡æˆ–é…ç½®è¦†ç›–)
OGW_AUTO_DISABLE_ERROR_CODES = [403]

# ====================== ç¯å¢ƒå˜é‡æ˜ å°„è¡¨ ======================
# ç»Ÿä¸€ç»´æ¤ç¯å¢ƒå˜é‡åå’Œé…ç½®é”®åç„æ˜ å°„å…³ç³»
# æ ¼å¼: "ç¯å¢ƒå˜é‡å": "é…ç½®é”®å"
ENV_MAPPINGS = {
    "OGW_CODE_ASSIST_ENDPOINT": "ogw_code_assist_endpoint",
    "OGW_CREDENTIALS_DIR": "ogw_credentials_dir",
    "OGW_PROXY": "ogw_proxy",
    "OGW_OAUTH_URL": "ogw_oauth_url",
    "OGW_GOOGLE_APIS_URL": "ogw_google_apis_url",
    "OGW_RESOURCE_MANAGER_URL": "ogw_resource_manager_url",
    "OGW_SERVICE_USAGE_URL": "ogw_service_usage_url",
    "OGW_API_URL": "ogw_api_url",
    "OGW_AUTO_DISABLE": "ogw_auto_disable_enabled",
    "OGW_AUTO_DISABLE_ERROR_CODES": "ogw_auto_disable_error_codes",
    "OGW_RETRY_429_MAX_RETRIES": "ogw_retry_429_max_retries",
    "OGW_RETRY_429_ENABLED": "ogw_retry_429_enabled",
    "OGW_RETRY_429_INTERVAL": "ogw_retry_429_interval",
    "OGW_ANTI_TRUNCATION_MAX_ATTEMPTS": "ogw_anti_truncation_max_attempts",
    "OGW_COMPATIBILITY_MODE": "ogw_compatibility_mode_enabled",
    "OGW_RETURN_THOUGHTS_TO_FRONTEND": "ogw_return_thoughts_to_frontend",
    "OGW_STREAM_TO_NONSTREAM": "ogw_stream_to_nonstream",
    "OGW_SWITCH_CREDENTIAL_ENABLED": "ogw_switch_credential_enabled",
    "OGW_HOST": "ogw_host",
    "OGW_PORT": "ogw_port",
    "OGW_API_PASSWORD": "ogw_api_password",
    "OGW_PANEL_PASSWORD": "ogw_panel_password",
    "OGW_PASSWORD": "ogw_password",
    "OGW_KEEPALIVE_URL": "ogw_keepalive_url",
    "OGW_KEEPALIVE_INTERVAL": "ogw_keepalive_interval",
}


# ====================== é…ç½®ç³»ç»Ÿ ======================

async def init_config():
    """åˆå§‹åŒ–é…ç½®ç¼“å­˜ï¼ˆå¯å¨æ—¶è°ƒç”¨ä¸€æ¬¡ï¼‰"""
    global _config_cache, _config_initialized

    if _config_initialized:
        return

    try:
        from omni_gateway.storage_adapter import get_storage_adapter
        storage_adapter = await get_storage_adapter()
        _config_cache = await storage_adapter.get_all_config()
        _config_initialized = True
    except Exception:
        # åˆå§‹åŒ–å¤±è´¥æ—¶ä½¿ç”¨ç©ºç¼“å­˜
        _config_cache = {}
        _config_initialized = True


async def reload_config():
    """é‡æ–°å è½½é…ç½®ï¼ˆä¿®æ”¹é…ç½®åè°ƒç”¨ï¼‰"""
    global _config_cache, _config_initialized

    try:
        from omni_gateway.storage_adapter import get_storage_adapter
        storage_adapter = await get_storage_adapter()

        # å¦‚æœåç«¯æ”¯æŒ reload_config_cacheï¼Œè°ƒç”¨å®ƒ
        if hasattr(storage_adapter._backend, 'reload_config_cache'):
            await storage_adapter._backend.reload_config_cache()

        # é‡æ–°å è½½é…ç½®ç¼“å­˜
        _config_cache = await storage_adapter.get_all_config()
        _config_initialized = True
    except Exception:
        pass


def _get_cached_config(key: str, default: Any = None) -> Any:
    """ä»å†…å­˜ç¼“å­˜è·å–é…ç½®ï¼ˆåŒæ­¥ï¼‰"""
    return _config_cache.get(key, default)


async def get_config_value(key: str, default: Any = None, env_var: Optional[str] = None) -> Any:
    """Get configuration value with priority: ENV > Storage > default."""
    # ç¡®ä¿é…ç½®å·²åˆå§‹åŒ–
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


# Configuration getters - all async
async def get_proxy_config():
    """Get proxy configuration."""
    proxy_url = await get_config_value("ogw_proxy", env_var="OGW_PROXY")
    return proxy_url if proxy_url else None


async def get_auto_disable_enabled() -> bool:
    """Get credential auto-disable setting."""
    env_value = os.getenv("OGW_AUTO_DISABLE")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("ogw_auto_disable_enabled", False))


async def get_auto_disable_error_codes() -> list:
    """
    Get credential auto-disable error codes.

    Environment variable: OGW_AUTO_DISABLE_ERROR_CODES (comma-separated, e.g., "400,403")
    Database config key: ogw_auto_disable_error_codes
    Default: [403]
    """
    env_value = os.getenv("OGW_AUTO_DISABLE_ERROR_CODES")
    if env_value:
        try:
            return [int(code.strip()) for code in env_value.split(",") if code.strip()]
        except ValueError:
            pass

    codes = await get_config_value("ogw_auto_disable_error_codes")
    if codes and isinstance(codes, list):
        return codes
    return OGW_AUTO_DISABLE_ERROR_CODES


async def get_retry_429_max_retries() -> int:
    """Get max retries for 429 errors."""
    env_value = os.getenv("OGW_RETRY_429_MAX_RETRIES")
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass

    return int(await get_config_value("ogw_retry_429_max_retries", 5))


async def get_retry_429_enabled() -> bool:
    """Get 429 retry enabled setting."""
    env_value = os.getenv("OGW_RETRY_429_ENABLED")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("ogw_retry_429_enabled", True))


async def get_retry_429_interval() -> float:
    """Get 429 retry interval in seconds."""
    env_value = os.getenv("OGW_RETRY_429_INTERVAL")
    if env_value:
        try:
            return float(env_value)
        except ValueError:
            pass

    return float(await get_config_value("ogw_retry_429_interval", 1))


async def get_anti_truncation_max_attempts() -> int:
    """
    Get maximum attempts for anti-truncation continuation.

    Environment variable: OGW_ANTI_TRUNCATION_MAX_ATTEMPTS
    Database config key: ogw_anti_truncation_max_attempts
    Default: 3
    """
    env_value = os.getenv("OGW_ANTI_TRUNCATION_MAX_ATTEMPTS")
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass

    return int(await get_config_value("ogw_anti_truncation_max_attempts", 3))


# Server Configuration
async def get_server_host() -> str:
    """
    Get server host setting.

    Environment variable: OGW_HOST
    Database config key: ogw_host
    Default: 0.0.0.0
    """
    return str(await get_config_value("ogw_host", "0.0.0.0", "OGW_HOST"))


async def get_server_port() -> int:
    """
    Get server port setting.

    Environment variable: OGW_PORT
    Database config key: ogw_port
    Default: 7861
    """
    env_value = os.getenv("OGW_PORT")
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass

    return int(await get_config_value("ogw_port", 7861))


async def get_api_password() -> str:
    """
    Get API password setting for chat endpoints.

    Environment variable: OGW_API_PASSWORD
    Database config key: ogw_api_password
    Default: Uses OGW_PASSWORD when no specific password is set.
    """
    # Prefer OGW_API_PASSWORD before falling back to OGW_PASSWORD.
    api_password = await get_config_value("ogw_api_password", None, "OGW_API_PASSWORD")
    if api_password is not None:
        return str(api_password)

    # å…¼å®¹æ€§ï¼ä½¿ç”¨é€ç”¨å¯†ç 
    return str(await get_config_value("ogw_password", "pwd", "OGW_PASSWORD"))


async def get_panel_password() -> str:
    """
    Get panel password setting for web interface.

    Environment variable: OGW_PANEL_PASSWORD
    Database config key: ogw_panel_password
    Default: Uses OGW_PASSWORD when no specific password is set.
    """
    # Prefer OGW_PANEL_PASSWORD before falling back to OGW_PASSWORD.
    panel_password = await get_config_value("ogw_panel_password", None, "OGW_PANEL_PASSWORD")
    if panel_password is not None:
        return str(panel_password)

    # å…¼å®¹æ€§ï¼ä½¿ç”¨é€ç”¨å¯†ç 
    return str(await get_config_value("ogw_password", "pwd", "OGW_PASSWORD"))


async def get_server_password() -> str:
    """
    Get server password setting (deprecated, use get_api_password or get_panel_password).

    Environment variable: OGW_PASSWORD
    Database config key: ogw_password
    Default: pwd
    """
    return str(await get_config_value("ogw_password", "pwd", "OGW_PASSWORD"))


async def get_credentials_dir() -> str:
    """
    Get credentials directory setting.

    Environment variable: OGW_CREDENTIALS_DIR
    Database config key: ogw_credentials_dir
    Default: backend/data/creds
    """
    env_value = os.getenv("OGW_CREDENTIALS_DIR")
    if env_value:
        return env_value

    value = await get_config_value("ogw_credentials_dir", str(DEFAULT_CREDENTIALS_DIR))
    if str(value) in {"./creds", ".\\creds", "creds"}:
        return str(DEFAULT_CREDENTIALS_DIR)
    return str(value)


async def get_code_assist_endpoint() -> str:
    """
    Get Code Assist endpoint setting.

    Environment variable: OGW_CODE_ASSIST_ENDPOINT
    Database config key: ogw_code_assist_endpoint
    Default: https://cloudcode-pa.googleapis.com
    """
    return str(
        await get_config_value(
            "ogw_code_assist_endpoint", "https://cloudcode-pa.googleapis.com", "OGW_CODE_ASSIST_ENDPOINT"
        )
    )


async def get_compatibility_mode_enabled() -> bool:
    """
    Get compatibility mode setting.

    å…¼å®¹æ€§æ¨¡å¼ï¼å¯ç”¨åæ‰€æœ‰systemæ¶ˆæ¯å…¨éƒ¨è½¬æ¢æˆuserï¼Œåœç”¨system_instructionsă€‚
    è¯¥é€‰é¡¹å¯èƒ½ä¼é™ä½æ¨¡å‹ç†è§£èƒ½å›ï¼Œä½†æ˜¯èƒ½é¿å…æµå¼ç©ºå›ç„æƒ…å†µă€‚

    Environment variable: OGW_COMPATIBILITY_MODE
    Database config key: ogw_compatibility_mode_enabled
    Default: False
    """
    env_value = os.getenv("OGW_COMPATIBILITY_MODE")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("ogw_compatibility_mode_enabled", False))


async def get_return_thoughts_to_frontend() -> bool:
    """
    Get return thoughts to frontend setting.

    æ§åˆ¶æ˜¯å¦å°†æ€ç»´é“¾è¿”å›åˆ°å‰ç«¯ă€‚
    å¯ç”¨åï¼Œæ€ç»´é“¾ä¼åœ¨å“åº”ä¸­è¿”å›ï¼›ç¦ç”¨åï¼Œæ€ç»´é“¾ä¼åœ¨å“åº”ä¸­è¢«è¿‡æ»¤æ‰ă€‚

    Environment variable: OGW_RETURN_THOUGHTS_TO_FRONTEND
    Database config key: ogw_return_thoughts_to_frontend
    Default: True
    """
    env_value = os.getenv("OGW_RETURN_THOUGHTS_TO_FRONTEND")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("ogw_return_thoughts_to_frontend", True))


async def get_ogw_stream_to_nonstream() -> bool:
    """
    Get use stream for non-stream setting.

    æ§åˆ¶omniéæµå¼è¯·æ±‚æ˜¯å¦ä½¿ç”¨æµå¼APIå¹¶æ”¶é›†ä¸ºå®Œæ•´å“åº”ă€‚
    å¯ç”¨åï¼Œéæµå¼è¯·æ±‚å°†åœ¨åç«¯ä½¿ç”¨æµå¼APIï¼Œç„¶åæ”¶é›†æ‰€æœ‰å—åå†è¿”å›å®Œæ•´å“åº”ă€‚

    Environment variable: OGW_STREAM_TO_NONSTREAM
    Database config key: ogw_stream_to_nonstream
    Default: True
    """
    env_value = os.getenv("OGW_STREAM_TO_NONSTREAM")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("ogw_stream_to_nonstream", True))


async def get_ogw_switch_credential_enabled() -> bool:
    """
    Get omni switch credential setting.

    æ§åˆ¶omniåœ¨é‡è¯•æ—¶æ˜¯å¦åˆ‡æ¢å‡­è¯ă€‚
    ç¦ç”¨æ—¶ä¼æŒç»­ä½¿ç”¨å½“å‰å‡­è¯ï¼Œç›´åˆ°è¯¥å‡­è¯å¯¹å½“å‰æ¨¡å‹è¿›å…¥CDæˆ–è¢«ç¦ç”¨ă€‚

    Environment variable: OGW_SWITCH_CREDENTIAL_ENABLED
    Database config key: ogw_switch_credential_enabled
    Default: False
    """
    env_value = os.getenv("OGW_SWITCH_CREDENTIAL_ENABLED")
    if env_value:
        return env_value.lower() in ("true", "1", "yes", "on")

    return bool(await get_config_value("ogw_switch_credential_enabled", False))


async def get_oauth_proxy_url() -> str:
    """
    Get OAuth proxy URL setting.

    ç”¨äºGoogle OAuth2è®¤è¯ç„ä»£ç†URLă€‚

    Environment variable: OGW_OAUTH_URL
    Database config key: ogw_oauth_url
    Default: https://oauth2.googleapis.com
    """
    return str(
        await get_config_value(
            "ogw_oauth_url", "https://oauth2.googleapis.com", "OGW_OAUTH_URL"
        )
    )


async def get_googleapis_proxy_url() -> str:
    """
    Get Google APIs proxy URL setting.

    ç”¨äºGoogle APIsè°ƒç”¨ç„ä»£ç†URLă€‚

    Environment variable: OGW_GOOGLE_APIS_URL
    Database config key: ogw_google_apis_url
    Default: https://www.googleapis.com
    """
    return str(
        await get_config_value(
            "ogw_google_apis_url", "https://www.googleapis.com", "OGW_GOOGLE_APIS_URL"
        )
    )


async def get_resource_manager_api_url() -> str:
    """
    Get Google Cloud Resource Manager API URL setting.

    ç”¨äºGoogle Cloud Resource Manager APIç„URLă€‚

    Environment variable: OGW_RESOURCE_MANAGER_URL
    Database config key: ogw_resource_manager_url
    Default: https://cloudresourcemanager.googleapis.com
    """
    return str(
        await get_config_value(
            "ogw_resource_manager_url",
            "https://cloudresourcemanager.googleapis.com",
            "OGW_RESOURCE_MANAGER_URL",
        )
    )


async def get_service_usage_api_url() -> str:
    """
    Get Google Cloud Service Usage API URL setting.

    ç”¨äºGoogle Cloud Service Usage APIç„URLă€‚

    Environment variable: OGW_SERVICE_USAGE_URL
    Database config key: ogw_service_usage_url
    Default: https://serviceusage.googleapis.com
    """
    return str(
        await get_config_value(
            "ogw_service_usage_url", "https://serviceusage.googleapis.com", "OGW_SERVICE_USAGE_URL"
        )
    )


async def get_ogw_api_url() -> str:
    """
    Get Omni API URL setting.

    ç”¨äºGoogle Omni APIç„URLă€‚

    Environment variable: OGW_API_URL
    Database config key: ogw_api_url
    Default: https://daily-cloudcode-pa.googleapis.com
    """
    return str(
        await get_config_value(
            "ogw_api_url",
            "https://daily-cloudcode-pa.googleapis.com",
            "OGW_API_URL",
        )
    )


async def get_keepalive_url() -> str:
    """
    Get keep-alive URL setting.

    é…ç½®åä¿æ´»æœå¡ä¼å®æœŸå‘è¯¥URLå‘é€GETè¯·æ±‚ă€‚
    ç•™ç©ºè¡¨ç¤ºç¦ç”¨ä¿æ´»æœå¡ă€‚

    Environment variable: OGW_KEEPALIVE_URL
    Database config key: ogw_keepalive_url
    Default: "" (disabled)
    """
    return str(await get_config_value("ogw_keepalive_url", "", "OGW_KEEPALIVE_URL"))


async def get_keepalive_interval() -> int:
    """
    Get keep-alive interval in seconds.

    ä¿æ´»è¯·æ±‚å‘é€é—´é”ï¼ˆç§’ï¼‰ă€‚

    Environment variable: OGW_KEEPALIVE_INTERVAL
    Database config key: ogw_keepalive_interval
    Default: 60
    """
    env_value = os.getenv("OGW_KEEPALIVE_INTERVAL")
    if env_value:
        try:
            return int(env_value)
        except ValueError:
            pass

    return int(await get_config_value("ogw_keepalive_interval", 60))


async def get_api_key() -> str:
    """è·å– API Keyï¼Œå¦‚æœæ•°æ®åº“ä¸­æ²¡æœ‰ï¼Œåˆ™è‡ªå¨ç”Ÿæˆä¸€ä¸ªå¹¶ä¿å­˜"""
    from omni_gateway.storage_adapter import get_storage_adapter
    storage_adapter = await get_storage_adapter()
    key = await get_config_value("ogw_api_key")
    if not key:
        import secrets
        key = f"sk-ogw-{secrets.token_hex(20)}"
        await storage_adapter.set_config("ogw_api_key", key)
        # Update cache
        global _config_cache
        _config_cache["ogw_api_key"] = key
    return key
