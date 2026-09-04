# Implementation Plan: Omni Gateway Enterprise Overhaul

## Overview

Deliver the enterprise overhaul as reversible vertical slices. The first release establishes the
UX and policy foundation, the second governs credentials and access, the third adds operational
evidence, and the final program phases earn multi-user identity and multi-replica claims.

## Execution Governance

This repository, not chat history, is the source of truth. A new human or agent resumes work in
this order:

1. Read `docs/specs/enterprise-overhaul.md` for product boundaries and success criteria.
2. Read applicable accepted ADRs in `docs/decisions/` before changing a contract.
3. Read this file for dependency order, wave scope, checkpoints, and approval gates.
4. Read `tasks/todo.md` for the authoritative completion checklist.
5. Read `tasks/current.md`, then verify its claims against `git status` and `git log`.

A task is complete only when its acceptance and verification evidence pass. Writing code, adding
a route, or rendering a page is not completion by itself. Every checkpoint must leave the branch
deployable and reversible, with a clean worktree and an atomic commit.

Implementation pauses at every wave boundary for human approval. Work borrowed from a later phase
may establish a reusable foundation, but the later phase remains incomplete until its full
acceptance criteria pass. No task is silently re-scoped or checked off to improve the progress
number.

## Delivery Waves

| Wave | Phase coverage | Outcome | Status |
| --- | --- | --- | --- |
| 1 — Policy and console foundation | Phases 0–2 | Decisions, theme/i18n/navigation, governed AI Quality | Complete |
| 2 — Credential operations | Phase 3 plus credential-scoped audit/telemetry foundations | Capability-correct provider and credential fleet | Complete |
| 3 — Access and operational evidence | Phases 4–5 | Access governance, complete audit, traces, SLOs | Complete |
| 4 — Identity and scale | Phase 6 | RBAC/OIDC, durable state, coordinated HA | In progress |
| 5 — Production release | Phase 7 | Security/performance hardening and staged launch | Not started |

Wave boundaries organize delivery; phase checkboxes continue to describe product completion.
Wave 2 may introduce credential mutation audit hooks and bounded operation telemetry because batch
operations are not enterprise-safe without evidence. This does not complete Phase 4 audit coverage
or Phase 5 request tracing.

## Current Approval Gate

- Wave 3 completion checkpoint: `76315e7` (`docs: close wave 3 operational evidence`).
- Completed product scope: Phases 0–5; Wave 3 was accepted by the human on 2026-08-26 through the
  instruction to start the project and execute the next plan.
- Active approved scope: Wave 4 under accepted ADR-007/ADR-008; W4.1–W4.16 and checkpoints W4-A/W4-B
  are complete and W4.17 is the active implementation slice.
- State: **IN PROGRESS — W4.17 NEXT**. Identity/session/security coordination is complete; routing,
  governance, and cache coordination is next. Runtime activation remains unchanged.
- Still gated by later slices and evidence: distributed-state activation, multiple workers/
  replicas, destructive migration, and production release activation.

## Architecture Decisions

- Preserve the stable 1.x SDK boundary and evolve management APIs additively.
- Introduce a typed policy plane; do not expand individual environment switches indefinitely.
- Keep safe structural history pruning as the only initial compression engine.
- Make provider capabilities authoritative for server and console actions.
- Add audit and scopes before RBAC; add distributed coordination before enabling scale-out.
- Migrate localization from positional arrays to keyed catalogs incrementally with parity gates.

## Dependency Graph

```text
Baseline + ADRs
  -> keyed UI foundation + theme
  -> policy schema/API
       -> AI Quality page + preview
       -> request decision metrics
  -> provider operation capabilities
       -> capability-aware credential API
       -> credential fleet UX
  -> audit model + scopes
       -> Access / virtual-key UX
       -> RBAC/OIDC
  -> request traces + durable ledger
       -> Redis coordination
       -> multi-worker/replica enablement
```

## Wave 2 Execution Slices

These slices refine Phase 3 into reviewable increments. Each slice targets at most one cohesive
contract or user workflow and receives its own test evidence and commit.

### W2.1 — Credential variant and operation inventory

Document every console-visible provider variant and map its currently supported operations before
changing behavior. Undeclared operations are unsupported.

- Acceptance: the inventory covers every provider/variant and resolves ambiguous legacy modes.
- Verification: registry consistency tests fail for a missing variant or operation declaration.
- Dependencies: ADR-005; none of the later Wave 2 slices.
- Likely files: `backend/core/provider_registry.py`, provider registry tests, ADR-005 notes.

### W2.2 — Capability catalog contract

Expose the authoritative variant/operation contract additively for management clients while
preserving existing provider catalog fields.

- Acceptance: typed, authenticated, bounded response; old clients remain compatible.
- Verification: API contract, authentication, unknown-provider, and serialization tests.
- Dependencies: W2.1.
- Likely files: provider catalog route/schema and focused tests.

### W2.3 — Capability-enforced single operations

Route existing single-credential actions through one service that validates variant capability,
authorization, state, environment locks, and filename safety before side effects.

- Acceptance: crafted unsupported actions fail with stable typed errors; supported legacy routes
  keep their 1.x behavior.
- Verification: provider/action matrix plus compatibility and malformed-input tests.
- Dependencies: W2.1–W2.2.
- Likely files: credential operation domain/route and focused tests.

### W2.4 — Batch preview and typed execution outcomes

Add a bounded selection contract, side-effect-free preview, idempotency boundary, and per-item
result envelope. Preview and execution re-evaluate capabilities server-side.

- Acceptance: mixed batches never claim unsupported work succeeded; destructive/high-volume work
  requires a matching preview contract.
- Verification: partial success, stale selection, duplicate, limit, timeout, and dry-run tests.
- Dependencies: W2.3.
- Likely files: batch schema/service/route and focused tests.

### W2.5 — Credential operation evidence foundation

Emit append-only, redacted credential mutation events and bounded operation metrics from the common
service. Never record credential content, prompt content, tokens, or secrets.

- Acceptance: every Wave 2 mutation has request ID, actor, action, target fingerprint, outcome,
  duration, and redacted summary.
- Verification: allowlist/redaction, failure-path, cardinality, and duplicate-event tests.
- Dependencies: W2.3–W2.4.
- Likely files: operation service, minimal audit/telemetry boundary, focused tests.

