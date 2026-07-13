"""Provider identity and capability helpers for the shared credential pool."""

from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

GOOGLE_ANTIGRAVITY = "google_antigravity"
GOOGLE_AI_STUDIO = "google_ai_studio"
MAX_DECLARED_MODELS = 500
MAX_MODEL_ID_LENGTH = 256

_PROVIDER_ALIASES = {
    "primary": GOOGLE_ANTIGRAVITY,
    "provider": GOOGLE_ANTIGRAVITY,
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


@dataclass(frozen=True)
class ProviderCapabilities:
    """Stable provider contract used by routing and the management API."""

    provider_id: str
    display_name: str
    credential_types: tuple[str, ...]
    model_prefixes: tuple[str, ...]
    supports_streaming: bool = True
    supports_tools: bool = True

    def supports_model(self, model_name: Optional[str]) -> bool:
        if not model_name or not self.model_prefixes:
            return True
        normalized = str(model_name).strip().lower().split("/")[-1]
        return normalized.startswith(self.model_prefixes)

    def to_dict(self) -> Dict[str, Any]:
        value = asdict(self)
        value["credential_types"] = list(self.credential_types)
        value["model_prefixes"] = list(self.model_prefixes)
        return value


_PROVIDER_CAPABILITIES = {
    GOOGLE_ANTIGRAVITY: ProviderCapabilities(
        provider_id=GOOGLE_ANTIGRAVITY,
        display_name=_PROVIDER_NAMES[GOOGLE_ANTIGRAVITY],
        credential_types=("oauth",),
        model_prefixes=(),
    ),
    GOOGLE_AI_STUDIO: ProviderCapabilities(
        provider_id=GOOGLE_AI_STUDIO,
        display_name=_PROVIDER_NAMES[GOOGLE_AI_STUDIO],
        credential_types=("api_key",),
        model_prefixes=("gemini-", "gemma-"),
    ),
}


def _short_fingerprint(value: Any) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        return ""
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]


def antigravity_account_fingerprint(
    credential_data: Optional[Dict[str, Any]] = None,
    *,
    email: Any = None,
) -> str:
    """Create a stable, non-reversible Antigravity account identifier."""
    data = credential_data or {}
    normalized_email = (
        str(email or data.get("user_email") or data.get("email") or data.get("account_email") or "")
        .strip()
        .lower()
    )
    if normalized_email:
        return _short_fingerprint(normalized_email)

    token_identity = data.get("refresh_token") or data.get("token")
    if token_identity:
        return _short_fingerprint(token_identity)

    project_identity = data.get("project_id") or data.get("quota_project_id")
    return _short_fingerprint(project_identity)


def build_antigravity_credential_filename(
    credential_data: Optional[Dict[str, Any]] = None,
    *,
    email: Any = None,
) -> str:
    """Build the canonical filename for a Google Antigravity credential."""
    fingerprint = antigravity_account_fingerprint(credential_data, email=email)
    return f"google-antigravity-{fingerprint or 'unknown'}.json"


def canonicalize_antigravity_credential_filename(
    filename: Any,
    credential_data: Optional[Dict[str, Any]] = None,
    *,
    email: Any = None,
) -> str:
    """Normalize current, legacy, and imported Antigravity credential names."""
    data = credential_data or {}
    fingerprint = antigravity_account_fingerprint(data, email=email)
    if fingerprint:
        return f"google-antigravity-{fingerprint}.json"

    basename = str(filename or "").replace("\\", "/").rsplit("/", 1)[-1].lower()
    if basename.startswith("google-antigravity-") and basename.endswith(".json"):
        suffix = basename[len("google-antigravity-") : -5]
        if len(suffix) == 16 and all(character in "0123456789abcdef" for character in suffix):
            return basename
    return build_antigravity_credential_filename(data)


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


def get_provider_capabilities(provider_id: Any) -> Optional[ProviderCapabilities]:
    """Return the declared contract for a known provider."""
    return _PROVIDER_CAPABILITIES.get(normalize_provider_id(provider_id))


def list_provider_capabilities() -> list[Dict[str, Any]]:
    """Return deterministic provider metadata for management clients."""
    return [
        _PROVIDER_CAPABILITIES[provider_id].to_dict()
        for provider_id in sorted(_PROVIDER_CAPABILITIES)
    ]


def api_key_fingerprint(api_key: str) -> str:
    """Create a stable, non-reversible identifier for an API key."""
    return _short_fingerprint(api_key)


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


def get_declared_credential_models(
    credential_data: Optional[Dict[str, Any]],
) -> list[str]:
    """Return safe, normalized model IDs declared by a credential."""
    declared_models = (credential_data or {}).get("model_ids")
    if not isinstance(declared_models, list):
        return []

    normalized_models = []
    seen = set()
    for value in declared_models:
        if not isinstance(value, str):
            continue
        model_id = value.strip().removeprefix("models/")
        if (
            not model_id
            or len(model_id) > MAX_MODEL_ID_LENGTH
            or not model_id.isprintable()
            or model_id in seen
        ):
            continue
        seen.add(model_id)
        normalized_models.append(model_id)
        if len(normalized_models) >= MAX_DECLARED_MODELS:
            break
    return normalized_models


def credential_supports_model(
    credential_data: Dict[str, Any],
    model_name: Optional[str],
    required_provider: Optional[str] = None,
) -> bool:
    """Return whether a credential can serve the requested provider and model."""
    provider_id = get_credential_provider(credential_data)
    if required_provider and provider_id != normalize_provider_id(required_provider):
        return False
    capabilities = get_provider_capabilities(provider_id)
    if not capabilities or not capabilities.supports_model(model_name):
        return False
    declared_models = get_declared_credential_models(credential_data)
    if model_name and declared_models:
        normalized_model = str(model_name).strip().removeprefix("models/")
        return normalized_model in declared_models
    return True
