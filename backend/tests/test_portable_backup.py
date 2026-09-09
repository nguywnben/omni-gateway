"""Portable SQLite backup, validation, restore, and sanitized-export contracts."""

from __future__ import annotations

import asyncio
import io
import json
import os
import shutil
import sqlite3
import sys
import unittest
import uuid
import zipfile
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.encrypted_backup import decrypt_bytes, encrypt_bytes
from core.portable_backup import (
    BackupArchiveError,
    BackupConflictError,
    BackupRestoreError,
    PortableBackupService,
    RestoreConflictPolicy,
)
from core.storage.sqlite_manager import SQLiteManager

PASSPHRASE = "portable backup test passphrase"


async def _initialize_state(root: Path, marker: str) -> None:
    await asyncio.to_thread(root.mkdir, parents=True, exist_ok=True)
    with patch.dict(os.environ, {"CREDENTIALS_DIR": str(root)}):
        manager = SQLiteManager()
        await manager.initialize()
        await manager.create_audit_repository(cursor_signing_key=b"a" * 32)
        await manager.create_identity_repository()
        await manager.create_migration_checkpoint_repository()
        await manager.create_request_trace_repository(cursor_signing_key=b"b" * 32)
        await manager.create_usage_ledger_repository()
        await manager.store_credential(
            f"{marker}.json",
            {
                "provider": "openai_platform",
                "credential_type": "api_key",
                "api_key": f"sk-live-{marker}-must-not-leak",
            },
            mode="primary",
        )
        await manager.set_config("api_key", f"sk-ogw-{marker}-root-secret")
        await manager.set_config("panel_password", f"scrypt${marker}-password-hash")
        await manager.set_config("routing_strategy", marker)
        await manager.set_config(
            "virtual_model_pool",
            {
                "alias": "omway",
                "strategy": "priority_fallback",
                "selected_models": ["gpt-test"],
                "enabled": True,
            },
        )
        await manager.set_config(
            "quality_policy_document",
            {"schema_version": 1, "revision": 1, "profile": "balanced"},
        )
        await manager.set_config(
            "virtual_keys",
            [
                {
                    "schema_version": 2,
                    "id": f"vk_{marker}",
                    "name": "Automation",
                    "key_hash": f"scrypt$virtual-{marker}-hash",
                    "key_preview": "sk-ogw-vk-...abcd",
                    "enabled": True,
                }
            ],
        )
        await manager.close()


def _read_config(database: Path, key: str) -> object:
    with sqlite3.connect(database) as connection:
        row = connection.execute("SELECT value FROM config WHERE key = ?", (key,)).fetchone()
    return json.loads(row[0]) if row else None


def _rewrite_archive(encrypted: bytes, transform) -> bytes:
    source = io.BytesIO(decrypt_bytes(encrypted, PASSPHRASE))
    output = io.BytesIO()
    with (
        zipfile.ZipFile(source, "r") as archive,
        zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as rewritten,
    ):
        for entry in archive.infolist():
            transformed = transform(entry.filename, archive.read(entry))
            if transformed is not None:
                name, data = transformed
                rewritten.writestr(name, data)
    return encrypt_bytes(output.getvalue(), PASSPHRASE)


class PortableBackupTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        test_root = Path(os.environ["CREDENTIALS_DIR"]).parent
        test_root.mkdir(parents=True, exist_ok=True)
        base = test_root / f"portable-backup-{uuid.uuid4().hex}"
        base.mkdir()
        self._base = base
        self.source = base / "source"
        self.destination = base / "destination"
        await _initialize_state(self.source, "source")
        await _initialize_state(self.destination, "destination")
        self.source_service = PortableBackupService(
            self.source / "credentials.db",
            credentials_dir=self.source,
            application_version="1.4.0",
        )
        self.destination_service = PortableBackupService(
            self.destination / "credentials.db",
            credentials_dir=self.destination,
            application_version="1.4.0",
        )

    async def asyncTearDown(self) -> None:
        shutil.rmtree(self._base, ignore_errors=True)

    async def test_encrypted_roundtrip_restores_routing_access_and_credentials(self) -> None:
        artifact = await self.source_service.create_backup(PASSPHRASE)
        plan = await self.destination_service.validate_restore(
            artifact.content,
            PASSPHRASE,
            conflict_policy=RestoreConflictPolicy.REPLACE,
        )

        self.assertTrue(plan.compatible)
        self.assertEqual(plan.archive_version, 1)
        self.assertIn("credentials", plan.components)
        self.assertNotIn("raw_logs", plan.components)
        result = await self.destination_service.restore(
            artifact.content,
            PASSPHRASE,
            conflict_policy=RestoreConflictPolicy.REPLACE,
        )

        self.assertTrue(result.restored)
        self.assertTrue(result.pre_restore_snapshot_id.startswith("pre-restore-"))
        self.assertEqual(
            _read_config(self.destination / "credentials.db", "routing_strategy"),
            "source",
        )
        self.assertEqual(
            _read_config(self.destination / "credentials.db", "api_key"),
            "sk-ogw-source-root-secret",
        )
        with sqlite3.connect(self.destination / "credentials.db") as connection:
            credential = connection.execute(
                "SELECT credential_data FROM primary_credentials WHERE filename = ?",
                ("source.json",),
            ).fetchone()
        self.assertIn("sk-live-source-must-not-leak", credential[0])
        self.assertEqual(len(list((self.destination / "backups").glob("*.ogb"))), 1)

    async def test_dry_run_and_abort_policy_do_not_mutate_or_snapshot(self) -> None:
        artifact = await self.source_service.create_backup(PASSPHRASE)

        with self.assertRaises(BackupConflictError):
            await self.destination_service.validate_restore(
                artifact.content,
                PASSPHRASE,
                conflict_policy=RestoreConflictPolicy.ABORT_IF_CONFIGURED,
            )

        self.assertEqual(
            _read_config(self.destination / "credentials.db", "routing_strategy"),
            "destination",
        )
        self.assertFalse((self.destination / "backups").exists())

    async def test_corrupted_manifest_hash_fails_before_mutation(self) -> None:
        artifact = await self.source_service.create_backup(PASSPHRASE)

        def corrupt(name: str, data: bytes):
            if name == "state/credentials.db":
                return name, data[:-1] + bytes([data[-1] ^ 1])
            return name, data

        corrupted = _rewrite_archive(artifact.content, corrupt)
        with self.assertRaisesRegex(BackupArchiveError, "hash"):
            await self.destination_service.restore(
                corrupted,
                PASSPHRASE,
                conflict_policy=RestoreConflictPolicy.REPLACE,
            )

        self.assertEqual(
            _read_config(self.destination / "credentials.db", "routing_strategy"),
            "destination",
        )

    async def test_traversal_and_unknown_members_fail_closed(self) -> None:
        artifact = await self.source_service.create_backup(PASSPHRASE)

        def add_traversal(name: str, data: bytes):
            if name == "manifest.json":
                return "../manifest.json", data
            return name, data

        malicious = _rewrite_archive(artifact.content, add_traversal)
        with self.assertRaises(BackupArchiveError):
            await self.destination_service.validate_restore(
                malicious,
                PASSPHRASE,
                conflict_policy=RestoreConflictPolicy.REPLACE,
            )

    async def test_oversized_member_fails_before_reading_database(self) -> None:
        artifact = await self.source_service.create_backup(PASSPHRASE)
        with patch("core.portable_backup.MAX_BACKUP_DATABASE_BYTES", 16):
            with self.assertRaisesRegex(BackupArchiveError, "size"):
                await self.destination_service.validate_restore(
                    artifact.content,
                    PASSPHRASE,
                    conflict_policy=RestoreConflictPolicy.REPLACE,
                )

    async def test_incompatible_schema_fails_closed(self) -> None:
        artifact = await self.source_service.create_backup(PASSPHRASE)

        def alter_manifest(name: str, data: bytes):
            if name == "manifest.json":
                manifest = json.loads(data)
                manifest["state_schema_version"] = 999
                return name, json.dumps(manifest, sort_keys=True).encode()
            return name, data

        incompatible = _rewrite_archive(artifact.content, alter_manifest)
        with self.assertRaisesRegex(BackupArchiveError, "version"):
            await self.destination_service.validate_restore(
                incompatible,
                PASSPHRASE,
                conflict_policy=RestoreConflictPolicy.REPLACE,
            )

    async def test_restore_rolls_back_database_when_secondary_state_write_fails(self) -> None:
        (self.source / "model_pricing.json").write_text(
            '{"gpt-test":{"input":1,"output":2}}', encoding="utf-8"
        )
        artifact = await self.source_service.create_backup(PASSPHRASE)

        with patch.object(
            self.destination_service,
            "_replace_pricing_override",
            side_effect=OSError("injected failure"),
        ):
            with self.assertRaises(BackupRestoreError):
                await self.destination_service.restore(
                    artifact.content,
                    PASSPHRASE,
                    conflict_policy=RestoreConflictPolicy.REPLACE,
                )

        self.assertEqual(
            _read_config(self.destination / "credentials.db", "routing_strategy"),
            "destination",
        )

    async def test_sanitized_export_contains_inventory_but_no_usable_secret(self) -> None:
        exported = json.loads(await self.source_service.create_sanitized_export())
        serialized = json.dumps(exported, sort_keys=True)

        self.assertEqual(exported["format"], "omni-gateway-sanitized-state")
        self.assertEqual(exported["version"], 1)
        self.assertEqual(exported["credentials"]["primary"], 1)
        self.assertEqual(exported["virtual_keys"]["configured"], 1)
        self.assertNotIn("sk-live-source-must-not-leak", serialized)
        self.assertNotIn("sk-ogw-source-root-secret", serialized)
        self.assertNotIn("source-password-hash", serialized)
        self.assertNotIn("virtual-source-hash", serialized)
        self.assertNotIn("key_preview", serialized)


if __name__ == "__main__":
    unittest.main()
