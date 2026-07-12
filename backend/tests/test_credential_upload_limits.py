"""Security and validation contracts for provider credential uploads."""

from __future__ import annotations

import io
import sys
import unittest
import zipfile
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.credential_operations import (
    extract_json_files_from_zip,
    upload_credentials_common,
)
from core.pool_import import MAX_POOL_ARCHIVE_BYTES, MAX_POOL_ENTRY_BYTES
from fastapi import HTTPException, UploadFile


def _zip_upload(entries: dict[str, bytes], filename: str = "credentials.zip") -> UploadFile:
    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for entry_name, content in entries.items():
            archive.writestr(entry_name, content)
    return UploadFile(filename=filename, file=io.BytesIO(archive_buffer.getvalue()))


class CredentialUploadLimitTests(unittest.IsolatedAsyncioTestCase):
    async def test_valid_nested_json_entry_uses_its_safe_basename(self):
        upload = _zip_upload({"nested/account.json": b'{"project_id":"project"}'})

        result = await extract_json_files_from_zip(upload)

        self.assertEqual(
            result, [{"filename": "account.json", "content": '{"project_id":"project"}'}]
        )

    async def test_zip_without_json_returns_a_client_error(self):
        upload = _zip_upload({"notes.txt": b"not a credential"})

        with self.assertRaises(HTTPException) as context:
            await extract_json_files_from_zip(upload)

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.detail, "No JSON files were found in the ZIP archive.")

    async def test_oversized_zip_is_rejected_before_parsing(self):
        upload = UploadFile(
            filename="credentials.zip",
            file=io.BytesIO(b"x" * (MAX_POOL_ARCHIVE_BYTES + 1)),
        )

        with self.assertRaises(HTTPException) as context:
            await extract_json_files_from_zip(upload)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("10 MB", context.exception.detail)

    async def test_oversized_zip_entry_is_rejected(self):
        upload = _zip_upload({"credential.json": b"x" * (MAX_POOL_ENTRY_BYTES + 1)})

        with self.assertRaises(HTTPException) as context:
            await extract_json_files_from_zip(upload)

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("2 MB", context.exception.detail)

    async def test_oversized_direct_json_is_rejected(self):
        upload = UploadFile(
            filename="credential.json",
            file=io.BytesIO(b"x" * (MAX_POOL_ENTRY_BYTES + 1)),
        )

        with self.assertRaises(HTTPException) as context:
            await upload_credentials_common([upload], mode="provider")

        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("2 MB", context.exception.detail)


if __name__ == "__main__":
    unittest.main()
