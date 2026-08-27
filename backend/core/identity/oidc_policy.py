"""Fail-closed, environment-locked OIDC configuration contract."""

from __future__ import annotations

import ipaddress
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import SplitResult, urlsplit

from core.identity.repository import OidcPolicyRevisionRecord
from pydantic import SecretStr

OIDC_POLICY_SCHEMA_VERSION = 1

_MAX_URL_LENGTH = 2_048
_MAX_CLIENT_ID_LENGTH = 256
_MIN_CLIENT_SECRET_LENGTH = 16
_MAX_CLIENT_SECRET_LENGTH = 2_048
_MAX_CLIENT_SECRET_FILE_BYTES = 4_096
_MAX_SCOPES = 16
_MAX_ENDPOINT_ORIGINS = 16
_MAX_PRIVATE_HOSTS = 32
_ALLOWED_ID_TOKEN_ALGORITHMS = frozenset({"RS256", "PS256", "ES256"})
_CLAIM_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_.:-]{0,63}$")
_SCOPE_PATTERN = re.compile(r"^[\x21\x23-\x5b\x5d-\x7e]{1,64}$")
_HOST_LABEL_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


class OidcConfigurationError(RuntimeError):
    """Raised when OIDC cannot be enabled without weakening its trust boundary."""


@dataclass(frozen=True, slots=True)
class OidcClaimPolicy:
    subject: str
    username: str
    display_name: str
    email: str
    groups: str

    def __post_init__(self) -> None:
        for value in (
            self.subject,
            self.username,
            self.display_name,
            self.email,
            self.groups,
        ):
            if type(value) is not str or not _CLAIM_NAME_PATTERN.fullmatch(value):
                raise OidcConfigurationError("OIDC claim configuration is invalid.")
        if self.subject != "sub":
            raise OidcConfigurationError("The OIDC subject claim must remain 'sub'.")


