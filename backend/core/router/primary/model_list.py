"""Internal implementation detail."""

import sys
from pathlib import Path


project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse


from core.utils import (
    get_base_model_from_feature_model,
    authenticate_flexible
)


from core.router.base_router import create_gemini_model_list, create_openai_model_list
from core.models import model_to_dict
from core.model_pool import get_public_virtual_models, model_catalog_service
from log import log




router = APIRouter()




async def get_primary_models_with_features():
    """Internal implementation detail."""

    catalog_entries = await model_catalog_service.get_catalog()
    if not catalog_entries:
        log.warning("[provider model list] No concrete provider models are currently available")
    base_model_ids = [entry.model_id for entry in catalog_entries]


    models = []
    for base_model in base_model_ids:

        models.append(base_model)


        models.append(f"fake-streaming/{base_model}")


        models.append(f"streaming-anti-truncation/{base_model}")

    for virtual_model in await get_public_virtual_models():
        if virtual_model not in models:
            models.append(virtual_model)

    log.info(f"[provider model list] {len(models)} models generated (with feature prefix)")
    return models




@router.get("/v1beta/models")
async def list_gemini_models(token: str = Depends(authenticate_flexible)):
    """Internal implementation detail."""
    models = await get_primary_models_with_features()
    log.info("[provider model list] Returns Gemini format")
    return JSONResponse(content=create_gemini_model_list(
        models,
        base_name_extractor=get_base_model_from_feature_model
    ))


@router.get("/v1/models")
async def list_openai_models(token: str = Depends(authenticate_flexible)):
    """Internal implementation detail."""
    models = await get_primary_models_with_features()
    log.info("[provider model list] Returns OpenAI format")
    model_list = create_openai_model_list(models, owned_by="provider")
    return JSONResponse(content={
        "object": "list",
        "data": [model_to_dict(model) for model in model_list.data]
    })
