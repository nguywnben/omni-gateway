"""Shared control-panel authentication policies and response shaping."""

from __future__ import annotations

import ipaddress
import os
import time
from collections import OrderedDict
from typing import Any, Dict, List

import config
from fastapi import HTTPException, Request


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(value, maximum))


LOGIN_WINDOW_SECONDS = _env_int("PANEL_LOGIN_WINDOW_SECONDS", 300, 30, 3600)
LOGIN_MAX_ATTEMPTS = _env_int("PANEL_LOGIN_MAX_ATTEMPTS", 10, 3, 100)
LOGIN_MAX_TRACKED_CLIENTS = _env_int("PANEL_LOGIN_MAX_TRACKED_CLIENTS", 10_000, 100, 100_000)
_login_failures: OrderedDict[str, List[float]] = OrderedDict()
RECOVERY_WINDOW_SECONDS = _env_int("PANEL_RECOVERY_WINDOW_SECONDS", 900, 60, 7200)
RECOVERY_MAX_ATTEMPTS = _env_int("PANEL_RECOVERY_MAX_ATTEMPTS", 5, 3, 20)
RECOVERY_MAX_TRACKED_CLIENTS = _env_int("PANEL_RECOVERY_MAX_TRACKED_CLIENTS", 10_000, 100, 100_000)
_recovery_failures: OrderedDict[str, List[float]] = OrderedDict()
OIDC_START_WINDOW_SECONDS = _env_int("OIDC_START_WINDOW_SECONDS", 300, 30, 3600)
OIDC_START_MAX_ATTEMPTS = _env_int("OIDC_START_MAX_ATTEMPTS", 20, 3, 100)
OIDC_START_MAX_TRACKED_CLIENTS = _env_int("OIDC_START_MAX_TRACKED_CLIENTS", 10_000, 100, 100_000)
_oidc_starts: OrderedDict[str, List[float]] = OrderedDict()


def _client_identity(request: Request) -> str:
    if config.trust_proxy_headers_enabled():
        forwarded_for = request.headers.get("x-forwarded-for", "")
        if forwarded_for:
            return forwarded_for.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def _prune_login_failures(now: float) -> None:
    cutoff = now - LOGIN_WINDOW_SECONDS
    expired_clients = [
        client_id
        for client_id, failures in _login_failures.items()
        if not failures or failures[-1] < cutoff
    ]
    for client_id in expired_clients:
        _login_failures.pop(client_id, None)


def _recent_failures(client_id: str, now: float | None = None) -> List[float]:
    current_time = time.time() if now is None else now
    _prune_login_failures(current_time)
    cutoff = current_time - LOGIN_WINDOW_SECONDS
    failures = [ts for ts in _login_failures.get(client_id, []) if ts >= cutoff]
    if failures:
        _login_failures[client_id] = failures
        _login_failures.move_to_end(client_id)
    else:
        _login_failures.pop(client_id, None)
    return failures


def _assert_login_allowed(client_id: str) -> None:
    if len(_recent_failures(client_id)) >= LOGIN_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Please wait before trying again.",
        )


def _record_login_failure(client_id: str) -> None:
    now = time.time()
    failures = _recent_failures(client_id, now)
    if client_id not in _login_failures and len(_login_failures) >= LOGIN_MAX_TRACKED_CLIENTS:
        _login_failures.popitem(last=False)
    failures.append(now)
    _login_failures[client_id] = failures
    _login_failures.move_to_end(client_id)


def _clear_login_failures(client_id: str) -> None:
    _login_failures.pop(client_id, None)


def _recent_recovery_failures(client_id: str, now: float | None = None) -> List[float]:
    current_time = time.time() if now is None else now
    cutoff = current_time - RECOVERY_WINDOW_SECONDS
    for candidate, failures in list(_recovery_failures.items()):
        if not failures or failures[-1] < cutoff:
            _recovery_failures.pop(candidate, None)
    failures = [ts for ts in _recovery_failures.get(client_id, []) if ts >= cutoff]
    if failures:
        _recovery_failures[client_id] = failures
        _recovery_failures.move_to_end(client_id)
    else:
        _recovery_failures.pop(client_id, None)
    return failures


def _assert_recovery_allowed(client_id: str) -> None:
    if len(_recent_recovery_failures(client_id)) >= RECOVERY_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many failed recovery attempts. Please wait before trying again.",
        )


def _record_recovery_failure(client_id: str) -> None:
    now = time.time()
    failures = _recent_recovery_failures(client_id, now)
    if (
        client_id not in _recovery_failures
        and len(_recovery_failures) >= RECOVERY_MAX_TRACKED_CLIENTS
    ):
        _recovery_failures.popitem(last=False)
    failures.append(now)
    _recovery_failures[client_id] = failures
    _recovery_failures.move_to_end(client_id)


def _clear_recovery_failures(client_id: str) -> None:
    _recovery_failures.pop(client_id, None)


def _assert_and_record_oidc_start(client_id: str) -> None:
    """Bound transaction allocation per client before any IdP network work occurs."""
    now = time.time()
    cutoff = now - OIDC_START_WINDOW_SECONDS
    for candidate, starts in list(_oidc_starts.items()):
        if not starts or starts[-1] < cutoff:
            _oidc_starts.pop(candidate, None)
    starts = [timestamp for timestamp in _oidc_starts.get(client_id, []) if timestamp >= cutoff]
    if len(starts) >= OIDC_START_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many OIDC sign-in attempts. Please wait before trying again.",
        )
    if client_id not in _oidc_starts and len(_oidc_starts) >= OIDC_START_MAX_TRACKED_CLIENTS:
        _oidc_starts.popitem(last=False)
    starts.append(now)
    _oidc_starts[client_id] = starts
    _oidc_starts.move_to_end(client_id)


def recovery_local_only_enabled() -> bool:
    """Return the effective recovery ingress policy without trusting proxy metadata."""

    return os.getenv("PANEL_RECOVERY_LOCAL_ONLY", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _assert_recovery_ingress(request: Request) -> None:
    if not recovery_local_only_enabled():
        return
    hostname = (request.url.hostname or "").strip().lower()
    peer = request.client.host if request.client else ""
    try:
        peer_is_loopback = ipaddress.ip_address(peer).is_loopback
    except ValueError:
        peer_is_loopback = False
    if hostname not in {"localhost", "127.0.0.1", "::1"} or not peer_is_loopback:
        raise HTTPException(
            status_code=403,
            detail="Local-owner recovery is restricted to direct loopback access.",
        )


def _credential_result_message(result: Dict[str, Any]) -> str:
    action = result.get("credential_action")
    if action == "replaced":
        return "Authentication completed. The existing credential was renewed with a later expiry."
    if action == "skipped":
        return "Authentication completed, but the credential was not added because the pool already has the same email with an equal or later expiry."
    return "Authentication completed. Credential saved."


def _auth_success_content(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "credentials": result["credentials"],
        "file_path": result["file_path"],
        "message": _credential_result_message(result),
        "auto_detected_project": result.get("auto_detected_project", False),
        "credential_saved": result.get("credential_saved", True),
        "credential_action": result.get("credential_action", "created"),
        "credential_message": result.get("credential_message"),
        "email": result.get("email"),
        "existing_expiry": result.get("existing_expiry"),
        "incoming_expiry": result.get("incoming_expiry"),
        "deleted_duplicates": result.get("deleted_duplicates", []),
    }
