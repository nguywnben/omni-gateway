"""Audit service lifecycle, key management, and redaction tests."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.audit_service import (
    AUDIT_MASTER_KEY_CONFIG,
    AuditService,
    record_credential_response,
)
from core.management_audit import classify_management_mutation


class _Repository:
    def __init__(self):
        self.events = []

    async def append(self, event):
        self.events.append(event)


class _Storage:
    def __init__(self, values=None):
        self.values = dict(values or {})
        self.set_calls = []
        self.cursor_keys = []
        self.repositories = []

    async def get_config(self, key, default=None):
        return self.values.get(key, default)

    async def set_config(self, key, value):
        self.set_calls.append((key, value))
        self.values[key] = value
        return True

    async def create_audit_repository(self, *, cursor_signing_key):
        self.cursor_keys.append(cursor_signing_key)
        repository = _Repository()
        self.repositories.append(repository)
        return repository


class AuditServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_first_start_persists_internal_master_and_redacts_before_append(self):
        storage = _Storage()
        service = await AuditService.create(storage)
        mutation = classify_management_mutation(
            "DELETE",
            "/api/virtual-keys/vk_plaintext-target",
        )

        event = await service.record(
            mutation,
            request_id="request-123",
            actor_type="panel_session",
            actor_identifier="panel-owner",
            outcome="succeeded",
        )

        self.assertEqual(storage.set_calls[0][0], AUDIT_MASTER_KEY_CONFIG)
        self.assertEqual(len(storage.cursor_keys[0]), 32)
        self.assertEqual(storage.repositories[0].events, [event])
        self.assertNotIn("vk_plaintext-target", repr(event.to_record()))
        self.assertNotIn("panel-owner", repr(event.to_record()))

    async def test_restart_reuses_master_for_stable_fingerprints_and_cursors(self):
        storage = _Storage()
        first = await AuditService.create(storage)
        second = await AuditService.create(storage)
        mutation = classify_management_mutation("POST", "/api/config/save")

        first_event = await first.record(
            mutation,
            request_id="first",
            actor_type="panel_session",
            actor_identifier="panel-owner",
            outcome="succeeded",
        )
        second_event = await second.record(
            mutation,
            request_id="second",
            actor_type="panel_session",
            actor_identifier="panel-owner",
            outcome="succeeded",
        )

        self.assertEqual(len(storage.set_calls), 1)
        self.assertEqual(storage.cursor_keys[0], storage.cursor_keys[1])
        self.assertEqual(first_event.actor_fingerprint, second_event.actor_fingerprint)
        self.assertEqual(first_event.target_fingerprint, second_event.target_fingerprint)

    async def test_corrupted_internal_master_fails_closed(self):
        storage = _Storage({AUDIT_MASTER_KEY_CONFIG: "not-a-valid-key"})

        with self.assertRaisesRegex(RuntimeError, "audit master key"):
            await AuditService.create(storage)

    async def test_credential_evidence_maps_to_canonical_durable_contract(self):
        storage = _Storage()
        service = await AuditService.create(storage)

        with patch(
            "core.audit_service.get_audit_service",
            return_value=service,
        ):
            event = await record_credential_response(
                request_id="credential-request",
                action="disable",
                mode="provider",
                filename="customer-secret.json",
                outcome="unsupported",
            )

        self.assertEqual(event.action, "credential.toggle")
        self.assertEqual(event.outcome, "invalid")
        self.assertEqual(event.change_codes, ("disabled",))
        self.assertNotIn("customer-secret.json", repr(event.to_record()))


if __name__ == "__main__":
    unittest.main()
