# Omni Gateway Enterprise Overhaul — Current Execution State

## Resume Here

- Updated: 2026-08-24 (Asia/Saigon).
- Branch: `codex/enterprise-overhaul`.
- Implementation baseline: `55dfce4 feat: connect audit repositories to storage backends`.
- Completed scope: Waves 1–2 / Phases 0–3, plus Wave 3 slices W3.1–W3.2.
- Original program progress: 14/28 approved checklist items complete (including specification
  approval), exactly 50%; Wave 2 execution-slice checkboxes are refinements and are not added
  to that denominator.
- Active scope: Wave 3 — Access and Operational Evidence; W3.3 mutation coverage is next.
- Control state: **IMPLEMENTING — WAVE 3**.
- Expected worktree state at this checkpoint: clean after the W3.2 documentation commit.
- Expected runtime: one Omni Gateway listener on `http://127.0.0.1:4283`; `/health` and `/ready`
  return HTTP 200.
- Last verified full suite: 562 tests passed; Ruff check, compileall, focused W3.2 format, and
  diff-check passed. The repository-wide format check still reports 16 pre-existing Wave 2 files
  that differ from the currently installed Ruff formatter; they remain isolated from the W3.2
  implementation commits.

Wave 2 was accepted and pushed by the human on 2026-08-24. Wave 3 / Phases 4–5 was approved for
implementation on the same date. Do not expand into Phase 6 or release activation.

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
- W2.8 evidence: all-matching batch requests resolve normalized filters against fresh fleet data,
  retain the 100-target cap, and reject expired selections or previews made stale by fleet changes;
  provider catalog capabilities now drive a fail-closed operation intersection in the toolbar.
  Preview precedes explicit confirmation, while execution returns localized bounded per-item
  outcomes and recovery guidance. Non-Antigravity tiers are explicitly not applicable rather than
  being mislabeled as Pro.
- W2-B evidence: 522 tests passed with mixed-provider, 101-target, stale-preview, tamper, and
  secret-exclusion fixtures; Ruff, compileall, every frontend JavaScript file, and diff-check passed.
  PID 3800 is the only listener on port 4283 and health/ready return 200. Real-browser checks found
  no horizontal overflow at 360/768/1024/1440, verified 2/3/5-column responsive filters,
  light/dark/system themes, bounded URL filter restoration, semantic controls/focus styling, and
  curated Vietnamese, English, and Simplified Chinese fleet copy; observed management requests
  returned 200.
- W2.9 evidence: one declarative manifest now covers all 37 editable fields across the nine console
  provider variants. It defines input type, required state, bounds, autocomplete, secret lifetime,
  environment locks, help, advanced status, validation, and reset behavior; runtime helpers apply
  the contract without browser persistence. Static audits enforce coverage, labels, secret safety,
  and a curated 15-locale catalog. The full suite reached 528 tests.
- W2.10 evidence: Google AI Studio and Google Antigravity now consume shared validation,
  environment-lock, help, and transient-secret reset behavior. Endpoint inputs use bounded URL
  semantics, callback content is cleared after submission, and Antigravity client secrets are no
  longer reflected by GET, save, or reset responses; a configured-state marker preserves unchanged
  secrets safely. Focused response-contract and form audits passed; the full suite reached 532 tests.
- W2.11 evidence: OpenAI Platform, Codex, Grok Build, SpaceXAI Console, Claude Code, Claude
  Platform, and Ollama now use the same declarative validation, environment-lock, generated help,
  and transient-secret lifecycle. Provider-specific API-key bounds remain aligned with backend
  request models. xAI metadata moved out of the Google AI Studio script, removing an implicit load-
  order dependency. Provider, locale, and syntax audits passed; the full suite reached 534 tests.
- W2-C evidence: all 534 tests, Ruff, compileall, every frontend JavaScript syntax check, and
  diff-check passed. The final checkpoint service restarted as the only listener and health/ready
  returned 200. Authenticated browser checks verified no horizontal overflow at 360/768/1024/1440, 23
  generated field-help nodes with ARIA associations, correct light/dark/system rendering,
  Vietnamese/English/Simplified-Chinese live locale changes, masked/empty Antigravity secret state,
  provider-specific secret bounds, and ArrowRight focus/selection from Antigravity to AI Studio;
  the browser console was empty. English literal leaks discovered in advanced provider forms were
  corrected before closing this checkpoint.
