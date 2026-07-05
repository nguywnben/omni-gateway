"""
Anthropic åˆ° Gemini æ ¼å¼è½¬æ¢å™¨

æä¾›è¯·æ±‚ä½“ă€å“åº”å’Œæµå¼è½¬æ¢ç„å®Œæ•´åŸèƒ½ă€‚
"""
from __future__ import annotations

import json
import os
import uuid
from typing import Any, AsyncIterator, Dict, List, Optional

from fastapi import Response
from log import log
from omni_gateway.converter.utils import merge_system_messages

from omni_gateway.converter.thoughtSignature_fix import (
    decode_tool_id_and_signature,
    is_internal_placeholder_text,
    is_skip_thought_signature_placeholder,
    SKIP_THOUGHT_SIGNATURE_VALIDATOR,
)

DEFAULT_TEMPERATURE = 0.4
_DEBUG_TRUE = {"1", "true", "yes", "on"}

# ============================================================================
# Thinking å—éªŒè¯å’Œæ¸…ç†
# ============================================================================

# æœ€å°æœ‰æ•ˆç­¾åé•¿åº¦
MIN_SIGNATURE_LENGTH = 10


def has_valid_thoughtsignature(block: Dict[str, Any]) -> bool:
    """
    æ£€æŸ¥ thinking å—æ˜¯å¦æœ‰æœ‰æ•ˆç­¾å
    
    Args:
        block: content block å­—å…¸
        
    Returns:
        bool: æ˜¯å¦æœ‰æœ‰æ•ˆç­¾å
    """
    if not isinstance(block, dict):
        return True
    
    block_type = block.get("type")
    if block_type not in ("thinking", "redacted_thinking"):
        return True  # é thinking å—é»˜è®¤æœ‰æ•ˆ
    
    thinking = block.get("thinking", "")
    thoughtsignature = block.get("thoughtSignature")
    
    # ç©º thinking + ä»»æ„ thoughtsignature = æœ‰æ•ˆ (trailing signature case)
    if not thinking and thoughtsignature is not None:
        return True
    
    # æœ‰å†…å®¹ + è¶³å¤Ÿé•¿åº¦ç„ thoughtsignature = æœ‰æ•ˆ
    if thoughtsignature and isinstance(thoughtsignature, str) and len(thoughtsignature) >= MIN_SIGNATURE_LENGTH:
        return True
    
    return False


def sanitize_thinking_block(block: Dict[str, Any]) -> Dict[str, Any]:
    """
    æ¸…ç† thinking å—,åªä¿ç•™å¿…è¦å­—æ®µ(ç§»é™¤ cache_control ç­‰)
    
    Args:
        block: content block å­—å…¸
        
    Returns:
        æ¸…ç†åç„ block å­—å…¸
    """
    if not isinstance(block, dict):
        return block
    
    block_type = block.get("type")
    if block_type not in ("thinking", "redacted_thinking"):
        return block
    
    # é‡å»ºå—,ç§»é™¤é¢å¤–å­—æ®µ
    sanitized: Dict[str, Any] = {
        "type": block_type,
        "thinking": block.get("thinking", "")
    }
    
    thoughtsignature = block.get("thoughtSignature")
    if thoughtsignature:
        sanitized["thoughtSignature"] = thoughtsignature
    
    return sanitized


def remove_trailing_unsigned_thinking(blocks: List[Dict[str, Any]]) -> None:
    """
    ç§»é™¤å°¾éƒ¨ç„æ— ç­¾å thinking å—
    
    Args:
        blocks: content blocks åˆ—è¡¨ (ä¼è¢«ä¿®æ”¹)
    """
    if not blocks:
        return
    
    # ä»åå‘å‰æ‰«æ
    end_index = len(blocks)
    for i in range(len(blocks) - 1, -1, -1):
        block = blocks[i]
        if not isinstance(block, dict):
            break
        
        block_type = block.get("type")
        if block_type in ("thinking", "redacted_thinking"):
            if not has_valid_thoughtsignature(block):
                end_index = i
            else:
                break  # é‡åˆ°æœ‰æ•ˆç­¾åç„ thinking å—,åœæ­¢
        else:
            break  # é‡åˆ°é thinking å—,åœæ­¢
    
    if end_index < len(blocks):
        removed = len(blocks) - end_index
        del blocks[end_index:]
        log.debug(f"Removed {removed} trailing unsigned thinking block(s)")


def filter_invalid_thinking_blocks(messages: List[Dict[str, Any]]) -> None:
    """
    è¿‡æ»¤æ¶ˆæ¯ä¸­ç„æ— æ•ˆ thinking å—ï¼Œå¹¶æ¸…ç†æ‰€æœ‰ thinking å—ç„é¢å¤–å­—æ®µï¼ˆå¦‚ cache_controlï¼‰

    Args:
        messages: Anthropic messages åˆ—è¡¨ (ä¼è¢«ä¿®æ”¹)
    """
    total_filtered = 0

    for msg in messages:
        # åªå¤„ç† assistant å’Œ model æ¶ˆæ¯
        role = msg.get("role", "")
        if role not in ("assistant", "model"):
            continue

        content = msg.get("content")
        if not isinstance(content, list):
            continue

        original_len = len(content)
        new_blocks: List[Dict[str, Any]] = []

        for block in content:
            if not isinstance(block, dict):
                new_blocks.append(block)
                continue

            block_type = block.get("type")
            if block_type not in ("thinking", "redacted_thinking"):
                new_blocks.append(block)
                continue

            # æ‰€æœ‰ thinking å—éƒ½éœ€è¦æ¸…ç†ï¼ˆç§»é™¤ cache_control ç­‰é¢å¤–å­—æ®µï¼‰
            # æ£€æŸ¥ thinking å—ç„æœ‰æ•ˆæ€§
            if has_valid_thoughtsignature(block):
                # æœ‰æ•ˆç­¾åï¼Œæ¸…ç†åä¿ç•™
                new_blocks.append(sanitize_thinking_block(block))
            else:
                # æ— æ•ˆç­¾åï¼Œå°†å†…å®¹è½¬æ¢ä¸º text å—
                thinking_text = block.get("thinking", "")
                if thinking_text and str(thinking_text).strip():
                    log.info(
                        f"[Claude-Handler] Converting thinking block with invalid thoughtSignature to text. "
                        f"Content length: {len(thinking_text)} chars"
                    )
                    new_blocks.append({"type": "text", "text": thinking_text})
                else:
                    log.debug("[Claude-Handler] Dropping empty thinking block with invalid thoughtSignature")

        msg["content"] = new_blocks
        filtered_count = original_len - len(new_blocks)
        total_filtered += filtered_count

        # å¦‚æœè¿‡æ»¤åä¸ºç©º,æ·»å ä¸€ä¸ªç©ºæ–‡æœ¬å—ä»¥ä¿æŒæ¶ˆæ¯æœ‰æ•ˆ
        if not new_blocks:
            msg["content"] = [{"type": "text", "text": ""}]

    if total_filtered > 0:
        log.debug(f"Filtered {total_filtered} invalid thinking block(s) from history")


