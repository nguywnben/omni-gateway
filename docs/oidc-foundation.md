# OIDC Foundation and Security Boundary

Wave 4 slices W4.7–W4.8 establish the configuration, discovery transport, metadata validation, JWKS
cache, and strict ID Token verifier used by the future enterprise OIDC login flow. They do **not**
activate OIDC login, create authorization transactions, exchange authorization codes, or issue OIDC
sessions. Those behaviors remain gated by W4.9–W4.10 and the management surface remains gated by
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
| `OIDC_CLOCK_SKEW_SECONDS` | `60` | Symmetric clock tolerance from 0 through 300 seconds for `exp`, `nbf`, and future `iat`. |
| `OIDC_MAX_ID_TOKEN_AGE_SECONDS` | `300` | Maximum accepted age from 60 through 3,600 seconds, before the configured skew. |

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

## ID Token Verification

The W4.8 verifier accepts only compact signed JWTs using the configured and discovered intersection
of `RS256`, `PS256`, and `ES256`. It rejects symmetric or unsigned algorithms, embedded or remote
header-selected keys, critical/unknown JOSE extensions, duplicate JSON fields, invalid UTF-8 or
base64url, and oversized headers, payloads, signatures, claims, audiences, or profile data before
using them.

Signature verification uses only a key from the exact policy/discovery-bound JWKS cache. An unknown
key ID may trigger one bounded rotation attempt; repeated unknown IDs share a short cooldown, while
a failed rotation never replaces the last valid snapshot or blocks a still-fresh known key.

After signature verification, the verifier requires exact `iss`, a bounded ASCII `sub`, an `aud`
containing the configured client ID, `azp` for multiple audiences, and exact client ID whenever
`azp` is present. It also requires transaction-bound `nonce`, integer `exp` and `iat`, optional
integer `nbf`, bounded clock skew, bounded token age, and a consistent issue/not-before/expiry
timeline. Optional UserInfo is usable only after its bounded `sub` exactly matches the ID Token.

Only issuer, subject, audiences, authorized party, verified timestamps/nonce, configured bounded
profile fields, policy revision, and JWKS generation leave the verifier. Unknown provider claims,
raw tokens, key material, and provider exception text have no output field. Every rejection uses
the same content-free error and suppresses the internal exception chain; asynchronous cancellation
continues to propagate.

## Activation and Rollback

W4.7–W4.8 have no browser-facing activation to roll back. Keep `OIDC_ENABLED=false` or unset until
the later slices provide PKCE/state/nonce transactions, deny-by-default identity resolution,
management/audit APIs, and the localized Identity console. Removing the OIDC
variables or setting `OIDC_ENABLED=false` preserves local-owner behavior.

OIDC activation must not proceed until the W4-B protocol, abuse, recovery, API, audit, i18n,
accessibility, and browser gates pass. IdP outage may eventually block only new OIDC login; it must
never disable an existing local-owner recovery path.
