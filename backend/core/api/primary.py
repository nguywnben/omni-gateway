import asyncio
import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from config import (
    get_antigravity_api_url,
    get_antigravity_payload_user_agent,
    get_antigravity_stream_to_nonstream,
    get_antigravity_switch_credential_enabled,
    get_antigravity_user_agent,
    get_auto_disable_error_codes,
    get_google_ai_studio_api_url,
    get_token_compression_config,
    get_upstream_timeout_seconds,
    get_xai_api_url,
    get_xai_user_agent,
)
from core.api.utils import (
    collect_streaming_response,
    get_retry_config,
    handle_error_with_retry,
    parse_and_log_cooldown,
    record_api_call_error,
    record_api_call_success,
    record_model_route_miss,
    record_unassigned_api_call_error,
)
from core.credential_manager import credential_manager
from core.google_ai_studio import (
    build_api_key_headers,
    build_generation_url,
    build_models_url,
    parse_model_ids,
)
from core.httpx_client import get_async, post_async, stream_post_async
from core.model_blacklist import record_model_not_found
from core.provider_registry import (
    GOOGLE_AI_STUDIO,
    GOOGLE_ANTIGRAVITY,
    XAI,
    get_credential_provider,
)
from core.storage_adapter import get_storage_adapter
from core.token_compression import (
    CompressionResult,
    CompressionSettings,
    compress_gemini_request,
)
from core.usage_stats import (
    extract_token_usage_from_response,
    extract_token_usage_from_stream_chunk,
)
from core.xai import (
    build_xai_headers,
    fetch_xai_model_ids,
    gemini_request_to_xai,
    xai_response_to_gemini,
    xai_stream_line_to_gemini,
)
from fastapi import Response
from log import log

SESSION_TTL_SECONDS = 6 * 60 * 60
MAX_SESSION_STATES = 1024
_REDIS_KEY_PREFIX = "primary:session:"
MAX_MODEL_ROUTE_ATTEMPTS = 128


@dataclass
class PrimarySessionState:
    conversation_id: str
    trajectory_id: str
    session_id: str
    step_index: int
    created_at: float
    last_used_at: float


@dataclass(frozen=True)
class ProviderRequestContext:
    provider_id: str
    target_url: str
    headers: Dict[str, str]
    payload: Dict[str, Any]
    request_metrics: Dict[str, Any]


_session_states: Dict[str, PrimarySessionState] = {}


_redis_client = None
_redis_checked = False


async def _get_redis():
    global _redis_client, _redis_checked
    if _redis_checked:
        return _redis_client
    _redis_checked = True
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return None
    try:
        import redis.asyncio as aioredis  # type: ignore

        client = aioredis.from_url(redis_url, decode_responses=True)
        await client.ping()
        _redis_client = client
        log.info("[SESSION] Redis session store enabled")
    except Exception as e:
        log.warning(f"[SESSION] Redis unavailable, falling back to in-memory: {e}")
    return _redis_client


def _extract_first_user_text(request_payload: Dict[str, Any]) -> str:
    contents = request_payload.get("contents", [])
    if not isinstance(contents, list):
        return ""
    for content in contents:
        if not isinstance(content, dict) or content.get("role") != "user":
            continue
        parts = content.get("parts", [])
        if not isinstance(parts, list):
            continue
        for part in parts:
            if isinstance(part, dict) and part.get("text"):
                return str(part["text"])
    return ""


def _session_key(request_payload: Dict[str, Any], model: str = "") -> str:
    session_id = request_payload.get("sessionId")
    if session_id:
        return f"session:{session_id}"
    model_prefix = f"model:{model}:" if model else ""
    first_user_text = _extract_first_user_text(request_payload)
    if first_user_text:
        digest = hashlib.sha256(first_user_text.encode("utf-8")).hexdigest()[:32]
        return f"{model_prefix}text:{digest}"
    return f"{model_prefix}default"


def _prune_session_states(now: float) -> None:
    expired = [k for k, s in _session_states.items() if now - s.last_used_at > SESSION_TTL_SECONDS]
    for k in expired:
        _session_states.pop(k, None)
    if len(_session_states) <= MAX_SESSION_STATES:
        return
    overflow = len(_session_states) - MAX_SESSION_STATES
    oldest = sorted(_session_states.items(), key=lambda item: item[1].last_used_at)
    for k, _ in oldest[:overflow]:
        _session_states.pop(k, None)


def _make_new_state(first_user_text: str, now: float) -> PrimarySessionState:
    if first_user_text:
        digest = hashlib.sha256(first_user_text.encode("utf-8")).digest()
        session_id_val = int.from_bytes(digest[:8], "big") & 0x7FFFFFFFFFFFFFFF
        session_id = f"-{session_id_val}"
    else:
        session_id = f"-{uuid.uuid4().int % 9_000_000_000_000_000_000}"
    return PrimarySessionState(
        conversation_id=str(uuid.uuid4()),
        trajectory_id=str(uuid.uuid4()),
        session_id=session_id,
        step_index=1,
        created_at=now,
        last_used_at=now,
    )