Checkpoint W2-A follows W2.1–W2.5: capability contracts are stable, existing routes are compatible,
and operation safety/evidence gates pass before fleet UI work begins.

### W2.6 — Faceted fleet query contract

Add provider variant, credential kind, health, cooldown, quota state, tier, and source filters with
stable pagination and an explicit all-matching selection token.

- Acceptance: filters compose deterministically and never return secret fields.
- Verification: empty, large, changing, invalid, and mixed-provider fixtures.
- Dependencies: W2.1–W2.2.
- Likely files: credential query domain/route and focused tests.

### W2.7 — Persistent filter and selection workflow

Build the responsive filter surface and distinguish current-page selection from all matching
results. Restore filters without restoring stale secret-bearing data.

- Acceptance: URL/session state is bounded; pagination and refresh preserve valid filters;
  keyboard and mobile workflows remain complete.
- Verification: frontend contract tests and browser checks at 360/768/1024/1440.
- Dependencies: W2.6.
- Likely files: pool fragment, credential manager/filter JavaScript, pool CSS/tests.

### W2.8 — Context-aware operation toolbar

Render only the intersection of supported actions, explain unavailable actions, preview work, and
show localized per-item results with recovery guidance.

- Acceptance: UI availability never exceeds server capability; stale previews are rejected and
  refreshed; destructive actions require explicit confirmation.
- Verification: mixed-provider browser matrix, accessibility tree, clean console/network, and API
  adversarial tests.
- Dependencies: W2.4, W2.5, W2.7.
- Likely files: batch-action/credential-card JavaScript, pool fragment/CSS, locales/tests.

Checkpoint W2-B follows W2.6–W2.8: the complete mixed-provider fleet workflow passes API,
responsive, theme, locale, keyboard, and accessibility gates.

### W2.9 — Shared provider form contract

Define reusable rules for field type, required state, bounds, autocomplete, secret lifetime,
environment locks, help, advanced sections, validation, and reset behavior.

- Acceptance: shared behavior is declarative and does not erase provider-specific constraints.
- Verification: form manifest/static audit tests detect missing labels, secret handling, or bounds.
- Dependencies: W2.1.
- Likely files: provider form metadata/shared JavaScript and focused tests.

### W2.10 — Google-family provider form correction

Apply the shared contract to Antigravity, Google AI Studio, and related OAuth/import flows without
changing credential compatibility.

- Acceptance: all Google-family fields and flows meet the W2.9 contract.
- Verification: contract tests plus keyboard, secret-lifetime, reset, and import browser flows.
- Dependencies: W2.9.
- Likely files: Google provider fragment/features, locales, focused tests.

### W2.11 — OpenAI, xAI, Anthropic, and Ollama form correction

Apply the shared contract to remaining provider variants, including endpoint and advanced
transport fields.

- Acceptance: every console provider variant passes the form contract with no English literal
  leak in any supported locale.
- Verification: provider contract tests, 15-locale audit, and representative browser flows.
- Dependencies: W2.9.
- Likely files: remaining provider fragment/features, locales, focused tests.

Checkpoint W2-C closes Wave 2 only when Phase 3 acceptance passes end-to-end, all repository quality
gates pass, the worktree is clean, the service restarts from the checkpoint commit, and the human
accepts the completion report. Phase 4 and Phase 5 remain open except for their reusable foundations.

## Wave 3 Execution Slices

Wave 3 converts the partial in-memory evidence and virtual-key implementation into an enterprise
access and operations plane. Audit precedes authorization changes; reservation semantics precede
new key controls; bounded trace storage precedes the Observability UI. Each slice is additive and
keeps the supported single-worker rollback path.

### W3.1 — Audit event and repository contract

Define the versioned append-only event schema, actor/action/target/outcome vocabularies, redacted
change-summary boundary, query cursor contract, retention policy, and repository interface.

- Acceptance: invalid or sensitive fields fail closed before crossing the repository boundary;
  callers cannot update or delete individual events.
- Verification: focused schema, redaction, immutability, cursor, and bounds tests fail before the
  contract exists and pass after implementation.
- Dependencies: ADR-006 and the W2.5 credential evidence vocabulary.
- Likely files: audit domain module and focused tests.

### W3.2 — Durable audit repositories

Implement additive append/list/export/prune semantics for SQLite, PostgreSQL, and MongoDB without
storing audit history inside the mutable configuration document.

- Acceptance: ordering and cursor behavior match across backends; restart preserves events; prune
  is policy-driven and never an individual-event mutation.
- Verification: backend contract, migration, restart, rollback-note, and failure tests.
- Dependencies: W3.1.
- Likely files: storage protocol and three backend managers, migrations, focused tests.

### W3.3 — Correlated management-mutation coverage

Attach normalized actor and request context to login, configuration, provider, credential, key,
policy, backup, and destructive mutations, then bridge W2 credential evidence into the audit
repository without duplicate events.

- Acceptance: the mutation matrix emits exactly one attributable, redacted event for success and
  failure paths, including idempotent retries.
- Verification: management-route mutation matrix, request-ID, actor, redaction, and outage tests.
- Dependencies: W3.2.
- Likely files: request context/middleware, panel mutation hooks, audit service, tests.

### W3.4 — Audit query, retention, and export API

Expose authenticated, bounded filtering by time/action/target/outcome/actor/request ID, opaque
cursor pagination, retention configuration, and streaming JSONL/CSV export.

- Acceptance: exports are formula-safe, secret-free, size-bounded, and consistent with filters;
  retention cannot silently erase events outside policy.
- Verification: API contract, tamper, pagination, export-injection, redaction, and limit tests.
- Dependencies: W3.3.
- Likely files: audit panel routes/models, retention service, export tests.

### W3.5 — Audit operations console

Add an Audit surface under Observability with saved-safe filters, event detail, request-ID pivot,
retention visibility, and bounded export controls.

- Acceptance: operators can investigate every management mutation without prompt, credential, or
  plaintext-key content reaching the DOM.
- Verification: 15-locale, desktop/mobile, keyboard, accessibility, console/network, and secret-
  lifetime browser checks.
- Dependencies: W3.4.
- Likely files: Observability fragment/features/CSS/locales and frontend tests.

Checkpoint W3-A follows W3.1–W3.5: complete management mutation coverage, durable audit parity,
redaction, retention, export, API, and browser gates pass before key governance expands.

