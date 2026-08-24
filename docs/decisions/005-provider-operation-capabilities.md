# ADR-005: Provider-Declared Credential Operation Capabilities

## Status

Accepted for the credential-fleet overhaul.

## Context

Credential operations vary by provider, authentication flow, and account type. A provider name is
not enough to determine whether a credential can be verified, refreshed, queried for quota,
exported, placed in credit mode, or moved to a preview channel. UI-only checks are unsafe because
a crafted request can invoke an operation that the server did not intend to support.

## Decision

Extend the provider registry with credential variants and an explicit operation capability set.
The initial vocabulary is `verify`, `test`, `quota`, `refresh_identity`, `toggle`, `delete`,
`export`, `credit_mode`, and `preview_channel`. Capabilities describe supported operations only;
authorization, current credential state, and environment locks are evaluated separately.

All management operations resolve the authoritative capability set on the server before executing.
Single-item unsupported requests return a typed validation error. Batch operations compute the
intersection of capabilities for the selected credentials and return a typed per-item outcome;
one unsupported item does not misreport successful items. Destructive or high-volume operations
support a side-effect-free preview before execution.

The console consumes the same catalog contract. It hides inapplicable actions, disables actions
that are temporarily unavailable, and explains the reason. “Select page” and “select all matching
results” remain distinct scopes, and the server re-evaluates the filter at execution time.

Provider-specific fields, validation, and defaults remain owned by provider adapters. The shared
fleet layer owns filtering, selection, preview, authorization, result envelopes, and audit hooks.

The initial conservative inventory is:

| Credential variant | Credential kind | Supported operations |
| --- | --- | --- |
| Google Antigravity | OAuth | verify, test, quota, toggle, delete, export, credit mode |
| Google AI Studio | API key | verify, test, toggle, delete, export |
| Grok Build | OAuth | verify, test, quota, toggle, delete, export |
| SpaceXAI Console | API key | verify, test, toggle, delete, export |
| Codex | OAuth | verify, test, quota, toggle, delete, export |
| OpenAI Platform | API key | verify, test, toggle, delete, export |
| Claude Code | OAuth | verify, test, toggle, delete, export |
| Claude Platform | API key | verify, test, toggle, delete, export |
| Ollama | Connection | verify, test, toggle, delete, export |

`refresh_identity` and `preview_channel` remain in the vocabulary for legacy compatibility but are
not declared for the current shared provider pool. They cannot be invoked through the Wave 2 fleet
service until a variant explicitly earns support through contract and failure-path tests.

## Compatibility and Rollback

- Existing provider metadata is mapped to a conservative default set derived from current server
  routes; an undeclared capability is unsupported.
- Current single-item routes remain available during 1.x and delegate to the capability-aware
  operation service.
- The console can fall back to current per-card controls while the new batch surface is disabled.

## Consequences

- Mixed-provider fleet operations become predictable and enforceable on both client and server.
- Adding a provider requires declaring its complete credential-operation contract.
- Conservative defaults may initially hide an operation until its provider adapter is updated.
- The operation result envelope and capability vocabulary become compatibility-sensitive APIs.

## Rejected Alternatives

- Provider-name conditionals in the console were rejected because they drift from server behavior.
- A universal operation set was rejected because provider credentials are not interchangeable.
- Fail-fast batches were rejected because they obscure partial progress and complicate recovery.
- Arbitrary provider plugins were rejected because executable extensions widen the trust boundary.
