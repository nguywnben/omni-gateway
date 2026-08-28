"""Bounded, one-time OIDC authorization transactions for standalone mode."""

from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import math
import re
import secrets
import time
from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from core.identity.oidc_discovery import OidcDiscoveryDocument
from core.identity.oidc_http import OidcHttpError, validate_oidc_endpoint_url
from core.identity.oidc_policy import OidcPolicy

_HMAC_DOMAIN = b"omni-gateway:oidc-transaction:v1\0"
_MAX_AUTHORIZATION_URL_LENGTH = 8_192
_TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]{43}$")
_TOKEN_AUTH_METHODS = frozenset({"client_secret_basic", "client_secret_post"})
_RESERVED_AUTHORIZATION_PARAMETERS = frozenset(
    {
        "client_id",
        "code_challenge",
        "code_challenge_method",
        "nonce",
        "redirect_uri",
        "response_type",
        "scope",
        "state",
    }
)


class OidcAuthorizationTransactionError(RuntimeError):
    """Content-free boundary for unavailable or invalid OIDC transactions."""

    def __init__(self) -> None:
        super().__init__("OIDC authorization transaction failed.")


@dataclass(frozen=True, slots=True)
class OidcAuthorizationRequest:
    """Browser redirect material; callers must never log or persist this object."""

    authorization_url: str
    browser_token: str
    expires_in_seconds: int

    def __repr__(self) -> str:
        return (
            "OidcAuthorizationRequest(authorization_url='<redacted>', "
            "browser_token='<redacted>', "
            f"expires_in_seconds={self.expires_in_seconds!r})"
        )


@dataclass(frozen=True, slots=True)
class OidcTransactionProof:
    """Consumed transaction proof for the immediate token-exchange boundary."""

    issuer: str
    client_id: str
    redirect_uri: str
    authorization_endpoint: str
    token_endpoint: str
    token_endpoint_auth_method: str
    code_verifier: str
    nonce: str
    policy_revision: int

    def __repr__(self) -> str:
        return (
            "OidcTransactionProof("
            f"issuer={self.issuer!r}, client_id={self.client_id!r}, "
            f"redirect_uri={self.redirect_uri!r}, "
            f"authorization_endpoint={self.authorization_endpoint!r}, "
            f"token_endpoint={self.token_endpoint!r}, "
            f"token_endpoint_auth_method={self.token_endpoint_auth_method!r}, "
            "code_verifier='<redacted>', nonce='<redacted>', "
            f"policy_revision={self.policy_revision!r})"
        )


@dataclass(frozen=True, slots=True)
class _TransactionRecord:
    state_digest: str
    browser_digest: str
    issuer: str
    client_id: str
    redirect_uri: str
    authorization_endpoint: str
    token_endpoint: str
    token_endpoint_auth_method: str
    policy_revision: int
    created_at: float
    expires_at: float


def _token(value: object) -> str:
    if type(value) is not str or not _TOKEN_PATTERN.fullmatch(value):
        raise OidcAuthorizationTransactionError
    return value


def _clock_value(clock: Callable[[], float]) -> float:
    try:
        value = float(clock())
    except (TypeError, ValueError) as exc:
        raise OidcAuthorizationTransactionError from exc
    if not math.isfinite(value) or value < 0:
        raise OidcAuthorizationTransactionError
    return value


def _digest(key: bytes, label: bytes, value: str) -> str:
    return hmac.digest(
        key,
        _HMAC_DOMAIN + label + b"\0" + value.encode("ascii"),
        hashlib.sha256,
    ).hex()