# ============================================================================
# è¯·æ±‚éªŒè¯å’Œæå–
# ============================================================================


def _anthropic_debug_enabled() -> bool:
    """æ£€æŸ¥æ˜¯å¦å¯ç”¨ Anthropic è°ƒè¯•æ¨¡å¼"""
    return str(os.getenv("OGW_ANTHROPIC_DEBUG", "true")).strip().lower() in _DEBUG_TRUE


def _cached_content_token_count(usage_metadata: Any) -> int:
    if not isinstance(usage_metadata, dict):
        return 0
    return int(usage_metadata.get("cachedContentTokenCount", 0) or 0)


def _anthropic_usage_from_metadata(usage_metadata: Any) -> Dict[str, int]:
    if not isinstance(usage_metadata, dict):
        return {"input_tokens": 0, "output_tokens": 0}

    prompt_tokens_total = int(usage_metadata.get("promptTokenCount", 0) or 0)
    cached_tokens = _cached_content_token_count(usage_metadata)
    usage = {
        "input_tokens": max(prompt_tokens_total - cached_tokens, 0),
        "output_tokens": int(usage_metadata.get("candidatesTokenCount", 0) or 0),
    }

    if cached_tokens > 0:
        usage["cache_read_input_tokens"] = cached_tokens

    return usage


def _is_non_whitespace_text(value: Any) -> bool:
    """
    åˆ¤æ–­æ–‡æœ¬æ˜¯å¦åŒ…å«"éç©ºç™½"å†…å®¹ă€‚

    è¯´æ˜ï¼ä¸‹æ¸¸ï¼ˆOmni/Claude å…¼å®¹å±‚ï¼‰ä¼å¯¹çº¯ text å†…å®¹å—åæ ¡éªŒï¼
    - text ä¸èƒ½ä¸ºç©ºå­—ç¬¦ä¸²
    - text ä¸èƒ½ä»…ç”±ç©ºç™½å­—ç¬¦ï¼ˆç©ºæ ¼/æ¢è¡Œ/åˆ¶è¡¨ç­‰ï¼‰ç»„æˆ
    """
    if value is None:
        return False
    try:
        return bool(str(value).strip())
    except Exception:
        return False


def _remove_nulls_for_tool_input(value: Any) -> Any:
    """
    é€’å½’ç§»é™¤ dict/list ä¸­å€¼ä¸º null/None ç„å­—æ®µ/å…ƒç´ ă€‚

    èƒŒæ™¯ï¼Roo/Kilo åœ¨ Anthropic native tool è·¯å¾„ä¸‹ï¼Œè‹¥æ”¶åˆ° tool_use.input ä¸­åŒ…å« nullï¼Œ
    å¯èƒ½ä¼æ null å½“ä½œçœŸå®å…¥å‚æ‰§è¡Œï¼ˆä¾‹å¦‚"åœ¨ null ä¸­æœç´¢"ï¼‰ă€‚
    """
    if isinstance(value, dict):
        cleaned: Dict[str, Any] = {}
        for k, v in value.items():
            if v is None:
                continue
            cleaned[k] = _remove_nulls_for_tool_input(v)
        return cleaned

    if isinstance(value, list):
        cleaned_list = []
        for item in value:
            if item is None:
                continue
            cleaned_list.append(_remove_nulls_for_tool_input(item))
        return cleaned_list

    return value

# ============================================================================
# 2. JSON Schema æ¸…ç†
# ============================================================================

def clean_json_schema(schema: Any) -> Any:
    """
    æ¸…ç† JSON Schemaï¼Œç§»é™¤ä¸‹æ¸¸ä¸æ”¯æŒç„å­—æ®µï¼Œå¹¶æéªŒè¯è¦æ±‚è¿½å åˆ° descriptionă€‚
    """
    if not isinstance(schema, dict):
        return schema

    # ä¸‹æ¸¸ä¸æ”¯æŒç„å­—æ®µ
    unsupported_keys = {
        "$schema", "$id", "$ref", "$defs", "definitions", "title",
        "example", "examples", "readOnly", "writeOnly", "default",
        "exclusiveMaximum", "exclusiveMinimum", "oneOf", "anyOf", "allOf",
        "const", "additionalItems", "contains", "patternProperties",
        "dependencies", "propertyNames", "if", "then", "else",
        "contentEncoding", "contentMediaType", "nullable",
    }

    validation_fields = {
        "minLength": "minLength",
        "maxLength": "maxLength",
        "minimum": "minimum",
        "maximum": "maximum",
        "minItems": "minItems",
        "maxItems": "maxItems",
    }
    fields_to_remove = {"additionalProperties"}

    validations: List[str] = []
    for field, label in validation_fields.items():
        if field in schema:
            validations.append(f"{label}: {schema[field]}")

    cleaned: Dict[str, Any] = {}
    for key, value in schema.items():
        if key in unsupported_keys or key in fields_to_remove or key in validation_fields:
            continue

        if key == "type" and isinstance(value, list):
            # type: ["string", "null"] -> type: "string", nullable: true
            has_null = any(
                isinstance(t, str) and t.strip() and t.strip().lower() == "null" for t in value
            )
            non_null_types = [
                t.strip()
                for t in value
                if isinstance(t, str) and t.strip() and t.strip().lower() != "null"
            ]

            cleaned[key] = non_null_types[0] if non_null_types else "string"
            continue

        if key == "description" and validations:
            cleaned[key] = f"{value} ({', '.join(validations)})"
        elif isinstance(value, dict):
            cleaned[key] = clean_json_schema(value)
        elif isinstance(value, list):
            cleaned[key] = [clean_json_schema(item) if isinstance(item, dict) else item for item in value]
        else:
            cleaned[key] = value

    if validations and "description" not in cleaned:
        cleaned["description"] = f"Validation: {', '.join(validations)}"

    # å¦‚æœæœ‰ properties ä½†æ²¡æœ‰æ˜¾å¼ typeï¼Œåˆ™è¡¥é½ä¸º object
    if "properties" in cleaned and "type" not in cleaned:
        cleaned["type"] = "object"

    if (
        isinstance(schema.get("properties"), dict)
        and isinstance(cleaned.get("required"), list)
    ):
        nullable_fields = {
            name
            for name, prop in schema["properties"].items()
            if isinstance(prop, dict)
            and isinstance(prop.get("type"), list)
            and any(str(t).lower() == "null" for t in prop["type"])
        }
        if nullable_fields:
            cleaned["required"] = [
                item for item in cleaned["required"]
                if item not in nullable_fields
            ]
            if not cleaned["required"]:
                cleaned.pop("required", None)

    return cleaned


