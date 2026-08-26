# Omni Gateway Enterprise Overhaul — Task Checklist

## Approval

- [x] Approve `docs/specs/enterprise-overhaul.md` and `tasks/plan.md`.

## Current Execution Gate

- Program progress: 20/28 original checklist items complete (including specification approval),
  approximately 71.4%. Wave execution-slice checkboxes below refine existing phase items and do
  not change that denominator.
- [x] Complete Wave 1 / Phases 0–2 at implementation commit `39fb9da`.
- [x] Record wave governance, recovery order, and the Wave 2 execution slices in repository docs.
- [x] Obtain explicit human approval before implementing Wave 2.
  - Approved: 2026-08-24; implementation begins at W2.1.
  - Resume: read `tasks/current.md`, then verify `git status`, `git log`, tests, and runtime health.

## Wave 2 — Credential Operations Execution Queue

- [x] W2.1 Inventory credential variants and operation capabilities.
- [x] W2.2 Add the authenticated additive capability catalog contract.
- [x] W2.3 Enforce capabilities for single-credential operations.
- [x] W2.4 Add bounded batch preview and typed per-item execution outcomes.
- [x] W2.5 Add credential-scoped redacted audit and bounded operation telemetry foundations.
- [x] Checkpoint W2-A: contracts, compatibility, safety, and evidence gates pass.
- [x] W2.6 Add the faceted fleet query and stable all-matching selection contract.
- [x] W2.7 Add persistent responsive filters and page/all-results selection.
- [x] W2.8 Add the context-aware toolbar, preview, and localized result workflow.
- [x] Checkpoint W2-B: mixed-provider API/browser/accessibility matrix passes.
- [x] W2.9 Define and enforce the shared provider form contract.
- [x] W2.10 Correct Google-family provider forms and flows.
- [x] W2.11 Correct OpenAI, xAI, Anthropic, and Ollama forms and flows.
- [x] Checkpoint W2-C: Phase 3 acceptance and all repository quality gates pass.
- [x] Report Wave 2 evidence and obtain human acceptance before Wave 3.
  - Accepted: 2026-08-24 after commit `578fbb4` was pushed to
    `origin/codex/enterprise-overhaul`.

These queue items refine Phase 3. W2.5 is a reusable foundation only: it does not complete the
Phase 4 audit item or the Phase 5 request-trace item.

## Wave 3 — Access and Operational Evidence Execution Queue

- [x] W3.1 Define the versioned append-only audit event and repository contract.
- [x] W3.2 Implement durable audit repositories for SQLite, PostgreSQL, and MongoDB.
- [x] W3.3 Cover every management mutation with correlated redacted audit evidence.
- [x] W3.4 Add bounded audit query, retention, and export APIs.
- [x] W3.5 Build the localized audit operations console.
  - Implementation complete at `9d581ae`; static/security gates and the authenticated real-browser
    matrix pass at 360/768/1024/1440, light/dark/system, and all 15 supported locales.
- [x] Checkpoint W3-A: audit durability, coverage, redaction, export, and browser gates pass.
- [x] W3.6 Add the backward-compatible scoped virtual-key model and pricing policy.
  - Complete at `1bb6596` and `f8513cf`; versioned migration, inference/management scope matrix,
    pricing-policy metadata, last-used/status, bounded model patterns, auth integration, and audit
    attribution pass the W3.6 contract and compatibility gates.
- [x] W3.7 Add atomic reserve/commit/release rate and budget enforcement.
  - Complete at `bb3bd74` and `5b38c71`; state-store atomicity, estimate-to-actual settlement,
    cancellation/failure release, retry idempotency, bounded reconciliation, fail-closed ledger
    outages, unknown-pricing policy, Vertex parity, and low-cardinality metrics pass 646 tests.
- [x] W3.8 Add audited revoke, rotate, one-time reveal, last-used, and conflict semantics.
  - Complete at `c8f62da`; stable-ID rotation and terminal revocation are atomic,
    secrets remain hashed at rest and are revealed only on create/rotate, stale revisions return
    conflicts, lifecycle routes are audited, and all 653 backend tests pass.
