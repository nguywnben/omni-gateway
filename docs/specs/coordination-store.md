# Coordination store semantic primitives

## Status and scope

Wave 4 slice W4.15 defined the original coordination semantics. W4.16-W4.19 moved runtime callers,
added the closed HA lifecycle, and removed process-local coordination authorities. The 2026-09-05
Quota State v2 checkpoint replaces the original record-population quota aggregation with fixed
work and adds bounded reconciliation. It does not activate coordinated mode, relax `WORKERS=1`,
or allow more than one application replica; external two-replica evidence remains mandatory.

This contract refines ADR-006 and ADR-008. Callers depend on typed compare-and-set, fencing,
reservation, expiry, replay, and invalidation behavior. They never depend on Redis commands,
scripts, key names, or response encodings.

## Alternatives considered

1. **Redis server-side scripts (selected).** A fixed set of bounded Lua scripts performs each
   read-modify-write atomically. Script bodies are application-owned, loaded by digest, and safe to
   reload after restart or failover. This matches Redis atomic-execution semantics and supports a
   deterministic in-process implementation.
2. **Best-effort distributed locks.** Rejected because an expired or paused lock holder can mutate
   state after a newer holder and because unlock-by-delete can release another owner's lock.
3. **Client-side WATCH/MULTI retry loops.** Rejected for the first contract because cancellation,
   retry ceilings, and unknown transaction outcomes enlarge the failure surface without improving
   the semantic boundary.
4. **Redis Functions.** Deferred. Functions are server-managed deployment artifacts; W4.15 keeps
   the implementation self-contained and reloadable without granting application startup library-
   management authority.

Official Redis sources:

- https://redis.io/docs/latest/develop/programmability/eval-intro/
- https://redis.io/docs/latest/develop/using-commands/keyspace/#hashtags
- https://redis.io/docs/latest/commands/time/

## Trust boundary and threat model

Redis replies, stored values, topology state, and caller inputs are untrusted. Assets are session
and authorization freshness, rate-limit capacity, reservation ownership, routing exclusivity,
cache freshness, and the sole active coordination epoch.

- **Spoofing/elevation:** every mutation carries the exact current fencing epoch. A stale epoch or
  an epoch awaiting reconciliation cannot mutate coordinated state.
- **Tampering:** stored records use a closed schema version and exact parser. Unknown fields,
  malformed numbers, impossible state, or a payload/revision mismatch fail closed.
- **Replay:** every mutation has a bounded operation or reservation ID. Exact replay is idempotent;
  same-ID/different-input replay is a conflict and never mutates state.
- **Disclosure:** keys contain only a deployment digest and digests of caller-provided logical
  names. Payloads and Redis URLs never enter logs or metric labels. Callers must never pass bearer
  tokens or plaintext secrets as logical identifiers.
- **Denial of service:** identifiers, payloads, TTLs, counters, records per resource, cleanup work,
  script keys, and script loops are bounded. Capacity or cleanup exhaustion fails admission closed.
- **Split brain:** advancing the epoch atomically enters `reconciling`. Normal mutations remain
  closed until the exact epoch is explicitly marked `ready` after the later reconciliation
  workflow.

## Versioned domain

`COORDINATION_SCHEMA_VERSION` is `1`. Public domain objects are frozen and reject booleans where
integers are required, non-finite numbers, control characters, unknown enum values, oversized
identifiers, negative revisions, invalid TTLs, and malformed stored results.

Common bounds:

- deployment namespace: 3–64 lower-case ASCII letters, digits, and hyphens;
- logical scope/key: 1–128 printable ASCII characters, hashed before becoming a Redis key;
- operation/reservation ID: 1–128 printable ASCII characters;
- opaque compare-and-set payload: at most 16 KiB;
- TTL: 1 second through 30 days;
- revision/generation/epoch: integer 1 through signed 63-bit maximum;
- active plus retained quota records per virtual key: at most 100,000;
- expired records pruned by one mutation: at most 256; additional due work returns a bounded
  `reconciliation_required` result instead of running an unbounded script.

