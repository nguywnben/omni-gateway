# Virtual-Key Management API

Virtual keys provide independently revocable, hashed-at-rest credentials for inference clients and
explicitly authorized management automation. The plaintext credential is returned only when a key
is created or rotated. List, update, revoke, usage, and delete responses never expose it, and the
plaintext is never persisted.

## Authentication and scope model

Inference routes accept a virtual key through the same SDK-compatible credential locations as the
root integration key. Management routes accept either the browser panel session, the legacy signed
Bearer session, or a virtual key in the `Authorization: Bearer <virtual-key>` header. Virtual keys
are not accepted from management query parameters or cookies.

Supported scopes are closed and versioned by the server:

| Scope | Permission |
| --- | --- |
| `inference:openai` | OpenAI-compatible inference and model routes |
| `inference:anthropic` | Anthropic-compatible inference routes |
| `inference:gemini` | Gemini-compatible inference routes |
| `management:read` | Safe management methods: `GET`, `HEAD`, and `OPTIONS` |
| `management:write` | Management mutation methods; requires `management:read` |

New keys default to the three inference scopes and no management access. This is least privilege
for the existing inference-key purpose while preserving the create API's prior behavior. Callers
must explicitly request management scopes. An unknown, empty, malformed, or internally inconsistent
scope set is rejected; authorization never treats an unknown scope as a wildcard.

Successful inference and management authentication updates `last_used_at` at most once per minute.
Management mutations performed by a virtual key are attributed to its stable key ID before the
audit service converts that identifier to a non-reversible fingerprint.

## Record contract and migration

Stored records use `schema_version: 2`. Existing unversioned keys migrate to version 2 with all
three inference scopes, preserving their previous inference access and adding no management access.
The migration writes only when every stored record is valid; a malformed record or unknown future
schema version fails closed and prevents a partial rewrite that could discard data.

Public records contain:

- `schema_version`, stable `id`, `name`, and masked `key_preview`;
- `enabled`, derived `status` (`active`, `disabled`, `expired`, or terminal `revoked`),
  `created_at`, `expires_at`, `last_used_at`, and `revoked_at`;
- monotonic `revision` for optimistic lifecycle concurrency;
- daily/monthly USD budgets and RPM/TPM limits;
- bounded `allowed_models` patterns and ordered `scopes`;
- `unknown_pricing_policy` and optional `fallback_price_usd_per_million`.

Model patterns use a bounded safe glob subset: letters, digits, `.`, `_`, `:`, `/`, `+`, `*`, `?`,
and `-`. Each pattern is at most 128 characters, at most 64 patterns are accepted, and bracket
classes or other regex-like syntax are rejected. Matching is case-insensitive.

## Unknown-pricing policy

Every key declares one of these policies:

| Policy | Contract |
| --- | --- |
| `deny` | With a hard budget, fail closed when any eligible model has no enforceable price; default for new and migrated keys |
| `warn` | Permit an unpriced hard-budget request with explicit bounded telemetry |
| `fallback` | Reserve unknown models at the positive configured price per one million estimated tokens |

Fallback prices are valid only with `fallback`, must be positive, and cannot exceed 100,000 USD per
one million tokens. A key without a daily or monthly hard budget does not invent a monetary cost
for unknown models. The durable ledger stores the fallback cost used by a budgeted request so a
restart cannot erase that spend.

## Reservation and settlement semantics

The supported single-worker runtime reserves constrained capacity atomically after authentication
and before provider selection. One reservation covers every credential retry and model fallback in
the request; retries never consume another RPM slot. For a virtual model, budget estimation uses the
highest calculated cost across its eligible concrete candidates. TPM reserves estimated prompt
tokens plus the requested maximum output; when no output maximum is supplied, the bounded default
is 4,096 tokens. Local count-token operations reserve RPM only.

Successful provider calls replace the estimate with normalized actual tokens and the policy cost
written to the durable usage ledger. Successful non-generation endpoints retain their estimate;
provider errors, response errors, disconnects, and cancelled streams release active capacity.
Commit and release are idempotent. Active reservations expire after 15 minutes, while completed RPM
and TPM usage remains in the rolling 60-second window. Actual usage above the estimate is committed
and emits overspend telemetry so later requests observe the exceeded limit.

Daily and monthly budget snapshots are reconciled with unreconciled in-process commits without
double counting. A spend-ledger outage fails hard-budget authentication with HTTP 503. Atomic
enforcement currently uses the in-process state-store implementation and therefore does not relax
the documented `WORKERS=1` and single-replica restriction. Prometheus exposes only bounded event
labels in `omni_virtual_key_quota_events_total`; key IDs and request contents are never labels.

## Management routes

| Method and route | Required virtual-key scope | Behavior |
| --- | --- | --- |
| `GET /api/virtual-keys` | `management:read` | List public records |
| `POST /api/virtual-keys` | `management:write` | Create and reveal plaintext once |
| `PATCH /api/virtual-keys/{key_id}` | `management:write` | Update supplied fields |
| `DELETE /api/virtual-keys/{key_id}` | `management:write` | Delete the record |
| `GET /api/virtual-keys/{key_id}/usage` | `management:read` | Read key-attributed usage |
| `POST /api/virtual-keys/{key_id}/rotate` | `management:write` | Atomically replace and reveal plaintext once |
| `POST /api/virtual-keys/{key_id}/revoke` | `management:write` | Permanently revoke while retaining stable identity |

Create accepts all public policy fields except server-owned identity, status, timestamps, preview,
revision, and usage metadata. Update is partial and remains backward-compatible when
`expected_revision` is omitted. Rotate and revoke require the current positive
`expected_revision`; update may supply it. A stale mutation returns HTTP 409 without changing the
record. Domain validation failures return HTTP 400 and a missing key returns HTTP 404. Rotation
preserves the stable key ID, invalidates the previous secret atomically, and returns the new secret
only in that successful response. Revocation is terminal: a revoked key cannot be re-enabled or
rotated. Create, update, rotate, revoke, and legacy delete operations use the bounded management
audit vocabulary without recording secret material.
