import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import HTTPException

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.panel import auth_support


class LoginRateLimitTests(unittest.TestCase):
    def setUp(self):
        auth_support._login_failures.clear()

    def tearDown(self):
        auth_support._login_failures.clear()

    def test_expired_clients_are_pruned_without_creating_empty_entries(self):
        auth_support._login_failures["expired"] = [100.0]

        with patch("core.panel.auth_support.time.time", return_value=1000.0):
            self.assertEqual(auth_support._recent_failures("new-client"), [])

        self.assertEqual(auth_support._login_failures, {})

    def test_tracked_clients_are_bounded_by_evicting_the_oldest_entry(self):
        with (
            patch.object(auth_support, "LOGIN_MAX_TRACKED_CLIENTS", 2),
            patch("core.panel.auth_support.time.time", side_effect=[100.0, 101.0, 102.0]),
        ):
            auth_support._record_login_failure("oldest")
            auth_support._record_login_failure("newer")
            auth_support._record_login_failure("newest")

        self.assertNotIn("oldest", auth_support._login_failures)
        self.assertEqual(list(auth_support._login_failures), ["newer", "newest"])

    def test_recording_an_existing_client_preserves_all_recent_attempts(self):
        with patch("core.panel.auth_support.time.time", side_effect=[100.0, 101.0]):
            auth_support._record_login_failure("client")
            auth_support._record_login_failure("client")

        self.assertEqual(auth_support._login_failures["client"], [100.0, 101.0])


class OidcStartRateLimitTests(unittest.TestCase):
    def setUp(self):
        auth_support._oidc_starts.clear()

    def tearDown(self):
        auth_support._oidc_starts.clear()

    def test_start_attempts_are_bounded_before_transaction_allocation(self):
        with (
            patch.object(auth_support, "OIDC_START_MAX_ATTEMPTS", 3),
            patch("core.panel.auth_support.time.time", return_value=100.0),
        ):
            for _attempt in range(3):
                auth_support._assert_and_record_oidc_start("client")
            with self.assertRaises(HTTPException) as context:
                auth_support._assert_and_record_oidc_start("client")

        self.assertEqual(context.exception.status_code, 429)
        self.assertEqual(len(auth_support._oidc_starts["client"]), 3)

    def test_expired_and_excess_clients_are_pruned_or_evicted(self):
        auth_support._oidc_starts["expired"] = [1.0]
        with (
            patch.object(auth_support, "OIDC_START_MAX_TRACKED_CLIENTS", 2),
            patch("core.panel.auth_support.time.time", side_effect=[1_000.0, 1_001.0, 1_002.0]),
        ):
            auth_support._assert_and_record_oidc_start("oldest")
            auth_support._assert_and_record_oidc_start("newer")
            auth_support._assert_and_record_oidc_start("newest")

        self.assertNotIn("expired", auth_support._oidc_starts)
        self.assertNotIn("oldest", auth_support._oidc_starts)
        self.assertEqual(list(auth_support._oidc_starts), ["newer", "newest"])


if __name__ == "__main__":
    unittest.main()
