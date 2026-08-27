"""Opaque, revocable management-session contract and standalone implementation."""

from __future__ import annotations

import asyncio
import base64
import binascii
import hashlib
import hmac
import math
import os
import re
import secrets
import threading
from collections import Counter
from dataclasses import dataclass, replace
from enum import StrEnum
from typing import Any, Protocol

from core.identity.authorization import ManagementPrincipal
from core.identity.repository import LOCAL_OWNER_ID, ManagedIdentity

SESSION_SCHEMA_VERSION = 1
SESSION_TOKEN_PREFIX = "ogs_"
SESSION_TOKEN_BYTES = 32
MIN_SESSION_TTL_SECONDS = 300
MAX_SESSION_TTL_SECONDS = 2_592_000

_SESSION_TOKEN_PATTERN = re.compile(r"^ogs_[A-Za-z0-9_-]{43}$")
_SESSION_DIGEST_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_SESSION_HMAC_DOMAIN = b"omni-gateway:management-session:v1\0"
_SESSION_MASTER_KEY_CONFIG = "_internal_session_master_key_v1"
_SESSION_MASTER_KEY_BYTES = 32
_SESSION_METRIC_ACTIONS = frozenset({"issue", "resolve", "revoke", "revoke_principal"})
_SESSION_METRIC_OUTCOMES = frozenset({"succeeded", "not_found", "expired", "stale", "failed"})
_session_metric_lock = threading.Lock()
_session_metrics: Counter[tuple[str, str]] = Counter()


class SessionError(RuntimeError):
    """Base error for a session that cannot authorize a request."""


class SessionNotFound(SessionError):
    pass


class SessionExpired(SessionError):
    pass


class SessionStale(SessionError):
    pass


class SessionAuthenticationMethod(StrEnum):
    LOCAL_PASSWORD = "local_password"
    OIDC = "oidc"


def _record_session_metric(action: str, outcome: str) -> None:
    if action not in _SESSION_METRIC_ACTIONS or outcome not in _SESSION_METRIC_OUTCOMES:
        raise ValueError("Session metric dimensions are invalid.")
    with _session_metric_lock:
        _session_metrics[(action, outcome)] += 1


def render_management_session_metrics() -> str:
    """Render only closed low-cardinality management-session outcomes."""
    with _session_metric_lock:
        snapshot = dict(_session_metrics)
    lines = [
        "# HELP omni_management_session_operations_total Management session lifecycle outcomes.",
        "# TYPE omni_management_session_operations_total counter",
    ]
    for (action, outcome), count in sorted(snapshot.items()):
        lines.append(
            "omni_management_session_operations_total"
            f'{{action="{action}",outcome="{outcome}"}} {count}'
        )
    return "\n".join(lines) + "\n"


def _strict_timestamp(value: object, label: str) -> float:
    if type(value) not in {int, float}:
        raise ValueError(f"{label} is invalid.")
    timestamp = float(value)
    if not math.isfinite(timestamp) or timestamp < 0:
        raise ValueError(f"{label} is invalid.")
    return timestamp


@dataclass(frozen=True, slots=True)
class SessionPolicy:
    idle_ttl_seconds: int
    absolute_ttl_seconds: int

    def __post_init__(self) -> None:
        if type(self.idle_ttl_seconds) is not int or not (
            MIN_SESSION_TTL_SECONDS <= self.idle_ttl_seconds <= MAX_SESSION_TTL_SECONDS
        ):
            raise ValueError("Session idle lifetime is invalid.")
        if type(self.absolute_ttl_seconds) is not int or not (
            MIN_SESSION_TTL_SECONDS <= self.absolute_ttl_seconds <= MAX_SESSION_TTL_SECONDS
        ):
            raise ValueError("Session absolute lifetime is invalid.")
        if self.absolute_ttl_seconds <= self.idle_ttl_seconds:
            raise ValueError("Session absolute lifetime must exceed its idle lifetime.")


