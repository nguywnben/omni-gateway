# Changelog

All notable user-facing changes are documented in this file. Omni Gateway follows [Semantic Versioning](https://semver.org/). The historical `0.x` beta series allowed breaking changes; compatibility changes after `1.0.0` require an appropriate major version.

## [Unreleased]

## [1.1.1] - 2026-07-15

### Changed

- Replaced Grok OAuth callback URL entry with the authorization code shown by xAI while preserving PKCE session validation.

## [1.1.0] - 2026-07-15

### Added

- Added Grok OAuth and xAI Console API-key credentials with model discovery, token refresh, pool backup restoration, and provider-aware routing.
- Added Grok request and response translation for text, image input, function tools, reasoning content, streaming, and provider-reported token usage.

### Fixed

- Scoped account deduplication by provider so OAuth accounts that share an email address across different providers remain independent.

## [1.0.0] - 2026-07-13

### Added

- Added provider-aware model discovery, credential model testing, virtual `omway` routing, and a manageable blacklist for unavailable virtual-model routes.
- Added Google AI Studio API-key credentials, JSON/ZIP import, model catalog discovery, credential backup restoration, and provider-specific pool views.
- Added stable OpenAI, Anthropic, and Google GenAI error envelopes across authentication, validation, upstream, and pre-stream failures.
- Added bounded request identifiers through `X-Request-ID` for client-side correlation.
- Added a configurable global request-body ceiling for fixed-length and chunked SDK requests.
- Added release-based update discovery that compares semantic versions against the latest published GitHub Release.
- Added first-class architecture, upgrade, security, contribution, and release-checklist documentation for the stable series.

### Changed

- Declared the SDK-compatible routes and canonical `/api/credentials` management routes as the 1.x compatibility baseline.
- Hardened configuration, credential-manager, and storage initialization so partial failures stop startup instead of exposing a split or misleading runtime state.
- Made explicit MongoDB or PostgreSQL configuration fail closed when unavailable, and rejected simultaneous external database selections.
- Moved default-branch container builds to the `edge` channel; `latest` now advances only for verified stable version tags.
- Pinned the official Python container base image by digest while retaining Dependabot updates.
- Removed inline browser event handlers and tightened the management console content-security policy.
- Improved first-run authentication state, bounded login-rate-limit memory, same-origin session enforcement, provider-error redaction, and shutdown cleanup.

### Removed

- Removed the beta `/api/creds` route aliases; integrations must use `/api/credentials`.
- Removed the ambiguous `PASSWORD`, `CLIENT_ID`, `CLIENT_SECRET`, `API_URL`, and other beta environment aliases in favor of the documented canonical names.

### Fixed

- Standardized "no credentials available" as `503 Service Unavailable` so SDK retry behavior is correct.
- Prevented startup races when initializing configuration, credential managers, and storage adapters.
- Prevented unauthenticated console startup probes from generating expected `401` errors in the browser console.

## [0.2.0-beta] - 2026-07-12

### Added

- Added secure remote first-run setup with an ephemeral or configured bootstrap token.
- Added a hash-locked production dependency set and reusable runtime/container smoke tests.
- Added canonical `/api/credentials` management routes while retaining hidden `/api/creds` aliases for beta migration.

### Changed

- Standardized internal module names, repository tooling, deployment defaults, and contributor documentation.
- Expanded CI across supported Python versions with linting, formatting, dependency auditing, route contracts, and runtime smoke tests.
- Gated Docker Hub and GHCR publication on successful verification and container smoke tests.
- Split the management console, authentication, and credential-management monoliths along behavioral boundaries.
- Migrated MongoDB storage from deprecated Motor to the official PyMongo Async API.
- Limited published container images to the fully verified `linux/amd64` provider stack.
- Declared single-worker operation as the supported runtime model until distributed reservations and usage aggregation are implemented.

### Fixed

- Removed an internal shortcut that intercepted a real `Hi` model prompt as a health check.
- Restricted forwarding-header trust to explicitly configured reverse-proxy deployments.
- Bounded provider credential uploads and ZIP extraction to prevent oversized or compressed archive exhaustion.
- Rejected unsafe credential filenames and expanded log redaction for connection URIs and provider tokens.
- Removed duplicate Preview-channel creation requests.
- Removed query-string authentication from the runtime-log WebSocket and enforced same-origin handshakes.
- Prevented release tags from generating invalid branch-prefixed container tags.
- Gated GitHub Releases on verified container publication and sourced release notes from this changelog.

## [0.1.0-beta] - 2026-07-08

### Added

- SDK-compatible OpenAI, Anthropic, and Google GenAI routes.
- Provider credential pool, virtual model routing, context optimization, usage visibility, and the management console.
- Docker Hub and GitHub Container Registry publishing.

[Unreleased]: https://github.com/nguywnben/omni-gateway/compare/v1.1.1...HEAD
[1.1.1]: https://github.com/nguywnben/omni-gateway/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/nguywnben/omni-gateway/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/nguywnben/omni-gateway/compare/v0.2.0-beta...v1.0.0
[0.2.0-beta]: https://github.com/nguywnben/omni-gateway/compare/v0.1.0-beta...v0.2.0-beta
[0.1.0-beta]: https://github.com/nguywnben/omni-gateway/releases/tag/v0.1.0-beta
