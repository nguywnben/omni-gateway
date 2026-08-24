"""Lifecycle and write boundary for durable management audit evidence."""

from __future__ import annotations

import asyncio
import base64
import binascii
import hashlib
import hmac
import secrets
from typing import Any

from core.audit import AuditEvent, AuditRepository, create_audit_event
from core.management_audit import ManagementMutation

AUDIT_MASTER_KEY_CONFIG = "_internal_audit_master_key_v1"
_MASTER_KEY_BYTES = 32
_FINGERPRINT_DOMAIN = b"omni-gateway:audit:fingerprint:v1"
_CURSOR_DOMAIN = b"omni-gateway:audit:cursor:v1"


def _encode_master_key(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii")


def _decode_master_key(value: Any) -> bytes:
    if not isinstance(value, str) or len(value) > 128:
        raise RuntimeError("Stored audit master key is invalid.")
    try:
        decoded = base64.b64decode(
            value,
            altchars=b"-_",
            validate=True,
        )
    except (ValueError, binascii.Error) as exc:
        raise RuntimeError("Stored audit master key is invalid.") from exc
    if len(decoded) != _MASTER_KEY_BYTES or _encode_master_key(decoded) != value:
        raise RuntimeError("Stored audit master key is invalid.")
    return decoded


def _derive_key(master_key: bytes, domain: bytes) -> bytes:
    return hmac.new(master_key, domain, hashlib.sha256).digest()


class AuditService:
    """Create redacted immutable events and append them to selected durable storage."""

    def __init__(self, repository: AuditRepository, *, fingerprint_key: bytes) -> None:
        self._repository = repository
        self._fingerprint_key = fingerprint_key

    @classmethod
    async def create(cls, storage: Any) -> "AuditService":
        encoded_master = await storage.get_config(AUDIT_MASTER_KEY_CONFIG, None)
        if encoded_master is None:
            encoded_master = _encode_master_key(secrets.token_bytes(_MASTER_KEY_BYTES))
            if not await storage.set_config(AUDIT_MASTER_KEY_CONFIG, encoded_master):
                raise RuntimeError("Unable to persist the audit master key.")
            encoded_master = await storage.get_config(AUDIT_MASTER_KEY_CONFIG, None)
        master_key = _decode_master_key(encoded_master)
        cursor_key = _derive_key(master_key, _CURSOR_DOMAIN)
        repository = await storage.create_audit_repository(
            cursor_signing_key=cursor_key,
        )
        return cls(
            repository,
            fingerprint_key=_derive_key(master_key, _FINGERPRINT_DOMAIN),
        )

    async def record(
        self,
        mutation: ManagementMutation,
        *,
        request_id: str,
        actor_type: str,
        actor_identifier: str,
        outcome: str,
    ) -> AuditEvent:
        if not isinstance(mutation, ManagementMutation) or not mutation.target_identifier:
            raise ValueError("A classified management mutation is required.")
        event = create_audit_event(
            request_id=request_id,
            actor_type=actor_type,
            actor_identifier=actor_identifier,
            action=mutation.action,
            target_type=mutation.target_type,
            target_identifier=mutation.target_identifier,
            outcome=outcome,
            change_codes=mutation.change_codes,
            fingerprint_key=self._fingerprint_key,
        )
        await self._repository.append(event)
        return event


_audit_service: AuditService | None = None
_audit_service_lock = asyncio.Lock()


async def initialize_audit_service(storage: Any | None = None) -> AuditService:
    global _audit_service
    async with _audit_service_lock:
        if _audit_service is None:
            if storage is None:
                from core.storage_adapter import get_storage_adapter

                storage = await get_storage_adapter()
            _audit_service = await AuditService.create(storage)
        return _audit_service


def get_audit_service() -> AuditService:
    if _audit_service is None:
        raise RuntimeError("Audit service is not initialized.")
    return _audit_service


_CREDENTIAL_ACTIONS = {
    "enable": ("credential.toggle", "enabled"),
    "disable": ("credential.toggle", "disabled"),
    "delete": ("credential.delete", "deleted"),
    "enable_credit": ("credential.credit_mode", "enabled"),
    "disable_credit": ("credential.credit_mode", "disabled"),
}
_CREDENTIAL_OUTCOMES = {
    "succeeded": "succeeded",
    "unsupported": "invalid",
    "not_found": "not_found",
    "invalid": "invalid",
    "duplicate": "conflict",
    "timed_out": "timed_out",
    "failed": "failed",
    "cancelled": "cancelled",
    "unknown": "failed",
}


async def record_credential_response(
    *,
    request_id: str,
    action: str,
    mode: str,
    filename: str,
    outcome: str,
) -> AuditEvent:
    """Bridge one W2 per-target credential result into durable audit storage."""

    try:
        audit_action, change_code = _CREDENTIAL_ACTIONS[action]
        audit_outcome = _CREDENTIAL_OUTCOMES[outcome]
    except KeyError as exc:
        raise ValueError("Unsupported credential audit evidence.") from exc
    mutation = ManagementMutation(
        action=audit_action,
        target_type="credential",
        change_codes=(change_code,),
        target_identifier=f"{mode}:{filename}",
    )
    return await get_audit_service().record(
        mutation,
        request_id=request_id,
        actor_type="panel_session",
        actor_identifier="panel-owner",
        outcome=audit_outcome,
    )


async def close_audit_service() -> None:
    global _audit_service
    async with _audit_service_lock:
        _audit_service = None
