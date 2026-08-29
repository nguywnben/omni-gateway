# Omni Gateway Enterprise Overhaul — Task Checklist

## Approval

- [x] Approve `docs/specs/enterprise-overhaul.md` and `tasks/plan.md`.

## Current Execution Gate

- Program progress: 21/28 original checklist items complete (including specification and Phase 6
  ADR approval), exactly 75.0%. Wave execution-slice checkboxes below refine existing phase items
  and do not change that denominator.
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
- [x] Report Wave 3 evidence and obtain human acceptance before Wave 4.
  - Accepted: 2026-08-26 when the human instructed the agent to start the project and execute the
    next plan after receiving the W3-C completion report.

These queue items refine Phases 4–5 and do not add to the 28-item program denominator.

## Wave 4 — Identity and Scale Execution Queue

- [x] W4.1 Draft the Phase 6 specification and proposed RBAC/OIDC and HA ADRs.
  - `docs/specs/enterprise-identity-and-ha.md`, ADR-007, and ADR-008 define principals, roles,
    sessions, recovery, OIDC validation, durable/coordinated state, migration, failure posture,
    measurable targets, alternatives, and rollback without activating the behavior.
- [x] Approval gate W4-0: human accepts ADR-007, ADR-008, permission bundles, recovery posture,
  `PyJWT[crypto]`, HA targets, and the Wave 4 execution queue before W4.2.
  - Accepted: 2026-08-26 when the human instructed execution of the next plan after receiving the
    W4.1 review gate and progress report.
- [x] W4.2 Define the principal, role, and permission contract.
  - Complete at `c745e18`; four exact immutable role bundles, strict typed principals, denial-first
    decisions, local-owner/OIDC adapters, bounded virtual-key compatibility, legacy-scope inventory
    markers, and additive granular scopes pass 15 focused and 724 total tests.
- [x] W4.3 Enforce a complete management HTTP/WebSocket permission manifest.
  - Complete at `627514d`; one exact manifest covers all 93 protected OpenAPI operations and the
    runtime-log WebSocket. The common dependency resolves typed principals, authorizes trusted
    FastAPI route templates before handlers, and fails closed on missing policy. Generated role and
    legacy-key matrices preserve existing read/write behavior without granting identity/recovery/HA
    rights. Root-key read and rotate are separate owner permissions. Ruff and all 741 tests pass.
- [x] W4.4 Add the versioned identity/role repository and SQLite migration.
  - Complete at `563fb9d` and `5a81b83`; strict versioned identities, bindings, OIDC policy
    revisions, and migration records use exact case-sensitive issuer/subject identity, independent
    optimistic revisions, authorization epochs, bounded closed records, generic errors, and an
    immutable enabled local-owner bootstrap. The additive SQLite transaction preserves existing
    data and fails closed on corruption. Twenty-one focused and 762 total tests pass.
- [x] W4.5 Add PostgreSQL and MongoDB identity repository parity.
  - Complete at `65335bc`, `3d47e9d`, `6ec265b`, and `12ff59e`, with review fixes `c610cd7` and
    `b3352b5`; one reusable behavioral fixture governs SQLite and opt-in live shared backends.
    PostgreSQL uses additive transactional tables, parameterized CAS, exact collation, and correct
    asyncpg timestamp encoding. MongoDB uses atomic identity/binding documents, OIDC-only partial
    uniqueness, simple collation, and revision CAS. Adapter selection passes for all three backends;
    46 focused tests run, 14 live tests skip without configured test URIs, and all 801 tests pass.
- [x] W4.6 Add opaque revocable sessions and local-owner recovery.
  - Complete at `849da03`, `a29dec1`, `4dd7bbb`, and review fix `6010e71`; the semantic
    in-process store issues 256-bit opaque values, retains only HMAC-indexed bounded records,
    enforces idle/absolute expiry and authorization epochs, and supports atomic
    rotation/revocation. New setup/login/recovery uses the store; logout and password rotation
    revoke server-side state; legacy local-owner JWTs have a bounded migration window; provider
    OAuth state never contains a bearer session. Recovery is independently throttled, audited,
    optionally direct-loopback-only, and returns generic errors. Store capacity is bounded with
    expiry pruning and least-recently-used revocation. All 829 tests pass with 14 opt-in
    live-backend skips.