@dataclass(frozen=True, slots=True)
class OidcPolicy:
    schema_version: int
    revision: int
    authorization_epoch: int
    enabled: bool
    issuer: str | None
    client_id: str | None
    redirect_uri: str | None
    scopes: tuple[str, ...]
    id_token_signing_algorithms: tuple[str, ...]
    claims: OidcClaimPolicy
    allowed_endpoint_origins: tuple[str, ...]
    allowed_private_hosts: tuple[str, ...]
    connect_timeout_seconds: int
    read_timeout_seconds: int
    max_response_bytes: int
    jwks_ttl_seconds: int

    def __post_init__(self) -> None:
        if (
            type(self.schema_version) is not int
            or self.schema_version != OIDC_POLICY_SCHEMA_VERSION
        ):
            raise OidcConfigurationError("OIDC policy schema version is unsupported.")
        if type(self.revision) is not int or self.revision < 1:
            raise OidcConfigurationError("OIDC policy revision is invalid.")
        if type(self.authorization_epoch) is not int or self.authorization_epoch < 1:
            raise OidcConfigurationError("OIDC authorization epoch is invalid.")
        if type(self.enabled) is not bool:
            raise OidcConfigurationError("OIDC enabled state is invalid.")
        if type(self.claims) is not OidcClaimPolicy:
            raise OidcConfigurationError("OIDC claim policy is invalid.")
        for value, minimum, maximum, label in (
            (self.connect_timeout_seconds, 1, 30, "connect timeout"),
            (self.read_timeout_seconds, 1, 60, "read timeout"),
            (self.max_response_bytes, 4_096, 1_048_576, "response size"),
            (self.jwks_ttl_seconds, 30, 3_600, "JWKS lifetime"),
        ):
            if type(value) is not int or not minimum <= value <= maximum:
                raise OidcConfigurationError(f"OIDC {label} is invalid.")

        if not self.enabled:
            if any(
                value
                for value in (
                    self.issuer,
                    self.client_id,
                    self.redirect_uri,
                    self.scopes,
                    self.id_token_signing_algorithms,
                    self.allowed_endpoint_origins,
                    self.allowed_private_hosts,
                )
            ):
                raise OidcConfigurationError("Disabled OIDC policy must not carry active settings.")
            return

        if (
            type(self.issuer) is not str
            or type(self.client_id) is not str
            or type(self.redirect_uri) is not str
        ):
            raise OidcConfigurationError("Enabled OIDC policy is incomplete.")
        issuer = _split_https_url(self.issuer, "OIDC_ISSUER")
        redirect = _split_https_url(self.redirect_uri, "OIDC_REDIRECT_URI")
        if issuer.query:
            raise OidcConfigurationError("OIDC issuer is invalid.")
        if redirect.query or redirect.path in {"", "/"} or not redirect.path.startswith("/"):
            raise OidcConfigurationError("OIDC redirect URI is invalid.")
        if (
            not self.client_id
            or self.client_id != self.client_id.strip()
            or len(self.client_id) > _MAX_CLIENT_ID_LENGTH
        ):
            raise OidcConfigurationError("OIDC client ID is invalid.")
        if (
            type(self.scopes) is not tuple
            or not self.scopes
            or len(self.scopes) > _MAX_SCOPES
            or "openid" not in self.scopes
            or len(self.scopes) != len(set(self.scopes))
            or any(
                type(value) is not str or not _SCOPE_PATTERN.fullmatch(value)
                for value in self.scopes
            )
        ):
            raise OidcConfigurationError("OIDC scope policy is invalid.")
        if (
            type(self.id_token_signing_algorithms) is not tuple
            or not self.id_token_signing_algorithms
            or len(self.id_token_signing_algorithms) != len(set(self.id_token_signing_algorithms))
            or any(
                type(value) is not str or value not in _ALLOWED_ID_TOKEN_ALGORITHMS
                for value in self.id_token_signing_algorithms
            )
        ):
            raise OidcConfigurationError("OIDC algorithm policy is invalid.")
        if (
            type(self.allowed_endpoint_origins) is not tuple
            or not self.allowed_endpoint_origins
            or len(self.allowed_endpoint_origins) > _MAX_ENDPOINT_ORIGINS
            or self.allowed_endpoint_origins != tuple(sorted(set(self.allowed_endpoint_origins)))
        ):
            raise OidcConfigurationError("OIDC endpoint origin policy is invalid.")
        for value in self.allowed_endpoint_origins:
            if type(value) is not str:
                raise OidcConfigurationError("OIDC endpoint origin policy is invalid.")
            parsed = _split_https_url(value, "OIDC endpoint origin")
            if parsed.path or parsed.query or value != _origin(parsed):
                raise OidcConfigurationError("OIDC endpoint origin policy is invalid.")
        if _origin(issuer) not in self.allowed_endpoint_origins:
            raise OidcConfigurationError("OIDC issuer origin must remain allowed.")
        if (
            type(self.allowed_private_hosts) is not tuple
            or len(self.allowed_private_hosts) > _MAX_PRIVATE_HOSTS
            or self.allowed_private_hosts != tuple(sorted(set(self.allowed_private_hosts)))
            or any(
                type(value) is not str or value != _private_host(value)
                for value in self.allowed_private_hosts
            )
        ):
            raise OidcConfigurationError("OIDC private host policy is invalid.")


class OidcConfiguration:
    """Runtime configuration whose secret cannot be serialized with the public policy."""

    __slots__ = ("_client_secret", "policy")

    def __init__(self, policy: OidcPolicy, client_secret: SecretStr | None) -> None:
        self.policy = policy
        self._client_secret = client_secret

    @property
    def secret_configured(self) -> bool:
        return self._client_secret is not None

    def reveal_client_secret(self) -> str:
        """Reveal only at the future token-exchange boundary; never use in logs or APIs."""
        if self._client_secret is None:
            raise OidcConfigurationError("OIDC client secret is not configured.")
        return self._client_secret.get_secret_value()

    def __repr__(self) -> str:
        return (
            "OidcConfiguration("
            f"policy={self.policy!r}, secret_configured={self.secret_configured!r})"
        )

    __str__ = __repr__


def _parse_boolean(environment: Mapping[str, str], name: str, *, default: bool) -> bool:
    raw_value = environment.get(name)
    if raw_value is None:
        return default
    value = raw_value.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    raise OidcConfigurationError(f"{name} is invalid.")