### W3.6 — Backward-compatible scoped virtual-key model

Add inference-protocol and management read/write scopes, explicit unknown-pricing policy, status,
last-used metadata, model-pattern validation, and versioned migration of existing keys.

- Acceptance: existing keys preserve current inference access; new keys default to least privilege;
  unknown or malformed scopes fail closed.
- Verification: migration, compatibility, scope matrix, pricing-policy, and malformed-input tests.
- Dependencies: W3-A.
- Likely files: virtual-key domain/routes/auth and focused tests.

### W3.7 — Reservation-aware rate and budget enforcement

Extend the state-store semantic boundary with atomic reserve/commit/release operations for RPM,
TPM, and estimated/actual cost in the supported single-worker implementation.

Status: complete at `bb3bd74` and `5b38c71`.

- Acceptance: concurrent requests cannot knowingly exceed a hard limit; cancellations and provider
  failures release reservations; unknown pricing follows deny/warn/fallback policy.
- Verification: concurrency, cancellation, retry, expiry, reconciliation, and overspend tests.
- Dependencies: W3.6 and ADR-006.
- Likely files: state-store contract, virtual-key enforcement, usage integration, tests.

### W3.8 — Safe key lifecycle

Add revoke, rotate, one-time reveal, last-used/usage summaries, and optimistic concurrency while
retaining hashed-at-rest secrets and stable existing routes.

- Acceptance: plaintext is returned only by create/rotate and cannot be recovered later; stale
  updates conflict; lifecycle actions are audited.
- Verification: API compatibility, plaintext lifetime, race, replay, and audit tests.
- Dependencies: W3.7.
- Likely files: virtual-key domain/routes, audit hooks, tests.

### W3.9 — Complete Access page

Build virtual-key list/create/edit/rotate/revoke flows with scopes, budgets, rate limits, expiry,
model patterns, status, usage, explicit unknown-pricing policy, and one-time reveal dismissal.

- Acceptance: root guidance and the whole virtual-key lifecycle work without persisting plaintext
  in browser storage or retaining it in the DOM after dismissal.
- Verification: desktop/mobile, theme, 15-locale, keyboard/accessibility, console/network, and
  secret-lifetime browser tests.
- Dependencies: W3.8.
- Likely files: Access fragment/features/CSS/locales and frontend tests.

Checkpoint W3-B follows W3.6–W3.9: scope, budget/rate concurrency, compatibility, audit, and Access
browser matrices pass before request tracing begins.

### W3.10 — Bounded request decision trace

Define and persist allowlisted trace summaries for routing attempts, fallback, retry, cooldown,
compression, guardrails, cache, tokens, cost, latency, and outcome without request content.

- Acceptance: one request ID explains the decision path across supported protocols and failures;
  trace retention is bounded and independent from raw logs.
- Verification: protocol/failure matrix, redaction, retention, cardinality, and restart tests.
- Dependencies: W3-B.
- Likely files: trace domain/repository, gateway hooks, storage backends, tests.

### W3.11 — Trace search and raw-log separation

Evolve Logs into Observability with trace search/detail, request-ID pivots, safe export, and a
visually and semantically separate bounded raw-log viewer.

- Acceptance: on-call can answer routing and failure questions from traces while raw logs remain
  explicitly diagnostic and redacted.
- Verification: API/browser/filter/export, websocket security, locale, and accessibility tests.
- Dependencies: W3.10.
- Likely files: observability routes/fragments/features/CSS/locales and tests.

### W3.12 — SLOs, health views, exporters, and runbooks

Add low-cardinality RED signals, provider/model-route health, budget/quota exhaustion views,
Prometheus/OpenTelemetry export controls, symptom-based alert rules, and linked runbooks.

- Acceptance: operators can answer rate/error/duration and exhaustion questions without
  high-cardinality metric labels or externally enabled telemetry by default.
- Verification: metric contract/cardinality, induced-failure, exporter-disabled-default, alert,
  dashboard, and runbook-link tests.
- Dependencies: W3.11.
- Likely files: metrics/telemetry, health APIs/UI, deployment rules, runbooks, tests.

Checkpoint W3-C closed on 2026-08-26 after Phase 4–5 acceptance passed end-to-end, all repository
quality gates passed, the committed service restarted cleanly, and the human instructed execution
of the next plan. ADR-007/ADR-008 were accepted on 2026-08-26; later Wave 4 slices still gate OIDC
and distributed behavior, and multi-worker/multi-replica mode remains disabled.

## Wave 4 Execution Slices

Wave 4 implements the accepted [Phase 6 specification](../docs/specs/enterprise-identity-and-ha.md).
Identity and authorization land before OIDC; OIDC and
revocable sessions land before identity UI; durable parity and Redis semantics land before any
scale-out configuration changes.

The remaining work is governed by the continuous completion plan at
`docs/superpowers/plans/2026-09-02-wave-4-continuous-completion.md`. The human authorized continuous
execution across W4.16–W4.19 on 2026-09-02; internal slices remain atomic, but no task-boundary pause
is required.

### W4.1 — Phase 6 specification and decision gate

Record the current trust boundaries, explicit role/session/OIDC contract, coordinated-state
activation criteria, rollback, and measurable HA targets in ADR-007 and ADR-008.

- Acceptance: the documents cover principals, permission bundles, claim mapping, recovery,
  dependency change, durable/coordinated state, failure posture, migration, alternatives, and
  rollback without claiming that the behavior is active.
- Verification: ADR convention/link audit, source review against OIDC Core and OAuth Security BCP,
  diff/secret review, and human acceptance before W4.2.
- Dependencies: accepted W3-C.
- Likely files: Phase 6 spec, ADR-007, ADR-008, architecture, task state.

### W4.2 — Principal and permission contract

Define closed principal/role/permission vocabularies and a pure authorization decision service.

- Acceptance: the four roles resolve explicit immutable permissions; unknown values fail closed;
  local owner and existing virtual-key semantics have typed compatibility adapters; broad legacy
  management keys are inventory-visible and new granular scopes do not silently narrow them.
- Verification: role matrix, spoofing, malformed principal, and compatibility unit tests.
- Dependencies: accepted W4.1.
- Likely files: identity domain, permission registry, focused tests, API contract docs.
- Completed: `c745e18`; 15 focused contract tests and all 724 backend tests pass.

### W4.3 — Complete management authorization coverage

