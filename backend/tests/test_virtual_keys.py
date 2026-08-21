"""Tests for virtual API keys: CRUD, verification, and enforcement."""

from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

import asyncio

from core import virtual_keys
from core.virtual_keys import (
    VirtualKey,
    VirtualKeyManager,
    extract_requested_model,
    hash_key,
)
from fastapi import HTTPException


class _FakeStorage:
    def __init__(self):
        self.config = {}

    async def get_config(self, key, default=None):
        return self.config.get(key, default)

    async def set_config(self, key, value):
        self.config[key] = value
        return True


def _patched_manager(storage: _FakeStorage) -> VirtualKeyManager:
    manager = VirtualKeyManager()
    return manager


def _run(coro):
    return asyncio.get_event_loop_policy().new_event_loop().run_until_complete(coro)


class VirtualKeyCrudTests(unittest.TestCase):
    def setUp(self):
        self.storage = _FakeStorage()
        self.manager = _patched_manager(self.storage)
        patcher = patch(
            "core.storage_adapter.get_storage_adapter",
            new=AsyncMock(return_value=self.storage),
        )
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_create_key_returns_plaintext_once_and_persists_hash_only(self):
        async def scenario():
            record, plaintext = await self.manager.create_key(
                "team-frontend", budget_daily_usd=5.0, rpm_limit=10
            )
            return record, plaintext

        record, plaintext = _run(scenario())
        self.assertTrue(plaintext.startswith("sk-ogw-vk-"))
        self.assertNotIn("key_hash", record)
        stored = self.storage.config[virtual_keys.VIRTUAL_KEYS_CONFIG_KEY]
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["key_hash"], hash_key(plaintext))
        self.assertNotIn(plaintext, str(stored))
        self.assertEqual(record["budget_daily_usd"], 5.0)
        self.assertEqual(record["rpm_limit"], 10)

    def test_create_key_requires_name(self):
        async def scenario():
            await self.manager.create_key("   ")

        with self.assertRaises(ValueError):
            _run(scenario())

    def test_update_and_delete_key(self):
        async def scenario():
            record, _ = await self.manager.create_key("temp-key")
            updated = await self.manager.update_key(
                record["id"],
                {"enabled": False, "budget_monthly_usd": 100, "allowed_models": ["gpt-*"]},
            )
            deleted = await self.manager.delete_key(record["id"])
            missing = await self.manager.update_key(record["id"], {"enabled": True})
            return updated, deleted, missing

        updated, deleted, missing = _run(scenario())
        self.assertFalse(updated["enabled"])
        self.assertEqual(updated["budget_monthly_usd"], 100.0)
        self.assertEqual(updated["allowed_models"], ["gpt-*"])
        self.assertTrue(deleted)
        self.assertIsNone(missing)

    def test_verify_matches_only_correct_secret(self):
        async def scenario():
            _, plaintext = await self.manager.create_key("verify-me")
            good = await self.manager.verify(plaintext)
            bad = await self.manager.verify("sk-ogw-vk-wrong")
            return good, bad

        good, bad = _run(scenario())
        self.assertIsNotNone(good)
        self.assertEqual(good.name, "verify-me")
        self.assertIsNone(bad)

    def test_keys_reload_from_storage(self):
        async def scenario():
            _, plaintext = await self.manager.create_key("persisted")
            fresh_manager = _patched_manager(self.storage)
            record = await fresh_manager.verify(plaintext)
            return record

        record = _run(scenario())
        self.assertIsNotNone(record)
        self.assertEqual(record.name, "persisted")


