"""
Gemini Router - Handles native Gemini format API requests (Omni backend)
å¤„ç†åŸç”ŸGeminiæ ¼å¼è¯·æ±‚ç„è·¯ç”±æ¨¡å—ï¼ˆOmniåç«¯ï¼‰
"""

import sys
from pathlib import Path

# æ·»å é¡¹ç›®æ ¹ç›®å½•åˆ°Pythonè·¯å¾„
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# æ ‡å‡†åº“
import asyncio
import json

# ç¬¬ä¸‰æ–¹åº“
from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import JSONResponse, StreamingResponse

# æœ¬åœ°æ¨¡å— - é…ç½®å’Œæ—¥å¿—
from config import get_anti_truncation_max_attempts
from log import log

# æœ¬åœ°æ¨¡å— - å·¥å…·å’Œè®¤è¯
from omni_gateway.utils import (
    get_base_model_from_feature_model,
    is_anti_truncation_model,
    authenticate_gemini_flexible,
    is_fake_streaming_model
)

# æœ¬åœ°æ¨¡å— - è½¬æ¢å™¨ï¼ˆå‡æµå¼éœ€è¦ï¼‰
from omni_gateway.converter.fake_stream import (
    parse_response_for_fake_stream,
    build_gemini_fake_stream_chunks,
    create_gemini_heartbeat_chunk,
)

# æœ¬åœ°æ¨¡å— - åŸºç¡€è·¯ç”±å·¥å…·
from omni_gateway.router.hi_check import is_health_check_request, create_health_check_response
from omni_gateway.router.stream_passthrough import (
    build_streaming_response_or_error,
    prepend_async_item,
    read_first_async_item,
)

# æœ¬åœ°æ¨¡å— - æ•°æ®æ¨¡å‹
from omni_gateway.models import GeminiRequest, model_to_dict

# æœ¬åœ°æ¨¡å— - ä»»å¡ç®¡ç†
from omni_gateway.task_manager import create_managed_task


# ==================== è·¯ç”±å™¨åˆå§‹åŒ– ====================

router = APIRouter()


# ==================== API è·¯ç”± ====================

@router.post("/ogw/v1beta/models/{model:path}:generateContent")
@router.post("/ogw/v1/models/{model:path}:generateContent")
async def generate_content(
    gemini_request: "GeminiRequest",
    model: str = Path(..., description="Model name"),
    api_key: str = Depends(authenticate_gemini_flexible),
):
    """
    å¤„ç†Geminiæ ¼å¼ç„å†…å®¹ç”Ÿæˆè¯·æ±‚ï¼ˆéæµå¼ï¼‰

    Args:
        gemini_request: Geminiæ ¼å¼ç„è¯·æ±‚ä½“
        model: æ¨¡å‹åç§°
        api_key: API å¯†é’¥
    """
    log.debug(f"[OMNI] Non-streaming request for model: {model}")

    # è½¬æ¢ä¸ºå­—å…¸
    normalized_dict = model_to_dict(gemini_request)

    # å¥åº·æ£€æŸ¥
    if is_health_check_request(normalized_dict, format="gemini"):
        response = create_health_check_response(format="gemini")
        return JSONResponse(content=response)

    # å¤„ç†æ¨¡å‹åç§°å’ŒåŸèƒ½æ£€æµ‹
    use_anti_truncation = is_anti_truncation_model(model)
    real_model = get_base_model_from_feature_model(model)

    # å¯¹äºæ—æˆªæ–­æ¨¡å‹ç„éæµå¼è¯·æ±‚ï¼Œç»™å‡ºè­¦å‘
    if use_anti_truncation:
        log.warning("Anti-truncation feature is only effective during streaming; this setting will be ignored for non-streaming requests")

    # æ›´æ–°æ¨¡å‹åä¸ºçœŸå®æ¨¡å‹å
    normalized_dict["model"] = real_model

    # è§„èŒƒåŒ– Gemini è¯·æ±‚ (ä½¿ç”¨ omni æ¨¡å¼)
    from omni_gateway.converter.gemini_fix import normalize_gemini_request
    normalized_dict = await normalize_gemini_request(normalized_dict, mode="omni")

    # å‡†å¤‡APIè¯·æ±‚æ ¼å¼ - æå–modelå¹¶å°†å…¶ä»–å­—æ®µæ”¾å…¥requestä¸­
    api_request = {
        "model": normalized_dict.pop("model"),
        "request": normalized_dict
    }

    # è°ƒç”¨ API å±‚ç„éæµå¼è¯·æ±‚
    from omni_gateway.api.omni import non_stream_request
    response = await non_stream_request(body=api_request)

    # è§£åŒ…è£…å“åº”ï¼Omni API å¯èƒ½è¿”å›ç„æ ¼å¼æœ‰é¢å¤–ç„ response åŒ…è£…å±‚
    # éœ€è¦æå–å¹¶è¿”å›æ ‡å‡† Gemini æ ¼å¼
    # ä¿æŒ Gemini åŸç”Ÿç„ inlineData æ ¼å¼,ä¸è¿›è¡Œ Markdown è½¬æ¢
    try:
        if response.status_code == 200:
            response_data = json.loads(response.body if hasattr(response, 'body') else response.content)
            # å¦‚æœæœ‰ response åŒ…è£…ï¼Œè§£åŒ…è£…å®ƒ
            if "response" in response_data:
                unwrapped_data = response_data["response"]
                return JSONResponse(content=unwrapped_data)
        # é”™è¯¯å“åº”æˆ–æ²¡æœ‰ response å­—æ®µï¼Œç›´æ¥è¿”å›
        return response
    except Exception as e:
        log.warning(f"Failed to unwrap response: {e}, returning original response")
        return response

