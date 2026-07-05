"""
Omni API Client - Handles communication with Google's Omni API
å¤„ç†ä¸ Google Omni API ç„é€ä¿¡
"""

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
    get_ogw_api_url,
    get_ogw_stream_to_nonstream,
    get_auto_disable_error_codes,
)
from log import log

from omni_gateway.credential_manager import credential_manager
from omni_gateway.httpx_client import stream_post_async, post_async
from omni_gateway.models import Model, model_to_dict
from omni_gateway.utils import OGW_USER_AGENT

# å¯¼å…¥å…±åŒç„åŸºç¡€åŸèƒ½
from omni_gateway.api.utils import (
    handle_error_with_retry,
    get_retry_config,
    record_api_call_success,
    record_api_call_error,
    parse_and_log_cooldown,
    collect_streaming_response,
)

# ==================== å…¨å±€å‡­è¯ç®¡ç†å™¨ ====================

# ä½¿ç”¨å…¨å±€å•ä¾‹ credential_managerï¼Œè‡ªå¨åˆå§‹åŒ–


# ==================== ä¼è¯ç¶æ€ç®¡ç† ====================

SESSION_TTL_SECONDS = 6 * 60 * 60
MAX_SESSION_STATES = 1024
_REDIS_KEY_PREFIX = "omni:session:"


@dataclass
class OmniSessionState:
    conversation_id: str
    trajectory_id: str
    session_id: str
    step_index: int
    created_at: float
    last_used_at: float


# å†…å­˜å›é€€å­˜å‚¨
_session_states: Dict[str, OmniSessionState] = {}

# Redis å®¢æˆ·ç«¯ï¼ˆæ‡’åˆå§‹åŒ–ï¼ŒOGW_REDIS_URL å­˜åœ¨æ—¶ä½¿ç”¨ï¼‰
_redis_client = None
_redis_checked = False


async def _get_redis():
    """æ‡’åˆå§‹åŒ– Redis å®¢æˆ·ç«¯ï¼ŒOGW_REDIS_URL æœªè®¾ç½®æ—¶è¿”å› Noneă€‚"""
    global _redis_client, _redis_checked
    if _redis_checked:
        return _redis_client
    _redis_checked = True
    redis_url = os.getenv("OGW_REDIS_URL")
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


def _make_new_state(first_user_text: str, now: float) -> OmniSessionState:
    if first_user_text:
        digest = hashlib.sha256(first_user_text.encode("utf-8")).digest()
        session_id_val = int.from_bytes(digest[:8], "big") & 0x7FFFFFFFFFFFFFFF
        session_id = f"-{session_id_val}"
    else:
        session_id = f"-{uuid.uuid4().int % 9_000_000_000_000_000_000}"
    return OmniSessionState(
        conversation_id=str(uuid.uuid4()),
        trajectory_id=str(uuid.uuid4()),
        session_id=session_id,
        step_index=1,
        created_at=now,
        last_used_at=now,
    )


async def _get_session_state(request_payload: Dict[str, Any], model: str = "") -> OmniSessionState:
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
                state = OmniSessionState(**data)
                state.step_index += 1
                state.last_used_at = now
            else:
                state = _make_new_state(first_user_text, now)
            await redis.set(redis_key, json.dumps(state.__dict__), ex=SESSION_TTL_SECONDS)
            return state
        except Exception as e:
            log.warning(f"[SESSION] Redis error, falling back to memory: {e}")

    # å†…å­˜å›é€€
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
    """
    å°† Gemini æ ¼å¼è¯·æ±‚åŒ…è£…æˆ Omni CLI æ ¼å¼ă€‚
    è¿”å› (payload, request_id)ă€‚
    """
    inner = dict(gemini_request)

    # ç§»é™¤ safetySettingsï¼ˆCLI ä¸å‘é€ï¼‰
    inner.pop("safetySettings", None)

    # è·å–/æ›´æ–°ä¼è¯ç¶æ€
    state = await _get_session_state(inner, model)

    # æ³¨å…¥ sessionId
    if not inner.get("sessionId"):
        inner["sessionId"] = state.session_id

    # æ³¨å…¥ labels
    inner["labels"] = _build_labels(model, state.trajectory_id, state.step_index)

    # toolConfig é»˜è®¤ VALIDATED
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
        "userAgent": "omni",
        "requestType": "agent",
        "enabledCreditTypes": ["GOOGLE_ONE_AI"],
    }
    return payload, request_id


