"""Internal implementation detail."""

import sys
from pathlib import Path


project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


import asyncio
import json


from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse


from config import get_anti_truncation_max_attempts
from log import log


from omni_gateway.utils import (
    get_base_model_from_feature_model,
    is_anti_truncation_model,
    is_fake_streaming_model,
    authenticate_bearer,
)


from omni_gateway.converter.fake_stream import (
    parse_response_for_fake_stream,
    build_openai_fake_stream_chunks,
    create_openai_heartbeat_chunk,
)


from omni_gateway.router.hi_check import is_health_check_request, create_health_check_response
from omni_gateway.router.stream_passthrough import (
    build_streaming_response_or_error,
    prepend_async_item,
    read_first_async_item,
)


from omni_gateway.models import OpenAIChatCompletionRequest, model_to_dict


from omni_gateway.task_manager import create_managed_task




router = APIRouter()




@router.post("/ogw/v1/chat/completions")
async def chat_completions(
    openai_request: OpenAIChatCompletionRequest,
    token: str = Depends(authenticate_bearer)
):
    """Internal implementation detail."""
    log.debug(f"[OMNI-OPENAI] Request for model: {openai_request.model}")


    normalized_dict = model_to_dict(openai_request)


    if is_health_check_request(normalized_dict, format="openai"):
        response = create_health_check_response(format="openai")
        return JSONResponse(content=response)


    use_fake_streaming = is_fake_streaming_model(openai_request.model)
    use_anti_truncation = is_anti_truncation_model(openai_request.model)
    real_model = get_base_model_from_feature_model(openai_request.model)


    is_streaming = openai_request.stream


    if use_anti_truncation and not is_streaming:
        log.warning("Anti-truncation feature is only effective during streaming; this setting will be ignored for non-streaming requests")


    normalized_dict["model"] = real_model


    from omni_gateway.converter.openai2gemini import convert_openai_to_gemini_request
    gemini_dict = await convert_openai_to_gemini_request(normalized_dict)


    gemini_dict["model"] = real_model


    from omni_gateway.converter.gemini_fix import normalize_gemini_request
    gemini_dict = await normalize_gemini_request(gemini_dict, mode="omni")


    api_request = {
        "model": gemini_dict.pop("model"),
        "request": gemini_dict
    }


    if not is_streaming:

        from omni_gateway.api.omni import non_stream_request
        response = await non_stream_request(body=api_request)


        status_code = getattr(response, "status_code", 200)


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


        from omni_gateway.converter.openai2gemini import convert_gemini_to_openai_response
        openai_response = convert_gemini_to_openai_response(
            gemini_response,
            real_model,
            status_code
        )

        return JSONResponse(content=openai_response, status_code=status_code)




    async def fake_stream_generator():
        from omni_gateway.api.omni import non_stream_request

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
            gemini_response = json.loads(response_body)
            log.debug(f"OpenAI fake stream Gemini response: {gemini_response}")


            if "error" in gemini_response:
                log.error(f"Fake streaming got error in response body: {gemini_response['error']}")

                from omni_gateway.converter.openai2gemini import convert_gemini_to_openai_response
                openai_error = convert_gemini_to_openai_response(
                    gemini_response,
                    real_model,
                    200
                )
                yield f"data: {json.dumps(openai_error)}\n\n".encode()
                yield "data: [DONE]\n\n".encode()
                return


            content, reasoning_content, finish_reason, images = parse_response_for_fake_stream(gemini_response)

            log.debug(f"OpenAI extracted content: {content}")
            log.debug(f"OpenAI extracted reasoning: {reasoning_content[:100] if reasoning_content else 'None'}...")
            log.debug(f"OpenAI extracted images count: {len(images)}")


            chunks = build_openai_fake_stream_chunks(content, reasoning_content, finish_reason, real_model, images)
            for idx, chunk in enumerate(chunks):
                chunk_json = json.dumps(chunk)
                log.debug(f"[FAKE_STREAM] Yielding chunk #{idx+1}: {chunk_json[:200]}")
                yield f"data: {chunk_json}\n\n".encode()

        except Exception as e:
            log.error(f"Response parsing failed: {e}, directly yield error")

            error_chunk = {
                "id": "error",
                "object": "chat.completion.chunk",
                "created": int(asyncio.get_event_loop().time()),
                "model": real_model,
                "choices": [{
                    "index": 0,
                    "delta": {"content": f"Error: {str(e)}"},
                    "finish_reason": "error"
                }]
            }
            yield f"data: {json.dumps(error_chunk)}\n\n".encode()

        yield "data: [DONE]\n\n".encode()


    async def anti_truncation_generator():
        from omni_gateway.converter.anti_truncation import AntiTruncationStreamProcessor
        from omni_gateway.api.omni import stream_request
        from omni_gateway.converter.anti_truncation import apply_anti_truncation
        from fastapi import Response

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


        import uuid
        response_id = str(uuid.uuid4())


        async for chunk in processor.process_stream():
            if not chunk:
                continue


            chunk_str = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk


            if not chunk_str.strip():
                continue


            if chunk_str.strip() == "data: [DONE]":
                yield "data: [DONE]\n\n".encode('utf-8')
                return


            if chunk_str.startswith("data: "):
                try:

                    from omni_gateway.converter.openai2gemini import convert_gemini_to_openai_stream
                    openai_chunk_str = convert_gemini_to_openai_stream(
                        chunk_str,
                        real_model,
                        response_id
                    )

                    if openai_chunk_str:
                        yield openai_chunk_str.encode('utf-8')

                except Exception as e:
                    log.error(f"Failed to convert chunk: {e}")
                    continue


        yield "data: [DONE]\n\n".encode('utf-8')


    async def normal_stream_generator():
        from omni_gateway.api.omni import stream_request
        from fastapi import Response
        import uuid


        stream_gen = stream_request(body=api_request, native=False)
        try:
            first_chunk = await read_first_async_item(stream_gen)
        except StopAsyncIteration:
            return

        if isinstance(first_chunk, Response):
            yield first_chunk
            return

        response_id = str(uuid.uuid4())


        async for chunk in prepend_async_item(first_chunk, stream_gen):

            if isinstance(chunk, Response):

                try:
                    error_content = chunk.body if isinstance(chunk.body, bytes) else (chunk.body or b'').encode('utf-8')
                    gemini_error = json.loads(error_content.decode('utf-8'))

                    from omni_gateway.converter.openai2gemini import convert_gemini_to_openai_response
                    openai_error = convert_gemini_to_openai_response(
                        gemini_error,
                        real_model,
                        chunk.status_code
                    )
                    yield f"data: {json.dumps(openai_error)}\n\n".encode('utf-8')
                except Exception:
                    yield f"data: {json.dumps({'error': 'Stream error'})}\n\n".encode('utf-8')
                yield b"data: [DONE]\n\n"
                return
            else:

                chunk_str = chunk.decode('utf-8') if isinstance(chunk, bytes) else chunk


                if not chunk_str.strip():
                    continue


                if chunk_str.strip() == "data: [DONE]":
                    yield "data: [DONE]\n\n".encode('utf-8')
                    return


                if chunk_str.startswith("data: "):
                    try:

                        from omni_gateway.converter.openai2gemini import convert_gemini_to_openai_stream
                        openai_chunk_str = convert_gemini_to_openai_stream(
                            chunk_str,
                            real_model,
                            response_id
                        )

                        if openai_chunk_str:
                            yield openai_chunk_str.encode('utf-8')

                    except Exception as e:
                        log.error(f"Failed to convert chunk: {e}")
                        continue


        yield "data: [DONE]\n\n".encode('utf-8')


    if use_fake_streaming:
        return await build_streaming_response_or_error(fake_stream_generator())
    elif use_anti_truncation:
        log.info("Enabling anti-truncation streaming feature")
        return await build_streaming_response_or_error(anti_truncation_generator())
    else:
        return await build_streaming_response_or_error(normal_stream_generator())
