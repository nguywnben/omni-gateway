# Durable-ledger migration runbook

## Current availability

W4.13 provides the versioned inventory, migration state machine, bounded copy/verification runner,
and durable checkpoint repositories for SQLite, PostgreSQL, and MongoDB. It deliberately does
**not** expose an operator command, management API, background job, automatic backend selection,
or authority switch. Do not attempt a live migration from this revision.

The supported topology remains standalone with one worker and one application replica. Setting
`POSTGRESQL_URI`, `MONGODB_URI`, `REDIS_URL`, or a higher worker/replica count does not complete a
migration and does not earn an HA claim. W4.14 must first close usage-ledger and hard-budget journal
parity; W4.18 will supply the executable operator workflow and readiness gate.

## Invariants an operator must preserve

- Record the exact source and target backend categories and stable non-secret instance IDs. The
  instances must differ; two distinct instances may use the same backend category.
- Acquire and persist a source mutation-barrier evidence ID before planning. Treat loss of that
  barrier at any later check as a hard stop.
- Keep the source as the only authoritative backend through planning, copy, verification, and
  `ready_to_switch`.
- Never write record payloads, credentials, prompts, identity attributes, or raw logical keys to a
  checkpoint, log, ticket, or migration report.
- Resume from the stored non-negative numeric offset. Re-running the last uncheckpointed page is
  expected and must result only in identical put-if-absent-or-equal writes.
- Treat a same-key/different-content duplicate, malformed stored checkpoint, stale revision,
  incomplete empty page, out-of-order record, count mismatch, or checksum mismatch as a stop
  condition.
- Never make target authoritative while any inventory family is marked not ready.
- Never delete source or target records as rollback. Durable history remains intact.

## Intended staged procedure

This is the contract W4.18 tooling must implement; it is not a manual command sequence for W4.13.

1. Drain to one worker and one replica and confirm standalone readiness.
2. Back up the authoritative backend and verify restore evidence outside the application process.
3. Create one immutable migration plan covering the complete versioned inventory.
4. Copy one bounded page at a time under the active source mutation barrier. Persist the next safe
   numeric offset and count with optimistic compare-and-set only after every strict target write
   in the page succeeds and the barrier is revalidated.
5. On restart, reload and strictly revalidate the checkpoint, then repeat at most the last
   uncheckpointed page.
6. Independently scan source and target in stable logical-key order. Compare counts and keyed
   canonical HMAC-SHA-256 digests for every family.
7. Keep source authoritative if verification fails or a required family is not switch-ready.
8. Only after W4.14–W4.19 gates and explicit operator approval, perform the single compare-and-set
   transition that makes target the sole authority.
9. For rollback, W4.18 tooling must block admission, drain outstanding work, reverse-migrate and
   reconcile all durable ledgers and policy epochs, verify evidence from the reverse barrier, then
   make source authoritative. W4.13 deliberately exposes no authority-flip shortcut. Do not
   truncate either side.

## Failure response matrix

| Failure | Required state | Response |
| --- | --- | --- |
| Process exits before page checkpoint | Source authoritative | Restart and replay the page; identical target records are no-ops. |
| Checkpoint CAS conflict | Current authority unchanged | Stop this runner, reload the latest checkpoint, and investigate concurrent operation. |
| Same key has different content | Source authoritative | Stop; preserve both stores and investigate corruption or an invalid snapshot boundary. |
| Source/target count or HMAC mismatch | Source authoritative, `verifying` | Do not switch; repeat a stable scan only after the cause is corrected. |
| Stored checkpoint has unknown/malformed data | Current authority unchanged | Mark migration unavailable and recover the checkpoint store from verified backup/evidence. |
| Usage ledger or reservation journal not ready | Source authoritative | Continue standalone; complete W4.14/W4.17 rather than bypassing inventory. |
| Failure after target authority | Target authoritative | Enter the drain/reconcile rollback procedure; never point writes at both stores. |

## Evidence to retain

Retain only bounded metadata: plan ID, schema/manifest version and manifest checksum, backend
categories and stable non-secret instance IDs, source barrier ID, phase, sole authority, revision,
per-family numeric offsets, explicit-empty declarations, counts and HMAC digests, timestamps, and
machine failure code.
Record test/build revision and operator approval separately. Never retain the HMAC key or durable
record payload in the migration evidence.

The detailed implementation contract is
[`docs/specs/durable-ledger-migration.md`](../specs/durable-ledger-migration.md). ADR-006 and ADR-008
remain authoritative for durable/coordinated state and HA activation.
