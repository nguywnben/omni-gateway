# Changelog

All notable user-facing changes are documented in this file. Omni Gateway follows [Semantic Versioning](https://semver.org/) while allowing breaking changes during the `0.x` beta series.

## [Unreleased]

### Changed

- Standardized internal module names, repository tooling, deployment defaults, and contributor documentation.
- Expanded CI across supported Python versions with linting, formatting, dependency auditing, route contracts, and runtime smoke tests.

### Fixed

- Removed an internal shortcut that intercepted a real `Hi` model prompt as a health check.
- Restricted forwarding-header trust to explicitly configured reverse-proxy deployments.

## [0.1.0-beta] - 2026-07-08

### Added

- SDK-compatible OpenAI, Anthropic, and Google GenAI routes.
- Provider credential pool, virtual model routing, context optimization, usage visibility, and the management console.
- Docker Hub and GitHub Container Registry publishing.

[Unreleased]: https://github.com/nguywnben/omni-gateway/compare/v0.1.0-beta...HEAD
[0.1.0-beta]: https://github.com/nguywnben/omni-gateway/releases/tag/v0.1.0-beta
