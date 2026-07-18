from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from starlette.responses import Response

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.api.primary import fetch_provider_model_ids
from core.credential_manager import CredentialManager
from core.model_pool import (
    DEFAULT_VIRTUAL_MODEL_ALIAS,
    ModelCatalogService,
    ModelPoolError,
    ModelResolution,
    get_public_virtual_models,
    get_virtual_model_pool,
    model_catalog_service,
    resolve_model_request,
    save_virtual_model_pool,
)
from core.models import ClaudeRequest, GeminiRequest, OpenAIChatCompletionRequest
from core.router.primary.anthropic import messages as anthropic_messages
from core.router.primary.gemini import generate_content as gemini_generate_content
from core.router.primary.model_list import get_primary_models_with_features
from core.router.primary.openai import chat_completions


class FakeConfigStorage:
    def __init__(self):
        self.values = {}

    async def get_config(self, key, default=None):
        return self.values.get(key, default)

    async def set_config(self, key, value):
        self.values[key] = value
        return True


class FakeCredentialStorage:
    def __init__(self):
        self.credentials = {
            "first.json": {
                "provider": "google_ai_studio",
                "model_ids": ["models/gemini-2.5-flash"],
            },
            "second.json": {
                "provider": "google_ai_studio",
                "model_ids": ["gemma-3-27b-it"],
            },
            "disabled.json": {
                "provider": "google_ai_studio",
                "model_ids": ["gemini-disabled"],
            },
        }

    async def list_credentials(self, mode="primary"):
        return list(self.credentials)

    async def get_credential_state(self, filename, mode="primary"):
        return {"disabled": filename == "disabled.json"}

    async def get_credential(self, filename, mode="primary"):
        return self.credentials.get(filename)