async def _get_session_state(
    request_payload: Dict[str, Any], model: str = ""
) -> PrimarySessionState:
    now = time.time()
    key = _session_key(request_payload, model)
    first_user_text = _extract_first_user_text(request_payload)

    redis = await _get_redis()
    if redis is not None:
        redis_key = f"{_REDIS_KEY_PREFIX}{key}"
        try:
            raw = await redis.get(redis_key)
            if raw:
                data = json.loads(raw)
                state = PrimarySessionState(**data)
                state.step_index += 1
                state.last_used_at = now
            else:
                state = _make_new_state(first_user_text, now)
            await redis.set(redis_key, json.dumps(state.__dict__), ex=SESSION_TTL_SECONDS)
            return state
        except Exception as e:
            log.warning(f"[SESSION] Redis error, falling back to memory: {e}")

    _prune_session_states(now)
    state = _session_states.get(key)
    if state:
        state.step_index += 1
        state.last_used_at = now
        return state
    state = _make_new_state(first_user_text, now)
    _session_states[key] = state
    return state


def _generate_request_id(conversation_id: str, trajectory_id: str, step: int) -> str:
    unix_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    return f"agent/{conversation_id}/{unix_ms}/{trajectory_id}/{step}"


def _build_labels(model: str, trajectory_id: str, step: int) -> Dict[str, str]:
    used_claude = "claude" in model.lower()
    return {
        "last_step_index": str(step),
        "model_enum": model,
        "trajectory_id": trajectory_id,
        "used_claude": str(used_claude).lower(),
        "used_claude_conservative": str(used_claude).lower(),
    }


def _apply_credit_mode(payload: Dict[str, Any], enabled: bool) -> None:
    if enabled:
        payload["enabledCreditTypes"] = ["GOOGLE_ONE_AI"]
    else:
        payload.pop("enabledCreditTypes", None)


async def wrap_cli_request(
    gemini_request: Dict[str, Any],
    model: str,
    project_id: str,
    enable_credit: bool = False,
) -> Tuple[Dict[str, Any], str, CompressionResult]:
    original_inner = dict(gemini_request)
    state = await _get_session_state(original_inner, model)
    compression_result = compress_gemini_request(
        original_inner,
        CompressionSettings(**await get_token_compression_config()),
    )
    inner = dict(compression_result.request)

    if compression_result.applied:
        log.info(
            f"Compressed request history for model={model}: "
            f"removed_contents={compression_result.removed_contents}, "
            f"estimated_tokens={compression_result.original_estimated_tokens}"
            f"->{compression_result.final_estimated_tokens}, "
            f"reason={compression_result.reason}."
        )

    inner.pop("safetySettings", None)

    if not inner.get("sessionId"):
        inner["sessionId"] = state.session_id

    inner["labels"] = _build_labels(model, state.trajectory_id, state.step_index)

    tool_config = inner.get("toolConfig") or {}
    func_config = tool_config.get("functionCallingConfig") or {}
    if "mode" not in func_config:
        func_config["mode"] = "VALIDATED"
    tool_config["functionCallingConfig"] = func_config
    inner["toolConfig"] = tool_config

    request_id = _generate_request_id(state.conversation_id, state.trajectory_id, state.step_index)

    payload = {
        "project": project_id,
        "requestId": request_id,
        "request": inner,
        "model": model,
        "userAgent": await get_antigravity_payload_user_agent(),
        "requestType": "agent",
    }
    _apply_credit_mode(payload, enable_credit)
    return payload, request_id, compression_result


async def build_primary_headers(access_token: str, model: str = "") -> Dict[str, str]:
    return {
        "User-Agent": await get_antigravity_user_agent(),
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
    }


