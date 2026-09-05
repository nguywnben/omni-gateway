# Omni Gateway Enterprise Overhaul — Current Execution State

## Resume Here

- Updated: 2026-09-05 (Asia/Saigon).
- Branch: `codex/enterprise-overhaul`.
- Latest committed evidence checkpoint: current `HEAD` (current HA blocker projection); Quota State
  v2 hardening is `69616a2`.
- Original program progress: 24/28 approved checklist items complete (85.7%). Wave execution-slice
  checkboxes refine those items and are not added to the denominator.
- Control state: **W4 LOCAL ENGINEERING COMPLETE; CHECKPOINT W4-C / HA ACTIVATION BLOCKED BY
  EXTERNAL TOPOLOGY EVIDENCE**.
- Supported runtime: standalone, one worker, one replica. OIDC remains disabled by default.
- Worktree and committed-runtime state must be rechecked after the final evidence commit.

## Wave 4 Delivered

- Explicit viewer/operator/security-admin/owner RBAC, disabled-by-default enterprise OIDC,
  revocable sessions, owner recovery, complete permission/audit coverage, and the localized
  Identity console.
- Selected-backend durable identity, usage, trace, audit, and hard-budget authority across SQLite,
  PostgreSQL, and transaction-capable MongoDB boundaries.
- Typed in-memory/Redis coordination for sessions, attempts, OIDC and provider authorization,
  device leases, routing leases/cooldowns, quotas, invalidation, cache metadata, conversation state,
  credential batches, and bounded admission registries.
- Storage-owned atomic credential identity mutation and encrypted 256-entry preview/idempotency
  domains with typed overload/outage behavior.
- A fail-closed HA lifecycle with persistent binding, fencing epoch, coordinated readiness,
  drain/advance/reconcile/mark-ready commands, one-replica deployment guards, alerts, runbooks,
  and rollback planning.
- Quota State v2: a 61-slot conservative RPM/TPM window, durable-ledger-only monetary budgets,
  direct lifecycle lookup, bounded cleanup, versioned markers, and resumable reconciliation.

## Final Local W4 Evidence

- Focused Quota State v2 and HA matrix: 164 passed; seven live Redis tests skipped explicitly.
- Full backend discovery: 1,320 passed; 30 opt-in live-backend tests skipped explicitly.
- A 100,000-retained-record target and a small target both inspect exactly one lifecycle record and
  61 rate buckets. No production quota mutation contains lifecycle-hash `HGETALL` or a per-record
  `ZSCORE` loop.
- Ruff lint/format, compileall, `pip check`, PyPI vulnerability audit, strict YAML, Compose config,
  45 JavaScript syntax checks, four i18n audits, and whitespace checks pass.
- All 1,116 referenced console keys remain populated across all 15 locales.
- Review hardening covers valid v1 chronology, marker TTL/order, cursor canonicality, input/count
  bounds, duplicate scan candidates, exact pipeline replies, and authoritative ready confirmation.
- The synthetic HA evidence tool now reports only the remaining external-topology blocker instead
  of the four historical blockers from its original W4.19 snapshot.

## Activation Disposition

The former process-local provider, batch, pool-mutation, batch-capacity, and quota O(n) blockers are
closed in code. The only retained blocker is the required real Redis plus shared PostgreSQL/MongoDB
two-replica matrix: partition/restart, audit and usage completeness, load/latency objectives, and
rollback. Docker Desktop is installed but its Linux daemon did not become available on this host;
`OMNI_TEST_REDIS_URI` is also absent.

The 2026-09-05 Docker preflight localized the host failure: Docker Desktop 4.81.0 exits while WSL
commands time out and its `dockerInference` AF_UNIX socket cannot be removed. Windows reports no
`vmcompute` or `hns` service, and non-elevated feature inspection cannot proceed. The stale socket
was not deleted and Docker data was not reset. Microsoft requires an administrator to enable the
WSL and Virtual Machine Platform optional features and restart Windows before WSL 2 can run.

Consequently:

- Checkpoint W4-C and the Phase 6 failure/load item remain unchecked;
- `SUPPORTED_HA_ACTIVATION_RECORDS` remains empty;
- `WORKERS=1`, `OMNI_REPLICA_COUNT=1`, and Helm `replicaCount: 1` remain enforced;
- skipped/unavailable evidence is not a pass;
- Wave 5 must not start until the human accepts the W4 disposition or the topology gate is supplied.

Separately, Phase 7 should migrate seven remaining Pydantic v2 class-based `Config` declarations to
`ConfigDict` before Pydantic v3. This is not an HA activation blocker.

## Immediate Next Action

From an Administrator PowerShell, enable `Microsoft-Windows-Subsystem-Linux` and
`VirtualMachinePlatform`, then restart Windows. After restart, verify `wsl --status` and Docker
daemon health. Provision Redis plus shared PostgreSQL or MongoDB with two application replicas and
run the ADR-008 partition/restart/load/completeness/rollback matrix. If every target passes, create
and review one immutable activation record, raise only the documented topology ceiling, check W4-C,
and obtain human acceptance. Otherwise keep standalone operation supported.

## Authoritative Reading Order

1. `docs/specs/enterprise-overhaul.md`
2. `docs/specs/enterprise-identity-and-ha.md`
3. `docs/decisions/007-explicit-rbac-and-oidc-identity.md`
4. `docs/decisions/008-gated-high-availability-activation.md`
5. `docs/specs/ha-runtime-lifecycle.md`
6. `docs/specs/coordination-store.md`
7. `docs/superpowers/specs/2026-09-04-redis-quota-state-v2-design.md`
8. `docs/superpowers/plans/2026-09-04-redis-quota-state-v2.md`
9. `docs/evidence/w4.19-ha-activation-disposition.md`
10. `docs/reviews/w4c-coordination-blocker-review.md`
11. `tasks/todo.md`
12. `git status`, `git log`, and current verification output

If records conflict, accepted ADRs constrain the implementation and current repository evidence
constrains every completion claim. Skipped or unavailable evidence is never a pass.
