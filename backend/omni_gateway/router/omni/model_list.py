"""Internal implementation detail."""

import sys
from pathlib import Path


project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse


from omni_gateway.utils import (
    get_base_model_from_feature_model,
    authenticate_flexible
)


from omni_gateway.api.omni import fetch_available_models


from omni_gateway.router.base_router import create_gemini_model_list, create_openai_model_list
from omni_gateway.models import model_to_dict
from log import log




router = APIRouter()




async def get_omni_models_with_features():
    """Internal implementation detail."""

    base_models_data = await fetch_available_models()

    if not base_models_data:
        log.warning("[OMNI model list] Unable to fetch model list, empty list returned")
        return []


    base_model_ids = [model['id'] for model in base_models_data if 'id' in model]


    models = []
    for base_model in base_model_ids:

        models.append(base_model)


        models.append(f"fake-streaming/{base_model}")


        models.append(f"streaming-anti-truncation/{base_model}")

    log.info(f"[OMNI model list] {len(models)} models generated (with feature prefix)")
    return models




@router.get("/ogw/v1beta/models")
async def list_gemini_models(token: str = Depends(authenticate_flexible)):
    """Internal implementation detail."""
    models = await get_omni_models_with_features()
    log.info("[OMNI model list] Returns Gemini format")
    return JSONResponse(content=create_gemini_model_list(
        models,
        base_name_extractor=get_base_model_from_feature_model
    ))


@router.get("/ogw/v1/models")
async def list_openai_models(token: str = Depends(authenticate_flexible)):
    """Internal implementation detail."""
    models = await get_omni_models_with_features()
    log.info("[OMNI model list] Returns OpenAI format")
    model_list = create_openai_model_list(models, owned_by="google")
    return JSONResponse(content={
        "object": "list",
        "data": [model_to_dict(model) for model in model_list.data]
    })
