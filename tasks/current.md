# Omni Gateway Enterprise Overhaul — Current Execution State

## Resume Here

- Updated: 2026-08-24 (Asia/Saigon).
- Branch: `codex/enterprise-overhaul`.
- Implementation baseline: `9d581ae feat: add audit operations console`.
- Completed scope: Waves 1–2 / Phases 0–3, Wave 3 slices W3.1–W3.4, and the W3.5
  implementation. W3.5 remains unchecked until its real-browser matrix passes.
- Original program progress: 14/28 approved checklist items complete (including specification
  approval), exactly 50%; Wave 2 execution-slice checkboxes are refinements and are not added
  to that denominator.
- Active scope: Wave 3 — Access and Operational Evidence; verify W3.5 and close W3-A.
- Control state: **VERIFYING — CHECKPOINT W3-A**.
- Expected worktree state at this checkpoint: clean after the W3.5 documentation commit.
- Expected runtime: one Omni Gateway listener on `http://127.0.0.1:4283`; `/health` and `/ready`
  return HTTP 200.
- Last verified full suite: 603 tests passed; Ruff lint/format, compileall, pip dependency
  consistency, pip-audit, all 38 JavaScript syntax checks, and diff-check passed. The 14 remaining
  Wave 2 formatter differences were normalized mechanically in commit `1abbb15`; the repository-
  wide formatter gate is now clean. Runtime `/audit`, `/health`, and `/ready` return HTTP 200.

Wave 2 was accepted and pushed by the human on 2026-08-24. Wave 3 / Phases 4–5 was approved for
implementation on the same date. Do not expand into Phase 6 or release activation.

The W3.5 real-browser gate is currently tooling-blocked: the selected in-app browser rejects both
`localhost:4283` and `127.0.0.1:4283` with `ERR_BLOCKED_BY_CLIENT`, while no connected Chrome
browser is available. This does not indicate an application HTTP failure—the same routes return
200 in runtime smoke tests—but it prevents honest claims about 360/768/1024/1440 layout, keyboard,
accessibility tree, theme, console/network, and secret lifetime. Do not mark W3.5 or W3-A complete
until those checks run in a connected real browser.

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
- W3.3 evidence: commit `d42ba90` adds a declarative coverage gate for all 57 control-plane write
  routes. Fifty durable mutations resolve through one correlated response boundary, single/batch
  credential actions bridge the existing per-target W2 evidence without duplicating idempotent
  retries, and the five remaining preview/OAuth-start routes are explicitly proven side-effect
  free. Actor, action, target, outcome, and change vocabularies are allowlisted; semantic provider,
  credential, key, configuration, and model targets are HMAC-redacted before append. A generated
  internal master key persists across restart and derives separate fingerprint/cursor keys without
  entering management config responses. Startup fails closed if audit cannot initialize, while
  append outages are surfaced with secret-free critical evidence. Commit `7024f4e` resolves targets
  before route execution. All 577 tests, Ruff, compileall, and diff-check passed. Runtime smoke found
  and removed stale PID 3540, then verified PID 11312 as the only listener; health/ready returned
  200 and request `w3-committed-smoke` persisted one `auth.logout` success event in SQLite.
- W3.4 evidence: commits `a274a5b`, `bf74e17`, and `6c6e541` add a strict durable retention
  policy service, authenticated audit query/retention routes, and bounded JSONL/CSV export.
  Repeated exact filters cover time, actor, action, target, outcome, and request ID; pages use
  signed opaque cursors and a 200-event maximum. Retention is persisted before exact policy prune
  and commit `cb2bd95` enforces it after every append. Exports reject rather than truncate above
  10,000 events or 8 MiB, CSV cells are formula-safe, filenames are server-generated, and only
  redacted event records cross the response boundary. Successful exports append correlated
  `audit.export` evidence before release. Fresh review commit `f49a5a6` added typed OpenAPI
  responses, CSV-header byte enforcement, and fail-closed startup ordering. All 596 tests passed;
  Ruff, compileall, focused format, pip consistency, 36 JavaScript syntax checks, and diff-check
  are clean. The maintained API contract is `docs/audit-api.md`.
- W3.5 implementation evidence: commit `9d581ae` adds `/audit` under an Observability navigation
  group with exact action/actor/target/outcome/time/request/fingerprint filters, session-only
  opaque cursor history, redacted event detail, request-ID copy/pivot, confirmed retention updates,
  and bounded JSONL/CSV downloads. Only category filters and page size enter local storage. The
  client strictly revalidates all 11 event fields and vocabulary values, renders untrusted records
  with `textContent`, allowlists export filenames, and cancels stale queries so older responses
  cannot replace newly filtered evidence. A dedicated keyed catalog supplies curated copy for all
  15 supported locales. Static contracts forbid sensitive fields and unsafe DOM insertion; all 603
  tests, Ruff lint/format, compileall, pip consistency, vulnerability audit, 38 JavaScript syntax
  checks, and runtime audit/health/readiness smoke tests pass. The real-browser matrix remains the
  only open W3.5/W3-A gate due to the browser tooling limitation recorded above.

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

Connect a controllable Chrome browser (or another real-browser surface that can reach loopback),
then verify W3.5 at 360/768/1024/1440 widths, light/dark/system themes, representative live locale
changes, keyboard/dialog focus, accessibility relationships, clean console/network, and absence of
credential/plaintext-key content in the DOM. Mark W3.5 and W3-A complete only after that evidence
is recorded and committed. Do not begin W3.6 before the checkpoint closes.

## Update Rule

Update this file whenever a checkpoint is committed, a blocker changes, scope is approved, or a
verification claim changes. Keep only current handoff state here; durable product decisions belong
in the spec or an ADR, and granular completion belongs in `tasks/todo.md`.