@dataclass(frozen=True, slots=True)
class SessionRecord:
    schema_version: int
    digest: str
    principal: ManagementPrincipal
    issued_at: float
    last_seen_at: float
    idle_expires_at: float
    absolute_expires_at: float
    authentication_method: SessionAuthenticationMethod
    authorization_epoch: int

    def __post_init__(self) -> None:
        if type(self.schema_version) is not int or self.schema_version != SESSION_SCHEMA_VERSION:
            raise ValueError("Session schema version is unsupported.")
        if type(self.digest) is not str or not _SESSION_DIGEST_PATTERN.fullmatch(self.digest):
            raise ValueError("Session digest is invalid.")
        if type(self.principal) is not ManagementPrincipal:
            raise ValueError("Session principal is invalid.")
        if type(self.authentication_method) is not SessionAuthenticationMethod:
            raise ValueError("Session authentication method is invalid.")
        if type(self.authorization_epoch) is not int or self.authorization_epoch < 1:
            raise ValueError("Session authorization epoch is invalid.")
        issued_at = _strict_timestamp(self.issued_at, "Session issue timestamp")
        last_seen_at = _strict_timestamp(self.last_seen_at, "Session last-seen timestamp")
        idle_expires_at = _strict_timestamp(self.idle_expires_at, "Session idle expiry")
        absolute_expires_at = _strict_timestamp(
            self.absolute_expires_at,
            "Session absolute expiry",
        )
        if not (
            issued_at <= last_seen_at < idle_expires_at <= absolute_expires_at
            and issued_at < absolute_expires_at
        ):
            raise ValueError("Session timestamps are inconsistent.")

    def __repr__(self) -> str:
        return (
            "SessionRecord("
            f"schema_version={self.schema_version!r}, principal={self.principal!r}, "
            f"issued_at={self.issued_at!r}, last_seen_at={self.last_seen_at!r}, "
            f"idle_expires_at={self.idle_expires_at!r}, "
            f"absolute_expires_at={self.absolute_expires_at!r}, "
            f"authentication_method={self.authentication_method!r}, "
            f"authorization_epoch={self.authorization_epoch!r})"
        )


@dataclass(frozen=True, slots=True)
class IssuedSession:
    token: str
    session: SessionRecord

    def __repr__(self) -> str:
        return f"IssuedSession(token='<redacted>', session={self.session!r})"


class SessionStore(Protocol):
    async def issue(
        self,
        *,
        principal: ManagementPrincipal,
        authentication_method: SessionAuthenticationMethod,
        authorization_epoch: int,
        now: float,
    ) -> IssuedSession: ...

    async def resolve(
        self,
        token: str,
        *,
        current_authorization_epoch: int,
        now: float,
    ) -> SessionRecord: ...

    async def rotate(
        self,
        token: str,
        *,
        principal: ManagementPrincipal,
        authentication_method: SessionAuthenticationMethod,
        authorization_epoch: int,
        now: float,
    ) -> IssuedSession: ...

    async def revoke(self, token: str) -> bool: ...

    async def revoke_principal(self, principal: ManagementPrincipal) -> int: ...