@router.post("/ogw/v1beta/models/{model:path}:streamGenerateContent")
@router.post("/ogw/v1/models/{model:path}:streamGenerateContent")
async def stream_generate_content(
    gemini_request: GeminiRequest,
    model: str = Path(..., description="Model name"),
    api_key: str = Depends(authenticate_gemini_flexible),
):
    """
    å¤„ç†Geminiæ ¼å¼ç„æµå¼å†…å®¹ç”Ÿæˆè¯·æ±‚

    Args:
        gemini_request: Geminiæ ¼å¼ç„è¯·æ±‚ä½“
        model: æ¨¡å‹åç§°
        api_key: API å¯†é’¥
    """
    log.debug(f"[OMNI] Streaming request for model: {model}")

    # è½¬æ¢ä¸ºå­—å…¸
    normalized_dict = model_to_dict(gemini_request)

    # å¤„ç†æ¨¡å‹åç§°å’ŒåŸèƒ½æ£€æµ‹
    use_fake_streaming = is_fake_streaming_model(model)
    use_anti_truncation = is_anti_truncation_model(model)
    real_model = get_base_model_from_feature_model(model)

    # æ›´æ–°æ¨¡å‹åä¸ºçœŸå®æ¨¡å‹å
    normalized_dict["model"] = real_model

    # ========== å‡æµå¼ç”Ÿæˆå™¨ ==========
    async def fake_stream_generator():
        from omni_gateway.converter.gemini_fix import normalize_gemini_request
        from omni_gateway.api.omni import non_stream_request

        normalized_req = await normalize_gemini_request(normalized_dict.copy(), mode="omni")

        # å‡†å¤‡APIè¯·æ±‚æ ¼å¼ - æå–modelå¹¶å°†å…¶ä»–å­—æ®µæ”¾å…¥requestä¸­
        api_request = {
            "model": normalized_req.pop("model"),
            "request": normalized_req
        }

        response = await non_stream_request(body=api_request)

        # æ£€æŸ¥å“åº”ç¶æ€ç 
        if hasattr(response, "status_code") and response.status_code != 200:
            log.error(f"Fake streaming got error response: status={response.status_code}")
            yield response
            return

        # å¤„ç†æˆåŸå“åº” - æå–å“åº”å†…å®¹
        if hasattr(response, "body"):
            response_body = response.body.decode() if isinstance(response.body, bytes) else response.body
        elif hasattr(response, "content"):
            response_body = response.content.decode() if isinstance(response.content, bytes) else response.content
        else:
            response_body = str(response)

        try:
            response_data = json.loads(response_body)
            log.debug(f"Gemini fake stream response data: {response_data}")

            # æ£€æŸ¥æ˜¯å¦æ˜¯é”™è¯¯å“åº”ï¼ˆæœ‰äº›é”™è¯¯å¯èƒ½status_codeæ˜¯200ä½†åŒ…å«errorå­—æ®µï¼‰
            if "error" in response_data:
                log.error(f"Fake streaming got error in response body: {response_data['error']}")
                yield f"data: {json.dumps(response_data)}\n\n".encode()
                yield "data: [DONE]\n\n".encode()
                return

            # ä½¿ç”¨ç»Ÿä¸€ç„è§£æå‡½æ•°
            content, reasoning_content, finish_reason, images = parse_response_for_fake_stream(response_data)

            log.debug(f"Gemini extracted content: {content}")
            log.debug(f"Gemini extracted reasoning: {reasoning_content[:100] if reasoning_content else 'None'}...")
            log.debug(f"Gemini extracted images count: {len(images)}")

            # æ„å»ºå“åº”å—
            chunks = build_gemini_fake_stream_chunks(content, reasoning_content, finish_reason, images)
            for idx, chunk in enumerate(chunks):
                chunk_json = json.dumps(chunk)
                log.debug(f"[FAKE_STREAM] Yielding chunk #{idx+1}: {chunk_json[:200]}")
                yield f"data: {chunk_json}\n\n".encode()

        except Exception as e:
            log.error(f"Response parsing failed: {e}, directly yield original response")
            # ç›´æ¥yieldåŸå§‹å“åº”,ä¸è¿›è¡ŒåŒ…è£…
            yield f"data: {response_body}\n\n".encode()

        yield "data: [DONE]\n\n".encode()

    # ========== æµå¼æ—æˆªæ–­ç”Ÿæˆå™¨ ==========
    async def anti_truncation_generator():
        from omni_gateway.converter.gemini_fix import normalize_gemini_request
        from omni_gateway.converter.anti_truncation import AntiTruncationStreamProcessor
        from omni_gateway.converter.anti_truncation import apply_anti_truncation
        from omni_gateway.api.omni import stream_request
        from fastapi import Response

        # å…ˆè¿›è¡ŒåŸºç¡€æ ‡å‡†åŒ–
        normalized_req = await normalize_gemini_request(normalized_dict.copy(), mode="omni")

        # å‡†å¤‡APIè¯·æ±‚æ ¼å¼ - æå–modelå¹¶å°†å…¶ä»–å­—æ®µæ”¾å…¥requestä¸­
        api_request = {
            "model": normalized_req.pop("model") if "model" in normalized_req else real_model,
            "request": normalized_req
        }

        max_attempts = await get_anti_truncation_max_attempts()

        # é¦–å…ˆå¯¹payloadåº”ç”¨åæˆªæ–­æŒ‡ä»¤
        anti_truncation_payload = apply_anti_truncation(api_request)

        first_attempt_stream = stream_request(body=anti_truncation_payload, native=False)
        try:
            first_chunk = await read_first_async_item(first_attempt_stream)
        except StopAsyncIteration:
            return

        if isinstance(first_chunk, Response):
            yield first_chunk
            return

        first_attempt_pending = True

        async def stream_request_wrapper(payload):
            nonlocal first_attempt_pending

            if first_attempt_pending:
                first_attempt_pending = False
                stream_gen = prepend_async_item(first_chunk, first_attempt_stream)
            else:
                stream_gen = stream_request(body=payload, native=False)
            return StreamingResponse(stream_gen, media_type="text/event-stream")

        # åˆ›å»ºåæˆªæ–­å¤„ç†å™¨
        processor = AntiTruncationStreamProcessor(
            stream_request_wrapper,
            anti_truncation_payload,
            max_attempts,
            enable_prefill_mode=("claude" not in str(api_request.get("model", "")).lower()),
        )

        # è¿­ä»£ process_stream() ç”Ÿæˆå™¨ï¼Œå¹¶å±•å¼€ response åŒ…è£…
        async for chunk in processor.process_stream():
            if isinstance(chunk, (str, bytes)):
                chunk_str = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk

                # è§£æå¹¶å±•å¼€ response åŒ…è£…
                if chunk_str.startswith("data: "):
                    json_str = chunk_str[6:].strip()

                    # è·³è¿‡ [DONE] æ ‡è®°
                    if json_str == "[DONE]":
                        yield chunk
                        continue

                    try:
                        # è§£æJSON
                        data = json.loads(json_str)

                        # å±•å¼€ response åŒ…è£…
                        if "response" in data and "candidates" not in data:
                            log.debug(f"[OMNI-ANTI-TRUNCATION] Expand response packaging")
                            unwrapped_data = data["response"]
                            # é‡æ–°æ„å»ºSSEæ ¼å¼
                            yield f"data: {json.dumps(unwrapped_data, ensure_ascii=False)}\n\n".encode('utf-8')
                        else:
                            # å·²ç»æ˜¯å±•å¼€ç„æ ¼å¼ï¼Œç›´æ¥è¿”å›
                            yield chunk
                    except json.JSONDecodeError:
                        # JSONè§£æå¤±è´¥ï¼Œç›´æ¥è¿”å›åŸå§‹chunk
                        yield chunk
                else:
                    # ä¸æ˜¯SSEæ ¼å¼ï¼Œç›´æ¥è¿”å›
                    yield chunk
            else:
                # å…¶ä»–ç±»å‹ï¼Œç›´æ¥è¿”å›
                yield chunk

    # ========== æ™®é€æµå¼ç”Ÿæˆå™¨ ==========
    async def normal_stream_generator():
        from omni_gateway.converter.gemini_fix import normalize_gemini_request
        from omni_gateway.api.omni import stream_request
        from fastapi import Response

        normalized_req = await normalize_gemini_request(normalized_dict.copy(), mode="omni")

        # å‡†å¤‡APIè¯·æ±‚æ ¼å¼ - æå–modelå¹¶å°†å…¶ä»–å­—æ®µæ”¾å…¥requestä¸­
        api_request = {
            "model": normalized_req.pop("model"),
            "request": normalized_req
        }

        # æ‰€æœ‰æµå¼è¯·æ±‚éƒ½ä½¿ç”¨é native æ¨¡å¼ï¼ˆSSEæ ¼å¼ï¼‰å¹¶å±•å¼€ response åŒ…è£…
        log.debug(f"[OMNI] Using non-native mode, the response wrapper will be expanded")
        stream_gen = stream_request(body=api_request, native=False)
        try:
            first_chunk = await read_first_async_item(stream_gen)
        except StopAsyncIteration:
            return

        if isinstance(first_chunk, Response):
            yield first_chunk
            return

        # å±•å¼€ response åŒ…è£…
        async for chunk in prepend_async_item(first_chunk, stream_gen):
            # æ£€æŸ¥æ˜¯å¦æ˜¯Responseå¯¹è±¡ï¼ˆé”™è¯¯æƒ…å†µï¼‰
            if isinstance(chunk, Response):
                # å°†Responseè½¬æ¢ä¸ºSSEæ ¼å¼ç„é”™è¯¯æ¶ˆæ¯
                try:
                    error_content = chunk.body if isinstance(chunk.body, bytes) else (chunk.body or b'').encode('utf-8')
                    error_json = json.loads(error_content.decode('utf-8'))
                except Exception:
                    error_json = {"error": {"code": chunk.status_code, "message": "upstream error", "status": "ERROR"}}
                log.error(f"[OMNI stream] returns an error to the client: status = {chunk.status_code}, error = {str(error_json)[:200]}")
                yield f"data: {json.dumps(error_json)}\n\n".encode('utf-8')
                yield b"data: [DONE]\n\n"
                return

            # å¤„ç†SSEæ ¼å¼ç„chunk
            if isinstance(chunk, (str, bytes)):
                chunk_str = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk

                # è§£æå¹¶å±•å¼€ response åŒ…è£…
                if chunk_str.startswith("data: "):
                    json_str = chunk_str[6:].strip()

                    # è·³è¿‡ [DONE] æ ‡è®°
                    if json_str == "[DONE]":
                        yield chunk
                        continue

                    try:
                        # è§£æJSON
                        data = json.loads(json_str)

                        # å±•å¼€ response åŒ…è£…
                        if "response" in data and "candidates" not in data:
                            log.debug(f"[OMNI] Expand response packaging")
                            unwrapped_data = data["response"]
                            # é‡æ–°æ„å»ºSSEæ ¼å¼
                            yield f"data: {json.dumps(unwrapped_data, ensure_ascii=False)}\n\n".encode('utf-8')
                        else:
                            # å·²ç»æ˜¯å±•å¼€ç„æ ¼å¼ï¼Œç›´æ¥è¿”å›
                            yield chunk
                    except json.JSONDecodeError:
                        # JSONè§£æå¤±è´¥ï¼Œç›´æ¥è¿”å›åŸå§‹chunk
                        yield chunk
                else:
                    # ä¸æ˜¯SSEæ ¼å¼ï¼Œç›´æ¥è¿”å›
                    yield chunk

    # ========== æ ¹æ®æ¨¡å¼é€‰æ‹©ç”Ÿæˆå™¨ ==========
    if use_fake_streaming:
        return await build_streaming_response_or_error(fake_stream_generator())
    elif use_anti_truncation:
        log.info("Enabling anti-truncation streaming feature")
        return await build_streaming_response_or_error(anti_truncation_generator())
    else:
        return await build_streaming_response_or_error(normal_stream_generator())

