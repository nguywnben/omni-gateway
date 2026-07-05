"""
Anthropic Router - Handles Anthropic/Claude format API requests via Omni
é€è¿‡Omniå¤„ç†Anthropic/Claudeæ ¼å¼è¯·æ±‚ç„è·¯ç”±æ¨¡å—
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
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

# æœ¬åœ°æ¨¡å— - é…ç½®å’Œæ—¥å¿—
from config import get_anti_truncation_max_attempts, get_api_password
from log import log

# æœ¬åœ°æ¨¡å— - å·¥å…·å’Œè®¤è¯
from omni_gateway.utils import (
    get_base_model_from_feature_model,
    is_anti_truncation_model,
    is_fake_streaming_model,
    authenticate_bearer,
)

# æœ¬åœ°æ¨¡å— - è½¬æ¢å™¨ï¼ˆå‡æµå¼éœ€è¦ï¼‰
from omni_gateway.converter.fake_stream import (
    parse_response_for_fake_stream,
    build_anthropic_fake_stream_chunks,
    create_anthropic_heartbeat_chunk,
)

# æœ¬åœ°æ¨¡å— - åŸºç¡€è·¯ç”±å·¥å…·
from omni_gateway.router.hi_check import is_health_check_request, create_health_check_response
from omni_gateway.router.stream_passthrough import (
    build_streaming_response_or_error,
    prepend_async_item,
    read_first_async_item,
)

# æœ¬åœ°æ¨¡å— - æ•°æ®æ¨¡å‹
from omni_gateway.models import ClaudeRequest, model_to_dict

# æœ¬åœ°æ¨¡å— - ä»»å¡ç®¡ç†
from omni_gateway.task_manager import create_managed_task

# æœ¬åœ°æ¨¡å— - Tokenä¼°ç®—
from omni_gateway.token_estimator import estimate_input_tokens


# ==================== è·¯ç”±å™¨åˆå§‹åŒ– ====================

router = APIRouter()


# ==================== API è·¯ç”± ====================

@router.post("/ogw/v1/messages")
async def messages(
    claude_request: ClaudeRequest,
    _token: str = Depends(authenticate_bearer)
):
    """
    å¤„ç†Anthropic/Claudeæ ¼å¼ç„æ¶ˆæ¯è¯·æ±‚ï¼ˆæµå¼å’Œéæµå¼ï¼‰

    Args:
        claude_request: Anthropic/Claudeæ ¼å¼ç„è¯·æ±‚ä½“
        token: Bearerè®¤è¯ä»¤ç‰Œ
    """
    log.debug(f"[OMNI-ANTHROPIC] Request for model: {claude_request.model}")

    # è½¬æ¢ä¸ºå­—å…¸
    normalized_dict = model_to_dict(claude_request)

    # å¥åº·æ£€æŸ¥
    if is_health_check_request(normalized_dict, format="anthropic"):
        response = create_health_check_response(format="anthropic")
        return JSONResponse(content=response)

    # å¤„ç†æ¨¡å‹åç§°å’ŒåŸèƒ½æ£€æµ‹
    use_fake_streaming = is_fake_streaming_model(claude_request.model)
    use_anti_truncation = is_anti_truncation_model(claude_request.model)
    real_model = get_base_model_from_feature_model(claude_request.model)

    # è·å–æµå¼æ ‡å¿—
    is_streaming = claude_request.stream

    # å¯¹äºæ—æˆªæ–­æ¨¡å‹ç„éæµå¼è¯·æ±‚ï¼Œç»™å‡ºè­¦å‘
    if use_anti_truncation and not is_streaming:
        log.warning("Anti-truncation feature is only effective during streaming; this setting will be ignored for non-streaming requests")

    # æ›´æ–°æ¨¡å‹åä¸ºçœŸå®æ¨¡å‹å
    normalized_dict["model"] = real_model

    # è½¬æ¢ä¸º Gemini æ ¼å¼ (ä½¿ç”¨ converter)
    from omni_gateway.converter.anthropic2gemini import anthropic_to_gemini_request
    gemini_dict = await anthropic_to_gemini_request(normalized_dict)

    # anthropic_to_gemini_request ä¸åŒ…å« model å­—æ®µï¼Œéœ€è¦æ‰‹å¨æ·»å 
    gemini_dict["model"] = real_model

    # è§„èŒƒåŒ– Gemini è¯·æ±‚ (ä½¿ç”¨ omni æ¨¡å¼)
    from omni_gateway.converter.gemini_fix import normalize_gemini_request
    gemini_dict = await normalize_gemini_request(gemini_dict, mode="omni")

    # å‡†å¤‡APIè¯·æ±‚æ ¼å¼ - æå–modelå¹¶å°†å…¶ä»–å­—æ®µæ”¾å…¥requestä¸­
    api_request = {
        "model": gemini_dict.pop("model"),
        "request": gemini_dict
    }

    # ========== éæµå¼è¯·æ±‚ ==========
    if not is_streaming:
        # è°ƒç”¨ API å±‚ç„éæµå¼è¯·æ±‚
        from omni_gateway.api.omni import non_stream_request
        response = await non_stream_request(body=api_request)

        # æ£€æŸ¥å“åº”ç¶æ€ç 
        status_code = getattr(response, "status_code", 200)

        # æå–å“åº”ä½“
        if hasattr(response, "body"):
            response_body = response.body.decode() if isinstance(response.body, bytes) else response.body
        elif hasattr(response, "content"):
            response_body = response.content.decode() if isinstance(response.content, bytes) else response.content
        else:
            response_body = str(response)

        try:
            gemini_response = json.loads(response_body)
        except Exception as e:
            log.error(f"Failed to parse Gemini response: {e}")
            raise HTTPException(status_code=500, detail="Response parsing failed")

        # è½¬æ¢ä¸º Anthropic æ ¼å¼
        from omni_gateway.converter.anthropic2gemini import gemini_to_anthropic_response
        anthropic_response = gemini_to_anthropic_response(
            gemini_response,
            real_model,
            status_code
        )

        return JSONResponse(content=anthropic_response, status_code=status_code)

    # ========== æµå¼è¯·æ±‚ ==========

    # ========== å‡æµå¼ç”Ÿæˆå™¨ ==========
    async def fake_stream_generator():
        from omni_gateway.api.omni import non_stream_request

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
            gemini_response = json.loads(response_body)
            log.debug(f"Anthropic fake stream Gemini response: {gemini_response}")

            # æ£€æŸ¥æ˜¯å¦æ˜¯é”™è¯¯å“åº”ï¼ˆæœ‰äº›é”™è¯¯å¯èƒ½status_codeæ˜¯200ä½†åŒ…å«errorå­—æ®µï¼‰
            if "error" in gemini_response:
                log.error(f"Fake streaming got error in response body: {gemini_response['error']}")
                # è½¬æ¢é”™è¯¯ä¸º Anthropic æ ¼å¼
                from omni_gateway.converter.anthropic2gemini import gemini_to_anthropic_response
                anthropic_error = gemini_to_anthropic_response(
                    gemini_response,
                    real_model,
                    200
                )
                yield f"data: {json.dumps(anthropic_error)}\n\n".encode()
                yield "data: [DONE]\n\n".encode()
                return

            # ä½¿ç”¨ç»Ÿä¸€ç„è§£æå‡½æ•°
            content, reasoning_content, finish_reason, images = parse_response_for_fake_stream(gemini_response)

            log.debug(f"Anthropic extracted content: {content}")
            log.debug(f"Anthropic extracted reasoning: {reasoning_content[:100] if reasoning_content else 'None'}...")
            log.debug(f"Anthropic extracted images count: {len(images)}")

            # æ„å»ºå“åº”å—
            chunks = build_anthropic_fake_stream_chunks(content, reasoning_content, finish_reason, real_model, images)
            for idx, chunk in enumerate(chunks):
                chunk_json = json.dumps(chunk)
                log.debug(f"[FAKE_STREAM] Yielding chunk #{idx+1}: {chunk_json[:200]}")
                yield f"data: {chunk_json}\n\n".encode()

        except Exception as e:
            log.error(f"Response parsing failed: {e}, directly yield error")
            # æ„å»ºé”™è¯¯å“åº”
            error_chunk = {
                "type": "error",
                "error": {
                    "type": "api_error",
                    "message": str(e)
                }
            }
            yield f"data: {json.dumps(error_chunk)}\n\n".encode()

        yield "data: [DONE]\n\n".encode()

    # ========== æµå¼æ—æˆªæ–­ç”Ÿæˆå™¨ ==========
    async def anti_truncation_generator():
        from omni_gateway.converter.anti_truncation import AntiTruncationStreamProcessor
        from omni_gateway.api.omni import stream_request
        from omni_gateway.converter.anti_truncation import apply_anti_truncation
        from omni_gateway.converter.anthropic2gemini import gemini_stream_to_anthropic_stream
        from fastapi import Response

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

        # åŒ…è£…ä»¥ç¡®ä¿æ˜¯bytesæµ
        async def bytes_wrapper():
            async for chunk in processor.process_stream():
                if isinstance(chunk, str):
                    yield chunk.encode('utf-8')
                else:
                    yield chunk

        # ç›´æ¥å°†æ•´ä¸ªæµä¼ é€’ç»™è½¬æ¢å™¨
        async for anthropic_chunk in gemini_stream_to_anthropic_stream(
            bytes_wrapper(),
            real_model,
            200
        ):
            if anthropic_chunk:
                yield anthropic_chunk

    # ========== æ™®é€æµå¼ç”Ÿæˆå™¨ ==========
    async def normal_stream_generator():
        from omni_gateway.api.omni import stream_request
        from fastapi import Response
        from omni_gateway.converter.anthropic2gemini import gemini_stream_to_anthropic_stream

        # è°ƒç”¨ API å±‚ç„æµå¼è¯·æ±‚ï¼ˆä¸ä½¿ç”¨ native æ¨¡å¼ï¼‰
        stream_gen = stream_request(body=api_request, native=False)
        try:
            first_chunk = await read_first_async_item(stream_gen)
        except StopAsyncIteration:
            return

        if isinstance(first_chunk, Response):
            yield first_chunk
            return

        # åŒ…è£…æµå¼ç”Ÿæˆå™¨ä»¥å¤„ç†é”™è¯¯å“åº”
        async def gemini_chunk_wrapper():
            async for chunk in prepend_async_item(first_chunk, stream_gen):
                # æ£€æŸ¥æ˜¯å¦æ˜¯Responseå¯¹è±¡ï¼ˆé”™è¯¯æƒ…å†µï¼‰
                if isinstance(chunk, Response):
                    # é”™è¯¯å“åº”ï¼Œä¸è¿›è¡Œè½¬æ¢ï¼Œç›´æ¥ä¼ é€’
                    try:
                        error_content = chunk.body if isinstance(chunk.body, bytes) else (chunk.body or b'').encode('utf-8')
                        gemini_error = json.loads(error_content.decode('utf-8'))
                        from omni_gateway.converter.anthropic2gemini import gemini_to_anthropic_response
                        anthropic_error = gemini_to_anthropic_response(
                            gemini_error,
                            real_model,
                            chunk.status_code
                        )
                        yield f"data: {json.dumps(anthropic_error)}\n\n".encode('utf-8')
                    except Exception:
                        yield f"data: {json.dumps({'type': 'error', 'error': {'type': 'api_error', 'message': 'Stream error'}})}\n\n".encode('utf-8')
                    yield b"data: [DONE]\n\n"
                    return
                else:
                    # ç¡®ä¿æ˜¯bytesç±»å‹
                    if isinstance(chunk, str):
                        yield chunk.encode('utf-8')
                    else:
                        yield chunk

        # ä½¿ç”¨è½¬æ¢å™¨å¤„ç†æ•´ä¸ªæµ
        async for anthropic_chunk in gemini_stream_to_anthropic_stream(
            gemini_chunk_wrapper(),
            real_model,
            200
        ):
            if anthropic_chunk:
                yield anthropic_chunk

    # ========== æ ¹æ®æ¨¡å¼é€‰æ‹©ç”Ÿæˆå™¨ ==========
    if use_fake_streaming:
        return await build_streaming_response_or_error(fake_stream_generator())
    elif use_anti_truncation:
        log.info("Enabling anti-truncation streaming feature")
        return await build_streaming_response_or_error(anti_truncation_generator())
    else:
        return await build_streaming_response_or_error(normal_stream_generator())


@router.post("/ogw/v1/messages/count_tokens")
async def count_tokens(
    request: Request,
    _token: str = Depends(authenticate_bearer)
):
    """
    å¤„ç†Anthropicæ ¼å¼ç„tokenè®¡æ•°è¯·æ±‚
    
    Args:
        request: FastAPIè¯·æ±‚å¯¹è±¡
        _token: Bearerè®¤è¯ä»¤ç‰Œï¼ˆç”±DependséªŒè¯ï¼‰
    
    Returns:
        JSONResponse: åŒ…å«input_tokensç„å“åº”
    """
    try:
        payload = await request.json()
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"type": "error", "error": {"type": "invalid_request_error", "message": f"JSON parsing failed: {str(e)}"}}
        )

    if not isinstance(payload, dict):
        return JSONResponse(
            status_code=400,
            content={"type": "error", "error": {"type": "invalid_request_error", "message": "Request body must be a JSON object"}}
        )

    if not payload.get("model") or not isinstance(payload.get("messages"), list):
        return JSONResponse(
            status_code=400,
            content={"type": "error", "error": {"type": "invalid_request_error", "message": "Missing required fields: model / messages"}}
        )

    try:
        client_host = request.client.host if request.client else "unknown"
        client_port = request.client.port if request.client else "unknown"
    except Exception:
        client_host = "unknown"
        client_port = "unknown"

    thinking_present = "thinking" in payload
    thinking_value = payload.get("thinking")
    thinking_summary = None
    if thinking_present:
        if isinstance(thinking_value, dict):
            thinking_summary = {
                "type": thinking_value.get("type"),
                "budget_tokens": thinking_value.get("budget_tokens"),
            }
        else:
            thinking_summary = thinking_value

    user_agent = request.headers.get("user-agent", "")
    log.info(
        f"[OMNI-ANTHROPIC] /messages/count_tokens received request: client={client_host}:{client_port}, "
        f"model={payload.get('model')}, messages={len(payload.get('messages') or [])}, "
        f"thinking_present={thinking_present}, thinking={thinking_summary}, ua={user_agent}"
    )

    # ç®€å•ä¼°ç®—
    input_tokens = 0
    try:
        input_tokens = estimate_input_tokens(payload)
    except Exception as e:
        log.error(f"[OMNI-ANTHROPIC] token evaluation failed: {e}")

    return JSONResponse(content={"input_tokens": input_tokens})


# ==================== æµ‹è¯•ä»£ç  ====================

if __name__ == "__main__":
    """
    æµ‹è¯•ä»£ç ï¼æ¼”ç¤ºAnthropicè·¯ç”±ç„æµå¼å’Œéæµå¼å“åº”
    è¿è¡Œæ–¹å¼: python backend/omni_gateway/router/omni/anthropic.py
    """

    from fastapi.testclient import TestClient
    from fastapi import FastAPI

    print("=" * 80)
    print("Anthropic Router Test")
    print("=" * 80)

    # åˆ›å»ºæµ‹è¯•åº”ç”¨
    app = FastAPI()
    app.include_router(router)

    # æµ‹è¯•å®¢æˆ·ç«¯
    client = TestClient(app)

    # æµ‹è¯•è¯·æ±‚ä½“ (Anthropicæ ¼å¼)
    test_request_body = {
        "model": "gemini-2.5-flash",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": "Hello, tell me a joke in one sentence."}
        ]
    }

    # æµ‹è¯•Bearerä»¤ç‰Œï¼ˆæ¨¡æ‹Ÿï¼‰
    test_token = "Bearer pwd"

    def test_non_stream_request():
        """æµ‹è¯•éæµå¼è¯·æ±‚"""
        print("\n" + "=" * 80)
        print("[Test 1] Non-streaming request (POST /ogw/v1/messages)")
        print("=" * 80)
        print(f"Request body: {json.dumps(test_request_body, indent=2, ensure_ascii=False)}\n")

        response = client.post(
            "/ogw/v1/messages",
            json=test_request_body,
            headers={"Authorization": test_token}
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
        print("[Test 2] Streaming request (POST /ogw/v1/messages)")
        print("=" * 80)

        stream_request_body = test_request_body.copy()
        stream_request_body["stream"] = True

        print(f"Request body: {json.dumps(stream_request_body, indent=2, ensure_ascii=False)}\n")

        print("Streaming response data (per chunk):")
        print("-" * 80)

        with client.stream(
            "POST",
            "/ogw/v1/messages",
            json=stream_request_body,
            headers={"Authorization": test_token}
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
                        if chunk_str.startswith("event: ") or chunk_str.startswith("data: "):
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
        print("[Test 3] Pseudo-streaming request (POST /ogw/v1/messages with pseudo-streaming prefix)")
        print("=" * 80)

        fake_stream_request_body = test_request_body.copy()
        fake_stream_request_body["model"] = "å‡æµå¼/gemini-2.5-flash"
        fake_stream_request_body["stream"] = True

        print(f"Request body: {json.dumps(fake_stream_request_body, indent=2, ensure_ascii=False)}\n")

        print("Pseudo-streaming response data (per chunk):")
        print("-" * 80)

        with client.stream(
            "POST",
            "/ogw/v1/messages",
            json=fake_stream_request_body,
            headers={"Authorization": test_token}
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
                        if line.startswith("data: ") or line.startswith("event: "):
                            events.append(line)

                    print(f"  Contains {len(events)} SSE events")

                    # æ˜¾ç¤ºæ¯ä¸ªäº‹ä»¶
                    for event_idx, event_line in enumerate(events, 1):
                        if event_line == "data: [DONE]":
                            print(f"  Event # {event_idx}: [done]")
                        elif event_line.startswith("data: "):
                            try:
                                json_str = event_line[6:]  # å»æ‰ "data: " å‰ç¼€
                                json_data = json.loads(json_str)
                                event_type = json_data.get("type", "unknown")
                                print(f"  Event # {event_idx}: type = {event_type}")
                            except Exception as e:
                                print(f"  Event # {event_idx}: Parsing failed - {e}")

            print(f"\nReceived a total of {chunk_count} HTTP chunks")

    # è¿è¡Œæµ‹è¯•
    try:
        # æµ‹è¯•éæµå¼è¯·æ±‚
        test_non_stream_request()

        # æµ‹è¯•æµå¼è¯·æ±‚
        test_stream_request()

        # æµ‹è¯•å‡æµå¼è¯·æ±‚
        test_fake_stream_request()

        print("\n" + "=" * 80)
        print("Test completed")
        print("=" * 80)

    except Exception as e:
        print(f"\nâŒ Exception during testing: {e}")
        import traceback
        traceback.print_exc()
