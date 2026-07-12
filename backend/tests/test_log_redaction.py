"""Sensitive values must be redacted before logs leave the process."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from log import redact_text


class LogRedactionTests(unittest.TestCase):
    def test_redacts_database_uri_password(self):
        output = redact_text("Connection failed: postgresql://user:secret@database:5432/app")

        self.assertEqual(
            output,
            "Connection failed: postgresql://user:<redacted>@database:5432/app",
        )

    def test_redacts_bare_assignments_and_query_parameters(self):
        output = redact_text(
            "client_secret='secret-value' callback=https://example.test/?token=session-value&ok=1"
        )

        self.assertNotIn("secret-value", output)
        self.assertNotIn("session-value", output)
        self.assertIn("client_secret='<redacted>", output)
        self.assertIn("token=<redacted>&ok=1", output)

    def test_redacts_provider_tokens_without_field_names(self):
        output = redact_text(
            "Tokens: ya29.access-token 1//refresh-token "
            "sk-provider-secret-1234567890 AIzaSyExampleApiKey1234567890123"
        )

        self.assertNotIn("access-token", output)
        self.assertNotIn("refresh-token", output)
        self.assertNotIn("provider-secret", output)
        self.assertNotIn("ExampleApiKey", output)


if __name__ == "__main__":
    unittest.main()
