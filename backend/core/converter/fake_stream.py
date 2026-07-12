import json
from typing import Any, Dict, List, Tuple

from core.converter.openai_to_gemini import _convert_usage_metadata
from core.converter.utils import extract_content_and_reasoning
from log import log


def safe_get_nested(obj: Any, *keys: str, default: Any = None) -> Any:
    for key in keys:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(key, default)
        if obj is default:
            return default
    return obj


def parse_response_for_fake_stream(response_data: Dict[str, Any]) -> tuple:
    import json

    if "response" in response_data and "candidates" not in response_data:
        log.debug("[FAKE_STREAM] Unwrapping response field")
        response_data = response_data["response"]

    candidates = response_data.get("candidates", [])
    log.debug(f"[FAKE_STREAM] Found {len(candidates)} candidates")
    if not candidates:
        return "", "", "STOP", []

    candidate = candidates[0]
    finish_reason = candidate.get("finishReason", "STOP")
    parts = safe_get_nested(candidate, "content", "parts", default=[])
    log.debug(
        f"[FAKE_STREAM] Extracted {len(parts)} parts: {json.dumps(parts, ensure_ascii=False)}"
    )
    content, reasoning_content, images = extract_content_and_reasoning(parts)
    log.debug(
        f"[FAKE_STREAM] Content length: {len(content)}, Reasoning length: {len(reasoning_content)}, Images count: {len(images)}"
    )

    return content, reasoning_content, finish_reason, images


