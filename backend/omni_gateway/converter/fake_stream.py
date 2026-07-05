from typing import Any, Dict, List, Tuple
import json
from omni_gateway.converter.utils import extract_content_and_reasoning
from log import log
from omni_gateway.converter.openai2gemini import _convert_usage_metadata

def safe_get_nested(obj: Any, *keys: str, default: Any = None) -> Any:
    """å®‰å…¨è·å–åµŒå¥—å­—å…¸å€¼
    
    Args:
        obj: å­—å…¸å¯¹è±¡
        *keys: åµŒå¥—é”®è·¯å¾„
        default: é»˜è®¤å€¼
    
    Returns:
        è·å–åˆ°ç„å€¼æˆ–é»˜è®¤å€¼
    """
    for key in keys:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(key, default)
        if obj is default:
            return default
    return obj

def parse_response_for_fake_stream(response_data: Dict[str, Any]) -> tuple:
    """ä»å®Œæ•´å“åº”ä¸­æå–å†…å®¹å’Œæ¨ç†å†…å®¹(ç”¨äºå‡æµå¼)

    Args:
        response_data: Gemini API å“åº”æ•°æ®

    Returns:
        (content, reasoning_content, finish_reason, images): å†…å®¹ă€æ¨ç†å†…å®¹ă€ç»“æŸåŸå› å’Œå›¾ç‰‡æ•°æ®ç„å…ƒç»„
    """
    import json

    # å¤„ç†Code Assistç„responseåŒ…è£…æ ¼å¼
    if "response" in response_data and "candidates" not in response_data:
        log.debug(f"[FAKE_STREAM] Unwrapping response field")
        response_data = response_data["response"]

    candidates = response_data.get("candidates", [])
    log.debug(f"[FAKE_STREAM] Found {len(candidates)} candidates")
    if not candidates:
        return "", "", "STOP", []

    candidate = candidates[0]
    finish_reason = candidate.get("finishReason", "STOP")
    parts = safe_get_nested(candidate, "content", "parts", default=[])
    log.debug(f"[FAKE_STREAM] Extracted {len(parts)} parts: {json.dumps(parts, ensure_ascii=False)}")
    content, reasoning_content, images = extract_content_and_reasoning(parts)
    log.debug(f"[FAKE_STREAM] Content length: {len(content)}, Reasoning length: {len(reasoning_content)}, Images count: {len(images)}")

    return content, reasoning_content, finish_reason, images

