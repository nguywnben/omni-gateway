# W4-C coordination blocker review

## Scope and result

This review covers the post-W4.19 provider authorization, Codex device-flow, credential-batch, and
credential-pool coordination changes through implementation commit `e02ff71`. The implementation
removes the identified process-local identity-admission authorities, restores exact bounded batch
domains, keeps HA activation closed, and passes the 1,285-test backend suite with 30 opt-in live
tests skipped.

## Findings resolved

| Severity | Finding | Resolution |
| --- | --- | --- |
| Critical | Claude/xAI PKCE verifiers and callback state were process-local and unavailable to another replica. | Replaced with encrypted, provider-bound, one-time OIDC coordination using domain-separated HMAC indexes and atomic consume. |
| Critical | Codex polling could not move between replicas and concurrent pollers could exchange the same device authorization. | Added an absolute-lifetime encrypted CAS state machine with bounded leases, exact revision ownership, release-on-pending, and terminal secret erasure before token exchange. |
| Critical | Credential batch reservations and completed responses were process-local, allowing duplicate mutation across replicas. | Added fenced shared reservation ownership, ownership checks before each mutation, encrypted/chunked response publication, and retained pending state after unknown post-mutation failure. |
| Important | A 100-target response can exceed the generic 16 KiB CAS payload limit. | Responses up to 256 KiB are compressed into 12 KiB encrypted chunks; a digest-bound root CAS publishes them atomically. |
| Important | Cancellation could release an idempotency reservation after a mutation had an unknown result. | The route releases only before the first mutation; after that point failure leaves the request in progress and prevents an unsafe retry. |
| Important | The Helm replica guard text and its test diverged in the W4.19 workspace. | Restored the exact tested guard while retaining the enforced one-replica ceiling. |
| Critical | Pool admission and deduplication composed multiple storage calls behind a process-local lock, so two replicas could admit the same identity. | Moved the complete snapshot-plan-write sequence into a storage-owned mutation transaction: SQLite `BEGIN IMMEDIATE`, PostgreSQL transactional table lock, and a MongoDB transaction-conflict gate. |
| Important | Preview and idempotency state used the generic coordination capacity without the historical 256-entry domain bounds. | Added separate encrypted CAS registries capped at exactly 256 live full-HMAC entries, pruned with backend time and covered by concurrent, expiry, completion, and release tests. |
| Important | Preview capacity/outage failures could surface as an ambiguous internal error. | Capacity now returns a typed HTTP 429 with `Retry-After`; dependency failure returns a typed 503 batch envelope. |
| Important | A MongoDB pool transaction could leave the optional standalone Redis routing cache stale. | Rebuild the mode cache after the durable mutation commits; coordinated mode continues to prohibit this legacy cache. |

## Retained blockers

- The Redis quota transition still lacks measured worst-case evidence at its supported record cap.
- Live Redis plus shared database, two-replica partition/restart, completeness, and rollback tests
  remain unavailable on this host.

`SUPPORTED_HA_ACTIVATION_RECORDS` therefore remains empty and both application deployment surfaces
remain fixed at one replica.

## Verification evidence

- Full backend suite: 1,285 passed, 30 opt-in live-backend tests skipped.
- Affected pool/import/provider/MongoDB/batch matrix: 63 passed.
- Repository-wide backend Ruff lint and format, `compileall`, `pip check`, and `git diff --check`
  pass.
- SQLite rollback and two-client identity admission execute against a real temporary database.
  PostgreSQL and MongoDB transaction boundaries are driver-contract tests; live shared-backend
  parity remains unavailable and is not counted as a pass.
