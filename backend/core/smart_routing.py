"""Concurrency-aware credential selection for provider requests."""

from __future__ import annotations

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Deque, Dict, Optional, Set, Tuple

from core.provider_registry import (
    credential_model_support_level,
    get_credential_provider,
    normalize_provider_id,
)
from core.request_context import get_request_id
from core.routing_decision import RouteCandidate, RouteDecision
from log import log

CredentialResult = Tuple[str, Dict[str, Any]]
CredentialKey = Tuple[str, str]
FailureKey = Tuple[str, str, str]


@dataclass(frozen=True)
class FailurePenalty:
    consecutive_failures: int
    retry_after: float
    kind: str


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
        auth_backoff_seconds: float = 300.0,
        model_backoff_seconds: float = 60.0,
    ) -> None:
        self._clock = clock
        self._lease_ttl_seconds = max(1.0, float(lease_ttl_seconds))
        self._state_cache_ttl_seconds = max(0.0, float(state_cache_ttl_seconds))
        self._base_backoff_seconds = max(0.0, float(base_backoff_seconds))
        self._max_backoff_seconds = max(self._base_backoff_seconds, float(max_backoff_seconds))
        self._auth_backoff_seconds = max(self._max_backoff_seconds, float(auth_backoff_seconds))
        self._model_backoff_seconds = max(self._base_backoff_seconds, float(model_backoff_seconds))
        self._lock = asyncio.Lock()
        self._leases: Dict[CredentialKey, Deque[float]] = {}
        self._failures: Dict[FailureKey, FailurePenalty] = {}
        self._last_selected: Dict[CredentialKey, float] = {}
        self._providers: Dict[CredentialKey, str] = {}
        self._state_cache: Dict[str, Tuple[float, Dict[str, Dict[str, Any]]]] = {}
        self._recent_decisions: Deque[RouteDecision] = deque(maxlen=100)

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
    def _failure_key(mode: str, filename: str, model_name: Optional[str] = None) -> FailureKey:
        return mode, filename, str(model_name or "")

    def _active_failure(
        self, mode: str, filename: str, model_name: Optional[str]
    ) -> Optional[FailurePenalty]:
        return self._failures.get(self._failure_key(mode, filename, model_name)) or self._failures.get(
            self._failure_key(mode, filename)
        )

    @staticmethod
    def _failure_kind(error_code: Optional[int]) -> str:
        if error_code in {401, 403}:
            return "authentication"
        if error_code == 404:
            return "model_unavailable"
        if error_code == 429:
            return "rate_limited"
        if error_code is not None and 400 <= error_code < 500:
            return "client_request"
        return "transient"

    def _retry_after(
        self,
        *,
        failure_count: int,
        failure_kind: str,
        now: float,
        cooldown_until: Optional[float],
    ) -> float:
        if cooldown_until is not None and cooldown_until > now:
            return cooldown_until
        if failure_kind == "authentication":
            return now + self._auth_backoff_seconds
        if failure_kind == "model_unavailable":
            return now + self._model_backoff_seconds
        backoff = min(
            self._base_backoff_seconds * (2 ** (failure_count - 1)),
            self._max_backoff_seconds,
        )
        return now + backoff

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
        excluded_credential_models: Set[Tuple[str, str]],
        now: float,
    ) -> tuple[list[tuple[tuple[Any, ...], str]], Dict[str, RouteCandidate]]:
        candidates = []
        decisions: Dict[str, RouteCandidate] = {}

        for filename, state in states.items():
            key = (mode, filename)
            provider_id = self._providers.get(key, "")
            in_flight = len(self._leases.get(key, ()))
            failure = self._active_failure(mode, filename, model_name)
            consecutive_failures = failure.consecutive_failures if failure else 0

            if state.get("disabled", False):
                decisions[filename] = RouteCandidate(
                    filename, provider_id, "rejected", "disabled", in_flight=in_flight,
                    consecutive_failures=consecutive_failures,
                )
                continue
            if not self._is_model_available(state, model_name, now):
                decisions[filename] = RouteCandidate(
                    filename, provider_id, "rejected", "model_cooldown", in_flight=in_flight,
                    consecutive_failures=consecutive_failures,
                )
                continue

            preview_penalty = self._preview_penalty(state, mode, model_name)
            if preview_penalty is None:
                decisions[filename] = RouteCandidate(
                    filename, provider_id, "rejected", "preview_incompatible", in_flight=in_flight,
                    consecutive_failures=consecutive_failures,
                )
                continue

            if model_name and (filename, model_name) in excluded_credential_models:
                decisions[filename] = RouteCandidate(
                    filename, provider_id, "rejected", "credential_model_blacklist",
                    in_flight=in_flight, consecutive_failures=consecutive_failures,
                )
                continue
            if model_name and (provider_id, model_name) in excluded_provider_models:
                decisions[filename] = RouteCandidate(
                    filename, provider_id, "rejected", "provider_model_blacklist",
                    in_flight=in_flight, consecutive_failures=consecutive_failures,
                )
                continue
            provider_penalty = 0
            if routing_strategy == "priority" and preferred_provider:
                provider_penalty = int(self._providers.get(key) != preferred_provider)
            retry_after = failure.retry_after if failure else 0.0
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
            failure_reason = ""
            if retry_after > now:
                failure_reason = f"backoff_{failure.kind}" if failure else "backoff"
            decisions[filename] = RouteCandidate(
                filename,
                provider_id,
                "eligible" if retry_after <= now else "rejected",
                failure_reason,
                in_flight=in_flight,
                consecutive_failures=consecutive_failures,
            )

        ready = [item for item in candidates if item[2] <= now]
        return sorted((score, filename) for score, filename, _ in ready), decisions

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

    async def acquire_with_decision(
        self,
        storage_adapter: Any,
        *,
        mode: str = "primary",
        model_name: Optional[str] = None,
        provider_id: Optional[str] = None,
        routing_strategy: str = "balanced",
        preferred_provider: Optional[str] = None,
        excluded_provider_models: Optional[Set[Tuple[str, str]]] = None,
        excluded_credential_models: Optional[Set[Tuple[str, str]]] = None,
    ) -> tuple[Optional[CredentialResult], RouteDecision]:
        """Reserve the best credential and return its diagnostic decision."""
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
            normalized_credential_exclusions = {
                (
                    str(excluded_filename).replace("\\", "/").rsplit("/", 1)[-1],
                    str(excluded_model).strip(),
                )
                for excluded_filename, excluded_model in (excluded_credential_models or set())
                if str(excluded_filename or "").strip() and str(excluded_model or "").strip()
            }
            ranked, decisions = self._rank_candidates(
                states,
                mode=mode,
                model_name=model_name,
                routing_strategy=normalized_strategy,
                preferred_provider=normalized_preferred_provider,
                excluded_provider_models=normalized_exclusions,
                excluded_credential_models=normalized_credential_exclusions,
                now=now,
            )

            selected = None
            for score, filename in ranked:
                credential_data = await storage_adapter.get_credential(filename, mode=mode)
                if not credential_data:
                    candidate = decisions[filename]
                    decisions[filename] = RouteCandidate(
                        filename, candidate.provider_id, "rejected", "credential_missing",
                        in_flight=candidate.in_flight,
                        consecutive_failures=candidate.consecutive_failures,
                    )
                    continue
                support_level = credential_model_support_level(
                    credential_data,
                    model_name,
                    required_provider=provider_id,
                )
                if not support_level:
                    candidate = decisions[filename]
                    decisions[filename] = RouteCandidate(
                        filename, candidate.provider_id, "rejected", "model_unsupported",
                        in_flight=candidate.in_flight,
                        consecutive_failures=candidate.consecutive_failures,
                    )
                    continue

                candidate = decisions[filename]
                decisions[filename] = RouteCandidate(
                    filename,
                    candidate.provider_id,
                    "eligible",
                    support_level=support_level,
                    in_flight=candidate.in_flight,
                    consecutive_failures=candidate.consecutive_failures,
                )

                candidate = ((-support_level, *score), score, filename, credential_data)
                if selected is None or candidate[0] < selected[0]:
                    selected = candidate

            if selected is not None:
                _, score, filename, credential_data = selected

                if mode == "primary":
                    credential_data["enable_credit"] = bool(
                        states.get(filename, {}).get("enable_credit", False)
                    )

                key = (mode, filename)
                self._leases.setdefault(key, deque()).append(now)
                self._last_selected[key] = now
                candidate = decisions[filename]
                selected_provider = get_credential_provider(credential_data)
                decisions[filename] = RouteCandidate(
                    filename,
                    selected_provider,
                    "selected",
                    support_level=candidate.support_level,
                    in_flight=candidate.in_flight + 1,
                    consecutive_failures=candidate.consecutive_failures,
                )
                decision = RouteDecision(
                    mode=mode,
                    requested_model=str(model_name or ""),
                    required_provider=str(provider_id or ""),
                    routing_strategy=normalized_strategy,
                    selected_filename=filename,
                    selected_provider=selected_provider,
                    candidates=tuple(decisions[name] for name in sorted(decisions)),
                    created_at=now,
                    request_id=get_request_id(),
                )
                self._recent_decisions.append(decision)
                log.debug(
                    f"Smart routing selected {filename} "
                    f"(mode={mode}, model={model_name or ''}, "
                    f"provider={get_credential_provider(credential_data)}, "
                    f"support={-selected[0][0]}, in_flight={score[2] + 1}, calls={score[4]})."
                )
                return (filename, credential_data), decision

            decision = RouteDecision(
                mode=mode,
                requested_model=str(model_name or ""),
                required_provider=str(provider_id or ""),
                routing_strategy=normalized_strategy,
                selected_filename=None,
                selected_provider=None,
                candidates=tuple(decisions[name] for name in sorted(decisions)),
                created_at=now,
                request_id=get_request_id(),
            )
            self._recent_decisions.append(decision)
            return None, decision

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
        excluded_credential_models: Optional[Set[Tuple[str, str]]] = None,
    ) -> Optional[CredentialResult]:
        """Reserve and return the best currently available credential."""
        result, _ = await self.acquire_with_decision(
            storage_adapter,
            mode=mode,
            model_name=model_name,
            provider_id=provider_id,
            routing_strategy=routing_strategy,
            preferred_provider=preferred_provider,
            excluded_provider_models=excluded_provider_models,
            excluded_credential_models=excluded_credential_models,
        )
        return result

    async def recent_decisions(self, limit: int = 20) -> tuple[RouteDecision, ...]:
        """Return recent sanitized decisions for diagnostics without credential secrets."""
        async with self._lock:
            return tuple(list(self._recent_decisions)[-max(0, int(limit)) :])

    async def complete(
        self,
        filename: str,
        *,
        mode: str = "primary",
        success: bool,
        cooldown_until: Optional[float] = None,
        model_name: Optional[str] = None,
        error_code: Optional[int] = None,
    ) -> None:
        """Release one reservation and update the short-lived health penalty."""
        async with self._lock:
            now = self._clock()
            self._prune_expired_leases(now)
            self._state_cache.pop(mode, None)
            key = (mode, filename)
            self._release_lease(key)

            failure_key = self._failure_key(mode, filename, model_name)

            if success:
                self._failures.pop(failure_key, None)
                if model_name is None:
                    self._failures.pop(self._failure_key(mode, filename), None)
                return

            failure_kind = self._failure_kind(error_code)
            if failure_kind == "client_request":
                return

            previous = self._failures.get(failure_key)
            failure_count = (previous.consecutive_failures if previous else 0) + 1
            retry_after = self._retry_after(
                failure_count=failure_count,
                failure_kind=failure_kind,
                now=now,
                cooldown_until=cooldown_until,
            )
            self._failures[failure_key] = FailurePenalty(
                failure_count,
                retry_after,
                failure_kind,
            )

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
            self._recent_decisions.clear()