class InProcessSessionStore:
    """Atomic single-process store that never retains a plaintext session token."""

    def __init__(self, *, hmac_key: bytes, policy: SessionPolicy) -> None:
        if type(hmac_key) is not bytes or len(hmac_key) < 32:
            raise ValueError("Session HMAC key must contain at least 32 bytes.")
        if type(policy) is not SessionPolicy:
            raise ValueError("A validated session policy is required.")
        self._hmac_key = hmac_key
        self._policy = policy
        self._sessions: dict[str, SessionRecord] = {}
        self._lock = asyncio.Lock()

    def __repr__(self) -> str:
        return (
            "InProcessSessionStore("
            f"policy={self._policy!r}, active_sessions={len(self._sessions)!r})"
        )

    def _digest(self, token: str) -> str:
        return hmac.digest(
            self._hmac_key,
            _SESSION_HMAC_DOMAIN + token.encode("ascii"),
            hashlib.sha256,
        ).hex()

    @staticmethod
    def _validated_token(token: object) -> str:
        if type(token) is not str or not _SESSION_TOKEN_PATTERN.fullmatch(token):
            raise SessionNotFound("Session is unavailable.")
        return token

    @staticmethod
    def _validated_issue_inputs(
        principal: object,
        authentication_method: object,
        authorization_epoch: object,
        now: object,
    ) -> tuple[ManagementPrincipal, SessionAuthenticationMethod, int, float]:
        if type(principal) is not ManagementPrincipal:
            raise ValueError("A validated session principal is required.")
        if type(authentication_method) is not SessionAuthenticationMethod:
            raise ValueError("A validated session authentication method is required.")
        if type(authorization_epoch) is not int or authorization_epoch < 1:
            raise ValueError("Session authorization epoch is invalid.")
        return (
            principal,
            authentication_method,
            authorization_epoch,
            _strict_timestamp(now, "Session timestamp"),
        )

    def _issue_locked(
        self,
        *,
        principal: ManagementPrincipal,
        authentication_method: SessionAuthenticationMethod,
        authorization_epoch: int,
        now: float,
    ) -> IssuedSession:
        for _attempt in range(4):
            token = SESSION_TOKEN_PREFIX + secrets.token_urlsafe(SESSION_TOKEN_BYTES)
            digest = self._digest(token)
            if digest not in self._sessions:
                break
        else:
            raise RuntimeError("Unable to allocate a unique session.")
        absolute_expires_at = now + self._policy.absolute_ttl_seconds
        record = SessionRecord(
            schema_version=SESSION_SCHEMA_VERSION,
            digest=digest,
            principal=principal,
            issued_at=now,
            last_seen_at=now,
            idle_expires_at=min(
                now + self._policy.idle_ttl_seconds,
                absolute_expires_at,
            ),
            absolute_expires_at=absolute_expires_at,
            authentication_method=authentication_method,
            authorization_epoch=authorization_epoch,
        )
        self._sessions[digest] = record
        return IssuedSession(token=token, session=record)

    def _resolve_locked(
        self,
        token: str,
        *,
        current_authorization_epoch: int | None,
        now: float,
        touch: bool,
    ) -> SessionRecord:
        digest = self._digest(token)
        record = self._sessions.get(digest)
        if record is None:
            raise SessionNotFound("Session is unavailable.")
        if now >= record.idle_expires_at or now >= record.absolute_expires_at:
            self._sessions.pop(digest, None)
            raise SessionExpired("Session expired.")
        if (
            current_authorization_epoch is not None
            and current_authorization_epoch != record.authorization_epoch
        ):
            self._sessions.pop(digest, None)
            raise SessionStale("Session authorization is stale.")
        if not touch:
            return record
        updated = replace(
            record,
            last_seen_at=now,
            idle_expires_at=min(
                now + self._policy.idle_ttl_seconds,
                record.absolute_expires_at,
            ),
        )
        self._sessions[digest] = updated
        return updated

    async def issue(
        self,
        *,
        principal: ManagementPrincipal,
        authentication_method: SessionAuthenticationMethod,
        authorization_epoch: int,
        now: float,
    ) -> IssuedSession:
        principal, authentication_method, authorization_epoch, now = self._validated_issue_inputs(
            principal,
            authentication_method,
            authorization_epoch,
            now,
        )
        async with self._lock:
            return self._issue_locked(
                principal=principal,
                authentication_method=authentication_method,
                authorization_epoch=authorization_epoch,
                now=now,
            )

    async def resolve(
        self,
        token: str,
        *,
        current_authorization_epoch: int,
        now: float,
    ) -> SessionRecord:
        token = self._validated_token(token)
        if type(current_authorization_epoch) is not int or current_authorization_epoch < 1:
            raise ValueError("Session authorization epoch is invalid.")
        now = _strict_timestamp(now, "Session timestamp")
        async with self._lock:
            return self._resolve_locked(
                token,
                current_authorization_epoch=current_authorization_epoch,
                now=now,
                touch=True,
            )

    async def rotate(
        self,
        token: str,
        *,
        principal: ManagementPrincipal,
        authentication_method: SessionAuthenticationMethod,
        authorization_epoch: int,
        now: float,
    ) -> IssuedSession:
        token = self._validated_token(token)
        principal, authentication_method, authorization_epoch, now = self._validated_issue_inputs(
            principal,
            authentication_method,
            authorization_epoch,
            now,
        )
        async with self._lock:
            existing = self._resolve_locked(
                token,
                current_authorization_epoch=None,
                now=now,
                touch=False,
            )
            self._sessions.pop(existing.digest, None)
            return self._issue_locked(
                principal=principal,
                authentication_method=authentication_method,
                authorization_epoch=authorization_epoch,
                now=now,
            )

    async def revoke(self, token: str) -> bool:
        try:
            token = self._validated_token(token)
        except SessionNotFound:
            return False
        async with self._lock:
            return self._sessions.pop(self._digest(token), None) is not None

    async def revoke_principal(self, principal: ManagementPrincipal) -> int:
        if type(principal) is not ManagementPrincipal:
            raise ValueError("A validated session principal is required.")
        async with self._lock:
            digests = [
                digest for digest, record in self._sessions.items() if record.principal == principal
            ]
            for digest in digests:
                self._sessions.pop(digest, None)
            return len(digests)


