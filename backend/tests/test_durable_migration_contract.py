"""Closed W4.13 durable-record and authority migration contract."""

from __future__ import annotations

import dataclasses
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.durable_migration import (
    DURABLE_INVENTORY,
    MIGRATION_SCHEMA_VERSION,
    AuthoritySide,
    DurableBackend,
    DurableFamily,
    DurableRecord,
    FamilyProgress,
    MigrationCheckpoint,
    MigrationPhase,
    checkpoint_from_record,
    compute_records_digest,
)

NOW = datetime(2026, 8, 29, 9, 0, tzinfo=timezone.utc)


def _progress(**overrides) -> FamilyProgress:
    values = {
        "family": DurableFamily.CONFIGURATION,
        "copy_cursor": None,
        "copied_count": 0,
        "copy_complete": False,
        "source_count": None,
        "target_count": None,
        "source_checksum": None,
        "target_checksum": None,
        "verified": False,
    }
    values.update(overrides)
    return FamilyProgress(**values)


def _checkpoint(**overrides) -> MigrationCheckpoint:
    values = {
        "schema_version": MIGRATION_SCHEMA_VERSION,
        "plan_id": "dmg_0123456789abcdef0123456789abcdef",
        "source_backend": DurableBackend.SQLITE,
        "target_backend": DurableBackend.POSTGRESQL,
        "phase": MigrationPhase.PLANNED,
        "authority": AuthoritySide.SOURCE,
        "revision": 1,
        "families": (_progress(),),
        "failure_code": None,
        "created_at": NOW.isoformat(),
        "updated_at": NOW.isoformat(),
    }
    values.update(overrides)
    return MigrationCheckpoint(**values)


class DurableInventoryContractTests(unittest.TestCase):
    def test_inventory_is_closed_complete_and_marks_blocking_gaps(self):
        expected = {
            DurableFamily.CONFIGURATION,
            DurableFamily.PROVIDER_CREDENTIAL,
            DurableFamily.PRIMARY_CREDENTIAL,
            DurableFamily.VIRTUAL_KEY,
            DurableFamily.IDENTITY,
            DurableFamily.ROLE_BINDING,
            DurableFamily.OIDC_POLICY_REVISION,
            DurableFamily.IDENTITY_SCHEMA_EVIDENCE,
            DurableFamily.AUDIT_EVENT,
            DurableFamily.REQUEST_TRACE,
            DurableFamily.USAGE_LEDGER,
            DurableFamily.HARD_BUDGET_RESERVATION,
            DurableFamily.MIGRATION_CHECKPOINT,
        }

        self.assertEqual({entry.family for entry in DURABLE_INVENTORY}, expected)
        self.assertEqual(len(DURABLE_INVENTORY), len(expected))
        readiness = {entry.family: entry.switch_ready for entry in DURABLE_INVENTORY}
        self.assertFalse(readiness[DurableFamily.USAGE_LEDGER])
        self.assertFalse(readiness[DurableFamily.HARD_BUDGET_RESERVATION])
        self.assertTrue(readiness[DurableFamily.AUDIT_EVENT])
        self.assertTrue(readiness[DurableFamily.IDENTITY])

    def test_inventory_and_checkpoint_metadata_have_no_payload_or_secret_fields(self):
        inventory_fields = {field.name for field in dataclasses.fields(DURABLE_INVENTORY[0])}
        checkpoint_fields = {field.name for field in dataclasses.fields(MigrationCheckpoint)}
        family_fields = {field.name for field in dataclasses.fields(FamilyProgress)}

        for fields in (inventory_fields, checkpoint_fields, family_fields):
            self.assertFalse(
                fields
                & {
                    "payload",
                    "record",
                    "credential",
                    "prompt",
                    "subject",
                    "filename",
                    "secret",
                    "token",
                }
            )


