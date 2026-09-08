# Omni Gateway Production Constraints

## Status

- Baseline: `PROD-SELFHOST-R1`
- Effective date: 2026-09-08
- Target: production-quality self-hosting for one person or a small trusted team.
- This file is the quality contract. A task is not complete if it weakens these constraints.

## Product Boundary

Omni Gateway is a self-hosted AI gateway, not a hosted commercial control plane. The supported
production baseline is one application instance on one machine, normally installed with Docker
Compose. It must remain useful without Redis, PostgreSQL, MongoDB, Kubernetes, an external identity
provider, or an observability vendor.

The expected deployment serves 1–20 trusted users and modest personal/team traffic. Features may
support larger deployments, but enterprise-scale, multi-tenant, billing, active-active, formal SLA,
and compliance-platform requirements are outside this baseline.

## Capability Tiers

| Tier | Meaning | Capabilities |
| --- | --- | --- |
| Core production | Must work, be documented, and block release when broken | Single-instance runtime, Docker Compose, SQLite, local owner login, provider and credential management, model routing, OpenAI/Anthropic/Gemini/Vertex-compatible APIs, streaming, retries/fallback, AI Quality policy, virtual keys, usage/cost, activity, backup/restore, Playground |
| Advanced production | Supported and tested, but optional | PostgreSQL, OIDC team login and roles, Prometheus/OTLP/Langfuse export, reverse-proxy deployment |
| Compatibility | Kept for existing users; no feature-parity expansion | MongoDB storage, platform-specific install scripts, existing hosted-platform descriptors, non-English/non-Vietnamese community translations |
| Experimental | Disabled by default; never described as production-ready | Redis coordinated mode, multiple workers/replicas, HA lifecycle and activation, Helm/ServiceMonitor/PrometheusRule deployment |

Experimental failure cannot block the core production release. Experimental code must not make a
default installation less secure, slower, or harder to configure.

## Required User Journeys

Every core journey must have an automated contract test and a browser smoke path:

1. Install with Docker Compose, finish first-run setup, and reach a healthy dashboard.
2. Add a provider credential, validate it, discover models, and understand a failure.
3. Create a model route and receive both streaming and non-streaming responses.
4. Inspect and change an AI Quality profile, including disabling compression.
5. Exercise a route in Playground and copy an equivalent request without exposing secrets.
6. Create, use, rotate, and revoke a virtual key.
7. Inspect usage, cost, routing decisions, and redacted activity by request ID.
8. Create a backup, validate it, restore it, and roll back an application update.
9. Enable optional team login without losing local-owner recovery.

## Quality Gates

### Correctness

- Zero failures in the required unit, contract, integration, container-smoke, and browser-smoke
  suites for a release candidate.
- No skipped test may cover a core production path. Live-provider and optional-backend tests must
  be explicitly labeled and reported separately.
- Changed backend logic requires focused tests. Changed user behavior requires a browser or DOM
  contract test. Bug fixes require a regression test.
- Public protocol behavior remains backward compatible throughout R1 unless a migration and
  deprecation notice are accepted in writing.

### Security and privacy

- Zero known critical or high-severity runtime dependency vulnerabilities at release.
- Secrets are never placed in URLs, logs, activity payloads, browser storage, exports, or committed
  configuration. Plaintext secrets are revealed only when a workflow strictly requires it.
- Authentication, session, backup/restore, imports, and provider callbacks fail closed.
- Default cookies, CORS, proxy-header trust, file permissions, and container privileges are safe.
- No new suppression (`# noqa`, `type: ignore`, skipped test, disabled lint rule) without an inline
  reason and a linked plan task.

### AI output quality

- Compression is transparent, reversible at configuration level, and off for a request whenever
  safety invariants cannot be proven.
- Compression never removes system instructions, tool definitions, the active user request,
  unmatched tool calls/results, or required structured payloads.
- Each compressed request reports original/final token estimates, chosen profile, action, and
  reason without storing prompt content.
- `quality` is the safest preset and `balanced` is the documented default. Users can disable
  compression globally and per allowed request/key policy.
- Retry, fallback, cache, guardrail, and reasoning transformations must be visible in the request
  trace and must not silently change API semantics.

### Performance and resource use

- Establish the baseline before optimization. The release gate is a reproducible 10-minute local
  synthetic run at 10 requests/second and 16 concurrent requests against a deterministic upstream.
- Gateway-added p95 latency must be at most 100 ms, excluding upstream generation time; gateway
  error rate must be below 0.1%; memory must remain bounded without monotonic growth.
- The authenticated dashboard should reach usable content within 2.5 seconds on a warmed localhost
  desktop run. No core page may issue an unbounded list request.
- Performance targets may only be relaxed through the change-control process below.

### Accessibility and interface

- Core pages work at 360, 768, 1024, and 1440 CSS pixels without horizontal overflow.
- Keyboard navigation, visible focus, dialog focus containment, labels, accessible names, status
  announcements, and contrast meet WCAG 2.2 AA intent.
- Browser smoke covers current Chromium. Firefox is manually checked for the release candidate;
  browser-specific defects are documented rather than silently ignored.
- English and Vietnamese are curated production locales. Other existing locales retain automated
  key completeness and English fallback but are community-maintained compatibility locales.

### Maintainability

- Do not add a new runtime framework or service unless an ADR proves that the existing stack cannot
  satisfy an accepted task.
- New or materially changed modules target at least 80% changed-line coverage.
- A file may grow beyond 1,500 lines only when splitting it would make ownership less clear; any
  touched file already above that size requires a small extraction assessment in the task report.
- Configuration has one authoritative schema. Basic setup exposes at most 20 user-facing options;
  advanced and experimental options remain available in separately documented sections.
- User-visible copy added or changed in English must have a reviewed Vietnamese equivalent.

## Verification Cadence

- During a task: run focused tests and the directly affected static checks.
- At a phase boundary: run the affected integration/browser slice once.
- At release: run the full required gate once. After a failure, rerun the failed slice; repeat the
  full gate only after all failures are corrected.
- A soak or matrix has a written duration and case count before it starts. It must never run
  indefinitely or expand because a new observation is merely interesting.
- Cross-model review is limited to one pass for authentication, secret handling, import/restore,
  or another explicitly security-critical change, unless the user requests more.

## Change Control

The fixed plan is `tasks/plan.md`. Its six phases and 36 task identifiers are immutable for R1.
Defects found while implementing a task are resolved inside that task; they do not create a new
Wave, phase, suffix, or denominator.

The plan may change only when at least one condition is true:

1. A critical/high security issue, data-loss risk, or impossible core installation is discovered.
2. An acceptance criterion is technically impossible or contradicts another accepted criterion.
3. A required provider or upstream protocol makes a breaking change.
4. The user explicitly changes the product boundary.

Every change requires a short `CR-###` record in `tasks/plan.md` containing evidence, affected task
IDs, removed/added scope, schedule impact, and user approval. Improvements that do not meet these
conditions go to the post-R1 backlog and cannot delay R1.

## Forbidden Scope Creep

- No active-active, auto-scaling, commercial billing, organization hierarchy, SAML/SCIM, policy
  engine, plugin marketplace, Kubernetes operator, or compliance certification in R1.
- No additional storage backend, identity provider protocol, telemetry vendor, frontend framework,
  or provider family unless required to repair an existing advertised capability.
- No rewriting stable subsystems solely to make them more elegant.
- No claim of “enterprise-ready”, HA-ready, or SLA compliance in R1 documentation.
