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
- Control state: **IN PROGRESS — W2.8**.
- Expected worktree state at this checkpoint: W2.7 changes staged for an atomic commit.
- Expected runtime: Omni Gateway PID 1364 on `http://127.0.0.1:4283`; `/health` and `/ready`
  return HTTP 200.
- Last verified full suite: 515 tests passed; focused Ruff, compileall, and diff-check passed.

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
- W2.2 evidence: the authenticated provider catalog exposes typed additive variant/operation
  metadata without changing existing provider records; 475 full-suite tests passed.
- W2.3 evidence: single-credential verify, test, quota, toggle, delete, export, and credit-mode
  operations are checked against the exact server-side variant contract before side effects;
  unknown variants fail closed with a stable secret-free error; 480 full-suite tests passed.
- W2.4 evidence: the existing batch route now has a typed additive contract with a 100-target
  bound, side-effect-free expiring previews, fresh capability evaluation, per-item outcomes and
  timeouts, duplicate handling, and concurrency-safe idempotency reservations; the 1.x client uses
  the new handshake; 497 full-suite tests passed.
- W2.5 evidence: credential fleet mutations emit one schema-versioned, correlated, allowlisted
  event per target; HMAC fingerprints replace names, raw failure details are withheld, retention is
  bounded, idempotent retries do not duplicate events, and Prometheus exposes fixed-cardinality
  outcome counters and duration histograms; 508 full-suite tests passed.
- W2-A evidence: committed checkpoint `7b2fbc2` restarted as the only listener on port 4283;
  `/health`, `/ready`, and `/metrics` returned HTTP 200; credential operation counter/histogram
  families were present; the real Vietnamese login shell had a clean browser console and no
  horizontal overflow at 360/768/1024/1440 widths.
- W2.6 evidence: credential status queries now compose exact provider variant, credential kind,
  health, cooldown, quota state, tier, source, status, error, and preview filters before stable
  sorting/pagination; responses expose safe facets and a bounded five-minute opaque all-matching
  token that retains only normalized filters. Empty, 125-record, changing-data, invalid, conflict,
  tamper, cross-mode, and secret-exclusion tests passed; the full suite reached 515 tests.
- W2.7 evidence: pool filters use explicit responsive controls for credential kind, health, quota
  state, and source; allowlisted filter/page-size state persists in URL and a 512-byte bounded
  session record without credential names; page selection and opaque all-matching selection are
  distinct, clearable states. All 15 supported locales received curated fleet copy, frontend
  locale/asset tests passed, and changed JavaScript files passed syntax checks.

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

Implement W2.8 with test-first evidence: resolve all-matching tokens into freshly evaluated bounded
batches, compute the contextual operation intersection, and present preview/per-item recovery
results with explicit destructive confirmation.

## Update Rule

Update this file whenever a checkpoint is committed, a blocker changes, scope is approved, or a
verification claim changes. Keep only current handoff state here; durable product decisions belong
in the spec or an ADR, and granular completion belongs in `tasks/todo.md`.
