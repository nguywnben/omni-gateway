"""Internal implementation detail."""

import asyncio
import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Callable, Tuple

from fastapi import Response
from config import (
    get_antigravity_api_url,
    get_antigravity_payload_user_agent,
    get_antigravity_stream_to_nonstream,
    get_antigravity_switch_credential_enabled,
    get_antigravity_user_agent,
    get_auto_disable_error_codes,
)
from log import log

from core.credential_manager import credential_manager
from core.httpx_client import stream_post_async, post_async
from core.models import Model, model_to_dict
from core.usage_stats import (
    extract_token_usage_from_response,
    extract_token_usage_from_stream_chunk,
)


from core.api.utils import (
    handle_error_with_retry,
    get_retry_config,
    record_api_call_success,
    record_api_call_error,
    record_unassigned_api_call_error,
    parse_and_log_cooldown,
    collect_streaming_response,
)








SESSION_TTL_SECONDS = 6 * 60 * 60
MAX_SESSION_STATES = 1024
_REDIS_KEY_PREFIX = "primary:session:"


@dataclass
class PrimarySessionState:
    conversation_id: str
    trajectory_id: str
    session_id: str
    step_index: int
    created_at: float
    last_used_at: float



_session_states: Dict[str, PrimarySessionState] = {}


_redis_client = None
_redis_checked = False


async def _get_redis():
    """Internal implementation detail."""
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


async def _get_session_state(request_payload: Dict[str, Any], model: str = "") -> PrimarySessionState:
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


async def wrap_cli_request(
    gemini_request: Dict[str, Any],
    model: str,
    project_id: str,
) -> Tuple[Dict[str, Any], str]:
    """Internal implementation detail."""
    inner = dict(gemini_request)


    inner.pop("safetySettings", None)


    state = await _get_session_state(inner, model)


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
        "enabledCreditTypes": ["GOOGLE_ONE_AI"],
    }
    return payload, request_id




async def build_primary_headers(access_token: str, model: str = "") -> Dict[str, str]:
    """Internal implementation detail."""
    return {
        "User-Agent": await get_antigravity_user_agent(),
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
    }


def _is_retryable_status(status_code: int, disable_error_codes: List[int]) -> bool:
    """Internal implementation detail."""
    return status_code in (429, 503) or status_code in disable_error_codes


async def _switch_credential_for_retry(
    *,
    next_cred_task: Optional[asyncio.Task],
    retry_interval: float,
    refresh_credential_fast: Callable[[], Any],
    apply_cred_result: Callable[[Tuple[str, Dict[str, Any]]], bool],
    log_prefix: str,
) -> Tuple[bool, Optional[asyncio.Task]]:
    """Internal implementation detail."""
    if next_cred_task is not None:
        try:
            cred_result = await next_cred_task
            next_cred_task = None
            if cred_result and apply_cred_result(cred_result):
                await asyncio.sleep(retry_interval)
                return True, next_cred_task
        except Exception as e:
            log.warning(f"{log_prefix} Credential warming task failed: {e}")
            next_cred_task = None

    await asyncio.sleep(retry_interval)
    if await refresh_credential_fast():
        return True, next_cred_task

    return False, next_cred_task




