"""Shared Grok Build OAuth and SpaceXAI Console transport helpers."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode, urlparse

import httpx
from config import (
    get_xai_api_url,
    get_xai_client_id,
    get_xai_oauth_issuer,
    get_xai_user_agent,
)
from core.credential_manager import credential_manager
from core.httpx_client import get_async, post_async
from core.provider_registry import (
    MAX_DECLARED_MODELS,
    MAX_MODEL_ID_LENGTH,
    XAI,
    api_key_fingerprint,
)

XAI_SCOPE = "openid profile email offline_access grok-cli:access api:access"
XAI_REDIRECT_URI = "http://127.0.0.1:56121/callback"
XAI_FLOW_TTL_SECONDS = 15 * 60
MAX_OAUTH_FLOWS = 256
_oauth_flows: Dict[str, Dict[str, Any]] = {}
_stream_tool_calls: Dict[str, Dict[int, Dict[int, Dict[str, str]]]] = {}
MAX_STREAM_TOOL_CALL_SESSIONS = 256


class XaiError(RuntimeError):
    """A sanitized xAI integration error."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


@dataclass(frozen=True)
class XaiValidation:
    model_ids: List[str]

    @property
    def model_count(self) -> int:
        return len(self.model_ids)


def normalize_xai_api_url(value: str) -> str:
    normalized = str(value or "").strip().rstrip("/")
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("xAI API endpoint must use HTTP or HTTPS.")
    return normalized


def normalize_xai_issuer(value: str) -> str:
    normalized = str(value or "").strip().rstrip("/")
    parsed = urlparse(normalized)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Grok Build OAuth issuer must use HTTPS.")
    host = parsed.hostname.lower()
    if host != "x.ai" and not host.endswith(".x.ai"):
        raise ValueError("Grok Build OAuth issuer must use an x.ai host.")
    return normalized


def _validate_discovered_endpoint(value: Any, label: str) -> str:
    try:
        return normalize_xai_issuer(str(value or ""))
    except ValueError as exc:
        raise XaiError(f"Grok Build OAuth discovery returned an invalid {label}.", 502) from exc


def build_xai_headers(access_token: str, user_agent: str = "") -> Dict[str, str]:
    token = str(access_token or "").strip()
    if not token:
        raise ValueError("Provider credential does not contain an access token or API key.")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if str(user_agent or "").strip():
        headers["User-Agent"] = str(user_agent).strip()
    return headers


def parse_xai_model_ids(payload: Any) -> List[str]:
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise XaiError("Grok Build returned an invalid model response.", 502)
    model_ids: List[str] = []
    for item in payload["data"]:
        model_id = str(item.get("id") if isinstance(item, dict) else "").strip()
        if (
            model_id
            and len(model_id) <= MAX_MODEL_ID_LENGTH
            and model_id.isprintable()
            and model_id not in model_ids
        ):
            model_ids.append(model_id)
            if len(model_ids) >= MAX_DECLARED_MODELS:
                break
    return model_ids


async def fetch_xai_model_ids(access_token: str) -> List[str]:
    try:
        response = await get_async(
            f"{normalize_xai_api_url(await get_xai_api_url())}/models",
            headers=build_xai_headers(access_token, await get_xai_user_agent()),
            timeout=30.0,
        )
    except (httpx.HTTPError, OSError) as exc:
        raise XaiError(
            "Unable to reach Grok Build. Check outbound network and proxy settings.", 502
        ) from exc
    if response.status_code in {401, 403}:
        raise XaiError("Grok Build rejected this credential. Check its access and permissions.")
    if response.status_code != 200:
        raise XaiError(
            f"Grok Build model discovery failed with HTTP {response.status_code}.",
            502 if response.status_code >= 500 else 400,
        )
    try:
        model_ids = parse_xai_model_ids(response.json())
    except ValueError as exc:
        raise XaiError("Grok Build returned an invalid JSON response.", 502) from exc
    if not model_ids:
        raise XaiError("The SpaceXAI Console API key is valid, but no models are available.")
    return model_ids


async def validate_xai_api_key(api_key: str) -> XaiValidation:
    normalized = str(api_key or "").strip()
    if len(normalized) < 16 or len(normalized) > 1024:
        raise XaiError("Enter a valid SpaceXAI Console API key.")
    return XaiValidation(model_ids=await fetch_xai_model_ids(normalized))


