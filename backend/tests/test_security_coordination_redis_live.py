"""Opt-in real-Redis evidence for W4.16 identity-security coordination."""

from __future__ import annotations

import asyncio
import os
import sys
import unittest
import uuid
from pathlib import Path
from typing import Any

import redis.asyncio as redis_asyncio

BACKEND_DIR = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

from core.coordination import validate_deployment_namespace
from core.redis_state_store import RedisStateStore
from core.security_coordination import (
    SessionResolveRequest,
    SessionRevokeRequest,
    SessionRevokeTarget,
)
from security_coordination_store_contract import SecurityCoordinationStoreContract
from test_coordination_redis_live import (
    _close_setup_resources,
    _teardown_live_resources,
)

REDIS_URI = os.getenv("OMNI_TEST_REDIS_URI", "").strip()
_CONNECT_TIMEOUT_SECONDS = 5.0


def _namespace() -> str:
    return validate_deployment_namespace(f"w416-security-live-{uuid.uuid4().hex}")


@unittest.skipUnless(REDIS_URI, "OMNI_TEST_REDIS_URI is not configured")
class LiveRedisSecurityCoordinationTests(
    SecurityCoordinationStoreContract,
    unittest.IsolatedAsyncioTestCase,
):
    """Execute the security scripts; a configured but unavailable endpoint is a failure."""

    async def asyncSetUp(self) -> None:
        self.store: RedisStateStore | None = None
        self.cleanup_client: Any | None = None
        try:
            self.namespace = _namespace()
            self.store = RedisStateStore(
                REDIS_URI,
                deployment_namespace=self.namespace,
                _security_session_limit_for_testing=8,
                _security_attempt_limit_for_testing=8,
                _oidc_transaction_limit_for_testing=8,
            )
            self.cleanup_client = redis_asyncio.from_url(
                REDIS_URI,
                decode_responses=False,
            )
            await asyncio.wait_for(
                self.store.initialize_epoch(),
                timeout=_CONNECT_TIMEOUT_SECONDS,
            )
        except BaseException as exc:
            await _close_setup_resources(self.store, self.cleanup_client)
            if isinstance(exc, asyncio.CancelledError):
                raise
            raise RuntimeError(
                "OMNI_TEST_REDIS_URI is configured but security coordination is unavailable."
            ) from None

    async def asyncTearDown(self) -> None:
        assert self.store is not None
        assert self.cleanup_client is not None
        pattern = f"{self.store._prefix}:*"
        await _teardown_live_resources(self.store, self.cleanup_client, pattern)

    async def test_attempt_and_oidc_shared_contract(self) -> None:
        assert self.store is not None
        await self.assert_attempt_and_oidc_transaction_contract()

    async def test_atomic_attempt_and_one_winner_consume_contract(self) -> None:
        assert self.store is not None
        await self.assert_atomic_attempt_and_consume_contract()

    async def test_exact_ready_epoch_contract(self) -> None:
        assert self.store is not None
        await self.assert_exact_ready_epoch_contract()

    async def test_session_state_is_visible_and_revocable_across_clients(self) -> None:
        assert self.store is not None
        issued = self._issue("abc")
        self.assertTrue((await self.store.issue_security_session(issued)).applied)
        second = RedisStateStore(REDIS_URI, deployment_namespace=self.namespace)
        try:
            self.assertTrue(
                (
                    await second.resolve_security_session(
                        SessionResolveRequest(
                            issued.session_digest,
                            300,
                            1,
                            "live-cross-resolve",
                        )
                    )
                ).resolved
            )
            revoked = await second.revoke_security_sessions(
                SessionRevokeRequest(
                    SessionRevokeTarget.REFERENCE,
                    issued.session_reference,
                    1,
                    "live-cross-revoke",
                )
            )
            self.assertEqual(revoked.revoked_count, 1)
            missing = await self.store.resolve_security_session(
                SessionResolveRequest(
                    issued.session_digest,
                    300,
                    1,
                    "live-cross-missing",
                )
            )
            self.assertEqual(missing.reason, "not_found")
        finally:
            await second.close()


if __name__ == "__main__":
    unittest.main()
