"""Internal implementation detail."""

import sys
from pathlib import Path


project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


import asyncio
import json


from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import JSONResponse, StreamingResponse


from config import get_anti_truncation_max_attempts
from log import log


from core.utils import (
    get_base_model_from_feature_model,
    is_anti_truncation_model,
    authenticate_gemini_flexible,
    is_fake_streaming_model
)


from core.converter.fake_stream import (
    parse_response_for_fake_stream,
    build_gemini_fake_stream_chunks,
    create_gemini_heartbeat_chunk,
)


from core.router.hi_check import is_health_check_request, create_health_check_response
from core.router.stream_passthrough import (
    build_streaming_response_or_error,
    prepend_async_item,
    read_first_async_item,
)


from core.models import GeminiRequest, model_to_dict


from core.task_manager import create_managed_task




router = APIRouter()




@router.post("/v1beta/models/{model:path}:generateContent")
async def generate_content(
    gemini_request: "GeminiRequest",
    model: str = Path(..., description="Model name"),
    api_key: str = Depends(authenticate_gemini_flexible),
):
    """Internal implementation detail."""
    log.debug(f"[provider] Non-streaming request for model: {model}")


    normalized_dict = model_to_dict(gemini_request)


    if is_health_check_request(normalized_dict, format="gemini"):
        response = create_health_check_response(format="gemini")
        return JSONResponse(content=response)


    use_anti_truncation = is_anti_truncation_model(model)
    real_model = get_base_model_from_feature_model(model)


    if use_anti_truncation:
        log.warning("Anti-truncation feature is only effective during streaming; this setting will be ignored for non-streaming requests")


    normalized_dict["model"] = real_model


    from core.converter.gemini_fix import normalize_gemini_request
    normalized_dict = await normalize_gemini_request(normalized_dict, mode="primary")


    api_request = {
        "model": normalized_dict.pop("model"),
        "request": normalized_dict
    }


    from core.api.primary import non_stream_request
    response = await non_stream_request(body=api_request)




    try:
        if response.status_code == 200:
            response_data = json.loads(response.body if hasattr(response, 'body') else response.content)

            if "response" in response_data:
                unwrapped_data = response_data["response"]
                return JSONResponse(content=unwrapped_data)

        return response
    except Exception as e:
        log.warning(f"Failed to unwrap response: {e}, returning original response")
        return response

