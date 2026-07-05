"""
OpenAI Transfer Module - Handles conversion between OpenAI and Gemini API formats
è¢«openai-routerè°ƒç”¨ï¼Œè´Ÿè´£OpenAIæ ¼å¼ä¸Geminiæ ¼å¼ç„åŒå‘è½¬æ¢
"""

import json
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from pypinyin import Style, lazy_pinyin

from omni_gateway.converter.thoughtSignature_fix import (
    decode_tool_id_and_signature,
    is_internal_placeholder_text,
    is_skip_thought_signature_placeholder,
    SKIP_THOUGHT_SIGNATURE_VALIDATOR,
)
from omni_gateway.converter.utils import merge_system_messages

from log import log

def _convert_usage_metadata(usage_metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    å°†Geminiç„usageMetadataè½¬æ¢ä¸ºOpenAIæ ¼å¼ç„usageå­—æ®µ

    Args:
        usage_metadata: Gemini APIç„usageMetadataå­—æ®µ

    Returns:
        OpenAIæ ¼å¼ç„usageå­—å…¸ï¼Œå¦‚æœæ²¡æœ‰usageæ•°æ®åˆ™è¿”å›None
    """
    if not usage_metadata:
        return None

    prompt_tokens_total = int(usage_metadata.get("promptTokenCount", 0) or 0)
    cached_tokens = int(usage_metadata.get("cachedContentTokenCount", 0) or 0)
    prompt_tokens = max(prompt_tokens_total - cached_tokens, 0)
    completion_tokens = int(usage_metadata.get("candidatesTokenCount", 0) or 0)
    raw_total_tokens = int(
        usage_metadata.get(
            "totalTokenCount",
            prompt_tokens_total + completion_tokens + int(usage_metadata.get("thoughtsTokenCount", 0) or 0),
        )
        or 0
    )

    usage = {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": max(raw_total_tokens - cached_tokens, prompt_tokens + completion_tokens),
    }

    if cached_tokens > 0:
        usage["prompt_tokens_details"] = {"cached_tokens": cached_tokens}

    reasoning_tokens = int(usage_metadata.get("thoughtsTokenCount", 0) or 0)
    if reasoning_tokens > 0:
        usage["completion_tokens_details"] = {"reasoning_tokens": reasoning_tokens}

    return usage


def _build_message_with_reasoning(role: str, content: str, reasoning_content: str) -> dict:
    """æ„å»ºåŒ…å«å¯é€‰æ¨ç†å†…å®¹ç„æ¶ˆæ¯å¯¹è±¡"""
    message = {"role": role, "content": content}

    # å¦‚æœæœ‰thinking tokensï¼Œæ·»å reasoning_content
    if reasoning_content:
        message["reasoning_content"] = reasoning_content

    return message


def _map_finish_reason(gemini_reason: str) -> str:
    """
    å°†Geminiç»“æŸåŸå› æ˜ å°„åˆ°OpenAIç»“æŸåŸå› 

    Args:
        gemini_reason: æ¥è‡ªGemini APIç„ç»“æŸåŸå› 

    Returns:
        OpenAIå…¼å®¹ç„ç»“æŸåŸå› 
    """
    if gemini_reason == "STOP":
        return "stop"
    elif gemini_reason == "MAX_TOKENS":
        return "length"
    elif gemini_reason in ["SAFETY", "RECITATION"]:
        return "content_filter"
    else:
        # å¯¹äº None æˆ–æœªçŸ¥ç„ finishReasonï¼Œè¿”å› "stop" ä½œä¸ºé»˜è®¤å€¼
        # é¿å…è¿”å› None å¯¼è‡´ MCP å®¢æˆ·ç«¯è¯¯åˆ¤ä¸ºå“åº”æœªå®Œæˆè€Œå¾ªç¯è°ƒç”¨
        return "stop"


# ==================== Tool Conversion Functions ====================


def _normalize_function_name(name: str) -> str:
    """
    è§„èŒƒåŒ–å‡½æ•°åä»¥ç¬¦åˆ Gemini API è¦æ±‚

    è§„åˆ™ï¼
    - å¿…é¡»ä»¥å­—æ¯æˆ–ä¸‹åˆ’çº¿å¼€å¤´
    - åªèƒ½åŒ…å« a-z, A-Z, 0-9, ä¸‹åˆ’çº¿, è‹±æ–‡å¥ç‚¹, è‹±æ–‡çŸ­åˆ’çº¿
    - æœ€å¤§é•¿åº¦ 64 ä¸ªå­—ç¬¦

    è½¬æ¢ç­–ç•¥ï¼
    1. ä¸­æ–‡å­—ç¬¦è½¬æ¢ä¸ºæ‹¼éŸ³
    2. å°†éæ³•å­—ç¬¦æ›¿æ¢ä¸ºä¸‹åˆ’çº¿
    3. å¦‚æœä»¥éå­—æ¯/ä¸‹åˆ’çº¿å¼€å¤´ï¼Œæ·»å ä¸‹åˆ’çº¿å‰ç¼€
    4. æˆªæ–­åˆ° 64 ä¸ªå­—ç¬¦

    Args:
        name: åŸå§‹å‡½æ•°å

    Returns:
        è§„èŒƒåŒ–åç„å‡½æ•°å
    """
    import re

    if not name:
        return "_unnamed_function"

    # æ­¥éª¤1ï¼è½¬æ¢ä¸­æ–‡å­—ç¬¦ä¸ºæ‹¼éŸ³
    if re.search(r"[\u4e00-\u9fff]", name):
        try:
            parts = []
            for char in name:
                if "\u4e00" <= char <= "\u9fff":
                    # ä¸­æ–‡å­—ç¬¦è½¬æ¢ä¸ºæ‹¼éŸ³
                    pinyin = lazy_pinyin(char, style=Style.NORMAL)
                    parts.append("".join(pinyin))
                else:
                    parts.append(char)
            normalized = "".join(parts)
        except ImportError:
            log.warning("pypinyin not installed, cannot convert Chinese characters to pinyin")
            normalized = name
    else:
        normalized = name

    # æ­¥éª¤2ï¼å°†éæ³•å­—ç¬¦æ›¿æ¢ä¸ºä¸‹åˆ’çº¿
    # åˆæ³•å­—ç¬¦ï¼a-z, A-Z, 0-9, _, ., -
    normalized = re.sub(r"[^a-zA-Z0-9_.\-]", "_", normalized)

    # æ­¥éª¤3ï¼ç¡®ä¿ä»¥å­—æ¯æˆ–ä¸‹åˆ’çº¿å¼€å¤´
    if normalized and not (normalized[0].isalpha() or normalized[0] == "_"):
        # ä»¥æ•°å­—ă€ç‚¹æˆ–çŸ­æ¨ªçº¿å¼€å¤´ï¼Œæ·»å ä¸‹åˆ’çº¿å‰ç¼€
        normalized = "_" + normalized

    # æ­¥éª¤4ï¼æˆªæ–­åˆ° 64 ä¸ªå­—ç¬¦
    if len(normalized) > 64:
        normalized = normalized[:64]

    # æ­¥éª¤5ï¼ç¡®ä¿ä¸ä¸ºç©º
    if not normalized:
        normalized = "_unnamed_function"

    return normalized


def _resolve_ref(ref: str, root_schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    è§£æ $ref æˆ– ref å¼•ç”¨
    
    Args:
        ref: å¼•ç”¨è·¯å¾„ï¼Œå¦‚ "#/definitions/MyType" æˆ– "#/$defs/MyType"
        root_schema: æ ¹ schema å¯¹è±¡
        
    Returns:
        è§£æåç„ schemaï¼Œå¦‚æœå¤±è´¥è¿”å› None
    """
    if not isinstance(ref, str):
        return None
        
    if not ref.startswith('#/'):
        # å°è¯•åœ¨ definitions æˆ– $defs ä¸­æŸ¥æ‰¾
        for key in ["definitions", "$defs"]:
            if key in root_schema and ref in root_schema[key]:
                return root_schema[key][ref]
        return None
    
    path = ref[2:].split('/')
    current = root_schema
    
    for segment in path:
        if isinstance(current, dict) and segment in current:
            current = current[segment]
        else:
            return None
    
    return current if isinstance(current, dict) else None


def _clean_schema_for_claude(schema: Any, root_schema: Optional[Dict[str, Any]] = None, visited: Optional[set] = None) -> Any:
    """
    æ¸…ç† JSON Schemaï¼Œè½¬æ¢ä¸º Claude API æ”¯æŒç„æ ¼å¼ï¼ˆç¬¦åˆ JSON Schema draft 2020-12ï¼‰

    å¤„ç†é€»è¾‘ï¼
    1. è§£æ $ref å¼•ç”¨
    2. åˆå¹¶ allOf ä¸­ç„ schema
    3. è½¬æ¢ anyOf ä¸ºæ›´å…¼å®¹ç„æ ¼å¼
    4. ä¿æŒæ ‡å‡† JSON Schema ç±»å‹ï¼ˆä¸è½¬æ¢ä¸ºå¤§å†™ï¼‰
    5. å¤„ç† array ç„ items
    6. æ¸…ç† Claude ä¸æ”¯æŒç„å­—æ®µ

    Args:
        schema: JSON Schema å¯¹è±¡
        root_schema: æ ¹ schemaï¼ˆç”¨äºè§£æ $refï¼‰
        visited: å·²è®¿é—®ç„å¯¹è±¡é›†åˆï¼ˆé˜²æ­¢å¾ªç¯å¼•ç”¨ï¼‰

    Returns:
        æ¸…ç†åç„ schema
    """
    # éå­—å…¸ç±»å‹ç›´æ¥è¿”å›
    if not isinstance(schema, dict):
        return schema

    # åˆå§‹åŒ–
    if root_schema is None:
        root_schema = schema
    if visited is None:
        visited = set()

    # é˜²æ­¢å¾ªç¯å¼•ç”¨
    schema_id = id(schema)
    if schema_id in visited:
        return schema
    visited.add(schema_id)

    # åˆ›å»ºå‰¯æœ¬é¿å…ä¿®æ”¹åŸå¯¹è±¡
    result = {}

    # 1. å¤„ç† $ref
    if "$ref" in schema:
        resolved = _resolve_ref(schema["$ref"], root_schema)
        if resolved:
            import copy
            result = copy.deepcopy(resolved)
            for key, value in schema.items():
                if key != "$ref":
                    result[key] = value
            schema = result
            result = {}

    # 2. å¤„ç† allOfï¼ˆåˆå¹¶æ‰€æœ‰ schemaï¼‰
    if "allOf" in schema:
        all_of_schemas = schema["allOf"]
        for item in all_of_schemas:
            cleaned_item = _clean_schema_for_claude(item, root_schema, visited)

            if "properties" in cleaned_item:
                if "properties" not in result:
                    result["properties"] = {}
                result["properties"].update(cleaned_item["properties"])

            if "required" in cleaned_item:
                if "required" not in result:
                    result["required"] = []
                result["required"].extend(cleaned_item["required"])

            for key, value in cleaned_item.items():
                if key not in ["properties", "required"]:
                    result[key] = value

        for key, value in schema.items():
            if key not in ["allOf", "properties", "required"]:
                result[key] = value
            elif key in ["properties", "required"] and key not in result:
                result[key] = value
    else:
        result = dict(schema)

    # 3. å¤„ç† type æ•°ç»„ï¼ˆå¦‚ ["string", "null"]ï¼‰
    if "type" in result:
        type_value = result["type"]
        if isinstance(type_value, list):
            # Claude æ”¯æŒ type æ•°ç»„ï¼Œä¿æŒä¸å˜
            pass

    # 4. å¤„ç† array ç„ items
    if result.get("type") == "array":
        if "items" not in result:
            result["items"] = {}
        elif isinstance(result["items"], list):
            # Tuple å®ä¹‰ï¼Œæ£€æŸ¥æ˜¯å¦æ‰€æœ‰å…ƒç´ ç±»å‹ç›¸åŒ
            tuple_items = result["items"]
            first_type = tuple_items[0].get("type") if tuple_items else None
            is_homogeneous = all(item.get("type") == first_type for item in tuple_items)

            if is_homogeneous and first_type:
                result["items"] = _clean_schema_for_claude(tuple_items[0], root_schema, visited)
            else:
                # å¼‚è´¨å…ƒç»„ï¼Œä½¿ç”¨ anyOf è¡¨ç¤º
                result["items"] = {
                    "anyOf": [_clean_schema_for_claude(item, root_schema, visited) for item in tuple_items]
                }
        else:
            result["items"] = _clean_schema_for_claude(result["items"], root_schema, visited)

    # 5. å¤„ç† anyOfï¼ˆä¿æŒ anyOfï¼Œé€’å½’æ¸…ç†ï¼‰
    if "anyOf" in result:
        result["anyOf"] = [_clean_schema_for_claude(item, root_schema, visited) for item in result["anyOf"]]

    # 6. æ¸…ç† Claude ä¸æ”¯æŒç„å­—æ®µï¼ˆæ ¹æ® JSON Schema 2020-12ï¼‰
    # Claude API å¯¹æŸäº›å­—æ®µæ¯”è¾ƒä¸¥æ ¼ï¼Œç§»é™¤å¯èƒ½å¯¼è‡´é—®é¢˜ç„å­—æ®µ
    unsupported_keys = {
        "title", "$schema", "strict",
        "additionalItems",  # åºŸå¼ƒå­—æ®µï¼Œä½¿ç”¨ items æ›¿ä»£
        "exclusiveMaximum", "exclusiveMinimum",  # åœ¨ 2020-12 ä¸­è¿™äº›åº”è¯¥æ˜¯æ•°å€¼è€Œéå¸ƒå°”å€¼
        "$defs", "definitions",  # ç§»é™¤ definitions ç›¸å…³å­—æ®µé¿å…å†²çª
        "example", "examples", "readOnly", "writeOnly",
        "const",  # const å¯èƒ½å¯¼è‡´é—®é¢˜
        "contentEncoding", "contentMediaType",
        "oneOf",  # oneOf å¯èƒ½å¯¼è‡´é—®é¢˜ï¼Œç”¨ anyOf æ›¿ä»£
        "patternProperties", "dependencies", "propertyNames",  # Google API ä¸æ”¯æŒ
    }

    for key in list(result.keys()):
        if key in unsupported_keys:
            del result[key]

    # é€’å½’å¤„ç† additionalPropertiesï¼ˆå¦‚æœå­˜åœ¨ï¼‰
    if "additionalProperties" in result and isinstance(result["additionalProperties"], dict):
        result["additionalProperties"] = _clean_schema_for_claude(result["additionalProperties"], root_schema, visited)

    # 7. é€’å½’å¤„ç† properties
    if "properties" in result:
        cleaned_props = {}
        for prop_name, prop_schema in result["properties"].items():
            cleaned_props[prop_name] = _clean_schema_for_claude(prop_schema, root_schema, visited)
        result["properties"] = cleaned_props

    # 8. ç¡®ä¿æœ‰ type å­—æ®µï¼ˆå¦‚æœæœ‰ properties ä½†æ²¡æœ‰ typeï¼‰
    if "properties" in result and "type" not in result:
        result["type"] = "object"

    # 9. å»é‡ required æ•°ç»„
    if "required" in result and isinstance(result["required"], list):
        result["required"] = list(dict.fromkeys(result["required"]))

    return result


def _clean_schema_for_gemini(schema: Any, root_schema: Optional[Dict[str, Any]] = None, visited: Optional[set] = None) -> Any:
    """
    æ¸…ç† JSON Schemaï¼Œè½¬æ¢ä¸º Gemini æ”¯æŒç„æ ¼å¼

    å‚è€ƒ worker.mjs ç„ transformOpenApiSchemaToGemini å®ç°

    å¤„ç†é€»è¾‘ï¼
    1. è§£æ $ref å¼•ç”¨
    2. åˆå¹¶ allOf ä¸­ç„ schema
    3. è½¬æ¢ anyOf ä¸º enumï¼ˆå¦‚æœå¯èƒ½ï¼‰
    4. ç±»å‹æ˜ å°„ï¼ˆstring -> STRINGï¼‰
    5. å¤„ç† ARRAY ç„ itemsï¼ˆåŒ…æ‹¬ Tupleï¼‰
    6. å°† default å€¼ç§»åˆ° description
    7. æ¸…ç†ä¸æ”¯æŒç„å­—æ®µ

    Args:
        schema: JSON Schema å¯¹è±¡
        root_schema: æ ¹ schemaï¼ˆç”¨äºè§£æ $refï¼‰
        visited: å·²è®¿é—®ç„å¯¹è±¡é›†åˆï¼ˆé˜²æ­¢å¾ªç¯å¼•ç”¨ï¼‰

    Returns:
        æ¸…ç†åç„ schema
    """
    # éå­—å…¸ç±»å‹ç›´æ¥è¿”å›
    if not isinstance(schema, dict):
        return schema
    
    # åˆå§‹åŒ–
    if root_schema is None:
        root_schema = schema
    if visited is None:
        visited = set()
    
    # é˜²æ­¢å¾ªç¯å¼•ç”¨
    schema_id = id(schema)
    if schema_id in visited:
        return schema
    visited.add(schema_id)
    
    # åˆ›å»ºå‰¯æœ¬é¿å…ä¿®æ”¹åŸå¯¹è±¡
    result = {}
    
    # 1. å¤„ç† $ref æˆ– ref
    ref_key = "$ref" if "$ref" in schema else ("ref" if "ref" in schema else None)
    if ref_key:
        resolved = _resolve_ref(schema[ref_key], root_schema)
        if resolved:
            # æ£€æµ‹å¾ªç¯å¼•ç”¨
            resolved_id = id(resolved)
            if resolved_id in visited:
                return {"type": "OBJECT", "description": "(circular reference)"}
            
            visited.add(resolved_id)
            # åˆå¹¶è§£æåç„ schema
            merged = dict(resolved)
            
            # é‡è¦ï¼æ ¹æ® Gemini API é™åˆ¶ï¼Œå½“å­˜åœ¨å¼•ç”¨æ—¶ï¼Œåªèƒ½å¹¶åˆ—å­˜åœ¨ description å’Œ default
            # å…¶ä»–å­—æ®µï¼ˆå¦‚ type, properties ç­‰ï¼‰å¿…é¡»ä¸¢å¼ƒï¼Œå¦åˆ™ä¼è§¦å‘ 400 é”™è¯¯
            for key in ["description", "default"]:
                if key in schema:
                    merged[key] = schema[key]
            
            schema = merged
            result = {}
    
    # 2. å¤„ç† allOfï¼ˆåˆå¹¶æ‰€æœ‰ schemaï¼‰
    if "allOf" in schema:
        all_of_schemas = schema["allOf"]
        for item in all_of_schemas:
            cleaned_item = _clean_schema_for_gemini(item, root_schema, visited)
            
            # åˆå¹¶ properties
            if "properties" in cleaned_item:
                if "properties" not in result:
                    result["properties"] = {}
                result["properties"].update(cleaned_item["properties"])
            
            # åˆå¹¶ required
            if "required" in cleaned_item:
                if "required" not in result:
                    result["required"] = []
                result["required"].extend(cleaned_item["required"])
            
            # åˆå¹¶å…¶ä»–å­—æ®µï¼ˆç®€å•è¦†ç›–ï¼‰
            for key, value in cleaned_item.items():
                if key not in ["properties", "required"]:
                    result[key] = value
        
        # å¤åˆ¶å…¶ä»–å­—æ®µ
        for key, value in schema.items():
            if key not in ["allOf", "properties", "required"]:
                result[key] = value
            elif key in ["properties", "required"] and key not in result:
                result[key] = value
    else:
        # å¤åˆ¶æ‰€æœ‰å­—æ®µ
        result = dict(schema)
    
    # 3. ç±»å‹æ˜ å°„ï¼ˆè½¬æ¢ä¸ºå¤§å†™ï¼‰
    # æ³¨æ„ï¼Gemini API ç„ type å­—æ®µå¿…é¡»æ˜¯å­—ç¬¦ä¸²ï¼Œä¸èƒ½æ˜¯æ•°ç»„
    if "type" in result:
        type_value = result["type"]

        # å¦‚æœ type æ˜¯åˆ—è¡¨ï¼Œæå–ä¸»è¦ç±»å‹ï¼ˆé nullï¼‰
        if isinstance(type_value, list):
            primary_type = next((t for t in type_value if t != "null"), None)
            type_value = primary_type if primary_type else "STRING"  # é»˜è®¤ä¸º STRING

        # ç±»å‹æ˜ å°„
        type_map = {
            "string": "STRING",
            "number": "NUMBER",
            "integer": "INTEGER",
            "boolean": "BOOLEAN",
            "array": "ARRAY",
            "object": "OBJECT",
        }

        if isinstance(type_value, str) and type_value.lower() in type_map:
            # ç¡®ä¿ result["type"] æ˜¯å­—ç¬¦ä¸²è€Œä¸æ˜¯åˆ—è¡¨
            result["type"] = type_map[type_value.lower()]
        else:
            # æœªçŸ¥ç±»å‹ï¼Œåˆ é™¤è¯¥å­—æ®µ
            del result["type"]
    
    # 4. å¤„ç† ARRAY ç„ items
    if result.get("type") == "ARRAY":
        if "items" not in result:
            # æ²¡æœ‰ itemsï¼Œé»˜è®¤å…è®¸ä»»æ„ç±»å‹
            result["items"] = {}
        elif isinstance(result["items"], list):
            # Tuple å®ä¹‰ï¼ˆitems æ˜¯æ•°ç»„ï¼‰
            tuple_items = result["items"]
            
            # æå–ç±»å‹ä¿¡æ¯ç”¨äº description
            tuple_types = [item.get("type", "any") for item in tuple_items]
            tuple_desc = f"(Tuple: [{', '.join(tuple_types)}])"
            
            original_desc = result.get("description", "")
            result["description"] = f"{original_desc} {tuple_desc}".strip()
            
            # æ£€æŸ¥æ˜¯å¦æ‰€æœ‰å…ƒç´ ç±»å‹ç›¸åŒ
            first_type = tuple_items[0].get("type") if tuple_items else None
            is_homogeneous = all(item.get("type") == first_type for item in tuple_items)
            
            if is_homogeneous and first_type:
                # åŒè´¨å…ƒç»„ï¼Œè½¬æ¢ä¸º List<Type>
                result["items"] = _clean_schema_for_gemini(tuple_items[0], root_schema, visited)
            else:
                # å¼‚è´¨å…ƒç»„ï¼ŒGemini ä¸æ”¯æŒï¼Œè®¾ä¸º {}
                result["items"] = {}
        else:
            # é€’å½’å¤„ç† items
            result["items"] = _clean_schema_for_gemini(result["items"], root_schema, visited)
    
    # 5. å¤„ç† anyOfï¼ˆå°è¯•è½¬æ¢ä¸º enumï¼‰
    if "anyOf" in result:
        any_of_schemas = result["anyOf"]
        
        # é€’å½’å¤„ç†æ¯ä¸ª schema
        cleaned_any_of = [_clean_schema_for_gemini(item, root_schema, visited) for item in any_of_schemas]
        
        # å°è¯•æå– enum
        if all("const" in item for item in cleaned_any_of):
            enum_values = [
                str(item["const"]) 
                for item in cleaned_any_of 
                if item.get("const") not in ["", None]
            ]
            if enum_values:
                result["type"] = "STRING"
                result["enum"] = enum_values
        elif "type" not in result:
            # å¦‚æœä¸æ˜¯ enumï¼Œå°è¯•å–ç¬¬ä¸€ä¸ªæœ‰æ•ˆç„ç±»å‹å®ä¹‰
            first_valid = next((item for item in cleaned_any_of if item.get("type") or item.get("enum")), None)
            if first_valid:
                result.update(first_valid)
        
        # åˆ é™¤ anyOf
        del result["anyOf"]
    
    # 6. å°† default å€¼ç§»åˆ° description
    if "default" in result:
        default_value = result["default"]
        original_desc = result.get("description", "")
        result["description"] = f"{original_desc} (Default: {json.dumps(default_value)})".strip()
        del result["default"]
    
    # 7. æ¸…ç†ä¸æ”¯æŒç„å­—æ®µ
    unsupported_keys = {
        "title", "$schema", "$ref", "ref", "strict", "exclusiveMaximum",
        "exclusiveMinimum", "additionalProperties", "oneOf", "allOf",
        "$defs", "definitions", "example", "examples", "readOnly",
        "writeOnly", "const", "additionalItems", "contains",
        "patternProperties", "dependencies", "propertyNames",
        "if", "then", "else", "contentEncoding", "contentMediaType"
    }
    
    for key in list(result.keys()):
        if key in unsupported_keys:
            del result[key]
    
    # 8. é€’å½’å¤„ç† properties
    if "properties" in result:
        cleaned_props = {}
        for prop_name, prop_schema in result["properties"].items():
            cleaned_props[prop_name] = _clean_schema_for_gemini(prop_schema, root_schema, visited)
        result["properties"] = cleaned_props
    
    # 9. ç¡®ä¿æœ‰ type å­—æ®µï¼ˆå¦‚æœæœ‰ properties ä½†æ²¡æœ‰ typeï¼‰
    if "properties" in result and "type" not in result:
        result["type"] = "OBJECT"
    
    # 10. å»é‡ required æ•°ç»„
    if "required" in result and isinstance(result["required"], list):
        result["required"] = list(dict.fromkeys(result["required"]))  # ä¿æŒé¡ºåºå»é‡
    
    return result


def _append_schema_hint(schema: Dict[str, Any], hint: str) -> None:
    """æä¸å…¼å®¹ç„æ ¡éªŒä¿¡æ¯æŒªåˆ° description é‡Œï¼Œé¿å…ä¸æ¸¸ç›´æ¥æ‹’æ”¶ă€‚"""
    if not hint:
        return
    desc = schema.get("description")
    schema["description"] = f"{desc} ({hint})" if desc else hint


def _clean_schema_for_parameters_json_schema(
    schema: Any,
    root_schema: Optional[Dict[str, Any]] = None,
    visited: Optional[set] = None,
) -> Any:
    """
    æ¸…ç† JSON Schemaï¼Œä¾› Code Assist å†…éƒ¨æ¥å£ç„ parametersJsonSchema ä½¿ç”¨ă€‚

    Code Assist ç„å†…éƒ¨æ¥å£æ›´æ¥è¿‘å®˜æ–¹ Code Assistï¼å·¥å…·å‚æ•°åº”æ”¾åœ¨
    parametersJsonSchema ä¸­ï¼Œå¹¶ä¿æŒ JSON Schema ç„å°å†™ typeă€‚
    """
    if not isinstance(schema, dict):
        return schema

    if root_schema is None:
        root_schema = schema
    if visited is None:
        visited = set()

    schema_id = id(schema)
    if schema_id in visited:
        return {"type": "object", "description": "(circular reference)"}
    visited.add(schema_id)

    result: Dict[str, Any]

    ref_key = "$ref" if "$ref" in schema else ("ref" if "ref" in schema else None)
    if ref_key:
        resolved = _resolve_ref(schema[ref_key], root_schema)
        if resolved:
            import copy
            result = copy.deepcopy(resolved)
            for key in ("description", "default"):
                if key in schema:
                    result[key] = schema[key]
            schema = result

    if "allOf" in schema:
        result = {}
        for item in schema.get("allOf") or []:
            cleaned_item = _clean_schema_for_parameters_json_schema(item, root_schema, visited)
            if not isinstance(cleaned_item, dict):
                continue
            if "properties" in cleaned_item:
                result.setdefault("properties", {}).update(cleaned_item["properties"])
            if "required" in cleaned_item:
                result.setdefault("required", []).extend(cleaned_item["required"])
            for key, value in cleaned_item.items():
                if key not in ("properties", "required"):
                    result[key] = value
        for key, value in schema.items():
            if key not in ("allOf", "properties", "required"):
                result[key] = value
            elif key in ("properties", "required") and key not in result:
                result[key] = value
    else:
        result = dict(schema)

    if "type" in result:
        type_value = result["type"]
        if isinstance(type_value, list):
            non_null_types = [t for t in type_value if isinstance(t, str) and t.lower() != "null"]
            if non_null_types:
                result["type"] = non_null_types[0]
                if "null" in [str(t).lower() for t in type_value]:
                    _append_schema_hint(result, "nullable")
            else:
                result["type"] = "string"
        elif isinstance(type_value, str):
            lower_type = type_value.lower()
            if lower_type in {"string", "number", "integer", "boolean", "array", "object", "null"}:
                result["type"] = "string" if lower_type == "null" else lower_type
            else:
                del result["type"]

    if "anyOf" in result or "oneOf" in result:
        union_key = "anyOf" if "anyOf" in result else "oneOf"
        union_items = result.get(union_key) or []
        cleaned_items = [
            item for item in (
                _clean_schema_for_parameters_json_schema(item, root_schema, visited)
                for item in union_items
            )
            if isinstance(item, dict)
        ]
        enum_values = [
            item.get("const")
            for item in union_items
            if isinstance(item, dict) and item.get("const") not in ("", None)
        ]
        if enum_values and len(enum_values) == len(union_items):
            result["type"] = "string"
            result["enum"] = [str(v) for v in enum_values]
        else:
            preferred = next(
                (
                    item for item in cleaned_items
                    if item.get("type") in ("object", "array") or item.get("properties")
                ),
                None,
            )
            if preferred is None:
                preferred = next((item for item in cleaned_items if item.get("type") or item.get("enum")), None)
            if preferred:
                existing_description = result.get("description")
                result.update(preferred)
                if existing_description:
                    _append_schema_hint(result, existing_description)
        result.pop("anyOf", None)
        result.pop("oneOf", None)

    if result.get("type") == "array":
        items = result.get("items")
        if isinstance(items, list):
            if items:
                result["items"] = _clean_schema_for_parameters_json_schema(items[0], root_schema, visited)
                _append_schema_hint(result, "tuple schema simplified")
            else:
                result.pop("items", None)
        elif isinstance(items, dict):
            result["items"] = _clean_schema_for_parameters_json_schema(items, root_schema, visited)

    validation_keys = {
        "default", "minLength", "maxLength", "minimum", "maximum",
        "minItems", "maxItems", "pattern", "format", "uniqueItems",
    }
    for key in list(result.keys()):
        if key in validation_keys:
            value = result.pop(key)
            if value not in (None, "", {}, []):
                _append_schema_hint(result, f"{key}: {json.dumps(value, ensure_ascii=False)}")

    unsupported_keys = {
        "title", "$schema", "$id", "$ref", "ref", "strict",
        "exclusiveMaximum", "exclusiveMinimum", "additionalProperties",
        "allOf", "anyOf", "oneOf", "$defs", "definitions", "example",
        "examples", "readOnly", "writeOnly", "const", "additionalItems",
        "contains", "patternProperties", "dependencies", "propertyNames",
        "if", "then", "else", "contentEncoding", "contentMediaType",
    }
    for key in list(result.keys()):
        if key in unsupported_keys or key.startswith("x-"):
            del result[key]

    nullable_props = set()
    if "properties" in result and isinstance(result["properties"], dict):
        cleaned_props = {}
        for prop_name, prop_schema in result["properties"].items():
            if isinstance(prop_schema, dict):
                prop_type = prop_schema.get("type")
                if isinstance(prop_type, list) and any(str(t).lower() == "null" for t in prop_type):
                    nullable_props.add(prop_name)
            cleaned_props[prop_name] = _clean_schema_for_parameters_json_schema(prop_schema, root_schema, visited)
        result["properties"] = cleaned_props

    if "properties" in result and "type" not in result:
        result["type"] = "object"

    if "required" in result and isinstance(result["required"], list):
        prop_names = set(result.get("properties", {}).keys()) if isinstance(result.get("properties"), dict) else None
        required = []
        for item in result["required"]:
            if not isinstance(item, str):
                continue
            if prop_names is not None and item not in prop_names:
                continue
            if item in nullable_props:
                continue
            if item not in required:
                required.append(item)
        if required:
            result["required"] = required
        else:
            result.pop("required", None)

    return result


def fix_tool_call_args_types(
    args: Dict[str, Any],
    parameters_schema: Dict[str, Any]
) -> Dict[str, Any]:
    """
    æ ¹æ®å·¥å…·ç„å‚æ•° schema ä¿®æ­£å‡½æ•°è°ƒç”¨å‚æ•°ç„ç±»å‹
    
    ä¾‹å¦‚ï¼å°†å­—ç¬¦ä¸² "5" è½¬æ¢ä¸ºæ•°å­— 5ï¼Œæ ¹æ® schema ä¸­ç„ type å®ä¹‰
    
    Args:
        args: å‡½æ•°è°ƒç”¨ç„å‚æ•°å­—å…¸
        parameters_schema: å·¥å…·å®ä¹‰ä¸­ç„ parameters schema
        
    Returns:
        ç±»å‹ä¿®æ­£åç„å‚æ•°å­—å…¸
    """
    if not args or not parameters_schema:
        return args
    
    properties = parameters_schema.get("properties", {})
    if not properties:
        return args
    
    fixed_args = {}
    for key, value in args.items():
        if key not in properties:
            # å‚æ•°ä¸åœ¨ schema ä¸­ï¼Œä¿æŒåŸæ ·
            fixed_args[key] = value
            continue
        
        param_schema = properties[key]
        param_type = param_schema.get("type")
        
        # æ ¹æ® schema ä¸­ç„ç±»å‹ä¿®æ­£å‚æ•°å€¼
        if param_type == "number" or param_type == "integer":
            # å¦‚æœå€¼æ˜¯å­—ç¬¦ä¸²ï¼Œå°è¯•è½¬æ¢ä¸ºæ•°å­—
            if isinstance(value, str):
                try:
                    if param_type == "integer":
                        fixed_args[key] = int(value)
                    else:
                        # å°è¯•è½¬æ¢ä¸º floatï¼Œå¦‚æœæ˜¯æ•´æ•°åˆ™ä¿æŒä¸º int
                        num_value = float(value)
                        fixed_args[key] = int(num_value) if num_value.is_integer() else num_value
                    log.debug(f"[OPENAI2GEMINI] Fixed parameter type: {key} '{value}' -> {fixed_args[key]} ({param_type})")
                except (ValueError, AttributeError):
                    # è½¬æ¢å¤±è´¥ï¼Œä¿æŒåŸæ ·
                    fixed_args[key] = value
                    log.warning(f"[OPENAI2GEMINI] Unable to convert value '{key}' of parameter {value} to {param_type}")
            else:
                fixed_args[key] = value
        elif param_type == "boolean":
            # å¦‚æœå€¼æ˜¯å­—ç¬¦ä¸²ï¼Œè½¬æ¢ä¸ºå¸ƒå°”å€¼
            if isinstance(value, str):
                if value.lower() in ("true", "1", "yes"):
                    fixed_args[key] = True
                elif value.lower() in ("false", "0", "no"):
                    fixed_args[key] = False
                else:
                    fixed_args[key] = value
                
                if fixed_args[key] != value:
                    log.debug(f"[OPENAI2GEMINI] Fixed parameter type: {key} '{value}' -> {fixed_args[key]} (boolean)")
            else:
                fixed_args[key] = value
        elif param_type == "string":
            # å¦‚æœå€¼ä¸æ˜¯å­—ç¬¦ä¸²ï¼Œè½¬æ¢ä¸ºå­—ç¬¦ä¸²
            if not isinstance(value, str):
                fixed_args[key] = str(value)
                log.debug(f"[OPENAI2GEMINI] Fixed parameter type: {key} {value} -> '{fixed_args[key]}' (string)")
            else:
                fixed_args[key] = value
        else:
            # å…¶ä»–ç±»å‹ï¼ˆarray, object ç­‰ï¼‰ä¿æŒåŸæ ·
            fixed_args[key] = value
    
    return fixed_args


def convert_openai_tools_to_gemini(openai_tools: List, model: str = "") -> List[Dict[str, Any]]:
    """
    å°† OpenAI tools æ ¼å¼è½¬æ¢ä¸º Gemini functionDeclarations æ ¼å¼

    Args:
        openai_tools: OpenAI æ ¼å¼ç„å·¥å…·åˆ—è¡¨ï¼ˆå¯èƒ½æ˜¯å­—å…¸æˆ– Pydantic æ¨¡å‹ï¼‰
        model: æ¨¡å‹åç§°ï¼ˆç”¨äºåˆ¤æ–­æ˜¯å¦ä¸º Claude æ¨¡å‹ï¼‰

    Returns:
        Gemini æ ¼å¼ç„å·¥å…·åˆ—è¡¨
    """
    if not openai_tools:
        return []

    # åˆ¤æ–­æ˜¯å¦ä¸º Claude æ¨¡å‹
    is_claude_model = "claude" in model.lower()

    function_declarations = []

    for tool in openai_tools:
        if tool.get("type") != "function":
            log.warning(f"Skipping non-function tool type: {tool.get('type')}")
            continue

        function = tool.get("function")
        if not function:
            log.warning("Tool missing 'function' field")
            continue

        # è·å–å¹¶è§„èŒƒåŒ–å‡½æ•°å
        original_name = function.get("name")
        if not original_name:
            log.warning("Tool missing 'name' field, using default")
            original_name = "_unnamed_function"

        normalized_name = _normalize_function_name(original_name)

        # å¦‚æœåç§°è¢«ä¿®æ”¹äº†ï¼Œè®°å½•æ—¥å¿—
        if normalized_name != original_name:
            log.debug(f"Function name normalized: '{original_name}' -> '{normalized_name}'")

        # æ„å»º Gemini function declaration
        declaration = {
            "name": normalized_name,
            "description": function.get("description", ""),
        }

        # æ·»å å‚æ•°ï¼ˆå¦‚æœæœ‰ï¼‰- Code Assist å†…éƒ¨æ¥å£æ›´é€‚åˆ parametersJsonSchema
        if "parameters" in function:
            if is_claude_model:
                cleaned_params = _clean_schema_for_parameters_json_schema(function["parameters"])
                log.debug(f"[OPENAI2GEMINI] Using Claude schema cleaning for tool: {normalized_name}")
            else:
                cleaned_params = _clean_schema_for_parameters_json_schema(function["parameters"])

            if cleaned_params:
                declaration["parametersJsonSchema"] = cleaned_params
            elif is_claude_model:
                declaration["parametersJsonSchema"] = {"type": "object", "properties": {}}
        elif is_claude_model:
            declaration["parametersJsonSchema"] = {"type": "object", "properties": {}}

        function_declarations.append(declaration)

    if not function_declarations:
        return []

    # Gemini æ ¼å¼ï¼å·¥å…·æ•°ç»„ä¸­åŒ…å« functionDeclarations
    return [{"functionDeclarations": function_declarations}]


def convert_tool_choice_to_tool_config(tool_choice: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    å°† OpenAI tool_choice è½¬æ¢ä¸º Gemini toolConfig

    Args:
        tool_choice: OpenAI æ ¼å¼ç„ tool_choice

    Returns:
        Gemini æ ¼å¼ç„ toolConfig
    """
    if isinstance(tool_choice, str):
        if tool_choice == "auto":
            return {"functionCallingConfig": {"mode": "AUTO"}}
        elif tool_choice == "none":
            return {"functionCallingConfig": {"mode": "NONE"}}
        elif tool_choice == "required":
            return {"functionCallingConfig": {"mode": "ANY"}}
    elif isinstance(tool_choice, dict):
        # {"type": "function", "function": {"name": "my_function"}}
        if tool_choice.get("type") == "function":
            function_name = tool_choice.get("function", {}).get("name")
            if function_name:
                return {
                    "functionCallingConfig": {
                        "mode": "ANY",
                        "allowedFunctionNames": [function_name],
                    }
                }

    # é»˜è®¤è¿”å› AUTO æ¨¡å¼
    return {"functionCallingConfig": {"mode": "AUTO"}}


def convert_tool_message_to_function_response(message, all_messages: List = None) -> Dict[str, Any]:
    """
    å°† OpenAI ç„ tool role æ¶ˆæ¯è½¬æ¢ä¸º Gemini functionResponse

    Args:
        message: OpenAI æ ¼å¼ç„å·¥å…·æ¶ˆæ¯
        all_messages: æ‰€æœ‰æ¶ˆæ¯ç„åˆ—è¡¨ï¼Œç”¨äºæŸ¥æ‰¾ tool_call_id å¯¹åº”ç„å‡½æ•°å

    Returns:
        Gemini æ ¼å¼ç„ functionResponse part
    """
    # è·å– name å­—æ®µ
    name = getattr(message, "name", None)
    encoded_tool_call_id = getattr(message, "tool_call_id", None) or ""

    # è§£ç è·å–åŸå§‹IDï¼ˆfunctionResponseä¸éœ€è¦ç­¾åï¼‰
    original_tool_call_id, _ = decode_tool_id_and_signature(encoded_tool_call_id)

    # å¦‚æœæ²¡æœ‰ nameï¼Œå°è¯•ä» all_messages ä¸­æŸ¥æ‰¾å¯¹åº”ç„ tool_call_id
    # æ³¨æ„ï¼ä½¿ç”¨ç¼–ç IDæŸ¥æ‰¾ï¼Œå› ä¸ºå­˜å‚¨ç„æ˜¯ç¼–ç ID
    if not name and encoded_tool_call_id and all_messages:
        for msg in all_messages:
            if getattr(msg, "role", None) == "assistant" and hasattr(msg, "tool_calls") and msg.tool_calls:
                for tool_call in msg.tool_calls:
                    if getattr(tool_call, "id", None) == encoded_tool_call_id:
                        func = getattr(tool_call, "function", None)
                        if func:
                            name = getattr(func, "name", None)
                            break
                if name:
                    break

    # æœ€ç»ˆå…œåº•ï¼å¦‚æœä»ç„¶æ²¡æœ‰ nameï¼Œä½¿ç”¨é»˜è®¤å€¼
    if not name:
        name = "unknown_function"
        log.warning(f"Tool message missing function name, using default: {name}")

    try:
        # å°è¯•å°† content è§£æä¸º JSON
        response_data = (
            json.loads(message.content) if isinstance(message.content, str) else message.content
        )
    except (json.JSONDecodeError, TypeError):
        # å¦‚æœä¸æ˜¯æœ‰æ•ˆç„ JSONï¼ŒåŒ…è£…ä¸ºå¯¹è±¡
        response_data = {"result": str(message.content)}

    # ç¡®ä¿ response_data æ˜¯å­—å…¸ç±»å‹ï¼ˆGemini API è¦æ±‚ response å¿…é¡»æ˜¯å¯¹è±¡ï¼‰
    if not isinstance(response_data, dict):
        response_data = {"result": response_data}

    return {"functionResponse": {"id": original_tool_call_id, "name": name, "response": response_data}}


def _reverse_transform_value(value: Any) -> Any:
    """
    å°†å€¼è½¬æ¢å›åŸå§‹ç±»å‹ï¼ˆGemini å¯èƒ½å°†æ‰€æœ‰å€¼è½¬ä¸ºå­—ç¬¦ä¸²ï¼‰

    ä»…å¤„ç† Gemini åœ¨å·¥å…·å‚æ•°ä¸­å¸¸è§ç„å¸ƒå°”/ç©ºå€¼å­—ç¬¦ä¸²åŒ–æƒ…å†µï¼Œ
    ä¸å†å¯¹æ•°å­—å­—ç¬¦ä¸²åå¯å‘å¼è½¬æ¢ï¼Œé¿å…æ schema å£°æ˜ä¸º string
    ç„å‚æ•°é”™è¯¯è¿˜åŸæˆ integeră€‚
    
    å‚è€ƒ worker.mjs ç„ reverseTransformValue
    
    Args:
        value: è¦è½¬æ¢ç„å€¼
        
    Returns:
        è½¬æ¢åç„å€¼
    """
    if not isinstance(value, str):
        return value
    
    # å¸ƒå°”å€¼
    if value == 'true':
        return True
    if value == 'false':
        return False
    
    # null
    if value == 'null':
        return None
    
    # å…¶ä»–æƒ…å†µä¿æŒå­—ç¬¦ä¸²
    return value


def _reverse_transform_args(args: Any) -> Any:
    """
    é€’å½’è½¬æ¢å‡½æ•°å‚æ•°ï¼Œå°†å­—ç¬¦ä¸²è½¬å›åŸå§‹ç±»å‹
    
    å‚è€ƒ worker.mjs ç„ reverseTransformArgs
    
    Args:
        args: å‡½æ•°å‚æ•°ï¼ˆå¯èƒ½æ˜¯å­—å…¸ă€åˆ—è¡¨æˆ–å…¶ä»–ç±»å‹ï¼‰
        
    Returns:
        è½¬æ¢åç„å‚æ•°
    """
    if not isinstance(args, (dict, list)):
        return args
    
    if isinstance(args, list):
        return [_reverse_transform_args(item) for item in args]
    
    # å¤„ç†å­—å…¸
    result = {}
    for key, value in args.items():
        if isinstance(value, (dict, list)):
            result[key] = _reverse_transform_args(value)
        else:
            result[key] = _reverse_transform_value(value)
    
    return result


def extract_tool_calls_from_parts(
    parts: List[Dict[str, Any]], is_streaming: bool = False
) -> Tuple[List[Dict[str, Any]], str]:
    """
    ä» Gemini response parts ä¸­æå–å·¥å…·è°ƒç”¨å’Œæ–‡æœ¬å†…å®¹

    Args:
        parts: Gemini response ç„ parts æ•°ç»„
        is_streaming: æ˜¯å¦ä¸ºæµå¼å“åº”ï¼ˆæµå¼å“åº”éœ€è¦æ·»å  index å­—æ®µï¼‰

    Returns:
        (tool_calls, text_content) å…ƒç»„
    """
    tool_calls = []
    text_content = ""

    for idx, part in enumerate(parts):
        # æ£€æŸ¥æ˜¯å¦æ˜¯å‡½æ•°è°ƒç”¨
        if "functionCall" in part:
            function_call = part["functionCall"]
            # è·å–åŸå§‹IDæˆ–ç”Ÿæˆæ–°ID
            original_id = function_call.get("id") or f"call_{uuid.uuid4().hex[:24]}"
            # è·å–å‚æ•°å¹¶è½¬æ¢ç±»å‹
            args = function_call.get("args", {})
            # å°†å­—ç¬¦ä¸²ç±»å‹ç„å€¼è½¬å›åŸå§‹ç±»å‹
            args = _reverse_transform_args(args)

            tool_call = {
                "id": original_id,
                "type": "function",
                "function": {
                    "name": function_call.get("name", "nameless_function"),
                    "arguments": json.dumps(args),
                },
            }
            # æµå¼å“åº”éœ€è¦ index å­—æ®µ
            if is_streaming:
                tool_call["index"] = idx
            tool_calls.append(tool_call)

        # æå–æ–‡æœ¬å†…å®¹ï¼ˆæ’é™¤ thinking tokensï¼‰
        elif "text" in part and not part.get("thought", False):
            text = part["text"]
            if (
                is_skip_thought_signature_placeholder(part)
                or is_internal_placeholder_text(text)
            ):
                continue
            text_content += text

    return tool_calls, text_content


def extract_images_from_content(content: Any) -> Dict[str, Any]:
    """
    ä» OpenAI content ä¸­æå–æ–‡æœ¬å’Œå›¾ç‰‡
    
    Args:
        content: OpenAI æ¶ˆæ¯ç„ content å­—æ®µï¼ˆå¯èƒ½æ˜¯å­—ç¬¦ä¸²æˆ–åˆ—è¡¨ï¼‰
    
    Returns:
        åŒ…å« text å’Œ images ç„å­—å…¸
    """
    result = {"text": "", "images": []}

    if isinstance(content, str):
        result["text"] = content
    elif isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    result["text"] += item.get("text", "")
                elif item.get("type") == "image_url":
                    image_url = item.get("image_url", {}).get("url", "")
                    # è§£æ data:image/png;base64,xxx æ ¼å¼
                    if image_url.startswith("data:image/"):
                        import re
                        match = re.match(r"^data:image/(\w+);base64,(.+)$", image_url)
                        if match:
                            mime_type = match.group(1)
                            base64_data = match.group(2)
                            result["images"].append({
                                "inlineData": {
                                    "mimeType": f"image/{mime_type}",
                                    "data": base64_data
                                }
                            })

    return result


def _sanitize_openai_roundtrip_signatures(contents: List[Dict[str, Any]]) -> None:
    """
    OpenAI-compatible clients may round-trip Gemini thinking signatures through
    fields we do not fully control. Keep tool calls on the safe bypass sentinel
    and drop signatures everywhere else to avoid Corrupted thought signature.
    """
    for content in contents:
        if not isinstance(content, dict):
            continue
        parts = content.get("parts")
        if not isinstance(parts, list):
            continue

        for index, part in enumerate(parts):
            if not isinstance(part, dict):
                continue

            sanitized_part = part.copy()
            if "thoughtSignature" in sanitized_part:
                if "functionCall" in sanitized_part or "function_call" in sanitized_part:
                    sanitized_part["thoughtSignature"] = SKIP_THOUGHT_SIGNATURE_VALIDATOR
                else:
                    sanitized_part.pop("thoughtSignature", None)

            if sanitized_part.get("thought") is True and not sanitized_part.get("thoughtSignature"):
                sanitized_part.pop("thought", None)

            parts[index] = sanitized_part


async def convert_openai_to_gemini_request(openai_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    å°† OpenAI æ ¼å¼è¯·æ±‚ä½“è½¬æ¢ä¸º Gemini æ ¼å¼è¯·æ±‚ä½“

    æ³¨æ„: æ­¤å‡½æ•°åªè´Ÿè´£åŸºç¡€è½¬æ¢,ä¸åŒ…å« normalize_gemini_request ä¸­ç„å¤„ç†
    (å¦‚ thinking config, search tools, å‚æ•°èŒƒå›´é™åˆ¶ç­‰)

    Args:
        openai_request: OpenAI æ ¼å¼ç„è¯·æ±‚ä½“å­—å…¸,åŒ…å«:
            - messages: æ¶ˆæ¯åˆ—è¡¨
            - temperature, top_p, max_tokens, stop ç­‰ç”Ÿæˆå‚æ•°
            - tools, tool_choice (å¯é€‰)
            - response_format (å¯é€‰)

    Returns:
        Gemini æ ¼å¼ç„è¯·æ±‚ä½“å­—å…¸,åŒ…å«:
            - contents: è½¬æ¢åç„æ¶ˆæ¯å†…å®¹
            - generationConfig: ç”Ÿæˆé…ç½®
            - systemInstruction: ç³»ç»ŸæŒ‡ä»¤ (å¦‚æœæœ‰)
            - tools, toolConfig (å¦‚æœæœ‰)
    """
    # å¤„ç†è¿ç»­ç„systemæ¶ˆæ¯ï¼ˆå…¼å®¹æ€§æ¨¡å¼ï¼‰
    openai_request = await merge_system_messages(openai_request)

    contents = []

    # æå–æ¶ˆæ¯åˆ—è¡¨
    messages = openai_request.get("messages", [])
    
    # æ„å»º tool_call_id -> (name, original_id, signature) ç„æ˜ å°„
    tool_call_mapping = {}
    for msg in messages:
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                encoded_id = tc.get("id", "")
                func_name = tc.get("function", {}).get("name") or ""
                if encoded_id:
                    # è§£ç è·å–åŸå§‹IDå’Œç­¾å
                    original_id, _ = decode_tool_id_and_signature(encoded_id)
                    tool_call_mapping[encoded_id] = (func_name, original_id, None)
    
    # æ„å»ºå·¥å…·åç§°åˆ°å‚æ•° schema ç„æ˜ å°„ï¼ˆç”¨äºç±»å‹ä¿®æ­£ï¼‰
    tool_schemas = {}
    if "tools" in openai_request and openai_request["tools"]:
        for tool in openai_request["tools"]:
            if tool.get("type") == "function":
                function = tool.get("function", {})
                func_name = function.get("name")
                if func_name:
                    tool_schemas[func_name] = function.get("parameters", {})

    # ç”¨äºç´¯ç§¯è¿ç»­ç„ tool message ç„ functionResponse parts
    pending_tool_parts = []

    def flush_pending_tool_parts():
        """å°†ç´¯ç§¯ç„ tool parts ä½œä¸ºå•ä¸ª contents æ¡ç›®è¿½å """
        nonlocal pending_tool_parts
        if pending_tool_parts:
            contents.append({
                "role": "user",
                "parts": pending_tool_parts
            })
            pending_tool_parts = []

    for message in messages:
        role = message.get("role", "user")
        content = message.get("content", "")

        # å¤„ç†å·¥å…·æ¶ˆæ¯ï¼ˆtool roleï¼‰- ç´¯ç§¯åˆ° pending_tool_parts
        if role == "tool":
            tool_call_id = message.get("tool_call_id", "")
            func_name = message.get("name")

            # ä½¿ç”¨æ˜ å°„è¡¨æŸ¥æ‰¾
            if tool_call_id in tool_call_mapping:
                func_name, original_id, _ = tool_call_mapping[tool_call_id]
            else:
                # å¦‚æœæ²¡æœ‰name,å°è¯•ä»æ¶ˆæ¯åˆ—è¡¨ä¸­æŸ¥æ‰¾
                if not func_name and tool_call_id:
                    for msg in messages:
                        if msg.get("role") == "assistant" and msg.get("tool_calls"):
                            for tc in msg["tool_calls"]:
                                if tc.get("id") == tool_call_id:
                                    func_name = tc.get("function", {}).get("name")
                                    break
                            if func_name:
                                break

                # è§£ç  tool_call_id è·å–åŸå§‹ ID
                original_id, _ = decode_tool_id_and_signature(tool_call_id)

            # æœ€ç»ˆå…œåº•ï¼ç¡®ä¿ func_name ä¸ä¸ºç©º
            if not func_name:
                func_name = "unknown_function"
                log.warning(f"Tool message missing function name for tool_call_id={tool_call_id}, using default: {func_name}")

            # è§£æå“åº”æ•°æ®
            try:
                response_data = json.loads(content) if isinstance(content, str) else content
            except (json.JSONDecodeError, TypeError):
                response_data = {"result": str(content)}

            # ç¡®ä¿ response_data æ˜¯å­—å…¸ç±»å‹ï¼ˆGemini API è¦æ±‚ response å¿…é¡»æ˜¯å¯¹è±¡ï¼‰
            if not isinstance(response_data, dict):
                response_data = {"result": response_data}

            # ç´¯ç§¯ functionResponse partï¼ˆä¸ç«‹å³è¿½å åˆ° contentsï¼‰
            pending_tool_parts.append({
                "functionResponse": {
                    "id": original_id,
                    "name": func_name,
                    "response": response_data
                }
            })
            continue

        # é‡åˆ°é tool æ¶ˆæ¯æ—¶ï¼Œå…ˆ flush ç´¯ç§¯ç„ tool parts
        flush_pending_tool_parts()

        # system æ¶ˆæ¯å·²ç»ç”± merge_system_messages å¤„ç†ï¼Œè¿™é‡Œè·³è¿‡
        if role == "system":
            continue

        # å°†OpenAIè§’è‰²æ˜ å°„åˆ°Geminiè§’è‰²
        if role == "assistant":
            role = "model"

        # æ£€æŸ¥æ˜¯å¦æœ‰tool_calls
        tool_calls = message.get("tool_calls")
        if tool_calls:
            parts = []

            # å¦‚æœæœ‰æ–‡æœ¬å†…å®¹,å…ˆæ·»å æ–‡æœ¬
            # æ³¨æ„: content å¯èƒ½æ˜¯ stră€listï¼ˆOpenAI content block æ ¼å¼ [{"type":"text","text":"..."}]ï¼‰ă€dict æˆ– None
            # å¿…é¡»è§£åŒ…ä¸ºçº¯å­—ç¬¦ä¸²ï¼Œå¦åˆ™ text å­—æ®µä¼å˜æˆ listï¼Œè§¦å‘ gemini_fix ç„ str(dict) äº§ç”ŸåµŒå¥—å­—ç¬¦ä¸²
            if content:
                if isinstance(content, list):
                    for _part in content:
                        if isinstance(_part, dict):
                            if _part.get("type") == "text" or "text" in _part:
                                _t = _part.get("text", "")
                                if _t:
                                    parts.append({"text": _t})
                        elif isinstance(_part, str) and _part:
                            parts.append({"text": _part})
                elif isinstance(content, str):
                    parts.append({"text": content})
                elif isinstance(content, dict):
                    _t = content.get("text", "")
                    if _t:
                        parts.append({"text": _t})
                else:
                    parts.append({"text": str(content)})

            # æ·»å æ¯ä¸ªå·¥å…·è°ƒç”¨
            for tool_call in tool_calls:
                try:
                    args = (
                        json.loads(tool_call["function"]["arguments"])
                        if isinstance(tool_call["function"]["arguments"], str)
                        else tool_call["function"]["arguments"]
                    )
                    
                    # æ ¹æ®å·¥å…·ç„ schema ä¿®æ­£å‚æ•°ç±»å‹
                    func_name = tool_call["function"]["name"]
                    if func_name in tool_schemas:
                        args = fix_tool_call_args_types(args, tool_schemas[func_name])

                    # è§£ç å·¥å…·IDå’ŒthoughtSignature
                    encoded_id = tool_call.get("id", "")
                    original_id, signature = decode_tool_id_and_signature(encoded_id)

                    # æ„å»ºfunctionCall part
                    function_call_part = {
                        "functionCall": {
                            "id": original_id,
                            "name": func_name,
                            "args": args
                        }
                    }

                    # OpenAI/RooCode ä¸­è½¬å¯èƒ½ä¼æ”¹å†™æˆ–æˆªæ–­ tool_call_idï¼ŒçœŸå®ç­¾åå›ä¼ åå®¹æ˜“è§¦å‘
                    # Corrupted thought signatureă€‚å·¥å…·è°ƒç”¨ä½¿ç”¨å®˜æ–¹è·³è¿‡æ ¡éªŒå ä½ç¬¦æ›´ç¨³ă€‚
                    function_call_part["thoughtSignature"] = SKIP_THOUGHT_SIGNATURE_VALIDATOR

                    parts.append(function_call_part)
                except (json.JSONDecodeError, KeyError) as e:
                    log.error(f"Failed to parse tool call: {e}")
                    continue

            if parts:
                contents.append({"role": role, "parts": parts})
            continue

        # å¤„ç†æ™®é€å†…å®¹
        if isinstance(content, list):
            parts = []
            for part in content:
                if part.get("type") == "text":
                    parts.append({"text": part.get("text", "")})
                elif part.get("type") == "image_url":
                    image_url = part.get("image_url", {}).get("url")
                    if image_url:
                        try:
                            mime_type, base64_data = image_url.split(";")
                            _, mime_type = mime_type.split(":")
                            _, base64_data = base64_data.split(",")
                            parts.append({
                                "inlineData": {
                                    "mimeType": mime_type,
                                    "data": base64_data,
                                }
                            })
                        except ValueError:
                            continue
            if parts:
                contents.append({"role": role, "parts": parts})
        elif content:
            contents.append({"role": role, "parts": [{"text": content}]})

    # å¾ªç¯ç»“æŸåï¼Œflush å‰©ä½™ç„ tool partsï¼ˆå¦‚æœæ¶ˆæ¯åˆ—è¡¨ä»¥ tool æ¶ˆæ¯ç»“å°¾ï¼‰
    flush_pending_tool_parts()
    _sanitize_openai_roundtrip_signatures(contents)

    # æ„å»ºç”Ÿæˆé…ç½®
    generation_config = {}
    model = openai_request.get("model", "")
    
    # åŸºç¡€å‚æ•°æ˜ å°„
    if "temperature" in openai_request:
        generation_config["temperature"] = openai_request["temperature"]
    if "top_p" in openai_request:
        generation_config["topP"] = openai_request["top_p"]
    if "top_k" in openai_request:
        generation_config["topK"] = openai_request["top_k"]
    if "max_tokens" in openai_request or "max_completion_tokens" in openai_request:
        # max_completion_tokens ä¼˜å…ˆäº max_tokens
        max_tokens = openai_request.get("max_completion_tokens") or openai_request.get("max_tokens")
        generation_config["maxOutputTokens"] = max_tokens
    if "stop" in openai_request:
        stop = openai_request["stop"]
        generation_config["stopSequences"] = [stop] if isinstance(stop, str) else stop
    if "frequency_penalty" in openai_request:
        generation_config["frequencyPenalty"] = openai_request["frequency_penalty"]
    if "presence_penalty" in openai_request:
        generation_config["presencePenalty"] = openai_request["presence_penalty"]
    if "n" in openai_request:
        generation_config["candidateCount"] = openai_request["n"]
    if "seed" in openai_request:
        generation_config["seed"] = openai_request["seed"]
    
    # å¤„ç† response_format
    if "response_format" in openai_request and openai_request["response_format"]:
        response_format = openai_request["response_format"]
        format_type = response_format.get("type")
        
        if format_type == "json_schema":
            # JSON Schema æ¨¡å¼
            if "json_schema" in response_format and "schema" in response_format["json_schema"]:
                schema = response_format["json_schema"]["schema"]
                # æ¸…ç† schema
                generation_config["responseSchema"] = _clean_schema_for_gemini(schema)
                generation_config["responseMimeType"] = "application/json"
        elif format_type == "json_object":
            # JSON Object æ¨¡å¼
            generation_config["responseMimeType"] = "application/json"
        elif format_type == "text":
            # Text æ¨¡å¼
            generation_config["responseMimeType"] = "text/plain"
            
    # å¦‚æœcontentsä¸ºç©º,æ·»å é»˜è®¤ç”¨æˆ·æ¶ˆæ¯
    if not contents:
        contents.append({"role": "user", "parts": [{"text": "è¯·æ ¹æ®ç³»ç»ŸæŒ‡ä»¤å›ç­”ă€‚"}]})

    # æ„å»ºåŸºç¡€è¯·æ±‚
    gemini_request = {
        "contents": contents,
        "generationConfig": generation_config
    }

    # å¦‚æœ merge_system_messages å·²ç»æ·»å äº† systemInstructionï¼Œä½¿ç”¨å®ƒ
    if "systemInstruction" in openai_request:
        gemini_request["systemInstruction"] = openai_request["systemInstruction"]

    # å¤„ç†å·¥å…· - ä¼ é€’ model å‚æ•°ä»¥ä¾¿æ ¹æ®æ¨¡å‹ç±»å‹é€‰æ‹©æ¸…ç†ç­–ç•¥
    model = openai_request.get("model", "")
    if "tools" in openai_request and openai_request["tools"]:
        gemini_request["tools"] = convert_openai_tools_to_gemini(openai_request["tools"], model)

    # å¤„ç†tool_choice
    if "tool_choice" in openai_request and openai_request["tool_choice"]:
        gemini_request["toolConfig"] = convert_tool_choice_to_tool_config(openai_request["tool_choice"])

    # é€ä¼ å›¾ç‰‡ç”Ÿæˆç„ size å‚æ•°ï¼ˆå¦‚ "1024x1536"ï¼‰
    if "size" in openai_request and openai_request["size"]:
        gemini_request["size"] = openai_request["size"]

    return gemini_request


def convert_gemini_to_openai_response(
    gemini_response: Union[Dict[str, Any], Any],
    model: str,
    status_code: int = 200
) -> Dict[str, Any]:
    """
    å°† Gemini æ ¼å¼éæµå¼å“åº”è½¬æ¢ä¸º OpenAI æ ¼å¼éæµå¼å“åº”

    æ³¨æ„: å¦‚æœæ”¶åˆ°ç„ä¸æ˜¯ 200 å¼€å¤´ç„å“åº”,ä¸åä»»ä½•å¤„ç†,ç›´æ¥è½¬å‘åŸå§‹å“åº”

    Args:
        gemini_response: Gemini æ ¼å¼ç„å“åº”ä½“ (å­—å…¸æˆ–å“åº”å¯¹è±¡)
        model: æ¨¡å‹åç§°
        status_code: HTTP ç¶æ€ç  (é»˜è®¤ 200)

    Returns:
        OpenAI æ ¼å¼ç„å“åº”ä½“å­—å…¸,æˆ–åŸå§‹å“åº” (å¦‚æœç¶æ€ç ä¸æ˜¯ 2xx)
    """
    # é 2xx ç¶æ€ç ç›´æ¥è¿”å›åŸå§‹å“åº”
    if not (200 <= status_code < 300):
        if isinstance(gemini_response, dict):
            return gemini_response
        else:
            # å¦‚æœæ˜¯å“åº”å¯¹è±¡,å°è¯•è§£æä¸ºå­—å…¸
            try:
                if hasattr(gemini_response, "json"):
                    return gemini_response.json()
                elif hasattr(gemini_response, "body"):
                    body = gemini_response.body
                    if isinstance(body, bytes):
                        return json.loads(body.decode())
                    return json.loads(str(body))
                else:
                    return {"error": str(gemini_response)}
            except Exception:
                return {"error": str(gemini_response)}

    # ç¡®ä¿æ˜¯å­—å…¸æ ¼å¼
    if not isinstance(gemini_response, dict):
        try:
            if hasattr(gemini_response, "json"):
                gemini_response = gemini_response.json()
            elif hasattr(gemini_response, "body"):
                body = gemini_response.body
                if isinstance(body, bytes):
                    gemini_response = json.loads(body.decode())
                else:
                    gemini_response = json.loads(str(body))
            else:
                gemini_response = json.loads(str(gemini_response))
        except Exception:
            return {"error": "Invalid response format"}

    # å¤„ç† Code Assist ç„ response åŒ…è£…æ ¼å¼
    if "response" in gemini_response:
        gemini_response = gemini_response["response"]

    # è½¬æ¢ä¸º OpenAI æ ¼å¼
    choices = []

    for candidate in gemini_response.get("candidates", []):
        role = candidate.get("content", {}).get("role", "assistant")

        # å°†Geminiè§’è‰²æ˜ å°„å›OpenAIè§’è‰²
        if role == "model":
            role = "assistant"

        # æå–å¹¶åˆ†ç¦»thinking tokenså’Œå¸¸è§„å†…å®¹
        parts = candidate.get("content", {}).get("parts", [])

        # æå–å·¥å…·è°ƒç”¨å’Œæ–‡æœ¬å†…å®¹
        tool_calls, text_content = extract_tool_calls_from_parts(parts)

        # æå–å¤ç§ç±»å‹ç„å†…å®¹
        content_parts = []
        reasoning_parts = []
        
        for part in parts:
            # å¤„ç† executableCodeï¼ˆä»£ç ç”Ÿæˆï¼‰
            if "executableCode" in part:
                exec_code = part["executableCode"]
                lang = exec_code.get("language", "python").lower()
                code = exec_code.get("code", "")
                # æ·»å ä»£ç å—ï¼ˆå‰åå æ¢è¡Œç¬¦ç¡®ä¿ Markdown æ¸²æŸ“æ­£ç¡®ï¼‰
                content_parts.append(f"\n```{lang}\n{code}\n```\n")
            
            # å¤„ç† codeExecutionResultï¼ˆä»£ç æ‰§è¡Œç»“æœï¼‰
            elif "codeExecutionResult" in part:
                result = part["codeExecutionResult"]
                outcome = result.get("outcome")
                output = result.get("output", "")
                
                if output:
                    label = "output" if outcome == "OUTCOME_OK" else "error"
                    content_parts.append(f"\n```{label}\n{output}\n```\n")
            
            # å¤„ç† thoughtï¼ˆæ€è€ƒå†…å®¹ï¼‰
            elif (
                part.get("thought", False)
                and "text" in part
                and not is_skip_thought_signature_placeholder(part)
            ):
                reasoning_parts.append(part["text"])
            
            # å¤„ç†æ™®é€æ–‡æœ¬ï¼ˆéæ€è€ƒå†…å®¹ï¼‰
            elif "text" in part and not part.get("thought", False):
                # è¿™éƒ¨åˆ†å·²ç»åœ¨ extract_tool_calls_from_parts ä¸­å¤„ç†
                pass
            
            # å¤„ç† inlineDataï¼ˆå›¾ç‰‡ï¼‰
            elif "inlineData" in part:
                inline_data = part["inlineData"]
                mime_type = inline_data.get("mimeType", "image/png")
                base64_data = inline_data.get("data", "")
                # ä½¿ç”¨ Markdown æ ¼å¼
                content_parts.append(f"![gemini-generated-content](data:{mime_type};base64,{base64_data})")
        
        # åˆå¹¶æ‰€æœ‰å†…å®¹éƒ¨åˆ†
        if content_parts:
            # ä½¿ç”¨åŒæ¢è¡Œç¬¦è¿æ¥å„éƒ¨åˆ†ï¼Œç¡®ä¿å—ä¹‹é—´æœ‰é—´è·
            additional_content = "\n\n".join(content_parts)
            if text_content:
                text_content = text_content + "\n\n" + additional_content
            else:
                text_content = additional_content
        
        # åˆå¹¶ reasoning content
        reasoning_content = "\n\n".join(reasoning_parts) if reasoning_parts else ""

        # æ„å»ºæ¶ˆæ¯å¯¹è±¡
        message = {"role": role}

        # è·å– Gemini ç„ finishReason
        gemini_finish_reason = candidate.get("finishReason")
        
        # å¦‚æœæœ‰å·¥å…·è°ƒç”¨
        if tool_calls:
            message["tool_calls"] = tool_calls
            message["content"] = text_content if text_content else None
            # åªæœ‰åœ¨æ­£å¸¸åœæ­¢ï¼ˆSTOPï¼‰æ—¶æ‰è®¾ä¸º tool_callsï¼Œå…¶ä»–æƒ…å†µä¿æŒåŸå§‹ finish_reason
            # è¿™æ ·å¯ä»¥é¿å…åœ¨ SAFETYă€MAX_TOKENS ç­‰æƒ…å†µä¸‹ä»ç„¶è¿”å› tool_calls å¯¼è‡´å¾ªç¯
            if gemini_finish_reason == "STOP":
                finish_reason = "tool_calls"
            else:
                finish_reason = _map_finish_reason(gemini_finish_reason)
        else:
            message["content"] = text_content
            finish_reason = _map_finish_reason(gemini_finish_reason)

        # æ·»å  reasoning content (å¦‚æœæœ‰)
        if reasoning_content:
            message["reasoning_content"] = reasoning_content

        choices.append({
            "index": candidate.get("index", 0),
            "message": message,
            "finish_reason": finish_reason,
        })

    # è½¬æ¢ usageMetadata
    usage = _convert_usage_metadata(gemini_response.get("usageMetadata"))

    response_data = {
        "id": str(uuid.uuid4()),
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": choices,
    }

    if usage:
        response_data["usage"] = usage

    return response_data


def convert_gemini_to_openai_stream(
    gemini_stream_chunk: str,
    model: str,
    response_id: str,
    status_code: int = 200
) -> Optional[str]:
    """
    å°† Gemini æ ¼å¼æµå¼å“åº”å—è½¬æ¢ä¸º OpenAI SSE æ ¼å¼æµå¼å“åº”

    æ³¨æ„: å¦‚æœæ”¶åˆ°ç„ä¸æ˜¯ 200 å¼€å¤´ç„å“åº”,ä¸åä»»ä½•å¤„ç†,ç›´æ¥è½¬å‘åŸå§‹å†…å®¹

    Args:
        gemini_stream_chunk: Gemini æ ¼å¼ç„æµå¼å“åº”å— (å­—ç¬¦ä¸²,é€å¸¸æ˜¯ "data: {json}" æ ¼å¼)
        model: æ¨¡å‹åç§°
        response_id: æ­¤æµå¼å“åº”ç„ä¸€è‡´ID
        status_code: HTTP ç¶æ€ç  (é»˜è®¤ 200)

    Returns:
        OpenAI SSE æ ¼å¼ç„å“åº”å­—ç¬¦ä¸² (å¦‚ "data: {json}\n\n"),
        æˆ–åŸå§‹å†…å®¹ (å¦‚æœç¶æ€ç ä¸æ˜¯ 2xx),
        æˆ– None (å¦‚æœè§£æå¤±è´¥)
    """
    # é 2xx ç¶æ€ç ç›´æ¥è¿”å›åŸå§‹å†…å®¹
    if not (200 <= status_code < 300):
        return gemini_stream_chunk

    # è§£æ Gemini æµå¼å—
    try:
        # å»é™¤ "data: " å‰ç¼€
        if isinstance(gemini_stream_chunk, bytes):
            if gemini_stream_chunk.startswith(b"data: "):
                payload_str = gemini_stream_chunk[len(b"data: "):].strip().decode("utf-8")
            else:
                payload_str = gemini_stream_chunk.strip().decode("utf-8")
        else:
            if gemini_stream_chunk.startswith("data: "):
                payload_str = gemini_stream_chunk[len("data: "):].strip()
            else:
                payload_str = gemini_stream_chunk.strip()

        # è·³è¿‡ç©ºå—
        if not payload_str:
            return None

        # è§£æ JSON
        gemini_chunk = json.loads(payload_str)
    except (json.JSONDecodeError, UnicodeDecodeError):
        # è§£æå¤±è´¥,è·³è¿‡æ­¤å—
        return None

    # å¤„ç† Code Assist ç„ response åŒ…è£…æ ¼å¼
    if "response" in gemini_chunk:
        gemini_response = gemini_chunk["response"]
    else:
        gemini_response = gemini_chunk

    # è½¬æ¢ä¸º OpenAI æµå¼æ ¼å¼
    choices = []

    for candidate in gemini_response.get("candidates", []):
        role = candidate.get("content", {}).get("role", "assistant")

        # å°†Geminiè§’è‰²æ˜ å°„å›OpenAIè§’è‰²
        if role == "model":
            role = "assistant"

        # æå–å¹¶åˆ†ç¦»thinking tokenså’Œå¸¸è§„å†…å®¹
        parts = candidate.get("content", {}).get("parts", [])

        # æå–å·¥å…·è°ƒç”¨å’Œæ–‡æœ¬å†…å®¹ (æµå¼éœ€è¦ index)
        tool_calls, text_content = extract_tool_calls_from_parts(parts, is_streaming=True)

        # æå–å¤ç§ç±»å‹ç„å†…å®¹
        content_parts = []
        reasoning_parts = []
        
        for part in parts:
            # å¤„ç† executableCodeï¼ˆä»£ç ç”Ÿæˆï¼‰
            if "executableCode" in part:
                exec_code = part["executableCode"]
                lang = exec_code.get("language", "python").lower()
                code = exec_code.get("code", "")
                content_parts.append(f"\n```{lang}\n{code}\n```\n")
            
            # å¤„ç† codeExecutionResultï¼ˆä»£ç æ‰§è¡Œç»“æœï¼‰
            elif "codeExecutionResult" in part:
                result = part["codeExecutionResult"]
                outcome = result.get("outcome")
                output = result.get("output", "")
                
                if output:
                    label = "output" if outcome == "OUTCOME_OK" else "error"
                    content_parts.append(f"\n```{label}\n{output}\n```\n")
            
            # å¤„ç† thoughtï¼ˆæ€è€ƒå†…å®¹ï¼‰
            elif (
                part.get("thought", False)
                and "text" in part
                and not is_skip_thought_signature_placeholder(part)
            ):
                reasoning_parts.append(part["text"])
            
            # å¤„ç†æ™®é€æ–‡æœ¬ï¼ˆéæ€è€ƒå†…å®¹ï¼‰
            elif "text" in part and not part.get("thought", False):
                # è¿™éƒ¨åˆ†å·²ç»åœ¨ extract_tool_calls_from_parts ä¸­å¤„ç†
                pass
            
            # å¤„ç† inlineDataï¼ˆå›¾ç‰‡ï¼‰
            elif "inlineData" in part:
                inline_data = part["inlineData"]
                mime_type = inline_data.get("mimeType", "image/png")
                base64_data = inline_data.get("data", "")
                content_parts.append(f"![gemini-generated-content](data:{mime_type};base64,{base64_data})")
        
        # åˆå¹¶æ‰€æœ‰å†…å®¹éƒ¨åˆ†
        if content_parts:
            additional_content = "\n\n".join(content_parts)
            if text_content:
                text_content = text_content + "\n\n" + additional_content
            else:
                text_content = additional_content
        
        # åˆå¹¶ reasoning content
        reasoning_content = "\n\n".join(reasoning_parts) if reasoning_parts else ""

        # æ„å»º delta å¯¹è±¡
        delta = {}

        if tool_calls:
            delta["tool_calls"] = tool_calls
            if text_content:
                delta["content"] = text_content
        elif text_content:
            delta["content"] = text_content

        if reasoning_content:
            delta["reasoning_content"] = reasoning_content

        # è·å– Gemini ç„ finishReason
        gemini_finish_reason = candidate.get("finishReason")
        finish_reason = _map_finish_reason(gemini_finish_reason)
        
        # åªæœ‰åœ¨æ­£å¸¸åœæ­¢ï¼ˆSTOPï¼‰ä¸”æœ‰å·¥å…·è°ƒç”¨æ—¶æ‰è®¾ä¸º tool_calls
        # é¿å…åœ¨ SAFETYă€MAX_TOKENS ç­‰æƒ…å†µä¸‹ä»ç„¶è¿”å› tool_calls å¯¼è‡´å¾ªç¯
        if tool_calls and gemini_finish_reason == "STOP":
            finish_reason = "tool_calls"

        choices.append({
            "index": candidate.get("index", 0),
            "delta": delta,
            "finish_reason": finish_reason,
        })

    # è½¬æ¢ usageMetadata (åªåœ¨æµç»“æŸæ—¶å­˜åœ¨)
    usage = _convert_usage_metadata(gemini_response.get("usageMetadata"))

    # æ„å»º OpenAI æµå¼å“åº”
    response_data = {
        "id": response_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": choices,
    }

    # åªåœ¨æœ‰ usage æ•°æ®ä¸”æœ‰ finish_reason æ—¶æ·»å  usage
    if usage:
        has_finish_reason = any(choice.get("finish_reason") for choice in choices)
        if has_finish_reason:
            response_data["usage"] = usage

    # è½¬æ¢ä¸º SSE æ ¼å¼: "data: {json}\n\n"
    return f"data: {json.dumps(response_data)}\n\n"
