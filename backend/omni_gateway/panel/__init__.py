"""
Panelæ¨¡å— - æ•´åˆæ‰€æœ‰æ§åˆ¶é¢æ¿è·¯ç”±
"""

from fastapi import APIRouter

from . import auth, creds, config_routes, logs, version, root, usage_routes


def create_router() -> APIRouter:
    """åˆ›å»ºå¹¶è¿”å›æ•´åˆæ‰€æœ‰å­è·¯ç”±ç„ä¸»è·¯ç”±å™¨"""
    router = APIRouter()

    # åŒ…å«æ‰€æœ‰å­è·¯ç”±
    router.include_router(root.router)
    router.include_router(auth.router)
    router.include_router(creds.router)
    router.include_router(config_routes.router)
    router.include_router(logs.router)
    router.include_router(version.router)
    router.include_router(usage_routes.router)

    return router


# å¯¼å‡ºä¸»è·¯ç”±å™¨
router = create_router()

# å¯¼å‡ºå¸¸ç”¨å·¥å…·
from .utils import ConnectionManager, is_mobile_user_agent, validate_mode, get_env_locked_keys

__all__ = [
    "router",
    "ConnectionManager",
    "is_mobile_user_agent",
    "validate_mode",
    "get_env_locked_keys",
]
