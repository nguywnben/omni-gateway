"""Gemini CLI provider metadata, authentication, and execution helpers."""

from __future__ import annotations

import base64
import hashlib
import platform
import secrets
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlencode, urlparse

import httpx
from config import (
    get_gemini_cli_api_url,
    get_gemini_cli_oauth_authorize_url,
    get_gemini_cli_oauth_client_config,
    get_gemini_cli_oauth_token_url,
)
from core.credential_pool import upsert_credential_by_email
from core.httpx_client import get_async, post_async
from core.provider_registry import (
    GEMINI_CLI,
    build_gemini_cli_credential_filename,
)
from log import log

GEMINI_CLI_VERSION = "0.34.0"
GEMINI_CLI_API_CLIENT = "google-genai-sdk/1.41.0 gl-node/v22.19.0"
GEMINI_CLI_DEFAULT_REDIRECT_URI = "http://localhost:4283/callback"
GEMINI_CLI_FLOW_TTL_SECONDS = 15 * 60
MAX_GEMINI_CLI_FLOWS = 256

GEMINI_CLI_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

DEFAULT_GEMINI_CLI_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3.1-pro-preview",
    "gemini-3-pro-preview",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
]

_oauth_flows: Dict[str, Dict[str, Any]] = {}


class GeminiCliError(RuntimeError):
    """A sanitized Gemini CLI integration error."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


def is_gemini_cli_oauth_state(state: str | None) -> bool:
    """Return whether a state parameter belongs to a pending Gemini CLI OAuth flow."""
    if not state or not isinstance(state, str):
        return False
    _prune_oauth_flows()
    return state in _oauth_flows


def _prune_oauth_flows(now: float | None = None) -> None:
    current = time.time() if now is None else now
    expired_keys = [
        state
        for state, flow in _oauth_flows.items()
        if current - float(flow.get("created_at") or 0.0) > GEMINI_CLI_FLOW_TTL_SECONDS
    ]
    for state in expired_keys:
        _oauth_flows.pop(state, None)

    if len(_oauth_flows) > MAX_GEMINI_CLI_FLOWS:
        sorted_states = sorted(
            _oauth_flows.keys(),
            key=lambda key: float(_oauth_flows[key].get("created_at") or 0.0),
        )
        for state in sorted_states[: len(_oauth_flows) - MAX_GEMINI_CLI_FLOWS]:
            _oauth_flows.pop(state, None)


def _gemini_cli_arch() -> str:
    machine = platform.machine().lower()
    if machine in {"amd64", "x86_64", "x64"}:
        return "x64"
    if machine in {"i386", "i686", "x86", "ia32"}:
        return "x86"
    if machine in {"arm64", "aarch64"}:
        return "arm64"
    return machine or "unknown"


def _gemini_cli_platform() -> str:
    system = sys.platform.lower()
    if system.startswith("win"):
        return "win32"
    if system.startswith("darwin"):
        return "darwin"
    if system.startswith("linux"):
        return "linux"
    return system or "unknown"


def gemini_cli_user_agent(model: str = "unknown") -> str:
    """Build the Gemini CLI User-Agent string."""
    return f"GeminiCLI/{GEMINI_CLI_VERSION}/{model or 'unknown'} ({_gemini_cli_platform()}; {_gemini_cli_arch()}; terminal)"


def normalize_gemini_cli_api_url(value: str) -> str:
    """Validate and normalize the Gemini CLI API endpoint."""
    normalized = str(value or "").strip().rstrip("/")
    parsed = urlparse(normalized)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Gemini CLI API endpoint must use HTTP or HTTPS.")
    if parsed.username or parsed.password:
        raise ValueError("Gemini CLI API endpoint must not contain credentials.")
    return normalized


def normalize_gemini_cli_oauth_url(value: str, label: str) -> str:
    """Validate Google OAuth service endpoints."""
    normalized = str(value or "").strip().rstrip("/")
    parsed = urlparse(normalized)
    hostname = str(parsed.hostname or "").lower()
    if parsed.scheme != "https" or not hostname:
        raise ValueError(f"{label} must use HTTPS.")
    if (
        hostname != "googleapis.com"
        and not hostname.endswith(".googleapis.com")
        and hostname != "google.com"
        and not hostname.endswith(".google.com")
    ):
        raise ValueError(f"{label} must use a Google host.")
    return normalized


async def create_gemini_cli_oauth_flow(
    redirect_uri: str = GEMINI_CLI_DEFAULT_REDIRECT_URI,
) -> tuple[str, str]:
    """Create a PKCE OAuth authorization URL for Gemini CLI."""
    _prune_oauth_flows()
    client_id, _ = await get_gemini_cli_oauth_client_config()
    if not client_id:
        raise GeminiCliError("Gemini CLI client ID is not configured.", status_code=500)

    auth_url_base = await get_gemini_cli_oauth_authorize_url()
    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode("ascii")).digest())
        .decode("ascii")
        .rstrip("=")
    )

    _oauth_flows[state] = {
        "created_at": time.time(),
        "code_verifier": code_verifier,
        "redirect_uri": redirect_uri,
    }

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(GEMINI_CLI_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{auth_url_base}?{urlencode(params)}", state


async def fetch_gemini_cli_project_id(
    access_token: str,
    base_url: str | None = None,
) -> Optional[str]:
    """Fetch or onboard the project ID for Gemini CLI via loadCodeAssist."""
    resolved_base_url = (base_url or await get_gemini_cli_api_url()).rstrip("/")
    endpoint = f"{resolved_base_url}/v1internal:loadCodeAssist"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "User-Agent": gemini_cli_user_agent("unknown"),
        "X-Goog-Api-Client": GEMINI_CLI_API_CLIENT,
    }
    payload = {
        "metadata": {
            "ideType": 0,
            "platform": 5,
            "pluginType": 2,
        }
    }

    try:
        response = await post_async(endpoint, json=payload, headers=headers, timeout=15.0)
        if response.status_code == 200:
            data = response.json()
            project_id = (
                data.get("cloudaicompanionProject")
                or data.get("currentProject")
                or data.get("projectId")
                or data.get("project")
            )
            if isinstance(project_id, dict):
                project_id = project_id.get("id") or project_id.get("projectId")
            if project_id and str(project_id).strip():
                return str(project_id).strip()

            # Attempt user onboarding with default tier if project not immediately found
            allowed_tiers = data.get("allowedTiers")
            tier_id = "legacy-tier"
            if isinstance(allowed_tiers, list):
                for tier in allowed_tiers:
                    if isinstance(tier, dict) and tier.get("isDefault") and tier.get("id"):
                        tier_id = str(tier["id"]).strip()
                        break

            onboard_endpoint = f"{resolved_base_url}/v1internal:onboardUser"
            onboard_resp = await post_async(
                onboard_endpoint,
                json={"tierId": tier_id, "metadata": payload["metadata"]},
                headers=headers,
                timeout=15.0,
            )
            if onboard_resp.status_code == 200:
                onboard_data = onboard_resp.json()
                onboard_project = (
                    onboard_data.get("cloudaicompanionProject")
                    or onboard_data.get("currentProject")
                    or onboard_data.get("projectId")
                )
                if isinstance(onboard_project, dict):
                    onboard_project = onboard_project.get("id") or onboard_project.get("projectId")
                if onboard_project:
                    return str(onboard_project).strip()
    except Exception as exc:
        log.warning(f"Failed to fetch Gemini CLI project ID: {exc}")

    return None


async def complete_gemini_cli_oauth(
    code: str,
    state: str = "",
    redirect_uri: str = GEMINI_CLI_DEFAULT_REDIRECT_URI,
) -> Dict[str, Any]:
    """Exchange code for Gemini CLI tokens and save credential into the pool."""
    _prune_oauth_flows()
    flow = _oauth_flows.pop(state, None) if state else None
    code_verifier = flow.get("code_verifier") if flow else None
    resolved_redirect_uri = flow.get("redirect_uri") if flow else redirect_uri

    client_id, client_secret = await get_gemini_cli_oauth_client_config()
    token_url = await get_gemini_cli_oauth_token_url()

    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code.strip(),
        "grant_type": "authorization_code",
        "redirect_uri": resolved_redirect_uri,
    }
    if code_verifier:
        token_data["code_verifier"] = code_verifier

    try:
        response = await post_async(
            token_url,
            data=token_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=20.0,
        )
    except (httpx.HTTPError, OSError) as exc:
        raise GeminiCliError("Unable to reach Google OAuth token service.", status_code=502) from exc

    if response.status_code != 200:
        raise GeminiCliError(
            f"Google OAuth authorization failed (HTTP {response.status_code}).",
            status_code=response.status_code,
        )

    tokens = response.json()
    access_token = str(tokens.get("access_token") or "").strip()
    if not access_token:
        raise GeminiCliError("Google OAuth response did not include an access token.", status_code=502)

    refresh_token = str(tokens.get("refresh_token") or "").strip()
    expires_in = int(tokens.get("expires_in") or 3600)
    expiry = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat()

    # Get user email
    user_email = ""
    try:
        userinfo_resp = await get_async(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10.0,
        )
        if userinfo_resp.status_code == 200:
            user_email = str(userinfo_resp.json().get("email") or "").strip().lower()
    except Exception as exc:
        log.warning(f"Could not fetch Google userinfo email: {exc}")

    # Fetch project ID
    project_id = await fetch_gemini_cli_project_id(access_token)

    credential_payload: Dict[str, Any] = {
        "provider": GEMINI_CLI,
        "provider_id": GEMINI_CLI,
        "credential_type": "oauth",
        "access_token": access_token,
        "token": access_token,
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "project_id": project_id or "",
        "user_email": user_email,
        "email": user_email,
        "expiry": expiry,
        "model_ids": list(DEFAULT_GEMINI_CLI_MODELS),
    }

    target_filename = build_gemini_cli_credential_filename(credential_payload, email=user_email)
    upsert_result = await upsert_credential_by_email(
        target_filename,
        credential_payload,
        mode="primary",
    )
    saved_filename = upsert_result.get("filename") or target_filename
    log.info(f"Gemini CLI OAuth credential saved: {saved_filename} ({user_email or 'anonymous'})")
    return {
        "success": True,
        "filename": saved_filename,
        "user_email": user_email,
        "project_id": project_id,
        "provider": GEMINI_CLI,
        "model_ids": list(DEFAULT_GEMINI_CLI_MODELS),
        "action": upsert_result.get("action", "created"),
    }


def build_gemini_cli_headers(
    access_token: str,
    model: str = "unknown",
    *,
    stream: bool = False,
) -> Dict[str, str]:
    """Build the request headers for Gemini CLI Cloud Code Assist."""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
        "User-Agent": gemini_cli_user_agent(model),
        "X-Goog-Api-Client": GEMINI_CLI_API_CLIENT,
        "Accept": "text/event-stream" if stream else "application/json",
    }


def wrap_gemini_cli_payload(
    body: Dict[str, Any],
    model: str,
    project_id: str | None = None,
) -> Dict[str, Any]:
    """Wrap Gemini API body into Cloud Code Assist { project, model, request } payload."""
    if isinstance(body, dict) and body.get("request") is not None and body.get("model"):
        return body

    return {
        "project": project_id or body.get("project") or "",
        "model": model,
        "request": body,
    }