async def prepare_provider_request(
    credential_data: Dict[str, Any],
    body: Dict[str, Any],
    *,
    streaming: bool,
    extra_headers: Optional[Dict[str, str]] = None,
) -> ProviderRequestContext:
    """Build the provider-specific URL, authentication, and request payload."""
    provider_id = get_credential_provider(credential_data)
    model_name = str(body.get("model") or "").strip()
    inner_request = body.get("request", body)

    if provider_id == GOOGLE_AI_STUDIO:
        api_key = str(credential_data.get("api_key") or "").strip()
        compression_result = compress_gemini_request(
            dict(inner_request),
            CompressionSettings(**await get_token_compression_config()),
        )
        payload = dict(compression_result.request)
        for internal_key in ("model", "sessionId", "labels", "enabledCreditTypes"):
            payload.pop(internal_key, None)
        target_url = build_generation_url(
            await get_google_ai_studio_api_url(), model_name, streaming
        )
        auth_headers = build_api_key_headers(api_key)
    elif provider_id == XAI:
        access_token = (
            credential_data.get("api_key")
            or credential_data.get("access_token")
            or credential_data.get("token")
        )
        if not access_token:
            raise ValueError("Provider credential does not contain an access token or API key.")
        compression_result = compress_gemini_request(
            dict(inner_request),
            CompressionSettings(**await get_token_compression_config()),
        )
        payload = gemini_request_to_xai(dict(compression_result.request), model_name, streaming)
        target_url = f"{(await get_xai_api_url()).rstrip('/')}/chat/completions"
        auth_headers = build_xai_headers(str(access_token), await get_xai_user_agent())
    else:
        access_token = credential_data.get("access_token") or credential_data.get("token")
        if not access_token:
            raise ValueError("Credential does not contain an access token.")
        project_id = str(credential_data.get("project_id") or "").strip()
        if not project_id:
            raise ValueError("Credential does not contain a Project ID.")
        primary_url = await get_antigravity_api_url()
        operation = (
            "v1internal:streamGenerateContent?alt=sse"
            if streaming
            else "v1internal:generateContent"
        )
        target_url = f"{primary_url.rstrip('/')}/{operation}"
        auth_headers = await build_primary_headers(str(access_token))
        payload, _, compression_result = await wrap_cli_request(
            inner_request,
            model_name,
            project_id,
            enable_credit=bool(credential_data.get("enable_credit", False)),
        )

    if extra_headers:
        auth_headers.update(extra_headers)
        if provider_id == GOOGLE_AI_STUDIO:
            auth_headers.pop("Authorization", None)
            auth_headers["x-goog-api-key"] = str(credential_data.get("api_key") or "")
        elif provider_id == XAI:
            auth_headers.pop("x-goog-api-key", None)
            access_token = (
                credential_data.get("api_key")
                or credential_data.get("access_token")
                or credential_data.get("token")
            )
            auth_headers["Authorization"] = f"Bearer {access_token}"
        else:
            auth_headers.pop("x-goog-api-key", None)
            access_token = credential_data.get("access_token") or credential_data.get("token")
            auth_headers["Authorization"] = f"Bearer {access_token}"

    return ProviderRequestContext(
        provider_id=provider_id,
        target_url=target_url,
        headers=auth_headers,
        payload=payload,
        request_metrics=compression_result.as_metrics(),
    )


def _is_retryable_status(status_code: int, disable_error_codes: List[int]) -> bool:
    return status_code in (429, 503) or status_code in disable_error_codes


def _normalize_model_candidates(
    body: Dict[str, Any],
    model_candidates: Optional[List[str]],
) -> List[str]:
    values = model_candidates or [str(body.get("model") or "")]
    candidates: List[str] = []
    seen = set()
    for value in values:
        model_name = str(value or "").strip()
        if model_name and model_name not in seen:
            seen.add(model_name)
            candidates.append(model_name)
    return candidates


async def _switch_credential_for_retry(
    *,
    refresh_credential_fast,
    log_prefix: str,
) -> bool:
    """Acquire a new credential after the current attempt has been recorded."""
    if await refresh_credential_fast():
        return True

    log.warning(f"{log_prefix} No alternate credential is currently available.")
    return False


async def _exclude_missing_model_route(
    *,
    route_exclusions: set[tuple[str, str]],
    provider_id: str,
    model_name: str,
) -> None:
    """Exclude a 404 route immediately and persist it when storage is available."""
    route_exclusions.add((provider_id, model_name))
    try:
        await record_model_not_found(provider_id, model_name)
    except Exception as exc:
        log.error(
            "Model route blacklist persistence failed "
            f"(provider={provider_id}, model={model_name}): {exc}"
        )