def _encode_master_key(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _decode_master_key(value: Any) -> bytes:
    if not isinstance(value, str) or len(value) > 128:
        raise RuntimeError("Stored session master key is invalid.")
    try:
        decoded = base64.b64decode(value, altchars=b"-_", validate=True)
    except (ValueError, binascii.Error) as exc:
        raise RuntimeError("Stored session master key is invalid.") from exc
    if len(decoded) != _SESSION_MASTER_KEY_BYTES or _encode_master_key(decoded) != value:
        raise RuntimeError("Stored session master key is invalid.")
    return decoded


def _env_lifetime(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(value, maximum))


def get_session_policy() -> SessionPolicy:
    """Build the bounded standalone policy while retaining the legacy TTL setting."""

    absolute_ttl = _env_lifetime(
        "PANEL_SESSION_TTL_SECONDS",
        86_400,
        MIN_SESSION_TTL_SECONDS + 1,
        MAX_SESSION_TTL_SECONDS,
    )
    idle_ttl = _env_lifetime(
        "PANEL_SESSION_IDLE_TTL_SECONDS",
        1_800,
        MIN_SESSION_TTL_SECONDS,
        absolute_ttl - 1,
    )
    return SessionPolicy(
        idle_ttl_seconds=idle_ttl,
        absolute_ttl_seconds=absolute_ttl,
    )


class SessionService:
    """Bind opaque runtime sessions to durable identity authorization epochs."""

    def __init__(self, store: SessionStore, *, identity_repository: Any) -> None:
        self._store = store
        self._identity_repository = identity_repository

    def __repr__(self) -> str:
        return f"SessionService(store={self._store!r})"

    @classmethod
    async def create(
        cls,
        storage: Any,
        *,
        policy: SessionPolicy | None = None,
    ) -> SessionService:
        selected_policy = policy or get_session_policy()
        encoded_master = await storage.get_config(_SESSION_MASTER_KEY_CONFIG, None)
        if encoded_master is None:
            generated = _encode_master_key(secrets.token_bytes(_SESSION_MASTER_KEY_BYTES))
            if not await storage.set_config(_SESSION_MASTER_KEY_CONFIG, generated):
                raise RuntimeError("Unable to persist the session master key.")
            encoded_master = await storage.get_config(_SESSION_MASTER_KEY_CONFIG, None)
        master_key = _decode_master_key(encoded_master)
        session_key = hmac.digest(
            master_key,
            _SESSION_HMAC_DOMAIN + b"index-key",
            hashlib.sha256,
        )
        identity_repository = await storage.create_identity_repository()
        return cls(
            InProcessSessionStore(hmac_key=session_key, policy=selected_policy),
            identity_repository=identity_repository,
        )

    async def _local_owner(self) -> ManagedIdentity:
        owner = await self._identity_repository.get_identity(LOCAL_OWNER_ID)
        if type(owner) is not ManagedIdentity or not owner.identity.enabled:
            raise RuntimeError("The local-owner recovery identity is unavailable.")
        return owner

    async def issue_local_owner(self, *, now: float) -> IssuedSession:
        try:
            owner = await self._local_owner()
            issued = await self._store.issue(
                principal=ManagementPrincipal.local_owner(owner.identity.identity_id),
                authentication_method=SessionAuthenticationMethod.LOCAL_PASSWORD,
                authorization_epoch=owner.identity.authorization_epoch,
                now=now,
            )
        except Exception:
            _record_session_metric("issue", "failed")
            raise
        _record_session_metric("issue", "succeeded")
        return issued

    async def resolve(self, token: str, *, now: float) -> SessionRecord:
        try:
            owner = await self._local_owner()
            resolved = await self._store.resolve(
                token,
                current_authorization_epoch=owner.identity.authorization_epoch,
                now=now,
            )
        except SessionExpired:
            _record_session_metric("resolve", "expired")
            raise
        except SessionStale:
            _record_session_metric("resolve", "stale")
            raise
        except SessionNotFound:
            _record_session_metric("resolve", "not_found")
            raise
        except Exception:
            _record_session_metric("resolve", "failed")
            raise
        _record_session_metric("resolve", "succeeded")
        return resolved

    async def revoke(self, token: str) -> bool:
        try:
            revoked = await self._store.revoke(token)
        except Exception:
            _record_session_metric("revoke", "failed")
            raise
        _record_session_metric("revoke", "succeeded" if revoked else "not_found")
        return revoked

    async def revoke_local_owner_sessions(self) -> int:
        try:
            owner = await self._local_owner()
            revoked = await self._store.revoke_principal(
                ManagementPrincipal.local_owner(owner.identity.identity_id)
            )
        except Exception:
            _record_session_metric("revoke_principal", "failed")
            raise
        _record_session_metric("revoke_principal", "succeeded")
        return revoked


_session_service: SessionService | None = None
_session_service_lock = asyncio.Lock()


async def initialize_session_service(storage: Any | None = None) -> SessionService:
    global _session_service
    async with _session_service_lock:
        if _session_service is None:
            if storage is None:
                from core.storage_adapter import get_storage_adapter

                storage = await get_storage_adapter()
            _session_service = await SessionService.create(storage)
        return _session_service


def get_session_service() -> SessionService:
    if _session_service is None:
        raise RuntimeError("Session service is not initialized.")
    return _session_service


async def close_session_service() -> None:
    global _session_service
    async with _session_service_lock:
        _session_service = None
