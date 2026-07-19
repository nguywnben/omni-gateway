# ADR-003: Deployment-Scoped Model Eligibility and Negative Route Cache

## Status

Accepted for the 1.x runtime.

## Context

One provider can expose different models to different credentials because of account entitlements, subscription tiers, regions, or changing upstream availability. A provider-wide model list or a provider-wide 404 blacklist therefore creates false negatives: one account can fail while another account can serve the same model.

## Decision

Treat each credential as a routable deployment. A verified credential may persist a normalized `model_ids` catalog. The router evaluates that catalog before sending a request and prefers declared support over generic provider inference. When a provider returns a model-not-found response, the negative route cache is keyed by credential filename and model ID. Legacy entries without a credential name remain readable as provider-wide exclusions for backward compatibility, but new observations must be credential-scoped.

Antigravity model discovery is performed during verification and uses the same upstream catalog endpoint as the quota view. The management catalog unions model IDs across enabled credentials for display, while request routing still evaluates the individual credential record.

Transient upstream statuses (`408`, `409`, `429`, `500`, `502`, `503`, and `504`) use bounded retry and fallback behavior. Authentication, validation, unsupported-model, and other client errors are not retried by default. Provider-specific hard-failure auto-disable remains controlled by the existing configuration.

## Consequences

- A subscription mismatch no longer removes a model from every account at that provider.
- The Models page can show and restore the exact unavailable route that was learned.
- Verification performs one additional metadata request for Antigravity credentials.
- Existing provider-wide blacklist entries continue to work and can be removed from the management page.
- The single-worker restriction remains necessary because reservations, cooldowns, and the negative route cache are process-local or storage-coordinated only in the supported runtime.

## Rejected Alternatives

- A provider-wide blacklist was rejected because it conflates provider identity with account entitlement.
- Blindly retrying every HTTP error was rejected because it amplifies invalid requests and authentication failures.
- Importing LiteLLM's complete router was rejected because it would add a large dependency and configuration surface to a personal gateway without solving the provider-specific credential contract.
