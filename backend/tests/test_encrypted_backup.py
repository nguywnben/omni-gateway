"""Tests for Encrypted Backup and Restore Module."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.encrypted_backup import decrypt_payload, encrypt_payload


class EncryptedBackupTests(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip(self) -> None:
        sample_data = {
            "credentials": [{"filename": "acc1.json", "provider": "openai_codex"}],
            "virtual_models": {"gpt-test": ["acc1.json"]},
            "settings": {"routing_policy": "smart"},
        }
        password = "strong-master-password-123!"

        bundle = encrypt_payload(sample_data, password)
        self.assertIn("salt", bundle)
        self.assertIn("nonce", bundle)
        self.assertIn("ciphertext", bundle)

        restored = decrypt_payload(bundle, password)
        self.assertEqual(restored, sample_data)

    def test_decrypt_with_wrong_password_fails(self) -> None:
        sample_data = {"secret": "api-key-123"}
        bundle = encrypt_payload(sample_data, "correct-password")

        with self.assertRaises(Exception):
            decrypt_payload(bundle, "wrong-password")


if __name__ == "__main__":
    unittest.main()
