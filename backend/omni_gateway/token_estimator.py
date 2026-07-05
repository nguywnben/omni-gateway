"""ç®€å•ç„ token ä¼°ç®—ï¼Œä¸è¿½æ±‚ç²¾ç¡®"""
from __future__ import annotations

from typing import Any, Dict


def estimate_input_tokens(payload: Dict[str, Any]) -> int:
    """ç²—ç•¥ä¼°ç®— token æ•°ï¼å­—ç¬¦æ•° / 4 + å›¾ç‰‡å›ºå®å€¼"""
    total_chars = 0
    image_count = 0

    # ç»Ÿè®¡æ‰€æœ‰æ–‡æœ¬å­—ç¬¦
    def count_str(obj: Any) -> None:
        nonlocal total_chars, image_count
        if isinstance(obj, str):
            total_chars += len(obj)
        elif isinstance(obj, dict):
            # æ£€æµ‹å›¾ç‰‡
            if obj.get("type") == "image" or "inlineData" in obj:
                image_count += 1
            for v in obj.values():
                count_str(v)
        elif isinstance(obj, list):
            for item in obj:
                count_str(item)

    count_str(payload)

    # ç²—ç•¥ä¼°ç®—ï¼å­—ç¬¦æ•°/4 + æ¯å¼ å›¾ç‰‡300 tokens
    return max(1, total_chars // 4 + image_count * 300)