async def discover_xai_oauth_endpoints() -> Dict[str, str]:
    issuer = normalize_xai_issuer(await get_xai_oauth_issuer())
    fallback = {
        "authorization_endpoint": f"{issuer}/oauth2/authorize",
        "token_endpoint": f"{issuer}/oauth2/token",
    }
    try:
        response = await get_async(
            f"{issuer}/.well-known/openid-configuration",
            headers={"Accept": "application/json"},
            timeout=15.0,
        )
        if response.status_code != 200:
            return fallback
        payload = response.json()
        return {
            "authorization_endpoint": _validate_discovered_endpoint(
                payload.get("authorization_endpoint"), "authorization endpoint"
            ),
            "token_endpoint": _validate_discovered_endpoint(
                payload.get("token_endpoint"), "token endpoint"
            ),
        }
    except (httpx.HTTPError, OSError, ValueError, XaiError):
        return fallback


def _base64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _prune_oauth_flows() -> None:
    cutoff = time.time() - XAI_FLOW_TTL_SECONDS
    for state in list(_oauth_flows):
        if float(_oauth_flows[state].get("created_at", 0)) < cutoff:
            _oauth_flows.pop(state, None)


async def create_xai_oauth_url() -> Dict[str, str]:
    _prune_oauth_flows()
    if len(_oauth_flows) >= MAX_OAUTH_FLOWS:
        _oauth_flows.pop(next(iter(_oauth_flows)), None)
    endpoints = await discover_xai_oauth_endpoints()
    state = secrets.token_urlsafe(32)
    verifier = _base64url(os.urandom(96))
    challenge = _base64url(hashlib.sha256(verifier.encode("ascii")).digest())
    client_id = await get_xai_client_id()
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": XAI_REDIRECT_URI,
        "scope": XAI_SCOPE,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
        "state": state,
        "nonce": secrets.token_hex(16),
        "plan": "generic",
        "referrer": "cli-proxy-api",
    }
    _oauth_flows[state] = {
        "created_at": time.time(),
        "code_verifier": verifier,
        "token_endpoint": endpoints["token_endpoint"],
        "client_id": client_id,
    }
    return {
        "auth_url": f"{endpoints['authorization_endpoint']}?{urlencode(params)}",
        "state": state,
        "redirect_uri": XAI_REDIRECT_URI,
    }


def _decode_id_token_identity(id_token: Any) -> str:
    parts = str(id_token or "").split(".")
    if len(parts) != 3:
        return ""
    try:
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))
        return str(
            claims.get("email") or claims.get("preferred_username") or claims.get("sub") or ""
        ).strip()
    except (ValueError, TypeError, json.JSONDecodeError):
        return ""


async def _exchange_xai_token(data: Dict[str, str], token_endpoint: str) -> Dict[str, Any]:
    token_endpoint = _validate_discovered_endpoint(token_endpoint, "token endpoint")
    try:
        response = await post_async(
            token_endpoint,
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
                "User-Agent": await get_xai_user_agent(),
            },
            timeout=30.0,
        )
    except (httpx.HTTPError, OSError) as exc:
        raise XaiError("Unable to reach the Grok Build OAuth token endpoint.", 502) from exc
    if response.status_code != 200:
        raise XaiError("Grok Build did not accept the OAuth authorization response.")
    try:
        payload = response.json()
    except ValueError as exc:
        raise XaiError("Grok Build returned an invalid OAuth token response.", 502) from exc
    if not payload.get("access_token"):
        raise XaiError("Grok Build OAuth token response did not include an access token.", 502)
    return payload


