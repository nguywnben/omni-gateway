from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.quality_policy import (
    QualityPolicyError,
    build_policy_document,
    load_policy_document,
    preview_policy,
    project_legacy_policy,
)


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


class QualityPolicyDomainTests(unittest.TestCase):
    def test_default_legacy_settings_project_to_balanced_without_persistence(self):
        policy = project_legacy_policy(balanced_legacy())

        self.assertEqual(policy["schema_version"], 1)
        self.assertEqual(policy["revision"], 0)
        self.assertEqual(policy["profile"], "balanced")
        self.assertEqual(policy["source"], "legacy_projection")
        self.assertEqual(policy["settings"]["compression"]["target_tokens"], 24_000)

    def test_nonstandard_legacy_settings_project_to_custom_without_changing_values(self):
        legacy = balanced_legacy()
        legacy["token_compression_enabled"] = False
        legacy["return_thoughts_to_frontend"] = False

        policy = project_legacy_policy(legacy)

        self.assertEqual(policy["profile"], "custom")
        self.assertFalse(policy["settings"]["compression"]["enabled"])
        self.assertFalse(policy["settings"]["return_reasoning"])

    def test_quality_preset_disables_compression_and_exact_response_cache(self):
        policy = build_policy_document(profile="quality", revision=1)

        self.assertFalse(policy["settings"]["compression"]["enabled"])
        self.assertFalse(policy["settings"]["response_cache"]["enabled"])
        self.assertTrue(policy["settings"]["return_reasoning"])

    def test_custom_policy_rejects_a_target_that_is_not_below_the_threshold(self):
        settings = project_legacy_policy(balanced_legacy())["settings"]
        settings["compression"]["target_tokens"] = settings["compression"]["threshold_tokens"]

        with self.assertRaises(QualityPolicyError) as context:
            build_policy_document(profile="custom", revision=1, settings=settings)

        self.assertEqual(context.exception.code, "quality_policy_invalid")

    def test_stored_preset_cannot_smuggle_settings_that_differ_from_its_profile(self):
        stored = build_policy_document(profile="balanced", revision=4)
        stored["settings"]["compression"]["enabled"] = False

        with self.assertRaises(QualityPolicyError):
            load_policy_document(stored, balanced_legacy())

    def test_preview_is_bounded_redacted_and_does_not_claim_a_provider_call(self):
        policy = build_policy_document(profile="balanced", revision=2)

        result = preview_policy(
            policy,
            {
                "estimated_input_tokens": 50_000,
                "message_count": 40,
                "tool_count": 3,
                "has_system_instruction": True,
                "has_tool_pairs": True,
            },
        )

        self.assertEqual(result["decision"]["reason"], "structural_compression_candidate")
        self.assertEqual(result["decision"]["estimated_tokens_after"], 24_000)
        self.assertFalse(result["provider_call"])
        self.assertFalse(result["persisted"])
        self.assertNotIn("prompt", str(result).lower())


if __name__ == "__main__":
    unittest.main()