# ============================================================================
# 4. Tools è½¬æ¢
# ============================================================================

def convert_tools(anthropic_tools: Optional[List[Dict[str, Any]]]) -> Optional[List[Dict[str, Any]]]:
    """
    å°† Anthropic tools[] è½¬æ¢ä¸ºä¸‹æ¸¸ toolsï¼ˆfunctionDeclarationsï¼‰ç»“æ„ă€‚
    """
    if not anthropic_tools:
        return None

    gemini_tools: List[Dict[str, Any]] = []
    for tool in anthropic_tools:
        name = tool.get("name", "nameless_function")
        description = tool.get("description", "")
        input_schema = tool.get("input_schema", {}) or {}
        parameters = clean_json_schema(input_schema)

        gemini_tools.append(
            {
                "functionDeclarations": [
                    {
                        "name": name,
                        "description": description,
                        "parametersJsonSchema": parameters,
                    }
                ]
            }
        )

    return gemini_tools or None


# ============================================================================
# 5. Messages è½¬æ¢
# ============================================================================

def _extract_tool_result_output(content: Any) -> str:
    """ä» tool_result.content ä¸­æå–è¾“å‡ºå­—ç¬¦ä¸²"""
    if isinstance(content, list):
        if not content:
            return ""
        first = content[0]
        if isinstance(first, dict) and first.get("type") == "text":
            return str(first.get("text", ""))
        return str(first)
    if content is None:
        return ""
    return str(content)


def convert_messages_to_contents(
    messages: List[Dict[str, Any]],
    *,
    include_thinking: bool = True
) -> List[Dict[str, Any]]:
    """
    å°† Anthropic messages[] è½¬æ¢ä¸ºä¸‹æ¸¸ contents[]ï¼ˆrole: user/model, parts: []ï¼‰ă€‚

    Args:
        messages: Anthropic æ ¼å¼ç„æ¶ˆæ¯åˆ—è¡¨
        include_thinking: æ˜¯å¦åŒ…å« thinking å—
    """
    contents: List[Dict[str, Any]] = []

    # ç¬¬ä¸€éï¼æ„å»º tool_use_id -> (name, thoughtsignature) ç„æ˜ å°„
    # æ³¨æ„ï¼å­˜å‚¨ç„æ˜¯ç¼–ç åç„ IDï¼ˆå¯èƒ½åŒ…å«ç­¾åï¼‰
    tool_use_info: Dict[str, tuple[str, Optional[str]]] = {}
    for msg in messages:
        raw_content = msg.get("content", "")
        if isinstance(raw_content, list):
            for item in raw_content:
                if isinstance(item, dict) and item.get("type") == "tool_use":
                    encoded_tool_id = item.get("id")
                    tool_name = item.get("name")
                    if encoded_tool_id and tool_name:
                        # è§£ç è·å–åŸå§‹IDå’Œç­¾å
                        original_id, thoughtsignature = decode_tool_id_and_signature(encoded_tool_id)
                        # å­˜å‚¨æ˜ å°„ï¼ç¼–ç ID -> (name, thoughtsignature)
                        tool_use_info[str(encoded_tool_id)] = (tool_name, thoughtsignature)

    for msg in messages:
        role = msg.get("role", "user")
        
        # system æ¶ˆæ¯å·²ç»ç”± merge_system_messages å¤„ç†ï¼Œè¿™é‡Œè·³è¿‡
        if role == "system":
            continue
        
        # æ”¯æŒ 'assistant' å’Œ 'model' è§’è‰²ï¼ˆGoogle history usageï¼‰
        gemini_role = "model" if role in ("assistant", "model") else "user"
        raw_content = msg.get("content", "")

        parts: List[Dict[str, Any]] = []
        if isinstance(raw_content, str):
            if _is_non_whitespace_text(raw_content):
                parts = [{"text": str(raw_content)}]
        elif isinstance(raw_content, list):
            for item in raw_content:
                if not isinstance(item, dict):
                    if _is_non_whitespace_text(item):
                        parts.append({"text": str(item)})
                    continue

                item_type = item.get("type")
                if item_type == "thinking":
                    # ä¸æå®¢æˆ·ç«¯å›ä¼ ç„ thinking signature å†é€ç»™ Googleă€‚
                    # è¿™äº›ç­¾åå¾ˆå®¹æ˜“åœ¨ä¸­è½¬/æ¢å·/è£å‰ªåå˜æˆ Corrupted thought signatureă€‚
                    continue
                elif item_type == "redacted_thinking":
                    continue
                elif item_type == "text":
                    text = item.get("text", "")
                    if _is_non_whitespace_text(text):
                        parts.append({"text": str(text)})
                elif item_type == "image":
                    source = item.get("source", {}) or {}
                    if source.get("type") == "base64":
                        parts.append(
                            {
                                "inlineData": {
                                    "mimeType": source.get("media_type", "image/png"),
                                    "data": source.get("data", ""),
                                }
                            }
                        )
                elif item_type == "tool_use":
                    encoded_id = item.get("id") or ""
                    original_id, _ = decode_tool_id_and_signature(encoded_id)

                    fc_part: Dict[str, Any] = {
                        "functionCall": {
                            "id": original_id,  # ä½¿ç”¨åŸå§‹IDï¼Œä¸å¸¦ç­¾å
                            "name": item.get("name"),
                            "args": item.get("input", {}) or {},
                        }
                    }

                    fc_part["thoughtSignature"] = SKIP_THOUGHT_SIGNATURE_VALIDATOR

                    parts.append(fc_part)
                elif item_type == "tool_result":
                    output = _extract_tool_result_output(item.get("content"))
                    encoded_tool_use_id = item.get("tool_use_id") or ""
                    
                    # è§£ç è·å–åŸå§‹IDï¼ˆfunctionResponseä¸éœ€è¦ç­¾åï¼‰
                    original_tool_use_id, _ = decode_tool_id_and_signature(encoded_tool_use_id)

                    # ä» tool_result è·å– nameï¼Œå¦‚æœæ²¡æœ‰åˆ™ä»æ˜ å°„ä¸­æŸ¥æ‰¾
                    func_name = item.get("name")
                    if not func_name and encoded_tool_use_id:
                        # ä½¿ç”¨ç¼–ç IDæŸ¥æ‰¾æ˜ å°„
                        tool_info = tool_use_info.get(str(encoded_tool_use_id))
                        if tool_info:
                            func_name = tool_info[0]  # è·å– name
                    if not func_name:
                        func_name = "unknown_function"
                    
                    parts.append(
                        {
                            "functionResponse": {
                                "id": original_tool_use_id,  # ä½¿ç”¨è§£ç åç„åŸå§‹IDä»¥åŒ¹é…functionCall
                                "name": func_name,
                                "response": {"output": output},
                            }
                        }
                    )
                else:
                    parts.append({"text": json.dumps(item, ensure_ascii=False)})
        else:
            if _is_non_whitespace_text(raw_content):
                parts = [{"text": str(raw_content)}]

        if not parts:
            continue

        contents.append({"role": gemini_role, "parts": parts})

    return contents