async def stream_request(
    body: Dict[str, Any],
    native: bool = False,
    headers: Optional[Dict[str, str]] = None,
):
    """Internal implementation detail."""
    model_name = body.get("model", "")


    cred_result = await credential_manager.get_valid_credential(
        mode="primary", model_name=model_name
    )

    if not cred_result:

        log.error("[provider stream] No credentials currently available")
        await record_unassigned_api_call_error(
            status_code=500, mode="primary", model_name=model_name
        )
        yield Response(
            content=json.dumps({"error": "No credentials are available."}),
            status_code=500,
            media_type="application/json"
        )
        return

    current_file, credential_data = cred_result
    access_token = credential_data.get("access_token") or credential_data.get("token")
    project_id = credential_data.get("project_id", "")

    if not access_token:
        log.error(f"[provider stream] No access token in credential: {current_file}")
        await record_api_call_error(
            credential_manager, current_file, 500,
            None, mode="primary", model_name=model_name,
            error_message="No access token in credential"
        )
        yield Response(
            content=json.dumps({"error": "No access token in credential"}),
            status_code=500,
            media_type="application/json"
        )
        return


    primary_url = await get_antigravity_api_url()
    target_url = f"{primary_url}/v1internal:streamGenerateContent?alt=sse"

    auth_headers = await build_primary_headers(access_token)


    if headers:
        auth_headers.update(headers)


    inner_request = body.get("request", body)
    final_payload, _ = await wrap_cli_request(inner_request, model_name, project_id)


    retry_config = await get_retry_config()
    max_retries = retry_config["max_retries"]
    retry_interval = retry_config["retry_interval"]
    switch_credential_enabled = await get_antigravity_switch_credential_enabled()

    DISABLE_ERROR_CODES = await get_auto_disable_error_codes()
    last_error_response = None
    next_cred_task = None


    async def refresh_credential_fast():
        nonlocal current_file, access_token, auth_headers, project_id, final_payload
        cred_result = await credential_manager.get_valid_credential(
            mode="primary", model_name=model_name
        )
        if not cred_result:
            return None
        current_file, credential_data = cred_result
        access_token = credential_data.get("access_token") or credential_data.get("token")
        project_id = credential_data.get("project_id", "")
        if not access_token:
            return None

        auth_headers["Authorization"] = f"Bearer {access_token}"
        final_payload["project"] = project_id
        return True

    def apply_cred_result(cred_result: Tuple[str, Dict[str, Any]]) -> bool:
        nonlocal current_file, access_token, project_id, auth_headers, final_payload
        current_file, credential_data = cred_result
        access_token = credential_data.get("access_token") or credential_data.get("token")
        project_id = credential_data.get("project_id", "")
        if not access_token or not project_id:
            return False
        auth_headers["Authorization"] = f"Bearer {access_token}"
        final_payload["project"] = project_id
        return True

    for attempt in range(max_retries + 1):
        received_content = False
        stream_token_usage: Dict[str, int] = {}
        need_retry = False

        try:
            async for chunk in stream_post_async(
                url=target_url,
                body=final_payload,
                native=native,
                headers=auth_headers
            ):

                if isinstance(chunk, Response):
                    status_code = chunk.status_code
                    last_error_response = chunk


                    error_body = None
                    try:
                        error_body = chunk.body.decode('utf-8') if isinstance(chunk.body, bytes) else str(chunk.body)
                    except Exception:
                        error_body = ""


                    if _is_retryable_status(status_code, DISABLE_ERROR_CODES):
                        log.warning(f"[provider stream] streaming request failed (status={status_code}), credential={current_file}, response={error_body[:500] if error_body else 'None'}")


                        cooldown_until = None
                        if (status_code == 429 or status_code == 503) and error_body:
                            try:
                                cooldown_until = await parse_and_log_cooldown(error_body, mode="primary")
                            except Exception:
                                pass


                        if switch_credential_enabled and next_cred_task is None and attempt < max_retries:
                            next_cred_task = asyncio.create_task(
                                credential_manager.get_valid_credential(
                                    mode="primary", model_name=model_name
                                )
                            )


                        await record_api_call_error(
                            credential_manager, current_file, status_code,
                            cooldown_until, mode="primary", model_name=model_name,
                            error_message=error_body
                        )


                        should_retry = await handle_error_with_retry(
                            credential_manager, status_code, current_file,
                            retry_config["retry_enabled"], attempt, max_retries, retry_interval,
                            mode="primary"
                        )

                        if should_retry and attempt < max_retries:
                            need_retry = True
                            break
                        else:

                            log.error(f"[provider stream] Maximum number of retries reached or should not be retried, returning original error")
                            yield chunk
                            return
                    else:

                        log.error(f"[provider stream] streaming request failed with a non-retryable status (status={status_code}), credential={current_file}, response={error_body[:500] if error_body else 'None'}")
                        await record_api_call_error(
                            credential_manager, current_file, status_code,
                            None, mode="primary", model_name=model_name,
                            error_message=error_body
                        )
                        yield chunk
                        return
                else:


                    if not received_content:
                        received_content = True
                        log.debug(f"[provider stream] started receiving streaming responses, model: {model_name}")

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
                )
                log.debug(f"[provider stream] Streaming response completed, model: {model_name}")
                return
            elif not need_retry:

                log.warning(f"[provider stream] received an empty reply with no content, voucher: {current_file}")
                await record_api_call_error(
                    credential_manager, current_file, 200,
                    None, mode="primary", model_name=model_name,
                    error_message="Empty response from API"
                )

                if attempt < max_retries:
                    need_retry = True
                else:
                    log.error(f"[provider stream] Empty response reaches maximum number of retries")
                    yield Response(
                        content=json.dumps({"error": "Empty response returned by service"}),
                        status_code=500,
                        media_type="application/json"
                    )
                    return


            if need_retry:
                log.info(f"[provider stream] retrying request (attempt {attempt + 2}/{max_retries + 1}).")

                if switch_credential_enabled:
                    switched, next_cred_task = await _switch_credential_for_retry(
                        next_cred_task=next_cred_task,
                        retry_interval=retry_interval,
                        refresh_credential_fast=refresh_credential_fast,
                        apply_cred_result=apply_cred_result,
                        log_prefix="[provider stream]",
                    )
                    if not switched:
                        log.error("[provider stream] No credentials or tokens available when retrying")
                        yield Response(
                            content=json.dumps({"error": "No credentials are available."}),
                            status_code=500,
                            media_type="application/json"
                        )
                        return
                continue

        except Exception as e:
            log.error(f"[provider stream] Streaming Request Exception: {e}, Credentials: {current_file}")
            await record_api_call_error(
                credential_manager, current_file, 500,
                None, mode="primary", model_name=model_name,
                error_message=str(e)
            )
            if attempt < max_retries:
                log.info(f"[provider stream] retry after abnormality (attempt {attempt + 2}/{max_retries + 1})...")
                await asyncio.sleep(retry_interval)
                continue
            else:

                log.error(f"[provider stream] all retries failed. Last exception: {e}")
                if last_error_response:
                    yield last_error_response
                else:

                    yield Response(
                        content=json.dumps({"error": f"Streaming request exception: {str(e)}"}),
                        status_code=500,
                        media_type="application/json"
                    )
                return


    log.error("[provider stream] all retries failed.")
    if last_error_response:
        yield last_error_response
    else:
        yield Response(
            content=json.dumps({"error": "Request failed after all retries were exhausted."}),
            status_code=429,
            media_type="application/json"
        )


