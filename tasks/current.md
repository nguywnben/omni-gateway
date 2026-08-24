# Omni Gateway Enterprise Overhaul — Current Execution State

## Resume Here

- Updated: 2026-08-24 (Asia/Saigon).
- Branch: `codex/enterprise-overhaul`.
- Implementation baseline: `39fb9da feat: record AI quality decision telemetry`.
- Completed scope: Wave 1 / Phases 0–2.
- Original program progress: 10/28 approved checklist items complete (including specification
  approval), approximately 36%; Wave 2 execution-slice checkboxes are refinements and are not added
  to that denominator.
- Active scope: Wave 2 — Credential Operations.
- Control state: **IN PROGRESS — W2.2**.
- Expected worktree state at this checkpoint: clean after the latest checkpoint commit.
- Expected runtime: Omni Gateway on `http://127.0.0.1:4283`, `/health` returns HTTP 200.
- Last verified full suite: 473 tests passed; Ruff, compileall, and diff-check passed.

Wave 2 was approved by the human on 2026-08-24. Do not expand beyond its documented scope.

## Authoritative Reading Order

1. `docs/specs/enterprise-overhaul.md` — product scope, boundaries, success criteria.
2. `docs/decisions/004-versioned-ai-quality-policy-plane.md` — AI Quality policy.
3. `docs/decisions/005-provider-operation-capabilities.md` — Wave 2 operation contract.
4. `docs/decisions/006-durable-and-coordinated-enterprise-state.md` — state and HA boundary.
5. `tasks/plan.md` — delivery waves, dependencies, detailed execution slices.
6. `tasks/todo.md` — authoritative checkboxes.
7. This file — latest handoff state, evidence, and immediate next action.
8. `git status`, `git log`, and the actual test/runtime output — final verification of all claims.

If documents conflict, accepted ADRs and the approved spec constrain the plan; current repository
state and test evidence constrain this handoff. Stop and surface an unresolved conflict instead of
silently choosing a new design.

## Completed Evidence

### Wave 1 — Policy and console foundation

- Phase 0: policy-plane, provider capability, and enterprise state ADRs accepted.
- Phase 1: light/dark/system theme, navigation ownership, keyed localization, and literal-leak
  gates delivered.
- Phase 2: versioned AI Quality policy, management API, runtime activation, structural token
  compression safety, decision telemetry, and AI Quality console delivered.
- Latest implementation checkpoint: `39fb9da`.
- Repository quality evidence at that checkpoint: 470 tests passed; Ruff and compileall clean.
- Service restart evidence: `/health` returned HTTP 200 after the checkpoint restart.
- W2.1 evidence: all nine console credential variants have an exact, fail-closed operation
  inventory; 473 full-suite tests passed before its checkpoint commit.

## Approved vs. Proposed Scope

### Already approved and complete

- Everything checked in Phases 0–2 of `tasks/todo.md`.

### Approved and active

- Wave 2 slices W2.1–W2.11 in `tasks/plan.md`.
- Phase 3 completion: provider capability contract, safe single/batch operations, fleet filtering,
  contextual toolbar, and complete provider-form audit.
- Minimal credential-scoped audit and operation telemetry foundations required to make new batch
  mutations diagnosable and safe.

### Explicitly not approved yet

- Full Phase 4 audit coverage and virtual-key governance.
- Full Phase 5 request traces, Observability console, SLOs, and alerting.
- Phase 6 RBAC/OIDC, Redis coordination, durable HA migration, or multiple workers/replicas.
- Phase 7 release activation, production deployment, or destructive migration.

Foundations borrowed from Phase 4 or Phase 5 remain partial and must not cause those phase
checkboxes to be marked complete.

## Wave 2 Checkpoint Protocol

1. W2-A: capability contract, single/batch operation service, preview, redacted evidence.
2. W2-B: faceted backend query, persistent selection/filter UX, contextual operation toolbar.
3. W2-C: shared provider form contract and all provider-family corrections.
4. At each checkpoint: focused tests, full regression tests, Ruff/compile/JS/i18n gates, diff and
   secret review, atomic commit, clean worktree, and runtime smoke when applicable.
5. Browser-facing checkpoints require 360/768/1024/1440 widths, light/dark/system themes,
   representative locales, keyboard/accessibility verification, and clean console/network.
6. At the Wave 2 boundary: restart from the committed checkpoint, verify health, report evidence,
   and pause for human acceptance before Wave 3.

## Immediate Next Action

Implement W2.2 with test-first evidence: expose the authenticated additive capability catalog
contract without changing existing provider fields.

## Update Rule

Update this file whenever a checkpoint is committed, a blocker changes, scope is approved, or a
verification claim changes. Keep only current handoff state here; durable product decisions belong
in the spec or an ADR, and granular completion belongs in `tasks/todo.md`.