class DurableRecordContractTests(unittest.TestCase):
    def test_payload_is_closed_json_and_hidden_from_representations(self):
        record = DurableRecord(
            family=DurableFamily.CONFIGURATION,
            logical_id="cfg_0123456789abcdef",
            schema_version=1,
            payload={"panel_password": "sensitive-value", "enabled": True},
        )

        self.assertNotIn("sensitive-value", repr(record))
        self.assertNotIn("panel_password", repr(record))
        with self.assertRaises(ValueError):
            DurableRecord(
                family=DurableFamily.CONFIGURATION,
                logical_id="cfg_0123456789abcdef",
                schema_version=1,
                payload={"bad": float("nan")},
            )
        with self.assertRaises(ValueError):
            DurableRecord(
                family=DurableFamily.CONFIGURATION,
                logical_id="raw filename.json",
                schema_version=1,
                payload={},
            )

    def test_keyed_digest_is_stable_order_independent_and_content_sensitive(self):
        key = b"k" * 32
        first = DurableRecord(
            family=DurableFamily.AUDIT_EVENT,
            logical_id="aud_1111111111111111",
            schema_version=1,
            payload={"count": 1, "nested": {"ok": True}},
        )
        second = DurableRecord(
            family=DurableFamily.AUDIT_EVENT,
            logical_id="aud_2222222222222222",
            schema_version=1,
            payload={"count": 2},
        )

        digest = compute_records_digest((first, second), integrity_key=key)
        self.assertEqual(digest, compute_records_digest((second, first), integrity_key=key))
        changed = dataclasses.replace(second, payload={"count": 3})
        self.assertNotEqual(digest, compute_records_digest((first, changed), integrity_key=key))
        with self.assertRaises(ValueError):
            compute_records_digest((first,), integrity_key=b"short")


class MigrationCheckpointContractTests(unittest.TestCase):
    def test_checkpoint_requires_one_authority_and_valid_phase_invariants(self):
        with self.assertRaises(ValueError):
            _checkpoint(authority=AuthoritySide.TARGET)

        verified = _progress(
            copy_complete=True,
            copied_count=2,
            source_count=2,
            target_count=2,
            source_checksum="a" * 64,
            target_checksum="a" * 64,
            verified=True,
        )
        ready = _checkpoint(
            phase=MigrationPhase.READY_TO_SWITCH,
            families=(verified,),
            revision=4,
            updated_at=(NOW + timedelta(minutes=1)).isoformat(),
        )
        self.assertIs(ready.authority, AuthoritySide.SOURCE)

        with self.assertRaises(ValueError):
            dataclasses.replace(ready, authority=AuthoritySide.TARGET)
        with self.assertRaises(ValueError):
            dataclasses.replace(
                ready,
                phase=MigrationPhase.TARGET_AUTHORITATIVE,
                authority=AuthoritySide.SOURCE,
            )

    def test_stored_checkpoint_is_exact_revalidated_and_secret_free(self):
        checkpoint = _checkpoint()
        restored = checkpoint_from_record(checkpoint.to_record())
        self.assertEqual(restored, checkpoint)

        with self.assertRaises(ValueError):
            checkpoint_from_record({**checkpoint.to_record(), "secret": "leak"})
        with self.assertRaises(ValueError):
            checkpoint_from_record({**checkpoint.to_record(), "revision": True})
        with self.assertRaises(ValueError):
            checkpoint_from_record({**checkpoint.to_record(), "phase": "dual_authoritative"})

        serialized = repr(checkpoint.to_record()).lower()
        self.assertNotIn("password", serialized)
        self.assertNotIn("credential", serialized)
        self.assertNotIn("prompt", serialized)

    def test_copy_cursor_and_failure_code_are_bounded_machine_values(self):
        with self.assertRaises(ValueError):
            _progress(copy_cursor="raw/filename.json")
        with self.assertRaises(ValueError):
            _checkpoint(failure_code="database said password=secret")


if __name__ == "__main__":
    unittest.main()