- [x] W3.9 Complete the Access page virtual-key lifecycle.
  - Complete at `49db870` and `8379d9c`; the localized Access console covers list, search,
    status/scope filtering, create/edit, usage, rotate, revoke, pricing policy, revision conflicts,
    and one-time secret reveal without retaining plaintext in the page DOM.
- [x] Checkpoint W3-B: scope, concurrency, compatibility, audit, and Access gates pass.
  - Closed after 659 tests, repository-wide Ruff lint/format, compile/dependency/vulnerability/JS
    gates, and an authenticated browser matrix at 360/768/1024/1440, light/dark/system, keyboard
    focus containment, clean console, and all 15 supported locales. Formatter debt was normalized
    independently at `bf5cc99`.
- [x] W3.10 Persist bounded redacted request decision traces.
  - Complete at `fdbe2ea`; the schema is strict and content-free, all supported inference protocols
    share the public request ID, streaming completion is deferred correctly, retention is separate,
    and additive SQLite/PostgreSQL/MongoDB repositories pass redaction/restart/cardinality tests.
- [x] W3.11 Build trace search/detail and keep raw logs separate.
  - Complete at `b52b1a3`; authenticated query/detail/retention/export APIs, audited policy/export
    operations, strict client revalidation, request-ID pivots, 15-locale UI, and a distinct
    diagnostic raw-log section pass 691 tests and the real-browser matrix.
- [x] W3.12 Add SLOs, health views, safe exporters, alert rules, and runbooks.
  - Complete at `4b775b9`; the authenticated Operational Health view exposes bounded RED,
    percentile, route-health, and exhaustion evidence. Prometheus and OTLP/HTTP JSON export are
    opt-in, secret-safe, and low-cardinality; deployment alerts link to symptom-based runbooks.
- [x] Checkpoint W3-C: Phase 4–5 acceptance and all repository quality gates pass.
  - Closed after 709 tests, repository-wide Ruff lint/format, compile, dependency, vulnerability,
    JavaScript, YAML, shell-syntax, and diff gates. The authenticated browser matrix passed at
    360/768/1024/1440, light/dark/system, all 15 locales, with no overflow or console errors.
- [ ] Report Wave 3 evidence and obtain human acceptance before Wave 4.

These queue items refine Phases 4–5 and do not add to the 28-item program denominator. Phase 6,
distributed activation, multiple workers/replicas, and release activation remain unapproved.

## Phase 0 — Decisions

- [x] Write policy-plane ADR.
  - Acceptance: profiles, precedence, migration, telemetry, alternatives, and rollback are explicit.
  - Verify: ADR matches the existing `docs/decisions/` convention.
  - Files: `docs/decisions/004-*.md`, `docs/architecture.md`.
- [x] Write provider-capability/state ADR.
  - Acceptance: operation capabilities and the path to distributed state are unambiguous.
  - Verify: current provider/runtime behavior is mapped to the proposed boundary.
  - Files: `docs/decisions/005-*.md`, `docs/decisions/006-*.md`, `docs/architecture.md`.

## Phase 1 — UI Foundation

- [x] Implement light/dark/system theme.
  - Acceptance: no flash; preference persists; all pages meet contrast/focus requirements.
  - Verify: browser at 360/768/1024/1440, clean console, theme unit/asset tests.
  - Files: theme core JS, foundation CSS, shell fragments, frontend tests.
- [x] Add AI Quality and Access navigation; simplify Overview.
  - Acceptance: old deep links work; root-key mutation no longer lives on Overview.
  - Verify: route/asset tests and keyboard navigation browser flow.
  - Files: sidebar, page fragments, navigation JS, root manifest/tests.
- [x] Add keyed localization and literal-leak gate.
  - Acceptance: 15 locales complete; known Vietnamese English leaks removed.
  - Verify: all i18n audits plus new user-visible-literal audit.
  - Files: locale catalogs, i18n tests/tooling, affected fragments/JS.

## Phase 2 — AI Quality

- [x] Add versioned quality-policy domain and migration.
  - Acceptance: existing config maps to `balanced/custom` without changing behavior.
  - Verify: policy validation, precedence, and migration tests.
  - Files: policy module, config bridge, focused tests, ADR.
