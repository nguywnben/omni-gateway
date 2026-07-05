"""
Base Router - å…±ç”¨ç„è·¯ç”±åŸºç¡€åŸèƒ½
æä¾›æ¨¡å‹åˆ—è¡¨å¤„ç†ă€é€ç”¨å“åº”ç­‰å…±åŒåŸèƒ½
"""

from typing import List

from omni_gateway.models import Model, ModelList

def create_openai_model_list(
    model_ids: List[str],
    owned_by: str = "google"
) -> ModelList:
    """
    åˆ›å»ºOpenAIæ ¼å¼ç„æ¨¡å‹åˆ—è¡¨
    
    Args:
        model_ids: æ¨¡å‹IDåˆ—è¡¨
        owned_by: æ¨¡å‹æ‰€æœ‰è€…
        
    Returns:
        ModelListå¯¹è±¡
    """
    from datetime import datetime, timezone
    current_timestamp = int(datetime.now(timezone.utc).timestamp())
    
    models = [
        Model(
            id=model_id,
            object='model',
            created=current_timestamp,
            owned_by=owned_by
        )
        for model_id in model_ids
    ]
    
    return ModelList(data=models)


def create_gemini_model_list(
    model_ids: List[str],
    base_name_extractor=None
) -> dict:
    """
    åˆ›å»ºGeminiæ ¼å¼ç„æ¨¡å‹åˆ—è¡¨
    
    Args:
        model_ids: æ¨¡å‹IDåˆ—è¡¨
        base_name_extractor: å¯é€‰ç„åŸºç¡€æ¨¡å‹åæå–å‡½æ•°
        
    Returns:
        åŒ…å«æ¨¡å‹åˆ—è¡¨ç„å­—å…¸
    """
    gemini_models = []
    
    for model_id in model_ids:
        base_model = model_id
        if base_name_extractor:
            try:
                base_model = base_name_extractor(model_id)
            except Exception:
                pass
        
        model_info = {
            "name": f"models/{model_id}",
            "baseModelId": base_model,
            "version": "001",
            "displayName": model_id,
            "description": f"Gemini {base_model} model",
            "supportedGenerationMethods": ["generateContent", "streamGenerateContent"],
        }
        gemini_models.append(model_info)
    
    return {"models": gemini_models}