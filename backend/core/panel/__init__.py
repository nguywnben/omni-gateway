from fastapi import APIRouter

from . import (
    auth,
    config_routes,
    credentials,
    environment_credentials,
    logs,
    model_pools,
    provider_settings,
    root,
    usage_routes,
    version,
)
from .utils import ConnectionManager, get_env_locked_keys, is_mobile_user_agent, validate_mode


def create_router() -> APIRouter:
    router = APIRouter()

    router.include_router(root.router)
    router.include_router(auth.router)
    router.include_router(environment_credentials.router)
    router.include_router(credentials.router, prefix="/api/credentials")
    router.include_router(
        credentials.router,
        prefix="/api/creds",
        include_in_schema=False,
    )
    router.include_router(config_routes.router)
    router.include_router(logs.router)
    router.include_router(version.router)
    router.include_router(usage_routes.router)
    router.include_router(provider_settings.router)
    router.include_router(model_pools.router)

    return router


router = create_router()

__all__ = [
    "router",
    "ConnectionManager",
    "is_mobile_user_agent",
    "validate_mode",
    "get_env_locked_keys",
]
