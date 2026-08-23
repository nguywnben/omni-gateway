# Implementation Plan: Omni Gateway Enterprise Overhaul

## Overview

Deliver the enterprise overhaul as reversible vertical slices. The first release establishes the
UX and policy foundation, the second governs credentials and access, the third adds operational
evidence, and the final program phases earn multi-tenant and multi-replica claims.

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