class VirtualKeyEnforcementTests(unittest.TestCase):
    def _make_key(self, **kwargs) -> VirtualKey:
        defaults = dict(
            id="vk_test",
            name="test",
            key_hash="hash",
            key_preview="sk-ogw-vk-...abcd",
            enabled=True,
            created_at=time.time(),
        )
        defaults.update(kwargs)
        return VirtualKey(**defaults)

    def setUp(self):
        self.manager = VirtualKeyManager()
        self.manager._loaded = True

    def test_disabled_key_rejected_401(self):
        record = self._make_key(enabled=False)
        with self.assertRaises(HTTPException) as ctx:
            _run(self.manager.enforce(record))
        self.assertEqual(ctx.exception.status_code, 401)

    def test_expired_key_rejected_401(self):
        record = self._make_key(expires_at=time.time() - 10)
        with self.assertRaises(HTTPException) as ctx:
            _run(self.manager.enforce(record))
        self.assertEqual(ctx.exception.status_code, 401)

    def test_model_allowlist_supports_glob_patterns(self):
        record = self._make_key(allowed_models=["gemini-2.5-*", "gpt-4o"])
        self.assertTrue(record.allows_model("gemini-2.5-flash"))
        self.assertTrue(record.allows_model("GPT-4O"))
        self.assertFalse(record.allows_model("claude-sonnet-4"))
        # Empty model (e.g. GET /v1/models) is allowed.
        self.assertTrue(record.allows_model(""))

    def test_disallowed_model_rejected_403(self):
        record = self._make_key(allowed_models=["gemini-*"])
        with self.assertRaises(HTTPException) as ctx:
            _run(self.manager.enforce(record, requested_model="gpt-4o"))
        self.assertEqual(ctx.exception.status_code, 403)

    def test_rpm_limit_enforced_with_retry_after(self):
        record = self._make_key(rpm_limit=2)

        async def scenario():
            await self.manager.enforce(record)
            await self.manager.enforce(record)
            await self.manager.enforce(record)

        with self.assertRaises(HTTPException) as ctx:
            _run(scenario())
        self.assertEqual(ctx.exception.status_code, 429)
        self.assertIn("Retry-After", ctx.exception.headers)

    def test_tpm_limit_enforced_after_note_tokens(self):
        record = self._make_key(tpm_limit=1000)
        self.manager.note_tokens(record.id, 1500)
        with self.assertRaises(HTTPException) as ctx:
            _run(self.manager.enforce(record))
        self.assertEqual(ctx.exception.status_code, 429)

    def test_budget_exceeded_rejected_429(self):
        record = self._make_key(budget_daily_usd=1.0)
        with patch(
            "core.usage_stats.get_spend_since",
            return_value={"cost_usd": 2.5, "total_tokens": 0, "calls": 3},
        ):
            with self.assertRaises(HTTPException) as ctx:
                _run(self.manager.enforce(record))
        self.assertEqual(ctx.exception.status_code, 429)
        self.assertIn("Budget exceeded", ctx.exception.detail)

    def test_budget_under_limit_allows_request(self):
        record = self._make_key(budget_daily_usd=10.0)
        with patch(
            "core.usage_stats.get_spend_since",
            return_value={"cost_usd": 2.5, "total_tokens": 0, "calls": 3},
        ):
            _run(self.manager.enforce(record))

    def test_budget_cache_avoids_repeated_ledger_queries(self):
        record = self._make_key(budget_daily_usd=10.0)
        with patch(
            "core.usage_stats.get_spend_since",
            return_value={"cost_usd": 0.5, "total_tokens": 0, "calls": 1},
        ) as spend_mock:

            async def scenario():
                await self.manager.enforce(record)
                await self.manager.enforce(record)

            _run(scenario())
        self.assertEqual(spend_mock.call_count, 1)


class ExtractRequestedModelTests(unittest.TestCase):
    def test_extracts_model_from_gemini_path(self):
        self.assertEqual(
            extract_requested_model("/v1beta/models/gemini-2.5-pro:generateContent", None),
            "gemini-2.5-pro",
        )

    def test_extracts_model_from_openai_body(self):
        self.assertEqual(
            extract_requested_model("/v1/chat/completions", {"model": "gpt-4o"}),
            "gpt-4o",
        )

    def test_returns_empty_for_unknown_shapes(self):
        self.assertEqual(extract_requested_model("/v1/models", None), "")
        self.assertEqual(extract_requested_model("/v1/chat/completions", "junk"), "")


if __name__ == "__main__":
    unittest.main()