def extract_fake_stream_content(response: Any) -> Tuple[str, str, Dict[str, int]]:
    """
    ä» Gemini éæµå¼å“åº”ä¸­æå–å†…å®¹ï¼Œç”¨äºå‡æµå¼å¤„ç†
    
    Args:
        response: Gemini API å“åº”å¯¹è±¡
    
    Returns:
        (content, reasoning_content, usage) å…ƒç»„
    """
    from omni_gateway.converter.utils import extract_content_and_reasoning
    
    # è§£æå“åº”ä½“
    if hasattr(response, "body"):
        body_str = (
            response.body.decode()
            if isinstance(response.body, bytes)
            else str(response.body)
        )
    elif hasattr(response, "content"):
        body_str = (
            response.content.decode()
            if isinstance(response.content, bytes)
            else str(response.content)
        )
    else:
        body_str = str(response)

    try:
        response_data = json.loads(body_str)

        # Code Assist è¿”å›ç„æ ¼å¼æ˜¯ {"response": {...}, "traceId": "..."}
        # éœ€è¦å…ˆæå– response å­—æ®µ
        if "response" in response_data:
            gemini_response = response_data["response"]
        else:
            gemini_response = response_data

        # ä»Geminiå“åº”ä¸­æå–å†…å®¹ï¼Œä½¿ç”¨æ€ç»´é“¾åˆ†ç¦»é€»è¾‘
        content = ""
        reasoning_content = ""
        images = []
        if "candidates" in gemini_response and gemini_response["candidates"]:
            # Geminiæ ¼å¼å“åº” - ä½¿ç”¨æ€ç»´é“¾åˆ†ç¦»
            candidate = gemini_response["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                content, reasoning_content, images = extract_content_and_reasoning(parts)
        elif "choices" in gemini_response and gemini_response["choices"]:
            # OpenAIæ ¼å¼å“åº”
            content = gemini_response["choices"][0].get("message", {}).get("content", "")

        # å¦‚æœæ²¡æœ‰æ­£å¸¸å†…å®¹ä½†æœ‰æ€ç»´å†…å®¹ï¼Œç»™å‡ºè­¦å‘
        if not content and reasoning_content:
            log.warning("Fake stream response contains only thinking content")
            content = "[æ¨¡å‹æ­£åœ¨æ€è€ƒä¸­ï¼Œè¯·ç¨åå†è¯•æˆ–é‡æ–°æé—®]"
        
        # å¦‚æœå®Œå…¨æ²¡æœ‰å†…å®¹ï¼Œæä¾›é»˜è®¤å›å¤
        if not content:
            log.warning(f"No content found in response: {gemini_response}")
            content = "[å“åº”ä¸ºç©ºï¼Œè¯·é‡æ–°å°è¯•]"

        # è½¬æ¢usageMetadataä¸ºOpenAIæ ¼å¼
        usage = _convert_usage_metadata(gemini_response.get("usageMetadata"))
        
        return content, reasoning_content, usage

    except json.JSONDecodeError:
        # å¦‚æœä¸æ˜¯JSONï¼Œç›´æ¥è¿”å›åŸå§‹æ–‡æœ¬
        return body_str, "", None

def _build_candidate(parts: List[Dict[str, Any]], finish_reason: str = "STOP") -> Dict[str, Any]:
    """æ„å»ºæ ‡å‡†å€™é€‰å“åº”ç»“æ„
    
    Args:
        parts: parts åˆ—è¡¨
        finish_reason: ç»“æŸåŸå› 
    
    Returns:
        å€™é€‰å“åº”å­—å…¸
    """
    return {
        "candidates": [{
            "content": {"parts": parts, "role": "model"},
            "finishReason": finish_reason,
            "index": 0,
        }]
    }

def create_openai_heartbeat_chunk() -> Dict[str, Any]:
    """
    åˆ›å»º OpenAI æ ¼å¼ç„å¿ƒè·³å—ï¼ˆç”¨äºå‡æµå¼ï¼‰
    
    Returns:
        å¿ƒè·³å“åº”å—å­—å…¸
    """
    return {
        "choices": [
            {
                "index": 0,
                "delta": {"role": "assistant", "content": ""},
                "finish_reason": None,
            }
        ]
    }

def build_gemini_fake_stream_chunks(content: str, reasoning_content: str, finish_reason: str, images: List[Dict[str, Any]] = None, chunk_size: int = 50) -> List[Dict[str, Any]]:
    """æ„å»ºå‡æµå¼å“åº”ç„æ•°æ®å—

    Args:
        content: ä¸»è¦å†…å®¹
        reasoning_content: æ¨ç†å†…å®¹
        finish_reason: ç»“æŸåŸå› 
        images: å›¾ç‰‡æ•°æ®åˆ—è¡¨ï¼ˆå¯é€‰ï¼‰
        chunk_size: æ¯ä¸ªchunkç„å­—ç¬¦æ•°ï¼ˆé»˜è®¤50ï¼‰

    Returns:
        å“åº”æ•°æ®å—åˆ—è¡¨
    """
    if images is None:
        images = []

    log.debug(f"[build_gemini_fake_stream_chunks] Input - content: {repr(content)}, reasoning: {repr(reasoning_content)}, finish_reason: {finish_reason}, images count: {len(images)}")
    chunks = []

    # å¦‚æœæ²¡æœ‰æ­£å¸¸å†…å®¹ä½†æœ‰æ€ç»´å†…å®¹,æä¾›é»˜è®¤å›å¤
    if not content:
        default_text = "[æ¨¡å‹æ­£åœ¨æ€è€ƒä¸­,è¯·ç¨åå†è¯•æˆ–é‡æ–°æé—®]" if reasoning_content else "[å“åº”ä¸ºç©º,è¯·é‡æ–°å°è¯•]"
        return [_build_candidate([{"text": default_text}], finish_reason)]

    # åˆ†å—å‘é€ä¸»è¦å†…å®¹
    first_chunk = True
    for i in range(0, len(content), chunk_size):
        chunk_text = content[i:i + chunk_size]
        is_last_chunk = (i + chunk_size >= len(content)) and not reasoning_content
        chunk_finish_reason = finish_reason if is_last_chunk else None

        # å¦‚æœæ˜¯ç¬¬ä¸€ä¸ªchunkä¸”æœ‰å›¾ç‰‡ï¼Œå°†å›¾ç‰‡åŒ…å«åœ¨partsä¸­
        parts = []
        if first_chunk and images:
            # åœ¨Geminiæ ¼å¼ä¸­ï¼Œéœ€è¦å°†image_urlæ ¼å¼è½¬æ¢ä¸ºinlineDataæ ¼å¼
            for img in images:
                if img.get("type") == "image_url":
                    url = img.get("image_url", {}).get("url", "")
                    # è§£æ data URL: data:{mime_type};base64,{data}
                    if url.startswith("data:"):
                        parts_of_url = url.split(";base64,")
                        if len(parts_of_url) == 2:
                            mime_type = parts_of_url[0].replace("data:", "")
                            base64_data = parts_of_url[1]
                            parts.append({
                                "inlineData": {
                                    "mimeType": mime_type,
                                    "data": base64_data
                                }
                            })
            first_chunk = False

        parts.append({"text": chunk_text})
        chunk_data = _build_candidate(parts, chunk_finish_reason)
        log.debug(f"[build_gemini_fake_stream_chunks] Generated chunk: {chunk_data}")
        chunks.append(chunk_data)

    # å¦‚æœæœ‰æ¨ç†å†…å®¹ï¼Œåˆ†å—å‘é€
    if reasoning_content:
        for i in range(0, len(reasoning_content), chunk_size):
            chunk_text = reasoning_content[i:i + chunk_size]
            is_last_chunk = i + chunk_size >= len(reasoning_content)
            chunk_finish_reason = finish_reason if is_last_chunk else None
            chunks.append(_build_candidate([{"text": chunk_text, "thought": True}], chunk_finish_reason))

    log.debug(f"[build_gemini_fake_stream_chunks] Total chunks generated: {len(chunks)}")
    return chunks


def create_gemini_heartbeat_chunk() -> Dict[str, Any]:
    """åˆ›å»º Gemini æ ¼å¼ç„å¿ƒè·³æ•°æ®å—

    Returns:
        å¿ƒè·³æ•°æ®å—
    """
    chunk = _build_candidate([{"text": ""}])
    chunk["candidates"][0]["finishReason"] = None
    return chunk


def build_openai_fake_stream_chunks(content: str, reasoning_content: str, finish_reason: str, model: str, images: List[Dict[str, Any]] = None, chunk_size: int = 50) -> List[Dict[str, Any]]:
    """æ„å»º OpenAI æ ¼å¼ç„å‡æµå¼å“åº”æ•°æ®å—

    Args:
        content: ä¸»è¦å†…å®¹
        reasoning_content: æ¨ç†å†…å®¹
        finish_reason: ç»“æŸåŸå› ï¼ˆå¦‚ "STOP", "MAX_TOKENS"ï¼‰
        model: æ¨¡å‹åç§°
        images: å›¾ç‰‡æ•°æ®åˆ—è¡¨ï¼ˆå¯é€‰ï¼‰
        chunk_size: æ¯ä¸ªchunkç„å­—ç¬¦æ•°ï¼ˆé»˜è®¤50ï¼‰

    Returns:
        OpenAI æ ¼å¼ç„å“åº”æ•°æ®å—åˆ—è¡¨
    """
    import time
    import uuid

    if images is None:
        images = []

    log.debug(f"[build_openai_fake_stream_chunks] Input - content: {repr(content)}, reasoning: {repr(reasoning_content)}, finish_reason: {finish_reason}, images count: {len(images)}")
    chunks = []
    response_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())

    # æ˜ å°„ Gemini finish_reason åˆ° OpenAI æ ¼å¼
    openai_finish_reason = None
    if finish_reason == "STOP":
        openai_finish_reason = "stop"
    elif finish_reason == "MAX_TOKENS":
        openai_finish_reason = "length"
    elif finish_reason in ["SAFETY", "RECITATION"]:
        openai_finish_reason = "content_filter"

    # å¦‚æœæ²¡æœ‰æ­£å¸¸å†…å®¹ä½†æœ‰æ€ç»´å†…å®¹ï¼Œæä¾›é»˜è®¤å›å¤
    if not content:
        default_text = "[æ¨¡å‹æ­£åœ¨æ€è€ƒä¸­ï¼Œè¯·ç¨åå†è¯•æˆ–é‡æ–°æé—®]" if reasoning_content else "[å“åº”ä¸ºç©ºï¼Œè¯·é‡æ–°å°è¯•]"
        return [{
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"content": default_text},
                "finish_reason": openai_finish_reason,
            }]
        }]

    # åˆ†å—å‘é€ä¸»è¦å†…å®¹
    first_chunk = True
    for i in range(0, len(content), chunk_size):
        chunk_text = content[i:i + chunk_size]
        is_last_chunk = (i + chunk_size >= len(content)) and not reasoning_content
        chunk_finish = openai_finish_reason if is_last_chunk else None

        delta_content = {}

        # å¦‚æœæ˜¯ç¬¬ä¸€ä¸ªchunkä¸”æœ‰å›¾ç‰‡ï¼Œæ„å»ºåŒ…å«å›¾ç‰‡ç„contentæ•°ç»„
        if first_chunk and images:
            delta_content["content"] = images + [{"type": "text", "text": chunk_text}]
            first_chunk = False
        else:
            delta_content["content"] = chunk_text

        chunk_data = {
            "id": response_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{
                "index": 0,
                "delta": delta_content,
                "finish_reason": chunk_finish,
            }]
        }
        log.debug(f"[build_openai_fake_stream_chunks] Generated chunk: {chunk_data}")
        chunks.append(chunk_data)

    # å¦‚æœæœ‰æ¨ç†å†…å®¹ï¼Œåˆ†å—å‘é€ï¼ˆä½¿ç”¨ reasoning_content å­—æ®µï¼‰
    if reasoning_content:
        for i in range(0, len(reasoning_content), chunk_size):
            chunk_text = reasoning_content[i:i + chunk_size]
            is_last_chunk = i + chunk_size >= len(reasoning_content)
            chunk_finish = openai_finish_reason if is_last_chunk else None

            chunks.append({
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [{
                    "index": 0,
                    "delta": {"reasoning_content": chunk_text},
                    "finish_reason": chunk_finish,
                }]
            })

    log.debug(f"[build_openai_fake_stream_chunks] Total chunks generated: {len(chunks)}")
    return chunks


