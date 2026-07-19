"""Shared provider credential persistence helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from core.credential_manager import credential_manager
from core.provider_registry import GOOGLE_AI_STUDIO, OPENAI, XAI, api_key_fingerprint


async def store_google_ai_studio_credential(
    api_key: str,
    validation: Any,
    *,
    created_at: Optional[str] = None,
) -> dict:
    """Store one validated Google AI Studio key without exposing it."""
    normalized_key = str(api_key or "").strip()
    fingerprint = api_key_fingerprint(normalized_key)
    credential_label = f"API key ending {normalized_key[-4:]}"
    credential_data = {
        "provider": GOOGLE_AI_STUDIO,
        "credential_type": "api_key",
        "api_key": normalized_key,
        "credential_label": credential_label,
        "key_fingerprint": fingerprint,
        "model_ids": validation.model_ids,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
    }
    filename = f"google-ai-studio-{fingerprint}.json"
    result = await credential_manager.add_primary_credential(filename, credential_data)
    return {
        "action": result.get("action", "created"),
        "filename": result.get("filename", filename),
        "label": credential_label,
        "fingerprint": fingerprint,
    }


async def store_xai_api_key_credential(
    api_key: str,
    validation: Any,
    *,
    created_at: Optional[str] = None,
) -> dict:
    """Store one validated SpaceXAI Console API key without exposing it."""
    normalized_key = str(api_key or "").strip()
    fingerprint = api_key_fingerprint(normalized_key)
    credential_label = f"API key ending {normalized_key[-4:]}"
    credential_data = {
        "provider": XAI,
        "credential_type": "api_key",
        "api_key": normalized_key,
        "credential_label": credential_label,
        "key_fingerprint": fingerprint,
        "model_ids": validation.model_ids,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
    }
    filename = f"xai-console-{fingerprint}.json"
    result = await credential_manager.add_primary_credential(filename, credential_data)
    return {
        "action": result.get("action", "created"),
        "filename": result.get("filename", filename),
        "label": credential_label,
        "fingerprint": fingerprint,
    }


async def store_openai_platform_credential(
    api_key: str,
    validation: Any,
    *,
    created_at: Optional[str] = None,
) -> dict:
    """Store one validated OpenAI Platform API key without exposing it."""
    normalized_key = str(api_key or "").strip()
    fingerprint = api_key_fingerprint(normalized_key)
    credential_label = f"API key ending {normalized_key[-4:]}"
    credential_data = {
        "provider": OPENAI,
        "credential_type": "api_key",
        "api_key": normalized_key,
        "credential_label": credential_label,
        "key_fingerprint": fingerprint,
        "model_ids": validation.model_ids,
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
    }
    filename = f"openai-platform-{fingerprint}.json"
    result = await credential_manager.add_primary_credential(filename, credential_data)
    return {
        "action": result.get("action", "created"),
        "filename": result.get("filename", filename),
        "label": credential_label,
        "fingerprint": fingerprint,
    }


async def store_codex_credential(credential_data: dict) -> dict:
    """Store one completed Codex OAuth credential in the primary pool."""
    payload = dict(credential_data)
    payload["provider"] = OPENAI
    payload["credential_type"] = "oauth"
    fingerprint = str(payload.get("account_fingerprint") or "").strip()
    if not fingerprint:
        fingerprint = api_key_fingerprint(
            str(payload.get("user_email") or payload.get("refresh_token") or "")
        )
    filename = f"openai-codex-{fingerprint or 'unknown'}.json"
    result = await credential_manager.add_primary_credential(filename, payload)
    return {
        "action": result.get("action", "created"),
        "filename": result.get("filename", filename),
        "label": payload.get("credential_label") or "Codex account",
        "fingerprint": fingerprint,
    }