def _required_text(
    environment: Mapping[str, str],
    name: str,
    *,
    maximum: int,
) -> str:
    value = environment.get(name)
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or len(value) > maximum
        or any(ord(character) < 0x20 or ord(character) == 0x7F for character in value)
    ):
        raise OidcConfigurationError(f"{name} is invalid.")
    return value


def _split_https_url(value: str, name: str) -> SplitResult:
    if len(value) > _MAX_URL_LENGTH or not value.startswith("https://") or "\\" in value:
        raise OidcConfigurationError(f"{name} must be an exact HTTPS URL.")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise OidcConfigurationError(f"{name} must be an exact HTTPS URL.") from exc
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or parsed.hostname.endswith(".")
        or "*" in parsed.hostname
        or port is not None
        and not 1 <= port <= 65_535
    ):
        raise OidcConfigurationError(f"{name} must be an exact HTTPS URL.")
    return parsed


def _issuer_url(environment: Mapping[str, str]) -> tuple[str, str]:
    value = _required_text(environment, "OIDC_ISSUER", maximum=_MAX_URL_LENGTH)
    parsed = _split_https_url(value, "OIDC_ISSUER")
    if parsed.query:
        raise OidcConfigurationError("OIDC_ISSUER must be an exact HTTPS issuer URL.")
    return value, _origin(parsed)


def _redirect_url(environment: Mapping[str, str]) -> str:
    value = _required_text(environment, "OIDC_REDIRECT_URI", maximum=_MAX_URL_LENGTH)
    parsed = _split_https_url(value, "OIDC_REDIRECT_URI")
    if parsed.query or parsed.path in {"", "/"} or not parsed.path.startswith("/"):
        raise OidcConfigurationError("OIDC_REDIRECT_URI must be an exact HTTPS callback URL.")
    return value


def _origin(parsed: SplitResult) -> str:
    hostname = parsed.hostname
    if hostname is None:  # pragma: no cover - guarded by _split_https_url
        raise OidcConfigurationError("OIDC endpoint origin is invalid.")
    rendered_host = f"[{hostname.lower()}]" if ":" in hostname else hostname.lower()
    return f"https://{rendered_host}" + (
        f":{parsed.port}" if parsed.port not in {None, 443} else ""
    )


def _scope_policy(environment: Mapping[str, str]) -> tuple[str, ...]:
    raw_value = environment.get("OIDC_SCOPES", "openid profile email")
    if type(raw_value) is not str:
        raise OidcConfigurationError("OIDC scope configuration is invalid.")
    values = tuple(raw_value.split())
    if (
        not values
        or len(values) > _MAX_SCOPES
        or "openid" not in values
        or len(values) != len(set(values))
        or any(not _SCOPE_PATTERN.fullmatch(value) for value in values)
    ):
        raise OidcConfigurationError("OIDC scope configuration is invalid.")
    return values


def _algorithm_policy(environment: Mapping[str, str]) -> tuple[str, ...]:
    raw_value = environment.get("OIDC_ID_TOKEN_SIGNING_ALGORITHMS", "RS256")
    if type(raw_value) is not str:
        raise OidcConfigurationError("OIDC algorithm configuration is invalid.")
    values = tuple(raw_value.split(","))
    if (
        not values
        or len(values) > len(_ALLOWED_ID_TOKEN_ALGORITHMS)
        or len(values) != len(set(values))
        or any(value not in _ALLOWED_ID_TOKEN_ALGORITHMS for value in values)
    ):
        raise OidcConfigurationError("OIDC algorithm configuration is invalid.")
    return values


def _claim_policy(environment: Mapping[str, str]) -> OidcClaimPolicy:
    values: dict[str, str] = {}
    for field, (name, default) in {
        "subject": ("OIDC_SUBJECT_CLAIM", "sub"),
        "username": ("OIDC_USERNAME_CLAIM", "preferred_username"),
        "display_name": ("OIDC_DISPLAY_NAME_CLAIM", "name"),
        "email": ("OIDC_EMAIL_CLAIM", "email"),
        "groups": ("OIDC_GROUPS_CLAIM", "groups"),
    }.items():
        value = environment.get(name, default)
        if type(value) is not str or not _CLAIM_NAME_PATTERN.fullmatch(value):
            raise OidcConfigurationError(f"{name} claim configuration is invalid.")
        values[field] = value
    return OidcClaimPolicy(**values)


