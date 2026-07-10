"""Provider identity and capability helpers for the shared credential pool."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, Optional


GOOGLE_ANTIGRAVITY = "google_antigravity"
GOOGLE_AI_STUDIO = "google_ai_studio"

_PROVIDER_ALIASES = {
    "antigravity": GOOGLE_ANTIGRAVITY,
    "google-antigravity": GOOGLE_ANTIGRAVITY,
    "google_antigravity": GOOGLE_ANTIGRAVITY,
    "ai-studio": GOOGLE_AI_STUDIO,
    "aistudio": GOOGLE_AI_STUDIO,
    "gemini": GOOGLE_AI_STUDIO,
    "google-ai-studio": GOOGLE_AI_STUDIO,
    "google_ai_studio": GOOGLE_AI_STUDIO,
}

_PROVIDER_NAMES = {
    GOOGLE_ANTIGRAVITY: "Google Antigravity",
    GOOGLE_AI_STUDIO: "Google AI Studio",
}


def normalize_provider_id(value: Any) -> str:
    """Normalize a provider identifier to its stable internal value."""
    normalized = str(value or "").strip().lower().replace(" ", "-")
    return _PROVIDER_ALIASES.get(normalized, normalized.replace("-", "_"))


def get_credential_provider(credential_data: Optional[Dict[str, Any]]) -> str:
    """Return the provider for new and legacy credential payloads."""
    data = credential_data or {}
    explicit = data.get("provider") or data.get("provider_id")
    if explicit:
        return normalize_provider_id(explicit)
    if data.get("credential_type") == "api_key" and data.get("api_key"):
        return GOOGLE_AI_STUDIO
    return GOOGLE_ANTIGRAVITY


def get_provider_display_name(provider_id: Any) -> str:
    normalized = normalize_provider_id(provider_id)
    return _PROVIDER_NAMES.get(normalized, str(provider_id or "Provider"))


def api_key_fingerprint(api_key: str) -> str:
    """Create a stable, non-reversible identifier for an API key."""
    normalized = str(api_key or "").strip()
    if not normalized:
        return ""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def get_static_credential_identity(credential_data: Dict[str, Any]) -> str:
    """Return a deduplication identity that does not require a network lookup."""
    provider_id = get_credential_provider(credential_data)
    if provider_id != GOOGLE_AI_STUDIO:
        return ""
    fingerprint = str(credential_data.get("key_fingerprint") or "").strip()
    if not fingerprint:
        fingerprint = api_key_fingerprint(str(credential_data.get("api_key") or ""))
    return f"{provider_id}:{fingerprint}" if fingerprint else ""


def is_api_key_credential(credential_data: Optional[Dict[str, Any]]) -> bool:
    data = credential_data or {}
    return bool(data.get("credential_type") == "api_key" and data.get("api_key"))


def credential_supports_model(
    credential_data: Dict[str, Any],
    model_name: Optional[str],
    required_provider: Optional[str] = None,
) -> bool:
    """Return whether a credential can serve the requested provider and model."""
    provider_id = get_credential_provider(credential_data)
    if required_provider and provider_id != normalize_provider_id(required_provider):
        return False
    if not model_name or provider_id != GOOGLE_AI_STUDIO:
        return True

    normalized_model = str(model_name).strip().lower().split("/")[-1]
    return normalized_model.startswith(("gemini-", "gemma-"))