def create_anthropic_heartbeat_chunk() -> Dict[str, Any]:
    """
    åˆ›å»º Anthropic æ ¼å¼ç„å¿ƒè·³å—ï¼ˆç”¨äºå‡æµå¼ï¼‰

    Returns:
        å¿ƒè·³å“åº”å—å­—å…¸
    """
    return {
        "type": "ping"
    }


def build_anthropic_fake_stream_chunks(content: str, reasoning_content: str, finish_reason: str, model: str, images: List[Dict[str, Any]] = None, chunk_size: int = 50) -> List[Dict[str, Any]]:
    """æ„å»º Anthropic æ ¼å¼ç„å‡æµå¼å“åº”æ•°æ®å—

    Args:
        content: ä¸»è¦å†…å®¹
        reasoning_content: æ¨ç†å†…å®¹ï¼ˆthinking contentï¼‰
        finish_reason: ç»“æŸåŸå› ï¼ˆå¦‚ "STOP", "MAX_TOKENS"ï¼‰
        model: æ¨¡å‹åç§°
        images: å›¾ç‰‡æ•°æ®åˆ—è¡¨ï¼ˆå¯é€‰ï¼‰
        chunk_size: æ¯ä¸ªchunkç„å­—ç¬¦æ•°ï¼ˆé»˜è®¤50ï¼‰

    Returns:
        Anthropic SSE æ ¼å¼ç„å“åº”æ•°æ®å—åˆ—è¡¨
    """
    import uuid

    if images is None:
        images = []

    log.debug(f"[build_anthropic_fake_stream_chunks] Input - content: {repr(content)}, reasoning: {repr(reasoning_content)}, finish_reason: {finish_reason}, images count: {len(images)}")
    chunks = []
    message_id = f"msg_{uuid.uuid4().hex}"

    # æ˜ å°„ Gemini finish_reason åˆ° Anthropic æ ¼å¼
    anthropic_stop_reason = "end_turn"
    if finish_reason == "MAX_TOKENS":
        anthropic_stop_reason = "max_tokens"
    elif finish_reason in ["SAFETY", "RECITATION"]:
        anthropic_stop_reason = "end_turn"

    # 1. å‘é€ message_start äº‹ä»¶
    chunks.append({
        "type": "message_start",
        "message": {
            "id": message_id,
            "type": "message",
            "role": "assistant",
            "model": model,
            "content": [],
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0}
        }
    })

    # å¦‚æœæ²¡æœ‰æ­£å¸¸å†…å®¹ä½†æœ‰æ€ç»´å†…å®¹ï¼Œæä¾›é»˜è®¤å›å¤
    if not content:
        default_text = "[æ¨¡å‹æ­£åœ¨æ€è€ƒä¸­ï¼Œè¯·ç¨åå†è¯•æˆ–é‡æ–°æé—®]" if reasoning_content else "[å“åº”ä¸ºç©ºï¼Œè¯·é‡æ–°å°è¯•]"

        # content_block_start
        chunks.append({
            "type": "content_block_start",
            "index": 0,
            "content_block": {"type": "text", "text": ""}
        })

        # content_block_delta
        chunks.append({
            "type": "content_block_delta",
            "index": 0,
            "delta": {"type": "text_delta", "text": default_text}
        })

        # content_block_stop
        chunks.append({
            "type": "content_block_stop",
            "index": 0
        })

        # message_delta
        chunks.append({
            "type": "message_delta",
            "delta": {"stop_reason": anthropic_stop_reason, "stop_sequence": None},
            "usage": {"output_tokens": 0}
        })

        # message_stop
        chunks.append({
            "type": "message_stop"
        })

        return chunks

    block_index = 0

    # 2. å¦‚æœæœ‰æ¨ç†å†…å®¹ï¼Œå…ˆå‘é€ thinking å—
    if reasoning_content:
        # thinking content_block_start
        chunks.append({
            "type": "content_block_start",
            "index": block_index,
            "content_block": {"type": "thinking", "thinking": ""}
        })

        # åˆ†å—å‘é€æ¨ç†å†…å®¹
        for i in range(0, len(reasoning_content), chunk_size):
            chunk_text = reasoning_content[i:i + chunk_size]
            chunks.append({
                "type": "content_block_delta",
                "index": block_index,
                "delta": {"type": "thinking_delta", "thinking": chunk_text}
            })

        # thinking content_block_stop
        chunks.append({
            "type": "content_block_stop",
            "index": block_index
        })

        block_index += 1

    # 3. å¦‚æœæœ‰å›¾ç‰‡ï¼Œå‘é€å›¾ç‰‡å—
    if images:
        for img in images:
            if img.get("type") == "image_url":
                url = img.get("image_url", {}).get("url", "")
                # è§£æ data URL: data:{mime_type};base64,{data}
                if url.startswith("data:"):
                    parts_of_url = url.split(";base64,")
                    if len(parts_of_url) == 2:
                        mime_type = parts_of_url[0].replace("data:", "")
                        base64_data = parts_of_url[1]

                        # image content_block_start
                        chunks.append({
                            "type": "content_block_start",
                            "index": block_index,
                            "content_block": {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": base64_data
                                }
                            }
                        })

                        # image content_block_stop
                        chunks.append({
                            "type": "content_block_stop",
                            "index": block_index
                        })

                        block_index += 1

    # 4. å‘é€ä¸»è¦å†…å®¹ï¼ˆtext å—ï¼‰
    # text content_block_start
    chunks.append({
        "type": "content_block_start",
        "index": block_index,
        "content_block": {"type": "text", "text": ""}
    })

    # åˆ†å—å‘é€ä¸»è¦å†…å®¹
    for i in range(0, len(content), chunk_size):
        chunk_text = content[i:i + chunk_size]
        chunks.append({
            "type": "content_block_delta",
            "index": block_index,
            "delta": {"type": "text_delta", "text": chunk_text}
        })

    # text content_block_stop
    chunks.append({
        "type": "content_block_stop",
        "index": block_index
    })

    # 5. å‘é€ message_delta
    chunks.append({
        "type": "message_delta",
        "delta": {"stop_reason": anthropic_stop_reason, "stop_sequence": None},
        "usage": {"output_tokens": len(content) + len(reasoning_content)}
    })

    # 6. å‘é€ message_stop
    chunks.append({
        "type": "message_stop"
    })

    log.debug(f"[build_anthropic_fake_stream_chunks] Total chunks generated: {len(chunks)}")
    return chunks