# ==================== è¾…å©å‡½æ•° ====================

def build_omni_headers(access_token: str) -> Dict[str, str]:
    """æ„å»º Omni CLI API è¯·æ±‚å¤´ă€‚"""
    return {
        "User-Agent": OGW_USER_AGENT,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
    }


def _is_retryable_status(status_code: int, disable_error_codes: List[int]) -> bool:
    """ç»Ÿä¸€åˆ¤æ–­æ˜¯å¦å±äºå¯é‡è¯•ç¶æ€ç ă€‚"""
    return status_code in (429, 503) or status_code in disable_error_codes


async def _switch_credential_for_retry(
    *,
    next_cred_task: Optional[asyncio.Task],
    retry_interval: float,
    refresh_credential_fast: Callable[[], Any],
    apply_cred_result: Callable[[Tuple[str, Dict[str, Any]]], bool],
    log_prefix: str,
) -> Tuple[bool, Optional[asyncio.Task]]:
    """ä¼˜å…ˆä½¿ç”¨é¢„çƒ­å‡­è¯ï¼Œå¤±è´¥åé€€å›åŒæ­¥åˆ·æ–°ă€‚"""
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


# ==================== æ–°ç„æµå¼å’Œéæµå¼è¯·æ±‚å‡½æ•° ====================

