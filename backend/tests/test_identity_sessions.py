import asyncio
import base64
import dataclasses
import re
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.identity import ManagementPrincipal
from core.identity.sessions import (
    InProcessSessionStore,
    SessionAuthenticationMethod,
    SessionExpired,
    SessionNotFound,
    SessionPolicy,
    SessionStale,
)


class InProcessSessionStoreTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.policy = SessionPolicy(idle_ttl_seconds=300, absolute_ttl_seconds=900)
        self.store = InProcessSessionStore(
            hmac_key=b"s" * 32,
            policy=self.policy,
        )
        self.owner = ManagementPrincipal.local_owner()

    async def _issue(self, *, now: float = 1_000.0, epoch: int = 7):
        return await self.store.issue(
            principal=self.owner,
            authentication_method=SessionAuthenticationMethod.LOCAL_PASSWORD,
            authorization_epoch=epoch,
            now=now,
        )

    async def test_issue_returns_256_bit_opaque_secret_but_stores_only_hmac_index(self):
        issued = await self._issue()

        self.assertRegex(issued.token, r"^ogs_[A-Za-z0-9_-]{43}$")
        raw = base64.urlsafe_b64decode(issued.token.removeprefix("ogs_") + "=")
        self.assertEqual(len(raw), 32)
        self.assertEqual(issued.session.principal, self.owner)
        self.assertEqual(issued.session.issued_at, 1_000.0)
        self.assertEqual(issued.session.last_seen_at, 1_000.0)
        self.assertEqual(issued.session.idle_expires_at, 1_300.0)
        self.assertEqual(issued.session.absolute_expires_at, 1_900.0)
        self.assertNotIn(issued.token, repr(self.store))
        self.assertNotIn(issued.token, repr(self.store._sessions))
        self.assertFalse(hasattr(issued.session, "token"))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            issued.session.authorization_epoch = 8

    async def test_resolve_slides_idle_expiry_without_extending_absolute_expiry(self):
        issued = await self._issue()

        resolved = await self.store.resolve(
            issued.token,
            current_authorization_epoch=7,
            now=1_250.0,
        )
        self.assertEqual(resolved.last_seen_at, 1_250.0)
        self.assertEqual(resolved.idle_expires_at, 1_550.0)
        self.assertEqual(resolved.absolute_expires_at, 1_900.0)

        await self.store.resolve(
            issued.token,
            current_authorization_epoch=7,
            now=1_500.0,
        )
        await self.store.resolve(
            issued.token,
            current_authorization_epoch=7,
            now=1_750.0,
        )
        resolved = await self.store.resolve(
            issued.token,
            current_authorization_epoch=7,
            now=1_850.0,
        )
        self.assertEqual(resolved.idle_expires_at, 1_900.0)

    async def test_idle_and_absolute_expiry_are_terminal(self):
        idle = await self._issue()
        absolute = await self._issue(now=2_000.0)

        with self.assertRaises(SessionExpired):
            await self.store.resolve(idle.token, current_authorization_epoch=7, now=1_300.0)
        with self.assertRaises(SessionNotFound):
            await self.store.resolve(idle.token, current_authorization_epoch=7, now=1_299.0)

        await self.store.resolve(
            absolute.token,
            current_authorization_epoch=7,
            now=2_250.0,
        )
        await self.store.resolve(
            absolute.token,
            current_authorization_epoch=7,
            now=2_500.0,
        )
        await self.store.resolve(
            absolute.token,
            current_authorization_epoch=7,
            now=2_750.0,
        )
        with self.assertRaises(SessionExpired):
            await self.store.resolve(
                absolute.token,
                current_authorization_epoch=7,
                now=2_900.0,
            )

    async def test_logout_revocation_and_authorization_epoch_change_block_replay(self):
        revoked = await self._issue()
        stale = await self._issue()

        self.assertTrue(await self.store.revoke(revoked.token))
        self.assertFalse(await self.store.revoke(revoked.token))
        with self.assertRaises(SessionNotFound):
            await self.store.resolve(
                revoked.token,
                current_authorization_epoch=7,
                now=1_001.0,
            )

        with self.assertRaises(SessionStale):
            await self.store.resolve(
                stale.token,
                current_authorization_epoch=8,
                now=1_001.0,
            )
        with self.assertRaises(SessionNotFound):
            await self.store.resolve(
                stale.token,
                current_authorization_epoch=7,
                now=1_001.0,
            )

    async def test_rotation_is_atomic_and_invalidates_the_old_secret(self):
        issued = await self._issue()

        rotated = await self.store.rotate(
            issued.token,
            principal=self.owner,
            authentication_method=SessionAuthenticationMethod.LOCAL_PASSWORD,
            authorization_epoch=8,
            now=1_100.0,
        )

        self.assertNotEqual(rotated.token, issued.token)
        self.assertEqual(rotated.session.authorization_epoch, 8)
        with self.assertRaises(SessionNotFound):
            await self.store.resolve(
                issued.token,
                current_authorization_epoch=7,
                now=1_101.0,
            )
        self.assertEqual(
            (
                await self.store.resolve(
                    rotated.token,
                    current_authorization_epoch=8,
                    now=1_101.0,
                )
            ).principal,
            self.owner,
        )

    async def test_only_one_concurrent_rotation_can_consume_a_session(self):
        issued = await self._issue()

        results = await asyncio.gather(
            *(
                self.store.rotate(
                    issued.token,
                    principal=self.owner,
                    authentication_method=SessionAuthenticationMethod.LOCAL_PASSWORD,
                    authorization_epoch=7,
                    now=1_010.0,
                )
                for _ in range(8)
            ),
            return_exceptions=True,
        )

        successes = [result for result in results if not isinstance(result, Exception)]
        failures = [result for result in results if isinstance(result, SessionNotFound)]
        self.assertEqual(len(successes), 1)
        self.assertEqual(len(failures), 7)

    async def test_principal_revocation_is_scoped_and_concurrency_safe(self):
        owner_sessions = [await self._issue(now=1_000.0 + index) for index in range(4)]
        other_owner = ManagementPrincipal.local_owner("secondary-local-owner")
        other = await self.store.issue(
            principal=other_owner,
            authentication_method=SessionAuthenticationMethod.LOCAL_PASSWORD,
            authorization_epoch=7,
            now=1_000.0,
        )

        counts = await asyncio.gather(*(self.store.revoke_principal(self.owner) for _ in range(4)))

        self.assertEqual(sum(counts), 4)
        for issued in owner_sessions:
            with self.assertRaises(SessionNotFound):
                await self.store.resolve(
                    issued.token,
                    current_authorization_epoch=7,
                    now=1_100.0,
                )
        self.assertEqual(
            (
                await self.store.resolve(
                    other.token,
                    current_authorization_epoch=7,
                    now=1_100.0,
                )
            ).principal,
            other_owner,
        )

    async def test_malformed_and_attacker_chosen_values_never_become_sessions(self):
        for token in ("", "chosen-by-attacker", "ogs_short", "x" * 10_000):
            with self.subTest(token=token[:20]):
                with self.assertRaises(SessionNotFound):
                    await self.store.resolve(
                        token,
                        current_authorization_epoch=7,
                        now=1_000.0,
                    )

        issued = await self._issue()
        self.assertTrue(re.fullmatch(r"ogs_[A-Za-z0-9_-]{43}", issued.token))


class SessionPolicyTests(unittest.TestCase):
    def test_policy_is_bounded_and_absolute_ttl_must_exceed_idle_ttl(self):
        self.assertEqual(
            SessionPolicy(idle_ttl_seconds=300, absolute_ttl_seconds=900).idle_ttl_seconds,
            300,
        )
        for values in (
            (299, 900),
            (300, 299),
            (900, 900),
            (300, 2_592_001),
            (True, 900),
        ):
            with self.subTest(values=values), self.assertRaises(ValueError):
                SessionPolicy(idle_ttl_seconds=values[0], absolute_ttl_seconds=values[1])


if __name__ == "__main__":
    unittest.main()
