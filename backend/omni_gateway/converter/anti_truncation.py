"""
Anti-Truncation Module - Ensures complete streaming output
ä¿æŒä¸€ä¸ªæµå¼è¯·æ±‚å†…å®Œæ•´è¾“å‡ºç„åæˆªæ–­æ¨¡å—
"""

import io
import json
import re
from typing import Any, AsyncGenerator, Dict, List, Tuple

from fastapi.responses import StreamingResponse

from log import log

# åæˆªæ–­é…ç½®
DONE_MARKER = "[done]"
CONTINUATION_PROMPT = f"""è¯·ä»åˆæ‰è¢«æˆªæ–­ç„åœ°æ–¹ç»§ç»­è¾“å‡ºå‰©ä½™ç„æ‰€æœ‰å†…å®¹ă€‚

é‡è¦æé†’ï¼
1. ä¸è¦é‡å¤å‰é¢å·²ç»è¾“å‡ºç„å†…å®¹
2. ç›´æ¥ç»§ç»­è¾“å‡ºï¼Œæ— éœ€ä»»ä½•å‰è¨€æˆ–è§£é‡
3. å½“ä½ å®Œæ•´å®Œæˆæ‰€æœ‰å†…å®¹è¾“å‡ºåï¼Œå¿…é¡»åœ¨æœ€åä¸€è¡Œå•ç‹¬è¾“å‡ºï¼{DONE_MARKER}
4. {DONE_MARKER} æ ‡è®°è¡¨ç¤ºä½ ç„å›ç­”å·²ç»å®Œå…¨ç»“æŸï¼Œè¿™æ˜¯å¿…éœ€ç„ç»“æŸæ ‡è®°

ç°åœ¨è¯·ç»§ç»­è¾“å‡ºï¼"""

# æ­£åˆ™æ›¿æ¢é…ç½®
REGEX_REPLACEMENTS: List[Tuple[str, str, str]] = [
    (
        "age_pattern",  # æ›¿æ¢è§„åˆ™åç§°
        r"(?:[1-9]|1[0-8])å²(?:ç„)?|(?:åä¸€|åäºŒ|åä¸‰|åå››|åäº”|åå…­|åä¸ƒ|åå…«|å|ä¸€|äºŒ|ä¸‰|å››|äº”|å…­|ä¸ƒ|å…«|ä¹)å²(?:ç„)?",  # æ­£åˆ™æ¨¡å¼
        "",  # æ›¿æ¢æ–‡æœ¬
    ),
    # å¯åœ¨æ­¤å¤„æ·»å æ›´å¤æ›¿æ¢è§„åˆ™
    # ("rule_name", r"pattern", "replacement"),
]


def apply_regex_replacements(text: str) -> str:
    """
    å¯¹æ–‡æœ¬åº”ç”¨æ­£åˆ™æ›¿æ¢è§„åˆ™

    Args:
        text: è¦å¤„ç†ç„æ–‡æœ¬

    Returns:
        å¤„ç†åç„æ–‡æœ¬
    """
    if not text:
        return text

    processed_text = text
    replacement_count = 0

    for rule_name, pattern, replacement in REGEX_REPLACEMENTS:
        try:
            # ç¼–è¯‘æ­£åˆ™è¡¨è¾¾å¼ï¼Œä½¿ç”¨IGNORECASEæ ‡å¿—
            regex = re.compile(pattern, re.IGNORECASE)

            # æ‰§è¡Œæ›¿æ¢
            new_text, count = regex.subn(replacement, processed_text)

            if count > 0:
                log.debug(f"Regex replacement '{rule_name}': {count} matches replaced")
                processed_text = new_text
                replacement_count += count

        except re.error as e:
            log.error(f"Invalid regex pattern in rule '{rule_name}': {e}")
            continue

    if replacement_count > 0:
        log.info(f"Applied {replacement_count} regex replacements to text")

    return processed_text


