# W4-C coordination blocker review

## Scope and result

This review covers the uncommitted provider authorization, Codex device-flow, and credential-batch
coordination changes added after W4.19. The implementation removes the corresponding process-local
maps/caches, keeps HA activation closed, and passes the 1,270-test backend suite with 30 opt-in live
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

## Retained blockers

- Credential-pool upsert/deduplication still relies on process-local locks. Safe HA requires
  storage-bound fencing or an equivalent atomic identity mutation, not a best-effort expiring lock.
- Batch CAS records are globally bounded by coordination capacity, but the historical dedicated
  256-entry domain cap has not yet been re-established with cross-replica evidence.
- The Redis quota transition still lacks measured worst-case evidence at its supported record cap.
- Live Redis plus shared database, two-replica partition/restart, completeness, and rollback tests
  remain unavailable on this host.

`SUPPORTED_HA_ACTIVATION_RECORDS` therefore remains empty and both application deployment surfaces
remain fixed at one replica.