async def stream_request(
    body: Dict[str, Any],
    native: bool = False,
    headers: Optional[Dict[str, str]] = None,
    model_candidates: Optional[List[str]] = None,
    model_routing: bool = False,
):
    request_started_at = time.perf_counter()
    requested_model = str(body.get("model") or "")
    candidates = _normalize_model_candidates(body, model_candidates)
    route_exclusions: set[tuple[str, str]] = set()
    credential_route_exclusions: set[tuple[str, str]] = set()

    route_result = await credential_manager.get_valid_model_credential(
        candidates,
        mode="primary",
        respect_model_blacklist=model_routing,
        excluded_provider_models=route_exclusions,
        excluded_credential_models=credential_route_exclusions,
    )

    if not route_result:
        log.error("[provider stream] No credentials currently available")
        await record_unassigned_api_call_error(
            status_code=503, mode="primary", model_name=requested_model
        )
        yield Response(
            content=json.dumps({"error": "No credentials are available."}),
            status_code=503,
            media_type="application/json",
        )
        return

    model_name, current_file, credential_data = route_result
    request_body = {**body, "model": model_name}
    try:
        context = await prepare_provider_request(
            credential_data,
            request_body,
            streaming=True,
            extra_headers=headers,
        )
    except ValueError as exc:
        provider_id = get_credential_provider(credential_data)
        await record_api_call_error(
            credential_manager,
            current_file,
            500,
            None,
            mode="primary",
            model_name=model_name,
            error_message=str(exc),
            provider=provider_id,
        )
        yield Response(
            content=json.dumps({"error": str(exc)}),
            status_code=500,
            media_type="application/json",
        )
        return

    provider_id = context.provider_id
    target_url = context.target_url
    auth_headers = context.headers
    final_payload = context.payload
    request_metrics = context.request_metrics

    retry_config = await get_retry_config()
    max_retries = retry_config["max_retries"]
    retry_interval = retry_config["retry_interval"]
    switch_credential_enabled = await get_antigravity_switch_credential_enabled()

    DISABLE_ERROR_CODES = await get_auto_disable_error_codes()
    last_error_response = None
    retry_attempt = 0

    async def refresh_credential_fast():
        nonlocal model_name, current_file, credential_data, provider_id, request_body
        nonlocal target_url, auth_headers, final_payload, request_metrics
        route_result = await credential_manager.get_valid_model_credential(
            candidates,
            mode="primary",
            respect_model_blacklist=model_routing,
            excluded_provider_models=route_exclusions,
            excluded_credential_models=credential_route_exclusions,
        )
        if not route_result:
            return None
        model_name, current_file, credential_data = route_result
        request_body = {**body, "model": model_name}
        try:
            new_context = await prepare_provider_request(
                credential_data,
                request_body,
                streaming=True,
                extra_headers=headers,
            )
        except ValueError:
            await credential_manager.release_credential(current_file, mode="primary")
            return None
        provider_id = new_context.provider_id
        target_url = new_context.target_url
        auth_headers = new_context.headers
        final_payload = new_context.payload
        request_metrics = new_context.request_metrics
        return True

    attempt_limit = max_retries + MAX_MODEL_ROUTE_ATTEMPTS
    for attempt in range(attempt_limit + 1):
        received_content = False
        stream_token_usage: Dict[str, int] = {}
        need_retry = False
        model_route_retry = False

        try:
            async for chunk in stream_post_async(
                url=target_url,
                body=final_payload,
                native=native,
                headers=auth_headers,
                timeout=await get_upstream_timeout_seconds(),
            ):
                if isinstance(chunk, Response):
                    status_code = chunk.status_code
                    last_error_response = chunk

                    error_body = None
                    try:
                        error_body = (
                            chunk.body.decode("utf-8")
                            if isinstance(chunk.body, bytes)
                            else str(chunk.body)
                        )
                    except Exception:
                        error_body = ""

                    if status_code == 404:
                        credential_route_exclusions.add((current_file, model_name))
                        if model_routing:
                            log.warning(
                                f"[provider stream] model route not found; blacklisting provider={provider_id}, model={model_name}."
                            )
                            await _exclude_missing_model_route(
                                route_exclusions=route_exclusions,
                                provider_id=provider_id,
                                model_name=model_name,
                            )
                        else:
                            log.warning(
                                "[provider stream] credential could not serve the requested model; "
                                f"trying another route (credential={current_file}, model={model_name})."
                            )
                        await record_model_route_miss(
                            credential_manager,
                            current_file,
                            model_name=model_name,
                            provider=provider_id,
                        )
                        if attempt < attempt_limit:
                            need_retry = True
                            model_route_retry = True
                            break
                        yield chunk
                        return
                    elif _is_retryable_status(status_code, DISABLE_ERROR_CODES):
                        log.warning(
                            f"[provider stream] streaming request failed (status={status_code}), credential={current_file}, response={error_body[:500] if error_body else 'None'}"
                        )

                        cooldown_until = None
                        if (status_code == 429 or status_code == 503) and error_body:
                            try:
                                cooldown_until = await parse_and_log_cooldown(
                                    error_body, mode="primary"
                                )
                            except Exception:
                                pass

                        await record_api_call_error(
                            credential_manager,
                            current_file,
                            status_code,
                            cooldown_until,
                            mode="primary",
                            model_name=model_name,
                            error_message=error_body,
                            provider=provider_id,
                        )

                        should_retry = await handle_error_with_retry(
                            credential_manager,
                            status_code,
                            current_file,
                            retry_config["retry_enabled"],
                            retry_attempt,
                            max_retries,
                            retry_interval,
                            mode="primary",
                        )

                        if should_retry:
                            retry_attempt += 1
                            need_retry = True
                            break
                        else:
                            log.error(
                                "[provider stream] Maximum number of retries reached or should not be retried, returning original error"
                            )
                            yield chunk
                            return
                    else:
                        log.error(
                            f"[provider stream] streaming request failed with a non-retryable status (status={status_code}), credential={current_file}, response={error_body[:500] if error_body else 'None'}"
                        )
                        await record_api_call_error(
                            credential_manager,
                            current_file,
                            status_code,
                            None,
                            mode="primary",
                            model_name=model_name,
                            error_message=error_body,
                            provider=provider_id,
                        )
                        yield chunk
                        return
                else:
                    if provider_id == XAI:
                        chunk = xai_stream_line_to_gemini(chunk)
                        if not chunk:
                            continue

                    if not received_content:
                        received_content = True
                        log.debug(
                            f"[provider stream] started receiving streaming responses, model: {model_name}"
                        )

                    chunk_token_usage = extract_token_usage_from_stream_chunk(chunk)
                    if any(chunk_token_usage.values()):
                        stream_token_usage = chunk_token_usage

                    if isinstance(chunk, bytes):
                        log.debug(f"[provider stream raw] chunk(bytes): {chunk}")
                    else:
                        log.debug(f"[provider stream raw] chunk(str): {chunk}")

                    yield chunk

            if received_content:
                await record_api_call_success(
                    credential_manager,
                    current_file,
                    mode="primary",
                    model_name=model_name,
                    token_usage=stream_token_usage,
                    request_metrics={
                        **request_metrics,
                        "latency_ms": round((time.perf_counter() - request_started_at) * 1000),
                        "retry_count": attempt,
                    },
                    provider=provider_id,
                )
                log.debug(f"[provider stream] Streaming response completed, model: {model_name}")
                return
            elif not need_retry:
                log.warning(
                    f"[provider stream] received an empty reply with no content, voucher: {current_file}"
                )
                await record_api_call_error(
                    credential_manager,
                    current_file,
                    200,
                    None,
                    mode="primary",
                    model_name=model_name,
                    error_message="Empty response from API",
                    provider=provider_id,
                )

                if retry_attempt < max_retries:
                    retry_attempt += 1
                    need_retry = True
                else:
                    log.error("[provider stream] Empty response reaches maximum number of retries")
                    yield Response(
                        content=json.dumps({"error": "Empty response returned by service"}),
                        status_code=500,
                        media_type="application/json",
                    )
                    return

            if need_retry:
                if model_route_retry:
                    log.info("[provider stream] Trying the next compatible model route.")
                else:
                    log.info(
                        "[provider stream] retrying request "
                        f"(attempt {retry_attempt + 1}/{max_retries + 1})."
                    )

                if model_route_retry or switch_credential_enabled:
                    switched = await _switch_credential_for_retry(
                        refresh_credential_fast=refresh_credential_fast,
                        log_prefix="[provider stream]",
                    )
                    if not switched:
                        log.error(
                            "[provider stream] No credentials or tokens available when retrying"
                        )
                        if model_route_retry and last_error_response is not None:
                            yield last_error_response
                            return
                        yield Response(
                            content=json.dumps({"error": "No credentials are available."}),
                            status_code=503,
                            media_type="application/json",
                        )
                        return
                continue

        except Exception as e:
            log.error(
                f"[provider stream] Streaming Request Exception: {e}, Credentials: {current_file}"
            )
            await record_api_call_error(
                credential_manager,
                current_file,
                500,
                None,
                mode="primary",
                model_name=model_name,
                error_message=str(e),
                provider=provider_id,
            )
            if retry_attempt < max_retries:
                retry_attempt += 1
                log.info(
                    "[provider stream] retry after abnormality "
                    f"(attempt {retry_attempt + 1}/{max_retries + 1})..."
                )
                await asyncio.sleep(retry_interval)
                if switch_credential_enabled:
                    switched = await _switch_credential_for_retry(
                        refresh_credential_fast=refresh_credential_fast,
                        log_prefix="[provider stream]",
                    )
                    if not switched:
                        yield Response(
                            content=json.dumps({"error": "No credentials are available."}),
                            status_code=503,
                            media_type="application/json",
                        )
                        return
                continue
            else:
                log.error(f"[provider stream] all retries failed. Last exception: {e}")
                if last_error_response:
                    yield last_error_response
                else:
                    yield Response(
                        content=json.dumps(
                            {"error": "The upstream streaming request failed unexpectedly."}
                        ),
                        status_code=500,
                        media_type="application/json",
                    )
                return

    log.error("[provider stream] all retries failed.")
    if last_error_response:
        yield last_error_response
    else:
        yield Response(
            content=json.dumps({"error": "Request failed after all retries were exhausted."}),
            status_code=429,
            media_type="application/json",
        )