Classify every protected HTTP/WebSocket route in one declarative permission manifest and enforce it
through a common dependency before handlers run.

- Acceptance: there is no unclassified protected route; UI state cannot bypass denial; existing
  management keys keep existing-route read/write compatibility and gain no identity/HA permission.
- Verification: generated OpenAPI/WebSocket allow-deny matrix and regression tests.
- Dependencies: W4.2.
- Likely files: permission manifest, auth dependency, route integration, coverage tests.
- Completed: `627514d`; all 93 protected HTTP operations and the one management WebSocket are
  classified and enforced before handlers. Generated human-role and legacy-key allow/deny matrices,
  path-converter normalization, fail-closed unknown-route behavior, and all 741 tests pass.

### W4.4 — Versioned identity repository and SQLite migration

Add strict identities, role bindings, OIDC policy revisions, and migration records with optimistic
concurrency and a backward-compatible local-owner bootstrap.

- Acceptance: stable `(issuer, subject)` identity, no email identity, owner invariants, bounded
  records, and non-destructive rollback are enforced.
- Verification: schema migration/restart, conflict, corruption, owner-lockout, and redaction tests.
- Dependencies: W4.2.
- Likely files: identity repository contract/domain, SQLite manager/migration, tests.
- Completed: `563fb9d` and `5a81b83`; closed schema-version-1 identity, role-binding, OIDC-policy,
  and migration records use exact case-sensitive `(issuer, subject)`, never email, and revalidate
  stored rows fail closed. The additive SQLite transaction idempotently bootstraps an immutable
  enabled local owner, preserves old tables, applies foreign keys per connection, and provides
  independent optimistic revisions plus authorization epochs. Sequential/concurrent conflicts,
  restart, corruption, owner lockout, rollback, bounds, and redaction are covered by 21 focused
  tests; all 762 tests pass.

### W4.5 — PostgreSQL and MongoDB identity parity

Implement the W4.4 repository contract for both shared durable backends.

- Acceptance: ordering, revisions, uniqueness, owner invariants, and migration checkpoints match
  SQLite without backend-specific API behavior.
- Verification: contract fixtures plus opt-in live backend integration tests.
- Dependencies: W4.4.
- Likely files: PostgreSQL repository, MongoDB repository, adapter wiring, parity tests.
- Completed: reusable contract fixture `65335bc`; PostgreSQL `3d47e9d`; MongoDB `6ec265b`; adapter
  and opt-in live parity harness `12ff59e`; review corrections `c610cd7` and `b3352b5`. Exact
  identity/order/uniqueness, independent revisions, authorization epochs, owner invariants,
  migration checkpoints, corruption handling, and generic errors match SQLite. Forty-six focused
  cases run locally, fourteen live backend cases skip without explicit test URIs, all 801 tests
  pass, and repository-wide lint/format/compile/dependency gates are clean.

### W4.6 — Opaque standalone sessions and local-owner recovery

Add the semantic session store with an in-process implementation, opaque HMAC-indexed sessions,
idle/absolute expiry, rotation/revocation, authorization epoch, and audited break-glass flow.

- Acceptance: fixation/replay/revoked sessions fail; privilege/password changes revoke affected
  sessions; cookie/CSRF protections and current local login remain compatible.
- Verification: concurrency, expiry, origin, recovery, secret-lifetime, and migration-window tests.
- Dependencies: W4.3–W4.4.
- Likely files: session domain/store, panel auth integration, audit vocabulary, tests.
- Completed: store contract `849da03`, durable-epoch binding `a29dec1`, panel/recovery activation
  `4dd7bbb`, and bounded-capacity review fix `6010e71`. New authentication issues 256-bit opaque
  tokens while retaining only an HMAC index and bounded metadata; idle/absolute expiry, atomic
  rotation/revocation, password and epoch invalidation, origin/cookie protections, isolated
  provider OAuth state, bounded legacy-JWT
  migration, recovery throttling/loopback restriction, audit evidence, generic failures, and
  fixed-cardinality metrics and bounded LRU capacity are covered. All 829 tests pass with 14 opt-in
  live-backend skips. The maintained operator contract is `docs/management-sessions.md`.

Checkpoint W4-A follows W4.2–W4.6: complete authorization coverage, backend identity durability,
local-owner compatibility, revocable sessions, and lockout-recovery gates pass before OIDC login.
Closed on 2026-08-27 after repository-wide quality gates and committed-runtime health/readiness
smoke passed; the single-worker/single-replica boundary remains enforced.

### W4.7 — OIDC policy, metadata, and endpoint safety

Add versioned disabled-by-default issuer/client/claim policy, exact discovery validation, bounded
JWKS caching, endpoint-host controls, and environment-locked secret handling.

- Acceptance: invalid HTTPS/issuer/redirect/endpoint/algorithm/claim configuration fails closed and
  no secret is returned or logged.
- Verification: metadata/JWKS poisoning, SSRF-oriented, redirect, size, timeout, rotation, and
  configuration revision tests.
- Dependencies: W4-A and accepted `PyJWT[crypto]` dependency.
- Likely files: OIDC policy/client, config bridge, schemas, tests.
- Completed: `407ecac`, `c32e369`, `247ada8`, `55c81d6`, and `d0874f7` add the immutable
  disabled-by-default policy, environment/file-secret isolation, exact origin and pinned-address
  HTTPS transport, strict discovery metadata, bounded public-key validation, and atomic
  single-flight JWKS rotation. Review closed duplicate-JSON, secret-file replacement, forged-JWKS-
  URI, and refresh-storm gaps. Checkpoint runtime fix `3ce001b` handles FastAPI's trusted effective
  template for nested management routers and adds a real ASGI regression. Thirty-eight OIDC-focused
  tests and all 868 tests pass on Python 3.12 and Python 3.14; Ruff lint/format, compile, route
  contract, dependency consistency, and vulnerability audit pass. The operator boundary is
  maintained in `docs/oidc-foundation.md`; no login route is active.

### W4.8 — ID Token verifier

Implement strict asymmetric signature, issuer, audience/authorized-party, expiry/skew, nonce, and
optional UserInfo subject validation behind a content-free error boundary.

- Acceptance: only the configured issuer/audience/algorithms and exact transaction succeed;
  unknown key ID refreshes once; provider text never reaches responses/audit.
