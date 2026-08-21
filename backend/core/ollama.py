"""Ollama connection, discovery, and chat transport helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List
from urllib.parse import urlparse

import httpx
from core.httpx_client import get_async
from core.provider_registry import MAX_DECLARED_MODELS, MAX_MODEL_ID_LENGTH


class OllamaError(RuntimeError):
    """A sanitized Ollama integration error."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class OllamaValidation:
    base_url: str
    model_ids: List[str]

    @property
    def model_count(self) -> int:
        return len(self.model_ids)


def normalize_ollama_base_url(value: str) -> str:
    normalized = str(value or "").strip().rstrip("/")
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Ollama endpoint must use HTTP or HTTPS.")
    if parsed.username or parsed.password:
        raise ValueError("Ollama endpoint must not contain credentials.")
    path = parsed.path.rstrip("/")
    for suffix in ("/api/chat", "/api/tags"):
        if path.endswith(suffix):
            path = path[: -len(suffix)]
            break
    result = f"{parsed.scheme}://{parsed.netloc}{path}"
    return result.rstrip("/")


def build_ollama_headers(api_key: str = "") -> Dict[str, str]:
    headers = {"Content-Type": "application/json"}
    token = str(api_key or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def parse_ollama_model_ids(payload: Any) -> List[str]:
    if not isinstance(payload, dict) or not isinstance(payload.get("models"), list):
        raise OllamaError("Ollama returned an invalid model response.", 502)
    models: List[str] = []
    for item in payload["models"]:
        model_id = str(
            (item.get("name") or item.get("model")) if isinstance(item, dict) else ""
        ).strip()
        if (
            model_id
            and len(model_id) <= MAX_MODEL_ID_LENGTH
            and model_id.isprintable()
            and model_id not in models
        ):
            models.append(model_id)
            if len(models) >= MAX_DECLARED_MODELS:
                break
    return models


async def fetch_ollama_model_ids(base_url: str, api_key: str = "") -> List[str]:
    endpoint = normalize_ollama_base_url(base_url)
    try:
        response = await get_async(
            f"{endpoint}/api/tags",
            headers=build_ollama_headers(api_key),
            timeout=30.0,
        )
    except (httpx.HTTPError, OSError) as exc:
        raise OllamaError(
            "Unable to reach Ollama. Check the endpoint, container networking, and proxy settings.",
            502,
        ) from exc
    if response.status_code in {401, 403}:
        raise OllamaError("Ollama rejected this API key or connection.")
    if response.status_code != 200:
        raise OllamaError(
            f"Ollama model discovery failed with HTTP {response.status_code}.",
            502 if response.status_code >= 500 else 400,
        )
    try:
        models = parse_ollama_model_ids(response.json())
    except ValueError as exc:
        raise OllamaError("Ollama returned invalid JSON.", 502) from exc
    if not models:
        raise OllamaError("The Ollama connection is available, but it does not expose any models.")
    return models


async def validate_ollama_connection(base_url: str, api_key: str = "") -> OllamaValidation:
    endpoint = normalize_ollama_base_url(base_url)
    key = str(api_key or "").strip()
    if len(key) > 1024:
        raise OllamaError("Ollama API key is too long.")
    return OllamaValidation(
        base_url=endpoint,
        model_ids=await fetch_ollama_model_ids(endpoint, key),
    )


def _text_content(parts: List[Dict[str, Any]]) -> str:
    values = []
    for part in parts:
        if not isinstance(part, dict) or part.get("thought") is True:
            continue
        if part.get("text") is not None:
            values.append(str(part.get("text") or ""))
        response = part.get("functionResponse") or part.get("function_response")
        if isinstance(response, dict):
            values.append(json.dumps(response.get("response", {}), ensure_ascii=False))
    return "\n".join(values)


def _ollama_tools(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    tools: List[Dict[str, Any]] = []
    for group in payload.get("tools") or []:
        if not isinstance(group, dict):
            continue
        for declaration in group.get("functionDeclarations") or []:
            if not isinstance(declaration, dict) or not declaration.get("name"):
                continue
            function: Dict[str, Any] = {
                "name": str(declaration["name"]),
                "parameters": declaration.get("parametersJsonSchema")
                or declaration.get("parameters")
                or {"type": "object", "properties": {}},
            }
            if declaration.get("description"):
                function["description"] = str(declaration["description"])
            tools.append({"type": "function", "function": function})
    return tools


def gemini_request_to_ollama(
    payload: Dict[str, Any], model: str, streaming: bool
) -> Dict[str, Any]:
    messages: List[Dict[str, Any]] = []
    system_text = _text_content((payload.get("systemInstruction") or {}).get("parts") or [])
    if system_text:
        messages.append({"role": "system", "content": system_text})
    for item in payload.get("contents") or []:
        if not isinstance(item, dict):
            continue
        role = "assistant" if item.get("role") == "model" else "user"
        parts = [part for part in item.get("parts") or [] if isinstance(part, dict)]
        message: Dict[str, Any] = {"role": role, "content": _text_content(parts)}
        images = []
        tool_calls = []
        for index, part in enumerate(parts):
            inline = part.get("inlineData") or part.get("inline_data")
            if isinstance(inline, dict) and inline.get("data"):
                images.append(str(inline["data"]))
            call = part.get("functionCall") or part.get("function_call")
            if isinstance(call, dict):
                tool_calls.append(
                    {
                        "function": {
                            "name": str(call.get("name") or f"tool_{index}"),
                            "arguments": call.get("args")
                            if isinstance(call.get("args"), dict)
                            else {},
                        }
                    }
                )
        if images:
            message["images"] = images
        if tool_calls:
            message["tool_calls"] = tool_calls
        messages.append(message)
    request: Dict[str, Any] = {
        "model": model,
        "messages": messages or [{"role": "user", "content": ""}],
        "stream": bool(streaming),
    }
    tools = _ollama_tools(payload)
    if tools:
        request["tools"] = tools
    generation = payload.get("generationConfig") or {}
    options: Dict[str, Any] = {}
    mapping = {
        "temperature": "temperature",
        "topP": "top_p",
        "topK": "top_k",
        "maxOutputTokens": "num_predict",
        "stopSequences": "stop",
        "seed": "seed",
    }
    for source, target in mapping.items():
        if generation.get(source) is not None:
            options[target] = generation[source]
    if options:
        request["options"] = options
    return request


def _tool_parts(message: Dict[str, Any]) -> List[Dict[str, Any]]:
    parts: List[Dict[str, Any]] = []
    content = str(message.get("content") or "")
    if content:
        parts.append({"text": content})
    thinking = str(message.get("thinking") or "")
    if thinking:
        parts.append({"text": thinking, "thought": True})
    for index, tool_call in enumerate(message.get("tool_calls") or []):
        function = tool_call.get("function") if isinstance(tool_call, dict) else {}
        if not isinstance(function, dict):
            continue
        arguments = function.get("arguments")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = {}
        parts.append(
            {
                "functionCall": {
                    "id": str(tool_call.get("id") or f"tool_{index}"),
                    "name": str(function.get("name") or "tool"),
                    "args": arguments if isinstance(arguments, dict) else {},
                }
            }
        )
    return parts


def ollama_response_to_gemini(payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get("message"), dict):
        raise OllamaError("Ollama returned an invalid chat response.", 502)
    prompt_tokens = int(payload.get("prompt_eval_count") or 0)
    output_tokens = int(payload.get("eval_count") or 0)
    return {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": _tool_parts(payload["message"]) or [{"text": ""}],
                },
                "finishReason": "STOP" if payload.get("done", True) else None,
                "index": 0,
            }
        ],
        "usageMetadata": {
            "promptTokenCount": prompt_tokens,
            "candidatesTokenCount": output_tokens,
            "totalTokenCount": prompt_tokens + output_tokens,
        },
        "modelVersion": str(payload.get("model") or ""),
    }


def ollama_stream_line_to_gemini(line: Any) -> str:
    text = line.decode("utf-8", errors="ignore") if isinstance(line, bytes) else str(line or "")
    stripped = text.strip()
    if not stripped:
        return ""
    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return ""
    if payload.get("error"):
        raise OllamaError(str(payload["error"]), 502)
    if not isinstance(payload.get("message"), dict):
        return ""
    translated = ollama_response_to_gemini(payload)
    if not payload.get("done"):
        translated.pop("usageMetadata", None)
        translated["candidates"][0].pop("finishReason", None)
    return f"data: {json.dumps(translated, ensure_ascii=False)}\n\n"