async def non_stream_request(
    body: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
    model_candidates: Optional[List[str]] = None,
    model_routing: bool = False,
) -> Response:
    request_started_at = time.perf_counter()

    if await get_antigravity_stream_to_nonstream():
        log.debug("[provider] Streaming collection mode for non-streaming requests")

        stream = stream_request(
            body=body,
            native=False,
            headers=headers,
            model_candidates=model_candidates,
            model_routing=model_routing,
        )

        return await collect_streaming_response(stream)

    log.debug("[provider] Direct non-streaming mode enabled")

    requested_model = str(body.get("model") or "")
    candidates = _normalize_model_candidates(body, model_candidates)
    route_exclusions: set[tuple[str, str]] = set()
    credential_route_exclusions: set[tuple[str, str]] = set()

    route_result = await credential_manager.get_valid_model_credential(
        candidates,
        mode="primary",
        respect_model_blacklist=model_routing,
        excluded_provider_models=route_exclusions,
        excluded_credential_models=credential_route_exclusions,
    )

    if not route_result:
        log.error("[provider] No credentials currently available")
        await record_unassigned_api_call_error(
            status_code=503, mode="primary", model_name=requested_model
        )
        return Response(
            content=json.dumps({"error": "No credentials are available."}),
            status_code=503,
            media_type="application/json",
        )

    model_name, current_file, credential_data = route_result
    request_body = {**body, "model": model_name}
    try:
        context = await prepare_provider_request(
            credential_data,
            request_body,
            streaming=False,
            extra_headers=headers,
        )
    except ValueError as exc:
        provider_id = get_credential_provider(credential_data)
        await record_api_call_error(
            credential_manager,
            current_file,
            500,
            None,
            mode="primary",
            model_name=model_name,
            error_message=str(exc),
            provider=provider_id,
        )
        return Response(
            content=json.dumps({"error": str(exc)}),
            status_code=500,
            media_type="application/json",
        )

    provider_id = context.provider_id
    target_url = context.target_url
    auth_headers = context.headers
    final_payload = context.payload
    request_metrics = context.request_metrics

    retry_config = await get_retry_config()
    max_retries = retry_config["max_retries"]
    retry_interval = retry_config["retry_interval"]
    switch_credential_enabled = await get_antigravity_switch_credential_enabled()

    DISABLE_ERROR_CODES = await get_auto_disable_error_codes()
    last_error_response = None
    retry_attempt = 0

    async def refresh_credential_fast():
        nonlocal model_name, current_file, credential_data, provider_id, request_body
        nonlocal target_url, auth_headers, final_payload, request_metrics
        route_result = await credential_manager.get_valid_model_credential(
            candidates,
            mode="primary",
            respect_model_blacklist=model_routing,
            excluded_provider_models=route_exclusions,
            excluded_credential_models=credential_route_exclusions,
        )
        if not route_result:
            return None
        model_name, current_file, credential_data = route_result
        request_body = {**body, "model": model_name}
        try:
            new_context = await prepare_provider_request(
                credential_data,
                request_body,
                streaming=False,
                extra_headers=headers,
            )
        except ValueError:
            await credential_manager.release_credential(current_file, mode="primary")
            return None
        provider_id = new_context.provider_id
        target_url = new_context.target_url
        auth_headers = new_context.headers
        final_payload = new_context.payload
        request_metrics = new_context.request_metrics
        return True

    attempt_limit = max_retries + MAX_MODEL_ROUTE_ATTEMPTS
    for attempt in range(attempt_limit + 1):
        need_retry = False

        try:
            response = await post_async(
                url=target_url,
                json=final_payload,
                headers=auth_headers,
                timeout=await get_upstream_timeout_seconds(),
            )

            status_code = response.status_code

            if status_code == 200:
                if not response.content or len(response.content) == 0:
                    log.warning(
                        f"[provider] Received 200 response but the content is empty, voucher: {current_file}"
                    )

                    await record_api_call_error(
                        credential_manager,
                        current_file,
                        200,
                        None,
                        mode="primary",
                        model_name=model_name,
                        error_message="Empty response from API",
                        provider=provider_id,
                    )

                    if retry_attempt < max_retries:
                        retry_attempt += 1
                        need_retry = True
                    else:
                        log.error("[provider] Empty response reaches maximum number of retries")
                        return Response(
                            content=json.dumps({"error": "Empty response returned by service"}),
                            status_code=503,
                            media_type="application/json",
                        )
                else:
                    response_content = response.content
                    if provider_id == XAI:
                        try:
                            response_content = json.dumps(
                                xai_response_to_gemini(response.json())
                            ).encode("utf-8")
                        except (ValueError, TypeError) as exc:
                            await record_api_call_error(
                                credential_manager,
                                current_file,
                                502,
                                None,
                                mode="primary",
                                model_name=model_name,
                                error_message=str(exc),
                                provider=provider_id,
                            )
                            return Response(
                                content=json.dumps({"error": "Grok returned an invalid response."}),
                                status_code=502,
                                media_type="application/json",
                            )
                    token_usage = extract_token_usage_from_response(response_content)
                    await record_api_call_success(
                        credential_manager,
                        current_file,
                        mode="primary",
                        model_name=model_name,
                        token_usage=token_usage,
                        status_code=status_code,
                        request_metrics={
                            **request_metrics,
                            "latency_ms": round((time.perf_counter() - request_started_at) * 1000),
                            "retry_count": attempt,
                        },
                        provider=provider_id,
                    )
                    return Response(
                        content=response_content,
                        status_code=200,
                        media_type="application/json",
                    )

            if status_code != 200:
                last_error_response = Response(
                    content=response.content,
                    status_code=status_code,
                    headers=dict(response.headers),
                )

                error_text = ""
                try:
                    error_text = response.text
                except Exception:
                    pass

                if status_code == 404:
                    credential_route_exclusions.add((current_file, model_name))
                    if model_routing:
                        log.warning(
                            f"[provider] model route not found; blacklisting provider={provider_id}, model={model_name}."
                        )
                        await _exclude_missing_model_route(
                            route_exclusions=route_exclusions,
                            provider_id=provider_id,
                            model_name=model_name,
                        )
                    else:
                        log.warning(
                            "[provider] credential could not serve the requested model; "
                            f"trying another route (credential={current_file}, model={model_name})."
                        )
                    await record_model_route_miss(
                        credential_manager,
                        current_file,
                        model_name=model_name,
                        provider=provider_id,
                    )
                    if attempt < attempt_limit and await refresh_credential_fast():
                        continue
                    return last_error_response
                elif _is_retryable_status(status_code, DISABLE_ERROR_CODES):
                    log.warning(
                        f"[provider] non-streaming request failed (status={status_code}), credential={current_file}, response={error_text[:500] if error_text else 'None'}"
                    )

                    cooldown_until = None
                    if (status_code == 429 or status_code == 503) and error_text:
                        try:
                            cooldown_until = await parse_and_log_cooldown(
                                error_text, mode="primary"
                            )
                        except Exception:
                            pass

                    await record_api_call_error(
                        credential_manager,
                        current_file,
                        status_code,
                        cooldown_until,
                        mode="primary",
                        model_name=model_name,
                        error_message=error_text,
                        provider=provider_id,
                    )

                    should_retry = await handle_error_with_retry(
                        credential_manager,
                        status_code,
                        current_file,
                        retry_config["retry_enabled"],
                        retry_attempt,
                        max_retries,
                        retry_interval,
                        mode="primary",
                    )

                    if should_retry:
                        retry_attempt += 1
                        need_retry = True
                    else:
                        log.error(
                            "[provider] Maximum number of retries reached or should not be retried, returning original error"
                        )
                        return last_error_response
                else:
                    log.error(
                        f"[provider] non-streaming request failed with a non-retryable status (status={status_code}), credential={current_file}, response={error_text[:500] if error_text else 'None'}"
                    )
                    await record_api_call_error(
                        credential_manager,
                        current_file,
                        status_code,
                        None,
                        mode="primary",
                        model_name=model_name,
                        error_message=error_text,
                        provider=provider_id,
                    )
                    return last_error_response

            if need_retry:
                log.info(
                    f"[provider] retrying request (attempt {retry_attempt + 1}/{max_retries + 1})."
                )

                if switch_credential_enabled:
                    switched = await _switch_credential_for_retry(
                        refresh_credential_fast=refresh_credential_fast,
                        log_prefix="[provider]",
                    )
                    if not switched:
                        log.error("[provider] No credentials or tokens available when retrying")
                        return Response(
                            content=json.dumps({"error": "No credentials are available."}),
                            status_code=503,
                            media_type="application/json",
                        )
                continue

        except Exception as e:
            log.error(
                f"[provider] non-streaming request raised an exception: {e}; credential={current_file}"
            )
            await record_api_call_error(
                credential_manager,
                current_file,
                500,
                None,
                mode="primary",
                model_name=model_name,
                error_message=str(e),
                provider=provider_id,
            )
            if retry_attempt < max_retries:
                retry_attempt += 1
                log.info(
                    "[provider] Retry after exception "
                    f"(attempt {retry_attempt + 1}/{max_retries + 1})..."
                )
                await asyncio.sleep(retry_interval)
                if switch_credential_enabled:
                    switched = await _switch_credential_for_retry(
                        refresh_credential_fast=refresh_credential_fast,
                        log_prefix="[provider]",
                    )
                    if not switched:
                        return Response(
                            content=json.dumps({"error": "No credentials are available."}),
                            status_code=503,
                            media_type="application/json",
                        )
                continue
            else:
                log.error(f"[provider] all retries failed. Last exception: {e}")
                if last_error_response:
                    return last_error_response
                else:
                    return Response(
                        content=json.dumps({"error": "The upstream request failed unexpectedly."}),
                        status_code=500,
                        media_type="application/json",
                    )

    log.error("[provider] all retries failed.")
    if last_error_response:
        return last_error_response
    else:
        return Response(
            content=json.dumps({"error": "Request failed after all retries were exhausted."}),
            status_code=500,
            media_type="application/json",
        )


