"""Single ownership boundary for runtime coordination and HA readiness state."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from collections.abc import Callable
from enum import StrEnum
from typing import Any

from core.coordination_service import CoordinationService
from core.credential_batch_coordination import (
    CredentialBatchCoordinationService,
    configure_credential_batch_coordination_service,
)
from core.credential_manager import credential_manager
from core.device_authorization_coordination import (
    DeviceAuthorizationService,
    configure_device_authorization_service,
)
from core.governance_coordination import configure_governance_coordination
from core.ha_activation import verify_ha_activation_record
from core.ha_coordination_binding import CoordinationBindingManager
from core.ha_runtime_policy import HaRuntimePolicy, RuntimeMode
from core.identity import configure_oidc_transaction_coordination
from core.panel.auth_support import (
    AuthenticationAttemptService,
    configure_authentication_attempt_service,
)
from core.primary_session_coordination import (
    PrimarySessionCoordinator,
    configure_primary_session_coordinator,
)
from core.provider_authorization_coordination import (
    ProviderAuthorizationService,
    configure_provider_authorization_service,
)
from core.redis_state_store import RedisStateStore
from core.response_cache import response_cache_coordinator
from core.routing_coordination import RoutingCoordinationAdapter
from core.state_store import InMemoryStateStore
from core.virtual_keys import virtual_key_manager

_ROUTING_KEY_DOMAIN = b"omni-gateway:runtime-routing-identifiers:v1\0"
_ATTEMPT_KEY_DOMAIN = b"omni-gateway:runtime-auth-attempt-identifiers:v1\0"
_PRIMARY_SESSION_KEY_DOMAIN = b"omni-gateway:runtime-primary-session-identifiers:v1\0"
_PROVIDER_AUTHORIZATION_KEY_DOMAIN = b"omni-gateway:runtime-provider-authorization-identifiers:v1\0"
_DEVICE_AUTHORIZATION_KEY_DOMAIN = b"omni-gateway:runtime-device-authorization-identifiers:v1\0"
_CREDENTIAL_BATCH_KEY_DOMAIN = b"omni-gateway:runtime-credential-batch-identifiers:v1\0"


class HaRuntimeState(StrEnum):
    STARTING = "starting"
    STANDALONE_READY = "standalone_ready"
    COORDINATED_READY = "coordinated_ready"
    DRAINING = "draining"
    RECONCILING = "reconciling"
    UNAVAILABLE = "unavailable"
    CLOSED = "closed"


class HaRuntimeLifecycle:
    """Construct and inject exactly one coordination service before request traffic."""

    def __init__(
        self,
        *,
        policy: HaRuntimePolicy | None = None,
        standalone_store_factory: Callable[[], Any] = InMemoryStateStore,
        coordinated_store_factory: Callable[[HaRuntimePolicy], Any] | None = None,
        activation_verifier: Callable[[str], bool] | None = None,
    ) -> None:
        self.policy = policy or HaRuntimePolicy.from_environment()
        self.state = HaRuntimeState.STARTING
        self._standalone_store_factory = standalone_store_factory
        self._coordinated_store_factory = coordinated_store_factory or self._redis_store
        self._activation_verifier = activation_verifier or verify_ha_activation_record
        self._coordination_service: CoordinationService | None = None
        self._routing_coordination: RoutingCoordinationAdapter | None = None
        self._credential_manager_owner: Any | None = None
        self._binding_manager: CoordinationBindingManager | None = None
        self._failure_code = ""
        self._recovery_latched = False
        self._recovery_reason = ""

    @staticmethod
    def _redis_store(policy: HaRuntimePolicy) -> RedisStateStore:
        assert policy.redis_url is not None
        assert policy.coordination_namespace is not None
        return RedisStateStore(
            policy.redis_url,
            deployment_namespace=policy.coordination_namespace,
        )

    @property
    def coordination_service(self) -> CoordinationService | None:
        return self._coordination_service

    @property
    def session_initialization_kwargs(self) -> dict[str, object]:
        if self._coordination_service is None:
            raise RuntimeError("HA runtime lifecycle is not initialized.")
        return {
            "coordination": self._coordination_service,
            "fencing_epoch": self.policy.fencing_epoch,
        }

    def health_snapshot(self) -> dict[str, object]:
        service = self._coordination_service
        return {
            "mode": self.policy.mode.value,
            "state": self.state.value,
            "ready": self.state
            in {HaRuntimeState.STANDALONE_READY, HaRuntimeState.COORDINATED_READY},
            "failure_code": self._failure_code,
            "recovery_latched": self._recovery_latched,
            "recovery_reason": self._recovery_reason,
            "coordination_available": bool(
                service is not None and service.health_snapshot()["available"]
            ),
        }

    async def start(self, *, storage: Any) -> None:
        if self._coordination_service is not None or self.state is not HaRuntimeState.STARTING:
            raise RuntimeError("HA runtime lifecycle has already started.")
        raw_store: Any | None = None
        service: CoordinationService | None = None
        try:
            if self.policy.mode is RuntimeMode.STANDALONE:
                raw_store = self._standalone_store_factory()
                identifier_root = secrets.token_bytes(32)
            else:
                raw_store = self._coordinated_store_factory(self.policy)
                binding = await CoordinationBindingManager(storage, raw_store).verify(self.policy)
                if not self._activation_verifier(binding.activation_record):
                    raise RuntimeError("The coordinated activation record is not accepted.")
                assert self.policy.coordination_key is not None
                identifier_root = self.policy.coordination_key

            service = CoordinationService(raw_store)
            routing_key = hmac.digest(identifier_root, _ROUTING_KEY_DOMAIN, hashlib.sha256)
            attempt_key = hmac.digest(identifier_root, _ATTEMPT_KEY_DOMAIN, hashlib.sha256)
            primary_session_key = hmac.digest(
                identifier_root, _PRIMARY_SESSION_KEY_DOMAIN, hashlib.sha256
            )
            provider_authorization_key = hmac.digest(
                identifier_root,
                _PROVIDER_AUTHORIZATION_KEY_DOMAIN,
                hashlib.sha256,
            )
            device_authorization_key = hmac.digest(
                identifier_root,
                _DEVICE_AUTHORIZATION_KEY_DOMAIN,
                hashlib.sha256,
            )
            credential_batch_key = hmac.digest(
                identifier_root,
                _CREDENTIAL_BATCH_KEY_DOMAIN,
                hashlib.sha256,
            )
            routing = RoutingCoordinationAdapter(
                service,
                identifier_key=routing_key,
                fencing_epoch=self.policy.fencing_epoch,
            )

            await credential_manager.configure_routing_coordination(routing)
            self._credential_manager_owner = credential_manager
            configure_governance_coordination(routing)
            configure_authentication_attempt_service(
                AuthenticationAttemptService(
                    service,
                    hmac_key=attempt_key,
                    fencing_epoch=self.policy.fencing_epoch,
                )
            )
            configure_oidc_transaction_coordination(
                service,
                fencing_epoch=self.policy.fencing_epoch,
            )
            configure_provider_authorization_service(
                ProviderAuthorizationService(
                    service,
                    key=provider_authorization_key,
                    fencing_epoch=self.policy.fencing_epoch,
                )
            )
            configure_device_authorization_service(
                DeviceAuthorizationService(
                    service,
                    key=device_authorization_key,
                    fencing_epoch=self.policy.fencing_epoch,
                )
            )
            configure_credential_batch_coordination_service(
                CredentialBatchCoordinationService(
                    service,
                    key=credential_batch_key,
                    fencing_epoch=self.policy.fencing_epoch,
                )
            )
            virtual_key_manager.configure_coordination(
                service,
                fencing_epoch=self.policy.fencing_epoch,
            )
            response_cache_coordinator.configure_coordination(routing)
            configure_primary_session_coordinator(
                PrimarySessionCoordinator(
                    service,
                    identifier_key=primary_session_key,
                    fencing_epoch=self.policy.fencing_epoch,
                )
            )

            self._coordination_service = service
            self._routing_coordination = routing
            if self.policy.mode is RuntimeMode.COORDINATED:
                self._binding_manager = CoordinationBindingManager(storage, service)
            self.state = (
                HaRuntimeState.STANDALONE_READY
                if self.policy.mode is RuntimeMode.STANDALONE
                else HaRuntimeState.COORDINATED_READY
            )
        except Exception as exc:
            self._failure_code = (
                "activation_gate_closed"
                if "activation record" in str(exc).lower()
                else "initialization_failed"
            )
            self.state = HaRuntimeState.UNAVAILABLE
            if self.policy.mode is RuntimeMode.COORDINATED:
                self._recovery_latched = True
                self._recovery_reason = "initialization_failed"
            if self._credential_manager_owner is not None:
                await self._credential_manager_owner.configure_routing_coordination(None)
                self._credential_manager_owner = None
            configure_provider_authorization_service(None)
            configure_device_authorization_service(None)
            configure_credential_batch_coordination_service(None)
            if service is not None:
                await service.close()
            elif raw_store is not None:
                await raw_store.close()
            raise

    async def check_ready(self) -> bool:
        """Probe the exact selected coordination state and recover only on success."""

        if self.state in {
            HaRuntimeState.STARTING,
            HaRuntimeState.DRAINING,
            HaRuntimeState.RECONCILING,
            HaRuntimeState.CLOSED,
        }:
            return False
        if self.policy.mode is RuntimeMode.COORDINATED and self._recovery_latched:
            return False
        service = self._coordination_service
        if service is None:
            return False
        try:
            if self.policy.mode is RuntimeMode.COORDINATED:
                if self._binding_manager is None:
                    raise RuntimeError("Coordination binding manager is unavailable.")
                if await service.get("ha-runtime-drain-v1") is not None:
                    self.state = HaRuntimeState.DRAINING
                    return False
                binding = await self._binding_manager.verify(self.policy)
                if not self._activation_verifier(binding.activation_record):
                    raise RuntimeError("The coordinated activation record is not accepted.")
            else:
                await service.read_coordination_time(epoch=self.policy.fencing_epoch)
        except Exception:
            self._failure_code = "dependency_unavailable"
            self.state = HaRuntimeState.UNAVAILABLE
            if self.policy.mode is RuntimeMode.COORDINATED:
                self._recovery_latched = True
                self._recovery_reason = "dependency_unavailable"
            return False
        self._failure_code = ""
        self.state = (
            HaRuntimeState.STANDALONE_READY
            if self.policy.mode is RuntimeMode.STANDALONE
            else HaRuntimeState.COORDINATED_READY
        )
        return True

    async def close(self) -> None:
        service = self._coordination_service
        if self._credential_manager_owner is not None:
            await self._credential_manager_owner.configure_routing_coordination(None)
            self._credential_manager_owner = None
        configure_governance_coordination(None)
        configure_primary_session_coordinator(None)
        configure_provider_authorization_service(None)
        configure_device_authorization_service(None)
        configure_credential_batch_coordination_service(None)
        self._coordination_service = None
        self._routing_coordination = None
        self._binding_manager = None
        if service is not None:
            await service.close()
        self.state = HaRuntimeState.CLOSED


_runtime_lifecycle: HaRuntimeLifecycle | None = None


def get_runtime_lifecycle() -> HaRuntimeLifecycle | None:
    return _runtime_lifecycle


def set_runtime_lifecycle(lifecycle: HaRuntimeLifecycle | None) -> None:
    global _runtime_lifecycle
    _runtime_lifecycle = lifecycle


async def initialize_ha_runtime(storage: Any | None = None) -> HaRuntimeLifecycle:
    """Initialize the process-global lifecycle exactly once."""

    global _runtime_lifecycle
    if _runtime_lifecycle is not None:
        return _runtime_lifecycle
    if storage is None:
        from core.storage_adapter import get_storage_adapter

        storage = await get_storage_adapter()
    lifecycle = HaRuntimeLifecycle()
    await lifecycle.start(storage=storage)
    _runtime_lifecycle = lifecycle
    return lifecycle


def get_runtime_session_kwargs() -> dict[str, object]:
    lifecycle = _runtime_lifecycle
    if lifecycle is None:
        raise RuntimeError("HA runtime lifecycle is not initialized.")
    return lifecycle.session_initialization_kwargs


async def close_ha_runtime() -> None:
    """Close and clear the process-global lifecycle idempotently."""

    global _runtime_lifecycle
    lifecycle = _runtime_lifecycle
    _runtime_lifecycle = None
    if lifecycle is not None:
        await lifecycle.close()


def render_ha_runtime_metrics() -> str:
    """Render a content-free fixed-cardinality lifecycle snapshot."""

    lifecycle = _runtime_lifecycle
    if lifecycle is None:
        snapshot = {
            "mode": "unknown",
            "state": HaRuntimeState.STARTING.value,
            "ready": False,
            "coordination_available": False,
        }
    else:
        snapshot = lifecycle.health_snapshot()
    return (
        "# HELP omni_ha_runtime_ready Whether the selected runtime lifecycle is ready.\n"
        "# TYPE omni_ha_runtime_ready gauge\n"
        f"omni_ha_runtime_ready {int(bool(snapshot['ready']))}\n"
        "# HELP omni_ha_coordination_available Whether the lifecycle coordination probe is available.\n"
        "# TYPE omni_ha_coordination_available gauge\n"
        f"omni_ha_coordination_available {int(bool(snapshot['coordination_available']))}\n"
        "# HELP omni_ha_runtime_info Fixed runtime topology and lifecycle state.\n"
        "# TYPE omni_ha_runtime_info gauge\n"
        "omni_ha_runtime_info"
        f'{{mode="{snapshot["mode"]}",state="{snapshot["state"]}"}} 1\n'
    )
