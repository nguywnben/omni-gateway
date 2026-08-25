# Implementation Plan: Omni Gateway Enterprise Overhaul

## Overview

Deliver the enterprise overhaul as reversible vertical slices. The first release establishes the
UX and policy foundation, the second governs credentials and access, the third adds operational
evidence, and the final program phases earn multi-tenant and multi-replica claims.

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
| 3 — Access and operational evidence | Phases 4–5 | Access governance, complete audit, traces, SLOs | In progress |
| 4 — Identity and scale | Phase 6 | RBAC/OIDC, durable state, coordinated HA | Not started |
| 5 — Production release | Phase 7 | Security/performance hardening and staged launch | Not started |

Wave boundaries organize delivery; phase checkboxes continue to describe product completion.
Wave 2 may introduce credential mutation audit hooks and bounded operation telemetry because batch
operations are not enterprise-safe without evidence. This does not complete Phase 4 audit coverage
or Phase 5 request tracing.

## Current Approval Gate

- Wave 2 completion checkpoint: commit `578fbb4` (`fix: complete provider form localization`).
- Completed product scope: Phases 0–3.
- Active approved scope: Wave 3 / Phases 4–5 only.
- State: **IMPLEMENTING — WAVE 3**; approved by the human on 2026-08-24 after Wave 2 was pushed.
- Out of scope until later approval: RBAC/OIDC, distributed-state activation, multiple
  workers/replicas, destructive migration, and production release activation.

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

Checkpoint W3-C closes Wave 3 only when Phase 4–5 acceptance passes end-to-end, all repository
quality gates pass, the committed service restarts cleanly, and the human accepts the completion
report. Phase 6 remains unapproved and multi-worker/multi-replica mode remains disabled.

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

### Task 6.1 — RBAC and OIDC ADR

Specify actor, role, session, OIDC, emergency owner access, migration, and lockout recovery before
implementation.

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

None blocks phases 1-4. OIDC provider compatibility, SCIM scope, and the exact multi-replica SLO
are decided in dedicated ADRs before phase 6.