@router.post("/v1beta/models/{model:path}:streamGenerateContent")
async def stream_generate_content(
    gemini_request: GeminiRequest,
    model: str = Path(..., description="Model name"),
    api_key: str = Depends(authenticate_gemini_flexible),
):
    """Internal implementation detail."""
    log.debug(f"[provider] Streaming request for model: {model}")


    normalized_dict = model_to_dict(gemini_request)


    use_fake_streaming = is_fake_streaming_model(model)
    use_anti_truncation = is_anti_truncation_model(model)
    real_model = get_base_model_from_feature_model(model)


    normalized_dict["model"] = real_model


    async def fake_stream_generator():
        from core.converter.gemini_fix import normalize_gemini_request
        from core.api.primary import non_stream_request

        normalized_req = await normalize_gemini_request(normalized_dict.copy(), mode="primary")


        api_request = {
            "model": normalized_req.pop("model"),
            "request": normalized_req
        }

        response = await non_stream_request(body=api_request)


        if hasattr(response, "status_code") and response.status_code != 200:
            log.error(f"Fake streaming got error response: status={response.status_code}")
            yield response
            return


        if hasattr(response, "body"):
            response_body = response.body.decode() if isinstance(response.body, bytes) else response.body
        elif hasattr(response, "content"):
            response_body = response.content.decode() if isinstance(response.content, bytes) else response.content
        else:
            response_body = str(response)

        try:
            response_data = json.loads(response_body)
            log.debug(f"Gemini fake stream response data: {response_data}")


            if "error" in response_data:
                log.error(f"Fake streaming got error in response body: {response_data['error']}")
                yield f"data: {json.dumps(response_data)}\n\n".encode()
                yield "data: [DONE]\n\n".encode()
                return


            content, reasoning_content, finish_reason, images = parse_response_for_fake_stream(response_data)

            log.debug(f"Gemini extracted content: {content}")
            log.debug(f"Gemini extracted reasoning: {reasoning_content[:100] if reasoning_content else 'None'}...")
            log.debug(f"Gemini extracted images count: {len(images)}")


            chunks = build_gemini_fake_stream_chunks(content, reasoning_content, finish_reason, images)
            for idx, chunk in enumerate(chunks):
                chunk_json = json.dumps(chunk)
                log.debug(f"[FAKE_STREAM] Yielding chunk #{idx+1}: {chunk_json[:200]}")
                yield f"data: {chunk_json}\n\n".encode()

        except Exception as e:
            log.error(f"Response parsing failed: {e}, directly yield original response")

            yield f"data: {response_body}\n\n".encode()

        yield "data: [DONE]\n\n".encode()


    async def anti_truncation_generator():
        from core.converter.gemini_fix import normalize_gemini_request
        from core.converter.anti_truncation import AntiTruncationStreamProcessor
        from core.converter.anti_truncation import apply_anti_truncation
        from core.api.primary import stream_request
        from fastapi import Response


        normalized_req = await normalize_gemini_request(normalized_dict.copy(), mode="primary")


        api_request = {
            "model": normalized_req.pop("model") if "model" in normalized_req else real_model,
            "request": normalized_req
        }

        max_attempts = await get_anti_truncation_max_attempts()


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


        processor = AntiTruncationStreamProcessor(
            stream_request_wrapper,
            anti_truncation_payload,
            max_attempts,
            enable_prefill_mode=("claude" not in str(api_request.get("model", "")).lower()),
        )


        async for chunk in processor.process_stream():
            if isinstance(chunk, (str, bytes)):
                chunk_str = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk


                if chunk_str.startswith("data: "):
                    json_str = chunk_str[6:].strip()


                    if json_str == "[DONE]":
                        yield chunk
                        continue

                    try:

                        data = json.loads(json_str)


                        if "response" in data and "candidates" not in data:
                            log.debug(f"[provider anti-truncation] Expand response packaging")
                            unwrapped_data = data["response"]

                            yield f"data: {json.dumps(unwrapped_data, ensure_ascii=False)}\n\n".encode('utf-8')
                        else:

                            yield chunk
                    except json.JSONDecodeError:

                        yield chunk
                else:

                    yield chunk
            else:

                yield chunk


    async def normal_stream_generator():
        from core.converter.gemini_fix import normalize_gemini_request
        from core.api.primary import stream_request
        from fastapi import Response

        normalized_req = await normalize_gemini_request(normalized_dict.copy(), mode="primary")


        api_request = {
            "model": normalized_req.pop("model"),
            "request": normalized_req
        }


        log.debug(f"[provider] Using non-native mode, the response wrapper will be expanded")
        stream_gen = stream_request(body=api_request, native=False)
        try:
            first_chunk = await read_first_async_item(stream_gen)
        except StopAsyncIteration:
            return

        if isinstance(first_chunk, Response):
            yield first_chunk
            return


        async for chunk in prepend_async_item(first_chunk, stream_gen):

            if isinstance(chunk, Response):

                try:
                    error_content = chunk.body if isinstance(chunk.body, bytes) else (chunk.body or b'').encode('utf-8')
                    error_json = json.loads(error_content.decode('utf-8'))
                except Exception:
                    error_json = {"error": {"code": chunk.status_code, "message": "upstream error", "status": "ERROR"}}
                log.error(f"[provider stream] returns an error to the client: status = {chunk.status_code}, error = {str(error_json)[:200]}")
                yield f"data: {json.dumps(error_json)}\n\n".encode('utf-8')
                yield b"data: [DONE]\n\n"
                return


            if isinstance(chunk, (str, bytes)):
                chunk_str = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk


                if chunk_str.startswith("data: "):
                    json_str = chunk_str[6:].strip()


                    if json_str == "[DONE]":
                        yield chunk
                        continue

                    try:

                        data = json.loads(json_str)


                        if "response" in data and "candidates" not in data:
                            log.debug(f"[provider] Expand response packaging")
                            unwrapped_data = data["response"]

                            yield f"data: {json.dumps(unwrapped_data, ensure_ascii=False)}\n\n".encode('utf-8')
                        else:

                            yield chunk
                    except json.JSONDecodeError:

                        yield chunk
                else:

                    yield chunk


    if use_fake_streaming:
        return await build_streaming_response_or_error(fake_stream_generator())
    elif use_anti_truncation:
        log.info("Enabling anti-truncation streaming feature")
        return await build_streaming_response_or_error(anti_truncation_generator())
    else:
        return await build_streaming_response_or_error(normal_stream_generator())

@router.post("/v1beta/models/{model:path}:countTokens")
async def count_tokens(
    request: Request = None,
    api_key: str = Depends(authenticate_gemini_flexible),
):
    """Internal implementation detail."""

    try:
        request_data = await request.json()
    except Exception as e:
        log.error(f"Failed to parse JSON request: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")


    total_tokens = 0


    if "contents" in request_data:
        for content in request_data["contents"]:
            if "parts" in content:
                for part in content["parts"]:
                    if "text" in part:

                        text_length = len(part["text"])
                        total_tokens += max(1, text_length // 4)


    elif "generateContentRequest" in request_data:
        gen_request = request_data["generateContentRequest"]
        if "contents" in gen_request:
            for content in gen_request["contents"]:
                if "parts" in content:
                    for part in content["parts"]:
                        if "text" in part:
                            text_length = len(part["text"])
                            total_tokens += max(1, text_length // 4)


    return JSONResponse(content={"totalTokens": total_tokens})
