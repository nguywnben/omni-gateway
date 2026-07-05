"""
Vertex AI Router - Handles native Gemini format API requests via anonymous Vertex AI endpoint
é€è¿‡åŒ¿å Vertex AI ç«¯ç‚¹å¤„ç† Gemini æ ¼å¼è¯·æ±‚
"""

from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.responses import JSONResponse

from log import log
from omni_gateway.utils import authenticate_gemini_flexible
from omni_gateway.models import GeminiRequest, model_to_dict
from omni_gateway.router.hi_check import is_health_check_request, create_health_check_response
from omni_gateway.router.stream_passthrough import build_streaming_response_or_error


router = APIRouter()


@router.post("/ogw/vertex/v1beta/models/{model:path}:generateContent")
@router.post("/ogw/vertex/v1/models/{model:path}:generateContent")
async def generate_content(
    gemini_request: GeminiRequest,
    model: str = Path(..., description="Model name"),
    api_key: str = Depends(authenticate_gemini_flexible),
):
    """å¤„ç† Vertex åŒ¿åé€é“ç„éæµå¼å†…å®¹ç”Ÿæˆè¯·æ±‚ă€‚"""
    log.debug(f"[VERTEX ROUTER] Non-streaming request for model: {model}")

    normalized_dict = model_to_dict(gemini_request)

    if is_health_check_request(normalized_dict, format="gemini"):
        return JSONResponse(content=create_health_check_response(format="gemini"))

    normalized_dict["model"] = model

    from omni_gateway.converter.gemini_fix import normalize_gemini_request
    normalized_dict = await normalize_gemini_request(normalized_dict, mode="vertex")

    api_request = {
        "model": normalized_dict.pop("model"),
        "request": normalized_dict,
    }

    from omni_gateway.api.vertex import non_stream_request
    response = await non_stream_request(body=api_request)

    return response


@router.post("/ogw/vertex/v1beta/models/{model:path}:streamGenerateContent")
@router.post("/ogw/vertex/v1/models/{model:path}:streamGenerateContent")
async def stream_generate_content(
    gemini_request: GeminiRequest,
    model: str = Path(..., description="Model name"),
    api_key: str = Depends(authenticate_gemini_flexible),
):
    """å¤„ç† Vertex åŒ¿åé€é“ç„æµå¼å†…å®¹ç”Ÿæˆè¯·æ±‚ă€‚"""
    log.debug(f"[VERTEX ROUTER] Streaming request for model: {model}")

    normalized_dict = model_to_dict(gemini_request)
    normalized_dict["model"] = model

    async def stream_generator():
        from omni_gateway.converter.gemini_fix import normalize_gemini_request
        from omni_gateway.api.vertex import stream_request
        from fastapi import Response

        normalized_req = await normalize_gemini_request(normalized_dict.copy(), mode="vertex")

        api_request = {
            "model": normalized_req.pop("model"),
            "request": normalized_req,
        }

        async for chunk in stream_request(body=api_request, native=False):
            if isinstance(chunk, Response):
                yield chunk
                return
            if isinstance(chunk, (str, bytes)):
                yield chunk if isinstance(chunk, bytes) else chunk.encode("utf-8")

    return await build_streaming_response_or_error(stream_generator())


@router.post("/ogw/vertex/v1beta/models/{model:path}:countTokens")
@router.post("/ogw/vertex/v1/models/{model:path}:countTokens")
async def count_tokens(
    request: Request = None,
    api_key: str = Depends(authenticate_gemini_flexible),
):
    """æ¨¡æ‹Ÿ token è®¡æ•°ï¼ˆå¯å‘å¼ä¼°ç®—ï¼‰ă€‚"""
    try:
        request_data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    total_tokens = 0
    contents = None

    if "generateContentRequest" in request_data:
        contents = request_data["generateContentRequest"].get("contents", [])
    elif "contents" in request_data:
        contents = request_data["contents"]

    if contents:
        for content in contents:
            if isinstance(content, dict) and "parts" in content:
                for part in content["parts"]:
                    if isinstance(part, dict) and "text" in part:
                        total_tokens += max(1, len(part["text"]) // 4)

    return JSONResponse(content={"totalTokens": total_tokens})
