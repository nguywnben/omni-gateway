"""Provider-specific management console routes."""

from fastapi import APIRouter

from . import antigravity, catalog, google_ai_studio, openai, xai


def create_router() -> APIRouter:
    router = APIRouter()
    router.include_router(catalog.router)
    router.include_router(antigravity.router)
    router.include_router(google_ai_studio.router)
    router.include_router(xai.router)
    router.include_router(openai.router)
    return router


router = create_router()

__all__ = ["router"]