@router.post("/ogw/v1beta/models/{model:path}:countTokens")
@router.post("/ogw/v1/models/{model:path}:countTokens")
async def count_tokens(
    request: Request = None,
    api_key: str = Depends(authenticate_gemini_flexible),
):
    """
    æ¨¡æ‹ŸGeminiæ ¼å¼ç„tokenè®¡æ•°

    ä½¿ç”¨ç®€å•ç„å¯å‘å¼æ–¹æ³•ï¼å¤§çº¦4å­—ç¬¦=1token
    """

    try:
        request_data = await request.json()
    except Exception as e:
        log.error(f"Failed to parse JSON request: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    # ç®€å•ç„tokenè®¡æ•°æ¨¡æ‹Ÿ - åŸºäºæ–‡æœ¬é•¿åº¦ä¼°ç®—
    total_tokens = 0

    # å¦‚æœæœ‰contentså­—æ®µ
    if "contents" in request_data:
        for content in request_data["contents"]:
            if "parts" in content:
                for part in content["parts"]:
                    if "text" in part:
                        # ç®€å•ä¼°ç®—ï¼å¤§çº¦4å­—ç¬¦=1token
                        text_length = len(part["text"])
                        total_tokens += max(1, text_length // 4)

    # å¦‚æœæœ‰generateContentRequestå­—æ®µ
    elif "generateContentRequest" in request_data:
        gen_request = request_data["generateContentRequest"]
        if "contents" in gen_request:
            for content in gen_request["contents"]:
                if "parts" in content:
                    for part in content["parts"]:
                        if "text" in part:
                            text_length = len(part["text"])
                            total_tokens += max(1, text_length // 4)

    # è¿”å›Geminiæ ¼å¼ç„å“åº”
    return JSONResponse(content={"totalTokens": total_tokens})

# ==================== æµ‹è¯•ä»£ç  ====================

if __name__ == "__main__":
    """
    æµ‹è¯•ä»£ç ï¼æ¼”ç¤ºGeminiè·¯ç”±ç„æµå¼å’Œéæµå¼å“åº”
    è¿è¡Œæ–¹å¼: python backend/omni_gateway/router/omni/gemini.py
    """

    from fastapi.testclient import TestClient
    from fastapi import FastAPI

    print("=" * 80)
    print("Gemini Router (Omni Backend) Test")
    print("=" * 80)

    # åˆ›å»ºæµ‹è¯•åº”ç”¨
    app = FastAPI()
    app.include_router(router)

    # æµ‹è¯•å®¢æˆ·ç«¯
    client = TestClient(app)

    # æµ‹è¯•è¯·æ±‚ä½“ (Geminiæ ¼å¼)
    test_request_body = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "Hello, tell me a joke in one sentence."}]
            }
        ]
    }

    # æµ‹è¯•APIå¯†é’¥ï¼ˆæ¨¡æ‹Ÿï¼‰
    test_api_key = "pwd"

    def test_non_stream_request():
        """æµ‹è¯•éæµå¼è¯·æ±‚"""
        print("\n" + "=" * 80)
        print("[Test 2] Non-streaming request (POST /ogw/v1/models/gemini-2.5-flash:generateContent)")
        print("=" * 80)
        print(f"Request body: {json.dumps(test_request_body, indent=2, ensure_ascii=False)}\n")

        response = client.post(
            "/ogw/v1/models/gemini-2.5-flash:generateContent",
            json=test_request_body,
            params={"key": test_api_key}
        )

        print("Non-streaming response data:")
        print("-" * 80)
        print(f"Status code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")

        try:
            content = response.text
            print(f"\nResponse content (raw):\n{content}\n")

            # å°è¯•è§£æJSON
            try:
                json_data = response.json()
                print(f"Response content (formatted JSON):")
                print(json.dumps(json_data, indent=2, ensure_ascii=False))
            except json.JSONDecodeError:
                print("(non-JSON format)")
        except Exception as e:
            print(f"Content parsing failed: {e}")

    def test_stream_request():
        """æµ‹è¯•æµå¼è¯·æ±‚"""
        print("\n" + "=" * 80)
        print("[Test 3] Streaming request (POST /ogw/v1/models/gemini-2.5-flash:streamGenerateContent)")
        print("=" * 80)
        print(f"Request body: {json.dumps(test_request_body, indent=2, ensure_ascii=False)}\n")

        print("Streaming response data (per chunk):")
        print("-" * 80)

        with client.stream(
            "POST",
            "/ogw/v1/models/gemini-2.5-flash:streamGenerateContent",
            json=test_request_body,
            params={"key": test_api_key}
        ) as response:
            print(f"Status code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'N/A')}\n")

            chunk_count = 0
            for chunk in response.iter_bytes():
                if chunk:
                    chunk_count += 1
                    print(f"\nChunk #{chunk_count}:")
                    print(f"  Genre:{type(chunk).__name__}")
                    print(f"  Length:{len(chunk)}")

                    # è§£ç chunk
                    try:
                        chunk_str = chunk.decode('utf-8')
                        print(f"  Content Preview{repr(chunk_str[:200] if len(chunk_str) > 200 else chunk_str)}")

                        # å¦‚æœæ˜¯SSEæ ¼å¼ï¼Œå°è¯•è§£ææ¯ä¸€è¡Œ
                        if chunk_str.startswith("data: "):
                            # æŒ‰è¡Œåˆ†å‰²ï¼Œå¤„ç†æ¯ä¸ªSSEäº‹ä»¶
                            for line in chunk_str.strip().split('\n'):
                                line = line.strip()
                                if not line:
                                    continue

                                if line == "data: [DONE]":
                                    print(f"  = > End of flow marker")
                                elif line.startswith("data: "):
                                    try:
                                        json_str = line[6:]  # å»æ‰ "data: " å‰ç¼€
                                        json_data = json.loads(json_str)
                                        print(f"  Parsed JSON: {json.dumps(json_data, indent=4, ensure_ascii=False)}")
                                    except Exception as e:
                                        print(f"  Failed to parse SSE: {e}")
                    except Exception as e:
                        print(f"  Decoding failure{e}")

            print(f"\nReceived a total of {chunk_count} chunks")

    def test_fake_stream_request():
        """æµ‹è¯•å‡æµå¼è¯·æ±‚"""
        print("\n" + "=" * 80)
        print("[Test 4] Pseudo-streaming request (POST /ogw/v1/models/pseudo-streaming/gemini-2.5-flash:streamGenerateContent)")
        print("=" * 80)
        print(f"Request body: {json.dumps(test_request_body, indent=2, ensure_ascii=False)}\n")

        print("Pseudo-streaming response data (per chunk):")
        print("-" * 80)

        with client.stream(
            "POST",
            "/ogw/v1/models/å‡æµå¼/gemini-2.5-flash:streamGenerateContent",
            json=test_request_body,
            params={"key": test_api_key}
        ) as response:
            print(f"Status code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'N/A')}\n")

            chunk_count = 0
            for chunk in response.iter_bytes():
                if chunk:
                    chunk_count += 1
                    chunk_str = chunk.decode('utf-8')

                    print(f"\nChunk #{chunk_count}:")
                    print(f"  Length: {len(chunk_str)} bytes")

                    # è§£æchunkä¸­ç„æ‰€æœ‰SSEäº‹ä»¶
                    events = []
                    for line in chunk_str.split('\n'):
                        line = line.strip()
                        if line.startswith("data: "):
                            events.append(line)

                    print(f"  Contains {len(events)} SSE events")

                    # æ˜¾ç¤ºæ¯ä¸ªäº‹ä»¶
                    for event_idx, event_line in enumerate(events, 1):
                        if event_line == "data: [DONE]":
                            print(f"  Event # {event_idx}: [done]")
                        else:
                            try:
                                json_str = event_line[6:]  # å»æ‰ "data: " å‰ç¼€
                                json_data = json.loads(json_str)
                                # æå–textå†…å®¹
                                text = json_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                                finish_reason = json_data.get("candidates", [{}])[0].get("finishReason")
                                print(f"  Event # {event_idx}: text =  {repr(text[:50])}{'...' if len(text) > 50 else ''}, finishReason = {finish_reason}")
                            except Exception as e:
                                print(f"  Event # {event_idx}: Parsing failed - {e}")

            print(f"\nReceived a total of {chunk_count} HTTP chunks")

    def test_anti_truncation_stream_request():
        """æµ‹è¯•æµå¼æ—æˆªæ–­è¯·æ±‚"""
        print("\n" + "=" * 80)
        print("[Test 5] Anti-truncation streaming request (POST /ogw/v1/models/anti-truncation/gemini-2.5-flash:streamGenerateContent)")
        print("=" * 80)
        print(f"Request body: {json.dumps(test_request_body, indent=2, ensure_ascii=False)}\n")

        print("Streaming anti-truncation response data (per chunk):")
        print("-" * 80)

        with client.stream(
            "POST",
            "/ogw/v1/models/æµå¼æ—æˆªæ–­/gemini-2.5-flash:streamGenerateContent",
            json=test_request_body,
            params={"key": test_api_key}
        ) as response:
            print(f"Status code: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type', 'N/A')}\n")

            chunk_count = 0
            for chunk in response.iter_bytes():
                if chunk:
                    chunk_count += 1
                    print(f"\nChunk #{chunk_count}:")
                    print(f"  Genre:{type(chunk).__name__}")
                    print(f"  Length:{len(chunk)}")

                    # è§£ç chunk
                    try:
                        chunk_str = chunk.decode('utf-8')
                        print(f"  Content Preview{repr(chunk_str[:200] if len(chunk_str) > 200 else chunk_str)}")

                        # å¦‚æœæ˜¯SSEæ ¼å¼ï¼Œå°è¯•è§£ææ¯ä¸€è¡Œ
                        if chunk_str.startswith("data: "):
                            # æŒ‰è¡Œåˆ†å‰²ï¼Œå¤„ç†æ¯ä¸ªSSEäº‹ä»¶
                            for line in chunk_str.strip().split('\n'):
                                line = line.strip()
                                if not line:
                                    continue

                                if line == "data: [DONE]":
                                    print(f"  = > End of flow marker")
                                elif line.startswith("data: "):
                                    try:
                                        json_str = line[6:]  # å»æ‰ "data: " å‰ç¼€
                                        json_data = json.loads(json_str)
                                        print(f"  Parsed JSON: {json.dumps(json_data, indent=4, ensure_ascii=False)}")
                                    except Exception as e:
                                        print(f"  Failed to parse SSE: {e}")
                    except Exception as e:
                        print(f"  Decoding failure{e}")

            print(f"\nReceived a total of {chunk_count} chunks")

    # è¿è¡Œæµ‹è¯•
    try:
        # æµ‹è¯•éæµå¼è¯·æ±‚
        test_non_stream_request()

        # æµ‹è¯•æµå¼è¯·æ±‚
        test_stream_request()

        # æµ‹è¯•å‡æµå¼è¯·æ±‚
        test_fake_stream_request()

        # æµ‹è¯•æµå¼æ—æˆªæ–­è¯·æ±‚
        test_anti_truncation_stream_request()

        print("\n" + "=" * 80)
        print("Test completed")
        print("=" * 80)

    except Exception as e:
        print(f"\nâŒ Exception during testing: {e}")
        import traceback
        traceback.print_exc()
