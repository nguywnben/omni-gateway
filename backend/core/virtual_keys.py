"""Virtual API keys with per-key budgets, rate limits, and model allowlists.

Design distilled from LiteLLM's proxy auth (`user_api_key_auth.py` /
`auth_checks.py`) adapted to Omni Gateway's single-process architecture:

- Keys are stored in the storage backend under the ``virtual_keys`` config
  entry. Only the SHA-256 hash of the secret is persisted; the plaintext is
  shown exactly once at creation time.
- RPM/TPM enforcement uses in-memory sliding windows. This is correct because
  the gateway enforces ``WORKERS=1`` (see ``main.py``); if multi-worker mode
  ever lands, these windows must move to ``core.state_store``.
- Budget enforcement uses rolling windows (24h / 30d) backed by the usage
  ledger (``usage_stats.get_spend_since``) with a short-lived cache so budget
  checks do not add a SQLite query to every request.
"""

from __future__ import annotations

import asyncio
import fnmatch
import hashlib
import re
import secrets
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, List, Optional, Tuple

from fastapi import HTTPException, status
from log import log

VIRTUAL_KEYS_CONFIG_KEY = "virtual_keys"
KEY_ID_PREFIX = "vk_"
BUDGET_CACHE_TTL_SECONDS = 15.0
DAILY_WINDOW_SECONDS = 86_400
MONTHLY_WINDOW_SECONDS = 30 * 86_400
RATE_WINDOW_SECONDS = 60.0
LAST_USED_PERSIST_INTERVAL_SECONDS = 60.0
VIRTUAL_KEY_SCHEMA_VERSION = 2
MAX_MODEL_PATTERNS = 64
MAX_MODEL_PATTERN_LENGTH = 128
MAX_FALLBACK_PRICE_USD_PER_MILLION = 100_000.0

INFERENCE_SCOPES = (
    "inference:openai",
    "inference:anthropic",
    "inference:gemini",
)
MANAGEMENT_SCOPES = ("management:read", "management:write")
VIRTUAL_KEY_SCOPES = INFERENCE_SCOPES + MANAGEMENT_SCOPES
DEFAULT_INFERENCE_SCOPES = INFERENCE_SCOPES
UNKNOWN_PRICING_POLICIES = ("deny", "warn", "fallback")

_GEMINI_MODEL_PATH_RE = re.compile(r"/models/([^/:?]+)")
_MODEL_PATTERN_RE = re.compile(r"^(?=.{1,128}$)(?=.*[A-Za-z0-9])[A-Za-z0-9._:/+*?-]+$")


def hash_key(token: str) -> str:
    return hashlib.sha256(str(token or "").encode("utf-8")).hexdigest()


def _key_preview(token: str) -> str:
    if len(token) <= 16:
        return token[:4] + "..."
    return f"{token[:12]}...{token[-4:]}"


