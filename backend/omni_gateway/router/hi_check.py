"""
ç»Ÿä¸€ç„å¥åº·æ£€æŸ¥ï¼ˆHiæ¶ˆæ¯ï¼‰å¤„ç†æ¨¡å—

æä¾›å¯¹OpenAIă€Geminiå’ŒAnthropicæ ¼å¼ç„Hiæ¶ˆæ¯ç„è§£æå’Œå“åº”
"""
import time
from typing import Any, Dict, List


# ==================== Hiæ¶ˆæ¯æ£€æµ‹ ====================

def is_health_check_request(request_data: dict, format: str = "openai") -> bool:
    """
    æ£€æŸ¥æ˜¯å¦æ˜¯å¥åº·æ£€æŸ¥è¯·æ±‚ï¼ˆHiæ¶ˆæ¯ï¼‰
    
    Args:
        request_data: è¯·æ±‚æ•°æ®
        format: è¯·æ±‚æ ¼å¼ï¼ˆ"openai"ă€"gemini" æˆ– "anthropic"ï¼‰
        
    Returns:
        æ˜¯å¦æ˜¯å¥åº·æ£€æŸ¥è¯·æ±‚
    """
    if format == "openai":
        # OpenAIæ ¼å¼å¥åº·æ£€æŸ¥: {"messages": [{"role": "user", "content": "Hi"}]}
        messages = request_data.get("messages", [])
        if len(messages) == 1:
            msg = messages[0]
            if msg.get("role") == "user" and msg.get("content") == "Hi":
                return True
                
    elif format == "gemini":
        # Geminiæ ¼å¼å¥åº·æ£€æŸ¥: {"contents": [{"role": "user", "parts": [{"text": "Hi"}]}]}
        contents = request_data.get("contents", [])
        if len(contents) == 1:
            content = contents[0]
            if (content.get("role") == "user" and 
                content.get("parts", [{}])[0].get("text") == "Hi"):
                return True
    
    elif format == "anthropic":
        # Anthropicæ ¼å¼å¥åº·æ£€æŸ¥: {"messages": [{"role": "user", "content": "Hi"}]}
        messages = request_data.get("messages", [])
        if (len(messages) == 1 
            and messages[0].get("role") == "user" 
            and messages[0].get("content") == "Hi"):
            return True
    
    return False


def is_health_check_message(messages: List[Dict[str, Any]]) -> bool:
    """
    ç›´æ¥æ£€æŸ¥æ¶ˆæ¯åˆ—è¡¨æ˜¯å¦ä¸ºå¥åº·æ£€æŸ¥æ¶ˆæ¯ï¼ˆAnthropicä¸“ç”¨ï¼‰
    
    è¿™æ˜¯ä¸€ä¸ªä¾¿æ·å‡½æ•°ï¼Œç”¨äºå·²ç»æå–å‡ºæ¶ˆæ¯åˆ—è¡¨ç„åœºæ™¯ă€‚
    
    Args:
        messages: æ¶ˆæ¯åˆ—è¡¨
        
    Returns:
        æ˜¯å¦ä¸ºå¥åº·æ£€æŸ¥æ¶ˆæ¯
    """
    return (
        len(messages) == 1 
        and messages[0].get("role") == "user" 
        and messages[0].get("content") == "Hi"
    )


# ==================== Hiæ¶ˆæ¯å“åº”ç”Ÿæˆ ====================

def create_health_check_response(format: str = "openai", **kwargs) -> dict:
    """
    åˆ›å»ºå¥åº·æ£€æŸ¥å“åº”
    
    Args:
        format: å“åº”æ ¼å¼ï¼ˆ"openai"ă€"gemini" æˆ– "anthropic"ï¼‰
        **kwargs: æ ¼å¼ç‰¹å®ç„é¢å¤–å‚æ•°
            - model: æ¨¡å‹åç§°ï¼ˆanthropicæ ¼å¼éœ€è¦ï¼‰
            - message_id: æ¶ˆæ¯IDï¼ˆanthropicæ ¼å¼éœ€è¦ï¼‰
        
    Returns:
        å¥åº·æ£€æŸ¥å“åº”å­—å…¸
    """
    if format == "openai":
        # OpenAIæ ¼å¼å“åº”
        return {
            "id": "healthcheck",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "healthcheck",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "API is working"
                },
                "finish_reason": "stop"
            }]
        }
    
    elif format == "gemini":
        # Geminiæ ¼å¼å“åº”
        return {
            "candidates": [{
                "content": {
                    "parts": [{"text": "omni-gatewayå·¥ä½œä¸­"}],
                    "role": "model"
                },
                "finishReason": "STOP",
                "index": 0,
            }]
        }
    
    elif format == "anthropic":
        # Anthropicæ ¼å¼å“åº”
        model = kwargs.get("model", "claude-unknown")
        message_id = kwargs.get("message_id", "msg_healthcheck")
        return {
            "id": message_id,
            "type": "message",
            "role": "assistant",
            "model": str(model),
            "content": [{"type": "text", "text": "omni Anthropic Messages æ­£å¸¸å·¥ä½œä¸­"}],
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }
    
    # æœªçŸ¥æ ¼å¼è¿”å›ç©ºå­—å…¸
    return {}
