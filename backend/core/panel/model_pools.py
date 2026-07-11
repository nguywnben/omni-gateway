"""Management API for the dynamic model catalog and virtual model pool."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from core.model_pool import (
    DEFAULT_VIRTUAL_MODEL_ALIAS,
    ModelPoolError,
    get_virtual_model_pool,
    model_catalog_service,
    save_virtual_model_pool,
)
from core.models import VirtualModelPoolUpdateRequest
from core.utils import verify_panel_token
from log import log


router = APIRouter(tags=["model-pools"])


@router.get("/api/model-catalog")
async def get_model_catalog(
    refresh: bool = Query(default=False),
    token: str = Depends(verify_panel_token),
):
    """Return dynamic provider models and the default virtual-model policy."""
    try:
        entries = await model_catalog_service.get_catalog(force_refresh=refresh)
        pool = await get_virtual_model_pool()
        catalog = [entry.to_dict() for entry in entries]
        catalog_ids = {entry["model_id"] for entry in catalog}
        for model_id in pool["selected_models"]:
            if model_id not in catalog_ids:
                catalog.append(
                    {
                        "model_id": model_id,
                        "providers": [],
                        "available": False,
                    }
                )
        catalog.sort(key=lambda entry: entry["model_id"])
        return JSONResponse(
            content={
                "catalog": catalog,
                "pool": pool,
                "summary": {
                    "available_models": sum(bool(entry["available"]) for entry in catalog),
                    "selected_models": len(pool["selected_models"]),
                    "unavailable_selected_models": sum(
                        model_id not in catalog_ids
                        for model_id in pool["selected_models"]
                    ),
                },
            }
        )
    except Exception as exc:
        log.error(f"Failed to load the model catalog: {exc}")
        raise HTTPException(
            status_code=502,
            detail="The provider model catalog could not be loaded.",
        ) from exc


@router.get("/api/model-pools")
async def list_model_pools(token: str = Depends(verify_panel_token)):
    """Return configured virtual model pools."""
    return JSONResponse(content={"model_pools": [await get_virtual_model_pool()]})


@router.put(f"/api/model-pools/{DEFAULT_VIRTUAL_MODEL_ALIAS}")
async def update_default_model_pool(
    request: VirtualModelPoolUpdateRequest,
    token: str = Depends(verify_panel_token),
):
    """Replace the ordered model members of the default virtual model."""
    try:
        pool = await save_virtual_model_pool(
            request.selected_models,
            enabled=request.enabled,
        )
        return JSONResponse(
            content={
                "message": f'Virtual model "{DEFAULT_VIRTUAL_MODEL_ALIAS}" updated.',
                "pool": pool,
            }
        )
    except ModelPoolError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        log.error(f"Failed to update the virtual model pool: {exc}")
        raise HTTPException(
            status_code=500,
            detail="The virtual model configuration could not be saved.",
        ) from exc