def apply_regex_replacements_to_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    å¯¹è¯·æ±‚payloadä¸­ç„æ–‡æœ¬å†…å®¹åº”ç”¨æ­£åˆ™æ›¿æ¢

    Args:
        payload: è¯·æ±‚payload

    Returns:
        åº”ç”¨æ›¿æ¢åç„payload
    """
    if not REGEX_REPLACEMENTS:
        return payload

    modified_payload = payload.copy()
    request_data = modified_payload.get("request", {})

    # å¤„ç†contentsä¸­ç„æ–‡æœ¬
    contents = request_data.get("contents", [])
    if contents:
        new_contents = []
        for content in contents:
            if isinstance(content, dict):
                new_content = content.copy()
                parts = new_content.get("parts", [])
                if parts:
                    new_parts = []
                    for part in parts:
                        if isinstance(part, dict) and "text" in part:
                            new_part = part.copy()
                            new_part["text"] = apply_regex_replacements(part["text"])
                            new_parts.append(new_part)
                        else:
                            new_parts.append(part)
                    new_content["parts"] = new_parts
                new_contents.append(new_content)
            else:
                new_contents.append(content)

        request_data["contents"] = new_contents
        modified_payload["request"] = request_data
        log.debug("Applied regex replacements to request contents")

    return modified_payload


def apply_anti_truncation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    å¯¹è¯·æ±‚payloadåº”ç”¨åæˆªæ–­å¤„ç†å’Œæ­£åˆ™æ›¿æ¢
    åœ¨systemInstructionä¸­æ·»å æé†’ï¼Œè¦æ±‚æ¨¡å‹åœ¨ç»“æŸæ—¶è¾“å‡ºDONE_MARKERæ ‡è®°

    Args:
        payload: åŸå§‹è¯·æ±‚payload

    Returns:
        æ·»å äº†åæˆªæ–­æŒ‡ä»¤å¹¶åº”ç”¨äº†æ­£åˆ™æ›¿æ¢ç„payload
    """
    # é¦–å…ˆåº”ç”¨æ­£åˆ™æ›¿æ¢
    modified_payload = apply_regex_replacements_to_payload(payload)
    request_data = modified_payload.get("request", {})

    # è·å–æˆ–åˆ›å»ºsystemInstruction
    system_instruction = request_data.get("systemInstruction", {})
    if not system_instruction:
        system_instruction = {"parts": []}
    elif "parts" not in system_instruction:
        system_instruction["parts"] = []

    # æ·»å åæˆªæ–­æŒ‡ä»¤
    anti_truncation_instruction = {
        "text": f"""ä¸¥æ ¼æ‰§è¡Œä»¥ä¸‹è¾“å‡ºç»“æŸè§„åˆ™ï¼

1. å½“ä½ å®Œæˆå®Œæ•´å›ç­”æ—¶ï¼Œå¿…é¡»åœ¨è¾“å‡ºç„æœ€åå•ç‹¬ä¸€è¡Œè¾“å‡ºï¼{DONE_MARKER}
2. {DONE_MARKER} æ ‡è®°è¡¨ç¤ºä½ ç„å›ç­”å·²ç»å®Œå…¨ç»“æŸï¼Œè¿™æ˜¯å¿…éœ€ç„ç»“æŸæ ‡è®°
3. åªæœ‰è¾“å‡ºäº† {DONE_MARKER} æ ‡è®°ï¼Œç³»ç»Ÿæ‰è®¤ä¸ºä½ ç„å›ç­”æ˜¯å®Œæ•´ç„
4. å¦‚æœä½ ç„å›ç­”è¢«æˆªæ–­ï¼Œç³»ç»Ÿä¼è¦æ±‚ä½ ç»§ç»­è¾“å‡ºå‰©ä½™å†…å®¹
5. æ— è®ºå›ç­”é•¿çŸ­ï¼Œéƒ½å¿…é¡»ä»¥ {DONE_MARKER} æ ‡è®°ç»“æŸ

ç¤ºä¾‹æ ¼å¼ï¼
```
ä½ ç„å›ç­”å†…å®¹...
æ›´å¤å›ç­”å†…å®¹...
{DONE_MARKER}
```

æ³¨æ„ï¼{DONE_MARKER} å¿…é¡»å•ç‹¬å ä¸€è¡Œï¼Œå‰é¢ä¸è¦æœ‰ä»»ä½•å…¶ä»–å­—ç¬¦ă€‚

è¿™ä¸ªè§„åˆ™å¯¹äºç¡®ä¿è¾“å‡ºå®Œæ•´æ€§æå…¶é‡è¦ï¼Œè¯·ä¸¥æ ¼éµå®ˆă€‚"""
    }

    # æ£€æŸ¥æ˜¯å¦å·²ç»åŒ…å«åæˆªæ–­æŒ‡ä»¤
    has_done_instruction = any(
        part.get("text", "").find(DONE_MARKER) != -1
        for part in system_instruction["parts"]
        if isinstance(part, dict)
    )

    if not has_done_instruction:
        system_instruction["parts"].append(anti_truncation_instruction)
        request_data["systemInstruction"] = system_instruction
        modified_payload["request"] = request_data

        log.debug("Applied anti-truncation instruction to request")

    return modified_payload


