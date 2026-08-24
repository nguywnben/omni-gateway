"""Credential batch preview and typed execution contract tests."""

from __future__ import annotations

import asyncio
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from pydantic import ValidationError

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.models import CredFileBatchActionRequest
from core.panel.credentials import creds_batch_action
from core.panel.credentials import router as credentials_router


class CredentialBatchOperationTests(unittest.IsolatedAsyncioTestCase):
    async def test_preview_is_side_effect_free_and_returns_a_typed_plan(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.credential_manager.set_cred_disabled",
                new=AsyncMock(),
            ) as mutate,
        ):
            response = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="disable",
                    filenames=["studio.json"],
                    preview=True,
                ),
                token="session",
                mode="provider",
            )

        body = json.loads(response.body)
        self.assertTrue(body["preview"])
        self.assertEqual(body["results"][0]["status"], "eligible")
        self.assertEqual(body["results"][0]["operation"], "toggle")
        self.assertTrue(body["preview_token"])
        self.assertNotIn("must-not-leak", response.body.decode())
        mutate.assert_not_awaited()

    async def test_delete_requires_a_matching_preview(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.credential_manager.remove_credential",
                new=AsyncMock(return_value=True),
            ) as remove,
        ):
            response = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="delete",
                    filenames=["studio.json"],
                ),
                token="session",
                mode="provider",
            )

        body = json.loads(response.body)
        self.assertEqual(response.status_code, 428)
        self.assertEqual(body["error"]["code"], "credential_batch_preview_required")
        remove.assert_not_awaited()

    async def test_mixed_batch_returns_supported_and_unsupported_item_outcomes(self):
        storage = AsyncMock()
        storage.get_credential.side_effect = [
            {
                "provider": "google_ai_studio",
                "credential_type": "api_key",
                "api_key": "secret-one",
            },
            {
                "provider": "unregistered-provider",
                "credential_type": "api_key",
                "api_key": "secret-two",
            },
        ]

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.credential_manager.set_cred_disabled",
                new=AsyncMock(return_value=True),
            ) as mutate,
        ):
            response = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="disable",
                    filenames=["studio.json", "unknown.json"],
                ),
                token="session",
                mode="provider",
            )

        body = json.loads(response.body)
        self.assertEqual([item["status"] for item in body["results"]], ["succeeded", "unsupported"])
        self.assertEqual(body["outcome_counts"]["succeeded"], 1)
        self.assertEqual(body["outcome_counts"]["unsupported"], 1)
        self.assertEqual(body["success_count"], 1)
        self.assertNotIn("secret-one", response.body.decode())
        self.assertNotIn("secret-two", response.body.decode())
        mutate.assert_awaited_once()

    async def test_duplicate_target_is_reported_and_executed_only_once(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.credential_manager.set_cred_disabled",
                new=AsyncMock(return_value=True),
            ) as mutate,
        ):
            response = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="disable",
                    filenames=["studio.json", "studio.json"],
                ),
                token="session",
                mode="provider",
            )

        body = json.loads(response.body)
        self.assertEqual([item["status"] for item in body["results"]], ["succeeded", "duplicate"])
        mutate.assert_awaited_once()

    async def test_matching_preview_executes_delete_and_rechecks_stale_capability(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.credential_manager.remove_credential",
                new=AsyncMock(return_value=True),
            ) as remove,
        ):
            preview = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="delete",
                    filenames=["studio.json"],
                    preview=True,
                ),
                token="session",
                mode="provider",
            )
            preview_body = json.loads(preview.body)
            storage.get_credential.return_value = {
                "provider": "unregistered-provider",
                "credential_type": "api_key",
                "api_key": "new-secret",
            }
            execution = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="delete",
                    filenames=["studio.json"],
                    preview_token=preview_body["preview_token"],
                    idempotency_key="delete-studio-001",
                ),
                token="session",
                mode="provider",
            )

        body = json.loads(execution.body)
        self.assertEqual(body["results"][0]["status"], "unsupported")
        self.assertEqual(body["success_count"], 0)
        self.assertNotIn("new-secret", execution.body.decode())
        remove.assert_not_awaited()

    async def test_matching_preview_and_idempotency_key_executes_delete_once(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.credential_manager.remove_credential",
                new=AsyncMock(return_value=True),
            ) as remove,
        ):
            preview = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="delete", filenames=["studio.json"], preview=True
                ),
                token="session",
                mode="provider",
            )
            preview_token = json.loads(preview.body)["preview_token"]
            request = CredFileBatchActionRequest(
                action="delete",
                filenames=["studio.json"],
                preview_token=preview_token,
                idempotency_key="delete-studio-002",
            )
            first = await creds_batch_action(request, token="session", mode="provider")
            second = await creds_batch_action(request, token="session", mode="provider")

        self.assertEqual(first.body, second.body)
        self.assertEqual(json.loads(first.body)["success_count"], 1)
        remove.assert_awaited_once()

    async def test_per_item_timeout_is_typed_and_does_not_fail_the_batch(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        async def slow_operation(*_args, **_kwargs):
            await asyncio.sleep(0.05)

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch("core.panel.credentials.BATCH_ITEM_TIMEOUT_SECONDS", 0.001),
            patch("core.panel.credentials._execute_credential_action", slow_operation),
        ):
            response = await creds_batch_action(
                CredFileBatchActionRequest(action="disable", filenames=["studio.json"]),
                token="session",
                mode="provider",
            )

        body = json.loads(response.body)
        self.assertEqual(body["results"][0]["status"], "timed_out")
        self.assertEqual(body["outcome_counts"]["timed_out"], 1)

    def test_batch_selection_is_bounded_to_one_hundred_targets(self):
        with self.assertRaises(ValidationError):
            CredFileBatchActionRequest(
                action="disable",
                filenames=[f"credential-{index}.json" for index in range(101)],
            )

    async def test_preview_token_is_bound_to_the_exact_selection(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        with patch(
            "core.panel.credentials.get_storage_adapter",
            AsyncMock(return_value=storage),
        ):
            preview = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="delete", filenames=["first.json"], preview=True
                ),
                token="session",
                mode="provider",
            )
            response = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="delete",
                    filenames=["second.json"],
                    preview_token=json.loads(preview.body)["preview_token"],
                    idempotency_key="delete-second-001",
                ),
                token="session",
                mode="provider",
            )

        body = json.loads(response.body)
        self.assertEqual(response.status_code, 428)
        self.assertEqual(body["error"]["code"], "credential_batch_preview_required")

    async def test_idempotency_key_reuse_for_another_request_is_rejected(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.credential_manager.set_cred_disabled",
                new=AsyncMock(return_value=True),
            ),
        ):
            await creds_batch_action(
                CredFileBatchActionRequest(
                    action="disable",
                    filenames=["first.json"],
                    idempotency_key="shared-key-001",
                ),
                token="session",
                mode="provider",
            )
            response = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="disable",
                    filenames=["second.json"],
                    idempotency_key="shared-key-001",
                ),
                token="session",
                mode="provider",
            )

        body = json.loads(response.body)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(body["error"]["code"], "credential_batch_idempotency_conflict")

    async def test_high_volume_batch_requires_preview_before_storage_access(self):
        get_storage = AsyncMock()
        with patch("core.panel.credentials.get_storage_adapter", get_storage):
            response = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="disable",
                    filenames=[f"credential-{index}.json" for index in range(20)],
                ),
                token="session",
                mode="provider",
            )

        self.assertEqual(response.status_code, 428)
        get_storage.assert_not_awaited()

    async def test_code_assist_credit_preview_is_never_marked_eligible(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "google_antigravity",
            "credential_type": "oauth",
            "access_token": "must-not-leak",
        }
        with patch(
            "core.panel.credentials.get_storage_adapter",
            AsyncMock(return_value=storage),
        ):
            response = await creds_batch_action(
                CredFileBatchActionRequest(
                    action="enable_credit",
                    filenames=["code-assist.json"],
                    preview=True,
                ),
                token="session",
                mode="code_assist",
            )

        body = json.loads(response.body)
        self.assertEqual(body["results"][0]["status"], "unsupported")

    def test_batch_route_publishes_the_typed_success_contract(self):
        route = next(
            route for route in credentials_router.routes if route.path == "/batch-action"
        )
        self.assertIsNotNone(route.response_model)
        self.assertEqual(route.response_model.__name__, "CredentialBatchOperationResponse")

    async def test_concurrent_same_idempotency_key_executes_mutation_once(self):
        storage = AsyncMock()
        storage.get_credential.return_value = {
            "provider": "google_ai_studio",
            "credential_type": "api_key",
            "api_key": "must-not-leak",
        }

        async def slow_mutation(*_args, **_kwargs):
            await asyncio.sleep(0.02)
            return True

        mutate = AsyncMock(side_effect=slow_mutation)
        request = CredFileBatchActionRequest(
            action="disable",
            filenames=["studio.json"],
            idempotency_key="concurrent-disable-001",
        )

        with (
            patch(
                "core.panel.credentials.get_storage_adapter",
                AsyncMock(return_value=storage),
            ),
            patch(
                "core.panel.credentials.credential_manager.set_cred_disabled",
                new=mutate,
            ),
        ):
            first, second = await asyncio.gather(
                creds_batch_action(request, token="session", mode="provider"),
                creds_batch_action(request, token="session", mode="provider"),
            )

        self.assertEqual(sorted([first.status_code, second.status_code]), [200, 409])
        mutate.assert_awaited_once()

    async def test_cancelled_execution_releases_idempotency_reservation(self):
        started = asyncio.Event()
        never_complete = asyncio.Event()
        storage = AsyncMock()

        async def blocked_read(*_args, **_kwargs):
            started.set()
            await never_complete.wait()

        storage.get_credential.side_effect = blocked_read
        get_storage = AsyncMock(return_value=storage)
        request = CredFileBatchActionRequest(
            action="disable",
            filenames=["studio.json"],
            idempotency_key="cancelled-disable-001",
        )

        with patch("core.panel.credentials.get_storage_adapter", get_storage):
            task = asyncio.create_task(
                creds_batch_action(request, token="session", mode="provider")
            )
            await started.wait()
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task

        storage.get_credential = AsyncMock(
            return_value={
                "provider": "google_ai_studio",
                "credential_type": "api_key",
                "api_key": "must-not-leak",
            }
        )
        with (
            patch("core.panel.credentials.get_storage_adapter", get_storage),
            patch(
                "core.panel.credentials.credential_manager.set_cred_disabled",
                new=AsyncMock(return_value=True),
            ),
        ):
            retry = await creds_batch_action(request, token="session", mode="provider")

        self.assertEqual(retry.status_code, 200)


if __name__ == "__main__":
    unittest.main()
