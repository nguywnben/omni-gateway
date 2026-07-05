"""
Base API Client - å…±ç”¨ç„ API å®¢æˆ·ç«¯åŸºç¡€åŸèƒ½
æä¾›é”™è¯¯å¤„ç†ă€è‡ªå¨å°ç¦ă€é‡è¯•é€»è¾‘ç­‰å…±åŒåŸèƒ½
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import Response

from config import (
    get_auto_disable_enabled,
    get_auto_disable_error_codes,
    get_retry_429_enabled,
    get_retry_429_interval,
    get_retry_429_max_retries,
)
from log import log
from omni_gateway.credential_manager import CredentialManager


# ==================== é”™è¯¯æ£€æŸ¥ä¸å¤„ç† ====================

async def check_should_auto_disable(status_code: int) -> bool:
    """
    æ£€æŸ¥æ˜¯å¦åº”è¯¥è§¦å‘è‡ªå¨å°ç¦
    
    Args:
        status_code: HTTPç¶æ€ç 
        
    Returns:
        bool: æ˜¯å¦åº”è¯¥è§¦å‘è‡ªå¨å°ç¦
    """
    return (
        await get_auto_disable_enabled()
        and status_code in await get_auto_disable_error_codes()
    )


async def handle_auto_disable(
    credential_manager: CredentialManager,
    status_code: int,
    credential_name: str,
    mode: str = "code_assist"
) -> None:
    """
    å¤„ç†è‡ªå¨å°ç¦ï¼ç›´æ¥ç¦ç”¨å‡­è¯
    
    Args:
        credential_manager: å‡­è¯ç®¡ç†å™¨å®ä¾‹
        status_code: HTTPç¶æ€ç 
        credential_name: å‡­è¯åç§°
        mode: æ¨¡å¼ï¼ˆcode_assist æˆ– omniï¼‰
    """
    if credential_manager and credential_name:
        log.warning(
            f"[{mode.upper()} AUTO_DISABLE] Status {status_code} triggers auto-disable for credential: {credential_name}"
        )
        await credential_manager.set_cred_disabled(
            credential_name, True, mode=mode
        )


async def handle_error_with_retry(
    credential_manager: CredentialManager,
    status_code: int,
    credential_name: str,
    retry_enabled: bool,
    attempt: int,
    max_retries: int,
    retry_interval: float,
    mode: str = "code_assist"
) -> bool:
    """
    ç»Ÿä¸€å¤„ç†é”™è¯¯å’Œé‡è¯•é€»è¾‘

    ä»…åœ¨ä»¥ä¸‹æƒ…å†µä¸‹è¿›è¡Œè‡ªå¨é‡è¯•:
    1. 429é”™è¯¯(é€Ÿç‡é™åˆ¶)
    2. 503é”™è¯¯(æœå¡ä¸å¯ç”¨)
    3. 500é”™è¯¯(æœå¡ä¸´æ—¶ä¸å¯ç”¨)
    4. å¯¼è‡´å‡­è¯å°ç¦ç„é”™è¯¯(OGW_AUTO_DISABLE_ERROR_CODESé…ç½®)

    Args:
        credential_manager: å‡­è¯ç®¡ç†å™¨å®ä¾‹
        status_code: HTTPç¶æ€ç 
        credential_name: å‡­è¯åç§°
        retry_enabled: æ˜¯å¦å¯ç”¨é‡è¯•
        attempt: å½“å‰é‡è¯•æ¬¡æ•°
        max_retries: æœ€å¤§é‡è¯•æ¬¡æ•°
        retry_interval: é‡è¯•é—´é”
        mode: æ¨¡å¼ï¼ˆcode_assist æˆ– omniï¼‰
        
    Returns:
        bool: Trueè¡¨ç¤ºéœ€è¦ç»§ç»­é‡è¯•ï¼ŒFalseè¡¨ç¤ºä¸éœ€è¦é‡è¯•
    """
    # ä¼˜å…ˆæ£€æŸ¥è‡ªå¨å°ç¦
    should_auto_disable = await check_should_auto_disable(status_code)

    if should_auto_disable:
        # è§¦å‘è‡ªå¨å°ç¦
        await handle_auto_disable(credential_manager, status_code, credential_name, mode)

        # è‡ªå¨å°ç¦åï¼Œä»ç„¶å°è¯•é‡è¯•ï¼ˆä¼åœ¨ä¸‹æ¬¡å¾ªç¯ä¸­è‡ªå¨è·å–æ–°å‡­è¯ï¼‰
        if retry_enabled and attempt < max_retries:
            log.info(
                f"[{mode.upper()} RETRY] Retrying with next credential after auto-disable "
                f"(status {status_code}, attempt {attempt + 1}/{max_retries})"
            )
            await asyncio.sleep(retry_interval)
            return True
        return False

    # å¦‚æœä¸è§¦å‘è‡ªå¨å°ç¦ï¼Œä»…å¯¹429ă€503å’Œ500é”™è¯¯è¿›è¡Œé‡è¯•
    if status_code in (429, 500, 503) and retry_enabled and attempt < max_retries:
        log.info(
            f"[{mode.upper()} RETRY] {status_code} error encountered, retrying "
            f"(attempt {attempt + 1}/{max_retries})"
        )
        await asyncio.sleep(retry_interval)
        return True

    # å…¶ä»–é”™è¯¯ä¸è¿›è¡Œé‡è¯•
    return False


# ==================== é‡è¯•é…ç½®è·å– ====================

async def get_retry_config() -> Dict[str, Any]:
    """
    è·å–é‡è¯•é…ç½®
    
    Returns:
        åŒ…å«é‡è¯•é…ç½®ç„å­—å…¸
    """
    return {
        "retry_enabled": await get_retry_429_enabled(),
        "max_retries": await get_retry_429_max_retries(),
        "retry_interval": await get_retry_429_interval(),
    }


# ==================== APIè°ƒç”¨ç»“æœè®°å½• ====================

async def record_api_call_success(
    credential_manager: CredentialManager,
    credential_name: str,
    mode: str = "code_assist",
    model_name: Optional[str] = None
) -> None:
    """
    è®°å½•APIè°ƒç”¨æˆåŸ
    
    Args:
        credential_manager: å‡­è¯ç®¡ç†å™¨å®ä¾‹
        credential_name: å‡­è¯åç§°
        mode: æ¨¡å¼ï¼ˆcode_assist æˆ– omniï¼‰
        model_name: æ¨¡å‹åç§°ï¼ˆç”¨äºæ¨¡å‹çº§CDï¼‰
    """
    if credential_manager and credential_name:
        await credential_manager.record_api_call_result(
            credential_name, True, mode=mode, model_name=model_name
        )


async def record_api_call_error(
    credential_manager: CredentialManager,
    credential_name: str,
    status_code: int,
    cooldown_until: Optional[float] = None,
    mode: str = "code_assist",
    model_name: Optional[str] = None,
    error_message: Optional[str] = None
) -> None:
    """
    è®°å½•APIè°ƒç”¨é”™è¯¯

    Args:
        credential_manager: å‡­è¯ç®¡ç†å™¨å®ä¾‹
        credential_name: å‡­è¯åç§°
        status_code: HTTPç¶æ€ç 
        cooldown_until: å†·å´æˆªæ­¢æ—¶é—´ï¼ˆUnixæ—¶é—´æˆ³ï¼‰
        mode: æ¨¡å¼ï¼ˆcode_assist æˆ– omniï¼‰
        model_name: æ¨¡å‹åç§°ï¼ˆç”¨äºæ¨¡å‹çº§CDï¼‰
        error_message: é”™è¯¯ä¿¡æ¯ï¼ˆå¯é€‰ï¼‰
    """
    if credential_manager and credential_name:
        await credential_manager.record_api_call_result(
            credential_name,
            False,
            status_code,
            cooldown_until=cooldown_until,
            mode=mode,
            model_name=model_name,
            error_message=error_message
        )


# ==================== 429é”™è¯¯å¤„ç† ====================

async def parse_and_log_cooldown(
    error_text: str,
    mode: str = "code_assist"
) -> Optional[float]:
    """
    è§£æå¹¶è®°å½•å†·å´æ—¶é—´

    Args:
        error_text: é”™è¯¯å“åº”æ–‡æœ¬
        mode: æ¨¡å¼ï¼ˆcode_assist æˆ– omniï¼‰

    Returns:
        å†·å´æˆªæ­¢æ—¶é—´ï¼ˆUnixæ—¶é—´æˆ³ï¼‰ï¼Œå¦‚æœè§£æå¤±è´¥åˆ™è¿”å›None
    """
    try:
        error_data = json.loads(error_text)
        cooldown_until = parse_quota_reset_timestamp(error_data)
        if cooldown_until:
            log.info(
                f"[{mode.upper()}] Quota cooldown detected: "
                f"{datetime.fromtimestamp(cooldown_until, timezone.utc).isoformat()}"
            )
            return cooldown_until
    except Exception as parse_err:
        log.debug(f"[{mode.upper()}] Failed to parse cooldown time: {parse_err}")
    return None


# ==================== æµå¼å“åº”æ”¶é›† ====================

async def collect_streaming_response(stream_generator) -> Response:
    """
    å°†Geminiæµå¼å“åº”æ”¶é›†ä¸ºä¸€æ¡å®Œæ•´ç„éæµå¼å“åº”

    Args:
        stream_generator: æµå¼å“åº”ç”Ÿæˆå™¨ï¼Œäº§ç”Ÿ "data: {json}" æ ¼å¼ç„è¡Œæˆ–Responseå¯¹è±¡

    Returns:
        Response: åˆå¹¶åç„å®Œæ•´å“åº”å¯¹è±¡

    Example:
        >>> async for line in stream_generator:
        ...     # line format: "data: {...}" or Response object
        >>> response = await collect_streaming_response(stream_generator)
    """
    # åˆå§‹åŒ–å“åº”ç»“æ„
    merged_response = {
        "response": {
            "candidates": [{
                "content": {
                    "parts": [],
                    "role": "model"
                },
                "finishReason": None,
                "safetyRatings": [],
                "citationMetadata": None
            }],
            "usageMetadata": {
                "promptTokenCount": 0,
                "candidatesTokenCount": 0,
                "totalTokenCount": 0
            }
        }
    }

    collected_text = []  # ç”¨äºæ”¶é›†æ–‡æœ¬å†…å®¹
    collected_thought_text = []  # ç”¨äºæ”¶é›†æ€ç»´é“¾å†…å®¹
    collected_other_parts = []  # ç”¨äºæ”¶é›†å…¶ä»–ç±»å‹ç„partsï¼ˆå›¾ç‰‡ă€æ–‡ä»¶ă€å·¥å…·è°ƒç”¨ç­‰ï¼‰
    collected_tool_parts_count = 0  # è®°å½•å·¥å…·è°ƒç”¨ç›¸å…³partæ•°é‡
    has_data = False
    line_count = 0

    log.debug("[STREAM COLLECTOR] Starting to collect streaming response")

    try:
        async for line in stream_generator:
            line_count += 1

            # å¦‚æœæ”¶åˆ°ç„æ˜¯Responseå¯¹è±¡ï¼ˆé”™è¯¯ï¼‰ï¼Œç›´æ¥è¿”å›
            if isinstance(line, Response):
                log.debug(f"[STREAM COLLECTOR] Received error response, status code: {line.status_code}")
                return line

            # å¤„ç† bytes ç±»å‹
            if isinstance(line, bytes):
                line_str = line.decode('utf-8', errors='ignore')
                log.debug(f"[STREAM COLLECTOR] Processing bytes line {line_count}: {line_str[:200] if line_str else 'empty'}")
            elif isinstance(line, str):
                line_str = line
                log.debug(f"[STREAM COLLECTOR] Processing line {line_count}: {line_str[:200] if line_str else 'empty'}")
            else:
                log.debug(f"[STREAM COLLECTOR] Skipping non-string/bytes line: {type(line)}")
                continue

            # è§£ææµå¼æ•°æ®è¡Œ
            if not line_str.startswith("data: "):
                log.debug(f"[STREAM COLLECTOR] Skipping line without 'data: ' prefix: {line_str[:100]}")
                continue

            raw = line_str[6:].strip()
            if raw == "[DONE]":
                log.debug("[STREAM COLLECTOR] Received [DONE] marker")
                break

            try:
                log.debug(f"[STREAM COLLECTOR] Parsing JSON: {raw[:200]}")
                chunk = json.loads(raw)
                has_data = True
                log.debug(f"[STREAM COLLECTOR] Chunk keys: {chunk.keys() if isinstance(chunk, dict) else type(chunk)}")

                # æå–å“åº”å¯¹è±¡
                response_obj = chunk.get("response", {})
                if not response_obj:
                    log.debug("[STREAM COLLECTOR] No 'response' key in chunk, trying direct access")
                    response_obj = chunk  # å°è¯•ç›´æ¥ä½¿ç”¨chunk

                candidates = response_obj.get("candidates", [])
                log.debug(f"[STREAM COLLECTOR] Found {len(candidates)} candidates")
                if not candidates:
                    log.debug(f"[STREAM COLLECTOR] No candidates in chunk, chunk structure: {list(chunk.keys()) if isinstance(chunk, dict) else type(chunk)}")
                    continue

                candidate = candidates[0]

                # æ”¶é›†æ–‡æœ¬å†…å®¹
                content = candidate.get("content", {})
                parts = content.get("parts", [])
                log.debug(f"[STREAM COLLECTOR] Processing {len(parts)} parts from candidate")

                for part in parts:
                    if not isinstance(part, dict):
                        continue

                    # ä¼˜å…ˆä¿ç•™å·¥å…·è°ƒç”¨ç›¸å…³ partï¼ˆfunctionCall / functionResponseï¼‰
                    # é¿å…åœ¨ stream_to_nonstream æ¨¡å¼ä¸‹å·¥å…·è°ƒç”¨ä¸¢å¤±
                    if "functionCall" in part or "functionResponse" in part or "function_call" in part:
                        collected_other_parts.append(part)
                        collected_tool_parts_count += 1
                        log.debug(f"[STREAM COLLECTOR] Collected tool part: {list(part.keys())}")
                        continue

                    # å¤„ç†æ–‡æœ¬å†…å®¹
                    text = part.get("text", "")
                    if text:
                        # åŒºåˆ†æ™®é€æ–‡æœ¬å’Œæ€ç»´é“¾
                        if part.get("thought", False):
                            collected_thought_text.append(text)
                            log.debug(f"[STREAM COLLECTOR] Collected thought text: {text[:100]}")
                        else:
                            collected_text.append(text)
                            log.debug(f"[STREAM COLLECTOR] Collected regular text: {text[:100]}")
                    # å¤„ç†éæ–‡æœ¬å†…å®¹ï¼ˆå›¾ç‰‡ă€æ–‡ä»¶ç­‰ï¼‰
                    elif "inlineData" in part or "fileData" in part or "executableCode" in part or "codeExecutionResult" in part:
                        collected_other_parts.append(part)
                        log.debug(f"[STREAM COLLECTOR] Collected non-text part: {list(part.keys())}")

                # æ”¶é›†å…¶ä»–ä¿¡æ¯ï¼ˆä½¿ç”¨æœ€åä¸€ä¸ªå—ç„å€¼ï¼‰
                if candidate.get("finishReason"):
                    merged_response["response"]["candidates"][0]["finishReason"] = candidate["finishReason"]

                if candidate.get("safetyRatings"):
                    merged_response["response"]["candidates"][0]["safetyRatings"] = candidate["safetyRatings"]

                if candidate.get("citationMetadata"):
                    merged_response["response"]["candidates"][0]["citationMetadata"] = candidate["citationMetadata"]

                # æ›´æ–°ä½¿ç”¨å…ƒæ•°æ®
                usage = response_obj.get("usageMetadata", {})
                if usage:
                    merged_response["response"]["usageMetadata"].update(usage)

            except json.JSONDecodeError as e:
                log.debug(f"[STREAM COLLECTOR] Failed to parse JSON chunk: {e}")
                continue
            except Exception as e:
                log.debug(f"[STREAM COLLECTOR] Error processing chunk: {e}")
                continue

    except Exception as e:
        log.error(f"[STREAM COLLECTOR] Error collecting stream after {line_count} lines: {e}")
        return Response(
            content=json.dumps({"error": f"Failed to collect streaming response: {str(e)}"}),
            status_code=500,
            media_type="application/json"
        )

    log.debug(f"[STREAM COLLECTOR] Finished iteration, has_data={has_data}, line_count={line_count}")

    # å¦‚æœæ²¡æœ‰æ”¶é›†åˆ°ä»»ä½•æ•°æ®ï¼Œè¿”å›é”™è¯¯
    if not has_data:
        log.error(f"[STREAM COLLECTOR] No data collected from stream after {line_count} lines")
        return Response(
            content=json.dumps({"error": "No data collected from stream"}),
            status_code=500,
            media_type="application/json"
        )

    # ç»„è£…æœ€ç»ˆç„parts
    final_parts = []

    # å…ˆæ·»å æ€ç»´é“¾å†…å®¹ï¼ˆå¦‚æœæœ‰ï¼‰
    if collected_thought_text:
        final_parts.append({
            "text": "".join(collected_thought_text),
            "thought": True
        })

    # å†æ·»å æ™®é€æ–‡æœ¬å†…å®¹
    if collected_text:
        final_parts.append({
            "text": "".join(collected_text)
        })

    # æ·»å å…¶ä»–ç±»å‹ç„partsï¼ˆå›¾ç‰‡ă€æ–‡ä»¶ç­‰ï¼‰
    final_parts.extend(collected_other_parts)

    # å¦‚æœæ²¡æœ‰ä»»ä½•å†…å®¹ï¼Œæ·»å ç©ºæ–‡æœ¬
    if not final_parts:
        final_parts.append({"text": ""})

    merged_response["response"]["candidates"][0]["content"]["parts"] = final_parts

    log.info(
        f"[STREAM COLLECTOR] Collected {len(collected_text)} text chunks, "
        f"{len(collected_thought_text)} thought chunks, {len(collected_other_parts)} other parts "
        f"(tool parts: {collected_tool_parts_count})"
    )

    # å»æ‰åµŒå¥—ç„ "response" åŒ…è£…ï¼ˆOmniæ ¼å¼ -> æ ‡å‡†Geminiæ ¼å¼ï¼‰
    if "response" in merged_response and "candidates" not in merged_response:
        log.debug(f"[STREAM COLLECTOR] Unwrapping response")
        merged_response = merged_response["response"]

    # è¿”å›çº¯JSONæ ¼å¼
    return Response(
        content=json.dumps(merged_response, ensure_ascii=False).encode('utf-8'),
        status_code=200,
        headers={},
        media_type="application/json"
    )


RESOURCE_EXHAUSTED_COOLDOWN_HOURS = 4  # RESOURCE_EXHAUSTED é”™è¯¯ç„é»˜è®¤å†·å´æ—¶é—´ï¼ˆå°æ—¶ï¼‰


def parse_quota_reset_timestamp(error_response: dict) -> Optional[float]:
    """
    ä»Google APIé”™è¯¯å“åº”ä¸­æå–quotaé‡ç½®æ—¶é—´æˆ³

    Args:
        error_response: Google APIè¿”å›ç„é”™è¯¯å“åº”å­—å…¸

    Returns:
        Unixæ—¶é—´æˆ³ï¼ˆç§’ï¼‰ï¼Œå¦‚æœæ— æ³•è§£æåˆ™è¿”å›None

    ç¤ºä¾‹é”™è¯¯å“åº”:
    {
      "error": {
        "code": 429,
        "message": "You have exhausted your capacity...",
        "status": "RESOURCE_EXHAUSTED",
        "details": [
          {
            "@type": "type.googleapis.com/google.rpc.ErrorInfo",
            "reason": "QUOTA_EXHAUSTED",
            "metadata": {
              "quotaResetTimeStamp": "2025-11-30T14:57:24Z",
              "quotaResetDelay": "13h19m1.20964964s"
            }
          }
        ]
      }
    }
    """
    try:
        error_obj = error_response.get("error", {})
        details = error_obj.get("details", [])

        for detail in details:
            if detail.get("@type") == "type.googleapis.com/google.rpc.ErrorInfo":
                reset_timestamp_str = detail.get("metadata", {}).get("quotaResetTimeStamp")

                if reset_timestamp_str:
                    if reset_timestamp_str.endswith("Z"):
                        reset_timestamp_str = reset_timestamp_str.replace("Z", "+00:00")

                    reset_dt = datetime.fromisoformat(reset_timestamp_str)
                    if reset_dt.tzinfo is None:
                        reset_dt = reset_dt.replace(tzinfo=timezone.utc)

                    return reset_dt.astimezone(timezone.utc).timestamp()

        # å¦‚æœæ˜¯ RESOURCE_EXHAUSTED é”™è¯¯ä¸”æ¶ˆæ¯å®Œå…¨åŒ¹é…ï¼Œè®¾ç½®é»˜è®¤4å°æ—¶å†·å´æ—¶é—´
        if (
            error_obj.get("status") == "RESOURCE_EXHAUSTED"
            and error_obj.get("message") == "Resource has been exhausted (e.g. check quota)."
        ):
            import time
            cooldown_until = time.time() + RESOURCE_EXHAUSTED_COOLDOWN_HOURS * 3600
            return cooldown_until

        return None

    except Exception:
        return None