async def non_stream_request(
    body: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
) -> Response:
    """Internal implementation detail."""

    if await get_antigravity_stream_to_nonstream():
        log.debug("[provider] Streaming collection mode for non-streaming requests")


        stream = stream_request(body=body, native=False, headers=headers)




        return await collect_streaming_response(stream)


    log.debug("[provider] Direct non-streaming mode enabled")

    model_name = body.get("model", "")


    cred_result = await credential_manager.get_valid_credential(
        mode="primary", model_name=model_name
    )

    if not cred_result:

        log.error("[provider] No credentials currently available")
        await record_unassigned_api_call_error(
            status_code=500, mode="primary", model_name=model_name
        )
        return Response(
            content=json.dumps({"error": "No credentials are available."}),
            status_code=500,
            media_type="application/json"
        )

    current_file, credential_data = cred_result
    access_token = credential_data.get("access_token") or credential_data.get("token")
    project_id = credential_data.get("project_id", "")

    if not access_token:
        log.error(f"[provider] No access token in credential: {current_file}")
        await record_api_call_error(
            credential_manager, current_file, 500,
            None, mode="primary", model_name=model_name,
            error_message="No access token in credential"
        )
        return Response(
            content=json.dumps({"error": "No access token in credential"}),
            status_code=500,
            media_type="application/json"
        )


    primary_url = await get_antigravity_api_url()
    target_url = f"{primary_url}/v1internal:generateContent"

    auth_headers = await build_primary_headers(access_token)


    if headers:
        auth_headers.update(headers)


    inner_request = body.get("request", body)
    final_payload, _ = await wrap_cli_request(inner_request, model_name, project_id)


    retry_config = await get_retry_config()
    max_retries = retry_config["max_retries"]
    retry_interval = retry_config["retry_interval"]
    switch_credential_enabled = await get_antigravity_switch_credential_enabled()

    DISABLE_ERROR_CODES = await get_auto_disable_error_codes()
    last_error_response = None
    next_cred_task = None


    async def refresh_credential_fast():
        nonlocal current_file, access_token, auth_headers, project_id, final_payload
        cred_result = await credential_manager.get_valid_credential(
            mode="primary", model_name=model_name
        )
        if not cred_result:
            return None
        current_file, credential_data = cred_result
        access_token = credential_data.get("access_token") or credential_data.get("token")
        project_id = credential_data.get("project_id", "")
        if not access_token:
            return None

        auth_headers["Authorization"] = f"Bearer {access_token}"
        final_payload["project"] = project_id
        return True

    def apply_cred_result(cred_result: Tuple[str, Dict[str, Any]]) -> bool:
        nonlocal current_file, access_token, project_id, auth_headers, final_payload
        current_file, credential_data = cred_result
        access_token = credential_data.get("access_token") or credential_data.get("token")
        project_id = credential_data.get("project_id", "")
        if not access_token or not project_id:
            return False
        auth_headers["Authorization"] = f"Bearer {access_token}"
        final_payload["project"] = project_id
        return True

    for attempt in range(max_retries + 1):
        need_retry = False

        try:
            response = await post_async(
                url=target_url,
                json=final_payload,
                headers=auth_headers,
                timeout=300.0
            )

            status_code = response.status_code


            if status_code == 200:

                if not response.content or len(response.content) == 0:
                    log.warning(f"[provider] Received 200 response but the content is empty, voucher: {current_file}")


                    await record_api_call_error(
                        credential_manager, current_file, 200,
                        None, mode="primary", model_name=model_name,
                        error_message="Empty response from API"
                    )

                    if attempt < max_retries:
                        need_retry = True
                    else:
                        log.error(f"[provider] Empty response reaches maximum number of retries")
                        return Response(
                            content=json.dumps({"error": "Empty response returned by service"}),
                            status_code=500,
                            media_type="application/json"
                        )
                else:

                    token_usage = extract_token_usage_from_response(response.content)
                    await record_api_call_success(
                        credential_manager,
                        current_file,
                        mode="primary",
                        model_name=model_name,
                        token_usage=token_usage,
                        status_code=status_code,
                    )
                    return Response(
                        content=response.content,
                        status_code=200,
                        headers=dict(response.headers)
                    )


            if status_code != 200:
                last_error_response = Response(
                    content=response.content,
                    status_code=status_code,
                    headers=dict(response.headers)
                )



                error_text = ""
                try:
                    error_text = response.text
                except Exception:
                    pass

                if _is_retryable_status(status_code, DISABLE_ERROR_CODES):
                    log.warning(f"[provider] non-streaming request failed (status={status_code}), credential={current_file}, response={error_text[:500] if error_text else 'None'}")


                    cooldown_until = None
                    if (status_code == 429 or status_code == 503) and error_text:
                        try:
                            cooldown_until = await parse_and_log_cooldown(error_text, mode="primary")
                        except Exception:
                            pass


                    if switch_credential_enabled and next_cred_task is None and attempt < max_retries:
                        next_cred_task = asyncio.create_task(
                            credential_manager.get_valid_credential(
                                mode="primary", model_name=model_name
                            )
                        )


                    await record_api_call_error(
                        credential_manager, current_file, status_code,
                        cooldown_until, mode="primary", model_name=model_name,
                        error_message=error_text
                    )


                    should_retry = await handle_error_with_retry(
                        credential_manager, status_code, current_file,
                        retry_config["retry_enabled"], attempt, max_retries, retry_interval,
                        mode="primary"
                    )

                    if should_retry and attempt < max_retries:
                        need_retry = True
                    else:

                        log.error(f"[provider] Maximum number of retries reached or should not be retried, returning original error")
                        return last_error_response
                else:

                    log.error(f"[provider] non-streaming request failed with a non-retryable status (status={status_code}), credential={current_file}, response={error_text[:500] if error_text else 'None'}")
                    await record_api_call_error(
                        credential_manager, current_file, status_code,
                        None, mode="primary", model_name=model_name,
                        error_message=error_text
                    )
                    return last_error_response


            if need_retry:
                log.info(f"[provider] retrying request (attempt {attempt + 2}/{max_retries + 1}).")

                if switch_credential_enabled:
                    switched, next_cred_task = await _switch_credential_for_retry(
                        next_cred_task=next_cred_task,
                        retry_interval=retry_interval,
                        refresh_credential_fast=refresh_credential_fast,
                        apply_cred_result=apply_cred_result,
                        log_prefix="[provider]",
                    )
                    if not switched:
                        log.error("[provider] No credentials or tokens available when retrying")
                        return Response(
                            content=json.dumps({"error": "No credentials are available."}),
                            status_code=500,
                            media_type="application/json"
                        )
                continue

        except Exception as e:
            log.error(f"[provider] non-streaming request raised an exception: {e}; credential={current_file}")
            await record_api_call_error(
                credential_manager, current_file, 500,
                None, mode="primary", model_name=model_name,
                error_message=str(e)
            )
            if attempt < max_retries:
                log.info(f"[provider] Retry after exception (attempt {attempt + 2}/{max_retries + 1})...")
                await asyncio.sleep(retry_interval)
                continue
            else:

                log.error(f"[provider] all retries failed. Last exception: {e}")
                if last_error_response:
                    return last_error_response
                else:
                    return Response(
                        content=json.dumps({"error": f"Non-streaming request exception: {str(e)}"}),
                        status_code=500,
                        media_type="application/json"
                    )


    log.error("[provider] all retries failed.")
    if last_error_response:
        return last_error_response
    else:
        return Response(
            content=json.dumps({"error": "Request failed after all retries were exhausted."}),
            status_code=500,
            media_type="application/json"
        )




