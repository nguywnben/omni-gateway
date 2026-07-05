from typing import Any, Dict

from omni_gateway.converter.thoughtSignature_fix import (
    is_internal_placeholder_text,
    is_skip_thought_signature_placeholder,
)


def extract_content_and_reasoning(parts: list) -> tuple:
    """ä»Geminiå“åº”éƒ¨ä»¶ä¸­æå–å†…å®¹å’Œæ¨ç†å†…å®¹

    Args:
        parts: Gemini å“åº”ä¸­ç„ parts åˆ—è¡¨

    Returns:
        (content, reasoning_content, images): æ–‡æœ¬å†…å®¹ă€æ¨ç†å†…å®¹å’Œå›¾ç‰‡æ•°æ®ç„å…ƒç»„
        - content: æ–‡æœ¬å†…å®¹å­—ç¬¦ä¸²
        - reasoning_content: æ¨ç†å†…å®¹å­—ç¬¦ä¸²
        - images: å›¾ç‰‡æ•°æ®åˆ—è¡¨,æ¯ä¸ªå…ƒç´ æ ¼å¼ä¸º:
          {
              "type": "image_url",
              "image_url": {
                  "url": "data:{mime_type};base64,{base64_data}"
              }
          }
    """
    content = ""
    reasoning_content = ""
    images = []

    for part in parts:
        if is_skip_thought_signature_placeholder(part):
            continue

        # æå–æ–‡æœ¬å†…å®¹
        text = part.get("text", "")
        if is_internal_placeholder_text(text):
            continue
        if text:
            if part.get("thought", False):
                reasoning_content += text
            else:
                content += text

        # æå–å›¾ç‰‡æ•°æ®
        if "inlineData" in part:
            inline_data = part["inlineData"]
            mime_type = inline_data.get("mimeType", "image/png")
            base64_data = inline_data.get("data", "")
            images.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{base64_data}"
                }
            })

    return content, reasoning_content, images