- Verification: valid and adversarial JWT/JWKS fixtures across supported algorithms.
- Dependencies: W4.7.
- Likely files: token verifier, bounded JWKS cache, focused tests, protocol docs.
- Completed: `5b40d51` adds bounded clock-skew and token-age policy; `e7d5911` prevents configurable
  profile claims from colliding with protocol claims; `9dcfa51` adds the strict verifier and closes
  cold-cache rotation plus sequential unknown-key refresh-storm behavior; `dbd2914` binds each
  verifier to its exact policy/discovery/cache configuration and suppresses all provider-controlled
  exception chains while preserving cancellation. RS256, PS256, ES256, issuer, audience, `azp`,
  nonce, `exp`, `nbf`, `iat`, subject, UserInfo, JOSE-header, duplicate-JSON, size, signature,
  rotation, outage, and claim-bound fixtures pass. Thirty-four focused tests and all 880 tests pass
  on Python 3.12 and Python 3.14 with 14 opt-in live-backend skips; Ruff lint/format, compile,
  dependency consistency, locked installation, diff, and vulnerability audit pass. No login route
  is active.

### W4.9 — OIDC authorization transaction and callback

Implement Authorization Code with PKCE S256, one-time state/nonce, exact callback handling, code
exchange, replay prevention, and internal session issuance.

- Acceptance: state/nonce/code are single-use and transaction-bound; no provider token persists;
  open redirects, query credentials, and mixed issuers are impossible.
- Verification: login/replay/CSRF/mix-up/cancellation/outage protocol matrix.
- Dependencies: W4.6–W4.8.
- Likely files: OIDC transaction service, identity routes, state store, tests.
- Completed: `e28cbab` requires discovered PKCE S256; `41795bc` adds capacity-bounded atomic
  transaction binding with HMAC-indexed state/browser proof and derived verifier/nonce; `4d849c0`
  adds bounded pinned form POST with exact Basic/Post authentication; `0b70c3a` adds strict raw
  callback parsing, single-use exchange, mix-up/replay/cancellation/outage denial, and verified-only
  output. External adversarial findings were reconciled before closure. Seventy-four focused OIDC
  tests and all 904 tests pass on Python 3.12 and Python 3.14 with 14 opt-in live-backend skips;
  repository Ruff/format/compile/dependency/locked-install/diff/vulnerability gates pass. The
  original internal-session substep is safely sequenced into W4.10: no external subject may receive
  a session before exact deny-by-default role resolution, so no browser route is registered yet.

### W4.10 — Role binding and just-in-time identity resolution

Resolve direct subject bindings before bounded provider-specific claim mappings and deny unmapped
users without assigning owner from claims.

- Acceptance: missing/malformed/oversized claims deny; mapping revisions revoke stale sessions;
  disabled identities cannot authenticate.
- Verification: provider claim-shape, precedence, downgrade, stale-session, and owner abuse tests.
- Dependencies: W4.5 and W4.9.
- Likely files: role-binding service, identity repository integration, tests.
- Completed: `f56781a`, `b5d7e66`, `0c4ed63`, and `a02d0af` add strict bounded group-to-role policy,
  exact direct-binding-first JIT resolution, non-owner claim mappings, login-time downgrade,
  independent identity/policy session invalidation, real-principal authorization, lazy IdP
  discovery, browser-bound start/callback routes, clean 303 redirects, and bounded start abuse
  controls. The closure review also removes implicit local-owner fallback, bounds discovery
  waiters with shared failure backoff, and invalidates existing sessions when a claim-mapped
  identity can no longer resolve. OIDC remains disabled by default and one worker/replica remains
  mandatory. All 929 tests pass on Python 3.14; the 40 affected tests pass on Python 3.12 after the
  preceding 926-test dual-interpreter checkpoint.

### W4.11 — Identity/session management API and audit

Add typed bounded APIs for current session, OIDC policy, identities, role bindings, sessions, and
recovery verification with complete mutation evidence.

Implementation slices:

1. Attribute authenticated denials to the verified typed principal and extend the closed audit
   vocabulary for identity, role-binding, session, OIDC-policy, and recovery events.
2. Add bounded repository/session inventory primitives with opaque cursors or non-secret revocation
   references; plaintext bearer tokens and internal token digests never cross the service boundary.
3. Add typed read APIs for the current session, OIDC readiness, identities, active sessions, and
   recovery health with exact manifest permissions and no secret/profile-claim output.
4. Add optimistic-concurrency mutations for direct OIDC identities, enablement, role bindings,
   session revocation, and OIDC authorization-epoch advancement; owner transitions require the
   dedicated owner permission.
5. Close the API, permission, audit, redaction, and conflict test matrices; document the contract,
   run an independent adversarial review, reconcile findings, and commit the slice checkpoint.

- Acceptance: pagination/revisions/permissions/errors are consistent; every mutation and denial is
  attributed to a redacted typed actor; exports or token-returning endpoints are absent.
- Verification: API contract, permission, audit matrix, redaction, and concurrent conflict tests.
- Dependencies: W4.10.
- Likely files: identity routes/schemas, audit matrix/vocabulary, API tests/docs.
- Completed in `798d2ae`: typed exact-route APIs now cover current principal, OIDC readiness,
  direct identities,
  active sessions, revocation, policy-epoch advancement, and recovery status. Stable bounded
  pagination, optimistic revisions, owner-transition permission checks, durable invalidation,
  HMAC-derived session references, typed actor attribution, and closed audit vocabularies prevent
  secret or privilege ambiguity. A fresh-context adversarial review corrected recovery ingress
  reporting and added the SQLite pagination-order index. All 946 tests pass with 14 opt-in live
  backend skips; repository Ruff/format/compile/dependency, JavaScript syntax, diff, and
  vulnerability gates pass. The maintained contract is `docs/identity-management-api.md`, and the
  reconciled review is `docs/w4.11-adversarial-review.md`.

### W4.12 — Localized Identity console

Add a dedicated Identity destination for current principal, OIDC readiness, identities/roles,
session revocation, and recovery health without overloading the API-key Access page.

Implementation slices:

1. Add the `/identity` navigation destination, assembled fragment/style/script assets, and static
   console contract tests. Render current-principal, OIDC-readiness, and recovery summaries from
   the exact W4.11 response shapes with explicit loading, unavailable, and permission-denied states.