def _float_or_none(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def _int_or_none(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def normalize_virtual_key_scopes(value: Any, *, legacy_default: bool = False) -> Tuple[str, ...]:
    if value is None and legacy_default:
        return DEFAULT_INFERENCE_SCOPES
    if not isinstance(value, (list, tuple)):
        raise ValueError("Virtual key scopes must be a list.")
    requested = {str(scope).strip().lower() for scope in value if str(scope).strip()}
    unknown = requested.difference(VIRTUAL_KEY_SCOPES)
    if unknown:
        raise ValueError("Virtual key scopes contain an unknown value.")
    if not requested:
        raise ValueError("At least one virtual key scope is required.")
    if "management:write" in requested and "management:read" not in requested:
        raise ValueError("The management:write scope requires management:read.")
    return tuple(scope for scope in VIRTUAL_KEY_SCOPES if scope in requested)


def normalize_model_patterns(value: Any) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, (list, tuple)):
        raise ValueError("Virtual key model patterns must be a list.")
    if len(value) > MAX_MODEL_PATTERNS:
        raise ValueError(f"At most {MAX_MODEL_PATTERNS} model patterns are allowed.")
    normalized: List[str] = []
    seen = set()
    for candidate in value:
        pattern = str(candidate).strip()
        if not _MODEL_PATTERN_RE.fullmatch(pattern):
            raise ValueError("Each model pattern must use only bounded safe glob characters.")
        folded = pattern.lower()
        if folded not in seen:
            normalized.append(pattern)
            seen.add(folded)
    return normalized


def normalize_unknown_pricing_policy(policy: Any, fallback: Any) -> Tuple[str, Optional[float]]:
    normalized_policy = str(policy or "deny").strip().lower()
    if normalized_policy not in UNKNOWN_PRICING_POLICIES:
        raise ValueError("Unknown pricing policy must be deny, warn, or fallback.")
    normalized_fallback = _float_or_none(fallback)
    if normalized_fallback is not None and normalized_fallback > MAX_FALLBACK_PRICE_USD_PER_MILLION:
        raise ValueError("Unknown-pricing fallback price exceeds the supported maximum.")
    if normalized_policy == "fallback" and normalized_fallback is None:
        raise ValueError("A positive fallback price is required for fallback pricing policy.")
    if normalized_policy != "fallback" and fallback is not None and fallback != "":
        raise ValueError("A fallback price is only valid with fallback pricing policy.")
    return normalized_policy, normalized_fallback


@dataclass
class VirtualKey:
    """A single virtual API key record (secret stored as SHA-256 hash)."""

    id: str
    name: str
    key_hash: str
    key_preview: str
    enabled: bool = True
    created_at: float = 0.0
    expires_at: Optional[float] = None
    budget_daily_usd: Optional[float] = None
    budget_monthly_usd: Optional[float] = None
    rpm_limit: Optional[int] = None
    tpm_limit: Optional[int] = None
    allowed_models: List[str] = field(default_factory=list)
    schema_version: int = VIRTUAL_KEY_SCHEMA_VERSION
    scopes: Tuple[str, ...] = DEFAULT_INFERENCE_SCOPES
    unknown_pricing_policy: str = "deny"
    fallback_price_usd_per_million: Optional[float] = None
    last_used_at: Optional[float] = None

    @property
    def status(self) -> str:
        if not self.enabled:
            return "disabled"
        if self.is_expired():
            return "expired"
        return "active"

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "id": self.id,
            "name": self.name,
            "key_preview": self.key_preview,
            "enabled": self.enabled,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "budget_daily_usd": self.budget_daily_usd,
            "budget_monthly_usd": self.budget_monthly_usd,
            "rpm_limit": self.rpm_limit,
            "tpm_limit": self.tpm_limit,
            "allowed_models": list(self.allowed_models),
            "scopes": list(self.scopes),
            "unknown_pricing_policy": self.unknown_pricing_policy,
            "fallback_price_usd_per_million": self.fallback_price_usd_per_million,
            "last_used_at": self.last_used_at,
            "status": self.status,
        }

    def to_storage_dict(self) -> Dict[str, Any]:
        payload = self.to_public_dict()
        payload.pop("status", None)
        payload["key_hash"] = self.key_hash
        return payload

    @classmethod
    def from_storage_dict(cls, raw: Dict[str, Any]) -> Optional["VirtualKey"]:
        if not isinstance(raw, dict):
            return None
        key_id = str(raw.get("id") or "").strip()
        key_hash = str(raw.get("key_hash") or "").strip()
        if not key_id or not key_hash:
            return None
        raw_version = raw.get("schema_version")
        is_legacy = raw_version is None
        if not is_legacy and raw_version != VIRTUAL_KEY_SCHEMA_VERSION:
            return None
        try:
            scopes = normalize_virtual_key_scopes(raw.get("scopes"), legacy_default=is_legacy)
            allowed_models = normalize_model_patterns(raw.get("allowed_models") or [])
            pricing_policy, fallback_price = normalize_unknown_pricing_policy(
                raw.get("unknown_pricing_policy"),
                raw.get("fallback_price_usd_per_million"),
            )
            return cls(
                id=key_id,
                name=str(raw.get("name") or key_id),
                key_hash=key_hash,
                key_preview=str(raw.get("key_preview") or ""),
                enabled=bool(raw.get("enabled", True)),
                created_at=float(raw.get("created_at") or 0.0),
                expires_at=_float_or_none(raw.get("expires_at")),
                budget_daily_usd=_float_or_none(raw.get("budget_daily_usd")),
                budget_monthly_usd=_float_or_none(raw.get("budget_monthly_usd")),
                rpm_limit=_int_or_none(raw.get("rpm_limit")),
                tpm_limit=_int_or_none(raw.get("tpm_limit")),
                allowed_models=allowed_models,
                schema_version=VIRTUAL_KEY_SCHEMA_VERSION,
                scopes=scopes,
                unknown_pricing_policy=pricing_policy,
                fallback_price_usd_per_million=fallback_price,
                last_used_at=_float_or_none(raw.get("last_used_at")),
            )
        except (TypeError, ValueError):
            return None

    def is_expired(self, now: Optional[float] = None) -> bool:
        if self.expires_at is None:
            return False
        return (now if now is not None else time.time()) >= self.expires_at

    def allows_model(self, model: str) -> bool:
        if not self.allowed_models:
            return True
        candidate = str(model or "").strip().lower()
        if not candidate:
            # Requests without a resolvable model (for example ``GET
            # /v1/models``) are allowed; enforcement happens on inference.
            return True
        return any(
            fnmatch.fnmatchcase(candidate, pattern.strip().lower())
            for pattern in self.allowed_models
        )