def _derived_token(key: bytes, label: bytes, state: str) -> str:
    value = hmac.digest(
        key,
        _HMAC_DOMAIN + label + b"\0" + state.encode("ascii"),
        hashlib.sha256,
    )
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _authorization_url(
    policy: OidcPolicy,
    discovery: OidcDiscoveryDocument,
    *,
    state: str,
    nonce: str,
    code_challenge: str,
) -> str:
    try:
        parsed = urlsplit(discovery.authorization_endpoint)
        existing = parse_qsl(
            parsed.query,
            keep_blank_values=True,
            strict_parsing=True,
            max_num_fields=32,
        )
    except (TypeError, ValueError) as exc:
        raise OidcAuthorizationTransactionError from exc
    names = [name.lower() for name, _value in existing]
    if (
        len(names) != len(set(names))
        or any(name in _RESERVED_AUTHORIZATION_PARAMETERS for name in names)
        or policy.client_id is None
        or policy.redirect_uri is None
    ):
        raise OidcAuthorizationTransactionError
    parameters = existing + [
        ("response_type", "code"),
        ("client_id", policy.client_id),
        ("redirect_uri", policy.redirect_uri),
        ("scope", " ".join(policy.scopes)),
        ("state", state),
        ("nonce", nonce),
        ("code_challenge", code_challenge),
        ("code_challenge_method", "S256"),
    ]
    result = urlunsplit(parsed._replace(query=urlencode(parameters)))
    if len(result) > _MAX_AUTHORIZATION_URL_LENGTH:
        raise OidcAuthorizationTransactionError
    return result