def extract_fake_stream_content(response: Any) -> Tuple[str, str, Dict[str, int]]:
    from core.converter.utils import extract_content_and_reasoning

    if hasattr(response, "body"):
        body_str = (
            response.body.decode() if isinstance(response.body, bytes) else str(response.body)
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

        if "response" in response_data:
            gemini_response = response_data["response"]
        else:
            gemini_response = response_data

        content = ""
        reasoning_content = ""
        images = []
        if "candidates" in gemini_response and gemini_response["candidates"]:
            candidate = gemini_response["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                content, reasoning_content, images = extract_content_and_reasoning(parts)
        elif "choices" in gemini_response and gemini_response["choices"]:
            content = gemini_response["choices"][0].get("message", {}).get("content", "")

        if not content and reasoning_content:
            log.warning("Fake stream response contains only thinking content")
            content = (
                "[The model returned only reasoning content. Please retry or rephrase the request.]"
            )

        if not content:
            log.warning(f"No content found in response: {gemini_response}")
            content = "[The upstream response was empty. Please retry.]"

        usage = _convert_usage_metadata(gemini_response.get("usageMetadata"))

        return content, reasoning_content, usage

    except json.JSONDecodeError:
        return body_str, "", None


def _build_candidate(parts: List[Dict[str, Any]], finish_reason: str = "STOP") -> Dict[str, Any]:
    return {
        "candidates": [
            {
                "content": {"parts": parts, "role": "model"},
                "finishReason": finish_reason,
                "index": 0,
            }
        ]
    }


def create_openai_heartbeat_chunk() -> Dict[str, Any]:
    return {
        "choices": [
            {
                "index": 0,
                "delta": {"role": "assistant", "content": ""},
                "finish_reason": None,
            }
        ]
    }


def build_gemini_fake_stream_chunks(
    content: str,
    reasoning_content: str,
    finish_reason: str,
    images: List[Dict[str, Any]] = None,
    chunk_size: int = 50,
) -> List[Dict[str, Any]]:
    if images is None:
        images = []

    log.debug(
        f"[build_gemini_fake_stream_chunks] Input - content: {repr(content)}, reasoning: {repr(reasoning_content)}, finish_reason: {finish_reason}, images count: {len(images)}"
    )
    chunks = []

    if not content:
        default_text = (
            "[The model returned only reasoning content. Please retry or rephrase the request.]"
            if reasoning_content
            else "[The upstream response was empty. Please retry.]"
        )
        return [_build_candidate([{"text": default_text}], finish_reason)]

    first_chunk = True
    for i in range(0, len(content), chunk_size):
        chunk_text = content[i : i + chunk_size]
        is_last_chunk = (i + chunk_size >= len(content)) and not reasoning_content
        chunk_finish_reason = finish_reason if is_last_chunk else None

        parts = []
        if first_chunk and images:
            for img in images:
                if img.get("type") == "image_url":
                    url = img.get("image_url", {}).get("url", "")

                    if url.startswith("data:"):
                        parts_of_url = url.split(";base64,")
                        if len(parts_of_url) == 2:
                            mime_type = parts_of_url[0].replace("data:", "")
                            base64_data = parts_of_url[1]
                            parts.append(
                                {"inlineData": {"mimeType": mime_type, "data": base64_data}}
                            )
            first_chunk = False

        parts.append({"text": chunk_text})
        chunk_data = _build_candidate(parts, chunk_finish_reason)
        log.debug(f"[build_gemini_fake_stream_chunks] Generated chunk: {chunk_data}")
        chunks.append(chunk_data)

    if reasoning_content:
        for i in range(0, len(reasoning_content), chunk_size):
            chunk_text = reasoning_content[i : i + chunk_size]
            is_last_chunk = i + chunk_size >= len(reasoning_content)
            chunk_finish_reason = finish_reason if is_last_chunk else None
            chunks.append(
                _build_candidate([{"text": chunk_text, "thought": True}], chunk_finish_reason)
            )

    log.debug(f"[build_gemini_fake_stream_chunks] Total chunks generated: {len(chunks)}")
    return chunks


def create_gemini_heartbeat_chunk() -> Dict[str, Any]:
    chunk = _build_candidate([{"text": ""}])
    chunk["candidates"][0]["finishReason"] = None
    return chunk


def build_openai_fake_stream_chunks(
    content: str,
    reasoning_content: str,
    finish_reason: str,
    model: str,
    images: List[Dict[str, Any]] = None,
    chunk_size: int = 50,
) -> List[Dict[str, Any]]:
    import time
    import uuid

    if images is None:
        images = []

    log.debug(
        f"[build_openai_fake_stream_chunks] Input - content: {repr(content)}, reasoning: {repr(reasoning_content)}, finish_reason: {finish_reason}, images count: {len(images)}"
    )
    chunks = []
    response_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
    created = int(time.time())

    openai_finish_reason = None
    if finish_reason == "STOP":
        openai_finish_reason = "stop"
    elif finish_reason == "MAX_TOKENS":
        openai_finish_reason = "length"
    elif finish_reason in ["SAFETY", "RECITATION"]:
        openai_finish_reason = "content_filter"

    if not content:
        default_text = (
            "[The model returned only reasoning content. Please retry or rephrase the request.]"
            if reasoning_content
            else "[The upstream response was empty. Please retry.]"
        )
        return [
            {
                "id": response_id,
                "object": "chat.completion.chunk",
                "created": created,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": default_text},
                        "finish_reason": openai_finish_reason,
                    }
                ],
            }
        ]

    first_chunk = True
    for i in range(0, len(content), chunk_size):
        chunk_text = content[i : i + chunk_size]
        is_last_chunk = (i + chunk_size >= len(content)) and not reasoning_content
        chunk_finish = openai_finish_reason if is_last_chunk else None

        delta_content = {}

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
            "choices": [
                {
                    "index": 0,
                    "delta": delta_content,
                    "finish_reason": chunk_finish,
                }
            ],
        }
        log.debug(f"[build_openai_fake_stream_chunks] Generated chunk: {chunk_data}")
        chunks.append(chunk_data)

    if reasoning_content:
        for i in range(0, len(reasoning_content), chunk_size):
            chunk_text = reasoning_content[i : i + chunk_size]
            is_last_chunk = i + chunk_size >= len(reasoning_content)
            chunk_finish = openai_finish_reason if is_last_chunk else None

            chunks.append(
                {
                    "id": response_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {"reasoning_content": chunk_text},
                            "finish_reason": chunk_finish,
                        }
                    ],
                }
            )

    log.debug(f"[build_openai_fake_stream_chunks] Total chunks generated: {len(chunks)}")
    return chunks


def create_anthropic_heartbeat_chunk() -> Dict[str, Any]:
    return {"type": "ping"}