async def merge_system_messages(request_body: Dict[str, Any]) -> Dict[str, Any]:
    """
    æ ¹æ®å…¼å®¹æ€§æ¨¡å¼å¤„ç†è¯·æ±‚ä½“ä¸­ç„systemæ¶ˆæ¯

    - å…¼å®¹æ€§æ¨¡å¼å…³é—­ï¼ˆFalseï¼‰ï¼å°†è¿ç»­ç„systemæ¶ˆæ¯åˆå¹¶ä¸ºsystemInstruction
    - å…¼å®¹æ€§æ¨¡å¼å¼€å¯ï¼ˆTrueï¼‰ï¼å°†æ‰€æœ‰systemæ¶ˆæ¯è½¬æ¢ä¸ºuseræ¶ˆæ¯

    Args:
        request_body: OpenAIæˆ–Claudeæ ¼å¼ç„è¯·æ±‚ä½“ï¼ŒåŒ…å«messageså­—æ®µ

    Returns:
        å¤„ç†åç„è¯·æ±‚ä½“

    Example (å…¼å®¹æ€§æ¨¡å¼å…³é—­):
        è¾“å…¥:
        {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "system", "content": "You are an expert in Python."},
                {"role": "user", "content": "Hello"}
            ]
        }

        è¾“å‡º:
        {
            "systemInstruction": {
                "parts": [
                    {"text": "You are a helpful assistant."},
                    {"text": "You are an expert in Python."}
                ]
            },
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }

    Example (å…¼å®¹æ€§æ¨¡å¼å¼€å¯):
        è¾“å…¥:
        {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
        }

        è¾“å‡º:
        {
            "messages": [
                {"role": "user", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello"}
            ]
        }
    
    Example (Anthropicæ ¼å¼ï¼Œå…¼å®¹æ€§æ¨¡å¼å…³é—­):
        è¾“å…¥:
        {
            "system": "You are a helpful assistant.",
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }

        è¾“å‡º:
        {
            "systemInstruction": {
                "parts": [
                    {"text": "You are a helpful assistant."}
                ]
            },
            "messages": [
                {"role": "user", "content": "Hello"}
            ]
        }
    """
    from config import get_compatibility_mode_enabled

    compatibility_mode = await get_compatibility_mode_enabled()
    
    # å¤„ç† Anthropic æ ¼å¼ç„é¡¶å±‚ system å‚æ•°
    # Anthropic API è§„èŒƒ: system æ˜¯é¡¶å±‚å‚æ•°ï¼Œä¸åœ¨ messages ä¸­
    system_content = request_body.get("system")
    if system_content:
        system_parts = []
        
        if isinstance(system_content, str):
            if system_content.strip():
                system_parts.append({"text": system_content})
        elif isinstance(system_content, list):
            # system å¯ä»¥æ˜¯åŒ…å«å¤ä¸ªå—ç„åˆ—è¡¨
            for item in system_content:
                if isinstance(item, dict):
                    if item.get("type") == "text" and item.get("text", "").strip():
                        system_parts.append({"text": item["text"]})
                elif isinstance(item, str) and item.strip():
                    system_parts.append({"text": item})
        
        if system_parts:
            if compatibility_mode:
                # å…¼å®¹æ€§æ¨¡å¼ï¼å°† system è½¬æ¢ä¸º user æ¶ˆæ¯æ’å…¥åˆ° messages å¼€å¤´
                user_system_message = {
                    "role": "user",
                    "content": system_content if isinstance(system_content, str) else 
                              "\n".join(part["text"] for part in system_parts)
                }
                messages = request_body.get("messages", [])
                request_body = request_body.copy()
                request_body["messages"] = [user_system_message] + messages
            else:
                # éå…¼å®¹æ€§æ¨¡å¼ï¼æ·»å ä¸º systemInstruction
                request_body = request_body.copy()
                request_body["systemInstruction"] = {"parts": system_parts}

    messages = request_body.get("messages", [])
    if not messages:
        return request_body

    compatibility_mode = await get_compatibility_mode_enabled()

    if compatibility_mode:
        # å…¼å®¹æ€§æ¨¡å¼å¼€å¯ï¼å°†æ‰€æœ‰systemæ¶ˆæ¯è½¬æ¢ä¸ºuseræ¶ˆæ¯
        converted_messages = []
        for message in messages:
            if message.get("role") == "system":
                # åˆ›å»ºæ–°ç„æ¶ˆæ¯å¯¹è±¡ï¼Œå°†roleæ”¹ä¸ºuser
                converted_message = message.copy()
                converted_message["role"] = "user"
                converted_messages.append(converted_message)
            else:
                converted_messages.append(message)

        result = request_body.copy()
        result["messages"] = converted_messages
        return result
    else:
        # å…¼å®¹æ€§æ¨¡å¼å…³é—­ï¼æå–è¿ç»­ç„systemæ¶ˆæ¯åˆå¹¶ä¸ºsystemInstruction
        system_parts = []
        
        # å¦‚æœå·²ç»ä»é¡¶å±‚ system å‚æ•°åˆ›å»ºäº† systemInstructionï¼Œè·å–ç°æœ‰ç„ parts
        if "systemInstruction" in request_body:
            existing_instruction = request_body.get("systemInstruction", {})
            if isinstance(existing_instruction, dict):
                system_parts = existing_instruction.get("parts", []).copy()
        
        remaining_messages = []
        collecting_system = True

        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")

            if role == "system" and collecting_system:
                # æå–systemæ¶ˆæ¯ç„æ–‡æœ¬å†…å®¹
                if isinstance(content, str):
                    if content.strip():
                        system_parts.append({"text": content})
                elif isinstance(content, list):
                    # å¤„ç†åˆ—è¡¨æ ¼å¼ç„content
                    for item in content:
                        if isinstance(item, dict):
                            if item.get("type") == "text" and item.get("text", "").strip():
                                system_parts.append({"text": item["text"]})
                        elif isinstance(item, str) and item.strip():
                            system_parts.append({"text": item})
            else:
                # é‡åˆ°ésystemæ¶ˆæ¯ï¼Œåœæ­¢æ”¶é›†
                collecting_system = False
                if role == "system":
                    # å°†åç»­ç„systemæ¶ˆæ¯è½¬æ¢ä¸ºuseræ¶ˆæ¯
                    converted_message = message.copy()
                    converted_message["role"] = "user"
                    remaining_messages.append(converted_message)
                else:
                    remaining_messages.append(message)

        # å¦‚æœæ²¡æœ‰æ‰¾åˆ°ä»»ä½•systemæ¶ˆæ¯ï¼ˆåŒ…æ‹¬é¡¶å±‚å‚æ•°å’Œmessagesä¸­ç„ï¼‰ï¼Œè¿”å›åŸå§‹è¯·æ±‚ä½“
        if not system_parts:
            return request_body

        # æ„å»ºæ–°ç„è¯·æ±‚ä½“
        result = request_body.copy()

        # æ·»å æˆ–æ›´æ–°systemInstruction
        result["systemInstruction"] = {"parts": system_parts}

        # æ›´æ–°messagesåˆ—è¡¨ï¼ˆç§»é™¤å·²å¤„ç†ç„systemæ¶ˆæ¯ï¼‰
        result["messages"] = remaining_messages

        return result
