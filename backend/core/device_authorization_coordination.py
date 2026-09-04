"""Encrypted leased state machine for shared device authorization flows."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import re
import secrets
from collections.abc import Callable
from dataclasses import dataclass

from core.coordination import CasRequest, CoordinationStore, validate_epoch
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_FLOW_PATTERN = re.compile(r"^codex_[A-Za-z0-9_-]{43}$")
_LEASE_PATTERN = re.compile(r"^[A-Za-z0-9_-]{22}$")
_HMAC_DOMAIN = b"omni-gateway:device-authorization:v1\0"
_PAYLOAD_KEY_DOMAIN = b"omni-gateway:device-authorization-payload-key:v1\0"
_PAYLOAD_AAD = b"omni-gateway:device-authorization-payload:v1"
_MAX_PAYLOAD_BYTES = 8 * 1024
_MAX_CAS_RETRIES = 4


class DeviceAuthorizationError(RuntimeError):
    """Content-free boundary for invalid or unavailable device transactions."""

    def __init__(self) -> None:
        super().__init__("Device authorization transaction failed.")


class DeviceAuthorizationBusyError(DeviceAuthorizationError):
    """A valid transaction is currently leased by another poller."""


@dataclass(frozen=True, slots=True)
class DeviceAuthorizationClaim:
    """Lease proof and decrypted payload for one immediate provider poll."""

    flow_id: str
    lease_id: str
    revision: int
    lease_until_ms: int
    expires_at_ms: int
    payload: bytes

    def __repr__(self) -> str:
        return (
            "DeviceAuthorizationClaim(flow_id='<redacted>', lease_id='<redacted>', "
            f"revision={self.revision!r}, lease_until_ms={self.lease_until_ms!r}, "
            f"expires_at_ms={self.expires_at_ms!r}, payload='<redacted>')"
        )


def _flow_id(value: object) -> str:
    if type(value) is not str or not _FLOW_PATTERN.fullmatch(value):
        raise DeviceAuthorizationError
    return value


class DeviceAuthorizationService:
    """Coordinate device-flow create, claim, release, and consume operations."""

    __slots__ = (
        "_coordination",
        "_fencing_epoch",
        "_hmac_key",
        "_payload_key",
        "_token_factory",
    )

    def __init__(
        self,
        coordination: CoordinationStore,
        *,
        key: bytes,
        fencing_epoch: int,
        token_factory: Callable[[int], str] = secrets.token_urlsafe,
    ) -> None:
        try:
            if type(key) is not bytes or len(key) < 32 or not callable(token_factory):
                raise DeviceAuthorizationError
            validate_epoch(fencing_epoch)
            if any(
                not callable(getattr(coordination, method, None))
                for method in (
                    "compare_and_set",
                    "read_cas",
                    "read_coordination_time",
                )
            ):
                raise DeviceAuthorizationError
        except DeviceAuthorizationError:
            raise DeviceAuthorizationError from None
        except Exception:
            raise DeviceAuthorizationError from None
        self._coordination = coordination
        self._fencing_epoch = fencing_epoch
        self._token_factory = token_factory
        self._hmac_key = hmac.digest(key, _HMAC_DOMAIN + b"index-key", hashlib.sha256)
        self._payload_key = hmac.digest(key, _PAYLOAD_KEY_DOMAIN, hashlib.sha256)

    def __repr__(self) -> str:
        return (
            f"DeviceAuthorizationService(fencing_epoch={self._fencing_epoch!r}, key='<redacted>')"
        )

    @staticmethod
    def _operation_id(action: str) -> str:
        return f"device-auth-{action}-{secrets.token_hex(16)}"

    def _key(self, flow_id: str) -> str:
        digest = hmac.digest(
            self._hmac_key,
            _HMAC_DOMAIN + b"flow\0" + flow_id.encode("ascii"),
            hashlib.sha256,
        ).hex()
        return f"device-authorization-{digest}"

    def _encrypt(self, key: str, record: dict[str, object]) -> bytes:
        plaintext = json.dumps(
            record,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
        nonce = secrets.token_bytes(12)
        return (
            b"\x01"
            + nonce
            + AESGCM(self._payload_key).encrypt(
                nonce,
                plaintext,
                b"\0".join((_PAYLOAD_AAD, key.encode("ascii"))),
            )
        )

    def _decrypt(self, key: str, payload: bytes) -> dict[str, object]:
        try:
            if len(payload) < 30 or payload[0] != 1:
                raise ValueError
            plaintext = AESGCM(self._payload_key).decrypt(
                payload[1:13],
                payload[13:],
                b"\0".join((_PAYLOAD_AAD, key.encode("ascii"))),
            )
            pairs = json.loads(plaintext, object_pairs_hook=lambda values: values)
            if type(pairs) is not list or any(type(pair) is not tuple for pair in pairs):
                raise ValueError
            record = dict(pairs)
            if len(record) != len(pairs) or set(record) != {
                "expires_at_ms",
                "lease_id",
                "lease_until_ms",
                "payload",
                "schema_version",
                "status",
            }:
                raise ValueError
            status = record["status"]
            expires_at_ms = record["expires_at_ms"]
            lease_until_ms = record["lease_until_ms"]
            lease_id = record["lease_id"]
            encoded_payload = record["payload"]
            if (
                record["schema_version"] != 1
                or status not in {"ready", "leased", "consumed"}
                or type(expires_at_ms) is not int
                or expires_at_ms < 1
                or type(lease_until_ms) is not int
                or lease_until_ms < 0
                or type(lease_id) is not str
                or type(encoded_payload) is not str
            ):
                raise ValueError
            decoded_payload = base64.b64decode(encoded_payload, validate=True)
            if status == "leased":
                if (
                    not _LEASE_PATTERN.fullmatch(lease_id)
                    or lease_until_ms < 1
                    or not 1 <= len(decoded_payload) <= _MAX_PAYLOAD_BYTES
                ):
                    raise ValueError
            elif status == "ready":
                if (
                    lease_id
                    or lease_until_ms
                    or not 1 <= len(decoded_payload) <= _MAX_PAYLOAD_BYTES
                ):
                    raise ValueError
            elif lease_id or lease_until_ms or decoded_payload:
                raise ValueError
            record["decoded_payload"] = decoded_payload
            return record
        except Exception:
            raise DeviceAuthorizationError from None

    @staticmethod
    def _ttl_seconds(expires_at_ms: int, now_ms: int) -> float:
        remaining_ms = expires_at_ms - now_ms
        if remaining_ms < 1_000:
            raise DeviceAuthorizationError
        return remaining_ms / 1_000

    async def _now_ms(self) -> int:
        result = await self._coordination.read_coordination_time(epoch=self._fencing_epoch)
        return result.milliseconds

    async def create(self, payload: bytes, *, ttl_seconds: int | float) -> str:
        """Create an encrypted flow with an immutable absolute expiry."""
        try:
            if (
                type(payload) is not bytes
                or not 1 <= len(payload) <= _MAX_PAYLOAD_BYTES
                or isinstance(ttl_seconds, bool)
                or not isinstance(ttl_seconds, (int, float))
                or not 60 <= float(ttl_seconds) <= 900
            ):
                raise DeviceAuthorizationError
            token = self._token_factory(32)
            flow_id = _flow_id(f"codex_{token}")
            now_ms = await self._now_ms()
            expires_at_ms = now_ms + int(float(ttl_seconds) * 1_000)
            key = self._key(flow_id)
            record = {
                "expires_at_ms": expires_at_ms,
                "lease_id": "",
                "lease_until_ms": 0,
                "payload": base64.b64encode(payload).decode("ascii"),
                "schema_version": 1,
                "status": "ready",
            }
            result = await self._coordination.compare_and_set(
                CasRequest(
                    key,
                    0,
                    self._encrypt(key, record),
                    float(ttl_seconds),
                    self._fencing_epoch,
                    self._operation_id("create"),
                )
            )
            if not result.applied:
                raise DeviceAuthorizationError
            return flow_id
        except asyncio.CancelledError:
            raise
        except DeviceAuthorizationError:
            raise DeviceAuthorizationError from None
        except Exception:
            raise DeviceAuthorizationError from None

    async def claim(
        self,
        flow_id: str,
        *,
        lease_seconds: int | float,
    ) -> DeviceAuthorizationClaim:
        """Atomically lease one flow for a bounded provider poll."""
        try:
            flow_id = _flow_id(flow_id)
            if (
                isinstance(lease_seconds, bool)
                or not isinstance(lease_seconds, (int, float))
                or not 5 <= float(lease_seconds) <= 60
            ):
                raise DeviceAuthorizationError
            key = self._key(flow_id)
            for _attempt in range(_MAX_CAS_RETRIES):
                now_ms = await self._now_ms()
                snapshot = await self._coordination.read_cas(key, epoch=self._fencing_epoch)
                if snapshot.revision is None or snapshot.payload is None:
                    raise DeviceAuthorizationError
                record = self._decrypt(key, snapshot.payload)
                expires_at_ms = int(record["expires_at_ms"])
                ttl_seconds = self._ttl_seconds(expires_at_ms, now_ms)
                if record["status"] == "consumed":
                    raise DeviceAuthorizationError
                if record["status"] == "leased" and int(record["lease_until_ms"]) > now_ms:
                    raise DeviceAuthorizationBusyError
                lease_id = self._token_factory(16)
                if type(lease_id) is not str or not _LEASE_PATTERN.fullmatch(lease_id):
                    raise DeviceAuthorizationError
                lease_until_ms = min(
                    expires_at_ms,
                    now_ms + int(float(lease_seconds) * 1_000),
                )
                next_record = {
                    "expires_at_ms": expires_at_ms,
                    "lease_id": lease_id,
                    "lease_until_ms": lease_until_ms,
                    "payload": record["payload"],
                    "schema_version": 1,
                    "status": "leased",
                }
                result = await self._coordination.compare_and_set(
                    CasRequest(
                        key,
                        snapshot.revision,
                        self._encrypt(key, next_record),
                        ttl_seconds,
                        self._fencing_epoch,
                        self._operation_id("claim"),
                    )
                )
                if result.applied and result.revision is not None:
                    return DeviceAuthorizationClaim(
                        flow_id,
                        lease_id,
                        result.revision,
                        lease_until_ms,
                        expires_at_ms,
                        bytes(record["decoded_payload"]),
                    )
            raise DeviceAuthorizationError
        except asyncio.CancelledError:
            raise
        except DeviceAuthorizationBusyError:
            raise DeviceAuthorizationBusyError from None
        except DeviceAuthorizationError:
            raise DeviceAuthorizationError from None
        except Exception:
            raise DeviceAuthorizationError from None

    async def _finish(self, claim: DeviceAuthorizationClaim, *, consume: bool) -> None:
        try:
            if type(claim) is not DeviceAuthorizationClaim:
                raise DeviceAuthorizationError
            flow_id = _flow_id(claim.flow_id)
            if (
                not _LEASE_PATTERN.fullmatch(claim.lease_id)
                or type(claim.revision) is not int
                or claim.revision < 1
                or type(claim.payload) is not bytes
                or not 1 <= len(claim.payload) <= _MAX_PAYLOAD_BYTES
            ):
                raise DeviceAuthorizationError
            now_ms = await self._now_ms()
            if now_ms >= claim.lease_until_ms:
                raise DeviceAuthorizationError
            ttl_seconds = self._ttl_seconds(claim.expires_at_ms, now_ms)
            key = self._key(flow_id)
            next_record = {
                "expires_at_ms": claim.expires_at_ms,
                "lease_id": "",
                "lease_until_ms": 0,
                "payload": "" if consume else base64.b64encode(claim.payload).decode("ascii"),
                "schema_version": 1,
                "status": "consumed" if consume else "ready",
            }
            result = await self._coordination.compare_and_set(
                CasRequest(
                    key,
                    claim.revision,
                    self._encrypt(key, next_record),
                    ttl_seconds,
                    self._fencing_epoch,
                    self._operation_id("consume" if consume else "release"),
                )
            )
            if not result.applied:
                raise DeviceAuthorizationError
        except asyncio.CancelledError:
            raise
        except DeviceAuthorizationError:
            raise DeviceAuthorizationError from None
        except Exception:
            raise DeviceAuthorizationError from None

    async def release(self, claim: DeviceAuthorizationClaim) -> None:
        """Release a still-owned lease while retaining its absolute expiry."""
        await self._finish(claim, consume=False)

    async def consume(self, claim: DeviceAuthorizationClaim) -> None:
        """Consume a still-owned lease and erase its encrypted secret payload."""
        await self._finish(claim, consume=True)


_device_authorization_service: DeviceAuthorizationService | None = None


def configure_device_authorization_service(
    service: DeviceAuthorizationService | None,
) -> None:
    """Inject or clear the lifecycle-owned device authorization service."""
    if service is not None and type(service) is not DeviceAuthorizationService:
        raise DeviceAuthorizationError
    global _device_authorization_service
    _device_authorization_service = service


def get_device_authorization_service() -> DeviceAuthorizationService:
    """Return the lifecycle-owned service and fail closed before initialization."""
    service = _device_authorization_service
    if service is None:
        raise DeviceAuthorizationError
    return service