- [x] Checkpoint W4-A: authorization, durability, compatibility, session, and recovery gates pass.
  - Closed on 2026-08-27 after 829 tests, repository-wide lint/format/compile/dependency/diff gates,
    session/recovery security review, and committed-runtime health/readiness smoke passed. The
    maintained operator contract is `docs/management-sessions.md`; one worker/replica remains the
    only activated topology.
- [x] W4.7 Add safe OIDC policy, discovery, JWKS, and secret configuration.
  - Completed on 2026-08-28 in `407ecac`, `c32e369`, `247ada8`, `55c81d6`, and `d0874f7`;
    checkpoint runtime fix `3ce001b` preserves full nested-router authorization.
    The immutable versioned policy is disabled by default, secrets remain environment/file-only,
    discovery uses pinned verified HTTPS with SSRF and response bounds, metadata/JWKS fail closed,
    and JWKS rotation is bounded and single-flight. Thirty-eight focused tests and all 868 tests
    pass on Python 3.12 and Python 3.14; dependency consistency, Ruff, format, compile, route
    contract, and vulnerability gates pass. Login activation remains gated by W4.8–W4.12.
- [x] W4.8 Add strict asymmetric ID Token verification.
  - Completed on 2026-08-28 in `5b40d51`, `e7d5911`, `9dcfa51`, and `dbd2914`.
    The verifier accepts only configured/discovered RS256, PS256, or ES256 keys, binds the JWKS
    cache to the exact immutable trust configuration, requires exact issuer/audience/authorized-
    party/nonce and bounded `exp`/`nbf`/`iat` semantics, validates optional UserInfo subject
    equality, returns only bounded allowlisted identity claims, and suppresses provider-controlled
    exception chains. Unknown key IDs receive one bounded rotation attempt without refresh storms;
    known cached keys remain usable after a failed rotation. Thirty-four focused OIDC policy/JWKS/
    token tests and all 880 tests pass on Python 3.12 and Python 3.14 with 14 opt-in live-backend
    skips. Ruff, format, compile, dependency consistency, diff, locked install, and vulnerability
    gates pass. No OIDC login, callback, token exchange, or OIDC session route is active.
- [x] W4.9 Add Authorization Code + PKCE/state/nonce transaction and callback.
  - Completed on 2026-08-28 in `e28cbab`, `41795bc`, `4d849c0`, and `0b70c3a`.
    Discovery now requires PKCE S256; a capacity-bounded atomic transaction service binds one-time
    state, browser proof, nonce, verifier, issuer, endpoints, auth method, and policy revision.
    Bounded raw callback parsing rejects duplicates, malformed encoding, query credentials, mix-up,
    and replay; the pinned token exchange supports only the discovered Basic/Post method, discards
    access/refresh tokens, and releases only a strictly verified ID Token projection. The external
    adversarial review findings were reconciled before closure. Seventy-four focused OIDC tests and
    all 904 tests pass on Python 3.12 and Python 3.14 with 14 opt-in live-backend skips; Ruff,
    format, compile, dependency, locked-install, diff, and vulnerability gates pass. The route and
    session remain gated by W4.10 so an unmapped external subject can never receive a session.
- [x] W4.10 Add explicit role binding and deny-by-default JIT identity resolution.
  - Completed on 2026-08-28 in `f56781a`, `b5d7e66`, `0c4ed63`, and `a02d0af`. Exact case-sensitive
    issuer/subject direct bindings win; bounded group mappings can assign only viewer/operator/
    security-admin and conflicting/unmapped claims deny. Claim roles are re-evaluated on login,
    OIDC sessions bind independent identity/policy authorization epochs, and management requests
    authorize the real OIDC principal. The disabled-by-default lazy browser flow uses a short-lived
    callback-scoped HttpOnly binding cookie, clean same-origin 303 completion, bounded start abuse,
    and never makes local-owner recovery depend on IdP availability. Adversarial closure removed
    implicit owner fallback, added bounded shared discovery-failure backoff, and made failed claim
    re-evaluation stale every older session for that identity.
