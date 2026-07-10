"""Tests for control-panel password storage and verification."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.passwords import hash_password, is_password_hash, verify_password_value


class PasswordSecurityTests(unittest.TestCase):
    def test_scrypt_hash_round_trip(self):
        encoded = hash_password("correct horse battery staple")

        self.assertTrue(is_password_hash(encoded))
        self.assertNotIn("correct horse battery staple", encoded)
        self.assertTrue(
            verify_password_value("correct horse battery staple", encoded)
        )
        self.assertFalse(verify_password_value("incorrect password", encoded))

    def test_plaintext_legacy_values_remain_verifiable_for_migration(self):
        self.assertTrue(verify_password_value("legacy-password", "legacy-password"))
        self.assertFalse(verify_password_value("incorrect", "legacy-password"))

    def test_malformed_hash_is_rejected(self):
        self.assertFalse(verify_password_value("password", "scrypt$invalid"))
