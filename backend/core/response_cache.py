"""Response Caching Layer for Omni Gateway.

Provides fast exact-match lookup for LLM responses to reduce latency,
save provider quota, and avoid duplicate API calls.
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple


def generate_cache_key(
    model: str,
    payload: Dict[str, Any],
    stream: bool = False,
) -> str:
    """Generate a deterministic SHA-256 hash key for a given request payload."""
    normalized_data = {
        "model": str(model).strip().lower(),
        "stream": bool(stream),
        "messages": payload.get("messages", []),
        "contents": payload.get("contents", []),
        "prompt": payload.get("prompt", ""),
        "system_instruction": payload.get("system_instruction")
        or payload.get("systemInstruction"),
        "temperature": payload.get("temperature"),
        "top_p": payload.get("top_p"),
        "max_tokens": payload.get("max_tokens") or payload.get("max_output_tokens"),
        "generation_config": payload.get("generationConfig"),
        "tools": payload.get("tools"),
    }

    # Dump deterministically sorted JSON string
    serialized = json.dumps(normalized_data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class ResponseCache:
    """In-memory cache with TTL and LRU expiration."""

    def __init__(self, default_ttl_seconds: int = 3600, max_entries: int = 1000) -> None:
        self.default_ttl_seconds = max(1, default_ttl_seconds)
        self.max_entries = max(1, max_entries)
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Any]:
        """Retrieve a cached response if valid and unexpired."""
        if key not in self._cache:
            self.misses += 1
            return None

        expires_at, data = self._cache[key]
        if time.time() > expires_at:
            self._cache.pop(key, None)
            self.misses += 1
            return None
        self.hits += 1
        return data

    def set(self, key: str, data: Any, ttl_seconds: Optional[int] = None) -> None:
        """Store a response in cache with TTL."""
        ttl = (
            ttl_seconds
            if (ttl_seconds is not None and ttl_seconds > 0)
            else self.default_ttl_seconds
        )
        expires_at = time.time() + ttl

        # Evict oldest entry if capacity is reached
        if len(self._cache) >= self.max_entries and key not in self._cache:
            first_key = next(iter(self._cache))
            self._cache.pop(first_key, None)

        self._cache[key] = (expires_at, data)

    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()

    def size(self) -> int:
        """Return the count of unexpired items."""
        now = time.time()
        # Clean expired
        expired = [k for k, (exp, _) in self._cache.items() if now > exp]
        for k in expired:
            self._cache.pop(k, None)
        return len(self._cache)


# Global singleton instance
response_cache = ResponseCache()