def _comma_separated(raw_value: str, *, label: str, maximum: int) -> tuple[str, ...]:
    if not raw_value:
        return ()
    values = tuple(value.strip() for value in raw_value.split(","))
    if not values or len(values) > maximum or any(not value for value in values):
        raise OidcConfigurationError(f"OIDC {label} configuration is invalid.")
    return values


def _endpoint_origins(environment: Mapping[str, str], issuer_origin: str) -> tuple[str, ...]:
    raw_value = environment.get("OIDC_ALLOWED_ENDPOINT_ORIGINS", "")
    if type(raw_value) is not str:
        raise OidcConfigurationError("OIDC endpoint origin configuration is invalid.")
    origins = {issuer_origin}
    for value in _comma_separated(
        raw_value,
        label="endpoint origin",
        maximum=_MAX_ENDPOINT_ORIGINS,
    ):
        parsed = _split_https_url(value, "OIDC endpoint origin")
        if parsed.path or parsed.query or parsed.fragment or value != _origin(parsed):
            raise OidcConfigurationError("OIDC endpoint origin configuration is invalid.")
        origins.add(value)
    if len(origins) > _MAX_ENDPOINT_ORIGINS:
        raise OidcConfigurationError("OIDC endpoint origin configuration is invalid.")
    return tuple(sorted(origins))


def _private_host(value: str) -> str:
    if value != value.strip() or "*" in value or "/" in value:
        raise OidcConfigurationError("OIDC private host configuration is invalid.")
    try:
        return ipaddress.ip_address(value).compressed.lower()
    except ValueError:
        pass
    if ":" in value or len(value) > 253 or value.endswith("."):
        raise OidcConfigurationError("OIDC private host configuration is invalid.")
    try:
        hostname = value.encode("idna").decode("ascii").lower()
    except UnicodeError as exc:
        raise OidcConfigurationError("OIDC private host configuration is invalid.") from exc
    if any(not _HOST_LABEL_PATTERN.fullmatch(label) for label in hostname.split(".")):
        raise OidcConfigurationError("OIDC private host configuration is invalid.")
    return hostname


def _private_hosts(environment: Mapping[str, str]) -> tuple[str, ...]:
    raw_value = environment.get("OIDC_ALLOWED_PRIVATE_HOSTS", "")
    if type(raw_value) is not str:
        raise OidcConfigurationError("OIDC private host configuration is invalid.")
    values = _comma_separated(raw_value, label="private host", maximum=_MAX_PRIVATE_HOSTS)
    hosts = tuple(sorted({_private_host(value) for value in values}))
    if len(hosts) != len(values):
        raise OidcConfigurationError("OIDC private host configuration contains duplicates.")
    return hosts


def _bounded_integer(
    environment: Mapping[str, str],
    name: str,
    *,
    default: int,
    minimum: int,
    maximum: int,
) -> int:
    raw_value = environment.get(name, str(default))
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise OidcConfigurationError(f"{name} is invalid.") from exc
    if not minimum <= value <= maximum:
        raise OidcConfigurationError(f"{name} is invalid.")
    return value


def _validate_secret(value: str) -> SecretStr:
    if (
        not _MIN_CLIENT_SECRET_LENGTH <= len(value) <= _MAX_CLIENT_SECRET_LENGTH
        or value != value.strip()
        or any(ord(character) < 0x20 or ord(character) == 0x7F for character in value)
    ):
        raise OidcConfigurationError("OIDC client secret is invalid.")
    return SecretStr(value)