- [x] Add quality-policy read/update/preview API.
  - Acceptance: authenticated, versioned, bounded, environment-lock aware.
  - Verify: management API contract and error-envelope tests.
  - Files: panel route, schemas/domain, router composition, tests.
- [x] Strengthen compression and enabled-security failure behavior.
  - Acceptance: protected structures survive; every skip/apply has a reason; enabled guardrails do
    not fail open.
  - Verify: adversarial long-context/tool-pair tests and gateway-pipeline tests.
  - Files: compression, pipeline, config, focused tests.
- [x] Build AI Quality page.
  - Acceptance: profiles, dependencies, preview, impact copy, save/reset all work.
  - Verify: API/browser workflow, accessibility tree, responsive screenshots, clean console.
  - Files: page fragment, feature JS, CSS, locale/test assets.

## Phase 3 — Credential Fleet

- [x] Extend provider operation capabilities.
  - Acceptance: every console provider/variant declares a complete operation set.
  - Verify: registry consistency and provider contract tests.
  - Files: provider registry/catalog, focused tests, docs.
- [x] Enforce capability-aware single/batch operations.
  - Acceptance: unsupported crafted actions fail; mixed batches return typed per-item outcomes.
  - Verify: action matrix and dry-run tests.
  - Files: credential operation route/domain, schemas, tests.
- [x] Add faceted filters and context-aware batch toolbar.
  - Acceptance: filters persist; page/all-result selection differs; only common actions are enabled.
  - Verify: large mixed-provider fixture and desktop/mobile browser flow.
  - Files: pool fragment, credential manager/cards/actions JS, CSS/tests.
- [x] Audit and correct all provider inputs.
  - Acceptance: input type, required, bounds, secret masking, help, and reset are correct.
  - Verify: provider form contract tests and keyboard/browser checks.
  - Files: provider fragment/features, locale catalog, frontend tests.

## Phase 4 — Access and Audit

- [x] Add append-only redacted audit events.
  - Acceptance: every management mutation is correlated, attributable, filterable, and bounded.
  - Verify: mutation matrix, redaction, retention, and export tests.
  - Files: audit domain/storage/routes, integration hooks, tests.
- [x] Add scoped, reservation-aware virtual keys.
  - Acceptance: scopes, limits, budgets, unknown pricing, expiry, revoke/rotate are enforced.
  - Verify: concurrent auth/rate/budget and compatibility tests.
  - Files: virtual-key domain/routes, request auth, state store, tests.
- [x] Build Access page.
  - Acceptance: root integration and virtual-key lifecycle work; plaintext appears exactly once.
  - Verify: DOM/console/network/accessibility and secret-lifetime browser tests.
  - Files: page fragment, feature JS, CSS, locales/tests.

## Phase 5 — Observability

- [x] Persist bounded request decision traces.
  - Acceptance: routing/retry/compression/guardrail/cache/token/cost/latency/outcome are correlated.
  - Verify: redaction, retention, and failure-path tests.
- [x] Build trace search/detail and separate raw logs.
  - Acceptance: request-ID diagnosis works without prompt or secret content.
  - Verify: API/browser/filter/export tests.
- [x] Add SLO health, alerts, and low-cardinality metrics.
  - Acceptance: p50/p95/p99, errors, exhaustion, storage, and unknown pricing are visible.
  - Verify: metric snapshot/cardinality and alert-state tests.

## Phase 6 — Identity and HA

- [ ] Approve RBAC/OIDC ADR before implementation.
- [ ] Implement viewer/operator/security-admin/owner and OIDC with recovery.
- [ ] Move usage, traces, and audit to the selected durable backend.
- [ ] Move runtime coordination to Redis-capable state interfaces.
- [ ] Pass failure/load tests and only then enable multiple workers/replicas.

## Phase 7 — Ship

- [ ] Complete security, performance, and fresh-context adversarial review.
- [ ] Complete architecture/API/operator/upgrade/rollback/i18n documentation.
- [ ] Pass full release checklist, container smoke, browser matrix, and staged rollout.
