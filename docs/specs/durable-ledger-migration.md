# Durable-ledger migration contract

## Status and scope

Wave 4 slice W4.13 defines the inventory and the version-1 contract used to move durable records
from an authoritative standalone backend to a shared backend. It does not copy a live deployment,
change the selected storage backend, activate coordinated mode, or relax the one-worker/one-replica
limit. Those actions remain gated by W4.14–W4.19 and explicit operator approval.

## Durable inventory

The migration manifest is closed and versioned. It covers every durable record named by ADR-006
and ADR-008, including implementation gaps rather than hiding them:

| Family | Current physical owner | Shared parity | Notes |
| --- | --- | --- | --- |
| Configuration | selected backend `config` record set | Yes | Includes hashed/local secrets and internal signing-key material; values are copied but never written to checkpoint metadata. |
| Provider-pool credentials | selected backend `credentials` records | Yes | Encrypted/token-bearing payload plus mutable routing fields; current complete record is copied until W4.17 separates coordinated fields. |
| Primary credentials | selected backend `primary_credentials` records | Yes | Same confidentiality rule as provider-pool credentials. |
| Virtual keys | `config.virtual_keys` versioned document | Yes, through config | Inventoried separately because it is an authorization and billing boundary. |
| Management identities | identity repository | Yes | Includes identities and authorization epochs. |
| Role bindings | identity repository | Yes | Independent optimistic revisions. |
| OIDC policy revision | identity repository | Yes | Contains policy and authorization epochs, not client secrets. |
| Identity schema evidence | identity repository | Yes | Existing additive `management_identity_v1` record. |
| Audit events | append-only audit repository | Yes | Redacted before storage. |
| Request traces | bounded trace repository | Yes | Prompt/body content is excluded by the trace contract. |
| Usage/cost ledger | standalone `usage_stats.db` | No | W4.14 must add selected-backend repositories before authority can switch. |
| Hard-budget reservation journal | not implemented | No | W4.14/W4.17 must provide durable journal and reconciliation semantics. |
| Migration checkpoints | versioned checkpoint repository | W4.13 | Contains metadata only; never record payloads, names, prompts, credentials, or identity attributes. |

A manifest entry explicitly declares its readiness. A migration plan containing any non-ready
family cannot reach the authority-switch state.

## Record and integrity contract

Each source repository exposes records in stable logical-key order through a bounded opaque cursor.
A record has a closed family, a stable bounded logical ID, a positive schema version, and a JSON
payload. The payload may contain sensitive durable data and is passed only from the source reader
to the target writer; it is excluded from checkpoints, logs, exceptions, and representations.

Copy is idempotent by `(family, logical ID)`. Replaying an identical record is accepted. A target
record with the same key but different canonical content is corruption and stops the migration.
Canonical JSON rejects unsupported/non-finite values. Counts and content checksums are calculated
independently over a stable full scan of source and target. Checkpoint digests use HMAC-SHA-256 with
an injected deployment secret so low-entropy configuration values cannot be tested offline from
checkpoint data.

## Authority state machine

Exactly one backend is authoritative throughout the contract:

1. `planned` — source is authoritative; immutable plan and manifest are recorded.
2. `copying` — source remains authoritative; bounded pages are upserted idempotently.
3. `verifying` — source remains authoritative; source and target are scanned independently.
4. `ready_to_switch` — source remains authoritative; all requested families have equal non-zero or
   explicitly empty counts and equal keyed checksums, and all manifest entries are switch-ready.
5. `target_authoritative` — the target becomes the sole authority through an explicit compare-and-
   set transition. This contract does not invoke the transition automatically.
6. `rollback_ready` — target remains authoritative while an operator drains and verifies the
   reverse path.
7. `rolled_back` — source becomes the sole authority after the rollback barrier.

There is no dual-authoritative or indefinite dual-write state. An interruption before
`target_authoritative`, including copy, verification, checksum, corruption, or restart failure,
leaves the source authoritative. Resume repeats at most the last uncheckpointed page and relies on
idempotent target upsert.

## Checkpoint contract

Checkpoint records use optimistic compare-and-set revisions and persist plan ID, source/target
backend types, phase, sole authority, opaque copy cursor, copied count, verified source/target
counts and HMAC digests, timestamps, and a bounded machine-readable failure code. Stored records
are reconstructed through the same closed validators used for new records. Unknown fields,
versions, phases, backends, authority contradictions, malformed cursors/checksums, revision gaps,
or target-authoritative state without completed verification fail closed as corruption.

Checkpoint creation and updates are additive. No API deletes a checkpoint or copied durable data.
Rollback changes authority only after a separate drain/reconciliation barrier and never truncates
audit, trace, identity, usage, configuration, or credential history.

## Verification and activation boundary

W4.13 closes only when contract tests cover interruption, duplicate replay, conflicting duplicate,
checksum mismatch, corrupt persisted checkpoint, optimistic conflict, restart/resume, invalid
transition, and rollback authority. W4.14 must close the usage and reservation-journal gaps and
live backend parity before any migration may reach `ready_to_switch`. W4.18 provides operator
commands and readiness integration; W4.19 supplies canary/failure evidence and the separate
activation decision.
