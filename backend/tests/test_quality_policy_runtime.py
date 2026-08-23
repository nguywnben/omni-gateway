from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.quality_policy import POLICY_STORAGE_KEY, build_policy_document
from core.quality_policy_runtime import get_quality_env_locked_keys, resolve_quality_policy


def balanced_legacy() -> dict:
    return {
        "compatibility_mode_enabled": False,
        "return_thoughts_to_frontend": True,
        "anti_truncation_max_attempts": 3,
        "token_compression_enabled": True,
        "token_compression_threshold": 32_000,
        "token_compression_target": 24_000,
        "token_compression_min_recent_turns": 4,
        "guardrails_enabled": False,
        "guardrails_pii_masking_enabled": True,
        "guardrails_injection_detection_enabled": True,
        "guardrails_blocked_keywords": [],
        "response_cache_enabled": False,
        "response_cache_ttl_seconds": 300,
        "response_cache_max_entries": 1_000,
    }


class QualityPolicyRuntimeTests(unittest.IsolatedAsyncioTestCase):
    async def test_all_quality_environment_controls_are_reported_as_locked(self):
        with patch.dict(
            os.environ,
            {
                "GUARDRAILS_ENABLED": "true",
                "RESPONSE_CACHE_ENABLED": "true",
                "TOKEN_COMPRESSION_ENABLED": "false",
            },
            clear=False,
        ):
            locked = get_quality_env_locked_keys()

        self.assertTrue(
            {
                "guardrails_enabled",
                "response_cache_enabled",
                "token_compression_enabled",
            }.issubset(locked)
        )

    async def test_stored_policy_is_the_active_runtime_source(self):
        stored = build_policy_document(profile="capacity", revision=4)
        with (
            patch(
                "core.quality_policy_runtime.read_legacy_quality_settings",
                new=AsyncMock(return_value=balanced_legacy()),
            ),
            patch(
                "core.quality_policy_runtime.config.get_config_value",
                new=AsyncMock(
                    side_effect=lambda key, default=None: (
                        stored if key == POLICY_STORAGE_KEY else default
                    )
                ),
            ),
            patch(
                "core.quality_policy_runtime.get_quality_env_locked_keys",
                return_value=set(),
            ),
        ):
            resolved = await resolve_quality_policy()

        self.assertTrue(resolved["runtime_active"])
        self.assertEqual(resolved["runtime_source"], "versioned_policy")
        self.assertEqual(resolved["policy"]["profile"], "capacity")
        self.assertEqual(resolved["effective_settings"]["compression"]["threshold_tokens"], 16_000)

    async def test_environment_locked_values_override_the_stored_intent(self):
        stored = build_policy_document(profile="capacity", revision=4)
        legacy = balanced_legacy()
        legacy["token_compression_enabled"] = False
        with (
            patch(
                "core.quality_policy_runtime.read_legacy_quality_settings",
                new=AsyncMock(return_value=legacy),
            ),
            patch(
                "core.quality_policy_runtime.config.get_config_value",
                new=AsyncMock(return_value=stored),
            ),
            patch(
                "core.quality_policy_runtime.get_quality_env_locked_keys",
                return_value={"token_compression_enabled"},
            ),
        ):
            resolved = await resolve_quality_policy()

        self.assertTrue(resolved["policy"]["settings"]["compression"]["enabled"])
        self.assertFalse(resolved["effective_settings"]["compression"]["enabled"])
        self.assertEqual(resolved["environment_overrides"], ["token_compression_enabled"])

    async def test_legacy_projection_remains_active_without_persisting_a_document(self):
        with (
            patch(
                "core.quality_policy_runtime.read_legacy_quality_settings",
                new=AsyncMock(return_value=balanced_legacy()),
            ),
            patch(
                "core.quality_policy_runtime.config.get_config_value",
                new=AsyncMock(return_value=None),
            ),
            patch(
                "core.quality_policy_runtime.get_quality_env_locked_keys",
                return_value=set(),
            ),
        ):
            resolved = await resolve_quality_policy()

        self.assertEqual(resolved["runtime_source"], "legacy_projection")
        self.assertEqual(resolved["policy"]["revision"], 0)
        self.assertEqual(resolved["policy"]["profile"], "balanced")


if __name__ == "__main__":
    unittest.main()