async def stream_request(
    body: Dict[str, Any],
    native: bool = False,
    headers: Optional[Dict[str, str]] = None,
):
    """
    æµå¼è¯·æ±‚å‡½æ•°

    Args:
        body: è¯·æ±‚ä½“
        native: æ˜¯å¦è¿”å›åŸç”Ÿbytesæµï¼ŒFalseåˆ™è¿”å›stræµ
        headers: é¢å¤–ç„è¯·æ±‚å¤´

    Yields:
        Responseå¯¹è±¡ï¼ˆé”™è¯¯æ—¶ï¼‰æˆ– bytesæµ/stræµï¼ˆæˆåŸæ—¶ï¼‰
    """
    model_name = body.get("model", "")

    # 1. è·å–æœ‰æ•ˆå‡­è¯
    cred_result = await credential_manager.get_valid_credential(
        mode="omni", model_name=model_name
    )

    if not cred_result:
        # å¦‚æœè¿”å›å€¼æ˜¯Noneï¼Œç›´æ¥è¿”å›é”™è¯¯500
        log.error("[OMNI stream] No credentials currently available")
        yield Response(
            content=json.dumps({"error": "No credentials available"}),
            status_code=500,
            media_type="application/json"
        )
        return

    current_file, credential_data = cred_result
    access_token = credential_data.get("access_token") or credential_data.get("token")
    project_id = credential_data.get("project_id", "")

    if not access_token:
        log.error(f"[OMNI STREAM] No access token in credential: {current_file}")
        yield Response(
            content=json.dumps({"error": "No access token in credential"}),
            status_code=500,
            media_type="application/json"
        )
        return

    # 2. æ„å»ºURLå’Œè¯·æ±‚å¤´
    omni_url = await get_ogw_api_url()
    target_url = f"{omni_url}/v1internal:streamGenerateContent?alt=sse"

    auth_headers = build_omni_headers(access_token)

    # åˆå¹¶è‡ªå®ä¹‰headers
    if headers:
        auth_headers.update(headers)

    # æ„å»º CLI æ ¼å¼è¯·æ±‚ä½“
    inner_request = body.get("request", body)
    final_payload, _ = await wrap_cli_request(inner_request, model_name, project_id)

    # 3. è°ƒç”¨stream_post_asyncè¿›è¡Œè¯·æ±‚
    retry_config = await get_retry_config()
    max_retries = retry_config["max_retries"]
    retry_interval = retry_config["retry_interval"]

    DISABLE_ERROR_CODES = await get_auto_disable_error_codes()  # ç¦ç”¨å‡­è¯ç„é”™è¯¯ç 
    last_error_response = None  # è®°å½•æœ€åä¸€æ¬¡ç„é”™è¯¯å“åº”
    next_cred_task = None  # é¢„çƒ­ç„ä¸‹ä¸€ä¸ªå‡­è¯ä»»å¡

    # å†…éƒ¨å‡½æ•°ï¼å¿«é€Ÿæ›´æ–°å‡­è¯(åªæ›´æ–°tokenå’Œproject_id,é¿å…é‡å»ºæ•´ä¸ªè¯·æ±‚)
    async def refresh_credential_fast():
        nonlocal current_file, access_token, auth_headers, project_id, final_payload
        cred_result = await credential_manager.get_valid_credential(
            mode="omni", model_name=model_name
        )
        if not cred_result:
            return None
        current_file, credential_data = cred_result
        access_token = credential_data.get("access_token") or credential_data.get("token")
        project_id = credential_data.get("project_id", "")
        if not access_token:
            return None
        # åªæ›´æ–°tokenå’Œproject_id,ä¸é‡å»ºæ•´ä¸ªheaderså’Œpayload
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
        success_recorded = False  # æ ‡è®°æ˜¯å¦å·²è®°å½•æˆåŸ
        need_retry = False  # æ ‡è®°æ˜¯å¦éœ€è¦é‡è¯•

        try:
            async for chunk in stream_post_async(
                url=target_url,
                body=final_payload,
                native=native,
                headers=auth_headers
            ):
                # åˆ¤æ–­æ˜¯å¦æ˜¯Responseå¯¹è±¡
                if isinstance(chunk, Response):
                    status_code = chunk.status_code
                    last_error_response = chunk  # è®°å½•æœ€åä¸€æ¬¡é”™è¯¯

                    # ç¼“å­˜é”™è¯¯è§£æç»“æœ,é¿å…é‡å¤decode
                    error_body = None
                    try:
                        error_body = chunk.body.decode('utf-8') if isinstance(chunk.body, bytes) else str(chunk.body)
                    except Exception:
                        error_body = ""

                    # å¦‚æœé”™è¯¯ç æ˜¯429ă€503æˆ–è€…åœ¨ç¦ç”¨ç å½“ä¸­ï¼Œåå¥½è®°å½•åè¿›è¡Œé‡è¯•
                    if _is_retryable_status(status_code, DISABLE_ERROR_CODES):
                        log.warning(f"[OMNI stream] streaming request failed (status = {status_code}), credentials: {current_file}, response: {error_body[:500] if error_body else 'None'}")

                        # è§£æå†·å´æ—¶é—´
                        cooldown_until = None
                        if (status_code == 429 or status_code == 503) and error_body:
                            try:
                                cooldown_until = await parse_and_log_cooldown(error_body, mode="omni")
                            except Exception:
                                pass

                        # é¢„çƒ­ä¸‹ä¸€ä¸ªå‡­è¯
                        if next_cred_task is None and attempt < max_retries:
                            next_cred_task = asyncio.create_task(
                                credential_manager.get_valid_credential(
                                    mode="omni", model_name=model_name
                                )
                            )

                        # è®°å½•é”™è¯¯å¹¶åˆ‡æ¢å‡­è¯
                        await record_api_call_error(
                            credential_manager, current_file, status_code,
                            cooldown_until, mode="omni", model_name=model_name,
                            error_message=error_body
                        )

                        # æ£€æŸ¥æ˜¯å¦åº”è¯¥é‡è¯•
                        should_retry = await handle_error_with_retry(
                            credential_manager, status_code, current_file,
                            retry_config["retry_enabled"], attempt, max_retries, retry_interval,
                            mode="omni"
                        )

                        if should_retry and attempt < max_retries:
                            need_retry = True
                            break  # è·³å‡ºå†…å±‚å¾ªç¯ï¼Œå‡†å¤‡é‡è¯•
                        else:
                            # ä¸é‡è¯•ï¼Œç›´æ¥è¿”å›åŸå§‹é”™è¯¯
                            log.error(f"[OMNI stream] Maximum number of retries reached or should not be retried, returning original error")
                            yield chunk
                            return
                    else:
                        # é”™è¯¯ç ä¸åœ¨ç¦ç”¨ç å½“ä¸­ï¼Œç›´æ¥è¿”å›ï¼Œæ— éœ€é‡è¯•
                        log.error(f"[OMNI stream] streaming request failed, non-retry error code (status = {status_code}), credentials: {current_file}, response: {error_body[:500] if error_body else 'None'}")
                        await record_api_call_error(
                            credential_manager, current_file, status_code,
                            None, mode="omni", model_name=model_name,
                            error_message=error_body
                        )
                        yield chunk
                        return
                else:
                    # ä¸æ˜¯Responseï¼Œè¯´æ˜æ˜¯çœŸæµï¼Œç›´æ¥yieldè¿”å›
                    # åªåœ¨ç¬¬ä¸€ä¸ªchunkæ—¶è®°å½•æˆåŸ
                    if not success_recorded:
                        await record_api_call_success(
                            credential_manager, current_file, mode="omni", model_name=model_name
                        )
                        success_recorded = True
                        log.debug(f"[OMNI stream] started receiving streaming responses, model: {model_name}")

                    # è®°å½•åŸå§‹chunkå†…å®¹ï¼ˆç”¨äºè°ƒè¯•ï¼‰
                    if isinstance(chunk, bytes):
                        log.debug(f"[OMNI STREAM RAW] chunk(bytes): {chunk}")
                    else:
                        log.debug(f"[OMNI STREAM RAW] chunk(str): {chunk}")

                    yield chunk

            # æµå¼è¯·æ±‚å®Œæˆï¼Œæ£€æŸ¥ç»“æœ
            if success_recorded:
                log.debug(f"[OMNI stream] Streaming response completed, model: {model_name}")
                return
            elif not need_retry:
                # æ²¡æœ‰æ”¶åˆ°ä»»ä½•æ•°æ®ï¼ˆç©ºå›å¤ï¼‰ï¼Œéœ€è¦é‡è¯•
                log.warning(f"[OMNI stream] received an empty reply with no content, voucher: {current_file}")
                await record_api_call_error(
                    credential_manager, current_file, 200,
                    None, mode="omni", model_name=model_name,
                    error_message="Empty response from API"
                )
                
                if attempt < max_retries:
                    need_retry = True
                else:
                    log.error(f"[OMNI stream] Empty response reaches maximum number of retries")
                    yield Response(
                        content=json.dumps({"error": "Empty response returned by service"}),
                        status_code=500,
                        media_type="application/json"
                    )
                    return
            
            # ç»Ÿä¸€å¤„ç†é‡è¯•
            if need_retry:
                log.info(f"[OMNI stream] retry request (attempt {attempt + 2}/{max_retries + 1})...")

                switched, next_cred_task = await _switch_credential_for_retry(
                    next_cred_task=next_cred_task,
                    retry_interval=retry_interval,
                    refresh_credential_fast=refresh_credential_fast,
                    apply_cred_result=apply_cred_result,
                    log_prefix="[OMNI STREAM]",
                )
                if not switched:
                    log.error("[OMNI stream] No credentials or tokens available when retrying")
                    yield Response(
                        content=json.dumps({"error": "No credentials available"}),
                        status_code=500,
                        media_type="application/json"
                    )
                    return
                continue  # é‡è¯•

        except Exception as e:
            log.error(f"[OMNI stream] Streaming Request Exception: {e}, Credentials: {current_file}")
            if attempt < max_retries:
                log.info(f"[OMNI stream] retry after abnormality (attempt {attempt + 2}/{max_retries + 1})...")
                await asyncio.sleep(retry_interval)
                continue
            else:
                # æ‰€æœ‰é‡è¯•éƒ½å¤±è´¥ï¼Œè¿”å›æœ€åä¸€æ¬¡ç„é”™è¯¯ï¼ˆå¦‚æœæœ‰ï¼‰
                log.error(f"[OMNI stream] All retries failed with last exception: {e}")
                if last_error_response:
                    yield last_error_response
                else:
                    # å¦‚æœæ²¡æœ‰è®°å½•åˆ°é”™è¯¯å“åº”ï¼Œè¿”å›500é”™è¯¯
                    yield Response(
                        content=json.dumps({"error": f"Streaming request exception: {str(e)}"}),
                        status_code=500,
                        media_type="application/json"
                    )
                return

    # æ‰€æœ‰é‡è¯•å‡å·²è€—å°½ï¼ˆforå¾ªç¯æ­£å¸¸ç»“æŸï¼‰ï¼Œè¿”å›æœ€åè®°å½•ç„é”™è¯¯
    log.error("[OMNI stream] All retries failed")
    if last_error_response:
        yield last_error_response
    else:
        yield Response(
            content=json.dumps({"error": "Request failed, all retries exhausted"}),
            status_code=429,
            media_type="application/json"
        )