class _SlidingWindow:
    """Sliding-window counter for RPM/TPM (single-process only)."""

    def __init__(self) -> None:
        self._events: Deque[Tuple[float, int]] = deque()
        self._total: int = 0

    def _prune(self, now: float) -> None:
        cutoff = now - RATE_WINDOW_SECONDS
        while self._events and self._events[0][0] <= cutoff:
            _, amount = self._events.popleft()
            self._total -= amount

    def add(self, amount: int = 1, now: Optional[float] = None) -> None:
        current = now if now is not None else time.monotonic()
        self._prune(current)
        self._events.append((current, max(0, int(amount))))
        self._total += max(0, int(amount))

    def current_total(self, now: Optional[float] = None) -> int:
        self._prune(now if now is not None else time.monotonic())
        return max(0, self._total)

    def seconds_until_slot_frees(self, now: Optional[float] = None) -> int:
        current = now if now is not None else time.monotonic()
        self._prune(current)
        if not self._events:
            return 1
        oldest_ts = self._events[0][0]
        return max(1, int(RATE_WINDOW_SECONDS - (current - oldest_ts)) + 1)


class VirtualKeyManager:
    """Loads, verifies, and enforces virtual API keys."""

    def __init__(self) -> None:
        self._keys_by_hash: Dict[str, VirtualKey] = {}
        self._loaded = False
        self._lock = asyncio.Lock()
        self._request_windows: Dict[str, _SlidingWindow] = {}
        self._token_windows: Dict[str, _SlidingWindow] = {}
        self._budget_cache: Dict[str, Tuple[float, float, float]] = {}

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    async def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        async with self._lock:
            if self._loaded:
                return
            from core.storage_adapter import get_storage_adapter

            storage_adapter = await get_storage_adapter()
            raw_keys = await storage_adapter.get_config(VIRTUAL_KEYS_CONFIG_KEY, [])
            keys: Dict[str, VirtualKey] = {}
            needs_migration = False
            invalid_record_found = False
            if isinstance(raw_keys, list):
                for raw in raw_keys:
                    record = VirtualKey.from_storage_dict(raw)
                    if record is not None:
                        keys[record.key_hash] = record
                        needs_migration = needs_migration or "schema_version" not in raw
                    else:
                        invalid_record_found = True
            self._keys_by_hash = keys
            self._loaded = True
            if needs_migration and not invalid_record_found:
                await storage_adapter.set_config(
                    VIRTUAL_KEYS_CONFIG_KEY,
                    [record.to_storage_dict() for record in keys.values()],
                )
            if keys:
                log.info(f"[virtual-keys] loaded {len(keys)} virtual API keys")

    async def _persist(self) -> None:
        from core.storage_adapter import get_storage_adapter

        storage_adapter = await get_storage_adapter()
        payload = [record.to_storage_dict() for record in self._keys_by_hash.values()]
        await storage_adapter.set_config(VIRTUAL_KEYS_CONFIG_KEY, payload)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    async def list_keys(self) -> List[Dict[str, Any]]:
        await self._ensure_loaded()
        records = sorted(self._keys_by_hash.values(), key=lambda item: item.created_at)
        return [record.to_public_dict() for record in records]

    async def create_key(
        self,
        name: str,
        *,
        budget_daily_usd: Optional[float] = None,
        budget_monthly_usd: Optional[float] = None,
        rpm_limit: Optional[int] = None,
        tpm_limit: Optional[int] = None,
        expires_at: Optional[float] = None,
        allowed_models: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None,
        unknown_pricing_policy: str = "deny",
        fallback_price_usd_per_million: Optional[float] = None,
    ) -> Tuple[Dict[str, Any], str]:
        """Create a key and return ``(public_record, plaintext_secret)``."""
        from config import API_KEY_PREFIX

        await self._ensure_loaded()
        clean_name = str(name or "").strip()
        if not clean_name:
            raise ValueError("Virtual key name is required.")
        normalized_scopes = normalize_virtual_key_scopes(
            list(DEFAULT_INFERENCE_SCOPES) if scopes is None else scopes
        )
        normalized_models = normalize_model_patterns(allowed_models or [])
        pricing_policy, fallback_price = normalize_unknown_pricing_policy(
            unknown_pricing_policy,
            fallback_price_usd_per_million,
        )

        plaintext = f"{API_KEY_PREFIX}vk-{secrets.token_hex(20)}"
        record = VirtualKey(
            id=f"{KEY_ID_PREFIX}{secrets.token_hex(6)}",
            name=clean_name[:128],
            key_hash=hash_key(plaintext),
            key_preview=_key_preview(plaintext),
            enabled=True,
            created_at=time.time(),
            expires_at=_float_or_none(expires_at),
            budget_daily_usd=_float_or_none(budget_daily_usd),
            budget_monthly_usd=_float_or_none(budget_monthly_usd),
            rpm_limit=_int_or_none(rpm_limit),
            tpm_limit=_int_or_none(tpm_limit),
            allowed_models=normalized_models,
            scopes=normalized_scopes,
            unknown_pricing_policy=pricing_policy,
            fallback_price_usd_per_million=fallback_price,
        )
        async with self._lock:
            self._keys_by_hash[record.key_hash] = record
            await self._persist()
        log.info(f"[virtual-keys] created key id={record.id} name={record.name!r}")
        return record.to_public_dict(), plaintext

    async def update_key(self, key_id: str, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        await self._ensure_loaded()
        async with self._lock:
            record = self._find_by_id_locked(key_id)
            if record is None:
                return None
            normalized_scopes = (
                normalize_virtual_key_scopes(patch.get("scopes")) if "scopes" in patch else None
            )
            normalized_models = (
                normalize_model_patterns(patch.get("allowed_models"))
                if "allowed_models" in patch
                else None
            )
            pricing_policy = record.unknown_pricing_policy
            fallback_price = record.fallback_price_usd_per_million
            if "unknown_pricing_policy" in patch or "fallback_price_usd_per_million" in patch:
                requested_policy = patch.get(
                    "unknown_pricing_policy", record.unknown_pricing_policy
                )
                if "fallback_price_usd_per_million" in patch:
                    requested_fallback = patch.get("fallback_price_usd_per_million")
                elif str(requested_policy).strip().lower() == "fallback":
                    requested_fallback = record.fallback_price_usd_per_million
                else:
                    requested_fallback = None
                pricing_policy, fallback_price = normalize_unknown_pricing_policy(
                    requested_policy,
                    requested_fallback,
                )
            if "name" in patch:
                new_name = str(patch.get("name") or "").strip()
                if new_name:
                    record.name = new_name[:128]
            if "enabled" in patch:
                record.enabled = bool(patch.get("enabled"))
            if "budget_daily_usd" in patch:
                record.budget_daily_usd = _float_or_none(patch.get("budget_daily_usd"))
            if "budget_monthly_usd" in patch:
                record.budget_monthly_usd = _float_or_none(patch.get("budget_monthly_usd"))
            if "rpm_limit" in patch:
                record.rpm_limit = _int_or_none(patch.get("rpm_limit"))
            if "tpm_limit" in patch:
                record.tpm_limit = _int_or_none(patch.get("tpm_limit"))
            if "expires_at" in patch:
                record.expires_at = _float_or_none(patch.get("expires_at"))
            if "allowed_models" in patch:
                record.allowed_models = normalized_models or []
            if normalized_scopes is not None:
                record.scopes = normalized_scopes
            record.unknown_pricing_policy = pricing_policy
            record.fallback_price_usd_per_million = fallback_price
            await self._persist()
            return record.to_public_dict()

    async def delete_key(self, key_id: str) -> bool:
        await self._ensure_loaded()
        async with self._lock:
            record = self._find_by_id_locked(key_id)
            if record is None:
                return False
            self._keys_by_hash.pop(record.key_hash, None)
            self._request_windows.pop(record.id, None)
            self._token_windows.pop(record.id, None)
            self._budget_cache = {
                cache_key: value
                for cache_key, value in self._budget_cache.items()
                if not cache_key.startswith(f"{record.id}:")
            }
            await self._persist()
            log.info(f"[virtual-keys] deleted key id={record.id}")
            return True

    def _find_by_id_locked(self, key_id: str) -> Optional[VirtualKey]:
        for record in self._keys_by_hash.values():
            if record.id == key_id:
                return record
        return None

    # ------------------------------------------------------------------
    # Verification and enforcement
    # ------------------------------------------------------------------

    async def verify(self, token: str) -> Optional[VirtualKey]:
        """Constant-time hash comparison against every stored key."""
        await self._ensure_loaded()
        candidate_hash = hash_key(token)
        matched: Optional[VirtualKey] = None
        for stored_hash, record in self._keys_by_hash.items():
            if secrets.compare_digest(candidate_hash, stored_hash):
                matched = record
        return matched

    @staticmethod
    def _enforce_active(record: VirtualKey) -> None:
        """Reject disabled or expired keys before evaluating any permission."""
        now = time.time()
        if not record.enabled:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This API key has been disabled.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if record.is_expired(now):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This API key has expired.",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def enforce(
        self,
        record: VirtualKey,
        *,
        protocol: str = "openai",
        requested_model: str = "",
    ) -> None:
        """Raise :class:`HTTPException` when the key may not serve this call."""
        now = time.time()
        self._enforce_active(record)
        required_scope = f"inference:{str(protocol or '').strip().lower()}"
        if required_scope not in INFERENCE_SCOPES or required_scope not in record.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This API key is not allowed to use the requested inference protocol.",
            )
        if not record.allows_model(requested_model):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This API key is not allowed to access model '{requested_model}'.",
            )

        self._enforce_rate_limits(record)
        await self._enforce_budgets(record, now)

        # Count this request in the RPM window only after all checks pass.
        self._request_windows.setdefault(record.id, _SlidingWindow()).add(1)

    def authorize_management(self, record: VirtualKey, *, write: bool) -> None:
        """Authorize a management read or write without consuming inference limits."""
        self._enforce_active(record)
        required_scope = "management:write" if write else "management:read"
        if required_scope not in record.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This API key does not have the required management scope.",
            )

    async def note_last_used(self, record: VirtualKey, *, now: Optional[float] = None) -> None:
        """Persist bounded last-used metadata without writing on every request."""
        current = now if now is not None else time.time()
        async with self._lock:
            if (
                record.last_used_at is not None
                and current - record.last_used_at < LAST_USED_PERSIST_INTERVAL_SECONDS
            ):
                return
            record.last_used_at = current
            await self._persist()

    def _enforce_rate_limits(self, record: VirtualKey) -> None:
        if record.rpm_limit is not None:
            window = self._request_windows.setdefault(record.id, _SlidingWindow())
            if window.current_total() >= record.rpm_limit:
                retry_after = window.seconds_until_slot_frees()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Rate limit exceeded: {record.rpm_limit} requests per minute "
                        "for this API key."
                    ),
                    headers={"Retry-After": str(retry_after)},
                )
        if record.tpm_limit is not None:
            token_window = self._token_windows.setdefault(record.id, _SlidingWindow())
            if token_window.current_total() >= record.tpm_limit:
                retry_after = token_window.seconds_until_slot_frees()
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Token rate limit exceeded: {record.tpm_limit} tokens per minute "
                        "for this API key."
                    ),
                    headers={"Retry-After": str(retry_after)},
                )

    async def _enforce_budgets(self, record: VirtualKey, now: float) -> None:
        checks = (
            ("daily", record.budget_daily_usd, DAILY_WINDOW_SECONDS),
            ("monthly", record.budget_monthly_usd, MONTHLY_WINDOW_SECONDS),
        )
        for window_name, limit_usd, window_seconds in checks:
            if limit_usd is None:
                continue
            spend = await self._get_cached_spend(record.id, window_name, window_seconds, now)
            if spend >= limit_usd:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Budget exceeded: this API key has spent ${spend:.4f} of its "
                        f"${limit_usd:.2f} {window_name} budget."
                    ),
                )

    async def _get_cached_spend(
        self, key_id: str, window_name: str, window_seconds: int, now: float
    ) -> float:
        cache_key = f"{key_id}:{window_name}"
        cached = self._budget_cache.get(cache_key)
        if cached is not None and (now - cached[0]) < BUDGET_CACHE_TTL_SECONDS:
            return cached[1]

        from core.usage_stats import get_spend_since

        spend_snapshot = await asyncio.to_thread(get_spend_since, now - window_seconds, key_id)
        spend = float(spend_snapshot.get("cost_usd") or 0.0)
        self._budget_cache[cache_key] = (now, spend, float(window_seconds))
        return spend

    def note_tokens(self, key_id: str, total_tokens: int) -> None:
        """Feed the TPM window after a completed call (fire-and-forget)."""
        if not key_id or total_tokens <= 0:
            return
        self._token_windows.setdefault(key_id, _SlidingWindow()).add(int(total_tokens))

    async def get_key_usage(self, key_id: str) -> Dict[str, Any]:
        """Spend snapshot used by the panel key list."""
        from core.usage_stats import get_spend_since

        now = time.time()
        daily = await asyncio.to_thread(get_spend_since, now - DAILY_WINDOW_SECONDS, key_id)
        monthly = await asyncio.to_thread(get_spend_since, now - MONTHLY_WINDOW_SECONDS, key_id)
        return {"daily": daily, "monthly": monthly}

    def reset_runtime_state(self) -> None:
        """Testing/maintenance hook: clear windows and caches, keep keys."""
        self._request_windows.clear()
        self._token_windows.clear()
        self._budget_cache.clear()

    def invalidate(self) -> None:
        """Force a reload from storage on next access."""
        self._loaded = False


def extract_requested_model(path: str, body: Any) -> str:
    """Best-effort extraction of the requested model for allowlist checks."""
    match = _GEMINI_MODEL_PATH_RE.search(str(path or ""))
    if match:
        return match.group(1)
    if isinstance(body, dict):
        return str(body.get("model") or "")
    return ""


virtual_key_manager = VirtualKeyManager()
