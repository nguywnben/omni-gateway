"""Provider OAuth flow state must never disclose a management session capability."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.auth import auth_flows, create_auth_url


class ProviderOAuthSessionIsolationTests(unittest.IsolatedAsyncioTestCase):
    def tearDown(self):
        auth_flows.clear()

    async def test_external_oauth_state_is_independent_from_internal_session_reference(self):
        flow = MagicMock()
        flow.get_auth_url.side_effect = lambda *, state: (
            f"https://issuer.example/auth?state={state}"
        )
        session_reference = "a" * 64

        with (
            patch(
                "core.auth.get_antigravity_oauth_client_config",
                new=AsyncMock(return_value=("client-id", "client-secret")),
            ),
            patch("core.auth.get_server_port", new=AsyncMock(return_value=4283)),
            patch("core.auth.Flow", return_value=flow),
        ):
            result = await create_auth_url(
                "project-1",
                session_reference,
                mode="primary",
            )

        self.assertTrue(result["success"])
        self.assertNotIn(session_reference, result["state"])
        self.assertNotIn(session_reference, result["auth_url"])
        self.assertEqual(auth_flows[result["state"]]["user_session"], session_reference)


if __name__ == "__main__":
    unittest.main()
