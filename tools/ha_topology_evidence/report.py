"""Atomic, sanitized evidence artifact writer and secret scanner."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Final, Iterable

from .contract import (
    CandidateTopology,
    EvidenceVerificationError,
    RunManifest,
    _read_bounded_regular_file,
    canonical_bytes,
    verify_run_manifest,
    write_atomic_manifest,
)

MAX_ARTIFACT_BYTES: Final = 64 * 1024 * 1024
_SECRET_PATTERNS: Final = (
    re.compile(
        rb"(?i)[\"']?(authorization|api[_-]?key|password|secret|token)[\"']?"
        rb"\s*[:=]\s*[\"']?[^,\s\"']{8,}"
    ),
    re.compile(rb"(?i)(postgres(?:ql)?|redis|mongodb)://[^\s/:]+:[^\s/@]+@"),
    re.compile(rb"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
)


def scan_secret_free(payload: bytes) -> None:
    if not isinstance(payload, bytes) or len(payload) > MAX_ARTIFACT_BYTES:
        raise EvidenceVerificationError("Evidence artifact is invalid or oversized.")
    if any(pattern.search(payload) for pattern in _SECRET_PATTERNS):
        raise EvidenceVerificationError("Evidence artifact contains prohibited secret material.")


def artifact_inventory(root: Path, names: Iterable[str]) -> tuple[tuple[str, str], ...]:
    resolved = root.resolve(strict=True)
    inventory: list[tuple[str, str]] = []
    for name in sorted(set(names)):
        unresolved = resolved / name
        if unresolved.is_symlink():
            raise EvidenceVerificationError("Evidence artifact symlinks are prohibited.")
        path = unresolved.resolve(strict=True)
        if (path.parent != resolved and resolved not in path.parents) or not path.is_file():
            raise EvidenceVerificationError("Evidence artifact escapes the run directory.")
        payload = _read_bounded_regular_file(path, MAX_ARTIFACT_BYTES)
        scan_secret_free(payload)
        inventory.append((name, hashlib.sha256(payload).hexdigest()))
    return tuple(inventory)


class EvidenceReportWriter:
    def __init__(self, root: Path) -> None:
        if root.exists() or not root.is_absolute():
            raise EvidenceVerificationError("Evidence output must be a new absolute directory.")
        root.mkdir(parents=False)
        self.root = root.resolve(strict=True)
        self._closed = False

    def write_json(self, name: str, value: object) -> str:
        if self._closed or "/" in name or "\\" in name or not name.endswith(".json"):
            raise EvidenceVerificationError("Evidence artifact name is invalid.")
        path = self.root / name
        payload = canonical_bytes(value) + b"\n"
        scan_secret_free(payload)
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        return hashlib.sha256(payload).hexdigest()

    def write_jsonl(self, name: str, records: Iterable[object]) -> str:
        if self._closed or "/" in name or "\\" in name or not name.endswith(".jsonl"):
            raise EvidenceVerificationError("Evidence artifact name is invalid.")
        chunks: list[bytes] = []
        size = 0
        for count, record in enumerate(records, start=1):
            if count > 100_000:
                raise EvidenceVerificationError("Evidence JSONL record limit is exceeded.")
            chunk = canonical_bytes(record) + b"\n"
            size += len(chunk)
            if size > MAX_ARTIFACT_BYTES:
                raise EvidenceVerificationError("Evidence JSONL artifact is oversized.")
            chunks.append(chunk)
        payload = b"".join(chunks)
        scan_secret_free(payload)
        path = self.root / name
        with path.open("xb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        return hashlib.sha256(payload).hexdigest()

    def complete(self, manifest: RunManifest, candidate: CandidateTopology) -> Path:
        if self._closed:
            raise EvidenceVerificationError("Evidence report is already complete.")
        expected = dict(manifest.artifacts)
        actual = dict(artifact_inventory(self.root, expected))
        if actual != expected:
            raise EvidenceVerificationError("Manifest artifact inventory does not match output.")
        # Reject before publishing the atomic completion marker. A rejected report must
        # remain visibly incomplete rather than leave behind a manifest that looks final.
        scan_secret_free(canonical_bytes(manifest.to_dict()) + b"\n")
        verify_run_manifest(manifest, candidate, self.root)
        path = self.root / "manifest.json"
        write_atomic_manifest(path, manifest)
        self._closed = True
        return path


def load_jsonl(path: Path, *, limit: int = 100_000) -> tuple[object, ...]:
    if type(limit) is not int or not 1 <= limit <= 100_000:
        raise EvidenceVerificationError("JSONL record limit is invalid.")
    payload = _read_bounded_regular_file(path, MAX_ARTIFACT_BYTES)
    scan_secret_free(payload)
    lines = payload.splitlines()
    if len(lines) > limit:
        raise EvidenceVerificationError("JSONL record limit is exceeded.")
    try:
        return tuple(
            json.loads(
                line,
                parse_constant=lambda value: (_ for _ in ()).throw(
                    EvidenceVerificationError(f"Invalid JSON number: {value}.")
                ),
            )
            for line in lines
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceVerificationError("Evidence JSONL is invalid or interrupted.") from exc