2. Add bounded identity inventory pagination plus create, enable/disable, and direct-role workflows.
   Derive every control from effective permissions, preserve submitted values on HTTP 409, and use
   explicit native-dialog confirmation for owner or access-removing changes.
3. Add bounded active-session inventory and revocation, plus OIDC authorization-epoch advancement.
   Mark the current session clearly, confirm disruptive actions, refresh affected resources after
   success, and surface incomplete eager revocation without weakening durable invalidation.
4. Add a dedicated curated Identity locale catalog for all 15 supported locales and responsive
   design-system styling. Enforce semantic headings, labels, status/live regions, focus containment
   and return, reduced motion, no horizontal overflow, and no secret-named DOM or browser storage.
5. Close static/API integration, JavaScript syntax, i18n, permission, stale-revision, DOM-secret,
   accessibility, theme, locale, console/network, and 360/768/1024/1440 browser matrices. Run a
   fresh-context adversarial review, reconcile findings, document the operator experience, commit
   W4.12, and then execute checkpoint W4-B.

- Acceptance: controls follow server permissions, risky changes use explicit confirmation, all 15
  locales are curated, and no session/OIDC secret enters DOM or browser storage.
- Verification: 360/768/1024/1440, themes, locales, keyboard/focus, stale revision, clean
  console/network, and permission matrix browser tests.
- Dependencies: W4.11.
- Likely files: Identity fragment/feature/CSS/locales and frontend tests.
- Completed in `0d1f608`: the dedicated permission-derived Identity console, bounded inventories,
  guarded mutations, 15 curated locales, responsive styling, authentication-boundary cleanup, and
  executable client contracts are active. Cross-model findings corrected pagination re-entrancy
  and create-conflict semantics. Authenticated browser closure additionally corrected exact token
  normalization, legacy alias translation, and Escape handling. All 960 tests pass with 14 opt-in
  external-backend skips; Ruff lint/format, compileall, pip consistency, 45 JavaScript syntax
  checks, diff, dependency audit, and the 360/768/1024/1440 browser matrix pass.

Checkpoint W4-B follows W4.7–W4.12: protocol, abuse, API, audit, migration, recovery, i18n,
accessibility, and authenticated browser gates pass before distributed-state work.

Checkpoint W4-B completed on 2026-08-29 after the W4.7–W4.12 protocol, abuse, identity, session,
audit, recovery, i18n, accessibility, dependency, full-regression, and authenticated browser gates
all passed. OIDC remains disabled by default and the supported runtime remains one worker and one
replica until W4-C.

### W4.13 — Durable-ledger inventory and migration contract

Inventory every usage/audit/trace/config/credential/identity record and define resumable copy,
checksum, authority-switch, and rollback checkpoints without indefinite dual-write.

Implementation slices:

1. Commit the closed versioned durable-record inventory and authority/checkpoint state machine,
   including explicit usage-ledger and reservation-journal readiness gaps.
2. Add strict record, manifest, checkpoint, repository, and copy/verification interfaces. Begin
   with failing abuse and transition tests; keep payloads outside metadata and exceptions.
3. Add a bounded one-page-at-a-time runner with idempotent replay, keyed canonical checksums,
   optimistic checkpoint updates, fail-closed corruption handling, and no automatic authority
   switch.
4. Add durable checkpoint repositories behind the storage adapter and prove optimistic conflict,
   corruption, restart/resume, and backend selection behavior.
5. Publish the operator contract, reconcile an adversarial review, run repository-wide gates,
   restart the committed standalone service, and leave all activation controls unchanged.

Completed on 2026-08-29. Commits `ed707cc`, `691984b`, `6ed71e8`, and `f7ba28b` define the canonical
manifest, strict resumable runner, three checkpoint repositories, and adversarial hardening. The
usage ledger and hard-budget reservation journal deliberately remain not ready, so W4.13 cannot
reach authority activation. All 987 tests pass with 14 opt-in live-backend skips; repository gates
are clean. The maintained operator contract and review reconciliation are published with the
closure checkpoint.

- Acceptance: each record has one authoritative backend at every step; incomplete verification
  leaves standalone authoritative and can resume idempotently.
- Verification: interruption, duplicate, corruption, checksum, restart, and rollback tests.
- Dependencies: W4-B.
- Likely files: migration contract/runner, storage adapter, tests, operator guide.
- Maintained detailed contract: `docs/specs/durable-ledger-migration.md`.

### W4.14 — Durable usage and backend parity

Move remaining usage/cost ledger records behind selected-backend repositories and complete live
SQLite/PostgreSQL/MongoDB parity.

Implementation slices:

1. Commit the strict usage-entry/reservation domain, async repository interface, threat model, and
   migration/authority contract with failing abuse and concurrency tests.
2. Implement real SQLite append/report/reserve/commit/release/reconcile semantics and additive
   verified import from legacy `usage_stats.db`.
3. Move the runtime `usage_stats` compatibility facade and its call sites to the async repository;
   prove no silent zero, double commit, or private local database remains on the selected path.
4. Implement PostgreSQL and transaction-capable MongoDB repositories against the same contract,
   with deterministic driver-boundary tests and opt-in live parity suites.
5. Integrate durable hard-budget journal admission/settlement with the in-process quota store while
   leaving RPM/TPM coordination and Redis semantics for W4.15.
6. Reconcile an adversarial review, publish migration/operations evidence, run repository-wide
   gates, restart the committed standalone service, and leave every HA control unchanged.

- Acceptance: estimate/commit/release/reconcile and reporting survive restart/migration with no
  double count or silent zero during outage.
- Verification: concurrency, restart, migration, ledger-outage, and live backend tests.
- Dependencies: W4.13.
- Likely files: usage repository implementations, adapter, focused parity tests.
- Maintained detailed contract: `docs/specs/durable-usage-ledger.md`.

Completed on 2026-08-30. Commits `aa3ab21`, `4443e4c`, `8bbae51`, `9860eb8`, `2dd0fbd`, `d0f1e98`,
`763fd36`, `d51f5c0`, `52e707c`, `5d61244`, `8447ab0`, and `763662f` define the strict domain,
SQLite authority/import, selected-backend lifecycle and reporting, PostgreSQL/MongoDB parity,
runtime hard-budget settlement, and adversarial hardening. All 1,042 tests pass with 18 opt-in live
backend skips; repository gates and the dependency audit are clean. Migration switch readiness
remains fail-closed until W4.18 supplies production adapters, live evidence, and operator tooling.

