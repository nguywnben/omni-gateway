"""Internal implementation detail."""

import sys
from pathlib import Path


project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse


from core.utils import authenticate_flexible

VERTEX_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.5-flash",
]


from core.router.base_router import create_gemini_model_list, create_openai_model_list
from core.models import model_to_dict
from log import log




router = APIRouter()




@router.get("/vertex/v1beta/models")
async def list_gemini_models(token: str = Depends(authenticate_flexible)):
    log.info("[VERTEX MODEL LIST] Returning Gemini format")
    return JSONResponse(content=create_gemini_model_list(
        VERTEX_MODELS,
        base_name_extractor=lambda m: m
    ))


@router.get("/vertex/v1/models")
async def list_openai_models(token: str = Depends(authenticate_flexible)):
    log.info("[VERTEX MODEL LIST] Returning OpenAI format")
    model_list = create_openai_model_list(VERTEX_MODELS, owned_by="google")
    return JSONResponse(content={
        "object": "list",
        "data": [model_to_dict(model) for model in model_list.data]
    })
