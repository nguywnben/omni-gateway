# HA lifecycle, reconciliation, and rollback

## Safety boundary

The coordinated implementation is present, but W4.19 produced no activation record because the
required external failure/load topology was unavailable and correctness blockers remain.
`REDIS_URL` alone never enables HA. Keep
`OMNI_RUNTIME_MODE=standalone`, `WORKERS=1`, and one replica unless the running release contains an
accepted activation record for the exact documented topology.

Back up the selected durable backend and Redis namespace before any planned transition. Never use
`FLUSHDB`, `FLUSHALL`, `SCRIPT FLUSH`, wildcard deletion, manual epoch edits, or direct binding
record edits.

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

4. Update only `OMNI_COORDINATION_EPOCH` to the returned epoch, then preview/apply bounded binding
   reconciliation:

   ```text
   python backend/ha_admin.py reconcile
   python backend/ha_admin.py reconcile --apply
   ```

5. After durable authority and backups are independently verified, mark the exact epoch ready with
   another stable operation ID:

   ```text
   python backend/ha_admin.py mark-ready --operation-id epoch-ready-00000001
   python backend/ha_admin.py mark-ready --operation-id epoch-ready-00000001 --apply
   ```

6. Restart normally and verify `/ready`, metrics, management login/OIDC (if enabled), inference,
   quota, audit, and usage evidence.

Re-running a command with the same operation ID is safe. Reconciliation only accepts one exact
epoch step and writes the shared binding before the durable binding so an interrupted operation can
resume without ambiguity.

## Rollback to supported standalone mode

`python backend/ha_admin.py rollback-plan` returns the immutable target: standalone, one worker,
one replica, durable authority preserved. It performs no mutation.

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
