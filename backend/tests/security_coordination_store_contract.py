"""Reusable W4.16 semantics for every identity-security coordination backend."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from core.coordination import CoordinationUnavailableError
from core.security_coordination import (
    AttemptClearRequest,
    AttemptReservationRequest,
    OidcTransactionConsumeRequest,
    OidcTransactionCreateRequest,
    SecurityAttemptCategory,
    SecurityPrincipalType,
    SessionIssueRequest,
    SessionListRequest,
    SessionResolveRequest,
    SessionRevokeRequest,
    SessionRevokeTarget,
    SessionRotateRequest,
)

if TYPE_CHECKING:
    from core.security_coordination import IdentitySecurityCoordinationStore


class SecurityCoordinationStoreContract:
    """Behavioral fixture mixed into in-memory, stateful Redis, and live Redis tests."""

    store: IdentitySecurityCoordinationStore
    advance_clock: Callable[[float], None]

    @staticmethod
    def _issue(
        suffix: str,
        *,
        operation_id: str | None = None,
    ) -> SessionIssueRequest:
        return SessionIssueRequest(
            session_digest=(suffix[0] * 64),
            session_reference=f"ssr_{suffix[1] * 32}",
            principal_index=(suffix[2] * 64),
            principal_type=SecurityPrincipalType.OIDC_USER,
            payload=f"payload-{suffix}".encode("ascii"),
            idle_ttl_seconds=300,
            absolute_ttl_seconds=900,
            fencing_epoch=1,
            operation_id=operation_id or f"issue-{suffix}",
        )

    async def assert_session_lifecycle_contract(self) -> None:
        first = self._issue("abc")
        issued = await self.store.issue_security_session(first)
        replayed = await self.store.issue_security_session(first)
        self.assertTrue(issued.applied)
        self.assertIsNotNone(issued.session)
        self.assertTrue(replayed.idempotent)

        resolved = await self.store.resolve_security_session(
            SessionResolveRequest(first.session_digest, 300, 1, "resolve-abc")
        )
        self.assertTrue(resolved.resolved)
        self.assertEqual(resolved.session.payload, first.payload)

        replacement = self._issue("def", operation_id="rotate-abc")
        rotated = await self.store.rotate_security_session(
            SessionRotateRequest(
                current_session_digest=first.session_digest,
                replacement=replacement,
                fencing_epoch=1,
                operation_id="rotate-abc",
            )
        )
        self.assertTrue(rotated.applied)
        missing = await self.store.resolve_security_session(
            SessionResolveRequest(first.session_digest, 300, 1, "resolve-old")
        )
        self.assertEqual((missing.resolved, missing.reason), (False, "not_found"))

        page = await self.store.list_security_sessions(
            SessionListRequest(limit=10, fencing_epoch=1)
        )
        self.assertEqual(
            [item.session_reference for item in page.sessions], [replacement.session_reference]
        )
        revoked = await self.store.revoke_security_sessions(
            SessionRevokeRequest(
                target=SessionRevokeTarget.REFERENCE,
                target_value=replacement.session_reference,
                fencing_epoch=1,
                operation_id="revoke-def",
            )
        )
        self.assertEqual(revoked.revoked_count, 1)

    async def assert_attempt_and_oidc_transaction_contract(self) -> None:
        request = AttemptReservationRequest(
            category=SecurityAttemptCategory.LOGIN,
            client_index="a" * 64,
            limit=2,
            window_seconds=300,
            fencing_epoch=1,
            operation_id="attempt-1",
        )
        first = await self.store.reserve_security_attempt(request)
        replayed = await self.store.reserve_security_attempt(request)
        second = await self.store.reserve_security_attempt(
            AttemptReservationRequest(
                category=SecurityAttemptCategory.LOGIN,
                client_index="a" * 64,
                limit=2,
                window_seconds=300,
                fencing_epoch=1,
                operation_id="attempt-2",
            )
        )
        denied = await self.store.reserve_security_attempt(
            AttemptReservationRequest(
                category=SecurityAttemptCategory.LOGIN,
                client_index="a" * 64,
                limit=2,
                window_seconds=300,
                fencing_epoch=1,
                operation_id="attempt-3",
            )
        )
        self.assertEqual((first.allowed, replayed.idempotent, second.allowed), (True, True, True))
        self.assertEqual((denied.allowed, denied.reason), (False, "limited"))
        await self.store.clear_security_attempts(
            AttemptClearRequest(
                category=SecurityAttemptCategory.LOGIN,
                client_index="a" * 64,
                fencing_epoch=1,
                operation_id="clear-attempts",
            )
        )

        create = OidcTransactionCreateRequest(
            state_index="b" * 64,
            browser_index="c" * 64,
            payload=b"opaque-transaction",
            ttl_seconds=300,
            fencing_epoch=1,
            operation_id="oidc-create",
        )
        self.assertTrue((await self.store.create_oidc_transaction(create)).applied)
        mismatch = await self.store.consume_oidc_transaction(
            OidcTransactionConsumeRequest(
                state_index="b" * 64,
                browser_index="d" * 64,
                fencing_epoch=1,
                operation_id="oidc-wrong-browser",
            )
        )
        consumed = await self.store.consume_oidc_transaction(
            OidcTransactionConsumeRequest(
                state_index="b" * 64,
                browser_index="c" * 64,
                fencing_epoch=1,
                operation_id="oidc-consume",
            )
        )
        self.assertEqual((mismatch.consumed, mismatch.reason), (False, "browser_mismatch"))
        self.assertEqual((consumed.consumed, consumed.payload), (True, b"opaque-transaction"))

    async def assert_security_operations_fail_after_close(self) -> None:
        await self.store.close()
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.issue_security_session(self._issue("abc"))