## Fencing lifecycle

A new namespace has one persistent initialization marker and one persistent epoch record in the
same deployment hash slot. `read_epoch()` is the sole provisioning transition: it may atomically
create marker plus ready epoch `1` only when both are absent. Reading the epoch is side-effect free
after provisioning. If exactly one member is absent, either member is malformed or expiring, or a
normal mutation observes an absent member, the namespace is corrupt and the operation fails
closed. CAS, invalidation, quota reserve, quota commit, quota release, epoch advance, and epoch
ready never infer or repair initialization.

The marker distinguishes a genuinely new namespace from partial marker/epoch loss. It cannot
distinguish a deliberate or accidental deletion of every key in the namespace from first use.
Preventing whole-namespace loss, restoring authoritative epoch state, and gating activation on
that operational protection belong to the W4.18 activation/reconciliation work. Clearing the
entire namespace is therefore not a supported recovery mechanism.

`advance_epoch(expected_epoch, operation_id)` is one compare-and-set transition to the next epoch
in `reconciling` state. Exact replay returns the same result; stale or conflicting replay does not
advance it again.

`mark_epoch_ready(epoch, operation_id)` changes only that exact reconciling epoch to `ready`.
Normal CAS, invalidation, quota reserve, quota commit, and quota release operations require the
exact ready epoch. A missing, corrupt, stale, or reconciling epoch fails closed.

## Compare-and-set

The store accepts an opaque bytes payload so domain codecs remain outside the coordination layer.
Create uses expected revision `0` and produces revision `1`; update requires the exact positive
revision and produces `revision + 1`. Records may have a bounded TTL. Exact operation replay returns
the original result without extending TTL or advancing revision. Same-ID/different-request replay
is a conflict. Expired or absent records behave as absent, and corrupt stored records fail closed.

## Invalidation

Invalidation is a monotonic generation per logical scope. The first mutation produces generation
`1`; each new operation increments it once. Exact replay returns the original generation;
conflicting replay fails. Consumers compare a cached generation with the current generation and
discard derived state when they differ. Invalidation history is bounded by the configured replay
TTL and contains no payload.

## Quota reservation lifecycle

The existing `QuotaReservationRequest`, `QuotaCommitRequest`, and result types remain the stable
compatibility surface. W4.15 adds an exact fencing epoch without changing existing call sites;
standalone requests default to epoch `1`.

Reserve atomically expires bounded stale state, detects exact/conflicting replay, evaluates only
RPM and TPM, then stores one active estimate or returns a typed denial. Commit atomically replaces
an unexpired estimate with actual token usage; release reverses only an active estimate. Terminal
or expired state never becomes active again. Unknown or malformed stored state, stale epoch,
unavailable Redis, cleanup backlog, or capacity exhaustion fails admission closed.

The selected durable usage ledger is the sole authority for daily/monthly monetary-budget reserve,
settlement, reconciliation, and crash recovery. Coordination request budget fields remain only for
source/replay compatibility and runtime callers send neutral values. Redis quota state must never
reconstruct durable spend.

Coordination expiry, retention, and rate windows use the backend's clock captured once per
mutation: the injected clock for the in-process reference and Redis `TIME` for Lua. Caller `now`
values remain validated business/replay evidence and cannot expire or extend coordination state.
TPM aggregation and comparison preserve the full signed-63-bit token domain with decimal-string
integer arithmetic; an aggregate above that domain saturates fail closed instead of passing
through a binary64 approximation. Both signed float zeros serialize canonically as `0`.

Quota State v2 uses exactly 61 circular second slots. At Redis second `S`, admission includes
absolute seconds `[S-60, S]`, so enforcement can be conservative by less than one second but never
under-enforces. Each slot field `0..60` has the closed encoding
`2|absolute_second|requests|tokens`. Each 14-field lifecycle record has the closed encoding
`2|fingerprint|key_digest|state|active_until_ms|retained_until_ms|accepted_at_ms|estimated_tokens|committed_at_ms|actual_tokens|rpm_limit_or_n|tpm_limit_or_n|retention_ms|next_expiry_ms`;
replay records retain their closed seven-field v2 encoding. A persistent, non-expiring
`2|epoch|ready` per-key schema marker fences every mutation, and reservation TTL is at least 61
seconds.

