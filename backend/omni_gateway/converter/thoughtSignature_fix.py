"""
thoughtSignature å¤„ç†å…¬å…±æ¨¡å—

æä¾›ç»Ÿä¸€ç„ thoughtSignature ç¼–ç /è§£ç åŸèƒ½ï¼Œç”¨äºåœ¨å·¥å…·è°ƒç”¨IDä¸­ä¿ç•™ç­¾åä¿¡æ¯ă€‚
è¿™ä½¿å¾—ç­¾åèƒ½å¤Ÿåœ¨å®¢æˆ·ç«¯å¾€è¿”ä¼ è¾“ä¸­ä¿ç•™ï¼Œå³ä½¿å®¢æˆ·ç«¯ä¼åˆ é™¤è‡ªå®ä¹‰å­—æ®µă€‚
"""

from typing import Any, Mapping, Optional, Tuple

# åœ¨å·¥å…·è°ƒç”¨IDä¸­åµŒå…¥thoughtSignatureç„åˆ†é”ç¬¦
# è¿™ä½¿å¾—ç­¾åèƒ½å¤Ÿåœ¨å®¢æˆ·ç«¯å¾€è¿”ä¼ è¾“ä¸­ä¿ç•™ï¼Œå³ä½¿å®¢æˆ·ç«¯ä¼åˆ é™¤è‡ªå®ä¹‰å­—æ®µ
THOUGHT_SIGNATURE_SEPARATOR = "__thought__"
SKIP_THOUGHT_SIGNATURE_VALIDATOR = "skip_thought_signature_validator"
SKIP_THOUGHT_SIGNATURE_PLACEHOLDER_TEXT = "..."


def is_internal_placeholder_text(text: Any) -> bool:
    if not isinstance(text, str):
        return False
    return text.strip() in (SKIP_THOUGHT_SIGNATURE_PLACEHOLDER_TEXT, "â€¦")


def is_skip_thought_signature_placeholder(part: Mapping[str, Any]) -> bool:
    """Return True for the internal placeholder that should not reach clients."""
    if not isinstance(part, Mapping):
        return False
    if part.get("thoughtSignature") != SKIP_THOUGHT_SIGNATURE_VALIDATOR:
        return False
    if "functionCall" in part or "function_call" in part or "functionResponse" in part:
        return False
    return is_internal_placeholder_text(part.get("text"))


def encode_tool_id_with_signature(tool_id: str, signature: Optional[str]) -> str:
    """
    å°† thoughtSignature ç¼–ç åˆ°å·¥å…·è°ƒç”¨IDä¸­ï¼Œä»¥ä¾¿å¾€è¿”ä¿ç•™ă€‚

    Args:
        tool_id: åŸå§‹å·¥å…·è°ƒç”¨ID
        signature: thoughtSignatureï¼ˆå¯é€‰ï¼‰

    Returns:
        ç¼–ç åç„å·¥å…·è°ƒç”¨ID

    Examples:
        >>> encode_tool_id_with_signature("call_123", "abc")
        'call_123__thought__abc'
        >>> encode_tool_id_with_signature("call_123", None)
        'call_123'
    """
    if not signature:
        return tool_id
    return f"{tool_id}{THOUGHT_SIGNATURE_SEPARATOR}{signature}"


def decode_tool_id_and_signature(encoded_id: str) -> Tuple[str, Optional[str]]:
    """
    ä»ç¼–ç ç„IDä¸­æå–åŸå§‹å·¥å…·IDå’ŒthoughtSignatureă€‚

    Args:
        encoded_id: ç¼–ç ç„å·¥å…·è°ƒç”¨ID

    Returns:
        (åŸå§‹å·¥å…·ID, thoughtSignature) å…ƒç»„

    Examples:
        >>> decode_tool_id_and_signature("call_123__thought__abc")
        ('call_123', 'abc')
        >>> decode_tool_id_and_signature("call_123")
        ('call_123', None)
    """
    if not encoded_id or THOUGHT_SIGNATURE_SEPARATOR not in encoded_id:
        return encoded_id, None
    parts = encoded_id.split(THOUGHT_SIGNATURE_SEPARATOR, 1)
    return parts[0], parts[1] if len(parts) == 2 else None
