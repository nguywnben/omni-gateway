"""Request-scoped metadata for safe routing and usage telemetry."""

from __future__ import annotations

import time
from contextlib import contextmanager
from contextvars import ContextVar, Token
from typing import Iterator

_request_id: ContextVar[str] = ContextVar("request_id", default="")
_request_started_at: ContextVar[float] = ContextVar("request_started_at", default=0.0)
_api_key_id: ContextVar[str] = ContextVar("api_key_id", default="")


@contextmanager
def request_scope(request_id: str) -> Iterator[None]:
    """Attach a sanitized request ID to work performed in this async context."""
    request_token: Token[str] = _request_id.set(str(request_id or ""))
    start_token: Token[float] = _request_started_at.set(time.perf_counter())
    api_key_token: Token[str] = _api_key_id.set("")
    try:
        yield
    finally:
        _api_key_id.reset(api_key_token)
        _request_id.reset(request_token)
        _request_started_at.reset(start_token)


def get_request_id() -> str:
    return _request_id.get()


def get_request_elapsed_ms() -> int:
    started_at = _request_started_at.get()
    if not started_at:
        return 0
    return max(0, round((time.perf_counter() - started_at) * 1000))


def set_api_key_id(api_key_id: str) -> None:
    """Attribute the current request to a virtual API key for the ledger."""
    _api_key_id.set(str(api_key_id or ""))


def get_api_key_id() -> str:
    return _api_key_id.get()
