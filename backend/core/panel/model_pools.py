"""Management API for the dynamic model catalog and virtual model pool."""

from core.model_blacklist import (
    clear_model_blacklist,
    get_model_blacklist,
    remove_model_blacklist_entry,
)
from core.model_pool import (
    DEFAULT_VIRTUAL_MODEL_ALIAS,
    ModelPoolError,
    get_virtual_model_pool,
    model_catalog_service,
    save_virtual_model_pool,
)
from core.models import VirtualModelPoolUpdateRequest
from core.utils import verify_panel_token
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse
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
        blacklist = await get_model_blacklist()
        blacklisted_pairs = {(entry["provider_id"], entry["model_id"]) for entry in blacklist}
        catalog = []
        for entry in entries:
            value = entry.to_dict()
            value["blacklisted_providers"] = [
                provider_id
                for provider_id in value["providers"]
                if (provider_id, value["model_id"]) in blacklisted_pairs
            ]
            value["routable_providers"] = [
                provider_id
                for provider_id in value["providers"]
                if (provider_id, value["model_id"]) not in blacklisted_pairs
            ]
            value["available"] = bool(value["routable_providers"])
            catalog.append(value)
        catalog_ids = {entry["model_id"] for entry in catalog}
        for model_id in pool["selected_models"]:
            if model_id not in catalog_ids:
                catalog.append(
                    {
                        "model_id": model_id,
                        "providers": [],
                        "routable_providers": [],
                        "blacklisted_providers": [],
                        "available": False,
                    }
                )
        catalog.sort(key=lambda entry: entry["model_id"])
        catalog_by_id = {entry["model_id"]: entry for entry in catalog}
        return JSONResponse(
            content={
                "catalog": catalog,
                "pool": pool,
                "blacklist": blacklist,
                "summary": {
                    "available_models": sum(bool(entry["available"]) for entry in catalog),
                    "selected_models": len(pool["selected_models"]),
                    "unavailable_selected_models": sum(
                        not catalog_by_id.get(model_id, {}).get("available", False)
                        for model_id in pool["selected_models"]
                    ),
                    "blacklisted_routes": len(blacklist),
                },
            }
        )
    except Exception as exc:
        log.error(f"Failed to load the model catalog: {exc}")
        raise HTTPException(
            status_code=502,
            detail="The provider model catalog could not be loaded.",
        ) from exc


@router.get("/api/model-blacklist")
async def get_model_blacklist_entries(token: str = Depends(verify_panel_token)):
    """Return model routes excluded by observed upstream 404 responses."""
    entries = await get_model_blacklist()
    return JSONResponse(content={"blacklist": entries, "count": len(entries)})


@router.delete("/api/model-blacklist/{provider_id}/models/{model_id:path}")
async def delete_model_blacklist_entry(
    provider_id: str,
    model_id: str = Path(..., description="Provider model ID"),
    credential_name: str = Query(default=""),
    token: str = Depends(verify_panel_token),
):
    """Restore one credential-model route, or every matching provider route."""
    try:
        if credential_name:
            removed = await remove_model_blacklist_entry(
                provider_id,
                model_id,
                credential_name=credential_name,
            )
        else:
            removed = await remove_model_blacklist_entry(provider_id, model_id)
    except (ModelPoolError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return JSONResponse(
        content={
            "removed": removed,
            "message": (
                "Model route removed from blacklist."
                if removed
                else "Model route is not blacklisted."
            ),
        }
    )


@router.delete("/api/model-blacklist")
async def delete_model_blacklist(token: str = Depends(verify_panel_token)):
    """Restore every provider-model route currently in the blacklist."""
    removed_count = await clear_model_blacklist()
    return JSONResponse(
        content={
            "removed_count": removed_count,
            "message": (
                "Model blacklist cleared." if removed_count else "Model blacklist is already empty."
            ),
        }
    )


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
