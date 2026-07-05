"""
Omni Model List Router - Handles model list requests
Omni æ¨¡å‹åˆ—è¡¨è·¯ç”± - å¤„ç†æ¨¡å‹åˆ—è¡¨è¯·æ±‚
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
from omni_gateway.utils import (
    get_base_model_from_feature_model,
    authenticate_flexible
)

# æœ¬åœ°æ¨¡å— - API
from omni_gateway.api.omni import fetch_available_models

# æœ¬åœ°æ¨¡å— - åŸºç¡€è·¯ç”±å·¥å…·
from omni_gateway.router.base_router import create_gemini_model_list, create_openai_model_list
from omni_gateway.models import model_to_dict
from log import log


# ==================== è·¯ç”±å™¨åˆå§‹åŒ– ====================

router = APIRouter()


# ==================== è¾…å©å‡½æ•° ====================

async def get_omni_models_with_features():
    """
    è·å– Omni æ¨¡å‹åˆ—è¡¨å¹¶æ·»å åŸèƒ½å‰ç¼€
    
    Returns:
        å¸¦æœ‰åŸèƒ½å‰ç¼€ç„æ¨¡å‹åˆ—è¡¨
    """
    # ä» API è·å–åŸºç¡€æ¨¡å‹åˆ—è¡¨
    base_models_data = await fetch_available_models()
    
    if not base_models_data:
        log.warning("[OMNI model list] Unable to fetch model list, empty list returned")
        return []
    
    # æå–æ¨¡å‹ ID
    base_model_ids = [model['id'] for model in base_models_data if 'id' in model]
    
    # æ·»å åŸèƒ½å‰ç¼€
    models = []
    for base_model in base_model_ids:
        # åŸºç¡€æ¨¡å‹
        models.append(base_model)
        
        # å‡æµå¼æ¨¡å‹ (å‰ç¼€æ ¼å¼)
        models.append(f"å‡æµå¼/{base_model}")
        
        # æµå¼æ—æˆªæ–­æ¨¡å‹ (ä»…åœ¨æµå¼ä¼ è¾“æ—¶æœ‰æ•ˆï¼Œå‰ç¼€æ ¼å¼)
        models.append(f"æµå¼æ—æˆªæ–­/{base_model}")
    
    log.info(f"[OMNI model list] {len(models)} models generated (with feature prefix)")
    return models


# ==================== API è·¯ç”± ====================

@router.get("/ogw/v1beta/models")
async def list_gemini_models(token: str = Depends(authenticate_flexible)):
    """
    è¿”å› Gemini æ ¼å¼ç„æ¨¡å‹åˆ—è¡¨
    
    ä» omni_gateway.api.omni.fetch_available_models å¨æ€è·å–æ¨¡å‹åˆ—è¡¨
    å¹¶æ·»å å‡æµå¼å’Œæµå¼æ—æˆªæ–­å‰ç¼€
    """
    models = await get_omni_models_with_features()
    log.info("[OMNI model list] Returns Gemini format")
    return JSONResponse(content=create_gemini_model_list(
        models,
        base_name_extractor=get_base_model_from_feature_model
    ))


@router.get("/ogw/v1/models")
async def list_openai_models(token: str = Depends(authenticate_flexible)):
    """
    è¿”å› OpenAI æ ¼å¼ç„æ¨¡å‹åˆ—è¡¨
    
    ä» omni_gateway.api.omni.fetch_available_models å¨æ€è·å–æ¨¡å‹åˆ—è¡¨
    å¹¶æ·»å å‡æµå¼å’Œæµå¼æ—æˆªæ–­å‰ç¼€
    """
    models = await get_omni_models_with_features()
    log.info("[OMNI model list] Returns OpenAI format")
    model_list = create_openai_model_list(models, owned_by="google")
    return JSONResponse(content={
        "object": "list",
        "data": [model_to_dict(model) for model in model_list.data]
    })
