# OIDC Foundation and Security Boundary

Wave 4 slice W4.7 establishes the configuration, discovery transport, metadata validation, and
JWKS cache used by the future enterprise OIDC login flow. It does **not** activate OIDC login,
create authorization transactions, exchange authorization codes, verify ID Tokens, or issue OIDC
sessions. Those behaviors remain gated by W4.8–W4.10 and the management surface remains gated by
W4.11–W4.12.

The local-owner login and recovery path remain available and independent of the identity provider.
`WORKERS=1` and one application replica remain the only supported topology.

## Configuration Contract

OIDC is disabled when `OIDC_ENABLED` is absent or false. A disabled snapshot carries no active
issuer, client, endpoint, algorithm, or secret configuration. When the later activation slices wire
this contract into login, an enabled snapshot will fail closed unless every required value is valid.

| Variable | Default | Contract |
| --- | --- | --- |
| `OIDC_ENABLED` | `false` | Boolean activation request; W4.7 does not yet expose a login path. |
| `OIDC_ISSUER` | required when enabled | Exact HTTPS issuer URL; no credentials, query, fragment, wildcard, or trailing-dot host. |
| `OIDC_CLIENT_ID` | required when enabled | Non-empty client identifier, at most 256 characters. |
| `OIDC_CLIENT_SECRET` | none | Client secret supplied directly; configure exactly one secret source. |
| `OIDC_CLIENT_SECRET_FILE` | none | Absolute regular-file path; symlinks, replacement races, invalid UTF-8, and files over 4 KiB are rejected. |
| `OIDC_REDIRECT_URI` | required when enabled | Exact HTTPS callback URL with a non-root path and no query or fragment. |
| `OIDC_SCOPES` | `openid profile email` | Space-separated, unique scopes; `openid` is mandatory; maximum 16. |
| `OIDC_ID_TOKEN_SIGNING_ALGORITHMS` | `RS256` | Comma-separated subset of `RS256`, `PS256`, and `ES256`; symmetric and `none` algorithms are impossible. |
| `OIDC_SUBJECT_CLAIM` | `sub` | Fixed to `sub`; it cannot be remapped. |
| `OIDC_USERNAME_CLAIM` | `preferred_username` | Bounded claim name for future profile display. |
| `OIDC_DISPLAY_NAME_CLAIM` | `name` | Bounded claim name for future profile display. |
| `OIDC_EMAIL_CLAIM` | `email` | Bounded profile claim only; email is never an identity key. |
| `OIDC_GROUPS_CLAIM` | `groups` | Bounded claim name for future explicit role mapping. |
| `OIDC_ALLOWED_ENDPOINT_ORIGINS` | issuer origin only | Comma-separated additional exact HTTPS origins, maximum 16 including the issuer origin. |
| `OIDC_ALLOWED_PRIVATE_HOSTS` | none | Comma-separated exact internal hostnames/IPs, maximum 32; no wildcards or CIDRs. |
| `OIDC_CONNECT_TIMEOUT_SECONDS` | `5` | Integer from 1 through 30. |
| `OIDC_READ_TIMEOUT_SECONDS` | `10` | Integer from 1 through 60. |
| `OIDC_MAX_RESPONSE_BYTES` | `262144` | Discovery/JWKS response cap from 4 KiB through 1 MiB. |
| `OIDC_JWKS_TTL_SECONDS` | `300` | Successful JWKS snapshot lifetime from 30 through 3,600 seconds. |

Secrets are excluded from the public immutable policy and its string representation. Configuration
uses the durable OIDC policy revision and authorization epoch already provided by the identity
repository. W4.11 will own mutation, optimistic concurrency, readiness preview, and revision
advancement. Until then, these variables define and test the future runtime contract; changing them
does not activate OIDC.

## Discovery and Network Safety

The client derives `/.well-known/openid-configuration` from the configured issuer and requires the
returned `issuer` to match exactly. Metadata must advertise Authorization Code flow, a supported
subject type, an allowed asymmetric ID Token algorithm, compatible client authentication, and all
configured scopes and claims. Authorization, token, JWKS, and optional UserInfo endpoints are
revalidated against the endpoint policy.

Outbound OIDC requests:

- use HTTPS with the original hostname as TLS SNI and certificate-verification target;
- resolve every address before connecting and connect only to an address from that approved set;
- reject private, loopback, link-local, reserved, unspecified, multicast, or mixed public/private
  DNS answers unless the exact host is explicitly allowlisted;
- ignore environment proxies and reject redirects, response compression, duplicate JSON keys,
  invalid UTF-8, non-finite JSON numbers, oversized headers/bodies, and unsupported media types;
- return content-free internal errors so provider responses and network details cannot reach APIs or
  audit records.

Additional endpoint origins and private hosts expand the IdP trust boundary. Operators should keep
both lists empty unless the provider architecture requires them and should use exact values rather
than broad infrastructure domains.

## JWKS Validation and Rotation

JWKS documents contain at most 64 unique-key-ID public signing keys. The parser accepts only RSA
and P-256 EC public keys compatible with the configured/discovered algorithm intersection. It
rejects symmetric keys, private key fields, malformed or non-canonical base64url values, weak or
oversized RSA moduli, invalid exponents, invalid EC points, duplicate key IDs, and a JWKS URI that
does not exactly match validated discovery metadata.

Successful snapshots replace the cache atomically and expire after the configured TTL. Cold loads,
expired refreshes, and unknown-key refreshes are single-flight. An unknown key ID causes at most one
refresh per lookup. Invalid refresh data never replaces the last valid snapshot, and a bounded
failure cooldown prevents concurrent provider failures from creating a refresh storm.

## Activation and Rollback

W4.7 has no browser-facing activation to roll back. Keep `OIDC_ENABLED=false` or unset until the
later slices provide strict ID Token verification, PKCE/state/nonce transactions, deny-by-default
identity resolution, management/audit APIs, and the localized Identity console. Removing the OIDC
variables or setting `OIDC_ENABLED=false` preserves local-owner behavior.

OIDC activation must not proceed until the W4-B protocol, abuse, recovery, API, audit, i18n,
accessibility, and browser gates pass. IdP outage may eventually block only new OIDC login; it must
never disable an existing local-owner recovery path.