class ModelPoolTests(unittest.IsolatedAsyncioTestCase):
    async def test_catalog_merges_provider_models_without_losing_provenance(self):
        calls = []

        async def load_models():
            calls.append(True)
            return {
                "google_antigravity": ["gemini-2.5-flash", "claude-sonnet-4-6"],
                "google_ai_studio": ["gemini-2.5-flash", "gemma-3-27b-it"],
            }

        service = ModelCatalogService(loader=load_models, ttl_seconds=60)

        first = await service.get_catalog()
        second = await service.get_catalog()

        self.assertEqual(len(calls), 1)
        self.assertEqual(first, second)
        flash = next(entry for entry in first if entry.model_id == "gemini-2.5-flash")
        self.assertEqual(
            flash.providers,
            ("google_ai_studio", "google_antigravity"),
        )

    async def test_virtual_model_pool_round_trips_ordered_models(self):
        storage = FakeConfigStorage()

        saved = await save_virtual_model_pool(
            ["gemini-2.5-flash", "claude-sonnet-4-6", "gemini-2.5-flash"],
            storage_adapter=storage,
        )
        loaded = await get_virtual_model_pool(storage_adapter=storage)

        self.assertEqual(saved["alias"], DEFAULT_VIRTUAL_MODEL_ALIAS)
        self.assertEqual(
            loaded["selected_models"],
            ["gemini-2.5-flash", "claude-sonnet-4-6"],
        )
        self.assertEqual(loaded["strategy"], "priority_fallback")

    async def test_alias_resolves_without_network_catalog_lookup(self):
        storage = FakeConfigStorage()
        await save_virtual_model_pool(
            ["missing-model", "gemini-2.5-flash", "claude-sonnet-4-6"],
            storage_adapter=storage,
        )

        with patch.object(
            model_catalog_service,
            "get_catalog",
            AsyncMock(side_effect=AssertionError("Catalog lookup reached the data path.")),
        ):
            resolution = await resolve_model_request(
                "omway",
                storage_adapter=storage,
            )

        self.assertTrue(resolution.is_virtual)
        self.assertEqual(resolution.response_model, "omway")
        self.assertEqual(
            resolution.candidates,
            ("missing-model", "gemini-2.5-flash", "claude-sonnet-4-6"),
        )

    async def test_concrete_model_passes_through_unchanged(self):
        resolution = await resolve_model_request("gemini-2.5-flash")

        self.assertFalse(resolution.is_virtual)
        self.assertEqual(resolution.candidates, ("gemini-2.5-flash",))
        self.assertEqual(resolution.response_model, "gemini-2.5-flash")

    async def test_empty_disabled_pool_is_not_advertised_or_routable(self):
        storage = FakeConfigStorage()
        await save_virtual_model_pool([], enabled=False, storage_adapter=storage)

        self.assertEqual(await get_public_virtual_models(storage_adapter=storage), [])
        with self.assertRaises(ModelPoolError):
            await resolve_model_request("omway", storage_adapter=storage)

    async def test_configured_alias_remains_in_model_list_during_catalog_outage(self):
        with (
            patch(
                "core.router.primary.model_list.model_catalog_service.get_catalog",
                AsyncMock(return_value=[]),
            ),
            patch(
                "core.router.primary.model_list.get_public_virtual_models",
                AsyncMock(return_value=["omway"]),
            ),
        ):
            models = await get_primary_models_with_features()

        self.assertEqual(models, ["omway"])

    async def test_empty_catalog_is_cached_until_expiry(self):
        loader = AsyncMock(return_value={})
        service = ModelCatalogService(loader=loader, ttl_seconds=60)

        await service.get_catalog()
        await service.get_catalog()

        self.assertEqual(loader.await_count, 1)

    async def test_provider_catalog_unions_models_from_all_enabled_credentials(self):
        storage = FakeCredentialStorage()
        with (
            patch(
                "core.api.primary.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch.object(
                CredentialManager,
                "get_valid_credential",
                AsyncMock(return_value=None),
            ),
        ):
            model_ids = await fetch_provider_model_ids("google_ai_studio")

        self.assertEqual(
            model_ids,
            {"gemini-2.5-flash", "gemma-3-27b-it"},
        )

    async def test_credential_manager_tries_model_candidates_in_order(self):
        manager = CredentialManager()
        manager.get_valid_credential = AsyncMock(
            side_effect=[None, ("credential.json", {"provider": "google_antigravity"})]
        )

        result = await manager.get_valid_model_credential(["gemini-2.5-pro", "gemini-2.5-flash"])

        self.assertEqual(result[0], "gemini-2.5-flash")
        self.assertEqual(result[1], "credential.json")
        self.assertEqual(manager.get_valid_credential.await_count, 2)

    async def test_credential_manager_applies_persistent_blacklist_to_virtual_routes(self):
        manager = CredentialManager()
        manager.get_valid_credential = AsyncMock(
            return_value=(
                "credential.json",
                {"provider": "google_antigravity"},
            )
        )

        with (
            patch(
                "core.credential_manager.get_model_blacklist_pairs",
                AsyncMock(
                    return_value={
                        ("google_ai_studio", "gemini-retired"),
                    }
                ),
            ),
            patch(
                "core.credential_manager.get_credential_model_blacklist_pairs",
                AsyncMock(
                    return_value={
                        ("limited.json", "gemini-retired"),
                    }
                ),
            ),
        ):
            await manager.get_valid_model_credential(
                ["gemini-retired", "claude-sonnet-4-6"],
                respect_model_blacklist=True,
                excluded_provider_models={
                    ("google_antigravity", "claude-sonnet-4-6"),
                },
            )

        self.assertEqual(
            manager.get_valid_credential.await_args.kwargs["excluded_provider_models"],
            {
                ("google_ai_studio", "gemini-retired"),
                ("google_antigravity", "claude-sonnet-4-6"),
            },
        )
        self.assertEqual(
            manager.get_valid_credential.await_args.kwargs["excluded_credential_models"],
            {("limited.json", "gemini-retired")},
        )

    async def test_openai_virtual_model_routes_hi_prompt_and_preserves_alias(self):
        request = OpenAIChatCompletionRequest(
            model="omway",
            messages=[{"role": "user", "content": "Hi"}],
        )
        upstream = Response(
            content=json.dumps(
                {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Hello back"}],
                            },
                            "finishReason": "STOP",
                        }
                    ]
                }
            ),
            media_type="application/json",
        )
        resolution = ModelResolution(
            requested_model="omway",
            response_model="omway",
            candidates=("gemini-2.5-flash", "claude-sonnet-4-6"),
            is_virtual=True,
        )

        with (
            patch(
                "core.router.primary.openai.resolve_model_request",
                AsyncMock(return_value=resolution),
            ),
            patch(
                "core.api.primary.non_stream_request",
                AsyncMock(return_value=upstream),
            ) as routed_request,
        ):
            response = await chat_completions(request, token="test")

        payload = json.loads(response.body)
        self.assertEqual(payload["model"], "omway")
        self.assertEqual(payload["choices"][0]["message"]["content"], "Hello back")
        self.assertEqual(
            routed_request.await_args.kwargs["model_candidates"],
            ["gemini-2.5-flash", "claude-sonnet-4-6"],
        )

    async def test_anthropic_virtual_model_preserves_alias(self):
        request = ClaudeRequest(
            model="omway",
            max_tokens=128,
            messages=[{"role": "user", "content": "Hello"}],
        )
        upstream = Response(
            content=json.dumps(
                {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Hello back"}],
                            },
                            "finishReason": "STOP",
                        }
                    ]
                }
            ),
            media_type="application/json",
        )
        resolution = ModelResolution(
            requested_model="omway",
            response_model="omway",
            candidates=("gemini-2.5-flash", "claude-sonnet-4-6"),
            is_virtual=True,
        )

        with (
            patch(
                "core.router.primary.anthropic.resolve_model_request",
                AsyncMock(return_value=resolution),
            ),
            patch(
                "core.api.primary.non_stream_request",
                AsyncMock(return_value=upstream),
            ) as routed_request,
        ):
            response = await anthropic_messages(request, _token="test")

        payload = json.loads(response.body)
        self.assertEqual(payload["model"], "omway")
        self.assertEqual(payload["content"][0]["text"], "Hello back")
        self.assertEqual(
            routed_request.await_args.kwargs["model_candidates"],
            ["gemini-2.5-flash", "claude-sonnet-4-6"],
        )

    async def test_gemini_virtual_model_routes_ordered_candidates(self):
        request = GeminiRequest(
            contents=[{"role": "user", "parts": [{"text": "Hello"}]}],
        )
        upstream_payload = {
            "candidates": [
                {
                    "content": {
                        "role": "model",
                        "parts": [{"text": "Hello back"}],
                    },
                    "finishReason": "STOP",
                }
            ]
        }
        upstream = Response(
            content=json.dumps(upstream_payload),
            media_type="application/json",
        )
        resolution = ModelResolution(
            requested_model="omway",
            response_model="omway",
            candidates=("gemini-2.5-flash", "claude-sonnet-4-6"),
            is_virtual=True,
        )

        with (
            patch(
                "core.router.primary.gemini.resolve_model_request",
                AsyncMock(return_value=resolution),
            ),
            patch(
                "core.api.primary.non_stream_request",
                AsyncMock(return_value=upstream),
            ) as routed_request,
        ):
            response = await gemini_generate_content(
                request,
                model="omway",
                api_key="test",
            )

        self.assertEqual(json.loads(response.body), upstream_payload)
        self.assertEqual(
            routed_request.await_args.kwargs["model_candidates"],
            ["gemini-2.5-flash", "claude-sonnet-4-6"],
        )


if __name__ == "__main__":
    unittest.main()
