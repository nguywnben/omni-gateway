# Credential batch coordination contract

## Status

Accepted W4-C blocker-closure implementation. This contract moves preview and idempotency authority
behind the lifecycle-selected coordination store. It does not make credential-pool upsert or
deduplication safe for multiple replicas and does not activate coordinated mode.

## Security and correctness boundary

- Preview and idempotency keys are HMAC-addressed; raw tokens, idempotency keys, filenames, and
  response bodies never appear in coordination keys, logs, or metric labels.
- CAS payloads are AES-GCM encrypted with a lifecycle-derived, domain-separated key.
- Reservations are bound to the exact request fingerprint and fencing epoch. A conflicting key,
  stale epoch, corrupt record, or unavailable backend fails closed.
- An active reservation is never automatically stolen. The route verifies exact ownership before
  every credential mutation.
- Cancellation before the first mutation releases the reservation. Once any mutation may have
  started, a completion failure retains the pending marker so a retry cannot repeat unknown work.
- Completed responses remain available for 24 hours. A response up to 256 KiB is compressed,
  divided into bounded encrypted CAS chunks, verified by digest, and made visible only by one final
  atomic root transition.
- Preview tokens expire after five minutes. Batch input remains capped at 100 targets and per-item
  execution remains bounded to five seconds.

## Failure semantics

Chunk writes that precede a failed root commit are invisible and expire. A missing/corrupt chunk,
digest mismatch, decompression overflow, duplicate JSON field in a control record, owner mismatch,
or dependency failure never returns a cached success and never grants mutation authority.

The generic coordination store remains globally bounded. A dedicated 256-entry per-domain
admission counter has not yet been proven, so capacity-hardening remains part of the retained
credential-mutation blocker before HA activation.

## Verification

Focused tests cover cross-client preview and replay, concurrent single-owner reservation,
conflicting key reuse, safe release, ownership fencing, large multi-chunk response reconstruction,
stale epochs, dependency loss, cancellation, and existing route compatibility.
