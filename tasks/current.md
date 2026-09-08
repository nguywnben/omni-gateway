# Omni Gateway — Current State

## Resume Here

- Updated: 2026-09-08 (Asia/Saigon)
- Active plan: `PROD-SELFHOST-R1`
- Target: production-quality self-hosting for one person or a trusted team, not enterprise service
  operation.
- Progress: **2/36 implementation tasks**; Phase 0 is 2/6 complete.
- Completed: **P0.2 — Product terminology and navigation inventory**.
- Next task: **P0.3 — Isolate unfinished HA work**.
- Supported runtime today: standalone, one worker, one replica.
- Redis coordination, multi-replica HA, and Helm are experimental and no longer R1 release blockers.

## Why the Plan Was Reset

The prior enterprise plan delivered substantial credential, audit, access, identity, storage, and
coordination work, but its Wave 4 HA closure expanded repeatedly and over-weighted distributed
failure evidence relative to the needs of a personal/small-team self-hosted product. Completed code
is preserved. Unfinished enterprise activation is frozen rather than allowed to keep changing the
release denominator.

## Authoritative Reading Order

1. `CONSTRAINTS.md`
2. `docs/audits/production-baseline-2026-09-08.md`
3. `docs/specs/production-self-hosted.md`
4. `tasks/plan.md`
5. `tasks/todo.md`
6. `git status` and recent commits

Historical enterprise specs, ADRs, evidence, and git history remain useful context but cannot
override the current product boundary or completion rules.

## Working Tree Caution

Before starting P0.1, inspect the working tree and preserve any unrelated user-owned changes. Plan
documents should be committed separately after approval. Do not push unless the user requests it.

## Fixed Verification Cadence

- Task: focused tests only.
- Phase: affected integration/browser gate once.
- Release candidate: full required gate once; rerun failed slices before another full pass.
- No HA topology matrix in R1.
- No cross-model review except one security pass for backup/restore or final auth/security closure,
  unless the user explicitly requests another.

## Latest Evidence

- `docs/evidence/p0.2-product-surface-inventory.md`
- Checked inventory: 11 pages/tabs, 134 OpenAPI operations, 24 Settings controls, 123 example
  environment variables, 16 advertised claims, and explicit locale ownership.
- Product copy now presents the fixed Core/Advanced/Compatibility/Experimental self-host boundary in
  both curated languages; Redis coordination and Kubernetes/Helm are explicitly experimental.
- P0.2 focused console/localization gate: 53 tests passed; all four localization audits passed.
- `docs/evidence/p0.1-capability-registry.md`
- Default runtime snapshot: 31 capabilities; only Core entries are active.
- Focused contract/runtime matrix: 45 tests passed.
- Full backend gate: 1,522 tests run; 1,468 passed and 54 existing optional/live-backend cases
  skipped.
- Ruff, compileall, runtime HTTP projection, and whitespace checks passed.