## Redis layout and atomicity

All keys for one deployment contain the same hash tag derived from the deployment namespace. This
keeps each bounded multi-key script in one Redis Cluster slot and makes the global fencing epoch
atomic with every mutation. The trade-off is that one deployment initially occupies one
coordination shard; W4.19 must measure the supported topology before activation.

Scripts receive every accessed key through `KEYS` and all data through `ARGV`; they never call
`KEYS`, perform `SCAN`, construct undisclosed key names, or execute unbounded loops. Redis server
time governs expiry so replica clock drift cannot admit stale work. Script-cache loss is handled by
reloading the fixed application-owned script and retrying `EVALSHA` once through redis-py.

Cleanup preflights at most 257 current due members before mutation and applies at most 256. A
backlog failure changes neither records nor expiry indexes and repeats until explicit
reconciliation; replaced/stale in-process heap nodes do not consume the cleanup budget.

Quota mutation work is independent of the retained-record population: one directly addressed
lifecycle record, 61 bucket fields through a fixed `HMGET`, cardinality/index checks, and at most
256 due lifecycle/replay entries after a 257-item preflight. Mutation scripts contain no
lifecycle-hash `HGETALL` or per-record `ZSCORE` loop. A deterministic 100,000-record fixture proves
the same `(1 record, 61 buckets)` inspection count as a small target. This closes the algorithmic
O(n) blocker; it is not live Redis latency or topology evidence.

During a drained epoch transition, operator reconciliation processes at most 256 lifecycle,
replay, or marker entries per call behind an opaque authenticated cursor. Dry-run never mutates.
Apply disposes terminal v1 ephemeral state, blocks on active/unexpired or corrupt state, initializes
empty v2 buckets and `2|epoch|ready`, and must reach an independently revalidated complete result
before `mark-ready` can succeed.

## Failure and cancellation semantics

- Connection, timeout, protocol, decode, script, or unknown-result failures raise one bounded
  coordination-unavailable/corrupt error and never return an allow decision.
- A caller may retry the identical operation ID after cancellation or an unknown response. The
  result is idempotent if the first execution committed.
- Commit/release retries remain idempotent only while their exact epoch is `ready`. During
  `reconciling`, every caller mutation fails closed; W4.18 reconciliation tooling owns settlement
  of durable evidence left by an earlier epoch.
- Closing the store is idempotent. Use after close fails closed.

## Operability

On-call questions are: is the coordination backend reachable, which semantic operation is failing,
are stale epochs or reconciliation barriers blocking work, and is bounded cleanup/capacity
exhausted? Metrics use only closed `backend`, `operation`, and `result` labels. No namespace,
logical key, operation ID, reservation ID, payload, URL, exception text, amount, or identity becomes
a metric label or log field.

W4.15 may expose internal rendering and health probes for tests, but `/ready` and deployment mode
selection remain unchanged until W4.18 establishes the full prerequisite and reconciliation gate.

## Verification and closure

- One behavioral fixture runs against in-process and opt-in live Redis stores.
- Deterministic tests cover validation, exact/conflicting replay, stale/reconciling epoch, CAS
  creation/update/expiry, invalidation generation, quota concurrency, commit/release/expiry,
  bounded cleanup, capacity, corrupt replies, cancellation retry, and script-cache reload.
- Live Redis tests use a unique deployment namespace and remove only that namespace's known keys.
- The 2026-09-05 focused quota/HA matrix passed 164 tests with seven live Redis skips. Full backend
  discovery passed 1,320 tests with 30 opt-in live-backend skips. The live Redis and required
  two-replica shared-database matrices did not run on this host and remain activation blockers.
- Repository-wide tests, Ruff, format, compileall, dependency consistency/audit, JavaScript/YAML/
  shell syntax, diff/secret review, adversarial review, atomic commits, and committed-runtime smoke
  are closure gates.
