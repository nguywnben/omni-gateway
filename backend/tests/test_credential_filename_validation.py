"""Credential filename validation contracts shared by management routes."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel.utils import validate_credential_filename
from fastapi import HTTPException


class CredentialFilenameValidationTests(unittest.TestCase):
    def test_canonical_filename_is_preserved(self):
        filename = "google-antigravity-a1b2c3d4e5f67890.json"

        self.assertEqual(validate_credential_filename(filename), filename)

    def test_unsafe_or_ambiguous_filenames_are_rejected(self):
        invalid_filenames = [
            "../credential.json",
            "folder/credential.json",
            "folder\\credential.json",
            "credential.json\nforged-log-entry",
            "credential.txt",
            "x" * 251 + ".json",
        ]

        for filename in invalid_filenames:
            with self.subTest(filename=filename):
                with self.assertRaises(HTTPException) as context:
                    validate_credential_filename(filename)
                self.assertEqual(context.exception.status_code, 400)
                self.assertEqual(context.exception.detail, "Invalid credential file name.")


if __name__ == "__main__":
    unittest.main()
