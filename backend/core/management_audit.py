"""Declarative coverage matrix for control-plane mutations."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, replace

from core.audit import (
    AUDIT_ACTIONS,
    AUDIT_CHANGE_CODES,
    AUDIT_TARGET_TYPES,
)


@dataclass(frozen=True, slots=True)
class ManagementMutation:
    action: str
    target_type: str
    change_codes: tuple[str, ...]
    target_identifier: str = ""

    def __post_init__(self) -> None:
        if self.action not in AUDIT_ACTIONS:
            raise ValueError(f"Unsupported management audit action: {self.action}")
        if self.target_type not in AUDIT_TARGET_TYPES:
            raise ValueError(f"Unsupported management audit target: {self.target_type}")
        if not self.change_codes or any(
            code not in AUDIT_CHANGE_CODES for code in self.change_codes
        ):
            raise ValueError("Unsupported management audit change summary.")


def _mutation(
    action: str,
    target_type: str,
    *change_codes: str,
) -> ManagementMutation:
    return ManagementMutation(action, target_type, tuple(change_codes))


MANAGEMENT_MUTATIONS: dict[tuple[str, str], ManagementMutation] = {
    ("POST", "/api/auth/login"): _mutation("auth.login", "session", "created"),
    ("POST", "/api/auth/setup"): _mutation("auth.setup", "session", "created"),
    ("POST", "/api/auth/logout"): _mutation("auth.logout", "session", "deleted"),
    ("POST", "/api/auth/callback"): _mutation("credential.create", "credential", "created"),
    ("POST", "/api/auth/callback-url"): _mutation("credential.create", "credential", "created"),
    ("POST", "/api/auth/keys/reset"): _mutation("root_key.rotate", "root_key", "rotated"),
    ("POST", "/api/auth/load-env-creds"): _mutation("credential.import", "credential", "created"),
    ("DELETE", "/api/auth/env-creds"): _mutation("credential.batch", "credential", "deleted"),
    ("POST", "/api/credentials/upload"): _mutation("credential.import", "credential", "created"),
    ("POST", "/api/credentials/fetch-email/{filename}"): _mutation(
        "credential.email_refresh", "credential", "updated"
    ),
    ("POST", "/api/credentials/refresh-all-emails"): _mutation(
        "credential.email_refresh", "credential", "updated"
    ),
    ("POST", "/api/credentials/deduplicate-by-email"): _mutation(
        "credential.batch", "credential", "deleted"
    ),
    ("POST", "/api/credentials/import"): _mutation("credential.import", "credential", "created"),
    ("POST", "/api/credentials/verify/{filename}"): _mutation(
        "credential.verify", "credential", "verified"
    ),
    ("POST", "/api/credentials/configure-preview/{filename}"): _mutation(
        "credential.update", "credential", "settings_changed"
    ),
    ("POST", "/api/credentials/test/{filename}"): _mutation(
        "credential.test", "credential", "verified"
    ),
    ("POST", "/api/config/save"): _mutation("config.update", "configuration", "settings_changed"),
    ("POST", "/api/config/access"): _mutation("config.update", "configuration", "settings_changed"),
    ("POST", "/api/config/reset"): _mutation("config.reset", "configuration", "settings_changed"),
    ("POST", "/api/logs/clear"): _mutation("logs.clear", "log_store", "deleted"),
    ("PUT", "/api/audit/retention"): _mutation(
        "audit.retention_update", "audit_policy", "retention_changed"
    ),
    ("POST", "/api/virtual-keys"): _mutation("virtual_key.create", "virtual_key", "created"),
    ("PATCH", "/api/virtual-keys/{key_id}"): _mutation(
        "virtual_key.update", "virtual_key", "updated"
    ),
    ("DELETE", "/api/virtual-keys/{key_id}"): _mutation(
        "virtual_key.revoke", "virtual_key", "revoked"
    ),
    ("POST", "/api/providers/antigravity/config"): _mutation(
        "provider.update", "provider", "settings_changed"
    ),
    ("POST", "/api/providers/antigravity/config/reset"): _mutation(
        "provider.update", "provider", "settings_changed"
    ),
    ("POST", "/api/providers/google-ai-studio/config"): _mutation(
        "provider.update", "provider", "settings_changed"
    ),
    ("POST", "/api/providers/google-ai-studio/config/reset"): _mutation(
        "provider.update", "provider", "settings_changed"
    ),
    ("POST", "/api/providers/google-ai-studio/credentials"): _mutation(
        "credential.create", "credential", "created"
    ),
    ("POST", "/api/providers/google-ai-studio/credentials/import"): _mutation(
        "credential.import", "credential", "created"
    ),
    ("POST", "/api/providers/xai/config"): _mutation(
        "provider.update", "provider", "settings_changed"
    ),
    ("POST", "/api/providers/xai/config/reset"): _mutation(
        "provider.update", "provider", "settings_changed"
    ),
    ("POST", "/api/providers/xai/credentials"): _mutation(
        "credential.create", "credential", "created"
    ),
    ("POST", "/api/providers/xai/oauth/complete"): _mutation(
        "credential.create", "credential", "created"
    ),
    ("POST", "/api/providers/xai/credentials/import"): _mutation(
        "credential.import", "credential", "created"
    ),
    ("POST", "/api/providers/openai/config"): _mutation(
        "provider.update", "provider", "settings_changed"
    ),
    ("POST", "/api/providers/openai/config/reset"): _mutation(
        "provider.update", "provider", "settings_changed"
    ),
    ("POST", "/api/providers/openai/platform/credentials"): _mutation(
        "credential.create", "credential", "created"
    ),
    ("POST", "/api/providers/openai/codex/oauth/complete"): _mutation(
        "credential.create", "credential", "created"
    ),
    ("POST", "/api/providers/openai/credentials/import"): _mutation(
        "credential.import", "credential", "created"
    ),
    ("POST", "/api/providers/anthropic/config"): _mutation(
        "provider.update", "provider", "settings_changed"
    ),
    ("POST", "/api/providers/anthropic/config/reset"): _mutation(
        "provider.update", "provider", "settings_changed"
    ),
    ("POST", "/api/providers/anthropic/platform/credentials"): _mutation(
        "credential.create", "credential", "created"
    ),
    ("POST", "/api/providers/anthropic/claude-code/oauth/complete"): _mutation(
        "credential.create", "credential", "created"
    ),
    ("POST", "/api/providers/anthropic/credentials/import"): _mutation(
        "credential.import", "credential", "created"
    ),
    ("POST", "/api/providers/ollama/credentials"): _mutation(
        "credential.create", "credential", "created"
    ),
    ("POST", "/api/providers/ollama/credentials/import"): _mutation(
        "credential.import", "credential", "created"
    ),
    ("DELETE", "/api/model-blacklist"): _mutation(
        "model_blacklist.clear", "model_blacklist", "deleted"
    ),
    ("DELETE", "/api/model-blacklist/{provider_id}/models/{model_id}"): _mutation(
        "model_blacklist.clear", "model_blacklist", "deleted"
    ),
    ("PUT", "/api/model-pools/omway"): _mutation("model_pool.update", "model_pool", "updated"),
    ("PUT", "/api/quality-policy"): _mutation(
        "quality_policy.update", "quality_policy", "policy_changed"
    ),
}

MANAGEMENT_AUDIT_EXCLUSIONS: dict[tuple[str, str], str] = {
    ("POST", "/api/auth/start"): "OAuth handshake only; no durable state mutation.",
    ("POST", "/api/providers/xai/oauth/start"): "OAuth handshake only.",
    ("POST", "/api/providers/openai/codex/oauth/start"): "OAuth handshake only.",
    ("POST", "/api/providers/anthropic/claude-code/oauth/start"): "OAuth handshake only.",
    ("POST", "/api/quality-policy/preview"): "Side-effect-free policy preview.",
    ("POST", "/api/credentials/action"): "Bridged from per-target credential evidence.",
    ("POST", "/api/credentials/batch-action"): "Bridged from per-target credential evidence.",
}


def _compile_template(template: str) -> re.Pattern[str]:
    parts = re.split(r"(\{[^}]+\})", template)
    expression = ""
    for part in parts:
        if part.startswith("{"):
            field_name = part[1:-1]
            value_expression = ".+" if field_name == "model_id" else "[^/]+"
            expression += f"(?P<{field_name}>{value_expression})"
        else:
            expression += re.escape(part)
    return re.compile(f"^{expression}$")


_RUNTIME_MUTATIONS = tuple(
    (method, path, _compile_template(path), mutation)
    for (method, path), mutation in MANAGEMENT_MUTATIONS.items()
)


def _bounded_target_identifier(value: str) -> str:
    if len(value) <= 512:
        return value
    return f"sha256:{hashlib.sha256(value.encode('utf-8')).hexdigest()}"


def _semantic_target_identifier(
    template: str,
    concrete_path: str,
    mutation: ManagementMutation,
    matched: re.Match[str],
) -> str:
    groups = matched.groupdict()
    if "key_id" in groups:
        return _bounded_target_identifier(groups["key_id"])
    if "filename" in groups:
        return _bounded_target_identifier(groups["filename"])
    if "provider_id" in groups and "model_id" in groups:
        return _bounded_target_identifier(f"{groups['provider_id']}:{groups['model_id']}")
    provider_match = re.match(r"^/api/providers/([^/]+)/", concrete_path)
    if mutation.target_type == "provider" and provider_match:
        return _bounded_target_identifier(provider_match.group(1))
    fixed_targets = {
        "configuration": "global",
        "session": "panel",
        "root_key": "root",
        "log_store": "runtime",
        "quality_policy": "global",
        "model_pool": "omway",
        "model_blacklist": "global",
    }
    if mutation.target_type in fixed_targets:
        return fixed_targets[mutation.target_type]
    if mutation.target_type == "virtual_key":
        return "collection"
    if mutation.target_type == "credential":
        if provider_match:
            return _bounded_target_identifier(f"{provider_match.group(1)}:collection")
        if template.startswith("/api/auth/"):
            return "authentication:collection"
        if template.startswith("/api/credentials/"):
            return "credential:collection"
        return "environment:collection"
    return _bounded_target_identifier(template)


def classify_management_mutation(
    method: str,
    path: str,
) -> ManagementMutation | None:
    """Resolve a concrete request path without retaining any raw target in storage."""

    normalized_method = str(method or "").upper()
    normalized_path = str(path or "")
    for candidate_method, template, pattern, mutation in _RUNTIME_MUTATIONS:
        matched = pattern.fullmatch(normalized_path)
        if candidate_method == normalized_method and matched:
            return replace(
                mutation,
                target_identifier=_semantic_target_identifier(
                    template,
                    normalized_path,
                    mutation,
                    matched,
                ),
            )
    return None


def _outcome_for_status(status_code: int) -> str:
    if 200 <= status_code < 400:
        return "succeeded"
    if status_code in {401, 403}:
        return "denied"
    if status_code == 404:
        return "not_found"
    if status_code == 409:
        return "conflict"
    if status_code in {408, 504}:
        return "timed_out"
    if status_code == 499:
        return "cancelled"
    if status_code in {400, 405, 422, 428}:
        return "invalid"
    return "failed"


async def record_management_response(
    *,
    method: str,
    path: str,
    status_code: int,
    request_id: str,
):
    """Append one correlated event for a classified management response."""

    mutation = classify_management_mutation(method, path)
    if mutation is None:
        return None
    return await record_classified_management_response(
        mutation,
        status_code=status_code,
        request_id=request_id,
    )


async def record_classified_management_response(
    mutation: ManagementMutation,
    *,
    status_code: int,
    request_id: str,
):
    """Append a mutation already resolved from trusted request routing metadata."""

    from core.audit_service import get_audit_service

    outcome = _outcome_for_status(status_code)
    unauthenticated_action = mutation.action in {"auth.login", "auth.setup"}
    denied = outcome == "denied"
    actor_type = "system" if unauthenticated_action or denied else "panel_session"
    actor_identifier = "unauthenticated-control-plane" if actor_type == "system" else "panel-owner"
    return await get_audit_service().record(
        mutation,
        request_id=request_id,
        actor_type=actor_type,
        actor_identifier=actor_identifier,
        outcome=outcome,
    )
