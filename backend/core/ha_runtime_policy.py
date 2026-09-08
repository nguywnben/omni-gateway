"""Closed, side-effect-free runtime topology policy for the HA lifecycle."""

from __future__ import annotations

import base64
import binascii
import os
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Mapping
from urllib.parse import urlsplit

from core.coordination import MAX_COORDINATION_INTEGER, validate_deployment_namespace

_DEPLOYMENT_ID = re.compile(r"[a-z0-9](?:[a-z0-9-]{6,62}[a-z0-9])")
_COORDINATED_FIELDS = (
    "OMNI_COORDINATION_NAMESPACE",
    "OMNI_DEPLOYMENT_ID",
    "OMNI_COORDINATION_KEY",
    "OMNI_COORDINATION_EPOCH",
)


class RuntimeMode(StrEnum):
    STANDALONE = "standalone"
    COORDINATED = "coordinated"


def _value(environment: Mapping[str, str], name: str, default: str = "") -> str:
    raw = environment.get(name, default)
    if not isinstance(raw, str):
        raise RuntimeError(f"{name} must be text.")
    return raw.strip()


def _positive_integer(environment: Mapping[str, str], name: str, default: str) -> int:
    raw = _value(environment, name, default)
    if not raw.isascii() or not raw.isdigit() or raw.startswith("0"):
        raise RuntimeError(f"{name} must be a positive integer.")
    value = int(raw)
    if not 1 <= value <= MAX_COORDINATION_INTEGER:
        raise RuntimeError(f"{name} is outside the supported range.")
    return value


def _redis_url(value: str) -> str:
    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError:
        raise RuntimeError("REDIS_URL is invalid.") from None
    valid_location = bool(parsed.path) if parsed.scheme == "unix" else bool(parsed.hostname)
    if parsed.scheme not in {"redis", "rediss", "unix"} or not valid_location or parsed.fragment:
        raise RuntimeError("REDIS_URL must be a redis, rediss, or unix URL without a fragment.")
    return value


def _coordination_key(value: str) -> bytes:
    try:
        padded = value + ("=" * (-len(value) % 4))
        decoded = base64.b64decode(padded, altchars=b"-_", validate=True)
    except (ValueError, binascii.Error):
        raise RuntimeError("OMNI_COORDINATION_KEY must be canonical base64url.") from None
    canonical = base64.urlsafe_b64encode(decoded).decode("ascii").rstrip("=")
    if canonical != value.rstrip("=") or not 32 <= len(decoded) <= 64:
        raise RuntimeError("OMNI_COORDINATION_KEY must decode to 32-64 bytes.")
    return decoded


@dataclass(frozen=True, slots=True)
class HaRuntimePolicy:
    mode: RuntimeMode
    workers: int
    replicas: int
    durable_backend: str
    redis_url: str | None = field(default=None, repr=False)
    coordination_namespace: str | None = field(default=None, repr=False)
    deployment_id: str | None = field(default=None, repr=False)
    coordination_key: bytes | None = field(default=None, repr=False)
    fencing_epoch: int = 1

    @classmethod
    def from_environment(
        cls,
        environment: Mapping[str, str] | None = None,
        *,
        topology_verifier: Callable[[RuntimeMode, int], bool] | None = None,
    ) -> HaRuntimePolicy:
        selected = os.environ if environment is None else environment
        raw_mode = _value(selected, "OMNI_RUNTIME_MODE", RuntimeMode.STANDALONE.value)
        try:
            mode = RuntimeMode(raw_mode)
        except ValueError:
            raise RuntimeError("OMNI_RUNTIME_MODE must be standalone or coordinated.") from None
        workers = _positive_integer(selected, "WORKERS", "1")
        replicas = _positive_integer(selected, "OMNI_REPLICA_COUNT", "1")
        if workers != 1:
            raise RuntimeError("WORKERS must remain 1 for the version-one coordination contract.")

        postgresql_uri = _value(selected, "POSTGRESQL_URI")
        mongodb_uri = _value(selected, "MONGODB_URI")
        if postgresql_uri and mongodb_uri:
            raise RuntimeError("Configure only one external durable backend.")
        durable_backend = "postgresql" if postgresql_uri else "mongodb" if mongodb_uri else "sqlite"
        redis_url = _value(selected, "REDIS_URL")

        if mode is RuntimeMode.STANDALONE:
            if replicas != 1:
                raise RuntimeError("Standalone mode requires OMNI_REPLICA_COUNT=1.")
            if any(_value(selected, name) for name in _COORDINATED_FIELDS):
                raise RuntimeError(
                    "Coordination identity fields require OMNI_RUNTIME_MODE=coordinated."
                )
            return cls(mode, workers, replicas, durable_backend)

        replica_topology_accepted = replicas == 1 or bool(
            topology_verifier is not None and topology_verifier(mode, replicas)
        )
        if not replica_topology_accepted:
            raise RuntimeError(
                "Experimental coordinated mode currently requires OMNI_REPLICA_COUNT=1."
            )
        if durable_backend == "sqlite":
            raise RuntimeError("Coordinated mode requires PostgreSQL or MongoDB durable storage.")
        if not redis_url:
            raise RuntimeError("Coordinated mode requires REDIS_URL.")
        redis_url = _redis_url(redis_url)

        namespace = _value(selected, "OMNI_COORDINATION_NAMESPACE")
        deployment_id = _value(selected, "OMNI_DEPLOYMENT_ID")
        encoded_key = _value(selected, "OMNI_COORDINATION_KEY")
        if not namespace or not deployment_id or not encoded_key:
            raise RuntimeError("Coordinated identity configuration is incomplete.")
        try:
            namespace = validate_deployment_namespace(namespace)
        except ValueError:
            raise RuntimeError("OMNI_COORDINATION_NAMESPACE is invalid.") from None
        if not _DEPLOYMENT_ID.fullmatch(deployment_id):
            raise RuntimeError("OMNI_DEPLOYMENT_ID is invalid.")
        key = _coordination_key(encoded_key)
        epoch = _positive_integer(selected, "OMNI_COORDINATION_EPOCH", "")
        return cls(
            mode,
            workers,
            replicas,
            durable_backend,
            redis_url,
            namespace,
            deployment_id,
            key,
            epoch,
        )

    def safe_summary(self) -> dict[str, object]:
        """Return content-free topology evidence suitable for readiness and logs."""

        return {
            "mode": self.mode.value,
            "workers": self.workers,
            "replicas": self.replicas,
            "durable_backend": self.durable_backend,
            "coordination_configured": self.mode is RuntimeMode.COORDINATED,
            "fencing_epoch": self.fencing_epoch if self.mode is RuntimeMode.COORDINATED else None,
        }
