"""Persistent route exclusions learned from upstream model-not-found responses."""

from __future__ import annotations

import asyncio
import math
import time
from typing import Any, Optional

from core.model_pool import ModelPoolError, normalize_model_id
from core.provider_registry import normalize_provider_id
from core.storage_adapter import get_storage_adapter

MODEL_BLACKLIST_CONFIG_KEY = "model_route_blacklist"
MAX_MODEL_BLACKLIST_ENTRIES = 512
_write_lock = asyncio.Lock()


def _normalize_timestamp(value: Any) -> float:
    try:
        timestamp = float(value)
    except (TypeError, ValueError):
        return 0.0
    return timestamp if math.isfinite(timestamp) and timestamp >= 0 else 0.0


def _normalize_credential_name(value: Any) -> str:
    basename = str(value or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    return basename[:255]


def _normalize_entry(value: Any) -> Optional[dict[str, Any]]:
    if not isinstance(value, dict):
        return None
    provider_id = normalize_provider_id(value.get("provider_id"))
    if not provider_id:
        return None
    try:
        model_id = normalize_model_id(value.get("model_id"))
    except ModelPoolError:
        return None

    first_seen_at = _normalize_timestamp(value.get("first_seen_at"))
    last_seen_at = max(first_seen_at, _normalize_timestamp(value.get("last_seen_at")))
    try:
        failure_count = max(1, int(value.get("failure_count") or 1))
    except (TypeError, ValueError):
        failure_count = 1
    entry = {
        "provider_id": provider_id,
        "model_id": model_id,
        "status_code": 404,
        "failure_count": failure_count,
        "first_seen_at": first_seen_at,
        "last_seen_at": last_seen_at,
    }
    credential_name = _normalize_credential_name(value.get("credential_name"))
    if credential_name:
        entry["credential_name"] = credential_name
    return entry


def _normalize_blacklist(raw: Any) -> list[dict[str, Any]]:
    values = raw.get("entries", []) if isinstance(raw, dict) else raw
    if not isinstance(values, list):
        return []

    entries_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for value in values:
        entry = _normalize_entry(value)
        if not entry:
            continue
        key = (
            entry["provider_id"],
            entry["model_id"],
            entry.get("credential_name", ""),
        )
        current = entries_by_key.get(key)
        if not current:
            entries_by_key[key] = entry
            continue
        current["failure_count"] += entry["failure_count"]
        current["first_seen_at"] = min(current["first_seen_at"], entry["first_seen_at"])
        current["last_seen_at"] = max(current["last_seen_at"], entry["last_seen_at"])

    entries = sorted(
        entries_by_key.values(),
        key=lambda entry: (
            -entry["last_seen_at"],
            entry["provider_id"],
            entry["model_id"],
            entry.get("credential_name", ""),
        ),
    )
    return entries[:MAX_MODEL_BLACKLIST_ENTRIES]


async def _load_entries(storage_adapter) -> list[dict[str, Any]]:
    raw = await storage_adapter.get_config(MODEL_BLACKLIST_CONFIG_KEY, {"entries": []})
    return _normalize_blacklist(raw)


async def _save_entries(storage_adapter, entries: list[dict[str, Any]]) -> None:
    if not await storage_adapter.set_config(
        MODEL_BLACKLIST_CONFIG_KEY,
        {"entries": _normalize_blacklist(entries)},
    ):
        raise RuntimeError("The model blacklist could not be saved.")


async def get_model_blacklist(*, storage_adapter=None) -> list[dict[str, Any]]:
    storage = storage_adapter or await get_storage_adapter()
    return await _load_entries(storage)


async def get_model_blacklist_pairs(*, storage_adapter=None) -> set[tuple[str, str]]:
    """Return legacy provider-wide exclusions without widening credential failures."""
    return {
        (entry["provider_id"], entry["model_id"])
        for entry in await get_model_blacklist(storage_adapter=storage_adapter)
        if not entry.get("credential_name")
    }


async def get_credential_model_blacklist_pairs(*, storage_adapter=None) -> set[tuple[str, str]]:
    """Return deployment-scoped exclusions keyed by credential filename and model."""
    return {
        (entry["credential_name"], entry["model_id"])
        for entry in await get_model_blacklist(storage_adapter=storage_adapter)
        if entry.get("credential_name")
    }


async def record_model_not_found(
    provider_id: Any,
    model_id: Any,
    *,
    credential_name: Any = None,
    storage_adapter=None,
    now: Optional[float] = None,
) -> dict[str, Any]:
    """Add or update a model exclusion after an upstream 404.

    New observations should include ``credential_name`` so one account's
    entitlement does not suppress a model for every account at that provider.
    Entries without a credential name remain supported for legacy data.
    """
    storage = storage_adapter or await get_storage_adapter()
    normalized_provider = normalize_provider_id(provider_id)
    if not normalized_provider:
        raise ValueError("A provider ID is required.")
    normalized_model = normalize_model_id(model_id)
    normalized_credential = _normalize_credential_name(credential_name)
    observed_at = _normalize_timestamp(time.time() if now is None else now)

    async with _write_lock:
        entries = await _load_entries(storage)
        entry = next(
            (
                item
                for item in entries
                if item["provider_id"] == normalized_provider
                and item["model_id"] == normalized_model
                and item.get("credential_name", "") == normalized_credential
            ),
            None,
        )
        if entry:
            entry["failure_count"] += 1
            entry["last_seen_at"] = max(entry["last_seen_at"], observed_at)
        else:
            entry = {
                "provider_id": normalized_provider,
                "model_id": normalized_model,
                "status_code": 404,
                "failure_count": 1,
                "first_seen_at": observed_at,
                "last_seen_at": observed_at,
            }
            if normalized_credential:
                entry["credential_name"] = normalized_credential
            entries.append(entry)
        await _save_entries(storage, entries)
        return dict(entry)


async def remove_model_blacklist_entry(
    provider_id: Any,
    model_id: Any,
    *,
    credential_name: Any = None,
    storage_adapter=None,
) -> bool:
    storage = storage_adapter or await get_storage_adapter()
    normalized_provider = normalize_provider_id(provider_id)
    normalized_model = normalize_model_id(model_id)
    normalized_credential = _normalize_credential_name(credential_name)

    async with _write_lock:
        entries = await _load_entries(storage)
        retained = [
            entry
            for entry in entries
            if not (
                entry["provider_id"] == normalized_provider
                and entry["model_id"] == normalized_model
                and (
                    not normalized_credential
                    or entry.get("credential_name", "") == normalized_credential
                )
            )
        ]
        if len(retained) == len(entries):
            return False
        await _save_entries(storage, retained)
        return True


async def clear_model_blacklist(*, storage_adapter=None) -> int:
    storage = storage_adapter or await get_storage_adapter()
    async with _write_lock:
        entries = await _load_entries(storage)
        if entries:
            await _save_entries(storage, [])
        return len(entries)