async def fetch_available_models() -> List[Dict[str, Any]]:
    """Internal implementation detail."""

    cred_result = await credential_manager.get_valid_credential(mode="primary")
    if not cred_result:
        log.error("[provider] No valid credentials available for fetching models")
        return []

    current_file, credential_data = cred_result
    access_token = credential_data.get("access_token") or credential_data.get("token")

    if not access_token:
        log.error(f"[provider] No access token in credential: {current_file}")
        return []


    headers = await build_primary_headers(access_token)

    try:

        primary_url = await get_antigravity_api_url()

        response = await post_async(
            url=f"{primary_url}/v1internal:fetchAvailableModels",
            json={},
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            log.debug(f"[provider] Raw models response: {json.dumps(data, ensure_ascii=False)[:500]}")


            model_list = []
            current_timestamp = int(datetime.now(timezone.utc).timestamp())

            if 'models' in data and isinstance(data['models'], dict):

                for model_id in data['models'].keys():
                    model = Model(
                        id=model_id,
                        object='model',
                        created=current_timestamp,
                        owned_by='google'
                    )
                    model_list.append(model_to_dict(model))

            if "claude-sonnet-4-6" in data.get('models', {}):
                model = Model(
                    id='claude-sonnet-4-6-thinking',
                    object='model',
                    created=current_timestamp,
                    owned_by='google'
                )
                model_list.append(model_to_dict(model))

            if "claude-opus-4-6-thinking" in data.get('models', {}):
                claude_opus_model = Model(
                    id='claude-opus-4-6',
                    object='model',
                    created=current_timestamp,
                    owned_by='google'
                )
                model_list.append(model_to_dict(claude_opus_model))

            log.info(f"[provider] Fetched {len(model_list)} available models")
            return model_list
        else:
            log.error(f"[provider] Failed to fetch models ({response.status_code}): {response.text[:500]}")
            return []

    except Exception as e:
        import traceback
        log.error(f"[provider] Failed to fetch models: {e}")
        log.error(f"[provider] Traceback: {traceback.format_exc()}")
        return []


async def fetch_quota_info(access_token: str) -> Dict[str, Any]:
    """Internal implementation detail."""

    headers = await build_primary_headers(access_token)

    try:
        primary_url = await get_antigravity_api_url()

        response = await post_async(
            url=f"{primary_url}/v1internal:fetchAvailableModels",
            json={},
            headers=headers,
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()
            log.debug(f"[provider quota] Raw response: {json.dumps(data, ensure_ascii=False)[:500]}")

            quota_info = {}

            if 'models' in data and isinstance(data['models'], dict):
                for model_id, model_data in data['models'].items():
                    if isinstance(model_data, dict) and 'quotaInfo' in model_data:
                        quota = model_data['quotaInfo']
                        remaining = quota.get('remainingFraction', 0)
                        reset_time_raw = quota.get('resetTime', '')


                        reset_time_beijing = 'N/A'
                        if reset_time_raw:
                            try:
                                utc_date = datetime.fromisoformat(reset_time_raw.replace('Z', '+00:00'))

                                from datetime import timedelta
                                beijing_date = utc_date + timedelta(hours=8)
                                reset_time_beijing = beijing_date.strftime('%m-%d %H:%M')
                            except Exception as e:
                                log.warning(f"[provider quota] Failed to parse reset time: {e}")

                        quota_info[model_id] = {
                            "remaining": remaining,
                            "resetTime": reset_time_beijing,
                            "resetTimeRaw": reset_time_raw
                        }

            return {
                "success": True,
                "models": quota_info
            }
        else:
            log.error(f"[provider quota] Failed to fetch quota ({response.status_code}): {response.text[:500]}")
            return {
                "success": False,
                "error": f"API returned an error: {response.status_code}"
            }

    except Exception as e:
        import traceback
        log.error(f"[provider quota] Failed to fetch quota: {e}")
        log.error(f"[provider quota] Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        }
