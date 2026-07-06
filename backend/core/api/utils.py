"""Internal implementation detail."""

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
from core.credential_manager import CredentialManager




async def check_should_auto_disable(status_code: int) -> bool:
    """Internal implementation detail."""
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
    """Internal implementation detail."""
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
    """Internal implementation detail."""

    should_auto_disable = await check_should_auto_disable(status_code)

    if should_auto_disable:

        await handle_auto_disable(credential_manager, status_code, credential_name, mode)


        if retry_enabled and attempt < max_retries:
            log.info(
                f"[{mode.upper()} RETRY] Retrying with next credential after auto-disable "
                f"(status {status_code}, attempt {attempt + 1}/{max_retries})"
            )
            await asyncio.sleep(retry_interval)
            return True
        return False


    if status_code in (429, 500, 503) and retry_enabled and attempt < max_retries:
        log.info(
            f"[{mode.upper()} RETRY] {status_code} error encountered, retrying "
            f"(attempt {attempt + 1}/{max_retries})"
        )
        await asyncio.sleep(retry_interval)
        return True


    return False




async def get_retry_config() -> Dict[str, Any]:
    """Internal implementation detail."""
    return {
        "retry_enabled": await get_retry_429_enabled(),
        "max_retries": await get_retry_429_max_retries(),
        "retry_interval": await get_retry_429_interval(),
    }




async def record_api_call_success(
    credential_manager: CredentialManager,
    credential_name: str,
    mode: str = "code_assist",
    model_name: Optional[str] = None
) -> None:
    """Internal implementation detail."""
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
    """Internal implementation detail."""
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




async def parse_and_log_cooldown(
    error_text: str,
    mode: str = "code_assist"
) -> Optional[float]:
    """Internal implementation detail."""
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




async def collect_streaming_response(stream_generator) -> Response:
    """Internal implementation detail."""

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

    collected_text = []
    collected_thought_text = []
    collected_other_parts = []
    collected_tool_parts_count = 0
    has_data = False
    line_count = 0

    log.debug("[STREAM COLLECTOR] Starting to collect streaming response")

    try:
        async for line in stream_generator:
            line_count += 1


            if isinstance(line, Response):
                log.debug(f"[STREAM COLLECTOR] Received error response, status code: {line.status_code}")
                return line


            if isinstance(line, bytes):
                line_str = line.decode('utf-8', errors='ignore')
                log.debug(f"[STREAM COLLECTOR] Processing bytes line {line_count}: {line_str[:200] if line_str else 'empty'}")
            elif isinstance(line, str):
                line_str = line
                log.debug(f"[STREAM COLLECTOR] Processing line {line_count}: {line_str[:200] if line_str else 'empty'}")
            else:
                log.debug(f"[STREAM COLLECTOR] Skipping non-string/bytes line: {type(line)}")
                continue


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


                response_obj = chunk.get("response", {})
                if not response_obj:
                    log.debug("[STREAM COLLECTOR] No 'response' key in chunk, trying direct access")
                    response_obj = chunk

                candidates = response_obj.get("candidates", [])
                log.debug(f"[STREAM COLLECTOR] Found {len(candidates)} candidates")
                if not candidates:
                    log.debug(f"[STREAM COLLECTOR] No candidates in chunk, chunk structure: {list(chunk.keys()) if isinstance(chunk, dict) else type(chunk)}")
                    continue

                candidate = candidates[0]


                content = candidate.get("content", {})
                parts = content.get("parts", [])
                log.debug(f"[STREAM COLLECTOR] Processing {len(parts)} parts from candidate")

                for part in parts:
                    if not isinstance(part, dict):
                        continue



                    if "functionCall" in part or "functionResponse" in part or "function_call" in part:
                        collected_other_parts.append(part)
                        collected_tool_parts_count += 1
                        log.debug(f"[STREAM COLLECTOR] Collected tool part: {list(part.keys())}")
                        continue


                    text = part.get("text", "")
                    if text:

                        if part.get("thought", False):
                            collected_thought_text.append(text)
                            log.debug(f"[STREAM COLLECTOR] Collected thought text: {text[:100]}")
                        else:
                            collected_text.append(text)
                            log.debug(f"[STREAM COLLECTOR] Collected regular text: {text[:100]}")

                    elif "inlineData" in part or "fileData" in part or "executableCode" in part or "codeExecutionResult" in part:
                        collected_other_parts.append(part)
                        log.debug(f"[STREAM COLLECTOR] Collected non-text part: {list(part.keys())}")


                if candidate.get("finishReason"):
                    merged_response["response"]["candidates"][0]["finishReason"] = candidate["finishReason"]

                if candidate.get("safetyRatings"):
                    merged_response["response"]["candidates"][0]["safetyRatings"] = candidate["safetyRatings"]

                if candidate.get("citationMetadata"):
                    merged_response["response"]["candidates"][0]["citationMetadata"] = candidate["citationMetadata"]


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


    if not has_data:
        log.error(f"[STREAM COLLECTOR] No data collected from stream after {line_count} lines")
        return Response(
            content=json.dumps({"error": "No data collected from stream"}),
            status_code=500,
            media_type="application/json"
        )


    final_parts = []


    if collected_thought_text:
        final_parts.append({
            "text": "".join(collected_thought_text),
            "thought": True
        })


    if collected_text:
        final_parts.append({
            "text": "".join(collected_text)
        })


    final_parts.extend(collected_other_parts)


    if not final_parts:
        final_parts.append({"text": ""})

    merged_response["response"]["candidates"][0]["content"]["parts"] = final_parts

    log.info(
        f"[STREAM COLLECTOR] Collected {len(collected_text)} text chunks, "
        f"{len(collected_thought_text)} thought chunks, {len(collected_other_parts)} other parts "
        f"(tool parts: {collected_tool_parts_count})"
    )


    if "response" in merged_response and "candidates" not in merged_response:
        log.debug(f"[STREAM COLLECTOR] Unwrapping response")
        merged_response = merged_response["response"]


    return Response(
        content=json.dumps(merged_response, ensure_ascii=False).encode('utf-8'),
        status_code=200,
        headers={},
        media_type="application/json"
    )


RESOURCE_EXHAUSTED_COOLDOWN_HOURS = 4


def parse_quota_reset_timestamp(error_response: dict) -> Optional[float]:
    """Internal implementation detail."""
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