def reorganize_tool_messages(contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    é‡æ–°ç»„ç»‡æ¶ˆæ¯ï¼Œæ»¡è¶³ tool_use/tool_result çº¦æŸă€‚
    """
    tool_results: Dict[str, Dict[str, Any]] = {}

    for msg in contents:
        for part in msg.get("parts", []) or []:
            if isinstance(part, dict) and "functionResponse" in part:
                tool_id = (part.get("functionResponse") or {}).get("id")
                if tool_id:
                    tool_results[str(tool_id)] = part

    flattened: List[Dict[str, Any]] = []
    for msg in contents:
        role = msg.get("role")
        for part in msg.get("parts", []) or []:
            flattened.append({"role": role, "parts": [part]})

    new_contents: List[Dict[str, Any]] = []
    i = 0
    while i < len(flattened):
        msg = flattened[i]
        part = msg["parts"][0]

        if isinstance(part, dict) and "functionResponse" in part:
            i += 1
            continue

        if isinstance(part, dict) and "functionCall" in part:
            tool_id = (part.get("functionCall") or {}).get("id")
            new_contents.append({"role": "model", "parts": [part]})

            if tool_id is not None and str(tool_id) in tool_results:
                new_contents.append({"role": "user", "parts": [tool_results[str(tool_id)]]})

            i += 1
            continue

        new_contents.append(msg)
        i += 1

    return new_contents


# ============================================================================
# 7. Tool Choice è½¬æ¢
# ============================================================================

def convert_tool_choice_to_tool_config(tool_choice: Any) -> Optional[Dict[str, Any]]:
    """
    å°† Anthropic tool_choice è½¬æ¢ä¸º Gemini toolConfig

    Args:
        tool_choice: Anthropic æ ¼å¼ç„ tool_choice
            - {"type": "auto"}: æ¨¡å‹è‡ªå¨å†³å®æ˜¯å¦ä½¿ç”¨å·¥å…·
            - {"type": "any"}: æ¨¡å‹å¿…é¡»ä½¿ç”¨å·¥å…·
            - {"type": "tool", "name": "tool_name"}: æ¨¡å‹å¿…é¡»ä½¿ç”¨æŒ‡å®å·¥å…·

    Returns:
        Gemini æ ¼å¼ç„ toolConfigï¼Œå¦‚æœæ— æ•ˆåˆ™è¿”å› None
    """
    if not tool_choice:
        return None
    
    if isinstance(tool_choice, dict):
        choice_type = tool_choice.get("type")
        
        if choice_type == "auto":
            return {"functionCallingConfig": {"mode": "AUTO"}}
        elif choice_type == "any":
            return {"functionCallingConfig": {"mode": "ANY"}}
        elif choice_type == "tool":
            tool_name = tool_choice.get("name")
            if tool_name:
                return {
                    "functionCallingConfig": {
                        "mode": "ANY",
                        "allowedFunctionNames": [tool_name],
                    }
                }
    
    # æ— æ•ˆæˆ–ä¸æ”¯æŒç„ tool_choiceï¼Œè¿”å› None
    return None


# ============================================================================
# 8. Generation Config æ„å»º
# ============================================================================

def build_generation_config(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    æ ¹æ® Anthropic Messages è¯·æ±‚æ„é€ ä¸‹æ¸¸ generationConfigă€‚

    Returns:
        generation_config: ç”Ÿæˆé…ç½®å­—å…¸
    """
    config: Dict[str, Any] = {
        "topP": 1,
        "candidateCount": 1,
        "stopSequences": [
            "<|user|>",
            "<|bot|>",
            "<|context_request|>",
            "<|endoftext|>",
            "<|end_of_turn|>",
        ],
    }

    temperature = payload.get("temperature", None)
    config["temperature"] = DEFAULT_TEMPERATURE if temperature is None else temperature

    top_p = payload.get("top_p", None)
    if top_p is not None:
        config["topP"] = top_p

    top_k = payload.get("top_k", None)
    if top_k is not None:
        config["topK"] = top_k

    max_tokens = payload.get("max_tokens")
    if max_tokens is not None:
        config["maxOutputTokens"] = max_tokens

    # å¤„ç† extended thinking å‚æ•° (plan mode)
    thinking = payload.get("thinking")
    is_plan_mode = False
    if thinking and isinstance(thinking, dict):
        thinking_type = thinking.get("type")
        budget_tokens = thinking.get("budget_tokens")
        
        # å¦‚æœå¯ç”¨äº† extended thinkingï¼Œè®¾ç½® thinkingConfig
        if thinking_type == "enabled":
            is_plan_mode = True
            thinking_config: Dict[str, Any] = {}
            
            # è®¾ç½®æ€è€ƒé¢„ç®—ï¼Œé»˜è®¤ä½¿ç”¨è¾ƒå¤§ç„å€¼ä»¥æ”¯æŒè®¡åˆ’æ¨¡å¼
            if budget_tokens is not None:
                thinking_config["thinkingBudget"] = budget_tokens
            else:
                # é»˜è®¤ç»™ä¸€ä¸ªè¾ƒå¤§ç„æ€è€ƒé¢„ç®—ä»¥æ”¯æŒå®Œæ•´ç„è®¡åˆ’ç”Ÿæˆ
                thinking_config["thinkingBudget"] = 48000
            
            # å§‹ç»ˆåŒ…å«æ€è€ƒå†…å®¹ï¼Œè¿™æ ·æ‰èƒ½çœ‹åˆ°è®¡åˆ’
            thinking_config["includeThoughts"] = True
            
            config["thinkingConfig"] = thinking_config
            log.info(f"[ANTHROPIC2GEMINI] Extended thinking enabled with budget: {thinking_config['thinkingBudget']}")
        elif thinking_type == "disabled":
            # æ˜ç¡®ç¦ç”¨æ€è€ƒæ¨¡å¼
            config["thinkingConfig"] = {
                "includeThoughts": False
            }
            log.info("[ANTHROPIC2GEMINI] Extended thinking explicitly disabled")

    stop_sequences = payload.get("stop_sequences")
    if isinstance(stop_sequences, list) and stop_sequences:
        config["stopSequences"] = config["stopSequences"] + [str(s) for s in stop_sequences]
    elif is_plan_mode:
        # Plan mode æ—¶æ¸…ç©ºé»˜è®¤ stop sequencesï¼Œé¿å…è¿‡æ—©åœæ­¢
        # é»˜è®¤ç„ stop sequences å¯èƒ½ä¼å¯¼è‡´æ¨¡å‹åœ¨ç”Ÿæˆè®¡åˆ’æ—¶è¿‡æ—©åœæ­¢
        config["stopSequences"] = []
        log.info("[ANTHROPIC2GEMINI] Plan mode: cleared default stop sequences to prevent premature stopping")
    
    # å¦‚æœä¸æ˜¯ plan mode ä¸”æ²¡æœ‰è‡ªå®ä¹‰ stop_sequencesï¼Œä¿æŒé»˜è®¤å€¼
    # (é»˜è®¤å€¼å·²ç»åœ¨ config åˆå§‹åŒ–æ—¶è®¾ç½®)

    return config


# ============================================================================
# 8. ä¸»è¦è½¬æ¢å‡½æ•°
# ============================================================================

async def anthropic_to_gemini_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    å°† Anthropic æ ¼å¼è¯·æ±‚ä½“è½¬æ¢ä¸º Gemini æ ¼å¼è¯·æ±‚ä½“

    æ³¨æ„: æ­¤å‡½æ•°åªè´Ÿè´£åŸºç¡€è½¬æ¢ï¼Œä¸åŒ…å« normalize_gemini_request ä¸­ç„å¤„ç†
    (å¦‚ thinking config è‡ªå¨è®¾ç½®ă€search toolsă€å‚æ•°èŒƒå›´é™åˆ¶ç­‰)

    Args:
        payload: Anthropic æ ¼å¼ç„è¯·æ±‚ä½“å­—å…¸

    Returns:
        Gemini æ ¼å¼ç„è¯·æ±‚ä½“å­—å…¸ï¼ŒåŒ…å«:
        - contents: è½¬æ¢åç„æ¶ˆæ¯å†…å®¹
        - generationConfig: ç”Ÿæˆé…ç½®
        - systemInstruction: ç³»ç»ŸæŒ‡ä»¤ (å¦‚æœæœ‰)
        - tools: å·¥å…·å®ä¹‰ (å¦‚æœæœ‰)
        - toolConfig: å·¥å…·è°ƒç”¨é…ç½® (å¦‚æœæœ‰ tool_choice)
    """
    # å¤„ç†è¿ç»­ç„systemæ¶ˆæ¯ï¼ˆå…¼å®¹æ€§æ¨¡å¼ï¼‰
    payload = await merge_system_messages(payload)

    # æå–å’Œè½¬æ¢åŸºç¡€ä¿¡æ¯
    messages = payload.get("messages") or []
    if not isinstance(messages, list):
        messages = []
    
    # [CRITICAL FIX] è¿‡æ»¤å¹¶ä¿®å¤ Thinking å—ç­¾å
    # åœ¨è½¬æ¢å‰å…ˆè¿‡æ»¤æ— æ•ˆç„ thinking å—
    filter_invalid_thinking_blocks(messages)

    # æ„å»ºç”Ÿæˆé…ç½®
    generation_config = build_generation_config(payload)

    # è½¬æ¢æ¶ˆæ¯å†…å®¹ï¼ˆå§‹ç»ˆåŒ…å«thinkingå—ï¼Œç”±å“åº”ç«¯å¤„ç†ï¼‰
    contents = convert_messages_to_contents(messages, include_thinking=True)
    
    # [CRITICAL FIX] ç§»é™¤å°¾éƒ¨æ— ç­¾åç„ thinking å—
    # å¯¹çœŸå®è¯·æ±‚åº”ç”¨é¢å¤–ç„æ¸…ç†
    for content in contents:
        role = content.get("role", "")
        if role == "model":  # åªå¤„ç† model/assistant æ¶ˆæ¯
            parts = content.get("parts", [])
            if isinstance(parts, list):
                remove_trailing_unsigned_thinking(parts)
    
    contents = reorganize_tool_messages(contents)

    # è½¬æ¢å·¥å…·
    tools = convert_tools(payload.get("tools"))
    
    # è½¬æ¢ tool_choice
    tool_config = convert_tool_choice_to_tool_config(payload.get("tool_choice"))

    # æ„å»ºåŸºç¡€è¯·æ±‚æ•°æ®
    gemini_request = {
        "contents": contents,
        "generationConfig": generation_config,
    }
    
    # å¦‚æœ merge_system_messages å·²ç»æ·»å äº† systemInstructionï¼Œä½¿ç”¨å®ƒ
    if "systemInstruction" in payload:
        gemini_request["systemInstruction"] = payload["systemInstruction"]
    
    if tools:
        gemini_request["tools"] = tools

    # æ·»å  toolConfigï¼ˆå¦‚æœæœ‰ tool_choiceï¼‰
    if tool_config:
        gemini_request["toolConfig"] = tool_config

    # é€ä¼ å›¾ç‰‡ç”Ÿæˆç„ size å‚æ•°ï¼ˆå¦‚ "1024x1536"ï¼‰
    if "size" in payload and payload["size"]:
        gemini_request["size"] = payload["size"]

    return gemini_request


def gemini_to_anthropic_response(
    gemini_response: Dict[str, Any],
    model: str,
    status_code: int = 200
) -> Dict[str, Any]:
    """
    å°† Gemini æ ¼å¼éæµå¼å“åº”è½¬æ¢ä¸º Anthropic æ ¼å¼éæµå¼å“åº”

    æ³¨æ„: å¦‚æœæ”¶åˆ°ç„ä¸æ˜¯ 200 å¼€å¤´ç„å“åº”ä½“ï¼Œä¸åä»»ä½•å¤„ç†ï¼Œç›´æ¥è½¬å‘

    Args:
        gemini_response: Gemini æ ¼å¼ç„å“åº”ä½“å­—å…¸
        model: æ¨¡å‹åç§°
        status_code: HTTP ç¶æ€ç  (é»˜è®¤ 200)

    Returns:
        Anthropic æ ¼å¼ç„å“åº”ä½“å­—å…¸ï¼Œæˆ–åŸå§‹å“åº” (å¦‚æœç¶æ€ç ä¸æ˜¯ 2xx)
    """
    # é 2xx ç¶æ€ç ç›´æ¥è¿”å›åŸå§‹å“åº”
    if not (200 <= status_code < 300):
        return gemini_response

    # å¤„ç† Code Assist ç„ response åŒ…è£…æ ¼å¼
    if "response" in gemini_response:
        response_data = gemini_response["response"]
    else:
        response_data = gemini_response

    # æå–å€™é€‰ç»“æœ
    candidate = response_data.get("candidates", [{}])[0] or {}
    parts = candidate.get("content", {}).get("parts", []) or []

    # è·å– usage metadata
    usage_metadata = {}
    if "usageMetadata" in response_data:
        usage_metadata = response_data["usageMetadata"]
    elif "usageMetadata" in candidate:
        usage_metadata = candidate["usageMetadata"]

    # è½¬æ¢å†…å®¹å—
    content = []
    has_tool_use = False

    for part in parts:
        if not isinstance(part, dict):
            continue

        # å¤„ç† thinking å—
        if part.get("thought") is True:
            if is_skip_thought_signature_placeholder(part):
                continue
            thinking_text = part.get("text", "")
            if thinking_text is None:
                thinking_text = ""
            
            block: Dict[str, Any] = {"type": "thinking", "thinking": str(thinking_text)}
            
            # å¦‚æœæœ‰ thoughtsignature åˆ™æ·»å 
            thoughtsignature = part.get("thoughtSignature")
            if thoughtsignature:
                block["thoughtSignature"] = thoughtsignature
            
            content.append(block)
            continue

        # å¤„ç†æ–‡æœ¬å—
        if "text" in part:
            text = part.get("text", "")
            if (
                is_skip_thought_signature_placeholder(part)
                or is_internal_placeholder_text(text)
            ):
                continue
            content.append({"type": "text", "text": text})
            continue

        # å¤„ç†å·¥å…·è°ƒç”¨
        if "functionCall" in part:
            has_tool_use = True
            fc = part.get("functionCall", {}) or {}
            original_id = fc.get("id") or f"toolu_{uuid.uuid4().hex}"
            content.append(
                {
                    "type": "tool_use",
                    "id": original_id,
                    "name": fc.get("name") or "",
                    "input": _remove_nulls_for_tool_input(fc.get("args", {}) or {}),
                }
            )
            continue

        # å¤„ç†å›¾ç‰‡
        if "inlineData" in part:
            inline = part.get("inlineData", {}) or {}
            content.append(
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": inline.get("mimeType", "image/png"),
                        "data": inline.get("data", ""),
                    },
                }
            )
            continue

    # ç¡®å®åœæ­¢åŸå› 
    finish_reason = candidate.get("finishReason")
    
    # åªæœ‰åœ¨æ­£å¸¸åœæ­¢ï¼ˆSTOPï¼‰ä¸”æœ‰å·¥å…·è°ƒç”¨æ—¶æ‰è®¾ä¸º tool_use
    # é¿å…åœ¨ SAFETYă€MAX_TOKENS ç­‰æƒ…å†µä¸‹ä»ç„¶è¿”å› tool_use å¯¼è‡´å¾ªç¯
    if has_tool_use and finish_reason == "STOP":
        stop_reason = "tool_use"
    elif finish_reason == "MAX_TOKENS":
        stop_reason = "max_tokens"
    else:
        # å…¶ä»–æƒ…å†µï¼ˆSAFETYă€RECITATION ç­‰ï¼‰é»˜è®¤ä¸º end_turn
        stop_reason = "end_turn"

    # æå– token ä½¿ç”¨æƒ…å†µ
    usage = _anthropic_usage_from_metadata(usage_metadata)

    # æ„å»º Anthropic å“åº”
    message_id = f"msg_{uuid.uuid4().hex}"

    return {
        "id": message_id,
        "type": "message",
        "role": "assistant",
        "model": model,
        "content": content,
        "stop_reason": stop_reason,
        "stop_sequence": None,
        "usage": usage,
    }


async def gemini_stream_to_anthropic_stream(
    gemini_stream: AsyncIterator[bytes],
    model: str,
    status_code: int = 200
) -> AsyncIterator[bytes]:
    """
    å°† Gemini æ ¼å¼æµå¼å“åº”è½¬æ¢ä¸º Anthropic SSE æ ¼å¼æµå¼å“åº”

    æ³¨æ„: å¦‚æœæ”¶åˆ°ç„ä¸æ˜¯ 200 å¼€å¤´ç„å“åº”ä½“ï¼Œä¸åä»»ä½•å¤„ç†ï¼Œç›´æ¥è½¬å‘

    Args:
        gemini_stream: Gemini æ ¼å¼ç„æµå¼å“åº” (bytes è¿­ä»£å™¨)
        model: æ¨¡å‹åç§°
        status_code: HTTP ç¶æ€ç  (é»˜è®¤ 200)

    Yields:
        Anthropic SSE æ ¼å¼ç„å“åº”å— (bytes)
    """
    # é 2xx ç¶æ€ç ç›´æ¥è½¬å‘åŸå§‹æµ
    if not (200 <= status_code < 300):
        async for chunk in gemini_stream:
            yield chunk
        return

    # åˆå§‹åŒ–ç¶æ€
    message_id = f"msg_{uuid.uuid4().hex}"
    message_start_sent = False
    current_block_type: Optional[str] = None
    current_block_index = -1
    current_thinking_signature: Optional[str] = None
    has_tool_use = False
    input_tokens = 0
    output_tokens = 0
    cached_input_tokens = 0
    finish_reason: Optional[str] = None

    def _sse_event(event: str, data: Dict[str, Any]) -> bytes:
        """ç”Ÿæˆ SSE äº‹ä»¶"""
        payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        return f"event: {event}\ndata: {payload}\n\n".encode("utf-8")

    def _close_block() -> Optional[bytes]:
        """å…³é—­å½“å‰å†…å®¹å—"""
        nonlocal current_block_type
        if current_block_type is None:
            return None
        event = _sse_event(
            "content_block_stop",
            {"type": "content_block_stop", "index": current_block_index},
        )
        current_block_type = None
        return event

    def _usage_payload() -> Dict[str, int]:
        usage = {"input_tokens": input_tokens, "output_tokens": output_tokens}
        if cached_input_tokens > 0:
            usage["cache_read_input_tokens"] = cached_input_tokens
        return usage

    # å¤„ç†æµå¼æ•°æ®
    try:
        async for chunk in gemini_stream:
            # æ£€æŸ¥æ˜¯å¦æ˜¯ Response å¯¹è±¡ï¼ˆé”™è¯¯æƒ…å†µï¼‰
            if isinstance(chunk, Response):
                log.warning(f"[GEMINI_TO_ANTHROPIC] Response object received, status code: {chunk.status_code}, forwarding error directly")
                # ç›´æ¥è½¬å‘é”™è¯¯å“åº”å†…å®¹ï¼Œä¸åæ ¼å¼è½¬æ¢
                error_content = chunk.body if isinstance(chunk.body, bytes) else chunk.body.encode('utf-8')
                yield error_content
                return

            # è®°å½•æ¥æ”¶åˆ°ç„åŸå§‹chunk
            log.debug(f"[GEMINI_TO_ANTHROPIC] Raw chunk: {chunk[:200] if chunk else b''}")

            # è§£æ Gemini æµå¼å—
            if not chunk or not chunk.startswith(b"data: "):
                log.debug(f"[GEMINI_TO_ANTHROPIC] Skipping chunk (not SSE format or empty)")
                continue

            raw = chunk[6:].strip()
            if raw == b"[DONE]":
                log.debug(f"[GEMINI_TO_ANTHROPIC] Received [DONE] marker")
                break

            log.debug(f"[GEMINI_TO_ANTHROPIC] Parsing JSON: {raw[:200]}")

            try:
                data = json.loads(raw.decode('utf-8', errors='ignore'))
                log.debug(f"[GEMINI_TO_ANTHROPIC] Parsed data: {json.dumps(data, ensure_ascii=False)[:300]}")
            except Exception as e:
                log.warning(f"[GEMINI_TO_ANTHROPIC] JSON parse error: {e}")
                continue

            # å¤„ç† Code Assist ç„ response åŒ…è£…æ ¼å¼
            if "response" in data:
                response = data["response"]
            else:
                response = data

            candidate = (response.get("candidates", []) or [{}])[0] or {}
            parts = (candidate.get("content", {}) or {}).get("parts", []) or []

            # æ›´æ–° usage metadata
            if "usageMetadata" in response:
                usage = response["usageMetadata"]
                if isinstance(usage, dict):
                    if "promptTokenCount" in usage:
                        prompt_tokens_total = int(usage.get("promptTokenCount", 0) or 0)
                        input_tokens = max(prompt_tokens_total - cached_input_tokens, 0)
                    if "candidatesTokenCount" in usage:
                        output_tokens = int(usage.get("candidatesTokenCount", 0) or 0)
                    if "cachedContentTokenCount" in usage:
                        cached_input_tokens = int(usage.get("cachedContentTokenCount", 0) or 0)
                        input_tokens = max(
                            int(usage.get("promptTokenCount", 0) or 0) - cached_input_tokens,
                            0,
                        )

            # å‘é€ message_startï¼ˆä»…ä¸€æ¬¡ï¼‰
            if not message_start_sent:
                message_start_sent = True
                yield _sse_event(
                    "message_start",
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
                            "usage": _usage_payload(),
                        },
                    },
                )

            # å¤„ç†å„ç§ parts
            for part in parts:
                if not isinstance(part, dict):
                    continue

                # å¤„ç† thinking å—
                if part.get("thought") is True:
                    if is_skip_thought_signature_placeholder(part):
                        continue
                    thinking_text = part.get("text", "")
                    thoughtsignature = part.get("thoughtSignature")
                    
                    # æ£€æŸ¥æ˜¯å¦éœ€è¦å…³é—­ä¸ä¸€ä¸ªå—å¹¶å¼€å¯æ–°ç„ thinking å—
                    if current_block_type != "thinking":
                        close_evt = _close_block()
                        if close_evt:
                            yield close_evt

                        current_block_index += 1
                        current_block_type = "thinking"
                        current_thinking_signature = thoughtsignature

                        block: Dict[str, Any] = {"type": "thinking", "thinking": ""}
                        if thoughtsignature:
                            block["thoughtSignature"] = thoughtsignature
                        yield _sse_event(
                            "content_block_start",
                            {
                                "type": "content_block_start",
                                "index": current_block_index,
                                "content_block": block,
                            },
                        )
                    elif thoughtsignature and thoughtsignature != current_thinking_signature:
                        # ç­¾åå˜åŒ–ï¼Œéœ€è¦å¼€å¯æ–°ç„ thinking å—
                        close_evt = _close_block()
                        if close_evt:
                            yield close_evt
                        
                        current_block_index += 1
                        current_block_type = "thinking"
                        current_thinking_signature = thoughtsignature
                        
                        block_new: Dict[str, Any] = {"type": "thinking", "thinking": ""}
                        if thoughtsignature:
                            block_new["thoughtSignature"] = thoughtsignature
                        
                        yield _sse_event(
                            "content_block_start",
                            {
                                "type": "content_block_start",
                                "index": current_block_index,
                                "content_block": block_new,
                            },
                        )

                    # å‘é€ thinking æ–‡æœ¬å¢é‡
                    if thinking_text:
                        yield _sse_event(
                            "content_block_delta",
                            {
                                "type": "content_block_delta",
                                "index": current_block_index,
                                "delta": {"type": "thinking_delta", "thinking": thinking_text},
                            },
                        )
                    continue

                # å¤„ç†æ–‡æœ¬å—
                if "text" in part:
                    if (
                        is_skip_thought_signature_placeholder(part)
                        or is_internal_placeholder_text(part.get("text"))
                    ):
                        continue
                    text = part.get("text", "")
                    if isinstance(text, str) and not text.strip():
                        continue

                    if current_block_type != "text":
                        close_evt = _close_block()
                        if close_evt:
                            yield close_evt

                        current_block_index += 1
                        current_block_type = "text"

                        yield _sse_event(
                            "content_block_start",
                            {
                                "type": "content_block_start",
                                "index": current_block_index,
                                "content_block": {"type": "text", "text": ""},
                            },
                        )

                    if text:
                        yield _sse_event(
                            "content_block_delta",
                            {
                                "type": "content_block_delta",
                                "index": current_block_index,
                                "delta": {"type": "text_delta", "text": text},
                            },
                        )
                    continue

                # å¤„ç†å·¥å…·è°ƒç”¨
                if "functionCall" in part:
                    close_evt = _close_block()
                    if close_evt:
                        yield close_evt

                    has_tool_use = True
                    fc = part.get("functionCall", {}) or {}
                    original_id = fc.get("id") or f"toolu_{uuid.uuid4().hex}"
                    tool_id = original_id
                    tool_name = fc.get("name") or ""
                    tool_args = _remove_nulls_for_tool_input(fc.get("args", {}) or {})

                    if _anthropic_debug_enabled():
                        log.info(
                            f"[ANTHROPIC][tool_use] Processing tool call: name={tool_name}, "
                            f"id={tool_id}"
                        )

                    current_block_index += 1
                    # æ³¨æ„ï¼å·¥å…·è°ƒç”¨ä¸è®¾ç½® current_block_typeï¼Œå› ä¸ºå®ƒæ˜¯ç‹¬ç«‹å®Œæ•´ç„å—

                    yield _sse_event(
                        "content_block_start",
                        {
                            "type": "content_block_start",
                            "index": current_block_index,
                            "content_block": {
                                "type": "tool_use",
                                "id": tool_id,
                                "name": tool_name,
                                "input": {},
                            },
                        },
                    )

                    input_json = json.dumps(tool_args, ensure_ascii=False, separators=(",", ":"))
                    yield _sse_event(
                        "content_block_delta",
                        {
                            "type": "content_block_delta",
                            "index": current_block_index,
                            "delta": {"type": "input_json_delta", "partial_json": input_json},
                        },
                    )

                    yield _sse_event(
                        "content_block_stop",
                        {"type": "content_block_stop", "index": current_block_index},
                    )
                    # å·¥å…·è°ƒç”¨å—å·²å®Œå…¨å…³é—­ï¼Œcurrent_block_type ä¿æŒä¸º None
                    
                    if _anthropic_debug_enabled():
                        log.info(f"[ANTHROPIC] [tool_use] tool call block closed: index = {current_block_index}")
                    
                    continue

            # æ£€æŸ¥æ˜¯å¦ç»“æŸ
            if candidate.get("finishReason"):
                finish_reason = candidate.get("finishReason")
                break

        # å…³é—­æœ€åç„å†…å®¹å—
        close_evt = _close_block()
        if close_evt:
            yield close_evt

        # ç¡®å®åœæ­¢åŸå› 
        # åªæœ‰åœ¨æ­£å¸¸åœæ­¢ï¼ˆSTOPï¼‰ä¸”æœ‰å·¥å…·è°ƒç”¨æ—¶æ‰è®¾ä¸º tool_use
        # é¿å…åœ¨ SAFETYă€MAX_TOKENS ç­‰æƒ…å†µä¸‹ä»ç„¶è¿”å› tool_use å¯¼è‡´å¾ªç¯
        if has_tool_use and finish_reason == "STOP":
            stop_reason = "tool_use"
        elif finish_reason == "MAX_TOKENS":
            stop_reason = "max_tokens"
        else:
            # å…¶ä»–æƒ…å†µï¼ˆSAFETYă€RECITATION ç­‰ï¼‰é»˜è®¤ä¸º end_turn
            stop_reason = "end_turn"

        if _anthropic_debug_enabled():
            log.info(
                f"[ANTHROPIC][stream_end] Stream ended: stop_reason={stop_reason}, "
                f"has_tool_use={has_tool_use}, finish_reason={finish_reason}, "
                f"input_tokens={input_tokens}, output_tokens={output_tokens}"
            )

        # å‘é€ message_delta å’Œ message_stop
        yield _sse_event(
            "message_delta",
            {
                "type": "message_delta",
                "delta": {"stop_reason": stop_reason, "stop_sequence": None},
                "usage": _usage_payload(),
            },
        )

        yield _sse_event("message_stop", {"type": "message_stop"})

    except Exception as e:
        log.error(f"[ANTHROPIC] Streaming conversion failed: {e}")
        # å‘é€é”™è¯¯äº‹ä»¶
        if not message_start_sent:
            yield _sse_event(
                "message_start",
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
                        "usage": _usage_payload(),
                    },
                },
            )
        yield _sse_event(
            "error",
            {"type": "error", "error": {"type": "api_error", "message": str(e)}},
        )