- W3.1 evidence: the versioned immutable audit contract now validates actor/action/target/outcome
  vocabularies, HMAC-redacts actor and target identifiers before the repository boundary, bounds
  change summaries and retention/query inputs, provides exact fingerprint filters, and signs
  opaque cursors against tampering. The repository protocol exposes append, query, and policy-
  driven prune only—never individual update/delete. Two RED cycles proved the missing module and
  direct-construction redaction bypass before implementation; 8 focused tests and all 542 tests
  passed.
- W3.2 evidence: additive, append-only audit repositories now exist for SQLite (`c722f9b`),
  PostgreSQL (`343903d`), and MongoDB (`bdf766f`). All three enforce unique event IDs, stable
  newest-first ordering, exact bounded filters, signed cursor pagination, strict stored-record
  revalidation, and policy-only age/count pruning. SQL writes and filters are parameterized;
  PostgreSQL prunes transactionally; MongoDB deliberately has no TTL index so records cannot be
  deleted outside the explicit retention policy. Commit `55dfce4` exposes the selected repository
  through the existing storage adapter without persisting its cursor-signing key. Backend parity,
  restart persistence, UTC boundaries, duplicate normalization, corrupted-record failure, and
  uninitialized fail-closed behavior are covered; all 562 tests passed with Ruff and compileall
  clean.

## Approved vs. Proposed Scope

### Already approved and complete

- Everything checked in Phases 0–2 of `tasks/todo.md`.

### Approved and complete

- Wave 2 slices W2.1–W2.11 in `tasks/plan.md`.
- Phase 3 completion: provider capability contract, safe single/batch operations, fleet filtering,
  contextual toolbar, and complete provider-form audit.
- Minimal credential-scoped audit and operation telemetry foundations required to make new batch
  mutations diagnosable and safe.

### Approved and active

- Wave 3 slices W3.1–W3.12 in `tasks/plan.md`.
- Phase 4: complete audit coverage, durable audit storage, virtual-key governance, reservation-
  aware enforcement, and the Access lifecycle.
- Phase 5: bounded request traces, Observability separation, health/SLO views, safe exporters,
  alert rules, and runbooks.

### Explicitly not approved yet

- Phase 6 RBAC/OIDC, Redis coordination, durable HA migration, or multiple workers/replicas.
- Phase 7 release activation, production deployment, or destructive migration.

Foundations borrowed from Phase 4 or Phase 5 remain partial and must not cause those phase
checkboxes to be marked complete.

## Wave 3 Checkpoint Protocol

1. W3-A: append-only audit contract, durable repositories, full mutation coverage, query/export,
   and audit console.
2. W3-B: scoped virtual keys, atomic rate/budget reservations, safe lifecycle, and Access page.
3. W3-C: bounded request traces, trace/raw-log separation, health/SLOs, exporters, alerts, and
   runbooks.
4. At each checkpoint: focused tests, full regression tests, Ruff/compile/JS/i18n gates, diff and
   secret review, atomic commit, clean worktree, and runtime smoke when applicable.
5. Browser-facing checkpoints require 360/768/1024/1440 widths, light/dark/system themes,
   representative locales, keyboard/accessibility verification, and clean console/network.
6. At the Wave 3 boundary: restart from the committed checkpoint, verify health, report evidence,
   and pause for human acceptance before Wave 4.

## Immediate Next Action

Implement W3.3 incrementally against the committed W3.2 repositories: define the management-
mutation coverage matrix first, add one fail-closed audit service boundary with request/actor
correlation, then instrument every authenticated management mutation with redacted success and
failure evidence. Do not add query/export routes or the audit console until W3.3 passes and is
committed.

## Update Rule

Update this file whenever a checkpoint is committed, a blocker changes, scope is approved, or a
verification claim changes. Keep only current handoff state here; durable product decisions belong
in the spec or an ADR, and granular completion belongs in `tasks/todo.md`.
