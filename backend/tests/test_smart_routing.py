"""Behavior tests for credential routing."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any, Dict


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.smart_routing import SmartCredentialRouter


class FakeStorageAdapter:
    def __init__(self, states: Dict[str, Dict[str, Any]]) -> None:
        self.states = states
        self.state_reads = 0
        self.credentials = {
            filename: {"token": f"token-{filename}", "project_id": filename}
            for filename in states
        }

    async def get_all_credential_states(self, mode: str = "primary"):
        self.state_reads += 1
        return self.states

    async def get_credential(self, filename: str, mode: str = "primary"):
        value = self.credentials.get(filename)
        return dict(value) if value else None


def credential_state(**overrides: Any) -> Dict[str, Any]:
    state = {
        "disabled": False,
        "error_codes": [],
        "last_success": 0.0,
        "model_cooldowns": {},
        "call_count": 0,
        "rotation_order": 0,
        "preview": False,
        "enable_credit": False,
    }
    state.update(overrides)
    return state


class SmartCredentialRouterTests(unittest.IsolatedAsyncioTestCase):
    async def test_concurrent_acquisitions_spread_across_available_credentials(self):
        now = [100.0]
        storage = FakeStorageAdapter(
            {
                "a.json": credential_state(rotation_order=0),
                "b.json": credential_state(rotation_order=1),
            }
        )
        router = SmartCredentialRouter(clock=lambda: now[0])

        first = await router.acquire(storage, mode="primary", model_name="model-a")
        second = await router.acquire(storage, mode="primary", model_name="model-a")

        self.assertEqual(first[0], "a.json")
        self.assertEqual(second[0], "b.json")
        self.assertEqual(storage.state_reads, 1)

    async def test_recent_failure_temporarily_routes_to_a_healthy_alternative(self):
        now = [100.0]
        storage = FakeStorageAdapter(
            {
                "a.json": credential_state(rotation_order=0),
                "b.json": credential_state(rotation_order=1),
            }
        )
        router = SmartCredentialRouter(
            clock=lambda: now[0],
            base_backoff_seconds=5.0,
            max_backoff_seconds=30.0,
        )

        first = await router.acquire(storage, mode="primary", model_name="model-a")
        await router.complete(first[0], mode="primary", success=False)
        second = await router.acquire(storage, mode="primary", model_name="model-a")

        self.assertEqual(first[0], "a.json")
        self.assertEqual(second[0], "b.json")

    async def test_all_credentials_in_backoff_are_not_reused_immediately(self):
        now = [100.0]
        storage = FakeStorageAdapter(
            {
                "a.json": credential_state(rotation_order=0),
                "b.json": credential_state(rotation_order=1),
            }
        )
        router = SmartCredentialRouter(
            clock=lambda: now[0],
            base_backoff_seconds=5.0,
            max_backoff_seconds=30.0,
        )

        first = await router.acquire(storage, mode="primary", model_name="model-a")
        await router.complete(first[0], mode="primary", success=False)
        second = await router.acquire(storage, mode="primary", model_name="model-a")
        await router.complete(second[0], mode="primary", success=False)

        self.assertIsNone(
            await router.acquire(storage, mode="primary", model_name="model-a")
        )

        now[0] = 105.0
        self.assertIsNotNone(
            await router.acquire(storage, mode="primary", model_name="model-a")
        )

    async def test_historical_call_count_does_not_flood_a_new_credential(self):
        storage = FakeStorageAdapter(
            {
                "established.json": credential_state(
                    call_count=1000, last_success=10.0, rotation_order=0
                ),
                "new.json": credential_state(
                    call_count=0, last_success=20.0, rotation_order=1
                ),
            }
        )
        router = SmartCredentialRouter(clock=lambda: 100.0)

        result = await router.acquire(
            storage, mode="primary", model_name="model-a"
        )

        self.assertEqual(result[0], "established.json")

    async def test_sequential_requests_rotate_by_last_selection(self):
        storage = FakeStorageAdapter(
            {
                "a.json": credential_state(last_success=0.0, rotation_order=0),
                "b.json": credential_state(last_success=0.0, rotation_order=1),
            }
        )
        now = [100.0]
        router = SmartCredentialRouter(clock=lambda: now[0])

        first = await router.acquire(storage, mode="primary", model_name="model-a")
        await router.complete(first[0], mode="primary", success=True)
        now[0] = 101.0
        second = await router.acquire(storage, mode="primary", model_name="model-a")

        self.assertEqual((first[0], second[0]), ("a.json", "b.json"))

    async def test_disabled_and_model_cooldown_credentials_are_not_selected(self):
        now = [100.0]
        storage = FakeStorageAdapter(
            {
                "disabled.json": credential_state(disabled=True),
                "cooldown.json": credential_state(
                    model_cooldowns={"model-a": 200.0}, rotation_order=1
                ),
                "ready.json": credential_state(rotation_order=2),
            }
        )
        router = SmartCredentialRouter(clock=lambda: now[0])

        result = await router.acquire(storage, mode="primary", model_name="model-a")

        self.assertEqual(result[0], "ready.json")

    async def test_preview_models_only_use_preview_compatible_credentials(self):
        storage = FakeStorageAdapter(
            {
                "standard.json": credential_state(preview=False, rotation_order=0),
                "preview.json": credential_state(preview=True, rotation_order=1),
            }
        )
        router = SmartCredentialRouter(clock=lambda: 100.0)

        result = await router.acquire(
            storage, mode="code_assist", model_name="model-preview"
        )

        self.assertEqual(result[0], "preview.json")

    async def test_provider_capabilities_exclude_ai_studio_for_claude(self):
        storage = FakeStorageAdapter(
            {
                "ai-studio.json": credential_state(rotation_order=0),
                "antigravity.json": credential_state(rotation_order=1),
            }
        )
        storage.credentials["ai-studio.json"] = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "example-key",
        }
        storage.credentials["antigravity.json"] = {
            "provider": "google_antigravity",
            "token": "access-token",
            "project_id": "project",
        }
        router = SmartCredentialRouter(clock=lambda: 100.0)

        result = await router.acquire(
            storage, mode="primary", model_name="claude-sonnet-4-6"
        )

        self.assertEqual(result[0], "antigravity.json")

    async def test_explicit_provider_filter_selects_matching_credential(self):
        storage = FakeStorageAdapter(
            {
                "antigravity.json": credential_state(rotation_order=0),
                "ai-studio.json": credential_state(rotation_order=1),
            }
        )
        storage.credentials["antigravity.json"]["provider"] = "google_antigravity"
        storage.credentials["ai-studio.json"] = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "example-key",
        }
        router = SmartCredentialRouter(clock=lambda: 100.0)

        result = await router.acquire(
            storage,
            mode="primary",
            model_name="gemini-2.5-flash",
            provider_id="google_ai_studio",
        )

        self.assertEqual(result[0], "ai-studio.json")

    async def test_priority_strategy_prefers_the_configured_provider(self):
        storage = FakeStorageAdapter(
            {
                "antigravity.json": credential_state(rotation_order=0),
                "ai-studio.json": credential_state(rotation_order=1),
            }
        )
        storage.credentials["antigravity.json"]["provider"] = "google_antigravity"
        storage.credentials["ai-studio.json"] = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "example-key",
        }
        router = SmartCredentialRouter(clock=lambda: 100.0)

        result = await router.acquire(
            storage,
            mode="primary",
            model_name="gemini-2.5-flash",
            routing_strategy="priority",
            preferred_provider="google_ai_studio",
        )

        self.assertEqual(result[0], "ai-studio.json")

    async def test_priority_strategy_falls_back_when_preferred_provider_is_unavailable(self):
        storage = FakeStorageAdapter(
            {
                "antigravity.json": credential_state(rotation_order=0),
                "ai-studio.json": credential_state(disabled=True, rotation_order=1),
            }
        )
        storage.credentials["antigravity.json"]["provider"] = "google_antigravity"
        storage.credentials["ai-studio.json"] = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "example-key",
        }
        router = SmartCredentialRouter(clock=lambda: 100.0)

        result = await router.acquire(
            storage,
            mode="primary",
            model_name="gemini-2.5-flash",
            routing_strategy="priority",
            preferred_provider="google_ai_studio",
        )

        self.assertEqual(result[0], "antigravity.json")


if __name__ == "__main__":
    unittest.main()
