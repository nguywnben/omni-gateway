# HA lifecycle, reconciliation, and rollback

## Safety boundary

This is an experimental engineering runbook, not a production deployment guide. The coordinated
implementation has no activation record and the Production Self-Hosted R1 allowlist is empty.
`REDIS_URL` alone never enables HA. Keep `OMNI_RUNTIME_MODE=standalone`, `WORKERS=1`, and one replica.

Back up the selected durable backend and Redis namespace before any planned transition. Never use
`FLUSHDB`, `FLUSHALL`, `SCRIPT FLUSH`, wildcard deletion, manual epoch edits, or direct binding
record edits.

The external evidence runner isolates its host-side lifecycle administrator in a dedicated,
initially empty temporary credentials directory. Do not point that runner at a workstation or
production credentials directory: legacy local SQLite files are not evidence inputs and the
synthetic PostgreSQL inventory is the sole durable authority for the matrix.

## Diagnose readiness

1. Confirm `/health` is HTTP 200. Liveness does not touch dependencies.
2. Inspect `/ready`. A 503 reports only storage, usage-ledger, and coordination categories.
3. Inspect `omni_ha_runtime_ready`, `omni_ha_coordination_available`,
   `omni_ha_runtime_info`, and `omni_coordination_operations_total`.
4. Run `python backend/ha_admin.py status` with the exact coordinated environment. Output is
   content-free and never includes URI, credentials, namespace, deployment ID, or key material.

If durable binding exists but the Redis binding marker is absent, treat this as namespace loss.
Restore the matching namespace from backup; do not bootstrap a new marker. If records mismatch,
stop and verify deployment identity, identifier-key fingerprint, manifest checksum, activation
record, and epoch using the original secured configuration.

An `unavailable` coordinated process is permanently latched for its configured epoch, even when
Redis and PostgreSQL later answer probes. Do not reopen it after a transient green ping. Complete
the operator recovery sequence on a new epoch and replace the process; only the restarted process
may report coordinated readiness. Public diagnostics expose only fixed reason categories and never
dependency exception text, DSNs, namespaces, or credentials.

## Planned epoch transition

Commands are dry-run unless `--apply` is present. Capture each JSON result in the change record.

1. Preview and apply drain:

   ```text
   python backend/ha_admin.py drain
   python backend/ha_admin.py drain --apply
   ```

2. Wait for in-flight provider requests and durable settlements to complete. Confirm `/ready` is
   503 and durable audit/usage writes are current.
3. Use a stable, unique operation ID and advance exactly one epoch:

   ```text
   python backend/ha_admin.py advance-epoch --operation-id epoch-change-00000001
   python backend/ha_admin.py advance-epoch --operation-id epoch-change-00000001 --apply
   ```

4. Update only `OMNI_COORDINATION_EPOCH` to the returned epoch, then choose one stable
   reconciliation operation ID. Preview bounded binding and reconciliation. The page size is
   closed to `1..256` and defaults to 256:

   ```text
   python backend/ha_admin.py reconcile --operation-id reconcile-00000001
   python backend/ha_admin.py reconcile --operation-id reconcile-00000001 --page-size 256
   ```

5. Apply reconciliation repeatedly until the content-free result reports
   `reconciliation_complete: true`. Components execute in the fixed order quota, durable
   usage/reservation liability, identity/session policy, and cache/governance invalidation. Each
   successful apply stores an opaque cursor inside an HMAC-authenticated durable receipt; output
   reports only whether a cursor exists. An interruption is resumed with the same operation ID,
   after authenticating the intermediate checkpoint. A different ID,
   stale cursor, missing generation, surviving prior-epoch session, active reservation conflict,
   durable-owner failure, or Redis failure stops the workflow:

   ```text
   python backend/ha_admin.py reconcile --operation-id reconcile-00000001 --page-size 256 --apply
   ```

   Every call validates at most 256 records and the full receipt permits at most 64 pages. Terminal
   v1 evidence is disposed because monetary budget authority remains in the durable usage ledger;
   active unexpired reservations stop the workflow. Empty per-key rate buckets are initialized as
   schema `2|<epoch>|ready` only while the exact epoch is reconciling.

6. Check `python backend/ha_admin.py status`. It must report
   `reconciliation_complete: true` and `reconciliation_receipt_present: true`. After durable
   authority, active liability, identity/session policy, cache generations, and backups are
   independently verified, mark the exact epoch ready with another stable operation ID:

   ```text
   python backend/ha_admin.py mark-ready --operation-id epoch-ready-00000001
   python backend/ha_admin.py mark-ready --operation-id epoch-ready-00000001 --apply
   ```

7. Restart normally and verify `/ready`, metrics, management login/OIDC (if enabled), inference,
   quota, audit, and usage evidence.

`read_epoch` never provisions state. Initial epoch creation is an explicit binding-bootstrap
operation for a deployment with no durable binding and no Redis binding marker. If either binding
already exists while the epoch/initialization pair is missing or partial, stop: this is namespace
loss, not a bootstrap opportunity.

Re-running a command with the same operation ID is safe. Reconciliation only accepts one exact
epoch step and writes the shared binding before the durable binding so an interrupted operation can
resume without ambiguity. Shared binding and drain records use closed canonical JSON so the same
bytes round-trip through Redis and the in-memory reference store.

## Rollback to supported standalone mode

`python backend/ha_admin.py rollback-plan` returns the immutable target: standalone, one worker,
one replica, durable authority preserved. It performs no mutation and refuses to produce a plan
unless the current binding still matches the complete signed reconciliation receipt.

1. Drain coordinated admission and preserve both backends for forensics/recovery.
2. Stop all coordinated replicas.
3. Remove coordinated-only environment values, set `OMNI_RUNTIME_MODE=standalone`, `WORKERS=1`,
   and `OMNI_REPLICA_COUNT=1`; keep the same external durable backend if healthy.
4. Start exactly one process. Do not delete Redis or migrate durable authority automatically.
5. Verify health/readiness, owner recovery, audit continuity, usage completeness, and a synthetic
   inference request before reopening traffic.

Rollback may conservatively lose short-lived in-flight routing/cache convenience state. It must
not lose durable identity, audit, usage, or hard-budget evidence. If those checks fail, keep traffic
closed and restore the durable backup rather than resetting state.
