# Architecture

This document describes the current Omni Gateway architecture, dependency rules, runtime state, completed module boundaries, and release constraints. It documents boundaries rather than duplicating implementation details.

## System Context

```text
OpenAI SDK     Anthropic SDK     Google GenAI SDK     IDE and CLI clients
     \               |                  |                    /
      +--------------+------------------+-------------------+
                             |
                    SDK-compatible routers
                             |
                normalization and translation
                             |
             model policy and credential selection
                             |
             provider adapters and fallback execution
                             |
                  provider APIs and account pools
```

The public transport surface is namespace-neutral. Product branding appears in the management experience and documentation. Generated API keys retain the `sk-ogw-` prefix as an intentional token-identification rule.

## Repository Boundaries

```text
backend/
  main.py                 Application composition and process startup
  config.py               Environment, stored configuration, and defaults
  core/
    router/               HTTP contracts and SDK-specific request handling
    api/                  Provider request orchestration and retry lifecycle
    converter/            Pure request/response format translation
    storage/              Concrete persistence backends
    panel/                Authenticated management API and setup policy
    antigravity.py        Google Antigravity headers and per-credential model discovery
    xai.py               Grok OAuth, xAI Console model discovery, and transport translation
    provider_registry.py  Provider identity and capability metadata
    smart_routing.py      Provider and credential selection policy
    storage_adapter.py    Persistence boundary used by the application
  tests/                   Regression and contract tests
frontend/
  index.html              Console shell and ordered asset manifest
  fragments/              Auth, layout, and page-level HTML fragments
  css/                    Cascade-ordered style layers
  js/core/                Shared state, navigation, and manager factories
  js/ui/                  Reusable UI primitives and credential views
  js/features/            Page and workflow modules
  assets/                 Brand and provider assets
deploy/                   Container and hosting definitions
docs/                     Architecture and maintained project assets
```

Dependencies should flow inward from HTTP adapters to orchestration and domain policy. Conversion code must not perform network or storage operations. Routes must use the storage adapter rather than importing database drivers directly.

## Request Lifecycle

1. A router authenticates the client and validates its SDK-specific payload.
2. The request is normalized into the provider-neutral working representation.
3. Context optimization removes only oversized, safe-to-drop history prefixes.
4. Model-pool policy resolves virtual models to ordered provider model candidates.
5. Smart routing reserves a compatible, healthy credential and applies cooldown and concurrency signals.
6. The provider adapter translates and sends the upstream request.
7. Recoverable failures trigger bounded credential or model fallback.
8. The response is translated to the originating SDK format and streamed or returned.
9. Usage, latency, token, retry, and credential-health results are recorded asynchronously.

Model eligibility is evaluated before a request is sent. A declared model catalog on a credential is authoritative; provider-prefix inference is used only when no catalog has been stored. A provider model-not-found response creates a credential-scoped negative route cache, so a missing entitlement on one account does not disable the same model for other accounts.

## State and Scaling

The default single-instance mode stores credentials, configuration, and usage data under `backend/data/creds`, with logs under `backend/data/logs`. Both locations must be persisted in containers.

`WORKERS=1` and one application replica are the supported process model for the 1.x series. MongoDB and PostgreSQL can replace local SQLite storage, but shared storage alone does not coordinate reservations, cooldowns, sessions, or usage aggregation across workers. The service rejects `WORKERS` values other than `1` instead of presenting an unsafe scale-out configuration as supported.

The Render Blueprint deliberately uses a paid persistent disk. Free Render services have ephemeral filesystems and are not suitable for durable credential storage.

## Security Boundaries

- Public inference requests use the generated API key; browser management routes use HttpOnly session cookies.
- Direct loopback setup remains frictionless. Remote first-run setup requires a bootstrap token from `SETUP_TOKEN` or the application logs.
- Runtime-log WebSockets require a matching console origin and authenticate only through the HttpOnly session cookie; credentials are never accepted in their URLs.
- Forwarded client and protocol headers are ignored unless `TRUST_PROXY_HEADERS=true`.
- Imported archives and credentials are validated by provider-specific paths before persistence.
- Fixed-length and chunked HTTP bodies are bounded before application parsers allocate request data.
- Credential values must never appear in logs, issue reports, filenames, or UI summaries.
- Provider tokens remain retrievable for upstream calls, so the deployment boundary must protect storage with least-privilege access and platform-level encryption at rest.
- Cross-origin browser access is disabled unless explicit origins are configured.

## Module Decomposition

The management console is assembled server-side from repository-owned fragments. The browser still receives one complete DOM, so route behavior and accessibility relationships do not depend on client-side template loading.

CSS and JavaScript remain split into reviewable source modules. The panel router concatenates each ordered manifest into one versioned, immutable browser bundle, which preserves module ownership without multiplying production network requests.

```text
frontend/
  index.html
  fragments/
    auth/                  Login and first-run setup
    layout/                Sidebar, mobile header, and footer
    pages/                 One fragment per console route
  css/
    foundation.css         Tokens, reset, typography, and base elements
    shell.css              Authentication and application layout
    providers-and-models.css
    forms-and-data.css
    components.css
    dialogs.css
    responsive.css         Breakpoint overrides loaded last
  js/
    core/                  Localization, navigation, state, and managers
    ui/                    Notifications, dialogs, API-key UI, and credential views
    features/              Authentication, pool, models, providers, settings, and logs

backend/core/panel/
  credentials.py          Credential HTTP routes
  credential_operations.py Reusable import, dedupe, download, and verification logic
  auth.py                 Login, setup, OAuth, and API-key routes
  auth_support.py         Login throttling and response shaping
  environment_credentials.py Environment credential import routes
  setup_security.py       Remote first-run bootstrap policy
  providers/
    catalog.py            Provider capability discovery
    antigravity.py        Google Antigravity settings
    google_ai_studio.py   Google AI Studio settings and imports
    xai.py                Grok OAuth and xAI Console settings and imports
    import_utils.py        Shared bounded-import policy
```

Module size is a review signal, not a target. A file is split when it owns independent workflows, provider contracts, or UI layers. Cohesive translation algorithms and storage adapters remain intact even when long because arbitrary slicing would increase coupling without creating a stable boundary.

Further converter decomposition should happen only when request, response, tool, and streaming contracts can be separated with behavior-preserving tests:

```text
backend/core/converter/{openai,anthropic}_to_gemini.py
  -> request.py, response.py, tools.py, streaming.py per format package
```

The storage drivers interpolate only table and column identifiers selected from internal allowlists; all credential values remain parameterized. Future storage work should consolidate those safe identifier builders, replace repeated broad exception handling with typed boundary errors, and add live integration suites for PostgreSQL and MongoDB.

Production dependencies are compiled into `requirements.lock` with hashes. `requirements.txt` remains the human-maintained input, and CI rejects stale lock output.

## Change Policy

Public SDK routes and payload contracts require compatibility tests. Storage schema changes require forward migration and rollback notes. Provider-specific changes must remain behind provider capability boundaries. Architectural decisions that are expensive to reverse should be recorded under `docs/decisions/` as ADRs.

Current decisions:

- [ADR-001: Preserve SDK-Compatible API Boundaries](decisions/001-sdk-compatible-api-boundaries.md)
- [ADR-002: Secure First Run and Enforce Single-Worker Operation](decisions/002-secure-first-run-and-single-worker.md)
- [ADR-003: Deployment-Scoped Model Eligibility and Negative Route Cache](decisions/003-deployment-scoped-model-eligibility.md)
