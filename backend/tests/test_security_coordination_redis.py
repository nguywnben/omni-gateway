"""Driver and semantic tests for Redis-backed identity security coordination."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.coordination import CoordinationCorruptError
from core.redis_state_store import SCRIPT_SOURCES, RedisStateStore
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
from tests.security_coordination_store_contract import SecurityCoordinationStoreContract
from tests.test_redis_state_store import (
    NOSCRIPT_THEN_RELOAD,
    FakeRedisClient,
    FakeRedisModule,
    StatefulRedisClient,
)


def _issued_reply(*, digest: bytes = b"a" * 64, reference: bytes = b"ssr_" + b"b" * 32):
    return [
        b"1",
        b"applied",
        b"",
        b"0",
        digest,
        reference,
        b"c" * 64,
        b"oidc_user",
        b"b3BhcXVl",
        b"1000000",
        b"1000000",
        b"1300000",
        b"1900000",
    ]


class StatefulSecurityRedisClient(StatefulRedisClient):
    """Deterministic Redis-script model used to exercise public session semantics."""

    _KEY_COUNTS = {
        **StatefulRedisClient._KEY_COUNTS,
        "security_session_issue": (10, 12),
        "security_session_resolve": (10, 6),
        "security_session_rotate": (10, 12),
        "security_session_revoke": (10, 7),
        "security_session_list": (10, 3),
        "security_attempt_reserve": (6, 8),
        "security_attempt_clear": (6, 6),
        "oidc_transaction_create": (6, 9),
        "oidc_transaction_consume": (6, 7),
    }

    def __init__(self) -> None:
        super().__init__()
        self.security_sessions: dict[bytes, dict[str, bytes]] = {}
        self.security_references: dict[bytes, bytes] = {}
        self.security_replays: dict[
            bytes, tuple[bytes, bytes, bytes, bytes, bytes, bytes, int]
        ] = {}
        self.security_attempts: dict[str, dict[bytes, tuple[int, int]]] = {}
        self.security_attempt_replays: dict[
            str, dict[bytes, tuple[bytes, bytes, bytes, bytes, bytes, int]]
        ] = {}
        self.oidc_transactions: dict[bytes, tuple[bytes, bytes, int]] = {}
        self.oidc_replays: dict[bytes, tuple[bytes, bytes, bytes, bytes, bytes, int]] = {}

    @staticmethod
    def _session_reply(
        status: bytes,
        reason: bytes = b"",
        idempotent: bool = False,
        digest: bytes = b"",
        session: dict[str, bytes] | None = None,
    ) -> list[bytes]:
        if session is None:
            return [b"1", status, reason, b"1" if idempotent else b"0"] + [b""] * 9
        return [
            b"1",
            status,
            reason,
            b"1" if idempotent else b"0",
            digest,
            session["reference"],
            session["principal"],
            session["principal_type"],
            session["payload"],
            session["issued"],
            session["last_seen"],
            session["idle_expiry"],
            session["absolute_expiry"],
        ]

    def _remove_session(self, digest: bytes) -> None:
        session = self.security_sessions.pop(digest)
        self.security_references.pop(session["reference"], None)

    def _security_cleanup(self) -> bool:
        due_sessions = [
            digest
            for digest, session in self.security_sessions.items()
            if min(int(session["idle_expiry"]), int(session["absolute_expiry"])) <= self.now_ms
        ]
        due_replays = [
            operation_id
            for operation_id, (*_evidence, expiry) in self.security_replays.items()
            if expiry <= self.now_ms
        ]
        if len(due_sessions) + len(due_replays) > 256:
            return False
        for digest in due_sessions:
            self._remove_session(digest)
        for operation_id in due_replays:
            del self.security_replays[operation_id]
        return True

    def _security_epoch_reason(self, epoch: bytes) -> bytes | None:
        if not self.epoch_exists or not self.initialization_exists:
            raise RuntimeError("COORDINATION_CORRUPT")
        if self.epoch == (int(epoch), b"ready"):
            return None
        return b"reconciling" if self.epoch[1] == b"reconciling" else b"stale_epoch"

    def _security_replay(
        self, operation_id: bytes, fingerprint: bytes
    ) -> tuple[bytes, bytes, bytes, bytes, bytes, int] | None:
        replay = self.security_replays.get(operation_id)
        if replay is None:
            return None
        saved_fingerprint, status, reason, digest, issued, absolute_expiry, expiry = replay
        if saved_fingerprint != fingerprint:
            return (b"conflict", b"", b"", b"", b"", expiry)
        return status, reason, digest, issued, absolute_expiry, expiry

    def _remember_security_replay(
        self,
        operation_id: bytes,
        fingerprint: bytes,
        status: bytes,
        reason: bytes,
        digest: bytes,
        issued: bytes,
        absolute_expiry: bytes,
        expiry: int,
        limit: int,
    ) -> bool:
        if operation_id not in self.security_replays and len(self.security_replays) >= limit:
            return False
        self.security_replays[operation_id] = (
            fingerprint,
            status,
            reason,
            digest,
            issued,
            absolute_expiry,
            expiry,
        )
        return True

    @staticmethod
    def _cleanup_mapping(mapping: dict[bytes, tuple], now_ms: int) -> list[bytes]:
        return [key for key, value in mapping.items() if int(value[-1]) <= now_ms]

    def _run_attempt_script(self, name: str, keys: list[str], values: list[bytes]) -> list[bytes]:
        reason = self._security_epoch_reason(values[0])
        if reason is not None:
            if name == "security_attempt_clear":
                raise RuntimeError("COORDINATION_UNAVAILABLE")
            return [b"1", b"denied", reason, b"0", b"0", b"0"]
        scope = keys[2]
        records = self.security_attempts.setdefault(scope, {})
        replays = self.security_attempt_replays.setdefault(scope, {})
        due = self._cleanup_mapping(records, self.now_ms)
        replay_due = self._cleanup_mapping(replays, self.now_ms)
        if len(due) + len(replay_due) > 256:
            if name == "security_attempt_clear":
                return [b"1", b"reconciliation_required", b"0", b"0"]
            return [b"1", b"denied", b"reconciliation_required", b"0", b"0", b"0"]
        for key in due:
            del records[key]
        for key in replay_due:
            del replays[key]

        if name == "security_attempt_reserve":
            _epoch, client, limit, window, operation, fingerprint, record_limit, replay_limit = (
                values
            )
            replay = replays.get(operation)
            if replay is not None:
                saved_fingerprint, status, replay_reason, remaining, retry_after, _expiry = replay
                if saved_fingerprint != fingerprint:
                    return [
                        b"1",
                        b"denied",
                        b"reconciliation_required",
                        b"0",
                        b"0",
                        b"0",
                    ]
                return [b"1", status, replay_reason, b"1", remaining, retry_after]
            if len(replays) >= int(replay_limit):
                return [b"1", b"denied", b"reconciliation_required", b"0", b"0", b"0"]
            record = records.get(client)
            expiry = self.now_ms + int(window) if record is None else record[1]
            if record is None and len(records) >= int(record_limit):
                status, denial, remaining, retry_after = b"denied", b"capacity", b"0", b"0"
            elif record is not None and record[0] >= int(limit):
                status, denial, remaining = b"denied", b"limited", b"0"
                retry_after = str(max(1, (expiry - self.now_ms + 999) // 1000)).encode()
            else:
                count = 1 if record is None else record[0] + 1
                status, denial = b"allowed", b""
                remaining = str(max(0, int(limit) - count)).encode()
                retry_after = b"0"
                records[client] = (count, expiry)
            replays[operation] = (
                fingerprint,
                status,
                denial,
                remaining,
                retry_after,
                expiry,
            )
            return [b"1", status, denial, b"0", remaining, retry_after]

        _epoch, client, replay_ttl, operation, fingerprint, replay_limit = values
        replay = replays.get(operation)
        if replay is not None:
            saved_fingerprint, _status, _reason, cleared, _retry, _expiry = replay
            if saved_fingerprint != fingerprint:
                raise RuntimeError("COORDINATION_UNAVAILABLE")
            return [b"1", b"ok", cleared, b"1"]
        if len(replays) >= int(replay_limit):
            return [b"1", b"reconciliation_required", b"0", b"0"]
        record = records.get(client)
        cleared = b"1" if record is not None else b"0"
        expiry = record[1] if record is not None else self.now_ms + int(replay_ttl)
        replays[operation] = (fingerprint, b"cleared", b"", cleared, b"0", expiry)
        records.pop(client, None)
        return [b"1", b"ok", cleared, b"0"]

    def _run_oidc_script(self, name: str, values: list[bytes]) -> list[bytes]:
        reason = self._security_epoch_reason(values[0])
        if reason is not None:
            return [b"1", b"denied", reason, b"0"] + (
                [b""] if name == "oidc_transaction_consume" else []
            )
        original = self.oidc_transactions.get(values[1])
        was_expired = original is not None and original[2] <= self.now_ms
        due = self._cleanup_mapping(self.oidc_transactions, self.now_ms)
        replay_due = self._cleanup_mapping(self.oidc_replays, self.now_ms)
        if len(due) + len(replay_due) > 256:
            return [b"1", b"denied", b"reconciliation_required", b"0"] + (
                [b""] if name == "oidc_transaction_consume" else []
            )
        for key in due:
            del self.oidc_transactions[key]
        for key in replay_due:
            del self.oidc_replays[key]

        if name == "oidc_transaction_create":
            _epoch, state, browser, payload, ttl, operation, fingerprint, limit, replay_limit = (
                values
            )
            replay = self.oidc_replays.get(operation)
            if replay is not None:
                saved_fingerprint, status, replay_reason, replay_state, replay_browser, expiry = (
                    replay
                )
                if saved_fingerprint != fingerprint:
                    return [b"1", b"denied", b"conflict", b"0"]
                transaction = self.oidc_transactions.get(state)
                if status == b"applied" and transaction != (browser, payload, expiry):
                    return [b"1", b"denied", b"conflict", b"0"]
                return [b"1", status, replay_reason, b"1"]
            if len(self.oidc_replays) >= int(replay_limit):
                return [b"1", b"denied", b"reconciliation_required", b"0"]
            expiry = self.now_ms + int(ttl)
            denial = (
                b"conflict"
                if state in self.oidc_transactions
                else b"capacity"
                if len(self.oidc_transactions) >= int(limit)
                else b""
            )
            status = b"denied" if denial else b"applied"
            self.oidc_replays[operation] = (
                fingerprint,
                status,
                denial,
                state if not denial else b"",
                browser if not denial else b"",
                expiry,
            )
            if not denial:
                self.oidc_transactions[state] = (browser, payload, expiry)
            return [b"1", status, denial, b"0"]

        _epoch, state, browser, fallback_ttl, operation, fingerprint, replay_limit = values
        replay = self.oidc_replays.get(operation)
        if replay is not None:
            saved_fingerprint, status, replay_reason, _state, _browser, _expiry = replay
            if saved_fingerprint != fingerprint:
                return [b"1", b"denied", b"reconciliation_required", b"0", b""]
            if status == b"consumed":
                return [b"1", b"denied", b"not_found", b"1", b""]
            return [b"1", b"denied", replay_reason, b"1", b""]
        if len(self.oidc_replays) >= int(replay_limit):
            return [b"1", b"denied", b"reconciliation_required", b"0", b""]
        transaction = self.oidc_transactions.get(state)
        if transaction is None:
            status, denial, payload = b"denied", b"expired" if was_expired else b"not_found", b""
            expiry = self.now_ms + int(fallback_ttl)
        elif transaction[0] != browser:
            status, denial, payload, expiry = b"denied", b"browser_mismatch", b"", transaction[2]
        else:
            status, denial, payload, expiry = b"consumed", b"", transaction[1], transaction[2]
        self.oidc_replays[operation] = (fingerprint, status, denial, state, browser, expiry)
        if status == b"consumed":
            del self.oidc_transactions[state]
        return [b"1", status, denial, b"0", payload]

    def run_script(self, name: str, keys: list[str], args: list[object]) -> list[bytes]:
        if not name.startswith(("security_session_", "security_attempt_", "oidc_transaction_")):
            return super().run_script(name, keys, args)
        key_count, arg_count = self._KEY_COUNTS[name]
        assert len(keys) == key_count and len(args) == arg_count
        assert len({key[key.index("{") + 1 : key.index("}")] for key in keys}) == 1
        assert all(isinstance(arg, bytes) for arg in args)
        values = [arg for arg in args if isinstance(arg, bytes)]

        if name.startswith("security_attempt_"):
            return self._run_attempt_script(name, keys, values)
        if name.startswith("oidc_transaction_"):
            return self._run_oidc_script(name, values)

        reason = self._security_epoch_reason(values[0])
        if reason is not None:
            if name in {"security_session_revoke", "security_session_list"}:
                raise RuntimeError("COORDINATION_UNAVAILABLE")
            return self._session_reply(b"denied", reason)
        expired_digest = None
        if name == "security_session_resolve":
            existing = self.security_sessions.get(values[1])
            if (
                existing is not None
                and min(int(existing["idle_expiry"]), int(existing["absolute_expiry"]))
                <= self.now_ms
            ):
                expired_digest = values[1]
        if not self._security_cleanup():
            if name == "security_session_revoke":
                return [b"1", b"reconciliation_required", b"0", b"0"]
            if name == "security_session_list":
                raise RuntimeError("COORDINATION_RECONCILIATION_REQUIRED")
            return self._session_reply(b"denied", b"reconciliation_required")

        if name == "security_session_issue":
            (
                _epoch,
                digest,
                reference,
                principal,
                principal_type,
                payload,
                idle_ttl,
                absolute_ttl,
                operation_id,
                fingerprint,
                session_limit,
                replay_limit,
            ) = values
            replay = self._security_replay(operation_id, fingerprint)
            if replay is not None:
                status, replay_reason, replay_digest, issued, absolute_expiry, _expiry = replay
                if status == b"conflict":
                    return self._session_reply(b"denied", b"conflict")
                if status != b"applied":
                    return self._session_reply(b"denied", replay_reason, True)
                session = self.security_sessions.get(replay_digest)
                stable = session is not None and (
                    replay_digest,
                    session["reference"],
                    session["principal"],
                    session["principal_type"],
                    session["payload"],
                    session["issued"],
                    session["absolute_expiry"],
                ) == (
                    digest,
                    reference,
                    principal,
                    principal_type,
                    payload,
                    issued,
                    absolute_expiry,
                )
                return (
                    self._session_reply(b"applied", idempotent=True, digest=digest, session=session)
                    if stable
                    else self._session_reply(b"denied", b"conflict")
                )
            absolute_expiry = self.now_ms + int(absolute_ttl)
            denial = (
                b"conflict"
                if digest in self.security_sessions or reference in self.security_references
                else b"capacity"
                if len(self.security_sessions) >= int(session_limit)
                else b""
            )
            status = b"denied" if denial else b"applied"
            if not self._remember_security_replay(
                operation_id,
                fingerprint,
                status,
                denial,
                digest if not denial else b"",
                str(self.now_ms).encode() if not denial else b"0",
                str(absolute_expiry).encode() if not denial else b"0",
                absolute_expiry,
                int(replay_limit),
            ):
                return self._session_reply(b"denied", b"reconciliation_required")
            if denial:
                return self._session_reply(b"denied", denial)
            timestamp = str(self.now_ms).encode()
            session = {
                "reference": reference,
                "principal": principal,
                "principal_type": principal_type,
                "payload": payload,
                "issued": timestamp,
                "last_seen": timestamp,
                "idle_expiry": str(self.now_ms + int(idle_ttl)).encode(),
                "absolute_expiry": str(absolute_expiry).encode(),
            }
            self.security_sessions[digest] = session
            self.security_references[reference] = digest
            return self._session_reply(b"applied", digest=digest, session=session)

        if name == "security_session_resolve":
            _epoch, digest, idle_ttl, operation_id, fingerprint, replay_limit = values
            replay = self._security_replay(operation_id, fingerprint)
            if replay is not None:
                status, replay_reason, replay_digest, issued, _absolute, _expiry = replay
                if status == b"conflict":
                    return self._session_reply(b"denied", b"reconciliation_required")
                if status != b"resolved":
                    return self._session_reply(b"denied", replay_reason, True)
                session = self.security_sessions.get(replay_digest)
                return (
                    self._session_reply(
                        b"resolved", idempotent=True, digest=digest, session=session
                    )
                    if session is not None and session["issued"] == issued
                    else self._session_reply(b"denied", b"not_found", True)
                )
            session = self.security_sessions.get(digest)
            if session is None:
                denial = b"expired" if expired_digest == digest else b"not_found"
                expiry = self.now_ms + int(idle_ttl)
                if not self._remember_security_replay(
                    operation_id,
                    fingerprint,
                    b"denied",
                    denial,
                    digest,
                    b"0",
                    b"0",
                    expiry,
                    int(replay_limit),
                ):
                    return self._session_reply(b"denied", b"reconciliation_required")
                return self._session_reply(b"denied", denial)
            idle_expiry = min(self.now_ms + int(idle_ttl), int(session["absolute_expiry"]))
            touched = dict(session)
            touched["last_seen"] = str(self.now_ms).encode()
            touched["idle_expiry"] = str(idle_expiry).encode()
            if not self._remember_security_replay(
                operation_id,
                fingerprint,
                b"resolved",
                b"",
                digest,
                touched["issued"],
                touched["absolute_expiry"],
                idle_expiry,
                int(replay_limit),
            ):
                return self._session_reply(b"denied", b"reconciliation_required")
            self.security_sessions[digest] = touched
            return self._session_reply(b"resolved", digest=digest, session=touched)

        if name == "security_session_rotate":
            (
                _epoch,
                current_digest,
                digest,
                reference,
                principal,
                principal_type,
                payload,
                idle_ttl,
                absolute_ttl,
                operation_id,
                fingerprint,
                replay_limit,
            ) = values
            replay = self._security_replay(operation_id, fingerprint)
            if replay is not None:
                status, replay_reason, replay_digest, issued, absolute_expiry, _expiry = replay
                if status == b"conflict":
                    return self._session_reply(b"denied", b"conflict")
                if status != b"applied":
                    return self._session_reply(b"denied", replay_reason, True)
                session = self.security_sessions.get(replay_digest)
                stable = (
                    session is not None
                    and session["issued"] == issued
                    and session["absolute_expiry"] == absolute_expiry
                )
                return (
                    self._session_reply(b"applied", idempotent=True, digest=digest, session=session)
                    if stable
                    else self._session_reply(b"denied", b"not_found")
                )
            denial = (
                b"not_found"
                if current_digest not in self.security_sessions
                else b"conflict"
                if digest in self.security_sessions
                or (
                    reference in self.security_references
                    and self.security_references[reference] != current_digest
                )
                else b""
            )
            absolute_expiry = self.now_ms + int(absolute_ttl)
            timestamp = str(self.now_ms).encode()
            if not self._remember_security_replay(
                operation_id,
                fingerprint,
                b"denied" if denial else b"applied",
                denial,
                digest if not denial else b"",
                timestamp if not denial else b"0",
                str(absolute_expiry).encode() if not denial else b"0",
                absolute_expiry,
                int(replay_limit),
            ):
                return self._session_reply(b"denied", b"reconciliation_required")
            if denial:
                return self._session_reply(b"denied", denial)
            self._remove_session(current_digest)
            session = {
                "reference": reference,
                "principal": principal,
                "principal_type": principal_type,
                "payload": payload,
                "issued": timestamp,
                "last_seen": timestamp,
                "idle_expiry": str(self.now_ms + int(idle_ttl)).encode(),
                "absolute_expiry": str(absolute_expiry).encode(),
            }
            self.security_sessions[digest] = session
            self.security_references[reference] = digest
            return self._session_reply(b"applied", digest=digest, session=session)

        if name == "security_session_revoke":
            _epoch, target, target_value, replay_ttl, operation_id, fingerprint, replay_limit = (
                values
            )
            replay = self._security_replay(operation_id, fingerprint)
            if replay is not None:
                status, _reason, count, _issued, _absolute, _expiry = replay
                if status == b"conflict":
                    raise RuntimeError("COORDINATION_UNAVAILABLE")
                return [b"1", b"ok", count, b"1"]
            if target == b"digest":
                digests = [target_value] if target_value in self.security_sessions else []
            elif target == b"reference":
                digest = self.security_references.get(target_value)
                digests = [] if digest is None else [digest]
            elif target == b"principal":
                digests = [
                    digest
                    for digest, session in self.security_sessions.items()
                    if session["principal"] == target_value
                ]
            else:
                digests = [
                    digest
                    for digest, session in self.security_sessions.items()
                    if session["principal_type"] == target_value
                ]
            if len(digests) > 256:
                return [b"1", b"reconciliation_required", b"0", b"0"]
            count = str(len(digests)).encode()
            if not self._remember_security_replay(
                operation_id,
                fingerprint,
                b"revoked",
                b"",
                count,
                b"0",
                b"0",
                self.now_ms + int(replay_ttl),
                int(replay_limit),
            ):
                return [b"1", b"reconciliation_required", b"0", b"0"]
            for digest in digests:
                self._remove_session(digest)
            return [b"1", b"ok", count, b"0"]

        _epoch, limit, after_reference = values
        references = sorted(
            reference
            for reference in self.security_references
            if not after_reference or reference >= after_reference
        )
        page_references = references[: int(limit)]
        next_reference = references[int(limit)] if len(references) > int(limit) else b""
        reply = [b"1", b"ok", next_reference, str(len(page_references)).encode()]
        for reference in page_references:
            digest = self.security_references[reference]
            reply.extend(
                self._session_reply(
                    b"applied", digest=digest, session=self.security_sessions[digest]
                )[4:]
            )
        return reply


class RedisSecurityCoordinationDriverTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.client = FakeRedisClient()
        self.store = RedisStateStore(
            "redis://user:secret@example.invalid:6379/0",
            deployment_namespace="security-test",
            _security_session_limit_for_testing=2,
            _security_replay_limit_for_testing=3,
            _redis_module_for_testing=FakeRedisModule(self.client),
        )

    @staticmethod
    def _issue(suffix: str = "abc", operation_id: str = "issue-session") -> SessionIssueRequest:
        return SessionIssueRequest(
            session_digest=suffix[0] * 64,
            session_reference=f"ssr_{suffix[1] * 32}",
            principal_index=suffix[2] * 64,
            principal_type=SecurityPrincipalType.OIDC_USER,
            payload=b"opaque",
            idle_ttl_seconds=300,
            absolute_ttl_seconds=900,
            fencing_epoch=1,
            operation_id=operation_id,
        )

    async def test_session_methods_use_fixed_explicit_cluster_safe_scripts(self) -> None:
        issue = self._issue()
        self.client.script_replies["security_session_issue"].append(_issued_reply())
        issued = await self.store.issue_security_session(issue)
        self.assertTrue(issued.applied)
        self.assertEqual(issued.session.payload, b"opaque")

        name, keys, args = self.client.script_calls[-1]
        self.assertEqual(name, "security_session_issue")
        self.assertEqual((len(keys), len(args)), (10, 12))
        self.assertEqual(args[0:5], [b"1", b"a" * 64, b"ssr_" + b"b" * 32, b"c" * 64, b"oidc_user"])
        tags = {key[key.index("{") + 1 : key.index("}")] for key in keys}
        self.assertEqual(len(tags), 1)
        self.assertNotIn("secret", repr(keys) + repr(args))

        self.client.script_replies["security_session_resolve"].append(
            [b"1", b"denied", b"not_found", b"0"] + [b""] * 9
        )
        resolved = await self.store.resolve_security_session(
            SessionResolveRequest(issue.session_digest, 300, 1, "resolve-session")
        )
        self.assertEqual((resolved.resolved, resolved.reason), (False, "not_found"))

        replacement = self._issue("def", "rotate-session")
        self.client.script_replies["security_session_rotate"].append(
            _issued_reply(digest=b"d" * 64, reference=b"ssr_" + b"e" * 32)
        )
        rotated = await self.store.rotate_security_session(
            SessionRotateRequest(issue.session_digest, replacement, 1, "rotate-session")
        )
        self.assertTrue(rotated.applied)

        self.client.script_replies["security_session_revoke"].append([b"1", b"ok", b"1", b"0"])
        revoked = await self.store.revoke_security_sessions(
            SessionRevokeRequest(
                SessionRevokeTarget.REFERENCE,
                replacement.session_reference,
                1,
                "revoke-session",
            )
        )
        self.assertEqual(revoked.revoked_count, 1)

        self.client.script_replies["security_session_list"].append(
            [b"1", b"ok", b"", b"1"]
            + _issued_reply(digest=b"d" * 64, reference=b"ssr_" + b"e" * 32)[4:]
        )
        page = await self.store.list_security_sessions(SessionListRequest(10, 1))
        self.assertEqual(
            [item.session_reference for item in page.sessions], [replacement.session_reference]
        )

    async def test_session_script_reload_and_closed_reply_decoding(self) -> None:
        self.client.script_replies["security_session_issue"].extend(
            [NOSCRIPT_THEN_RELOAD, _issued_reply()]
        )
        self.assertTrue((await self.store.issue_security_session(self._issue())).applied)
        self.assertEqual(self.client.script_loads, 1)

        for reply in (
            [b"1", b"applied", b"", b"2"] + [b""] * 9,
            [b"1", b"denied", b"unknown", b"0"] + [b""] * 9,
            _issued_reply()[:-1],
            _issued_reply(digest=b"not-a-digest"),
        ):
            client = FakeRedisClient()
            client.script_replies["security_session_issue"].append(reply)
            store = RedisStateStore(
                "redis://example.invalid/0",
                _redis_module_for_testing=FakeRedisModule(client),
            )
            with self.assertRaises(CoordinationCorruptError):
                await store.issue_security_session(self._issue())

    async def test_attempt_and_oidc_methods_use_fixed_explicit_scripts(self) -> None:
        self.client.script_replies["security_attempt_reserve"].append(
            [b"1", b"allowed", b"", b"0", b"1", b"0"]
        )
        decision = await self.store.reserve_security_attempt(
            AttemptReservationRequest(
                SecurityAttemptCategory.LOGIN,
                "a" * 64,
                2,
                300,
                1,
                "reserve-login",
            )
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(self.client.script_calls[-1][0], "security_attempt_reserve")
        self.assertEqual(
            (len(self.client.script_calls[-1][1]), len(self.client.script_calls[-1][2])),
            (6, 8),
        )

        self.client.script_replies["security_attempt_clear"].append([b"1", b"ok", b"1", b"0"])
        cleared = await self.store.clear_security_attempts(
            AttemptClearRequest(
                SecurityAttemptCategory.LOGIN,
                "a" * 64,
                1,
                "clear-login",
            )
        )
        self.assertTrue(cleared.cleared)

        self.client.script_replies["oidc_transaction_create"].append([b"1", b"applied", b"", b"0"])
        created = await self.store.create_oidc_transaction(
            OidcTransactionCreateRequest(
                "b" * 64,
                "c" * 64,
                b"opaque-proof",
                300,
                1,
                "create-proof",
            )
        )
        self.assertTrue(created.applied)

        self.client.script_replies["oidc_transaction_consume"].append(
            [b"1", b"consumed", b"", b"0", b"b3BhcXVlLXByb29m"]
        )
        consumed = await self.store.consume_oidc_transaction(
            OidcTransactionConsumeRequest(
                "b" * 64,
                "c" * 64,
                1,
                "consume-proof",
            )
        )
        self.assertEqual(consumed.payload, b"opaque-proof")

        for name, key_count, arg_count in (
            ("security_attempt_clear", 6, 6),
            ("oidc_transaction_create", 6, 9),
            ("oidc_transaction_consume", 6, 7),
        ):
            call = next(call for call in self.client.script_calls if call[0] == name)
            self.assertEqual((len(call[1]), len(call[2])), (key_count, arg_count))
            self.assertEqual(
                len({key[key.index("{") + 1 : key.index("}")] for key in call[1]}),
                1,
            )

    async def test_attempt_and_oidc_reply_decoders_fail_closed(self) -> None:
        cases = (
            (
                "security_attempt_reserve",
                [b"1", b"allowed", b"limited", b"0", b"0", b"0"],
                lambda store: store.reserve_security_attempt(
                    AttemptReservationRequest(
                        SecurityAttemptCategory.LOGIN,
                        "a" * 64,
                        2,
                        300,
                        1,
                        "bad-reserve",
                    )
                ),
            ),
            (
                "oidc_transaction_consume",
                [b"1", b"consumed", b"", b"0", b"%%%"],
                lambda store: store.consume_oidc_transaction(
                    OidcTransactionConsumeRequest(
                        "b" * 64,
                        "c" * 64,
                        1,
                        "bad-consume",
                    )
                ),
            ),
        )
        for name, reply, operation in cases:
            with self.subTest(name=name):
                client = FakeRedisClient()
                client.script_replies[name].append(reply)
                store = RedisStateStore(
                    "redis://example.invalid/0",
                    _redis_module_for_testing=FakeRedisModule(client),
                )
                with self.assertRaises(CoordinationCorruptError):
                    await operation(store)

    def test_session_lua_is_fixed_bounded_and_cluster_safe(self) -> None:
        expected = {
            "security_session_issue",
            "security_session_resolve",
            "security_session_rotate",
            "security_session_revoke",
            "security_session_list",
            "security_attempt_reserve",
            "security_attempt_clear",
            "oidc_transaction_create",
            "oidc_transaction_consume",
        }
        self.assertTrue(expected.issubset(SCRIPT_SOURCES))
        for name in expected:
            source = SCRIPT_SOURCES[name]
            self.assertTrue(source.startswith(f"-- omni:{name}:v1"))
            self.assertIn("redis.call('TIME')", source)
            self.assertNotIn("redis.call('KEYS'", source)
            self.assertNotIn("redis.call('SCAN'", source)
            self.assertNotIn("while ", source)
            self.assertIn("LIMIT', 0, 257", source)
            marker = source.index("-- apply validated mutation")
            if name != "security_session_list":
                self.assertLess(source.index("local replay_value"), marker)


class RedisSecurityCoordinationStatefulTests(
    SecurityCoordinationStoreContract,
    unittest.IsolatedAsyncioTestCase,
):
    """Run the shared session contract against the Redis script boundary model."""

    def setUp(self) -> None:
        self.client = StatefulSecurityRedisClient()
        self.store = RedisStateStore(
            "redis://example.invalid/0",
            deployment_namespace="security-stateful",
            _redis_module_for_testing=FakeRedisModule(self.client),
        )
        self.advance_clock = lambda seconds: self.client.advance(round(seconds * 1000))

    async def test_shared_session_lifecycle_contract(self) -> None:
        await self.assert_session_lifecycle_contract()

    async def test_shared_attempt_and_oidc_transaction_contract(self) -> None:
        await self.assert_attempt_and_oidc_transaction_contract()

    async def test_atomic_attempt_and_consume_contract(self) -> None:
        await self.assert_atomic_attempt_and_consume_contract()

    async def test_exact_ready_epoch_contract(self) -> None:
        await self.assert_exact_ready_epoch_contract()

    async def test_capacity_preserves_live_evidence_contract(self) -> None:
        client = StatefulSecurityRedisClient()
        limited_store = RedisStateStore(
            "redis://example.invalid/0",
            deployment_namespace="security-capacity",
            _security_session_limit_for_testing=1,
            _security_attempt_limit_for_testing=1,
            _oidc_transaction_limit_for_testing=1,
            _redis_module_for_testing=FakeRedisModule(client),
        )
        await self.assert_capacity_preserves_live_evidence_contract(limited_store)

    async def test_security_operations_fail_after_close(self) -> None:
        await self.assert_security_operations_fail_after_close()


if __name__ == "__main__":
    unittest.main()