### W4.15 — Redis semantic primitive parity

Implement versioned atomic compare-and-set, reserve/commit/release, expiry, replay, invalidation,
and fencing-epoch semantics against Redis without exposing Redis commands to callers.

- Acceptance: in-process and Redis implementations pass the same contract; unknown state, stale
  epoch, partial execution, and duplicate delivery fail safely.
- Verification: live Redis atomicity, expiry, restart, cancellation, and fault-injection tests.
- Dependencies: W4.14.
- Likely files: state-store interface/Redis implementation, contract tests, configuration.

Completed on 2026-09-02. Commits `a60dcf9` through `be5e3b7` deliver the strict contract,
in-process reference, Redis transport/Lua semantics, quota lifecycle, metrics/live-test harness,
and reconciled adversarial fixes. The complete backend suite passes 1,147 tests with 25 explicit
opt-in live-backend skips; Ruff lint/format, compileall, pip consistency/audit, JavaScript, YAML,
shell, secret, and diff gates pass. The committed standalone runtime has exactly one listener and
HTTP 200 health/readiness. Redis remains inactive: W4.18 owns namespace-loss protection and W4.19
must measure or redesign the bounded O(n) quota scan before activation.

### W4.16 — Coordinate identity and security state

Move management sessions, login throttles, OIDC replay/nonce state, and authorization invalidation
to the W4.15 boundary.

- Acceptance: logout/revocation/role changes are visible across processes and an unavailable store
  cannot create a session or authorize stale privilege.
- Verification: cross-process login/revoke/replay, partition, expiry, and recovery tests.
- Dependencies: W4.15.
- Likely files: session/OIDC/throttle adapters, integration tests.
- Maintained specification: `docs/specs/identity-security-coordination.md`.
- Detailed execution plan:
  `docs/superpowers/plans/2026-09-02-w4.16-identity-security-coordination.md`.

Implementation slices:

Progress: complete in `f0c66bd` plus the W4.16 closure record. The shared domain, in-memory/Redis
parity, session/authentication/OIDC adapters, live harness, metrics, adversarial reconciliation,
1,195-test full suite, repository gates, and committed standalone runtime smoke pass. Twenty-nine
live-backend cases skip explicitly. Runtime selection and HA activation remain unchanged.

1. Define the strict opaque security-state domain and reusable behavioral fixture.
2. Implement the in-process fenced reference for sessions, attempts, and one-time transactions.
3. Add Redis session lifecycle/index parity through fixed bounded Lua.
4. Add Redis throttle and OIDC transaction parity through fixed bounded Lua.
5. Move the session service behind the typed boundary while standalone remains in-memory.
6. Replace process-local login/recovery/OIDC-start throttles with atomic attempt coordination.
7. Move OIDC transaction persistence behind the typed boundary.
8. Add opt-in live parity and low-cardinality operability evidence.
9. Reconcile adversarial review, run repository gates, and restart the committed standalone
   checkpoint without activation.

### W4.17 — Coordinate routing, governance, and cache state

Move credential reservations/cooldowns, rate/budget reservations, response-cache metadata, and
invalidation to the Redis boundary.

- Acceptance: no process-local supported state can change admission, hard budget, routing, or cache
  correctness in coordinated mode.
- Verification: multi-process overspend, duplicate selection, stale cache, failover, and
  reconciliation tests.
- Dependencies: W4.15–W4.16.
- Likely files: routing/quota/cache state adapters and fault-injection tests.

### W4.18 — HA deployment gate, probes, alerts, and rollback

Add explicit standalone/coordinated configuration, prerequisite validation, migration/reconciliation
readiness, topology ceiling, low-cardinality alerts, and executable operator runbooks.

- Acceptance: templates remain one replica by default; unsafe combinations fail startup/readiness;
  secrets are redacted; drain/reconcile/rollback is executable.
- Verification: configuration matrix, container/Helm render, probe/alert, backup, and rollback smoke.
- Dependencies: W4.13–W4.17.
- Likely files: deployment templates, readiness/metrics, migration/rollback scripts, runbooks/tests.

### W4.19 — Failure/load evidence and activation record

Run the accepted two-replica and target worker topology through dependency loss, restart,
split-brain/stale epoch, migration, reconciliation, and measured load tests.

- Acceptance: ADR-008 correctness/recovery/performance targets pass and a separate activation ADR
  records exact versions/topology/evidence before superseding ADR-002's limit.
- Verification: reproducible reports, dashboards, full repository/security/container/browser gates,
  committed restart, and human acceptance.
- Dependencies: W4.18.
- Likely files: load/failure harness, CI jobs, activation ADR, evidence docs.

Checkpoint W4-C closes Wave 4 only after W4.13–W4.19, all Phase 6 criteria and repository gates,
the committed coordinated canary/rollback evidence, and human acceptance. Production release
activation remains Wave 5.

## Phase 0: Baseline and Decision Records

### Task 0.1 — Approve the enterprise specification

Confirm `docs/specs/enterprise-overhaul.md`, this plan, and `tasks/todo.md`.

### Task 0.2 — Record policy-plane and capability decisions

Create proposed ADRs for the AI policy plane, provider-operation capabilities, and enterprise
state model. Acceptance requires explicit alternatives and rollback consequences.

## Phase 1: Console and Localization Foundation

### Task 1.1 — Theme foundation

Add `system`, `light`, and `dark` theme selection using design tokens and pre-render
initialization. Verify no theme flash, contrast regression, or broken provider asset.

### Task 1.2 — Navigation and page ownership

Add AI Quality and Access destinations, move root-key operations out of Overview, and keep old
deep links working. Overview must contain operational information only.

### Task 1.3 — Keyed localization gate

Add a user-visible-string audit, remove the known Vietnamese/English leaks, and begin replacing
positional translation arrays with keyed values. All 15 catalogs must remain complete.

### Checkpoint 1

- Full tests, lint, JS syntax, i18n audits, and desktop/mobile browser checks pass.
- Existing console routes and root API-key behavior remain compatible.

## Phase 2: AI Quality Center

### Task 2.1 — Versioned quality-policy domain

Add typed profiles, validation, precedence, and migration from the existing compression,
reasoning, anti-truncation, guardrail, and cache keys. Existing config remains readable.