async def complete_xai_oauth(code: str, state: str) -> Dict[str, Any]:
    _prune_oauth_flows()
    code = str(code or "").strip()
    state = str(state or "").strip()
    if not code:
        raise XaiError("Enter the code shown on the Grok Build authorization page.")
    if "://" in code or "code=" in code:
        raise XaiError("Enter the Grok Build authorization code, not a callback URL.")
    flow = _oauth_flows.pop(state, None)
    if not state or not flow:
        raise XaiError("The Grok Build OAuth session was not found or has expired.")
    tokens = await _exchange_xai_token(
        {
            "grant_type": "authorization_code",
            "client_id": flow["client_id"],
            "code": code,
            "redirect_uri": XAI_REDIRECT_URI,
            "code_verifier": flow["code_verifier"],
        },
        flow["token_endpoint"],
    )
    model_ids = await fetch_xai_model_ids(tokens["access_token"])
    identity = _decode_id_token_identity(tokens.get("id_token"))
    expires_in = max(60, int(tokens.get("expires_in") or 3600))
    expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    refresh_token = str(tokens.get("refresh_token") or "").strip()
    stable_identity = identity or refresh_token or tokens["access_token"]
    fingerprint = api_key_fingerprint(stable_identity)
    credential_data = {
        "provider": XAI,
        "credential_type": "oauth",
        "access_token": tokens["access_token"],
        "token": tokens["access_token"],
        "refresh_token": refresh_token,
        "id_token": tokens.get("id_token"),
        "token_type": tokens.get("token_type", "Bearer"),
        "client_id": flow["client_id"],
        "token_uri": flow["token_endpoint"],
        "expiry": expiry.isoformat(),
        "user_email": identity,
        "credential_label": identity or f"Grok Build account {fingerprint[:8]}",
        "account_fingerprint": fingerprint,
        "model_ids": model_ids,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    filename = f"grok-{fingerprint}.json"
    saved = await credential_manager.add_primary_credential(filename, credential_data)
    return {
        "action": saved.get("action", "created"),
        "filename": saved.get("filename", filename),
        "label": credential_data["credential_label"],
        "model_count": len(model_ids),
    }


async def refresh_xai_oauth_credential(credential_data: Dict[str, Any]) -> Dict[str, Any]:
    refresh_token = str(credential_data.get("refresh_token") or "").strip()
    if not refresh_token:
        raise XaiError("Grok Build OAuth credential does not contain a refresh token.")
    token_endpoint = str(credential_data.get("token_uri") or "").strip()
    if not token_endpoint:
        token_endpoint = (await discover_xai_oauth_endpoints())["token_endpoint"]
    client_id = str(credential_data.get("client_id") or await get_xai_client_id()).strip()
    tokens = await _exchange_xai_token(
        {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token,
        },
        token_endpoint,
    )
    expires_in = max(60, int(tokens.get("expires_in") or 3600))
    credential_data["access_token"] = tokens["access_token"]
    credential_data["token"] = tokens["access_token"]
    credential_data["expiry"] = (
        datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    ).isoformat()
    if tokens.get("refresh_token"):
        credential_data["refresh_token"] = tokens["refresh_token"]
    if tokens.get("id_token"):
        credential_data["id_token"] = tokens["id_token"]
    return credential_data


def _stringify_tool_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(value)


def _openai_message_content(parts: List[Dict[str, Any]]) -> Any:
    content: List[Dict[str, Any]] = []
    for part in parts:
        if not isinstance(part, dict) or part.get("thought") is True:
            continue
        if part.get("text") is not None:
            content.append({"type": "text", "text": str(part.get("text") or "")})
            continue
        inline_data = part.get("inlineData") or part.get("inline_data")
        if isinstance(inline_data, dict) and inline_data.get("data"):
            mime_type = str(
                inline_data.get("mimeType")
                or inline_data.get("mime_type")
                or "application/octet-stream"
            )
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{inline_data['data']}"},
                }
            )
            continue
        file_data = part.get("fileData") or part.get("file_data")
        if isinstance(file_data, dict):
            file_uri = str(file_data.get("fileUri") or file_data.get("file_uri") or "")
            if file_uri:
                content.append({"type": "image_url", "image_url": {"url": file_uri}})

    if not content:
        return None
    if all(item.get("type") == "text" for item in content):
        return "\n".join(str(item.get("text") or "") for item in content)
    return content


