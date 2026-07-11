"""Internal implementation detail."""

from fastapi import APIRouter

from . import auth, creds, config_routes, logs, version, root, usage_routes, provider_settings, model_pools


def create_router() -> APIRouter:
    """Internal implementation detail."""
    router = APIRouter()


    router.include_router(root.router)
    router.include_router(auth.router)
    router.include_router(creds.router)
    router.include_router(config_routes.router)
    router.include_router(logs.router)
    router.include_router(version.router)
    router.include_router(usage_routes.router)
    router.include_router(provider_settings.router)
    router.include_router(model_pools.router)

    return router



router = create_router()


from .utils import ConnectionManager, is_mobile_user_agent, validate_mode, get_env_locked_keys

__all__ = [
    "router",
    "ConnectionManager",
    "is_mobile_user_agent",
    "validate_mode",
    "get_env_locked_keys",
]
