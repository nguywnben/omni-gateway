"""Shared control-panel authentication policies and response shaping."""

from __future__ import annotations

import os
import time
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
_login_failures: Dict[str, List[float]] = {}


def _client_identity(request: Request) -> str:
    if config.trust_proxy_headers_enabled():
        forwarded_for = request.headers.get("x-forwarded-for", "")
        if forwarded_for:
            return forwarded_for.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def _recent_failures(client_id: str) -> List[float]:
    now = time.time()
    cutoff = now - LOGIN_WINDOW_SECONDS
    failures = [ts for ts in _login_failures.get(client_id, []) if ts >= cutoff]
    _login_failures[client_id] = failures
    return failures


def _assert_login_allowed(client_id: str) -> None:
    if len(_recent_failures(client_id)) >= LOGIN_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Please wait before trying again.",
        )


def _record_login_failure(client_id: str) -> None:
    failures = _recent_failures(client_id)
    failures.append(time.time())
    _login_failures[client_id] = failures


def _clear_login_failures(client_id: str) -> None:
    _login_failures.pop(client_id, None)


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