async def get_configured_provider_model_ids() -> Dict[str, set[str]]:
    """Return enabled providers and model metadata already stored per credential."""
    storage_adapter = await get_storage_adapter()
    provider_models: Dict[str, set[str]] = {}
    for filename in await storage_adapter.list_credentials(mode="primary"):
        state = await storage_adapter.get_credential_state(filename, mode="primary")
        if state.get("disabled"):
            continue
        credential_data = await storage_adapter.get_credential(filename, mode="primary")
        if not credential_data:
            continue
        provider_id = get_credential_provider(credential_data)
        model_ids = provider_models.setdefault(provider_id, set())
        stored_model_ids = credential_data.get("model_ids")
        if isinstance(stored_model_ids, list):
            model_ids.update(
                str(model_id).removeprefix("models/").strip()
                for model_id in stored_model_ids
                if str(model_id or "").strip()
            )
    return provider_models


async def get_configured_provider_ids() -> set[str]:
    """Return providers with at least one enabled credential."""
    return set(await get_configured_provider_model_ids())


async def fetch_provider_model_ids(
    provider_id: str,
    stored_model_ids: Optional[set[str]] = None,
) -> set[str]:
    """Discover model IDs exposed by one configured provider."""
    if stored_model_ids is None:
        provider_models = await get_configured_provider_model_ids()
        stored_model_ids = provider_models.get(provider_id, set())
    model_ids = set(stored_model_ids)

    if provider_id == GOOGLE_ANTIGRAVITY:
        cred_result = await credential_manager.get_valid_credential(
            mode="primary", provider_id=GOOGLE_ANTIGRAVITY
        )
        if cred_result:
            current_file, credential_data = cred_result
            try:
                access_token = credential_data.get("access_token") or credential_data.get("token")
                if access_token:
                    response = await post_async(
                        url=(
                            f"{(await get_antigravity_api_url()).rstrip('/')}"
                            "/v1internal:fetchAvailableModels"
                        ),
                        json={},
                        headers=await build_primary_headers(str(access_token)),
                    )
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data.get("models"), dict):
                            model_ids.update(data["models"].keys())
                            if "claude-sonnet-4-6" in data["models"]:
                                model_ids.add("claude-sonnet-4-6-thinking")
                            if "claude-opus-4-6-thinking" in data["models"]:
                                model_ids.add("claude-opus-4-6")
                    else:
                        log.warning(
                            "Google Antigravity model discovery failed with HTTP "
                            f"{response.status_code}."
                        )
            except Exception as exc:
                log.warning(f"Google Antigravity model discovery failed: {exc}")
            finally:
                await credential_manager.release_credential(current_file, mode="primary")
    elif provider_id == GOOGLE_AI_STUDIO:
        cred_result = await credential_manager.get_valid_credential(
            mode="primary", provider_id=GOOGLE_AI_STUDIO
        )
        if cred_result:
            current_file, credential_data = cred_result
            try:
                response = await get_async(
                    build_models_url(await get_google_ai_studio_api_url()),
                    headers=build_api_key_headers(credential_data.get("api_key", "")),
                    timeout=30.0,
                )
                if response.status_code == 200:
                    model_ids.update(parse_model_ids(response.json()))
                else:
                    log.warning(
                        f"Google AI Studio model discovery failed with HTTP {response.status_code}."
                    )
            except Exception as exc:
                log.warning(f"Google AI Studio model discovery failed: {exc}")
            finally:
                await credential_manager.release_credential(current_file, mode="primary")
    elif provider_id == XAI:
        cred_result = await credential_manager.get_valid_credential(mode="primary", provider_id=XAI)
        if cred_result:
            current_file, credential_data = cred_result
            try:
                access_token = (
                    credential_data.get("api_key")
                    or credential_data.get("access_token")
                    or credential_data.get("token")
                )
                if access_token:
                    model_ids.update(await fetch_xai_model_ids(str(access_token)))
            except Exception as exc:
                log.warning(f"Grok model discovery failed: {exc}")
            finally:
                await credential_manager.release_credential(current_file, mode="primary")

    return model_ids