def build_anthropic_fake_stream_chunks(
    content: str,
    reasoning_content: str,
    finish_reason: str,
    model: str,
    images: List[Dict[str, Any]] = None,
    chunk_size: int = 50,
) -> List[Dict[str, Any]]:
    import uuid

    if images is None:
        images = []

    log.debug(
        f"[build_anthropic_fake_stream_chunks] Input - content: {repr(content)}, reasoning: {repr(reasoning_content)}, finish_reason: {finish_reason}, images count: {len(images)}"
    )
    chunks = []
    message_id = f"msg_{uuid.uuid4().hex}"

    anthropic_stop_reason = "end_turn"
    if finish_reason == "MAX_TOKENS":
        anthropic_stop_reason = "max_tokens"
    elif finish_reason in ["SAFETY", "RECITATION"]:
        anthropic_stop_reason = "end_turn"

    chunks.append(
        {
            "type": "message_start",
            "message": {
                "id": message_id,
                "type": "message",
                "role": "assistant",
                "model": model,
                "content": [],
                "stop_reason": None,
                "stop_sequence": None,
                "usage": {"input_tokens": 0, "output_tokens": 0},
            },
        }
    )

    if not content:
        default_text = (
            "[The model returned only reasoning content. Please retry or rephrase the request.]"
            if reasoning_content
            else "[The upstream response was empty. Please retry.]"
        )

        # content_block_start
        chunks.append(
            {
                "type": "content_block_start",
                "index": 0,
                "content_block": {"type": "text", "text": ""},
            }
        )

        # content_block_delta
        chunks.append(
            {
                "type": "content_block_delta",
                "index": 0,
                "delta": {"type": "text_delta", "text": default_text},
            }
        )

        # content_block_stop
        chunks.append({"type": "content_block_stop", "index": 0})

        # message_delta
        chunks.append(
            {
                "type": "message_delta",
                "delta": {"stop_reason": anthropic_stop_reason, "stop_sequence": None},
                "usage": {"output_tokens": 0},
            }
        )

        # message_stop
        chunks.append({"type": "message_stop"})

        return chunks

    block_index = 0

    if reasoning_content:
        # thinking content_block_start
        chunks.append(
            {
                "type": "content_block_start",
                "index": block_index,
                "content_block": {"type": "thinking", "thinking": ""},
            }
        )

        for i in range(0, len(reasoning_content), chunk_size):
            chunk_text = reasoning_content[i : i + chunk_size]
            chunks.append(
                {
                    "type": "content_block_delta",
                    "index": block_index,
                    "delta": {"type": "thinking_delta", "thinking": chunk_text},
                }
            )

        # thinking content_block_stop
        chunks.append({"type": "content_block_stop", "index": block_index})

        block_index += 1

    if images:
        for img in images:
            if img.get("type") == "image_url":
                url = img.get("image_url", {}).get("url", "")

                if url.startswith("data:"):
                    parts_of_url = url.split(";base64,")
                    if len(parts_of_url) == 2:
                        mime_type = parts_of_url[0].replace("data:", "")
                        base64_data = parts_of_url[1]

                        # image content_block_start
                        chunks.append(
                            {
                                "type": "content_block_start",
                                "index": block_index,
                                "content_block": {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": mime_type,
                                        "data": base64_data,
                                    },
                                },
                            }
                        )

                        # image content_block_stop
                        chunks.append({"type": "content_block_stop", "index": block_index})

                        block_index += 1

    # text content_block_start
    chunks.append(
        {
            "type": "content_block_start",
            "index": block_index,
            "content_block": {"type": "text", "text": ""},
        }
    )

    for i in range(0, len(content), chunk_size):
        chunk_text = content[i : i + chunk_size]
        chunks.append(
            {
                "type": "content_block_delta",
                "index": block_index,
                "delta": {"type": "text_delta", "text": chunk_text},
            }
        )

    # text content_block_stop
    chunks.append({"type": "content_block_stop", "index": block_index})

    chunks.append(
        {
            "type": "message_delta",
            "delta": {"stop_reason": anthropic_stop_reason, "stop_sequence": None},
            "usage": {"output_tokens": len(content) + len(reasoning_content)},
        }
    )

    chunks.append({"type": "message_stop"})

    log.debug(f"[build_anthropic_fake_stream_chunks] Total chunks generated: {len(chunks)}")
    return chunks