async def non_stream_request(
    body: Dict[str, Any],
    headers: Optional[Dict[str, str]] = None,
) -> Response:
    """
    éæµå¼è¯·æ±‚å‡½æ•°

    Args:
        body: è¯·æ±‚ä½“
        headers: é¢å¤–ç„è¯·æ±‚å¤´

    Returns:
        Responseå¯¹è±¡
    """
    # æ£€æŸ¥æ˜¯å¦å¯ç”¨æµå¼æ”¶é›†æ¨¡å¼
    if await get_ogw_stream_to_nonstream():
        log.debug("[OMNI] Streaming collection mode for non-streaming requests")

        # è°ƒç”¨stream_requestè·å–æµ
        stream = stream_request(body=body, native=False, headers=headers)

        # æ”¶é›†æµå¼å“åº”
        # stream_requestæ˜¯ä¸€ä¸ªå¼‚æ­¥ç”Ÿæˆå™¨ï¼Œå¯èƒ½yield Responseï¼ˆé”™è¯¯ï¼‰æˆ–æµæ•°æ®
        # collect_streaming_responseä¼è‡ªå¨å¤„ç†è¿™ä¸¤ç§æƒ…å†µ
        return await collect_streaming_response(stream)

    # å¦åˆ™ä½¿ç”¨ä¼ ç»Ÿéæµå¼æ¨¡å¼
    log.debug("[OMNI] Direct non-streaming mode enabled")

    model_name = body.get("model", "")

    # 1. è·å–æœ‰æ•ˆå‡­è¯
    cred_result = await credential_manager.get_valid_credential(
        mode="omni", model_name=model_name
    )

    if not cred_result:
        # å¦‚æœè¿”å›å€¼æ˜¯Noneï¼Œç›´æ¥è¿”å›é”™è¯¯500
        log.error("[OMNI] No credentials currently available")
        return Response(
            content=json.dumps({"error": "No credentials available"}),
            status_code=500,
            media_type="application/json"
        )

    current_file, credential_data = cred_result
    access_token = credential_data.get("access_token") or credential_data.get("token")
    project_id = credential_data.get("project_id", "")

    if not access_token:
        log.error(f"[OMNI] No access token in credential: {current_file}")
        return Response(
            content=json.dumps({"error": "No access token in credential"}),
            status_code=500,
            media_type="application/json"
        )

    # 2. æ„å»ºURLå’Œè¯·æ±‚å¤´
    omni_url = await get_ogw_api_url()
    target_url = f"{omni_url}/v1internal:generateContent"

    auth_headers = build_omni_headers(access_token)

    # åˆå¹¶è‡ªå®ä¹‰headers
    if headers:
        auth_headers.update(headers)

    # æ„å»º CLI æ ¼å¼è¯·æ±‚ä½“
    inner_request = body.get("request", body)
    final_payload, _ = await wrap_cli_request(inner_request, model_name, project_id)

    # 3. è°ƒç”¨post_asyncè¿›è¡Œè¯·æ±‚
    retry_config = await get_retry_config()
    max_retries = retry_config["max_retries"]
    retry_interval = retry_config["retry_interval"]

    DISABLE_ERROR_CODES = await get_auto_disable_error_codes()  # ç¦ç”¨å‡­è¯ç„é”™è¯¯ç 
    last_error_response = None  # è®°å½•æœ€åä¸€æ¬¡ç„é”™è¯¯å“åº”
    next_cred_task = None  # é¢„çƒ­ç„ä¸‹ä¸€ä¸ªå‡­è¯ä»»å¡

    # å†…éƒ¨å‡½æ•°ï¼å¿«é€Ÿæ›´æ–°å‡­è¯(åªæ›´æ–°tokenå’Œproject_id,é¿å…é‡å»ºæ•´ä¸ªè¯·æ±‚)
    async def refresh_credential_fast():
        nonlocal current_file, access_token, auth_headers, project_id, final_payload
        cred_result = await credential_manager.get_valid_credential(
            mode="omni", model_name=model_name
        )
        if not cred_result:
            return None
        current_file, credential_data = cred_result
        access_token = credential_data.get("access_token") or credential_data.get("token")
        project_id = credential_data.get("project_id", "")
        if not access_token:
            return None
        # åªæ›´æ–°tokenå’Œproject_id,ä¸é‡å»ºæ•´ä¸ªheaderså’Œpayload
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
        need_retry = False  # æ ‡è®°æ˜¯å¦éœ€è¦é‡è¯•
        
        try:
            response = await post_async(
                url=target_url,
                json=final_payload,
                headers=auth_headers,
                timeout=300.0
            )

            status_code = response.status_code

            # æˆåŸ
            if status_code == 200:
                # æ£€æŸ¥æ˜¯å¦ä¸ºç©ºå›å¤
                if not response.content or len(response.content) == 0:
                    log.warning(f"[OMNI] Received 200 response but the content is empty, voucher: {current_file}")
                    
                    # è®°å½•é”™è¯¯
                    await record_api_call_error(
                        credential_manager, current_file, 200,
                        None, mode="omni", model_name=model_name,
                        error_message="Empty response from API"
                    )
                    
                    if attempt < max_retries:
                        need_retry = True
                    else:
                        log.error(f"[OMNI] Empty response reaches maximum number of retries")
                        return Response(
                            content=json.dumps({"error": "Empty response returned by service"}),
                            status_code=500,
                            media_type="application/json"
                        )
                else:
                    # æ­£å¸¸å“åº”
                    await record_api_call_success(
                        credential_manager, current_file, mode="omni", model_name=model_name
                    )
                    return Response(
                        content=response.content,
                        status_code=200,
                        headers=dict(response.headers)
                    )

            # å¤±è´¥ - è®°å½•æœ€åä¸€æ¬¡é”™è¯¯
            if status_code != 200:
                last_error_response = Response(
                    content=response.content,
                    status_code=status_code,
                    headers=dict(response.headers)
                )

                # åˆ¤æ–­æ˜¯å¦éœ€è¦é‡è¯•
                # ç¼“å­˜é”™è¯¯æ–‡æœ¬,é¿å…é‡å¤è§£æ
                error_text = ""
                try:
                    error_text = response.text
                except Exception:
                    pass

                if _is_retryable_status(status_code, DISABLE_ERROR_CODES):
                    log.warning(f"[OMNI] Non streaming request failed (status = {status_code}), credentials: {current_file}, response: {error_text[:500] if error_text else 'None'}")

                    # è§£æå†·å´æ—¶é—´
                    cooldown_until = None
                    if (status_code == 429 or status_code == 503) and error_text:
                        try:
                            cooldown_until = await parse_and_log_cooldown(error_text, mode="omni")
                        except Exception:
                            pass

                    # å¹¶è¡Œé¢„çƒ­ä¸‹ä¸€ä¸ªå‡­è¯,ä¸é˜»å¡å½“å‰å¤„ç†
                    if next_cred_task is None and attempt < max_retries:
                        next_cred_task = asyncio.create_task(
                            credential_manager.get_valid_credential(
                                mode="omni", model_name=model_name
                            )
                        )

                    # è®°å½•é”™è¯¯å¹¶åˆ‡æ¢å‡­è¯
                    await record_api_call_error(
                        credential_manager, current_file, status_code,
                        cooldown_until, mode="omni", model_name=model_name,
                        error_message=error_text
                    )

                    # æ£€æŸ¥æ˜¯å¦åº”è¯¥é‡è¯•
                    should_retry = await handle_error_with_retry(
                        credential_manager, status_code, current_file,
                        retry_config["retry_enabled"], attempt, max_retries, retry_interval,
                        mode="omni"
                    )

                    if should_retry and attempt < max_retries:
                        need_retry = True
                    else:
                        # ä¸é‡è¯•ï¼Œç›´æ¥è¿”å›åŸå§‹é”™è¯¯
                        log.error(f"[OMNI] Maximum number of retries reached or should not be retried, returning original error")
                        return last_error_response
                else:
                    # é”™è¯¯ç ä¸åœ¨ç¦ç”¨ç å½“ä¸­ï¼Œç›´æ¥è¿”å›ï¼Œæ— éœ€é‡è¯•
                    log.error(f"[OMNI] Non Streaming Request Failed, Non Retry Error Code (status = {status_code}), Credential: {current_file}, Response: {error_text[:500] if error_text else 'None'}")
                    await record_api_call_error(
                        credential_manager, current_file, status_code,
                        None, mode="omni", model_name=model_name,
                        error_message=error_text
                    )
                    return last_error_response
            
            # ç»Ÿä¸€å¤„ç†é‡è¯•
            if need_retry:
                log.info(f"[OMNI] Retry request (attempt {attempt + 2}/{max_retries + 1})...")

                switched, next_cred_task = await _switch_credential_for_retry(
                    next_cred_task=next_cred_task,
                    retry_interval=retry_interval,
                    refresh_credential_fast=refresh_credential_fast,
                    apply_cred_result=apply_cred_result,
                    log_prefix="[OMNI]",
                )
                if not switched:
                    log.error("[OMNI] No credentials or tokens available when retrying")
                    return Response(
                        content=json.dumps({"error": "No credentials available"}),
                        status_code=500,
                        media_type="application/json"
                    )
                continue  # é‡è¯•

        except Exception as e:
            log.error(f"[OMNI] Non Streaming Request Exception: {e}, Credentials: {current_file}")
            if attempt < max_retries:
                log.info(f"[OMNI] Retry after exception (attempt {attempt + 2}/{max_retries + 1})...")
                await asyncio.sleep(retry_interval)
                continue
            else:
                # æ‰€æœ‰é‡è¯•éƒ½å¤±è´¥ï¼Œè¿”å›æœ€åä¸€æ¬¡ç„é”™è¯¯ï¼ˆå¦‚æœæœ‰ï¼‰æˆ–500é”™è¯¯
                log.error(f"[OMNI] All retries failed with last exception: {e}")
                if last_error_response:
                    return last_error_response
                else:
                    return Response(
                        content=json.dumps({"error": f"Non-streaming request exception: {str(e)}"}),
                        status_code=500,
                        media_type="application/json"
                    )

    # æ‰€æœ‰é‡è¯•éƒ½å¤±è´¥ï¼Œè¿”å›æœ€åä¸€æ¬¡ç„åŸå§‹é”™è¯¯ï¼ˆå¦‚æœæœ‰ï¼‰æˆ–500é”™è¯¯
    log.error("[OMNI] All retries failed")
    if last_error_response:
        return last_error_response
    else:
        return Response(
            content=json.dumps({"error": "All retries failed"}),
            status_code=500,
            media_type="application/json"
        )