def _xai_tools(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    tools: List[Dict[str, Any]] = []
    for tool_group in payload.get("tools") or []:
        if not isinstance(tool_group, dict):
            continue
        for declaration in tool_group.get("functionDeclarations") or []:
            if not isinstance(declaration, dict) or not declaration.get("name"):
                continue
            function: Dict[str, Any] = {"name": str(declaration["name"])}
            if declaration.get("description"):
                function["description"] = str(declaration["description"])
            schema = declaration.get("parametersJsonSchema") or declaration.get("parameters")
            if isinstance(schema, dict):
                function["parameters"] = schema
            tools.append({"type": "function", "function": function})
    return tools


def _xai_tool_choice(payload: Dict[str, Any]) -> Any:
    function_config = (payload.get("toolConfig") or {}).get("functionCallingConfig") or {}
    mode = str(function_config.get("mode") or "").upper()
    allowed_names = function_config.get("allowedFunctionNames") or []
    if mode == "NONE":
        return "none"
    if mode == "ANY" and len(allowed_names) == 1:
        return {
            "type": "function",
            "function": {"name": str(allowed_names[0])},
        }
    if mode == "ANY":
        return "required"
    return "auto" if mode else None


def gemini_request_to_xai(payload: Dict[str, Any], model: str, streaming: bool) -> Dict[str, Any]:
    messages: List[Dict[str, Any]] = []
    system = payload.get("systemInstruction") or {}
    system_content = _openai_message_content(system.get("parts") or [])
    if system_content:
        messages.append({"role": "system", "content": system_content})

    for content in payload.get("contents") or []:
        if not isinstance(content, dict):
            continue
        role = "assistant" if content.get("role") == "model" else "user"
        parts = [part for part in content.get("parts") or [] if isinstance(part, dict)]
        message_content = _openai_message_content(parts)
        tool_calls: List[Dict[str, Any]] = []
        tool_results: List[Dict[str, Any]] = []

        for index, part in enumerate(parts):
            function_call = part.get("functionCall") or part.get("function_call")
            if isinstance(function_call, dict):
                name = str(function_call.get("name") or "tool")
                call_id = str(function_call.get("id") or f"call_{name}_{index}")
                tool_calls.append(
                    {
                        "id": call_id,
                        "type": "function",
                        "function": {
                            "name": name,
                            "arguments": _stringify_tool_value(
                                function_call["args"] if "args" in function_call else {}
                            ),
                        },
                    }
                )
                continue

            function_response = part.get("functionResponse") or part.get("function_response")
            if isinstance(function_response, dict):
                name = str(function_response.get("name") or "tool")
                tool_results.append(
                    {
                        "role": "tool",
                        "tool_call_id": str(function_response.get("id") or f"call_{name}_{index}"),
                        "name": name,
                        "content": _stringify_tool_value(
                            function_response["response"] if "response" in function_response else {}
                        ),
                    }
                )

        if message_content is not None or tool_calls:
            message: Dict[str, Any] = {"role": role, "content": message_content}
            if tool_calls:
                message["tool_calls"] = tool_calls
            messages.append(message)
        messages.extend(tool_results)

    config = payload.get("generationConfig") or {}
    result: Dict[str, Any] = {"model": model, "messages": messages, "stream": streaming}
    for source, target in {
        "temperature": "temperature",
        "topP": "top_p",
        "maxOutputTokens": "max_tokens",
        "stopSequences": "stop",
        "candidateCount": "n",
        "seed": "seed",
        "frequencyPenalty": "frequency_penalty",
        "presencePenalty": "presence_penalty",
    }.items():
        if config.get(source) is not None:
            result[target] = config[source]

    response_mime = str(config.get("responseMimeType") or "")
    response_schema = config.get("responseSchema")
    if response_mime == "application/json" and isinstance(response_schema, dict):
        result["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "response", "schema": response_schema},
        }
    elif response_mime == "application/json":
        result["response_format"] = {"type": "json_object"}

    tools = _xai_tools(payload)
    if tools:
        result["tools"] = tools
        tool_choice = _xai_tool_choice(payload)
        if tool_choice is not None:
            result["tool_choice"] = tool_choice
    return result


def xai_response_to_gemini(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload.get("choices"), list):
        raise ValueError("Grok Build response does not contain a choices array.")
    candidates = []
    for choice in payload.get("choices") or []:
        message = choice.get("message") or {}
        parts: List[Dict[str, Any]] = []
        content = message.get("content")
        if isinstance(content, str) and content:
            parts.append({"text": content})
        elif isinstance(content, list):
            for item in content:
                if not isinstance(item, dict):
                    continue
                text = item.get("text") or item.get("content")
                if text:
                    parts.append({"text": str(text)})
        reasoning = message.get("reasoning_content") or message.get("reasoning")
        if reasoning:
            parts.insert(0, {"text": str(reasoning), "thought": True})
        for tool_call in message.get("tool_calls") or []:
            function = tool_call.get("function") or {}
            try:
                arguments = json.loads(function.get("arguments") or "{}")
            except ValueError:
                arguments = {"raw": function.get("arguments") or ""}
            parts.append(
                {
                    "functionCall": {
                        "id": tool_call.get("id"),
                        "name": function.get("name") or "tool",
                        "args": arguments,
                    }
                }
            )
        finish = str(choice.get("finish_reason") or "STOP").upper()
        finish_map = {"STOP": "STOP", "LENGTH": "MAX_TOKENS", "TOOL_CALLS": "STOP"}
        candidates.append(
            {
                "index": int(choice.get("index") or 0),
                "content": {"role": "model", "parts": parts},
                "finishReason": finish_map.get(finish, finish),
            }
        )
    usage = payload.get("usage") or {}
    result: Dict[str, Any] = {"candidates": candidates}
    if usage:
        prompt_details = usage.get("prompt_tokens_details") or {}
        completion_details = usage.get("completion_tokens_details") or {}
        result["usageMetadata"] = {
            "promptTokenCount": int(usage.get("prompt_tokens") or 0),
            "candidatesTokenCount": int(usage.get("completion_tokens") or 0),
            "totalTokenCount": int(usage.get("total_tokens") or 0),
            "cachedContentTokenCount": int(prompt_details.get("cached_tokens") or 0),
            "thoughtsTokenCount": int(completion_details.get("reasoning_tokens") or 0),
        }
    return result


def xai_stream_line_to_gemini(line: Any) -> Optional[str]:
    text = line.decode("utf-8") if isinstance(line, bytes) else str(line or "")
    if not text.startswith("data:"):
        return None
    data = text[5:].strip()
    if not data or data == "[DONE]":
        return None
    try:
        payload = json.loads(data)
    except ValueError:
        return None
    response_id = str(payload.get("id") or "")
    choices = []
    for choice in payload.get("choices") or []:
        delta = choice.get("delta") or {}
        parts: List[Dict[str, Any]] = []
        if delta.get("content"):
            parts.append({"text": delta["content"]})
        reasoning = delta.get("reasoning_content") or delta.get("reasoning")
        if reasoning:
            parts.append({"text": str(reasoning), "thought": True})
        finish = choice.get("finish_reason")
        choice_index = int(choice.get("index") or 0)
        if response_id and delta.get("tool_calls"):
            if len(_stream_tool_calls) >= MAX_STREAM_TOOL_CALL_SESSIONS:
                _stream_tool_calls.pop(next(iter(_stream_tool_calls)), None)
            choice_calls = _stream_tool_calls.setdefault(response_id, {}).setdefault(
                choice_index, {}
            )
            for position, tool_call in enumerate(delta.get("tool_calls") or []):
                tool_index = int(tool_call.get("index", position))
                pending = choice_calls.setdefault(
                    tool_index,
                    {"id": "", "name": "", "arguments": ""},
                )
                function = tool_call.get("function") or {}
                if tool_call.get("id"):
                    pending["id"] = str(tool_call["id"])
                if function.get("name"):
                    pending["name"] = str(function["name"])
                if function.get("arguments"):
                    pending["arguments"] += str(function["arguments"])

        if response_id and finish and response_id in _stream_tool_calls:
            pending_choices = _stream_tool_calls[response_id]
            pending_tools = pending_choices.pop(choice_index, {})
            for tool_index, pending in sorted(pending_tools.items()):
                try:
                    arguments = json.loads(pending["arguments"] or "{}")
                except ValueError:
                    arguments = {"raw": pending["arguments"]}
                parts.append(
                    {
                        "functionCall": {
                            "id": pending["id"] or f"call_tool_{tool_index}",
                            "name": pending["name"] or "tool",
                            "args": arguments,
                        }
                    }
                )
            if not pending_choices:
                _stream_tool_calls.pop(response_id, None)

        candidate: Dict[str, Any] = {
            "index": choice_index,
            "content": {"role": "model", "parts": parts},
        }
        if finish:
            candidate["finishReason"] = "MAX_TOKENS" if finish == "length" else "STOP"
        choices.append(candidate)
    result: Dict[str, Any] = {"candidates": choices}
    usage = payload.get("usage") or {}
    if usage:
        prompt_details = usage.get("prompt_tokens_details") or {}
        completion_details = usage.get("completion_tokens_details") or {}
        result["usageMetadata"] = {
            "promptTokenCount": int(usage.get("prompt_tokens") or 0),
            "candidatesTokenCount": int(usage.get("completion_tokens") or 0),
            "totalTokenCount": int(usage.get("total_tokens") or 0),
            "cachedContentTokenCount": int(prompt_details.get("cached_tokens") or 0),
            "thoughtsTokenCount": int(completion_details.get("reasoning_tokens") or 0),
        }
    return f"data: {json.dumps(result)}"