async def fetch_configured_provider_models() -> Dict[str, List[str]]:
    """Return active provider model catalogs with provider provenance."""
    stored_provider_models = await get_configured_provider_model_ids()
    provider_ids = sorted(stored_provider_models)
    discovered = await asyncio.gather(
        *(
            fetch_provider_model_ids(provider_id, stored_provider_models[provider_id])
            for provider_id in provider_ids
        ),
        return_exceptions=True,
    )
    provider_models: Dict[str, List[str]] = {}
    for provider_id, result in zip(provider_ids, discovered):
        if isinstance(result, Exception):
            log.warning(f"{provider_id} model discovery failed: {result}")
            result = stored_provider_models[provider_id]
        provider_models[provider_id] = sorted(result)
    return provider_models


async def fetch_quota_info(access_token: str) -> Dict[str, Any]:

    headers = await build_primary_headers(access_token)

    try:
        primary_url = await get_antigravity_api_url()

        response = await post_async(
            url=f"{primary_url}/v1internal:fetchAvailableModels",
            json={},
            headers=headers,
            timeout=30.0,
        )

        if response.status_code == 200:
            data = response.json()
            log.debug(
                f"[provider quota] Raw response: {json.dumps(data, ensure_ascii=False)[:500]}"
            )

            quota_info = {}

            if "models" in data and isinstance(data["models"], dict):
                for model_id, model_data in data["models"].items():
                    if isinstance(model_data, dict) and "quotaInfo" in model_data:
                        quota = model_data["quotaInfo"]
                        remaining = quota.get("remainingFraction", 0)
                        reset_time_raw = quota.get("resetTime", "")

                        reset_time_beijing = "N/A"
                        if reset_time_raw:
                            try:
                                utc_date = datetime.fromisoformat(
                                    reset_time_raw.replace("Z", "+00:00")
                                )

                                from datetime import timedelta

                                beijing_date = utc_date + timedelta(hours=8)
                                reset_time_beijing = beijing_date.strftime("%m-%d %H:%M")
                            except Exception as e:
                                log.warning(f"[provider quota] Failed to parse reset time: {e}")

                        quota_info[model_id] = {
                            "remaining": remaining,
                            "resetTime": reset_time_beijing,
                            "resetTimeRaw": reset_time_raw,
                        }

            return {"success": True, "models": quota_info}
        else:
            log.error(
                f"[provider quota] Failed to fetch quota ({response.status_code}): {response.text[:500]}"
            )
            return {"success": False, "error": f"API returned an error: {response.status_code}"}

    except Exception as e:
        import traceback

        log.error(f"[provider quota] Failed to fetch quota: {e}")
        log.error(f"[provider quota] Traceback: {traceback.format_exc()}")
        return {"success": False, "error": "Unable to retrieve provider quota information."}
