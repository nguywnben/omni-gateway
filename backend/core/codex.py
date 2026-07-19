"""OpenAI Codex device OAuth and Responses transport helpers."""

from __future__ import annotations

import base64
import json
import secrets
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx
from config import (
    get_codex_api_url,
    get_codex_auth_base,
    get_codex_client_id,
    get_codex_user_agent,
)
from core.httpx_client import get_async, post_async
from core.provider_registry import OPENAI, api_key_fingerprint
from log import log

CODEX_FLOW_TTL_SECONDS = 15 * 60
CODEX_DEVICE_POLL_INTERVAL_SECONDS = 5
MAX_CODEX_FLOWS = 128
CODEX_DEFAULT_MODEL_IDS = [
    "gpt-5",
    "gpt-5-codex",
    "gpt-5.1-codex",
    "gpt-5.2-codex",
    "gpt-5.3-codex",
    "gpt-5.3-codex-spark",
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5.5",
]
MAX_CODEX_MODELS = 500
MAX_CODEX_MODEL_ID_LENGTH = 256

_device_flows: Dict[str, Dict[str, Any]] = {}


class CodexError(RuntimeError):
    """A sanitized Codex integration error."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def _decode_jwt_claims(token: Any) -> Dict[str, Any]:
    parts = str(token or "").split(".")
    if len(parts) < 2:
        return {}
    try:
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        return json.loads(base64.urlsafe_b64decode(payload).decode("utf-8"))
    except (ValueError, TypeError, json.JSONDecodeError):
        return {}


def _token_expiry(token: Any) -> Optional[str]:
    exp = _decode_jwt_claims(token).get("exp")
    if not isinstance(exp, (int, float)):
        return None
    return datetime.fromtimestamp(exp, timezone.utc).isoformat()


def _account_identity(tokens: Dict[str, Any]) -> tuple[str, str]:
    claims = _decode_jwt_claims(tokens.get("id_token") or tokens.get("access_token"))
    auth_claims = claims.get("https://api.openai.com/auth")
    account_id = str(
        auth_claims.get("chatgpt_account_id") if isinstance(auth_claims, dict) else ""
    ).strip()
    email = str(claims.get("email") or claims.get("preferred_username") or "").strip().lower()
    return account_id, email


def _prune_device_flows() -> None:
    cutoff = time.time() - CODEX_FLOW_TTL_SECONDS
    for flow_id in list(_device_flows):
        if float(_device_flows[flow_id].get("created_at", 0)) < cutoff:
            _device_flows.pop(flow_id, None)
    while len(_device_flows) > MAX_CODEX_FLOWS:
        _device_flows.pop(next(iter(_device_flows)), None)


async def _auth_endpoint(path: str) -> str:
    return f"{(await get_codex_auth_base()).rstrip('/')}/{path.lstrip('/')}"


def _provider_error(response: httpx.Response, fallback: str, status_code: int = 502) -> CodexError:
    detail = ""
    try:
        payload = response.json()
        if isinstance(payload, dict):
            detail = str(payload.get("error_description") or payload.get("message") or "").strip()
    except ValueError:
        pass
    return CodexError(detail or fallback, status_code)


async def create_codex_device_flow() -> Dict[str, Any]:
    """Request a short-lived device code that the user completes at OpenAI."""
    _prune_device_flows()
    try:
        response = await post_async(
            await _auth_endpoint("api/accounts/deviceauth/usercode"),
            json={"client_id": await get_codex_client_id()},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=30.0,
        )
    except (httpx.HTTPError, OSError) as exc:
        raise CodexError("Unable to reach the OpenAI authorization service.", 502) from exc
    if response.status_code != 200:
        raise _provider_error(response, "OpenAI did not issue a device code.")
    try:
        data = response.json()
    except ValueError as exc:
        raise CodexError("OpenAI returned an invalid device authorization response.", 502) from exc

    device_auth_id = str(data.get("device_auth_id") or "").strip()
    user_code = str(data.get("user_code") or data.get("usercode") or "").strip()
    if not device_auth_id or not user_code:
        raise CodexError("OpenAI device authorization response was incomplete.", 502)

    flow_id = secrets.token_urlsafe(24)
    interval = max(3, int(data.get("interval") or CODEX_DEVICE_POLL_INTERVAL_SECONDS))
    _device_flows[flow_id] = {
        "created_at": time.time(),
        "device_auth_id": device_auth_id,
        "user_code": user_code,
        "interval": interval,
    }
    return {
        "flow_id": flow_id,
        "user_code": user_code,
        "verification_uri": f"{(await get_codex_auth_base()).rstrip('/')}/codex/device",
        "interval": interval,
        "expires_in": int(data.get("expires_in") or CODEX_FLOW_TTL_SECONDS),
    }


async def _poll_device_flow(flow: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        response = await post_async(
            await _auth_endpoint("api/accounts/deviceauth/token"),
            json={
                "device_auth_id": flow["device_auth_id"],
                "user_code": flow["user_code"],
            },
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=30.0,
        )
    except (httpx.HTTPError, OSError) as exc:
        raise CodexError("Unable to reach the OpenAI device authorization service.", 502) from exc
    if response.status_code in {403, 404}:
        return None
    if response.status_code != 200:
        raise _provider_error(response, "OpenAI rejected the device authorization.")
    try:
        data = response.json()
    except ValueError as exc:
        raise CodexError("OpenAI returned an invalid device token response.", 502) from exc
    if not all(data.get(key) for key in ("authorization_code", "code_challenge", "code_verifier")):
        raise CodexError("OpenAI device token response was incomplete.", 502)
    return data


async def _exchange_codex_tokens(code_data: Dict[str, Any]) -> Dict[str, Any]:
    redirect_uri = f"{(await get_codex_auth_base()).rstrip('/')}/deviceauth/callback"
    form = urlencode(
        {
            "grant_type": "authorization_code",
            "code": code_data["authorization_code"],
            "redirect_uri": redirect_uri,
            "client_id": await get_codex_client_id(),
            "code_verifier": code_data["code_verifier"],
        }
    )
    try:
        response = await post_async(
            await _auth_endpoint("oauth/token"),
            data=form,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=30.0,
        )
    except (httpx.HTTPError, OSError) as exc:
        raise CodexError("Unable to reach the OpenAI token service.", 502) from exc
    if response.status_code != 200:
        raise _provider_error(response, "OpenAI rejected the token exchange.")
    try:
        tokens = response.json()
    except ValueError as exc:
        raise CodexError("OpenAI returned an invalid OAuth token response.", 502) from exc
    if not tokens.get("access_token") or not tokens.get("refresh_token"):
        raise CodexError("OpenAI OAuth token response was incomplete.", 502)
    return tokens


async def complete_codex_device_flow(flow_id: str) -> Dict[str, Any]:
    _prune_device_flows()
    flow = _device_flows.get(str(flow_id or "").strip())
    if not flow:
        raise CodexError("The OpenAI Codex authorization session was not found or has expired.")
    device_data = await _poll_device_flow(flow)
    if device_data is None:
        return {
            "pending": True,
            "message": "Authorization is still pending. Finish sign-in and try again.",
        }

    tokens = await _exchange_codex_tokens(device_data)
    _device_flows.pop(str(flow_id), None)
    account_id, email = _account_identity(tokens)
    try:
        model_ids = await fetch_codex_model_ids(tokens["access_token"], account_id)
    except CodexError as exc:
        log.warning(
            "OpenAI Codex model discovery failed after authorization; using the fallback catalog: %s",
            exc,
        )
        model_ids = list(CODEX_DEFAULT_MODEL_IDS)
    identity = email or account_id or str(tokens.get("refresh_token") or tokens["access_token"])
    fingerprint = api_key_fingerprint(identity)
    credential = {
        "provider": OPENAI,
        "credential_type": "oauth",
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "id_token": tokens.get("id_token", ""),
        "account_id": account_id,
        "user_email": email,
        "account_fingerprint": fingerprint,
        "credential_label": email or f"Codex account {fingerprint[:8]}",
        "model_ids": model_ids,
        "expiry": _token_expiry(tokens["access_token"]),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    return {"pending": False, "credential": credential, "model_count": len(model_ids)}


async def refresh_codex_oauth_credential(credential_data: Dict[str, Any]) -> Dict[str, Any]:
    refresh_token = str(credential_data.get("refresh_token") or "").strip()
    if not refresh_token:
        raise CodexError("OpenAI Codex credential does not contain a refresh token.", 401)
    try:
        response = await post_async(
            await _auth_endpoint("oauth/token"),
            json={
                "client_id": await get_codex_client_id(),
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "scope": "openid profile email offline_access",
            },
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=30.0,
        )
    except (httpx.HTTPError, OSError) as exc:
        raise CodexError("Unable to reach the OpenAI token service.", 502) from exc
    if response.status_code != 200:
        raise _provider_error(response, "OpenAI rejected the Codex token refresh.")
    data = response.json()
    if not data.get("access_token"):
        raise CodexError("OpenAI token refresh did not return an access token.", 502)
    refreshed = dict(credential_data)
    refreshed.update(
        {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token") or refresh_token,
            "id_token": data.get("id_token") or credential_data.get("id_token", ""),
            "expiry": _token_expiry(data["access_token"]),
        }
    )
    account_id, email = _account_identity(refreshed)
    if account_id:
        refreshed["account_id"] = account_id
    if email:
        refreshed["user_email"] = email
        refreshed["credential_label"] = email
    return refreshed


def build_codex_headers(
    access_token: str,
    account_id: str = "",
    *,
    session_id: str = "",
    user_agent: str = "",
) -> Dict[str, str]:
    token = str(access_token or "").strip()
    if not token:
        raise ValueError("OpenAI Codex credential does not contain an access token.")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "originator": "codex_cli_rs",
        "User-Agent": str(user_agent or "codex_cli_rs/0.0.0 (Unknown 0; unknown)"),
    }
    if account_id:
        headers["ChatGPT-Account-Id"] = str(account_id)
    if session_id:
        headers["session_id"] = str(session_id)
    return headers


def parse_codex_model_ids(payload: Any) -> List[str]:
    """Normalize the account-scoped model catalog returned by Codex."""
    if isinstance(payload, list):
        values = payload
    elif isinstance(payload, dict):
        values = payload.get("data") or payload.get("models") or payload.get("results") or []
    else:
        values = []

    if isinstance(values, dict):
        values = [
            {**(value if isinstance(value, dict) else {}), "id": model_id}
            for model_id, value in values.items()
        ]
    if not isinstance(values, list):
        return []

    model_ids: List[str] = []
    seen = set()
    for item in values:
        raw_id = (
            item.get("id") or item.get("slug") or item.get("model") or item.get("name")
            if isinstance(item, dict)
            else item
        )
        model_id = str(raw_id or "").strip().removeprefix("models/")
        if (
            not model_id
            or len(model_id) > MAX_CODEX_MODEL_ID_LENGTH
            or not model_id.isprintable()
            or model_id in seen
        ):
            continue
        seen.add(model_id)
        model_ids.append(model_id)
        if len(model_ids) >= MAX_CODEX_MODELS:
            break
    return model_ids


async def fetch_codex_model_ids(access_token: str, account_id: str = "") -> List[str]:
    """Fetch the model entitlements declared for one OpenAI Codex account."""
    api_url = (await get_codex_api_url()).rstrip("/")
    headers = build_codex_headers(
        access_token,
        account_id,
        user_agent=await get_codex_user_agent(),
    )
    headers["Accept"] = "application/json"
    try:
        response = await get_async(
            f"{api_url}/models?client_version=1.0.0",
            headers=headers,
            timeout=30.0,
        )
    except (httpx.HTTPError, OSError) as exc:
        raise CodexError("Unable to retrieve the OpenAI Codex model catalog.", 502) from exc
    if response.status_code != 200:
        raise _provider_error(response, "OpenAI Codex model discovery failed.")
    try:
        model_ids = parse_codex_model_ids(response.json())
    except ValueError as exc:
        raise CodexError("OpenAI returned an invalid Codex model catalog.", 502) from exc
    if not model_ids:
        raise CodexError("OpenAI Codex did not return any available models.", 502)
    return model_ids


def gemini_request_to_codex(payload: Dict[str, Any], model: str, streaming: bool) -> Dict[str, Any]:
    """Translate the internal Gemini request into the Codex Responses shape."""
    del streaming  # The Codex backend requires SSE, even for downstream non-stream clients.
    instructions = ""
    response_input: List[Dict[str, Any]] = []
    system = payload.get("systemInstruction") or {}
    system_parts = system.get("parts") if isinstance(system, dict) else []
    instructions = "\n".join(
        str(part.get("text") or "")
        for part in system_parts or []
        if isinstance(part, dict) and part.get("text")
    ).strip()

    for content in payload.get("contents") or []:
        if not isinstance(content, dict):
            continue
        role = "assistant" if content.get("role") == "model" else "user"
        message_parts: List[Dict[str, Any]] = []
        for index, part in enumerate(content.get("parts") or []):
            if not isinstance(part, dict):
                continue
            if part.get("text") is not None:
                message_parts.append(
                    {
                        "type": "output_text" if role == "assistant" else "input_text",
                        "text": str(part.get("text") or ""),
                    }
                )
                continue
            inline_data = part.get("inlineData") or part.get("inline_data")
            if role == "user" and isinstance(inline_data, dict) and inline_data.get("data"):
                mime_type = str(
                    inline_data.get("mimeType")
                    or inline_data.get("mime_type")
                    or "application/octet-stream"
                )
                message_parts.append(
                    {
                        "type": "input_image",
                        "image_url": f"data:{mime_type};base64,{inline_data['data']}",
                    }
                )
                continue
            function_call = part.get("functionCall") or part.get("function_call")
            if isinstance(function_call, dict):
                name = str(function_call.get("name") or "tool")
                arguments = function_call.get("args") or {}
                response_input.append(
                    {
                        "type": "function_call",
                        "call_id": str(function_call.get("id") or f"call_{name}_{index}"),
                        "name": name,
                        "arguments": json.dumps(arguments, separators=(",", ":")),
                    }
                )
                continue
            function_response = part.get("functionResponse") or part.get("function_response")
            if isinstance(function_response, dict):
                name = str(function_response.get("name") or "tool")
                response_input.append(
                    {
                        "type": "function_call_output",
                        "call_id": str(function_response.get("id") or f"call_{name}_{index}"),
                        "output": json.dumps(
                            function_response.get("response") or {}, separators=(",", ":")
                        ),
                    }
                )

        if message_parts:
            response_input.append(
                {
                    "type": "message",
                    "role": role,
                    "content": message_parts,
                }
            )

    result: Dict[str, Any] = {
        "model": model,
        "input": response_input,
        "stream": True,
        "store": False,
        "include": ["reasoning.encrypted_content"],
    }
    if instructions:
        result["instructions"] = instructions

    tools: List[Dict[str, Any]] = []
    for tool_group in payload.get("tools") or []:
        if not isinstance(tool_group, dict):
            continue
        for declaration in tool_group.get("functionDeclarations") or []:
            if not isinstance(declaration, dict) or not declaration.get("name"):
                continue
            tool: Dict[str, Any] = {
                "type": "function",
                "name": str(declaration["name"])[:128],
                "parameters": declaration.get("parametersJsonSchema")
                or declaration.get("parameters")
                or {"type": "object", "properties": {}},
            }
            if declaration.get("description"):
                tool["description"] = str(declaration["description"])
            tools.append(tool)
    if tools:
        result["tools"] = tools

        function_config = (payload.get("toolConfig") or {}).get("functionCallingConfig") or {}
        mode = str(function_config.get("mode") or "").upper()
        allowed_names = function_config.get("allowedFunctionNames") or []
        if mode == "NONE":
            result["tool_choice"] = "none"
        elif mode == "ANY" and len(allowed_names) == 1:
            result["tool_choice"] = {"type": "function", "name": str(allowed_names[0])}
        elif mode == "ANY":
            result["tool_choice"] = "required"
    return result


def codex_response_to_gemini(payload: Dict[str, Any]) -> Dict[str, Any]:
    output = payload.get("output")
    if not isinstance(output, list):
        raise ValueError("OpenAI Codex response does not contain an output array.")
    parts: List[Dict[str, Any]] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "function_call":
            try:
                arguments = json.loads(item.get("arguments") or "{}")
            except ValueError:
                arguments = {"raw": str(item.get("arguments") or "")}
            parts.append(
                {
                    "functionCall": {
                        "id": item.get("call_id") or item.get("id"),
                        "name": item.get("name") or "tool",
                        "args": arguments,
                    }
                }
            )
            continue
        if item.get("type") in {"reasoning", "reasoning_summary"}:
            summary = item.get("summary") or item.get("content") or []
            for content in summary if isinstance(summary, list) else []:
                if isinstance(content, dict) and content.get("text"):
                    parts.append({"text": str(content["text"]), "thought": True})
            continue
        for content in item.get("content") or []:
            if not isinstance(content, dict):
                continue
            text = content.get("text")
            if text:
                parts.append({"text": str(text)})
    usage = payload.get("usage") or {}
    result: Dict[str, Any] = {
        "candidates": [
            {
                "index": 0,
                "content": {"role": "model", "parts": parts},
                "finishReason": "STOP",
            }
        ]
    }
    if usage:
        result["usageMetadata"] = {
            "promptTokenCount": int(usage.get("input_tokens") or 0),
            "candidatesTokenCount": int(usage.get("output_tokens") or 0),
            "totalTokenCount": int(usage.get("total_tokens") or 0),
        }
    return result


def codex_stream_line_to_gemini(line: Any) -> Optional[str]:
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
    event_type = str(payload.get("type") or "")
    if event_type in {"error", "response.failed"}:
        error = payload.get("error") or (payload.get("response") or {}).get("error") or {}
        error_code = str(error.get("code") or error.get("type") or "").strip().lower()
        message = str(error.get("message") or "OpenAI Codex streaming request failed.").strip()
        status_code = 502
        if error_code in {"model_not_found", "not_found"}:
            status_code = 404
        elif error_code in {"rate_limit_exceeded", "rate_limit_error"}:
            status_code = 429
        elif error_code in {"authentication_error", "invalid_api_key"}:
            status_code = 401
        raise CodexError(message[:500], status_code)
    if event_type == "response.output_text.delta":
        delta = str(payload.get("delta") or "")
        if not delta:
            return None
        return "data: " + json.dumps(
            {"candidates": [{"index": 0, "content": {"role": "model", "parts": [{"text": delta}]}}]}
        )
    if event_type in {"response.reasoning_summary_text.delta", "response.reasoning_text.delta"}:
        delta = str(payload.get("delta") or "")
        if not delta:
            return None
        return "data: " + json.dumps(
            {
                "candidates": [
                    {
                        "index": 0,
                        "content": {
                            "role": "model",
                            "parts": [{"text": delta, "thought": True}],
                        },
                    }
                ]
            }
        )
    if event_type == "response.output_item.done":
        item = payload.get("item") or {}
        if not isinstance(item, dict) or item.get("type") != "function_call":
            return None
        try:
            arguments = json.loads(item.get("arguments") or "{}")
        except ValueError:
            arguments = {"raw": str(item.get("arguments") or "")}
        return "data: " + json.dumps(
            {
                "candidates": [
                    {
                        "index": 0,
                        "content": {
                            "role": "model",
                            "parts": [
                                {
                                    "functionCall": {
                                        "id": item.get("call_id") or item.get("id"),
                                        "name": item.get("name") or "tool",
                                        "args": arguments,
                                    }
                                }
                            ],
                        },
                    }
                ]
            }
        )
    if event_type in {"response.completed", "response.done"}:
        response = payload.get("response") or payload
        usage = response.get("usage") if isinstance(response, dict) else None
        result: Dict[str, Any] = {
            "candidates": [
                {"index": 0, "content": {"role": "model", "parts": []}, "finishReason": "STOP"}
            ]
        }
        if isinstance(usage, dict):
            result["usageMetadata"] = {
                "promptTokenCount": int(usage.get("input_tokens") or 0),
                "candidatesTokenCount": int(usage.get("output_tokens") or 0),
                "totalTokenCount": int(usage.get("total_tokens") or 0),
            }
        return "data: " + json.dumps(result)
    return None
