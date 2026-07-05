"""
Code Assist Model List Router - Handles model list requests
Code Assist æ¨¡å‹åˆ—è¡¨è·¯ç”± - å¤„ç†æ¨¡å‹åˆ—è¡¨è¯·æ±‚
"""

import sys
from pathlib import Path

# æ·»å é¡¹ç›®æ ¹ç›®å½•åˆ°Pythonè·¯å¾„
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ç¬¬ä¸‰æ–¹åº“
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

# æœ¬åœ°æ¨¡å— - å·¥å…·å’Œè®¤è¯
from omni_gateway.utils import authenticate_flexible

VERTEX_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.5-flash",
]

# æœ¬åœ°æ¨¡å— - åŸºç¡€è·¯ç”±å·¥å…·
from omni_gateway.router.base_router import create_gemini_model_list, create_openai_model_list
from omni_gateway.models import model_to_dict
from log import log


# ==================== è·¯ç”±å™¨åˆå§‹åŒ– ====================

router = APIRouter()


# ==================== API è·¯ç”± ====================

@router.get("/ogw/vertex/v1beta/models")
async def list_gemini_models(token: str = Depends(authenticate_flexible)):
    log.info("[VERTEX MODEL LIST] Returning Gemini format")
    return JSONResponse(content=create_gemini_model_list(
        VERTEX_MODELS,
        base_name_extractor=lambda m: m
    ))


@router.get("/ogw/vertex/v1/models")
async def list_openai_models(token: str = Depends(authenticate_flexible)):
    log.info("[VERTEX MODEL LIST] Returning OpenAI format")
    model_list = create_openai_model_list(VERTEX_MODELS, owned_by="google")
    return JSONResponse(content={
        "object": "list",
        "data": [model_to_dict(model) for model in model_list.data]
    })