class AntiTruncationStreamProcessor:
    """åæˆªæ–­æµå¼å¤„ç†å™¨"""

    def __init__(
        self,
        original_request_func,
        payload: Dict[str, Any],
        max_attempts: int = 3,
        enable_prefill_mode: bool = False,
    ):
        self.original_request_func = original_request_func
        self.base_payload = payload.copy()
        self.max_attempts = max_attempts
        self.enable_prefill_mode = enable_prefill_mode
        # ä½¿ç”¨ StringIO é¿å…å­—ç¬¦ä¸²æ‹¼æ¥ç„å†…å­˜é—®é¢˜
        self.collected_content = io.StringIO()
        self.current_attempt = 0

    def _get_collected_text(self) -> str:
        """è·å–æ”¶é›†ç„æ–‡æœ¬å†…å®¹"""
        return self.collected_content.getvalue()

    def _append_content(self, content: str):
        """è¿½å å†…å®¹åˆ°æ”¶é›†å™¨"""
        if content:
            self.collected_content.write(content)

    def _clear_content(self):
        """æ¸…ç©ºæ”¶é›†ç„å†…å®¹ï¼Œé‡æ”¾å†…å­˜"""
        self.collected_content.close()
        self.collected_content = io.StringIO()

    async def process_stream(self) -> AsyncGenerator[bytes, None]:
        """å¤„ç†æµå¼å“åº”ï¼Œæ£€æµ‹å¹¶å¤„ç†æˆªæ–­"""

        while self.current_attempt < self.max_attempts:
            self.current_attempt += 1

            # æ„å»ºå½“å‰è¯·æ±‚payload
            current_payload = self._build_current_payload()

            log.debug(f"Anti-truncation attempt {self.current_attempt}/{self.max_attempts}")

            # å‘é€è¯·æ±‚
            try:
                response = await self.original_request_func(current_payload)

                if not isinstance(response, StreamingResponse):
                    # éæµå¼å“åº”ï¼Œç›´æ¥å¤„ç†
                    yield await self._handle_non_streaming_response(response)
                    return

                # å¤„ç†æµå¼å“åº”ï¼ˆæŒ‰è¡Œå¤„ç†ï¼‰
                chunk_buffer = io.StringIO()  # ä½¿ç”¨ StringIO ç¼“å­˜å½“å‰è½®æ¬¡ç„chunk
                found_done_marker = False

                async for line in response.body_iterator:
                    if not line:
                        yield line
                        continue

                    # å¤„ç†ä¸æ¸¸ç”Ÿæˆå™¨ yield å‡º Response å¯¹è±¡ç„æƒ…å†µï¼ˆé”™è¯¯å“åº”ï¼‰
                    from fastapi import Response as FastAPIResponse
                    if isinstance(line, FastAPIResponse):
                        log.error(f"Anti-truncation: Received Response object from stream (status={line.status_code}), treating as error")
                        error_chunk = {
                            "error": {
                                "message": line.body.decode('utf-8', errors='ignore') if hasattr(line, 'body') and line.body else "Upstream error",
                                "type": "api_error",
                                "code": line.status_code,
                            }
                        }
                        yield f"data: {json.dumps(error_chunk)}\n\n".encode()
                        yield b"data: [DONE]\n\n"
                        return

                    # å¤„ç† bytes ç±»å‹ç„æµå¼æ•°æ®
                    if isinstance(line, bytes):
                        # è§£ç  bytes ä¸ºå­—ç¬¦ä¸²
                        line_str = line.decode('utf-8', errors='ignore').strip()
                    else:
                        line_str = str(line).strip()

                    # è·³è¿‡ç©ºè¡Œ
                    if not line_str:
                        yield line
                        continue

                    # å¤„ç† SSE æ ¼å¼ç„æ•°æ®è¡Œ
                    if line_str.startswith("data: "):
                        payload_str = line_str[6:]  # å»æ‰ "data: " å‰ç¼€

                        # æ£€æŸ¥æ˜¯å¦æ˜¯ [DONE] æ ‡è®°
                        if payload_str.strip() == "[DONE]":
                            if found_done_marker:
                                log.info("Anti-truncation: Found [done] marker, output complete")
                                yield line
                                # æ¸…ç†å†…å­˜
                                chunk_buffer.close()
                                self._clear_content()
                                return
                            else:
                                log.warning("Anti-truncation: Stream ended without [done] marker")
                                # ä¸å‘é€[DONE]ï¼Œå‡†å¤‡ç»§ç»­
                                break

                        # å°è¯•è§£æ JSON æ•°æ®
                        try:
                            data = json.loads(payload_str)
                            content = self._extract_content_from_chunk(data)

                            log.debug(f"Anti-truncation: Extracted content: {repr(content[:100] if content else '')}")

                            if content:
                                chunk_buffer.write(content)

                                # æ£€æŸ¥æ˜¯å¦åŒ…å«doneæ ‡è®°
                                has_marker = self._check_done_marker_in_chunk_content(content)
                                log.debug(f"Anti-truncation: Check done marker result: {has_marker}, DONE_MARKER='{DONE_MARKER}'")
                                if has_marker:
                                    found_done_marker = True
                                    log.debug(f"Anti-truncation: Found [done] marker in chunk, content: {content[:200]}")

                            # æ¸…ç†è¡Œä¸­ç„[done]æ ‡è®°åå†å‘é€
                            cleaned_line = self._remove_done_marker_from_line(line, line_str, data)
                            yield cleaned_line

                        except (json.JSONDecodeError, ValueError):
                            # æ— æ³•è§£æç„è¡Œï¼Œç›´æ¥ä¼ é€’
                            yield line
                            continue
                    else:
                        # é data: å¼€å¤´ç„è¡Œï¼Œç›´æ¥ä¼ é€’
                        yield line

                # æ›´æ–°æ”¶é›†ç„å†…å®¹ - ä½¿ç”¨ StringIO é«˜æ•ˆå¤„ç†
                chunk_text = chunk_buffer.getvalue()
                if chunk_text:
                    self._append_content(chunk_text)
                chunk_buffer.close()

                log.debug(f"Anti-truncation: After processing stream, found_done_marker={found_done_marker}")

                # å¦‚æœæ‰¾åˆ°äº†doneæ ‡è®°ï¼Œç»“æŸ
                if found_done_marker:
                    # ç«‹å³æ¸…ç†å†…å®¹é‡æ”¾å†…å­˜
                    self._clear_content()
                    yield b"data: [DONE]\n\n"
                    return

                # åªæœ‰åœ¨å•ä¸ªchunkä¸­æ²¡æœ‰æ‰¾åˆ°doneæ ‡è®°æ—¶ï¼Œæ‰æ£€æŸ¥ç´¯ç§¯å†…å®¹ï¼ˆé˜²æ­¢doneæ ‡è®°è·¨chunkå‡ºç°ï¼‰
                if not found_done_marker:
                    accumulated_text = self._get_collected_text()
                    if self._check_done_marker_in_text(accumulated_text):
                        log.info("Anti-truncation: Found [done] marker in accumulated content")
                        # ç«‹å³æ¸…ç†å†…å®¹é‡æ”¾å†…å­˜
                        self._clear_content()
                        yield b"data: [DONE]\n\n"
                        return

                # å¦‚æœæ²¡æ‰¾åˆ°doneæ ‡è®°ä¸”ä¸æ˜¯æœ€åä¸€æ¬¡å°è¯•ï¼Œå‡†å¤‡ç»­ä¼ 
                if self.current_attempt < self.max_attempts:
                    accumulated_text = self._get_collected_text()
                    total_length = len(accumulated_text)
                    log.info(
                        f"Anti-truncation: No [done] marker found in output (length: {total_length}), preparing continuation (attempt {self.current_attempt + 1})"
                    )
                    if total_length > 100:
                        log.debug(
                            f"Anti-truncation: Current collected content ends with: ...{accumulated_text[-100:]}"
                        )
                    # åœ¨ä¸‹ä¸€æ¬¡å¾ªç¯ä¸­ä¼ç»§ç»­
                    continue
                else:
                    # æœ€åä¸€æ¬¡å°è¯•ï¼Œç›´æ¥ç»“æŸ
                    log.warning("Anti-truncation: Max attempts reached, ending stream")
                    # ç«‹å³æ¸…ç†å†…å®¹é‡æ”¾å†…å­˜
                    self._clear_content()
                    yield b"data: [DONE]\n\n"
                    return

            except Exception as e:
                log.error(f"Anti-truncation error in attempt {self.current_attempt}: {str(e)}")
                if self.current_attempt >= self.max_attempts:
                    # å‘é€é”™è¯¯chunk
                    error_chunk = {
                        "error": {
                            "message": f"Anti-truncation failed: {str(e)}",
                            "type": "api_error",
                            "code": 500,
                        }
                    }
                    yield f"data: {json.dumps(error_chunk)}\n\n".encode()
                    yield b"data: [DONE]\n\n"
                    return
                # å¦åˆ™ç»§ç»­ä¸‹ä¸€æ¬¡å°è¯•

        # å¦‚æœæ‰€æœ‰å°è¯•éƒ½å¤±è´¥äº†
        log.error("Anti-truncation: All attempts failed")
        # æ¸…ç†å†…å­˜
        self._clear_content()
        yield b"data: [DONE]\n\n"

    def _build_current_payload(self) -> Dict[str, Any]:
        """æ„å»ºå½“å‰è¯·æ±‚ç„payload"""
        if self.current_attempt == 1:
            # ç¬¬ä¸€æ¬¡è¯·æ±‚ï¼Œä½¿ç”¨åŸå§‹payloadï¼ˆå·²ç»åŒ…å«åæˆªæ–­æŒ‡ä»¤ï¼‰
            return self.base_payload

        # åç»­è¯·æ±‚ï¼Œæ·»å ç»­ä¼ æŒ‡ä»¤
        continuation_payload = self.base_payload.copy()
        request_data = continuation_payload.get("request", {})

        # è·å–åŸå§‹å¯¹è¯å†…å®¹
        contents = request_data.get("contents", [])
        new_contents = contents.copy()

        # å¦‚æœæœ‰æ”¶é›†åˆ°ç„å†…å®¹ï¼Œæ·»å åˆ°å¯¹è¯ä¸­
        accumulated_text = self._get_collected_text()
        if accumulated_text:
            new_contents.append({"role": "model", "parts": [{"text": accumulated_text}]})

        # é¢„å¡«å……æ¨¡å¼ï¼ç›´æ¥ç”¨æ‹¼æ¥å†…å®¹ä½œä¸ºæœ«å°¾ model é¢„å¡«å……ï¼Œä¸å†å¢å  user ç»­å†™æŒ‡ä»¤
        if self.enable_prefill_mode:
            log.debug("Anti-truncation: Using prefill continuation mode (no user continuation prompt)")
            request_data["contents"] = new_contents
            continuation_payload["request"] = request_data
            return continuation_payload

        # æ„å»ºå…·ä½“ç„ç»­å†™æŒ‡ä»¤ï¼ŒåŒ…å«å‰é¢ç„å†…å®¹æ‘˜è¦
        content_summary = ""
        if accumulated_text:
            if len(accumulated_text) > 200:
                content_summary = f'\n\nå‰é¢ä½ å·²ç»è¾“å‡ºäº†çº¦ {len(accumulated_text)} ä¸ªå­—ç¬¦ç„å†…å®¹ï¼Œç»“å°¾æ˜¯ï¼\n"...{accumulated_text[-100:]}"'
            else:
                content_summary = f'\n\nå‰é¢ä½ å·²ç»è¾“å‡ºç„å†…å®¹æ˜¯ï¼\n"{accumulated_text}"'

        detailed_continuation_prompt = f"""{CONTINUATION_PROMPT}{content_summary}"""

        # æ·»å ç»§ç»­æŒ‡ä»¤
        continuation_message = {"role": "user", "parts": [{"text": detailed_continuation_prompt}]}
        new_contents.append(continuation_message)

        request_data["contents"] = new_contents
        continuation_payload["request"] = request_data

        return continuation_payload

    def _extract_content_from_chunk(self, data: Dict[str, Any]) -> str:
        """ä»chunkæ•°æ®ä¸­æå–æ–‡æœ¬å†…å®¹"""
        content = ""

        # å…ˆå°è¯•è§£åŒ… response å­—æ®µï¼ˆGemini API æ ¼å¼ï¼‰
        if "response" in data:
            data = data["response"]

        # å¤„ç† Gemini æ ¼å¼
        if "candidates" in data:
            for candidate in data["candidates"]:
                if "content" in candidate:
                    parts = candidate["content"].get("parts", [])
                    for part in parts:
                        if "text" in part:
                            content += part["text"]
        
        # å¤„ç† OpenAI æµå¼æ ¼å¼ï¼ˆchoices/deltaï¼‰
        elif "choices" in data:
            for choice in data["choices"]:
                if "delta" in choice and "content" in choice["delta"]:
                    delta_content = choice["delta"]["content"]
                    if delta_content:
                        content += delta_content

        return content

    async def _handle_non_streaming_response(self, response) -> bytes:
        """å¤„ç†éæµå¼å“åº” - ä½¿ç”¨å¾ªç¯ä»£æ›¿é€’å½’é¿å…æ ˆæº¢å‡º"""
        # ä½¿ç”¨å¾ªç¯ä»£æ›¿é€’å½’
        while True:
            try:
                # ç‰¹æ®å¤„ç†ï¼å¦‚æœè¿”å›ç„æ˜¯StreamingResponseï¼Œéœ€è¦è¯»å–å…¶body_iterator
                if isinstance(response, StreamingResponse):
                    log.error("Anti-truncation: Received StreamingResponse in non-streaming handler - this should not happen")
                    # å°è¯•è¯»å–æµå¼å“åº”ç„å†…å®¹
                    chunks = []
                    async for chunk in response.body_iterator:
                        chunks.append(chunk)
                    content = b"".join(chunks).decode() if chunks else ""
                # æå–å“åº”å†…å®¹
                elif hasattr(response, "body"):
                    content = (
                        response.body.decode() if isinstance(response.body, bytes) else response.body
                    )
                elif hasattr(response, "content"):
                    content = (
                        response.content.decode()
                        if isinstance(response.content, bytes)
                        else response.content
                    )
                else:
                    log.error(f"Anti-truncation: Unknown response type: {type(response)}")
                    content = str(response)

                # éªŒè¯å†…å®¹ä¸ä¸ºç©º
                if not content or not content.strip():
                    log.error("Anti-truncation: Received empty response content")
                    return json.dumps(
                        {
                            "error": {
                                "message": "Empty response from server",
                                "type": "api_error",
                                "code": 500,
                            }
                        }
                    ).encode()

                # å°è¯•è§£æ JSON
                try:
                    response_data = json.loads(content)
                except json.JSONDecodeError as json_err:
                    log.error(f"Anti-truncation: Failed to parse JSON response: {json_err}, content: {content[:200]}")
                    # å¦‚æœä¸æ˜¯ JSONï¼Œç›´æ¥è¿”å›åŸå§‹å†…å®¹
                    return content.encode() if isinstance(content, str) else content

                # æ£€æŸ¥æ˜¯å¦åŒ…å«doneæ ‡è®°
                text_content = self._extract_content_from_response(response_data)
                has_done_marker = self._check_done_marker_in_text(text_content)

                if has_done_marker or self.current_attempt >= self.max_attempts:
                    # æ‰¾åˆ°doneæ ‡è®°æˆ–è¾¾åˆ°æœ€å¤§å°è¯•æ¬¡æ•°ï¼Œè¿”å›ç»“æœ
                    return content.encode() if isinstance(content, str) else content

                # éœ€è¦ç»§ç»­ï¼Œæ”¶é›†å†…å®¹å¹¶æ„å»ºä¸‹ä¸€ä¸ªè¯·æ±‚
                if text_content:
                    self._append_content(text_content)

                log.info("Anti-truncation: Non-streaming response needs continuation")

                # å¢å å°è¯•æ¬¡æ•°
                self.current_attempt += 1

                # æ„å»ºç»­ä¼ payloadå¹¶å‘é€ä¸‹ä¸€ä¸ªè¯·æ±‚
                next_payload = self._build_current_payload()
                response = await self.original_request_func(next_payload)

                # ç»§ç»­å¾ªç¯å¤„ç†ä¸‹ä¸€ä¸ªå“åº”

            except Exception as e:
                log.error(f"Anti-truncation non-streaming error: {str(e)}")
                return json.dumps(
                    {
                        "error": {
                            "message": f"Anti-truncation failed: {str(e)}",
                            "type": "api_error",
                            "code": 500,
                        }
                    }
                ).encode()

    def _check_done_marker_in_text(self, text: str) -> bool:
        """æ£€æµ‹æ–‡æœ¬ä¸­æ˜¯å¦åŒ…å«DONE_MARKERï¼ˆåªæ£€æµ‹æŒ‡å®æ ‡è®°ï¼‰"""
        if not text:
            return False

        # åªè¦æ–‡æœ¬ä¸­å‡ºç°DONE_MARKERå³å¯
        return DONE_MARKER in text

    def _check_done_marker_in_chunk_content(self, content: str) -> bool:
        """æ£€æŸ¥å•ä¸ªchunkå†…å®¹ä¸­æ˜¯å¦åŒ…å«doneæ ‡è®°"""
        return self._check_done_marker_in_text(content)

    def _extract_content_from_response(self, data: Dict[str, Any]) -> str:
        """ä»å“åº”æ•°æ®ä¸­æå–æ–‡æœ¬å†…å®¹"""
        content = ""

        # å…ˆå°è¯•è§£åŒ… response å­—æ®µï¼ˆGemini API æ ¼å¼ï¼‰
        if "response" in data:
            data = data["response"]

        # å¤„ç†Geminiæ ¼å¼
        if "candidates" in data:
            for candidate in data["candidates"]:
                if "content" in candidate:
                    parts = candidate["content"].get("parts", [])
                    for part in parts:
                        if "text" in part:
                            content += part["text"]

        # å¤„ç†OpenAIæ ¼å¼
        elif "choices" in data:
            for choice in data["choices"]:
                if "message" in choice and "content" in choice["message"]:
                    content += choice["message"]["content"]

        return content

    def _remove_done_marker_from_line(self, line: bytes, line_str: str, data: Dict[str, Any]) -> bytes:
        """ä»è¡Œä¸­ç§»é™¤[done]æ ‡è®°"""
        try:
            # é¦–å…ˆæ£€æŸ¥æ˜¯å¦çœŸç„åŒ…å«[done]æ ‡è®°
            if "[done]" not in line_str.lower():
                return line  # æ²¡æœ‰[done]æ ‡è®°ï¼Œç›´æ¥è¿”å›åŸå§‹è¡Œ

            log.info(f"Anti-truncation: Attempting to remove [done] marker from line")
            log.debug(f"Anti-truncation: Original line (first 200 chars): {line_str[:200]}")

            # ç¼–è¯‘æ­£åˆ™è¡¨è¾¾å¼ï¼ŒåŒ¹é…[done]æ ‡è®°ï¼ˆå¿½ç•¥å¤§å°å†™ï¼ŒåŒ…æ‹¬å¯èƒ½ç„ç©ºç™½å­—ç¬¦ï¼‰
            done_pattern = re.compile(r"\s*\[done\]\s*", re.IGNORECASE)

            # æ£€æŸ¥æ˜¯å¦æœ‰ response åŒ…è£¹å±‚
            has_response_wrapper = "response" in data
            log.debug(f"Anti-truncation: has_response_wrapper={has_response_wrapper}, data keys={list(data.keys())}")
            if has_response_wrapper:
                # éœ€è¦ä¿ç•™å¤–å±‚ç„ response å­—æ®µ
                inner_data = data["response"]
            else:
                inner_data = data
            
            log.debug(f"Anti-truncation: inner_data keys={list(inner_data.keys())}")

            log.debug(f"Anti-truncation: inner_data keys={list(inner_data.keys())}")

            # å¤„ç†Geminiæ ¼å¼
            if "candidates" in inner_data:
                log.info(f"Anti-truncation: Processing Gemini format to remove [done] marker")
                modified_inner = inner_data.copy()
                modified_inner["candidates"] = []

                for i, candidate in enumerate(inner_data["candidates"]):
                    modified_candidate = candidate.copy()
                    # åªåœ¨æœ€åä¸€ä¸ªcandidateä¸­æ¸…ç†[done]æ ‡è®°
                    is_last_candidate = i == len(inner_data["candidates"]) - 1

                    if "content" in candidate:
                        modified_content = candidate["content"].copy()
                        if "parts" in modified_content:
                            modified_parts = []
                            for part in modified_content["parts"]:
                                if "text" in part and isinstance(part["text"], str):
                                    modified_part = part.copy()
                                    original_text = part["text"]
                                    # åªåœ¨æœ€åä¸€ä¸ªcandidateä¸­æ¸…ç†[done]æ ‡è®°
                                    if is_last_candidate:
                                        modified_part["text"] = done_pattern.sub("", part["text"])
                                        if "[done]" in original_text.lower():
                                            log.debug(f"Anti-truncation: Removed [done] from text: '{original_text[:100]}' -> '{modified_part['text'][:100]}'")
                                    modified_parts.append(modified_part)
                                else:
                                    modified_parts.append(part)
                            modified_content["parts"] = modified_parts
                        modified_candidate["content"] = modified_content
                    modified_inner["candidates"].append(modified_candidate)

                # å¦‚æœæœ‰ response åŒ…è£¹å±‚ï¼Œéœ€è¦é‡æ–°åŒ…è£…
                if has_response_wrapper:
                    modified_data = data.copy()
                    modified_data["response"] = modified_inner
                else:
                    modified_data = modified_inner

                # é‡æ–°ç¼–ç ä¸ºè¡Œæ ¼å¼ - SSEæ ¼å¼éœ€è¦ä¸¤ä¸ªæ¢è¡Œç¬¦
                json_str = json.dumps(modified_data, separators=(",", ":"), ensure_ascii=False)
                result = f"data: {json_str}\n\n".encode("utf-8")
                log.debug(f"Anti-truncation: Modified line (first 200 chars): {result.decode('utf-8', errors='ignore')[:200]}")
                return result

            # å¤„ç†OpenAIæ ¼å¼
            elif "choices" in inner_data:
                modified_inner = inner_data.copy()
                modified_inner["choices"] = []

                for choice in inner_data["choices"]:
                    modified_choice = choice.copy()
                    if "delta" in choice and "content" in choice["delta"]:
                        modified_delta = choice["delta"].copy()
                        modified_delta["content"] = done_pattern.sub("", choice["delta"]["content"])
                        modified_choice["delta"] = modified_delta
                    elif "message" in choice and "content" in choice["message"]:
                        modified_message = choice["message"].copy()
                        modified_message["content"] = done_pattern.sub("", choice["message"]["content"])
                        modified_choice["message"] = modified_message
                    modified_inner["choices"].append(modified_choice)

                # å¦‚æœæœ‰ response åŒ…è£¹å±‚ï¼Œéœ€è¦é‡æ–°åŒ…è£…
                if has_response_wrapper:
                    modified_data = data.copy()
                    modified_data["response"] = modified_inner
                else:
                    modified_data = modified_inner

                # é‡æ–°ç¼–ç ä¸ºè¡Œæ ¼å¼ - SSEæ ¼å¼éœ€è¦ä¸¤ä¸ªæ¢è¡Œç¬¦
                json_str = json.dumps(modified_data, separators=(",", ":"), ensure_ascii=False)
                return f"data: {json_str}\n\n".encode("utf-8")

            # å¦‚æœæ²¡æœ‰æ‰¾åˆ°æ”¯æŒç„æ ¼å¼ï¼Œè¿”å›åŸå§‹è¡Œ
            return line

        except Exception as e:
            log.warning(f"Failed to remove [done] marker from line: {str(e)}")
            return line


