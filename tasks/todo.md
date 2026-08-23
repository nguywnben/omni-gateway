# Omni Gateway Enterprise Overhaul — Task Checklist

## Approval

- [x] Approve `docs/specs/enterprise-overhaul.md` and `tasks/plan.md`.

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

- [ ] Extend provider operation capabilities.
  - Acceptance: every console provider/variant declares a complete operation set.
  - Verify: registry consistency and provider contract tests.
  - Files: provider registry/catalog, focused tests, docs.
- [ ] Enforce capability-aware single/batch operations.
  - Acceptance: unsupported crafted actions fail; mixed batches return typed per-item outcomes.
  - Verify: action matrix and dry-run tests.
  - Files: credential operation route/domain, schemas, tests.
- [ ] Add faceted filters and context-aware batch toolbar.
  - Acceptance: filters persist; page/all-result selection differs; only common actions are enabled.
  - Verify: large mixed-provider fixture and desktop/mobile browser flow.
  - Files: pool fragment, credential manager/cards/actions JS, CSS/tests.
- [ ] Audit and correct all provider inputs.
  - Acceptance: input type, required, bounds, secret masking, help, and reset are correct.
  - Verify: provider form contract tests and keyboard/browser checks.
  - Files: provider fragment/features, locale catalog, frontend tests.

## Phase 4 — Access and Audit

- [ ] Add append-only redacted audit events.
  - Acceptance: every management mutation is correlated, attributable, filterable, and bounded.
  - Verify: mutation matrix, redaction, retention, and export tests.
  - Files: audit domain/storage/routes, integration hooks, tests.
- [ ] Add scoped, reservation-aware virtual keys.
  - Acceptance: scopes, limits, budgets, unknown pricing, expiry, revoke/rotate are enforced.
  - Verify: concurrent auth/rate/budget and compatibility tests.
  - Files: virtual-key domain/routes, request auth, state store, tests.
- [ ] Build Access page.
  - Acceptance: root integration and virtual-key lifecycle work; plaintext appears exactly once.
  - Verify: DOM/console/network/accessibility and secret-lifetime browser tests.
  - Files: page fragment, feature JS, CSS, locales/tests.

## Phase 5 — Observability

- [ ] Persist bounded request decision traces.
  - Acceptance: routing/retry/compression/guardrail/cache/token/cost/latency/outcome are correlated.
  - Verify: redaction, retention, and failure-path tests.
- [ ] Build trace search/detail and separate raw logs.
  - Acceptance: request-ID diagnosis works without prompt or secret content.
  - Verify: API/browser/filter/export tests.
- [ ] Add SLO health, alerts, and low-cardinality metrics.
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