# ==================== æ¨¡å‹å’Œé…é¢æŸ¥è¯¢ ====================

async def fetch_available_models() -> List[Dict[str, Any]]:
    """
    è·å–å¯ç”¨æ¨¡å‹åˆ—è¡¨ï¼Œè¿”å›ç¬¦åˆ OpenAI API è§„èŒƒç„æ ¼å¼
    
    Returns:
        æ¨¡å‹åˆ—è¡¨ï¼Œæ ¼å¼ä¸ºå­—å…¸åˆ—è¡¨ï¼ˆç”¨äºå…¼å®¹ç°æœ‰ä»£ç ï¼‰
        
    Raises:
        è¿”å›ç©ºåˆ—è¡¨å¦‚æœè·å–å¤±è´¥
    """
    # è·å–å‡­è¯ç®¡ç†å™¨å’Œå¯ç”¨å‡­è¯
    cred_result = await credential_manager.get_valid_credential(mode="omni")
    if not cred_result:
        log.error("[OMNI] No valid credentials available for fetching models")
        return []

    current_file, credential_data = cred_result
    access_token = credential_data.get("access_token") or credential_data.get("token")

    if not access_token:
        log.error(f"[OMNI] No access token in credential: {current_file}")
        return []

    # æ„å»ºè¯·æ±‚å¤´
    headers = build_omni_headers(access_token)

    try:
        # ä½¿ç”¨ POST è¯·æ±‚è·å–æ¨¡å‹åˆ—è¡¨
        omni_url = await get_ogw_api_url()

        response = await post_async(
            url=f"{omni_url}/v1internal:fetchAvailableModels",
            json={},  # ç©ºç„è¯·æ±‚ä½“
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            log.debug(f"[OMNI] Raw models response: {json.dumps(data, ensure_ascii=False)[:500]}")

            # è½¬æ¢ä¸º OpenAI æ ¼å¼ç„æ¨¡å‹åˆ—è¡¨ï¼Œä½¿ç”¨ Model ç±»
            model_list = []
            current_timestamp = int(datetime.now(timezone.utc).timestamp())

            if 'models' in data and isinstance(data['models'], dict):
                # éå†æ¨¡å‹å­—å…¸
                for model_id in data['models'].keys():
                    model = Model(
                        id=model_id,
                        object='model',
                        created=current_timestamp,
                        owned_by='google'
                    )
                    model_list.append(model_to_dict(model))
            # æ·»å é¢å¤–ç„ claude-sonnet-4-6-thinking æ¨¡å‹
            if "claude-sonnet-4-6" in data.get('models', {}):
                model = Model(
                    id='claude-sonnet-4-6-thinking',
                    object='model',
                    created=current_timestamp,
                    owned_by='google'
                )
                model_list.append(model_to_dict(model))
            # æ·»å é¢å¤–ç„ claude-opus-4-6 æ¨¡å‹
            if "claude-opus-4-6-thinking" in data.get('models', {}):
                claude_opus_model = Model(
                    id='claude-opus-4-6',
                    object='model',
                    created=current_timestamp,
                    owned_by='google'
                )
                model_list.append(model_to_dict(claude_opus_model))

            log.info(f"[OMNI] Fetched {len(model_list)} available models")
            return model_list
        else:
            log.error(f"[OMNI] Failed to fetch models ({response.status_code}): {response.text[:500]}")
            return []

    except Exception as e:
        import traceback
        log.error(f"[OMNI] Failed to fetch models: {e}")
        log.error(f"[OMNI] Traceback: {traceback.format_exc()}")
        return []


async def fetch_quota_info(access_token: str) -> Dict[str, Any]:
    """
    è·å–æŒ‡å®å‡­è¯ç„é¢åº¦ä¿¡æ¯
    
    Args:
        access_token: Omni è®¿é—®ä»¤ç‰Œ
        
    Returns:
        åŒ…å«é¢åº¦ä¿¡æ¯ç„å­—å…¸ï¼Œæ ¼å¼ä¸ºï¼
        {
            "success": True/False,
            "models": {
                "model_name": {
                    "remaining": 0.95,
                    "resetTime": "12-20 10:30",
                    "resetTimeRaw": "2025-12-20T02:30:00Z"
                }
            },
            "error": "é”™è¯¯ä¿¡æ¯" (ä»…åœ¨å¤±è´¥æ—¶)
        }
    """

    headers = build_omni_headers(access_token)

    try:
        omni_url = await get_ogw_api_url()

        response = await post_async(
            url=f"{omni_url}/v1internal:fetchAvailableModels",
            json={},
            headers=headers,
            timeout=30.0
        )

        if response.status_code == 200:
            data = response.json()
            log.debug(f"[OMNI QUOTA] Raw response: {json.dumps(data, ensure_ascii=False)[:500]}")

            quota_info = {}

            if 'models' in data and isinstance(data['models'], dict):
                for model_id, model_data in data['models'].items():
                    if isinstance(model_data, dict) and 'quotaInfo' in model_data:
                        quota = model_data['quotaInfo']
                        remaining = quota.get('remainingFraction', 0)
                        reset_time_raw = quota.get('resetTime', '')

                        # è½¬æ¢ä¸ºåŒ—äº¬æ—¶é—´
                        reset_time_beijing = 'N/A'
                        if reset_time_raw:
                            try:
                                utc_date = datetime.fromisoformat(reset_time_raw.replace('Z', '+00:00'))
                                # è½¬æ¢ä¸ºåŒ—äº¬æ—¶é—´ (UTC+8)
                                from datetime import timedelta
                                beijing_date = utc_date + timedelta(hours=8)
                                reset_time_beijing = beijing_date.strftime('%m-%d %H:%M')
                            except Exception as e:
                                log.warning(f"[OMNI QUOTA] Failed to parse reset time: {e}")

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
            log.error(f"[OMNI QUOTA] Failed to fetch quota ({response.status_code}): {response.text[:500]}")
            return {
                "success": False,
                "error": f"APIè¿”å›é”™è¯¯: {response.status_code}"
            }

    except Exception as e:
        import traceback
        log.error(f"[OMNI QUOTA] Failed to fetch quota: {e}")
        log.error(f"[OMNI QUOTA] Traceback: {traceback.format_exc()}")
        return {
            "success": False,
            "error": str(e)
        }