async def apply_anti_truncation_to_stream(
    request_func,
    payload: Dict[str, Any],
    max_attempts: int = 3,
    enable_prefill_mode: bool = False,
) -> StreamingResponse:
    """
    å¯¹æµå¼è¯·æ±‚åº”ç”¨åæˆªæ–­å¤„ç†

    Args:
        request_func: åŸå§‹è¯·æ±‚å‡½æ•°
        payload: è¯·æ±‚payload
        max_attempts: æœ€å¤§ç»­ä¼ å°è¯•æ¬¡æ•°
        enable_prefill_mode: æ˜¯å¦å¯ç”¨é¢„å¡«å……æ¨¡å¼ă€‚å¯ç”¨åç»­ä¼ è¯·æ±‚ä¸å†æ·»å  user ç»­å†™æŒ‡ä»¤ï¼Œ
            è€Œæ˜¯å°†å·²æ”¶é›†å†…å®¹ä½œä¸ºæœ«å°¾ model å†…å®¹è¿›è¡Œé¢„å¡«å……

    Returns:
        å¤„ç†åç„StreamingResponse
    """

    # é¦–å…ˆå¯¹payloadåº”ç”¨åæˆªæ–­æŒ‡ä»¤
    anti_truncation_payload = apply_anti_truncation(payload)

    # åˆ›å»ºåæˆªæ–­å¤„ç†å™¨
    processor = AntiTruncationStreamProcessor(
        lambda p: request_func(p),
        anti_truncation_payload,
        max_attempts,
        enable_prefill_mode,
    )

    # è¿”å›åŒ…è£…åç„æµå¼å“åº”
    return StreamingResponse(processor.process_stream(), media_type="text/event-stream")


def is_anti_truncation_enabled(request_data: Dict[str, Any]) -> bool:
    """
    æ£€æŸ¥è¯·æ±‚æ˜¯å¦å¯ç”¨äº†åæˆªæ–­åŸèƒ½

    Args:
        request_data: è¯·æ±‚æ•°æ®

    Returns:
        æ˜¯å¦å¯ç”¨åæˆªæ–­
    """
    return request_data.get("enable_anti_truncation", False)