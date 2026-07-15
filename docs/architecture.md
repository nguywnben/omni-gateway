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
    xai.py                Grok OAuth, xAI model discovery, and transport translation
    provider_registry.py  Provider identity and capability metadata
    smart_routing.py      Provider and credential selection policy
    storage_adapter.py    Persistence boundary used by the application
  tests/                   Regression and contract tests
frontend/
  js/                     Console scripts split by UI responsibility
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

## State and Scaling

The default single-instance mode stores credentials, configuration, and usage data under `backend/data/creds`, with logs under `backend/data/logs`. Both locations must be persisted in containers.

`WORKERS=1` and one application replica are the supported process model for the 1.x series. MongoDB and PostgreSQL can replace local SQLite storage, but shared storage alone does not coordinate reservations, cooldowns, sessions, or usage aggregation across workers. The service rejects `WORKERS` values other than `1` instead of presenting an unsafe scale-out configuration as supported.

The Render Blueprint deliberately uses a paid persistent disk. Free Render services have ephemeral filesystems and are not suitable for durable credential storage.

## Security Boundaries

- Public inference requests use the generated API key; browser management routes use HttpOnly session cookies.
- Direct loopback setup remains frictionless. Remote first-run setup requires a bootstrap token from `SETUP_TOKEN` or the application logs.
- Runtime-log WebSockets require a matching console origin and authenticate only through the HttpOnly session cookie; credentials are never accepted in their URLs.
- Forwarded client and protocol headers are ignored unless `TRUST_PROXY_HEADERS=true`.
- Uploaded archives and credentials are validated by provider-specific import paths before persistence.
- Fixed-length and chunked HTTP bodies are bounded before application parsers allocate request data.
- Credential values must never appear in logs, issue reports, filenames, or UI summaries.
- Provider tokens remain retrievable for upstream calls, so the deployment boundary must protect storage with least-privilege access and platform-level encryption at rest.
- Cross-origin browser access is disabled unless explicit origins are configured.

## Module Decomposition

The first decomposition stage is complete:

```text
frontend/js/
  core.js                 Localization, shared state, and manager factories
  ui.js                   Dialogs, result views, and credential-card rendering
  console.js              Authentication, navigation, model pool, and OAuth flows
  credentials.js          Credential pool actions and batch operations
  settings.js             Logs, provider settings, and system configuration
  dashboard.js            Usage, version, responsive controls, and startup

backend/core/panel/
  credentials.py          Credential HTTP routes
  credential_operations.py Reusable import, dedupe, download, and verification logic
  auth.py                 Login, setup, OAuth, and API-key routes
  auth_support.py         Login throttling and response shaping
  environment_credentials.py Environment credential import routes
  setup_security.py       Remote first-run bootstrap policy
```

Further decomposition should happen only with behavior-preserving contract tests:

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
