# Changelog

All notable user-facing changes are documented in this file. Omni Gateway follows [Semantic Versioning](https://semver.org/) while allowing breaking changes during the `0.x` beta series.

## [Unreleased]

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

[Unreleased]: https://github.com/nguywnben/omni-gateway/compare/v0.2.0-beta...HEAD
[0.2.0-beta]: https://github.com/nguywnben/omni-gateway/compare/v0.1.0-beta...v0.2.0-beta
[0.1.0-beta]: https://github.com/nguywnben/omni-gateway/releases/tag/v0.1.0-beta