### Task 2.2 — Quality-policy management API

Add authenticated read/update/preview endpoints with optimistic version checks and stable error
codes. Environment-locked fields must be reported explicitly.

### Task 2.3 — Compression safety and decision record

Strengthen structural invariants, add skip reasons and metrics, and ensure guardrails fail closed
when enabled but unavailable. No semantic compression is introduced.

### Task 2.4 — AI Quality page

Build profile cards, advanced controls, dependency-aware enable/disable behavior, a safe preview,
impact explanations, and restore-defaults behavior.

### Checkpoint 2

- A policy can be previewed and changed end-to-end.
- Request traces/usage expose the selected profile and compression decision.
- The full long-context and tool-pair fixture suite passes.

## Phase 3: Provider and Credential Fleet

### Task 3.1 — Provider operation capability contract

Extend the registry with credential variants and operation capabilities. Add consistency tests
covering every provider exposed by the console.

### Task 3.2 — Capability-enforced credential operations

Validate single and batch actions server-side, return per-item typed outcomes, and add a dry-run
operation preview for mixed selections.

### Task 3.3 — Faceted credential filtering

Add provider variant, credential kind, health, cooldown, quota, tier, and source facets with
stable pagination and preserved filter state.

### Task 3.4 — Context-aware bulk action UX

Show only common valid actions, explain excluded items, distinguish page/all-results selection,
and summarize mixed-provider results without hard-coded English.

### Task 3.5 — Provider form correctness

Audit all provider inputs, secret fields, required/bounds/autocomplete attributes, help text,
advanced sections, and provider-specific reset behavior.

### Checkpoint 3

- Mixed-provider operation matrix passes at API and browser levels.
- No provider-only action appears as generally applicable.
- Filters remain correct with empty, large, and changing pools.

## Phase 4: Access Governance and Audit

### Task 4.1 — Append-only audit events

Add the audit domain and storage API, request correlation, redacted mutation hooks, filtering,
retention settings, and export.

### Task 4.2 — Scoped virtual-key model

Add scopes, concurrency-safe reservations, unknown-pricing policy, last-used metadata, and
revoke/rotate semantics while preserving existing keys.

### Task 4.3 — Access page

Build root-key integration guidance and virtual-key CRUD, one-time reveal, copy confirmation,
budgets, limits, expiry, model patterns, scopes, status, usage, and revoke flows.

### Checkpoint 4

- Every management mutation creates one redacted audit event.
- Key secrets are never returned after creation and never appear in logs/DOM after dismissal.
- Concurrent limit/budget tests pass.

## Phase 5: Observability and Operations

### Task 5.1 — Request decision trace

Persist bounded trace summaries for routing attempts, fallback, compression, guardrails, cache,
tokens, cost, latency, and outcome.

### Task 5.2 — Observability console

Add trace search/detail and keep raw runtime logs in a separate tab. Include request-ID lookup,
provider/model/key filters, retention status, and redacted export.

### Task 5.3 — SLO health and alerts

Add p50/p95/p99 latency, error rate, credential/quota/budget exhaustion, storage health, unknown
pricing, alert-ready status, and low-cardinality metrics.

### Checkpoint 5

- A failed request is diagnosable by request ID without reading raw prompt content.
- Metric cardinality, retention bounds, and trace redaction tests pass.

## Phase 6: Enterprise Identity and High Availability

### Task 6.1 — RBAC, OIDC, and HA activation ADRs

Specify actor, role, session, OIDC, emergency owner access, migration, and lockout recovery before
implementation. Separately specify coordinated-state prerequisites, failure posture, measurable HA
targets, staged activation, and rollback before distributed implementation or scale-out.

### Task 6.2 — Roles and identity

Implement viewer/operator/security-admin/owner authorization with server-side route enforcement,
OIDC, session revocation, and audit coverage. SCIM remains a separate follow-up unless approved.

### Task 6.3 — Durable usage ledger

Move usage/traces/audit to the selected storage backend with forward migration, rollback, and live
SQLite/PostgreSQL/MongoDB integration tests.

### Task 6.4 — Distributed runtime state

Move sessions, rate/budget reservations, credential reservations, cooldowns, response cache, and
invalidation behind Redis-capable state interfaces.

### Task 6.5 — Earn scale-out support

Add multi-worker/multi-replica failure, restart, split-brain, and load tests; only then supersede
ADR-002 and change deployment replica limits.

### Checkpoint 6

- Authorization matrix and lockout-recovery tests pass.
- No supported state remains process-local in multi-replica mode.
- Controlled failover preserves limits, audit, and usage accounting.

## Phase 7: Release Hardening

### Task 7.1 — Security and performance review

Run threat modeling, secret scanning, dependency audit, malformed-input tests, and measured hot-path
profiling. Resolve or explicitly accept every finding.

### Task 7.2 — Documentation and migration

Update architecture, operator guide, API docs, upgrade/rollback instructions, screenshots, locale
documentation, changelog, and release checklist.

### Task 7.3 — Staged launch

Ship behind feature flags where appropriate, run container and deployment smoke tests, canary the
new policy plane, verify telemetry, and retain a tested rollback image/data path.

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Broad rewrite destabilizes SDK traffic | High | Additive APIs, vertical slices, full contract gates |
| Compression saves tokens but harms answer quality | High | Structural-only engine, explicit off/quality mode, eval gate |
| UI claims an action unsupported by a provider | High | One authoritative capability contract enforced server-side |
| Localized catalogs drift | Medium | Keyed catalogs, static literal gate, 15-locale parity tests |
| Budgets overshoot under concurrency | High | Reservation model and atomic state operations |
| HA advertised before state is distributed | Critical | Keep worker/replica restriction until checkpoint 6 |
| Trace/audit leaks prompts or secrets | Critical | Allowlisted fields, redaction tests, bounded exports |
| RBAC locks out operators | High | Emergency owner path, staged migration, recovery tests |

## Open Questions

No decision gate blocks W4.12. The accepted constraints keep SCIM and tenant isolation out of Wave
4, use exact OIDC issuer/subject identity, approve an audited `PyJWT[crypto]` addition in W4.7, and
require 99.9% end-to-end availability, 60-second supported failover recovery, zero correctness
violations, and bounded performance impact before coordinated activation. Enabling OIDC by default,
disabling local recovery, changing role bundles, live migration, and scale-out still require their
explicit later gates.
