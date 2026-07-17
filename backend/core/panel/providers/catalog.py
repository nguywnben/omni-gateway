"""Provider catalog routes for the management console."""

from core.provider_registry import list_provider_capabilities
from core.utils import verify_panel_token
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

router = APIRouter(tags=["provider-catalog"])


@router.get("/api/providers")
async def get_provider_catalog(token: str = Depends(verify_panel_token)):
    """Return provider capabilities without exposing stored credentials."""
    return JSONResponse(content={"providers": list_provider_capabilities()})
