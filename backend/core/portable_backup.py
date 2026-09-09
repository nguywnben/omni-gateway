"""Versioned portable backup, validation, restore, and sanitized export.

Only the canonical SQLite state plane is supported in R1. Archive paths are a
closed allowlist and are read without extraction. Restore first creates a
passphrase-encrypted local snapshot, then uses SQLite's transactional backup
API to replace the live database.
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import json
import os
import re
import shutil
import sqlite3
import stat
import uuid
import zipfile
from collections.abc import Awaitable, Callable
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any

from app_version import get_application_version
from core.configuration_schema import CONFIGURATION_FIELDS, ConfigValueType
from core.encrypted_backup import (
    MAX_BACKUP_ENVELOPE_BYTES,
    BackupEnvelopeError,
    decrypt_bytes,
    encrypt_bytes,
)

BACKUP_ARCHIVE_FORMAT = "omni-gateway-portable-state"
BACKUP_ARCHIVE_VERSION = 1
BACKUP_STATE_SCHEMA_VERSION = 1
SANITIZED_EXPORT_FORMAT = "omni-gateway-sanitized-state"
SANITIZED_EXPORT_VERSION = 1
BACKUP_EXTENSION = ".ogb"
MAX_BACKUP_UPLOAD_BYTES = 64 * 1024 * 1024
MAX_BACKUP_DATABASE_BYTES = 120 * 1024 * 1024
MAX_BACKUP_PRICING_BYTES = 1024 * 1024
MAX_BACKUP_MANIFEST_BYTES = 64 * 1024
MAX_BACKUP_UNCOMPRESSED_BYTES = 122 * 1024 * 1024
MAX_BACKUP_COMPRESSION_RATIO = 200

_DATABASE_MEMBER = "state/credentials.db"
_PRICING_MEMBER = "state/model_pricing.json"
_MANIFEST_MEMBER = "manifest.json"
_ALLOWED_MEMBERS = frozenset({_MANIFEST_MEMBER, _DATABASE_MEMBER, _PRICING_MEMBER})
_REQUIRED_MEMBERS = frozenset({_MANIFEST_MEMBER, _DATABASE_MEMBER})
_CORE_TABLES = frozenset(
    {
        "audit_events",
        "config",
        "credentials",
        "durable_migration_checkpoints",
        "durable_usage_ledger",
        "durable_usage_migrations",
        "identity_migrations",
        "management_identities",
        "management_role_bindings",
        "oidc_policy_revision",
        "primary_credentials",
        "request_traces",
    }
)
_COMPONENTS = (
    "audit",
    "configuration",
    "credentials",
    "identity",
    "ledgers",
    "quality_policy",
    "request_traces",
    "routes",
    "virtual_keys",
)
_EXCLUDED = ("legacy_usage_stats", "pre_restore_snapshots", "raw_logs")
_MANIFEST_FIELDS = frozenset(
    {
        "format",
        "archive_version",
        "state_schema_version",
        "application_version",
        "created_at",
        "schema_fingerprint",
        "components",
        "excluded",
        "contents",
        "table_counts",
    }
)
_CONTENT_FIELDS = frozenset({"path", "media_type", "size_bytes", "sha256"})
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
_maintenance_lock = asyncio.Lock()


class BackupError(RuntimeError):
    """Base class for safe backup workflow failures."""


class BackupBackendError(BackupError):
    """Raised when portable restore is requested for a non-SQLite backend."""


class BackupArchiveError(BackupError):
    """Raised when an archive is corrupt, unsafe, or incompatible."""


class BackupConflictError(BackupError):
    """Raised when the requested conflict policy prevents replacement."""


class BackupRestoreError(BackupError):
    """Raised when replacement fails and the previous state is rolled back."""


class RestoreConflictPolicy(StrEnum):
    ABORT_IF_CONFIGURED = "abort_if_configured"
    REPLACE = "replace"


@dataclass(frozen=True, slots=True)
class BackupArtifact:
    content: bytes
    filename: str
    created_at: str
    manifest: dict[str, Any]


@dataclass(frozen=True, slots=True)
class RestorePlan:
    compatible: bool
    archive_version: int
    source_application_version: str
    created_at: str
    conflict_policy: str
    components: tuple[str, ...]
    excluded: tuple[str, ...]
    table_counts: dict[str, int]
    pricing_override_included: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "compatible": self.compatible,
            "archive_version": self.archive_version,
            "source_application_version": self.source_application_version,
            "created_at": self.created_at,
            "conflict_policy": self.conflict_policy,
            "components": list(self.components),
            "excluded": list(self.excluded),
            "table_counts": dict(self.table_counts),
            "pricing_override_included": self.pricing_override_included,
        }


@dataclass(frozen=True, slots=True)
class RestoreResult:
    restored: bool
    pre_restore_snapshot_id: str
    source_application_version: str
    restored_at: str
    components: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "restored": self.restored,
            "pre_restore_snapshot_id": self.pre_restore_snapshot_id,
            "source_application_version": self.source_application_version,
            "restored_at": self.restored_at,
            "components": list(self.components),
        }


@dataclass(frozen=True, slots=True)
class _ValidatedArchive:
    manifest: dict[str, Any]
    database_path: Path
    pricing_override: bytes | None


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp(value: datetime | None = None) -> str:
    return (value or _utc_now()).astimezone(timezone.utc).isoformat()


@contextmanager
def _work_directory(root: Path, prefix: str):
    path = root / f".{prefix}-{uuid.uuid4().hex}"
    path.mkdir()
    if os.name != "nt":
        os.chmod(path, 0o700)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _reject_duplicate_fields(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise BackupArchiveError("Backup JSON contains duplicate fields.")
        result[key] = value
    return result


def _load_json_object(value: bytes, *, label: str, maximum: int) -> dict[str, Any]:
    if not value or len(value) > maximum:
        raise BackupArchiveError(f"Backup {label} size is invalid.")
    try:
        parsed = json.loads(
            value.decode("utf-8", errors="strict"),
            object_pairs_hook=_reject_duplicate_fields,
        )
    except BackupArchiveError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BackupArchiveError(f"Backup {label} is invalid.") from exc
    if not isinstance(parsed, dict):
        raise BackupArchiveError(f"Backup {label} must be an object.")
    return parsed


def _safe_database_uri(path: Path) -> str:
    return f"{path.resolve().as_uri()}?mode=ro"


def _sqlite_backup(source_path: Path, destination_path: Path) -> None:
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with (
        sqlite3.connect(_safe_database_uri(source_path), uri=True, timeout=30) as source,
        sqlite3.connect(destination_path, timeout=30) as destination,
    ):
        source.backup(destination, pages=1024, sleep=0.01)


def _database_schema_fingerprint(connection: sqlite3.Connection) -> str:
    rows = connection.execute(
        "SELECT type, name, tbl_name, COALESCE(sql, '') FROM sqlite_master "
        "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
    ).fetchall()
    return _sha256(_canonical_json([list(row) for row in rows]))


def _inspect_database(path: Path) -> tuple[str, dict[str, int]]:
    if not path.is_file() or path.is_symlink():
        raise BackupArchiveError("Backup database is missing or unsafe.")
    size = path.stat().st_size
    if size <= 0 or size > MAX_BACKUP_DATABASE_BYTES:
        raise BackupArchiveError("Backup database size is invalid.")
    try:
        with sqlite3.connect(_safe_database_uri(path), uri=True, timeout=30) as connection:
            integrity = connection.execute("PRAGMA quick_check").fetchone()
            if integrity != ("ok",):
                raise BackupArchiveError("Backup database integrity check failed.")
            if connection.execute("PRAGMA foreign_key_check").fetchone() is not None:
                raise BackupArchiveError("Backup database foreign keys are invalid.")
            tables = {
                str(row[0])
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            }
            if not _CORE_TABLES.issubset(tables):
                raise BackupArchiveError("Backup database schema is incomplete.")
            counts = {
                table: int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])
                for table in sorted(tables - {"sqlite_sequence"})
            }
            return _database_schema_fingerprint(connection), counts
    except BackupArchiveError:
        raise
    except sqlite3.Error as exc:
        raise BackupArchiveError("Backup database is invalid.") from exc


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o600 << 16
    return info


def _content_record(path: str, value: bytes, media_type: str) -> dict[str, Any]:
    return {
        "path": path,
        "media_type": media_type,
        "size_bytes": len(value),
        "sha256": _sha256(value),
    }


def _build_archive(
    database_path: Path,
    *,
    application_version: str,
    created_at: str,
    pricing_override: bytes | None,
) -> tuple[bytes, dict[str, Any]]:
    schema_fingerprint, table_counts = _inspect_database(database_path)
    database = database_path.read_bytes()
    records = [
        _content_record(_DATABASE_MEMBER, database, "application/vnd.sqlite3"),
    ]
    if pricing_override is not None:
        _load_json_object(
            pricing_override,
            label="pricing override",
            maximum=MAX_BACKUP_PRICING_BYTES,
        )
        records.append(_content_record(_PRICING_MEMBER, pricing_override, "application/json"))
    records.sort(key=lambda item: item["path"])
    manifest = {
        "format": BACKUP_ARCHIVE_FORMAT,
        "archive_version": BACKUP_ARCHIVE_VERSION,
        "state_schema_version": BACKUP_STATE_SCHEMA_VERSION,
        "application_version": application_version,
        "created_at": created_at,
        "schema_fingerprint": schema_fingerprint,
        "components": list(_COMPONENTS),
        "excluded": list(_EXCLUDED),
        "contents": records,
        "table_counts": table_counts,
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", allowZip64=False) as archive:
        archive.writestr(_zip_info(_MANIFEST_MEMBER), _canonical_json(manifest))
        archive.writestr(_zip_info(_DATABASE_MEMBER), database)
        if pricing_override is not None:
            archive.writestr(_zip_info(_PRICING_MEMBER), pricing_override)
    payload = output.getvalue()
    if len(payload) > MAX_BACKUP_UNCOMPRESSED_BYTES:
        raise BackupArchiveError("Backup archive exceeds the supported size.")
    return payload, manifest


def _read_member(archive: zipfile.ZipFile, info: zipfile.ZipInfo, maximum: int) -> bytes:
    result = bytearray()
    with archive.open(info, "r") as stream:
        while True:
            chunk = stream.read(min(1024 * 1024, maximum + 1 - len(result)))
            if not chunk:
                break
            result.extend(chunk)
            if len(result) > maximum:
                raise BackupArchiveError(f"Backup member {info.filename!r} exceeds its size limit.")
    if len(result) != info.file_size:
        raise BackupArchiveError(f"Backup member {info.filename!r} size is inconsistent.")
    return bytes(result)


def _validate_manifest(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if set(manifest) != _MANIFEST_FIELDS:
        raise BackupArchiveError("Backup manifest fields are invalid.")
    if (
        manifest["format"] != BACKUP_ARCHIVE_FORMAT
        or type(manifest["archive_version"]) is not int
        or manifest["archive_version"] != BACKUP_ARCHIVE_VERSION
        or type(manifest["state_schema_version"]) is not int
        or manifest["state_schema_version"] != BACKUP_STATE_SCHEMA_VERSION
    ):
        raise BackupArchiveError("Backup archive version is unsupported.")
    application_version = manifest["application_version"]
    if type(application_version) is not str or not _SEMVER.fullmatch(application_version):
        raise BackupArchiveError("Backup application version is invalid.")
    try:
        created_at = datetime.fromisoformat(manifest["created_at"])
    except (TypeError, ValueError) as exc:
        raise BackupArchiveError("Backup creation timestamp is invalid.") from exc
    if created_at.tzinfo is None or created_at.astimezone(timezone.utc) > _utc_now() + timedelta(
        minutes=5
    ):
        raise BackupArchiveError("Backup creation timestamp is invalid.")
    if not isinstance(manifest["schema_fingerprint"], str) or not _SHA256.fullmatch(
        manifest["schema_fingerprint"]
    ):
        raise BackupArchiveError("Backup schema fingerprint is invalid.")
    if manifest["components"] != list(_COMPONENTS) or manifest["excluded"] != list(_EXCLUDED):
        raise BackupArchiveError("Backup component inventory is incompatible.")
    table_counts = manifest["table_counts"]
    if (
        not isinstance(table_counts, dict)
        or not _CORE_TABLES.issubset(table_counts)
        or any(
            type(key) is not str
            or not key
            or type(value) is not int
            or value < 0
            or value > 1_000_000_000
            for key, value in table_counts.items()
        )
    ):
        raise BackupArchiveError("Backup table inventory is invalid.")
    contents = manifest["contents"]
    if not isinstance(contents, list) or not 1 <= len(contents) <= 2:
        raise BackupArchiveError("Backup content inventory is invalid.")
    indexed: dict[str, dict[str, Any]] = {}
    for record in contents:
        if not isinstance(record, dict) or set(record) != _CONTENT_FIELDS:
            raise BackupArchiveError("Backup content record is invalid.")
        path = record["path"]
        if path not in {_DATABASE_MEMBER, _PRICING_MEMBER} or path in indexed:
            raise BackupArchiveError("Backup content path is invalid.")
        expected_media = (
            "application/vnd.sqlite3" if path == _DATABASE_MEMBER else "application/json"
        )
        if record["media_type"] != expected_media:
            raise BackupArchiveError("Backup content media type is invalid.")
        if (
            type(record["size_bytes"]) is not int
            or record["size_bytes"] <= 0
            or not isinstance(record["sha256"], str)
            or not _SHA256.fullmatch(record["sha256"])
        ):
            raise BackupArchiveError("Backup content metadata is invalid.")
        indexed[path] = record
    if _DATABASE_MEMBER not in indexed or list(indexed) != sorted(indexed):
        raise BackupArchiveError("Backup content inventory is invalid.")
    return indexed


def _validate_zip(payload: bytes, work_dir: Path) -> _ValidatedArchive:
    if not payload or len(payload) > MAX_BACKUP_UNCOMPRESSED_BYTES:
        raise BackupArchiveError("Backup archive size is invalid.")
    try:
        archive = zipfile.ZipFile(io.BytesIO(payload), "r")
    except (OSError, zipfile.BadZipFile) as exc:
        raise BackupArchiveError("Backup payload is not a valid ZIP archive.") from exc
    with archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if (
            len(entries) not in {2, 3}
            or len(names) != len(set(names))
            or not _REQUIRED_MEMBERS.issubset(names)
            or not set(names).issubset(_ALLOWED_MEMBERS)
        ):
            raise BackupArchiveError("Backup archive members are invalid.")
        total_size = 0
        by_name: dict[str, zipfile.ZipInfo] = {}
        for entry in entries:
            mode = (entry.external_attr >> 16) & 0o170000
            if (
                entry.is_dir()
                or entry.flag_bits & 0x1
                or mode == stat.S_IFLNK
                or entry.file_size < 0
                or entry.compress_size < 0
            ):
                raise BackupArchiveError("Backup archive contains an unsafe member.")
            maximum = {
                _MANIFEST_MEMBER: MAX_BACKUP_MANIFEST_BYTES,
                _DATABASE_MEMBER: MAX_BACKUP_DATABASE_BYTES,
                _PRICING_MEMBER: MAX_BACKUP_PRICING_BYTES,
            }[entry.filename]
            if entry.file_size <= 0 or entry.file_size > maximum:
                raise BackupArchiveError("Backup archive member size is invalid.")
            if entry.file_size > 1024 * 1024 and (
                entry.compress_size == 0
                or entry.file_size > entry.compress_size * MAX_BACKUP_COMPRESSION_RATIO
            ):
                raise BackupArchiveError("Backup archive compression ratio is unsafe.")
            total_size += entry.file_size
            by_name[entry.filename] = entry
        if total_size > MAX_BACKUP_UNCOMPRESSED_BYTES:
            raise BackupArchiveError("Backup archive expands beyond the supported size.")

        manifest_bytes = _read_member(
            archive,
            by_name[_MANIFEST_MEMBER],
            MAX_BACKUP_MANIFEST_BYTES,
        )
        manifest = _load_json_object(
            manifest_bytes,
            label="manifest",
            maximum=MAX_BACKUP_MANIFEST_BYTES,
        )
        inventory = _validate_manifest(manifest)
        if set(inventory) != set(names) - {_MANIFEST_MEMBER}:
            raise BackupArchiveError("Backup manifest does not match archive members.")

        database = _read_member(
            archive,
            by_name[_DATABASE_MEMBER],
            MAX_BACKUP_DATABASE_BYTES,
        )
        if (
            len(database) != inventory[_DATABASE_MEMBER]["size_bytes"]
            or _sha256(database) != inventory[_DATABASE_MEMBER]["sha256"]
        ):
            raise BackupArchiveError("Backup database hash does not match the manifest.")
        database_path = work_dir / "validated.db"
        database_path.write_bytes(database)
        os.chmod(database_path, 0o600)
        schema_fingerprint, table_counts = _inspect_database(database_path)
        if schema_fingerprint != manifest["schema_fingerprint"]:
            raise BackupArchiveError("Backup database schema hash does not match the manifest.")
        if table_counts != manifest["table_counts"]:
            raise BackupArchiveError("Backup database inventory does not match the manifest.")

        pricing_override = None
        if _PRICING_MEMBER in inventory:
            pricing_override = _read_member(
                archive,
                by_name[_PRICING_MEMBER],
                MAX_BACKUP_PRICING_BYTES,
            )
            if (
                len(pricing_override) != inventory[_PRICING_MEMBER]["size_bytes"]
                or _sha256(pricing_override) != inventory[_PRICING_MEMBER]["sha256"]
            ):
                raise BackupArchiveError("Backup pricing hash does not match the manifest.")
            _load_json_object(
                pricing_override,
                label="pricing override",
                maximum=MAX_BACKUP_PRICING_BYTES,
            )
        return _ValidatedArchive(manifest, database_path, pricing_override)


def _is_configured(database_path: Path) -> bool:
    with sqlite3.connect(_safe_database_uri(database_path), uri=True, timeout=30) as connection:
        credential_count = sum(
            int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
            for table in ("credentials", "primary_credentials")
        )
        configured = connection.execute(
            "SELECT COUNT(*) FROM config WHERE key NOT LIKE '_internal_%' "
            "AND key != 'setup_preflight_checkpoint'"
        ).fetchone()[0]
        oidc_users = connection.execute(
            "SELECT COUNT(*) FROM management_identities WHERE principal_type = 'oidc_user'"
        ).fetchone()[0]
        usage = connection.execute("SELECT COUNT(*) FROM durable_usage_ledger").fetchone()[0]
    return any(int(value) > 0 for value in (credential_count, configured, oidc_users, usage))


def _read_pricing_override(root: Path) -> bytes | None:
    path = root / "model_pricing.json"
    if not path.exists():
        return None
    if not path.is_file() or path.is_symlink() or path.resolve().parent != root:
        raise BackupArchiveError("Pricing override path is unsafe.")
    value = path.read_bytes()
    _load_json_object(value, label="pricing override", maximum=MAX_BACKUP_PRICING_BYTES)
    return value


class PortableBackupService:
    """Own the bounded SQLite backup lifecycle for one trusted data directory."""

    def __init__(
        self,
        database_path: str | Path,
        *,
        credentials_dir: str | Path,
        application_version: str | None = None,
        reload_callback: Callable[[], Awaitable[None]] | None = None,
    ) -> None:
        root = Path(credentials_dir).expanduser().resolve()
        database = Path(database_path).expanduser().resolve()
        if database.parent != root or database.name != "credentials.db":
            raise BackupBackendError("SQLite backup path is outside the configured data directory.")
        if database.is_symlink():
            raise BackupBackendError("SQLite backup path cannot be a symbolic link.")
        version = application_version or get_application_version()
        if not _SEMVER.fullmatch(version):
            raise BackupBackendError("Application version is invalid for portable backup.")
        self._root = root
        self._database = database
        self._application_version = version
        self._reload_callback = reload_callback

    async def _snapshot_database(self, destination: Path) -> None:
        await asyncio.to_thread(_sqlite_backup, self._database, destination)

    async def _create_from_snapshot(
        self,
        snapshot: Path,
        passphrase: str,
        *,
        created_at: str,
        pricing_override: bytes | None,
    ) -> BackupArtifact:
        payload, manifest = await asyncio.to_thread(
            _build_archive,
            snapshot,
            application_version=self._application_version,
            created_at=created_at,
            pricing_override=pricing_override,
        )
        try:
            encrypted = await asyncio.to_thread(encrypt_bytes, payload, passphrase)
        except BackupEnvelopeError as exc:
            raise BackupArchiveError(str(exc)) from exc
        if len(encrypted) > MAX_BACKUP_UPLOAD_BYTES:
            raise BackupArchiveError("Encrypted backup exceeds the portable upload limit.")
        stamp = created_at.replace("-", "").replace(":", "").replace("+00:00", "Z")
        return BackupArtifact(
            encrypted,
            f"omni-gateway-backup-{stamp}{BACKUP_EXTENSION}",
            created_at,
            manifest,
        )

    async def create_backup(self, passphrase: str) -> BackupArtifact:
        """Create a consistent encrypted snapshot without including raw log files."""

        async with _maintenance_lock:
            self._assert_live_database()
            with _work_directory(self._root, "backup-create") as work_dir:
                snapshot = work_dir / "snapshot.db"
                await self._snapshot_database(snapshot)
                return await self._create_from_snapshot(
                    snapshot,
                    passphrase,
                    created_at=_timestamp(),
                    pricing_override=await asyncio.to_thread(_read_pricing_override, self._root),
                )

    async def validate_restore(
        self,
        encrypted: bytes,
        passphrase: str,
        *,
        conflict_policy: RestoreConflictPolicy,
    ) -> RestorePlan:
        """Fully decrypt and validate an archive without changing durable state."""

        if type(conflict_policy) is not RestoreConflictPolicy:
            raise BackupArchiveError("Restore conflict policy is invalid.")
        async with _maintenance_lock:
            self._assert_live_database()
            with _work_directory(self._root, "backup-validate") as work_dir:
                validated = await self._decrypt_and_validate(encrypted, passphrase, work_dir)
                await self._assert_compatible(validated)
                if (
                    conflict_policy is RestoreConflictPolicy.ABORT_IF_CONFIGURED
                    and await asyncio.to_thread(_is_configured, self._database)
                ):
                    raise BackupConflictError(
                        "Restore was not applied because the current instance is configured."
                    )
                return self._plan(validated, conflict_policy)

    async def restore(
        self,
        encrypted: bytes,
        passphrase: str,
        *,
        conflict_policy: RestoreConflictPolicy,
    ) -> RestoreResult:
        """Validate, snapshot, and transactionally replace the live SQLite state."""

        if type(conflict_policy) is not RestoreConflictPolicy:
            raise BackupArchiveError("Restore conflict policy is invalid.")
        async with _maintenance_lock:
            self._assert_live_database()
            with _work_directory(self._root, "backup-restore") as work_dir:
                validated = await self._decrypt_and_validate(encrypted, passphrase, work_dir)
                await self._assert_compatible(validated)
                if (
                    conflict_policy is RestoreConflictPolicy.ABORT_IF_CONFIGURED
                    and await asyncio.to_thread(_is_configured, self._database)
                ):
                    raise BackupConflictError(
                        "Restore was not applied because the current instance is configured."
                    )

                previous_database = work_dir / "pre-restore.db"
                await self._snapshot_database(previous_database)
                previous_pricing = await asyncio.to_thread(_read_pricing_override, self._root)
                snapshot = await self._create_from_snapshot(
                    previous_database,
                    passphrase,
                    created_at=_timestamp(),
                    pricing_override=previous_pricing,
                )
                snapshot_id = await asyncio.to_thread(self._persist_snapshot, snapshot.content)

                try:
                    await asyncio.to_thread(
                        _sqlite_backup,
                        validated.database_path,
                        self._database,
                    )
                    await asyncio.to_thread(
                        self._replace_pricing_override,
                        validated.pricing_override,
                    )
                    await self._reload()
                except Exception as exc:
                    try:
                        await asyncio.to_thread(
                            _sqlite_backup,
                            previous_database,
                            self._database,
                        )
                        await asyncio.to_thread(
                            self._replace_pricing_override,
                            previous_pricing,
                        )
                        await self._reload()
                    except Exception as rollback_exc:
                        raise BackupRestoreError(
                            "Restore failed and the automatic rollback could not be completed."
                        ) from rollback_exc
                    raise BackupRestoreError(
                        "Restore failed; the previous state was restored from its snapshot."
                    ) from exc

                return RestoreResult(
                    restored=True,
                    pre_restore_snapshot_id=snapshot_id,
                    source_application_version=validated.manifest["application_version"],
                    restored_at=_timestamp(),
                    components=_COMPONENTS,
                )

    async def create_sanitized_export(self) -> bytes:
        """Return a non-restorable inventory that cannot authenticate any request."""

        async with _maintenance_lock:
            self._assert_live_database()
            with _work_directory(self._root, "backup-sanitize") as work_dir:
                snapshot = work_dir / "snapshot.db"
                await self._snapshot_database(snapshot)
                exported = await asyncio.to_thread(self._sanitized_inventory, snapshot)
                return _canonical_json(exported)

    async def _decrypt_and_validate(
        self,
        encrypted: bytes,
        passphrase: str,
        work_dir: Path,
    ) -> _ValidatedArchive:
        if (
            type(encrypted) is not bytes
            or not encrypted
            or len(encrypted) > min(MAX_BACKUP_UPLOAD_BYTES, MAX_BACKUP_ENVELOPE_BYTES)
        ):
            raise BackupArchiveError("Encrypted backup upload size is invalid.")
        try:
            payload = await asyncio.to_thread(decrypt_bytes, encrypted, passphrase)
        except BackupEnvelopeError as exc:
            raise BackupArchiveError(str(exc)) from exc
        return await asyncio.to_thread(_validate_zip, payload, work_dir)

    async def _assert_compatible(self, validated: _ValidatedArchive) -> None:
        live_schema, _ = await asyncio.to_thread(_inspect_database, self._database)
        if live_schema != validated.manifest["schema_fingerprint"]:
            raise BackupArchiveError(
                "Backup database schema is incompatible with this Omni Gateway instance."
            )

    def _plan(
        self,
        validated: _ValidatedArchive,
        policy: RestoreConflictPolicy,
    ) -> RestorePlan:
        manifest = validated.manifest
        return RestorePlan(
            compatible=True,
            archive_version=manifest["archive_version"],
            source_application_version=manifest["application_version"],
            created_at=manifest["created_at"],
            conflict_policy=policy.value,
            components=_COMPONENTS,
            excluded=_EXCLUDED,
            table_counts=dict(manifest["table_counts"]),
            pricing_override_included=validated.pricing_override is not None,
        )

    def _assert_live_database(self) -> None:
        if (
            not self._root.is_dir()
            or not self._database.is_file()
            or self._database.is_symlink()
            or self._database.resolve().parent != self._root
        ):
            raise BackupBackendError("The SQLite state path is unavailable or unsafe.")

    def _persist_snapshot(self, content: bytes) -> str:
        backup_dir = self._root / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        if os.name != "nt":
            os.chmod(backup_dir, 0o700)
        if backup_dir.is_symlink() or backup_dir.resolve().parent != self._root:
            raise BackupRestoreError("The pre-restore snapshot directory is unsafe.")
        identifier = f"pre-restore-{_utc_now().strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex}"
        final_path = backup_dir / f"{identifier}{BACKUP_EXTENSION}"
        temporary = backup_dir / f".{identifier}.tmp"
        try:
            with temporary.open("xb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temporary, 0o600)
            os.replace(temporary, final_path)
        finally:
            temporary.unlink(missing_ok=True)
        return identifier

    def _replace_pricing_override(self, content: bytes | None) -> None:
        path = self._root / "model_pricing.json"
        if path.exists() and (path.is_symlink() or path.resolve().parent != self._root):
            raise BackupRestoreError("Pricing override path is unsafe.")
        if content is None:
            path.unlink(missing_ok=True)
            return
        _load_json_object(content, label="pricing override", maximum=MAX_BACKUP_PRICING_BYTES)
        temporary = self._root / f".model-pricing-{uuid.uuid4().hex}.tmp"
        try:
            with temporary.open("xb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temporary, 0o600)
            os.replace(temporary, path)
        finally:
            temporary.unlink(missing_ok=True)

    async def _reload(self) -> None:
        if self._reload_callback is not None:
            await self._reload_callback()

    def _sanitized_inventory(self, database_path: Path) -> dict[str, Any]:
        safe_types = {
            ConfigValueType.BOOLEAN,
            ConfigValueType.INTEGER,
            ConfigValueType.NUMBER,
            ConfigValueType.INTEGER_LIST,
        }
        safe_fields = {
            field.config_key: field
            for field in CONFIGURATION_FIELDS
            if field.config_key and not field.secret
        }
        with sqlite3.connect(_safe_database_uri(database_path), uri=True) as connection:
            raw_config = {
                str(key): json.loads(value)
                for key, value in connection.execute("SELECT key, value FROM config").fetchall()
            }
            configuration: dict[str, Any] = {}
            for key, field in safe_fields.items():
                if key not in raw_config:
                    continue
                value = raw_config[key]
                if field.value_type in safe_types:
                    configuration[key] = value
                elif field.choices and type(value) is str and value in field.choices:
                    configuration[key] = value

            virtual_keys = raw_config.get("virtual_keys")
            key_records = virtual_keys if isinstance(virtual_keys, list) else []
            quality = raw_config.get("quality_policy_document")
            pool = raw_config.get("virtual_model_pool")
            blacklist = raw_config.get("model_route_blacklist")
            role_counts = {
                str(role): int(count)
                for role, count in connection.execute(
                    "SELECT role, COUNT(*) FROM management_role_bindings GROUP BY role"
                ).fetchall()
            }

            def count(table: str) -> int:
                return int(connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])

            return {
                "format": SANITIZED_EXPORT_FORMAT,
                "version": SANITIZED_EXPORT_VERSION,
                "application_version": self._application_version,
                "created_at": _timestamp(),
                "backend": "sqlite",
                "configuration": configuration,
                "credentials": {
                    "code_assist": count("credentials"),
                    "primary": count("primary_credentials"),
                },
                "routing": {
                    "virtual_pool_configured": isinstance(pool, dict),
                    "selected_model_count": (
                        len(pool.get("selected_models", []))
                        if isinstance(pool, dict) and isinstance(pool.get("selected_models"), list)
                        else 0
                    ),
                    "blacklist_entry_count": (
                        len(blacklist.get("entries", []))
                        if isinstance(blacklist, dict)
                        and isinstance(blacklist.get("entries"), list)
                        else 0
                    ),
                },
                "quality_policy": {
                    "configured": isinstance(quality, dict),
                    "profile": (
                        quality.get("profile")
                        if isinstance(quality, dict)
                        and quality.get("profile") in {"quality", "balanced", "capacity", "custom"}
                        else None
                    ),
                    "revision": (
                        quality.get("revision")
                        if isinstance(quality, dict) and type(quality.get("revision")) is int
                        else None
                    ),
                },
                "virtual_keys": {
                    "configured": len(key_records),
                    "enabled": sum(
                        1
                        for record in key_records
                        if isinstance(record, dict) and record.get("enabled") is True
                    ),
                },
                "identity": {
                    "identities": count("management_identities"),
                    "roles": role_counts,
                },
                "records": {
                    "audit_events": count("audit_events"),
                    "request_traces": count("request_traces"),
                    "usage_ledger": count("durable_usage_ledger"),
                },
                "excluded": [
                    "access_secrets",
                    "credential_payloads",
                    "raw_logs",
                    "restorable_key_material",
                ],
                "restorable": False,
            }