class OidcAuthorizationTransactionService:
    """Atomic in-process transaction store that retains only keyed digests."""

    __slots__ = (
        "_clock",
        "_discovery",
        "_hmac_key",
        "_lock",
        "_max_pending",
        "_policy",
        "_token_factory",
        "_transactions",
        "_ttl_seconds",
    )

    def __init__(
        self,
        policy: OidcPolicy,
        discovery: OidcDiscoveryDocument,
        *,
        hmac_key: bytes,
        clock: Callable[[], float] = time.monotonic,
        token_factory: Callable[[int], str] = secrets.token_urlsafe,
        ttl_seconds: int = 300,
        max_pending: int = 1_000,
    ) -> None:
        """Create a standalone store.

        ``token_factory`` is a deterministic test seam; production callers must keep the default
        cryptographic generator, which returns 32 random bytes as canonical base64url text.
        """
        try:
            if (
                type(policy) is not OidcPolicy
                or not policy.enabled
                or policy.issuer is None
                or policy.client_id is None
                or policy.redirect_uri is None
                or type(discovery) is not OidcDiscoveryDocument
                or discovery.issuer != policy.issuer
                or "code" not in discovery.response_types
                or discovery.code_challenge_methods != ("S256",)
                or not discovery.token_endpoint_auth_methods
                or any(
                    method not in _TOKEN_AUTH_METHODS
                    for method in discovery.token_endpoint_auth_methods
                )
                or type(hmac_key) is not bytes
                or len(hmac_key) < 32
                or not callable(clock)
                or not callable(token_factory)
                or type(ttl_seconds) is not int
                or not 60 <= ttl_seconds <= 900
                or type(max_pending) is not int
                or not 1 <= max_pending <= 10_000
            ):
                raise OidcAuthorizationTransactionError
            validate_oidc_endpoint_url(policy, discovery.authorization_endpoint)
            validate_oidc_endpoint_url(policy, discovery.token_endpoint)
            _authorization_url(
                policy,
                discovery,
                state="A" * 43,
                nonce="B" * 43,
                code_challenge="C" * 43,
            )
        except (OidcAuthorizationTransactionError, OidcHttpError):
            raise OidcAuthorizationTransactionError from None
        self._policy = policy
        self._discovery = discovery
        self._hmac_key = hmac_key
        self._clock = clock
        self._token_factory = token_factory
        self._ttl_seconds = ttl_seconds
        self._max_pending = max_pending
        self._transactions: dict[str, _TransactionRecord] = {}
        self._lock = asyncio.Lock()

    def __repr__(self) -> str:
        return (
            "OidcAuthorizationTransactionService("
            f"policy_revision={self._policy.revision!r}, "
            f"issuer={self._policy.issuer!r}, pending={len(self._transactions)!r}, "
            f"ttl_seconds={self._ttl_seconds!r}, max_pending={self._max_pending!r})"
        )

    def matches_configuration(
        self,
        policy: OidcPolicy,
        discovery: OidcDiscoveryDocument,
    ) -> bool:
        """Return whether callers may reuse this service for the current trust snapshot.

        A false result requires replacing the service and dropping its pending transactions before
        accepting another begin or callback operation.
        """
        return self._policy == policy and self._discovery == discovery

    def _prune(self, now: float) -> None:
        expired = [
            digest for digest, record in self._transactions.items() if now >= record.expires_at
        ]
        for digest in expired:
            self._transactions.pop(digest, None)

    async def begin(self) -> OidcAuthorizationRequest:
        """Create one transaction and return browser-only redirect material."""
        try:
            now = _clock_value(self._clock)
            async with self._lock:
                self._prune(now)
                if len(self._transactions) >= self._max_pending:
                    raise OidcAuthorizationTransactionError
                state = _token(self._token_factory(32))
                browser_token = _token(self._token_factory(32))
                state_digest = _digest(self._hmac_key, b"state", state)
                if state_digest in self._transactions:
                    raise OidcAuthorizationTransactionError
                nonce = _derived_token(self._hmac_key, b"nonce", state)
                verifier = _derived_token(self._hmac_key, b"verifier", state)
                challenge = (
                    base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
                    .rstrip(b"=")
                    .decode("ascii")
                )
                expires_at = now + self._ttl_seconds
                authorization_url = _authorization_url(
                    self._policy,
                    self._discovery,
                    state=state,
                    nonce=nonce,
                    code_challenge=challenge,
                )
                record = _TransactionRecord(
                    state_digest=state_digest,
                    browser_digest=_digest(
                        self._hmac_key,
                        b"browser",
                        browser_token,
                    ),
                    issuer=self._policy.issuer,
                    client_id=self._policy.client_id,
                    redirect_uri=self._policy.redirect_uri,
                    authorization_endpoint=self._discovery.authorization_endpoint,
                    token_endpoint=self._discovery.token_endpoint,
                    token_endpoint_auth_method=self._discovery.token_endpoint_auth_methods[0],
                    policy_revision=self._policy.revision,
                    created_at=now,
                    expires_at=expires_at,
                )
                self._transactions[state_digest] = record
            return OidcAuthorizationRequest(
                authorization_url=authorization_url,
                browser_token=browser_token,
                expires_in_seconds=self._ttl_seconds,
            )
        except asyncio.CancelledError:
            raise
        except OidcAuthorizationTransactionError:
            raise OidcAuthorizationTransactionError from None
        except Exception:
            raise OidcAuthorizationTransactionError from None

    async def consume(
        self,
        *,
        state: str,
        browser_token: str,
        response_issuer: str | None = None,
    ) -> OidcTransactionProof:
        """Consume one browser-bound transaction; pass the response issuer whenever supplied."""
        try:
            state = _token(state)
            browser_token = _token(browser_token)
            if response_issuer is not None and (
                type(response_issuer) is not str
                or not response_issuer
                or len(response_issuer) > 2_048
                or response_issuer != response_issuer.strip()
                or any(
                    ord(character) < 0x20 or ord(character) > 0x7E for character in response_issuer
                )
            ):
                raise OidcAuthorizationTransactionError
            now = _clock_value(self._clock)
            state_digest = _digest(self._hmac_key, b"state", state)
            browser_digest = _digest(self._hmac_key, b"browser", browser_token)
            async with self._lock:
                self._prune(now)
                record = self._transactions.get(state_digest)
                if record is None or not hmac.compare_digest(
                    record.browser_digest,
                    browser_digest,
                ):
                    raise OidcAuthorizationTransactionError
                self._transactions.pop(state_digest, None)
            if response_issuer is not None and not hmac.compare_digest(
                response_issuer.encode("ascii"),
                record.issuer.encode("ascii"),
            ):
                raise OidcAuthorizationTransactionError
            return OidcTransactionProof(
                issuer=record.issuer,
                client_id=record.client_id,
                redirect_uri=record.redirect_uri,
                authorization_endpoint=record.authorization_endpoint,
                token_endpoint=record.token_endpoint,
                token_endpoint_auth_method=record.token_endpoint_auth_method,
                code_verifier=_derived_token(self._hmac_key, b"verifier", state),
                nonce=_derived_token(self._hmac_key, b"nonce", state),
                policy_revision=record.policy_revision,
            )
        except asyncio.CancelledError:
            raise
        except OidcAuthorizationTransactionError:
            raise OidcAuthorizationTransactionError from None
        except Exception:
            raise OidcAuthorizationTransactionError from None
