"""Resolve the versioned quality policy used by inference-time components."""

from __future__ import annotations

import copy
import os
from typing import Any

import config
from core.quality_policy import (
    LOCKED_SETTING_PATHS,
    POLICY_STORAGE_KEY,
    load_policy_document,
    settings_from_legacy,
)


async def read_legacy_quality_settings() -> dict[str, Any]:
    """Read the compatibility settings without recursively resolving the policy."""
    compression = await config.get_legacy_token_compression_config()
    guardrails = await config.get_legacy_guardrails_config()
    response_cache = await config.get_legacy_response_cache_config()
    return {
        "compatibility_mode_enabled": await config.get_legacy_compatibility_mode_enabled(),
        "return_thoughts_to_frontend": await config.get_legacy_return_thoughts_to_frontend(),
        "anti_truncation_max_attempts": await config.get_legacy_anti_truncation_max_attempts(),
        "token_compression_enabled": compression["enabled"],
        "token_compression_threshold": compression["threshold_tokens"],
        "token_compression_target": compression["target_tokens"],
        "token_compression_min_recent_turns": compression["min_recent_turns"],
        "guardrails_enabled": guardrails["enabled"],
        "guardrails_pii_masking_enabled": guardrails["pii_masking_enabled"],
        "guardrails_injection_detection_enabled": guardrails["injection_detection_enabled"],
        "guardrails_blocked_keywords": guardrails["blocked_keywords"],
        "response_cache_enabled": response_cache["enabled"],
        "response_cache_ttl_seconds": response_cache["ttl_seconds"],
        "response_cache_max_entries": response_cache["max_entries"],
    }


def get_quality_env_locked_keys() -> set[str]:
    """Return quality fields whose effective value is owned by the environment."""
    return {
        config_key
        for env_key, config_key in config.ENV_MAPPINGS.items()
        if config_key in LOCKED_SETTING_PATHS and os.getenv(env_key)
    }


def _set_path(target: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    current = target
    for part in path[:-1]:
        current = current[part]
    current[path[-1]] = copy.deepcopy(value)


def apply_environment_overrides(
    settings: dict[str, Any],
    legacy_settings: dict[str, Any],
    env_locked: set[str],
) -> tuple[dict[str, Any], list[str]]:
    """Apply the environment safety ceiling without mutating the stored policy."""
    effective = copy.deepcopy(settings)
    legacy = settings_from_legacy(legacy_settings)
    overrides = []
    for field in sorted(env_locked & set(LOCKED_SETTING_PATHS)):
        path = LOCKED_SETTING_PATHS[field]
        value: Any = legacy
        current: Any = effective
        for part in path:
            value = value[part]
            current = current[part]
        if current != value:
            _set_path(effective, path, value)
            overrides.append(field)
    return effective, overrides


async def resolve_quality_policy() -> dict[str, Any]:
    """Return stored intent plus the environment-constrained runtime settings."""
    legacy = await read_legacy_quality_settings()
    stored = await config.get_config_value(POLICY_STORAGE_KEY, None)
    policy = load_policy_document(stored, legacy)
    env_locked = get_quality_env_locked_keys()
    effective, overrides = apply_environment_overrides(policy["settings"], legacy, env_locked)
    return {
        "policy": policy,
        "effective_settings": effective,
        "env_locked": sorted(env_locked),
        "environment_overrides": overrides,
        "runtime_active": True,
        "runtime_source": "versioned_policy" if stored is not None else "legacy_projection",
    }


async def get_effective_quality_settings() -> dict[str, Any]:
    return (await resolve_quality_policy())["effective_settings"]