def _client_secret(environment: Mapping[str, str]) -> SecretStr:
    environment_secret = environment.get("OIDC_CLIENT_SECRET")
    secret_file_value = environment.get("OIDC_CLIENT_SECRET_FILE")
    configured_sources = sum(
        value is not None and value != "" for value in (environment_secret, secret_file_value)
    )
    if configured_sources != 1:
        raise OidcConfigurationError("Configure exactly one OIDC client secret source.")
    if environment_secret:
        return _validate_secret(environment_secret)

    if type(secret_file_value) is not str:
        raise OidcConfigurationError("OIDC client secret file is invalid.")
    secret_path = Path(secret_file_value)
    if not secret_path.is_absolute():
        raise OidcConfigurationError("OIDC client secret file path must be absolute.")
    try:
        if secret_path.is_symlink():
            raise OidcConfigurationError("OIDC client secret file cannot be a symbolic link.")
        if not secret_path.is_file() or secret_path.stat().st_size > _MAX_CLIENT_SECRET_FILE_BYTES:
            raise OidcConfigurationError("OIDC client secret file is invalid.")
        raw_secret = secret_path.read_bytes()
        if len(raw_secret) > _MAX_CLIENT_SECRET_FILE_BYTES:
            raise OidcConfigurationError("OIDC client secret file is invalid.")
        secret = raw_secret.decode("utf-8").rstrip("\r\n")
    except OidcConfigurationError:
        raise
    except (OSError, UnicodeError) as exc:
        raise OidcConfigurationError("OIDC client secret file is invalid.") from exc
    return _validate_secret(secret)


def _disabled_policy(revision: OidcPolicyRevisionRecord) -> OidcPolicy:
    return OidcPolicy(
        schema_version=OIDC_POLICY_SCHEMA_VERSION,
        revision=revision.revision,
        authorization_epoch=revision.authorization_epoch,
        enabled=False,
        issuer=None,
        client_id=None,
        redirect_uri=None,
        scopes=(),
        id_token_signing_algorithms=(),
        claims=OidcClaimPolicy("sub", "preferred_username", "name", "email", "groups"),
        allowed_endpoint_origins=(),
        allowed_private_hosts=(),
        connect_timeout_seconds=5,
        read_timeout_seconds=10,
        max_response_bytes=262_144,
        jwks_ttl_seconds=300,
    )


def load_oidc_configuration(
    revision: OidcPolicyRevisionRecord,
    *,
    environ: Mapping[str, str] | None = None,
) -> OidcConfiguration:
    """Load one immutable OIDC snapshot without exposing its client secret in policy data."""
    if type(revision) is not OidcPolicyRevisionRecord:
        raise OidcConfigurationError("OIDC policy revision record is invalid.")
    environment = os.environ if environ is None else environ
    enabled = _parse_boolean(environment, "OIDC_ENABLED", default=False)
    if not enabled:
        return OidcConfiguration(_disabled_policy(revision), None)

    issuer, issuer_origin = _issuer_url(environment)
    client_id = _required_text(
        environment,
        "OIDC_CLIENT_ID",
        maximum=_MAX_CLIENT_ID_LENGTH,
    )
    policy = OidcPolicy(
        schema_version=OIDC_POLICY_SCHEMA_VERSION,
        revision=revision.revision,
        authorization_epoch=revision.authorization_epoch,
        enabled=True,
        issuer=issuer,
        client_id=client_id,
        redirect_uri=_redirect_url(environment),
        scopes=_scope_policy(environment),
        id_token_signing_algorithms=_algorithm_policy(environment),
        claims=_claim_policy(environment),
        allowed_endpoint_origins=_endpoint_origins(environment, issuer_origin),
        allowed_private_hosts=_private_hosts(environment),
        connect_timeout_seconds=_bounded_integer(
            environment,
            "OIDC_CONNECT_TIMEOUT_SECONDS",
            default=5,
            minimum=1,
            maximum=30,
        ),
        read_timeout_seconds=_bounded_integer(
            environment,
            "OIDC_READ_TIMEOUT_SECONDS",
            default=10,
            minimum=1,
            maximum=60,
        ),
        max_response_bytes=_bounded_integer(
            environment,
            "OIDC_MAX_RESPONSE_BYTES",
            default=262_144,
            minimum=4_096,
            maximum=1_048_576,
        ),
        jwks_ttl_seconds=_bounded_integer(
            environment,
            "OIDC_JWKS_TTL_SECONDS",
            default=300,
            minimum=30,
            maximum=3_600,
        ),
    )
    return OidcConfiguration(policy, _client_secret(environment))