- [x] W4.11 Add bounded identity/session APIs and complete actor-aware audit.
  - Completed on 2026-08-29 in `798d2ae`. Exact typed routes expose current principal, OIDC
    readiness, direct identities, active sessions, revocation, policy-epoch advancement, and
    recovery status through granular permissions, bounded stable pagination, optimistic revisions,
    and dedicated owner-transition authority. Sessions use non-secret HMAC references; responses
    exclude bearer tokens, internal digests, provider tokens, claims, groups, and configured
    secrets. Verified denials retain a typed redacted actor, and every identity/session/policy
    mutation uses the closed audit matrix. Fresh-context adversarial review corrected recovery
    ingress reporting and added the SQLite pagination-order index. All 946 tests pass on Python
    3.14.6 with 14 opt-in live-backend skips; repository lint/format/compile/dependency, JavaScript
    syntax, diff, and vulnerability gates pass.
- [x] W4.12 Build the localized Identity console.
  - Completed on 2026-08-29 in `0d1f608`. The dedicated Identity destination derives controls from
    exact effective permissions, bounds identity/session pagination, preserves stale drafts,
    confirms disruptive changes, resets state across authentication boundaries, and supplies
    curated copy for all 15 locales. Cross-model and authenticated-browser findings were fixed
    with regression tests. All 960 tests and repository gates pass.
- [x] Checkpoint W4-B: OIDC, API, audit, recovery, i18n, accessibility, and browser gates pass.
  - Completed on 2026-08-29. Authenticated 360/768/1024/1440, system/light/dark,
    Vietnamese/English/Simplified-Chinese, keyboard/focus, accessible-name, endpoint, and clean
    console checks passed without executing a governance mutation. OIDC remains disabled by
    default; one worker and one replica remain enforced until W4-C.
- [x] W4.13 Add the resumable durable-ledger migration contract.
  - Completed on 2026-08-29. The closed semantic manifest binds every durable family and excludes
    checkpoint control metadata from recursive copying. Source mutation barriers, exact endpoint
    instances, strict add-or-equal target writes, explicit-empty declarations, streaming keyed
    verification, and revision-one/CAS checkpoints fail closed. SQLite restart/corruption behavior
    and PostgreSQL/MongoDB driver boundaries pass; live backend parity remains W4.14. All 987 tests
    pass with 14 configured live-backend skips.
- [ ] W4.14 Complete durable usage ledger and backend parity.
- [ ] W4.15 Implement Redis semantic primitive parity.
- [ ] W4.16 Coordinate identity/session/security runtime state.
- [ ] W4.17 Coordinate routing/governance/cache runtime state.
- [ ] W4.18 Add the HA deployment gate, readiness, alerts, runbooks, and rollback.
- [ ] W4.19 Pass failure/load gates and record the exact activation topology.
- [ ] Checkpoint W4-C: Phase 6 acceptance and all repository/rollback gates pass.
- [ ] Report Wave 4 evidence and obtain human acceptance before Wave 5.

These queue items refine Phase 6 and do not add to the 28-item program denominator. RBAC/OIDC code,
distributed activation, multiple workers/replicas, and release activation remain gated.

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

- [x] Approve RBAC/OIDC and HA activation ADRs before implementation.
- [ ] Implement viewer/operator/security-admin/owner and OIDC with recovery.
- [ ] Move usage, traces, and audit to the selected durable backend.
- [ ] Move runtime coordination to Redis-capable state interfaces.
- [ ] Pass failure/load tests and only then enable multiple workers/replicas.

## Phase 7 — Ship

- [ ] Complete security, performance, and fresh-context adversarial review.
- [ ] Complete architecture/API/operator/upgrade/rollback/i18n documentation.
- [ ] Pass full release checklist, container smoke, browser matrix, and staged rollout.
