"""Bounded, secret-free planning state for credential batch operations."""

from __future__ import annotations

import hashlib
import json
import secrets
import threading
import time
from collections import OrderedDict
from typing import Any

from core.credential_validation import validate_credential_filename
from core.provider_registry import (
    credential_supports_operation,
    get_credential_provider_variant,
    get_credential_variant_capabilities,
)
from fastapi import HTTPException

BATCH_ACTION_OPERATIONS = {
    "enable": "toggle",
    "disable": "toggle",
    "delete": "delete",
    "enable_credit": "credit_mode",
    "disable_credit": "credit_mode",
}
BATCH_HIGH_VOLUME_THRESHOLD = 20
BATCH_ITEM_TIMEOUT_SECONDS = 5.0
BATCH_PREVIEW_TTL_SECONDS = 300
MAX_BATCH_STATE_ENTRIES = 256

_preview_cache: OrderedDict[str, tuple[str, float]] = OrderedDict()
_idempotency_cache: OrderedDict[str, tuple[str, int, dict[str, Any]]] = OrderedDict()
_idempotency_pending: dict[str, str] = {}
_state_lock = threading.RLock()


def batch_request_fingerprint(mode: str, action: str, filenames: list[str]) -> str:
    """Return a deterministic digest without retaining target names in coordination state."""
    serialized = json.dumps(
        {"mode": mode, "action": action, "filenames": filenames},
        ensure_ascii=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def batch_requires_preview(action: str, target_count: int) -> bool:
    return action == "delete" or target_count >= BATCH_HIGH_VOLUME_THRESHOLD


def issue_batch_preview(fingerprint: str) -> str:
    with _state_lock:
        now = time.monotonic()
        _prune_state(now)
        token = secrets.token_urlsafe(32)
        _preview_cache[token] = (fingerprint, now + BATCH_PREVIEW_TTL_SECONDS)
        _trim_state(_preview_cache)
        return token


def preview_matches(token: str | None, fingerprint: str) -> bool:
    if not token:
        return False
    with _state_lock:
        now = time.monotonic()
        _prune_state(now)
        preview = _preview_cache.get(token)
        if not preview:
            return False
        stored_fingerprint, expires_at = preview
        return expires_at > now and secrets.compare_digest(stored_fingerprint, fingerprint)


def get_idempotent_response(
    key: str | None,
    fingerprint: str,
    *,
    reserve: bool = False,
) -> tuple[int, dict[str, Any]] | None:
    if not key:
        return None
    with _state_lock:
        cached = _idempotency_cache.get(key)
        if cached:
            stored_fingerprint, status_code, body = cached
            if not secrets.compare_digest(stored_fingerprint, fingerprint):
                raise HTTPException(
                    status_code=409,
                    detail="The idempotency key is already bound to another batch request.",
                )
            _idempotency_cache.move_to_end(key)
            return status_code, body

        if not reserve:
            return None
        pending_fingerprint = _idempotency_pending.get(key)
        if pending_fingerprint:
            if not secrets.compare_digest(pending_fingerprint, fingerprint):
                detail = "The idempotency key is already bound to another batch request."
            else:
                detail = "The batch request for this idempotency key is still in progress."
            raise HTTPException(status_code=409, detail=detail)
        if len(_idempotency_pending) >= MAX_BATCH_STATE_ENTRIES:
            raise HTTPException(
                status_code=429,
                detail="Too many credential batches are currently in progress.",
            )
        _idempotency_pending[key] = fingerprint
        return None


def store_idempotent_response(
    key: str | None,
    fingerprint: str,
    status_code: int,
    body: dict[str, Any],
) -> None:
    if not key:
        return
    with _state_lock:
        _idempotency_pending.pop(key, None)
        _idempotency_cache[key] = (fingerprint, status_code, body)
        _idempotency_cache.move_to_end(key)
        _trim_state(_idempotency_cache)


def release_idempotency_reservation(key: str | None, fingerprint: str) -> None:
    if not key:
        return
    with _state_lock:
        pending_fingerprint = _idempotency_pending.get(key)
        if pending_fingerprint and secrets.compare_digest(pending_fingerprint, fingerprint):
            _idempotency_pending.pop(key, None)


async def build_batch_plan(
    storage_adapter: Any,
    action: str,
    filenames: list[str],
    *,
    mode: str,
) -> list[dict[str, Any]]:
    """Re-evaluate targets and capabilities without mutating credential state."""
    operation = BATCH_ACTION_OPERATIONS[action]
    results: list[dict[str, Any]] = []
    seen: set[str] = set()

    for target_index, raw_filename in enumerate(filenames):
        try:
            filename = validate_credential_filename(raw_filename)
        except HTTPException:
            results.append(_plan_item(target_index, None, operation, "invalid", "invalid_filename"))
            continue

        if filename in seen:
            results.append(
                _plan_item(target_index, filename, operation, "duplicate", "duplicate_target")
            )
            continue
        seen.add(filename)

        credential_data = await storage_adapter.get_credential(filename, mode=mode)
        if not credential_data:
            results.append(
                _plan_item(target_index, filename, operation, "not_found", "credential_not_found")
            )
            continue

        inferred_variant = get_credential_provider_variant(credential_data)
        capabilities = get_credential_variant_capabilities(inferred_variant)
        variant_id = capabilities.variant_id if capabilities else "unknown"
        operation_unsupported = (operation == "credit_mode" and mode != "primary") or (
            mode == "primary" and not credential_supports_operation(credential_data, operation)
        )
        if operation_unsupported:
            results.append(
                _plan_item(
                    target_index,
                    filename,
                    operation,
                    "unsupported",
                    "credential_operation_unsupported",
                    variant_id,
                )
            )
            continue

        item = _plan_item(target_index, filename, operation, "eligible", "eligible", variant_id)
        item["credential_data"] = credential_data
        results.append(item)

    return results


def public_batch_plan(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {key: value for key, value in item.items() if key != "credential_data"} for item in results
    ]


def _plan_item(
    target_index: int,
    filename: str | None,
    operation: str,
    status: str,
    code: str,
    variant_id: str = "unknown",
) -> dict[str, Any]:
    return {
        "target_index": target_index,
        "filename": filename,
        "variant_id": variant_id,
        "operation": operation,
        "status": status,
        "code": code,
    }


def _prune_state(now: float) -> None:
    expired = [token for token, (_, expires_at) in _preview_cache.items() if expires_at <= now]
    for token in expired:
        _preview_cache.pop(token, None)


def _trim_state(cache: OrderedDict) -> None:
    while len(cache) > MAX_BATCH_STATE_ENTRIES:
        cache.popitem(last=False)
