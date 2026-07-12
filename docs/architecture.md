# Architecture

This document describes the current Omni Gateway architecture, its dependency rules, runtime state, and the planned decomposition of the largest modules. It documents boundaries rather than duplicating implementation details.

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
    panel/                Authenticated management API
    provider_registry.py  Provider identity and capability metadata
    smart_routing.py      Provider and credential selection policy
    storage_adapter.py    Persistence boundary used by the application
  tests/                   Regression and contract tests
frontend/                 Browser console and provider assets
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

`WORKERS=1` is the supported default for local SQLite and file storage. Multiple workers or replicas need a shared database, distributed coordination for reservations/cooldowns, and centralized usage aggregation. MongoDB and PostgreSQL storage adapters are available, but multi-instance operation should be load-tested against the selected backend before production rollout.

The Render Blueprint deliberately uses a paid persistent disk. Free Render services have ephemeral filesystems and are not suitable for durable credential storage.

## Security Boundaries

- Public inference requests use the generated API key; browser management routes use HttpOnly session cookies.
- Forwarded client and protocol headers are ignored unless `TRUST_PROXY_HEADERS=true`.
- Uploaded archives and credentials are validated by provider-specific import paths before persistence.
- Credential values must never appear in logs, issue reports, filenames, or UI summaries.
- Cross-origin browser access is disabled unless explicit origins are configured.

## Planned Decomposition

The following changes should be delivered as separate, regression-tested refactors rather than one rewrite:

```text
frontend/control-panel.js
  -> frontend/js/api/
  -> frontend/js/components/
  -> frontend/js/pages/
  -> frontend/js/state/

backend/core/panel/credentials.py
  -> backend/core/panel/credentials/routes.py
  -> backend/core/panel/credentials/imports.py
  -> backend/core/panel/credentials/actions.py
  -> backend/core/panel/credentials/schemas.py

backend/core/converter/{openai,anthropic}_to_gemini.py
  -> request.py, response.py, tools.py, streaming.py per format package
```

Additional priorities are migrating the deprecated Motor dependency to PyMongo's asynchronous API, replacing repeated broad exception handling with typed boundary errors, auditing dynamic SQL fragments, and introducing a cross-platform dependency lock for deterministic release builds.

## Change Policy

Public SDK routes and payload contracts require compatibility tests. Storage schema changes require forward migration and rollback notes. Provider-specific changes must remain behind provider capability boundaries. Architectural decisions that are expensive to reverse should be recorded under `docs/decisions/` as ADRs.

Current decisions:

- [ADR-001: Preserve SDK-Compatible API Boundaries](decisions/001-sdk-compatible-api-boundaries.md)
