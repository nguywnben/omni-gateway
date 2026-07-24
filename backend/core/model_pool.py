"""Dynamic model catalog and virtual-model routing configuration."""

from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Iterable, Mapping, Optional, Sequence

from core.storage_adapter import get_storage_adapter

DEFAULT_VIRTUAL_MODEL_ALIAS = "omway"
MODEL_POOL_CONFIG_KEY = "virtual_model_pool"
MODEL_CATALOG_TTL_SECONDS = 5 * 60.0
MAX_POOL_MODELS = 64
_MODEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,199}$")


class ModelPoolError(ValueError):
    """A safe model-pool configuration or resolution error."""


@dataclass(frozen=True, order=True)
class ModelCatalogEntry:
    model_id: str
    providers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "model_id": self.model_id,
            "providers": list(self.providers),
            "available": bool(self.providers),
        }


@dataclass(frozen=True)
class ModelResolution:
    requested_model: str
    response_model: str
    candidates: tuple[str, ...]
    is_virtual: bool


CatalogLoader = Callable[[], Awaitable[Mapping[str, Iterable[str]]]]


def normalize_model_id(value: Any) -> str:
    model_id = str(value or "").strip()
    if model_id.startswith("models/"):
        model_id = model_id[7:]
    if not model_id or not _MODEL_ID_PATTERN.fullmatch(model_id):
        raise ModelPoolError("Enter a valid provider model ID.")
    return model_id


def _normalize_selected_models(values: Sequence[Any]) -> list[str]:
    if not isinstance(values, (list, tuple)):
        raise ModelPoolError("selected_models must be an array.")
    if len(values) > MAX_POOL_MODELS:
        raise ModelPoolError(f"A model pool can contain at most {MAX_POOL_MODELS} models.")

    selected: list[str] = []
    seen = set()
    for value in values:
        model_id = normalize_model_id(value)
        if model_id in seen:
            continue
        seen.add(model_id)
        selected.append(model_id)
    return selected


async def _default_catalog_loader() -> Mapping[str, Iterable[str]]:
    from core.api.primary import fetch_configured_provider_models

    return await fetch_configured_provider_models()


class ModelCatalogService:
    """Cache normalized provider model discovery without losing provenance."""

    def __init__(
        self,
        *,
        loader: Optional[CatalogLoader] = None,
        ttl_seconds: float = MODEL_CATALOG_TTL_SECONDS,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._loader = loader or _default_catalog_loader
        self._ttl_seconds = max(0.0, float(ttl_seconds))
        self._clock = clock
        self._lock = asyncio.Lock()
        self._entries: tuple[ModelCatalogEntry, ...] = ()
        self._expires_at = 0.0
        self._loaded = False

    async def get_catalog(self, *, force_refresh: bool = False) -> list[ModelCatalogEntry]:
        now = self._clock()
        if not force_refresh and self._loaded and self._expires_at > now:
            return list(self._entries)

        async with self._lock:
            now = self._clock()
            if not force_refresh and self._loaded and self._expires_at > now:
                return list(self._entries)

            provider_models = await self._loader()
            providers_by_model: dict[str, set[str]] = {}
            for provider_id, model_ids in provider_models.items():
                normalized_provider = str(provider_id or "").strip()
                if not normalized_provider:
                    continue
                for value in model_ids or ():
                    try:
                        model_id = normalize_model_id(value)
                    except ModelPoolError:
                        continue
                    providers_by_model.setdefault(model_id, set()).add(normalized_provider)

            self._entries = tuple(
                ModelCatalogEntry(model_id, tuple(sorted(providers)))
                for model_id, providers in sorted(providers_by_model.items())
            )
            self._expires_at = now + self._ttl_seconds
            self._loaded = True
            return list(self._entries)

    async def invalidate(self) -> None:
        async with self._lock:
            self._entries = ()
            self._expires_at = 0.0
            self._loaded = False


model_catalog_service = ModelCatalogService()


def _normalize_pool_config(raw: Any) -> dict[str, Any]:
    source = raw if isinstance(raw, dict) else {}
    try:
        selected_models = _normalize_selected_models(source.get("selected_models") or [])
    except ModelPoolError:
        selected_models = []
    return {
        "alias": DEFAULT_VIRTUAL_MODEL_ALIAS,
        "strategy": "priority_fallback",
        "selected_models": selected_models,
        "enabled": bool(source.get("enabled", True)),
    }


async def get_virtual_model_pool(storage_adapter=None) -> dict[str, Any]:
    storage = storage_adapter or await get_storage_adapter()
    raw = await storage.get_config(MODEL_POOL_CONFIG_KEY, {})
    return _normalize_pool_config(raw)


async def save_virtual_model_pool(
    selected_models: Sequence[Any],
    *,
    enabled: bool = True,
    storage_adapter=None,
) -> dict[str, Any]:
    storage = storage_adapter or await get_storage_adapter()
    config = {
        "alias": DEFAULT_VIRTUAL_MODEL_ALIAS,
        "strategy": "priority_fallback",
        "selected_models": _normalize_selected_models(selected_models),
        "enabled": bool(enabled),
    }
    if not await storage.set_config(MODEL_POOL_CONFIG_KEY, config):
        raise ModelPoolError("The virtual model configuration could not be saved.")
    return config


async def resolve_model_request(
    model_name: Any,
    *,
    storage_adapter=None,
) -> ModelResolution:
    requested_model = normalize_model_id(model_name)
    if requested_model != DEFAULT_VIRTUAL_MODEL_ALIAS:
        return ModelResolution(
            requested_model=requested_model,
            response_model=requested_model,
            candidates=(requested_model,),
            is_virtual=False,
        )

    pool = await get_virtual_model_pool(storage_adapter=storage_adapter)
    if not pool["enabled"] or not pool["selected_models"]:
        raise ModelPoolError(
            f'The virtual model "{DEFAULT_VIRTUAL_MODEL_ALIAS}" has no configured provider models.'
        )

    return ModelResolution(
        requested_model=requested_model,
        response_model=DEFAULT_VIRTUAL_MODEL_ALIAS,
        candidates=tuple(pool["selected_models"]),
        is_virtual=True,
    )


async def get_public_virtual_models(storage_adapter=None) -> list[str]:
    pool = await get_virtual_model_pool(storage_adapter=storage_adapter)
    if pool["enabled"] and pool["selected_models"]:
        return [pool["alias"]]
    return []
