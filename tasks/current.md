# Omni Gateway Enterprise Overhaul — Current Execution State

## Resume Here

- Updated: 2026-09-04 (Asia/Saigon).
- Branch: `codex/enterprise-overhaul`.
- Last committed implementation checkpoint: `e02ff71` (W4.18-W4.19.2).
- Workspace scope complete: W4.18 lifecycle, W4.19 HA evidence/disposition, and the local W4-C
  process-local-state and bounded-capacity blocker closure.
- Original program progress: 24/28 approved checklist items complete (85.7%). Wave execution-slice
  checkboxes refine those items and are not added to the denominator.
- Control state: **W4-C BLOCKER CLOSURE IN PROGRESS; HA ACTIVATION DENIED**.
- Supported runtime: standalone, one worker, one replica. OIDC remains disabled by default.
- Current runtime: committed `e02ff71` is running on `http://127.0.0.1:4283`; health/readiness
  returned HTTP 200, including storage, usage-ledger, and coordination checks. The authenticated
  Vietnamese dashboard, audit, and request-trace pages loaded without console errors or horizontal
  overflow at a 451-pixel viewport.
- Worktree is clean at the recorded checkpoint after this progress-ledger commit.

## What W4.18 Delivered

- A closed `standalone`/`coordinated` runtime policy. Coordinated mode requires Redis, shared
  PostgreSQL or MongoDB durable authority, a stable HMAC key/namespace/epoch, exact persistent
  binding, and a compiled activation record.
- One lifecycle-owned coordination service injected into sessions, attempts, OIDC transactions,
  routing, quota, governance invalidation, exact-cache metadata, and primary conversation steps.
- HMAC-addressed, schema-closed, epoch-fenced primary session CAS; dependency loss and corrupt state
  fail closed.
- Dependency-aware readiness and bounded HA metrics.
- Dry-run-first status, drain, epoch advance, reconciliation, mark-ready, and rollback-plan CLI.
- Compose/Helm configuration, one-replica render guard, secret references, 45-second termination
  grace, alerts, and the HA lifecycle runbook.
- Coordinated MongoDB disables the legacy unnamespaced Redis cache so `REDIS_URL` cannot mix cache
  data with the coordination namespace.

The internal review and exact fixes are in `docs/reviews/w4.18-adversarial-review.md`.

## W4.19 Evidence and Decision

- Full backend suite: 1,254 passed, 30 opt-in live-backend skips.
- W4.18 focused matrix: 184 passed.
- W4.19 focused lifecycle/evidence/deployment matrix: 28 passed.
- Synthetic 256-operation matrix: zero duplicate transitions, stale epoch denied, coordination
  failure closed, and recovery after reconciliation succeeded. The executable marks these results
  as non-activation evidence.
- Repository gates: Ruff lint/format, compileall, `pip check`, PyPI vulnerability audit, strict YAML
  lint, Compose config, diff, 45 JavaScript syntax checks, and four i18n audits pass.
- Locale coverage: all 1,116 referenced keys are present in all 15 console locales; backend
  management literals are catalog-connected.
- Unavailable on this host: live Redis URI, Docker daemon/container topology, Helm renderer, and a
  functioning Git-for-Windows Bash runtime.

Activation was correctly denied. `SUPPORTED_HA_ACTIVATION_RECORDS` is empty, `WORKERS=1`,
`OMNI_REPLICA_COUNT=1`, and Helm `replicaCount: 1` remain enforced. The authoritative record is
`docs/evidence/w4.19-ha-activation-disposition.md`.

## Post-W4.19 Blocker Closure

- Claude/xAI authorization now stores AES-GCM-encrypted PKCE state in the shared, fenced one-time
  transaction primitive. Provider binding, atomic consumption, replay, expiry, cross-client use,
  stale epoch, capacity, and dependency failure are tested.
- Codex device authorization now uses an encrypted CAS lease with immutable absolute expiry,
  single-poller ownership, release-on-pending, takeover only after lease expiry, and terminal secret
  erasure before token exchange.
- Credential batch previews and idempotency now use encrypted shared CAS. Large responses are
  compressed into bounded chunks and published through one digest-bound root transition. Exact
  ownership is checked before every mutation; an unknown post-mutation failure cannot release the
  reservation and permit unsafe replay.
- Credential upsert and deduplication now plan and commit against one storage-owned snapshot using
  SQLite writer transactions, PostgreSQL table locking, or a MongoDB transaction-conflict gate.
  The former process-local pool locks are gone.
- Preview and idempotency each enforce an encrypted 256-live-entry HMAC admission registry using
  coordination time. Completion retains replay capacity, release reclaims it, overload returns
  HTTP 429 with retry guidance, and dependency loss returns a typed HTTP 503 envelope.
- Full backend suite: 1,285 passed, 30 opt-in live-backend skips. Backend Ruff lint/format,
  compileall, diff checks, `pip check`, and a 63-test affected matrix pass. No dependency,
  deployment, frontend, or locale asset changed in W4.19.2, so their earlier clean gates remain the
  latest evidence rather than being falsely reported as rerun.

The implementation review is `docs/reviews/w4c-coordination-blocker-review.md`.

## Retained HA Blockers

1. Worst-case Redis quota transition cost at the 100,000-record ceiling has no live measurement.
2. Redis plus shared database, two-replica partition/restart, durable audit/usage completeness, and
   rollback evidence did not run.

These blockers prevent the remaining Phase 6 failure/load item and W4-C from being marked complete.
They do not weaken the safe standalone release.

Separately, Phase 7 should migrate seven remaining Pydantic v2 class-based `Config` declarations to
`ConfigDict` before Pydantic v3. This pre-existing deprecation is not an HA activation blocker and
did not fail the supported test suite.

## Immediate Next Action

1. Redesign or measure the worst-case Redis quota transition at the 100,000-record ceiling.
2. Run the required external
   two-replica topology and rollback matrix when infrastructure is available.
3. Do not enter Wave 5, raise worker/replica limits, populate an activation record, enable OIDC, or
   mutate production data without a separate accepted plan and required evidence.

## Authoritative Reading Order

1. `docs/specs/enterprise-overhaul.md`
2. `docs/specs/enterprise-identity-and-ha.md`
3. `docs/decisions/007-explicit-rbac-and-oidc-identity.md`
4. `docs/decisions/008-gated-high-availability-activation.md`
5. `docs/specs/ha-runtime-lifecycle.md`
6. `docs/evidence/w4.19-ha-activation-disposition.md`
7. `docs/reviews/w4.18-adversarial-review.md`
8. `docs/reviews/w4.19-adversarial-review.md`
9. `docs/specs/provider-authorization-coordination.md`
10. `docs/specs/credential-batch-coordination.md`
11. `docs/specs/credential-pool-atomic-mutation.md`
12. `docs/reviews/w4c-coordination-blocker-review.md`
13. `docs/superpowers/plans/2026-09-04-w4c-credential-mutation-capacity.md`
14. `tasks/todo.md`
15. `git status`, `git log`, and current verification output

If records conflict, accepted ADRs constrain the implementation and current repository evidence
constrains every completion claim. Skipped or unavailable evidence is never a pass.
