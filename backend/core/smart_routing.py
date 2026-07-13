"""Concurrency-aware credential selection for provider requests."""

from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Deque, Dict, Optional, Set, Tuple

from core.provider_registry import (
    credential_supports_model,
    get_credential_provider,
    normalize_provider_id,
)
from log import log

CredentialResult = Tuple[str, Dict[str, Any]]
CredentialKey = Tuple[str, str]


@dataclass(frozen=True)
class FailurePenalty:
    consecutive_failures: int
    retry_after: float


class SmartCredentialRouter:
    """Select healthy credentials while spreading concurrent requests."""

    def __init__(
        self,
        *,
        clock: Callable[[], float] = time.time,
        lease_ttl_seconds: float = 15 * 60,
        state_cache_ttl_seconds: float = 0.25,
        base_backoff_seconds: float = 2.0,
        max_backoff_seconds: float = 30.0,
    ) -> None:
        self._clock = clock
        self._lease_ttl_seconds = max(1.0, float(lease_ttl_seconds))
        self._state_cache_ttl_seconds = max(0.0, float(state_cache_ttl_seconds))
        self._base_backoff_seconds = max(0.0, float(base_backoff_seconds))
        self._max_backoff_seconds = max(self._base_backoff_seconds, float(max_backoff_seconds))
        self._lock = asyncio.Lock()
        self._leases: Dict[CredentialKey, Deque[float]] = {}
        self._failures: Dict[CredentialKey, FailurePenalty] = {}
        self._last_selected: Dict[CredentialKey, float] = {}
        self._providers: Dict[CredentialKey, str] = {}
        self._state_cache: Dict[str, Tuple[float, Dict[str, Dict[str, Any]]]] = {}

    def _prune_expired_leases(self, now: float) -> None:
        expires_before = now - self._lease_ttl_seconds
        empty_keys = []
        for key, leases in self._leases.items():
            while leases and leases[0] <= expires_before:
                leases.popleft()
            if not leases:
                empty_keys.append(key)
        for key in empty_keys:
            self._leases.pop(key, None)

    @staticmethod
    def _is_model_available(state: Dict[str, Any], model_name: Optional[str], now: float) -> bool:
        if not model_name:
            return True
        cooldowns = state.get("model_cooldowns") or {}
        cooldown_until = cooldowns.get(model_name)
        return not isinstance(cooldown_until, (int, float)) or cooldown_until <= now

    @staticmethod
    def _preview_penalty(
        state: Dict[str, Any], mode: str, model_name: Optional[str]
    ) -> Optional[int]:
        if mode != "code_assist" or not model_name:
            return 0

        is_preview_credential = bool(state.get("preview", True))
        if "preview" in model_name.lower():
            return 0 if is_preview_credential else None
        return 1 if is_preview_credential else 0

    def _rank_candidates(
        self,
        states: Dict[str, Dict[str, Any]],
        *,
        mode: str,
        model_name: Optional[str],
        routing_strategy: str,
        preferred_provider: Optional[str],
        excluded_provider_models: Set[Tuple[str, str]],
        now: float,
    ) -> list[tuple[tuple[Any, ...], str]]:
        candidates = []

        for filename, state in states.items():
            if state.get("disabled", False):
                continue
            if not self._is_model_available(state, model_name, now):
                continue

            preview_penalty = self._preview_penalty(state, mode, model_name)
            if preview_penalty is None:
                continue

            key = (mode, filename)
            if model_name and (self._providers.get(key), model_name) in excluded_provider_models:
                continue
            provider_penalty = 0
            if routing_strategy == "priority" and preferred_provider:
                provider_penalty = int(self._providers.get(key) != preferred_provider)
            failure = self._failures.get(key)
            retry_after = failure.retry_after if failure else 0.0
            consecutive_failures = failure.consecutive_failures if failure else 0
            in_flight = len(self._leases.get(key, ()))
            error_count = len(state.get("error_codes") or [])
            last_selected = max(
                float(state.get("last_success") or 0.0),
                self._last_selected.get(key, 0.0),
            )

            score = (
                provider_penalty,
                preview_penalty,
                in_flight,
                last_selected,
                max(0, int(state.get("call_count") or 0)),
                consecutive_failures,
                error_count,
                max(0, int(state.get("rotation_order") or 0)),
                filename,
            )
            candidates.append((score, filename, retry_after))

        ready = [item for item in candidates if item[2] <= now]
        return sorted((score, filename) for score, filename, _ in ready)

    async def _load_candidate_providers(
        self,
        storage_adapter: Any,
        filenames,
        *,
        mode: str,
    ) -> None:
        """Cache provider identities used by the routing policy."""
        for filename in filenames:
            key = (mode, filename)
            if key in self._providers:
                continue
            credential_data = await storage_adapter.get_credential(filename, mode=mode)
            if credential_data:
                self._providers[key] = get_credential_provider(credential_data)

    async def acquire(
        self,
        storage_adapter: Any,
        *,
        mode: str = "primary",
        model_name: Optional[str] = None,
        provider_id: Optional[str] = None,
        routing_strategy: str = "balanced",
        preferred_provider: Optional[str] = None,
        excluded_provider_models: Optional[Set[Tuple[str, str]]] = None,
    ) -> Optional[CredentialResult]:
        """Reserve and return the best currently available credential."""
        async with self._lock:
            now = self._clock()
            self._prune_expired_leases(now)
            cached = self._state_cache.get(mode)
            if cached and cached[0] > now:
                states = cached[1]
            else:
                states = await storage_adapter.get_all_credential_states(mode=mode)
                self._state_cache[mode] = (
                    now + self._state_cache_ttl_seconds,
                    states,
                )
            await self._load_candidate_providers(storage_adapter, states, mode=mode)
            normalized_strategy = (
                "priority" if str(routing_strategy).lower() == "priority" else "balanced"
            )
            normalized_preferred_provider = (
                normalize_provider_id(preferred_provider) if preferred_provider else None
            )
            normalized_exclusions = {
                (normalize_provider_id(excluded_provider), str(excluded_model).strip())
                for excluded_provider, excluded_model in (excluded_provider_models or set())
                if str(excluded_provider or "").strip() and str(excluded_model or "").strip()
            }
            ranked = self._rank_candidates(
                states,
                mode=mode,
                model_name=model_name,
                routing_strategy=normalized_strategy,
                preferred_provider=normalized_preferred_provider,
                excluded_provider_models=normalized_exclusions,
                now=now,
            )

            for score, filename in ranked:
                credential_data = await storage_adapter.get_credential(filename, mode=mode)
                if not credential_data:
                    continue
                if not credential_supports_model(
                    credential_data,
                    model_name,
                    required_provider=provider_id,
                ):
                    continue

                if mode == "primary":
                    credential_data["enable_credit"] = bool(
                        states.get(filename, {}).get("enable_credit", False)
                    )

                key = (mode, filename)
                self._leases.setdefault(key, deque()).append(now)
                self._last_selected[key] = now
                log.debug(
                    f"Smart routing selected {filename} "
                    f"(mode={mode}, model={model_name or ''}, "
                    f"provider={get_credential_provider(credential_data)}, "
                    f"in_flight={score[2] + 1}, calls={score[4]})."
                )
                return filename, credential_data

            return None

    async def complete(
        self,
        filename: str,
        *,
        mode: str = "primary",
        success: bool,
        cooldown_until: Optional[float] = None,
    ) -> None:
        """Release one reservation and update the short-lived health penalty."""
        async with self._lock:
            now = self._clock()
            self._prune_expired_leases(now)
            self._state_cache.pop(mode, None)
            key = (mode, filename)
            self._release_lease(key)

            if success:
                self._failures.pop(key, None)
                return

            previous = self._failures.get(key)
            failure_count = (previous.consecutive_failures if previous else 0) + 1
            if cooldown_until is not None and cooldown_until > now:
                retry_after = cooldown_until
            else:
                backoff = min(
                    self._base_backoff_seconds * (2 ** (failure_count - 1)),
                    self._max_backoff_seconds,
                )
                retry_after = now + backoff
            self._failures[key] = FailurePenalty(failure_count, retry_after)

    def _release_lease(self, key: CredentialKey) -> None:
        leases = self._leases.get(key)
        if not leases:
            return
        leases.popleft()
        if not leases:
            self._leases.pop(key, None)

    async def release(self, filename: str, *, mode: str = "primary") -> None:
        """Release one reservation without changing credential health."""
        async with self._lock:
            now = self._clock()
            self._prune_expired_leases(now)
            self._state_cache.pop(mode, None)
            self._release_lease((mode, filename))

    async def reset(self) -> None:
        async with self._lock:
            self._leases.clear()
            self._failures.clear()
            self._last_selected.clear()
            self._providers.clear()
            self._state_cache.clear()
