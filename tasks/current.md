# Omni Gateway Enterprise Overhaul — Current Execution State

## Resume Here

- Updated: 2026-09-04 (Asia/Saigon).
- Branch: `codex/enterprise-overhaul`.
- Implementation baseline: W4.16 code checkpoint `f0c66bd` plus closure evidence.
- Completed scope: Waves 1–3 / Phases 0–5 plus Wave 4 slices W4.1–W4.16 and checkpoints W4-A/W4-B.
- Original program progress: 21/28 approved checklist items complete (including specification and
  Phase 6 ADR approval), exactly 75.0%; wave execution-slice checkboxes are refinements and are not
  added to that denominator.
- Active scope: Wave 4 W4.17, routing/governance/cache state coordination.
- Control state: **IN PROGRESS — W4.17 SLICE 4/9 COMPLETE**.
- Execution mode: continuous through the remaining W4.16–W4.19 queue under
  `docs/superpowers/plans/2026-09-02-wave-4-continuous-completion.md`; do not pause at internal task
  boundaries.
- Expected worktree state at this checkpoint: clean after the W4.16 closure commit.
- Expected runtime: one Omni Gateway listener on `http://127.0.0.1:4283`; `/health` and `/ready`
  return HTTP 200.
- Last verified full suite: 1,195 tests passed on Python 3.14.6 with 29 opt-in live backend tests
  skipped because no test URI was configured. The W4.15–W4.16 closure matrix passes 253 tests with
  11 explicit live Redis skips;
  repository-wide Ruff lint/format, compileall, pip consistency, diff, and all 45 frontend
  JavaScript syntax checks pass. No dependency, YAML, or shell file changed in this slice. The
  dependency audit reports no known vulnerabilities. YAML and all six shell syntax gates pass.
  Runtime `f0c66bd` is the sole listener on port 4283 (PID 17952); health/readiness return HTTP 200,
  and no Redis test URI or coordination runtime mode is selected.

### W4.17 live handoff

- The accepted state inventory and semantic boundary are recorded in
  `docs/specs/routing-governance-cache-coordination.md`.
- The resumable nine-slice execution plan is
  `docs/superpowers/plans/2026-09-04-w4.17-routing-governance-cache-coordination.md`.
- Readable fenced records now have a closed `CasSnapshot` schema, exact-epoch in-memory semantics,
  a fixed cluster-slot-safe Redis Lua read, strict binary-safe decoding, service metrics, and the
  shared live contract. The focused coordination matrix passes 93 tests; configured live Redis
  execution remains opt-in.
- The semantic adapter adds a backend-owned coordination clock, domain-separated HMAC identifiers,
  bounded exclusive/shared credential leases, shared route cooldown/latency outcomes, exact and
  semantic cache metadata types, and fixed-scope monotonic invalidation. The expanded focused
  matrix passes 99 tests without exposing credential, model, or cache identifiers to store keys or
  payloads.
- `SmartCredentialRouter` and `CredentialManager` now accept the exact supplied adapter (including
  false-valued test doubles), rank against shared in-flight/last-selection/cooldown/latency state,
  acquire bounded lease handles before returning credentials, and release/publish outcomes through
  the same fenced backend. Standalone defaults use a private in-memory adapter. Two independent
  routers sharing a store cannot double-acquire an exclusive credential or bypass a published
  cooldown. All 48 routing-focused and 37 adjacent gateway/manager tests pass.
- Immediate next action: preserve the selected quota store and fencing epoch across every
  `VirtualKeyManager` reserve/commit/release transition and prove shared-manager concurrency.
- Coordinated activation remains closed; standalone runtime and the one-worker/one-replica ceiling
  are unchanged.

Wave 2 was accepted and pushed by the human on 2026-08-24. Wave 3 / Phases 4–5 was accepted on
2026-08-26. ADR-007/ADR-008 and the Wave 4 queue were accepted later that day when the human again
instructed execution of the next plan. Do not skip Wave 4 slice gates or enter release activation.

The W3.5 browser blocker cleared on retry. The authenticated loopback console completed its full
W3-A browser matrix without requiring a code change; the browser was returned to its default
viewport with Vietnamese locale, system theme, cleared filters, and no open dialog.

## Authoritative Reading Order

1. `docs/specs/enterprise-overhaul.md` — product scope, boundaries, success criteria.
2. `docs/decisions/004-versioned-ai-quality-policy-plane.md` — AI Quality policy.
3. `docs/decisions/005-provider-operation-capabilities.md` — Wave 2 operation contract.
4. `docs/decisions/006-durable-and-coordinated-enterprise-state.md` — state and HA boundary.
5. `docs/specs/enterprise-identity-and-ha.md` — accepted Phase 6 contract.
6. `docs/decisions/007-explicit-rbac-and-oidc-identity.md` — accepted identity decision.
7. `docs/decisions/008-gated-high-availability-activation.md` — accepted HA decision.
8. `tasks/plan.md` — delivery waves, dependencies, detailed execution slices.
9. `tasks/todo.md` — authoritative checkboxes.
10. This file — latest handoff state, evidence, and immediate next action.
11. `git status`, `git log`, and the actual test/runtime output — final verification of all claims.

If documents conflict, accepted ADRs and the approved spec constrain the plan; current repository
state and test evidence constrain this handoff. Stop and surface an unresolved conflict instead of
silently choosing a new design.

## Completed Evidence

### Wave 1 — Policy and console foundation

- Phase 0: policy-plane, provider capability, and enterprise state ADRs accepted.
- Phase 1: light/dark/system theme, navigation ownership, keyed localization, and literal-leak
  gates delivered.
- Phase 2: versioned AI Quality policy, management API, runtime activation, structural token
  compression safety, decision telemetry, and AI Quality console delivered.
- Latest implementation checkpoint: `39fb9da`.
- Repository quality evidence at that checkpoint: 470 tests passed; Ruff and compileall clean.
- Service restart evidence: `/health` returned HTTP 200 after the checkpoint restart.
- W2.1 evidence: all nine console credential variants have an exact, fail-closed operation
  inventory; 473 full-suite tests passed before its checkpoint commit.
- W2.2 evidence: the authenticated provider catalog exposes typed additive variant/operation
  metadata without changing existing provider records; 475 full-suite tests passed.
- W2.3 evidence: single-credential verify, test, quota, toggle, delete, export, and credit-mode
  operations are checked against the exact server-side variant contract before side effects;
  unknown variants fail closed with a stable secret-free error; 480 full-suite tests passed.
- W2.4 evidence: the existing batch route now has a typed additive contract with a 100-target
  bound, side-effect-free expiring previews, fresh capability evaluation, per-item outcomes and
  timeouts, duplicate handling, and concurrency-safe idempotency reservations; the 1.x client uses
  the new handshake; 497 full-suite tests passed.
- W2.5 evidence: credential fleet mutations emit one schema-versioned, correlated, allowlisted
  event per target; HMAC fingerprints replace names, raw failure details are withheld, retention is
  bounded, idempotent retries do not duplicate events, and Prometheus exposes fixed-cardinality
  outcome counters and duration histograms; 508 full-suite tests passed.
- W2-A evidence: committed checkpoint `7b2fbc2` restarted as the only listener on port 4283;
  `/health`, `/ready`, and `/metrics` returned HTTP 200; credential operation counter/histogram
  families were present; the real Vietnamese login shell had a clean browser console and no
  horizontal overflow at 360/768/1024/1440 widths.
- W2.6 evidence: credential status queries now compose exact provider variant, credential kind,
  health, cooldown, quota state, tier, source, status, error, and preview filters before stable
  sorting/pagination; responses expose safe facets and a bounded five-minute opaque all-matching
  token that retains only normalized filters. Empty, 125-record, changing-data, invalid, conflict,
  tamper, cross-mode, and secret-exclusion tests passed; the full suite reached 515 tests.
- W2.7 evidence: pool filters use explicit responsive controls for credential kind, health, quota
  state, and source; allowlisted filter/page-size state persists in URL and a 512-byte bounded
  session record without credential names; page selection and opaque all-matching selection are
  distinct, clearable states. All 15 supported locales received curated fleet copy, frontend
  locale/asset tests passed, and changed JavaScript files passed syntax checks.
- W2.8 evidence: all-matching batch requests resolve normalized filters against fresh fleet data,
  retain the 100-target cap, and reject expired selections or previews made stale by fleet changes;
  provider catalog capabilities now drive a fail-closed operation intersection in the toolbar.
  Preview precedes explicit confirmation, while execution returns localized bounded per-item
  outcomes and recovery guidance. Non-Antigravity tiers are explicitly not applicable rather than
  being mislabeled as Pro.
- W2-B evidence: 522 tests passed with mixed-provider, 101-target, stale-preview, tamper, and
  secret-exclusion fixtures; Ruff, compileall, every frontend JavaScript file, and diff-check passed.
  PID 3800 is the only listener on port 4283 and health/ready return 200. Real-browser checks found
  no horizontal overflow at 360/768/1024/1440, verified 2/3/5-column responsive filters,
  light/dark/system themes, bounded URL filter restoration, semantic controls/focus styling, and
  curated Vietnamese, English, and Simplified Chinese fleet copy; observed management requests
  returned 200.
- W2.9 evidence: one declarative manifest now covers all 37 editable fields across the nine console
  provider variants. It defines input type, required state, bounds, autocomplete, secret lifetime,
  environment locks, help, advanced status, validation, and reset behavior; runtime helpers apply
  the contract without browser persistence. Static audits enforce coverage, labels, secret safety,
  and a curated 15-locale catalog. The full suite reached 528 tests.
- W2.10 evidence: Google AI Studio and Google Antigravity now consume shared validation,
  environment-lock, help, and transient-secret reset behavior. Endpoint inputs use bounded URL
  semantics, callback content is cleared after submission, and Antigravity client secrets are no
  longer reflected by GET, save, or reset responses; a configured-state marker preserves unchanged
  secrets safely. Focused response-contract and form audits passed; the full suite reached 532 tests.
- W2.11 evidence: OpenAI Platform, Codex, Grok Build, SpaceXAI Console, Claude Code, Claude
  Platform, and Ollama now use the same declarative validation, environment-lock, generated help,
  and transient-secret lifecycle. Provider-specific API-key bounds remain aligned with backend
  request models. xAI metadata moved out of the Google AI Studio script, removing an implicit load-
  order dependency. Provider, locale, and syntax audits passed; the full suite reached 534 tests.
- W2-C evidence: all 534 tests, Ruff, compileall, every frontend JavaScript syntax check, and
  diff-check passed. The final checkpoint service restarted as the only listener and health/ready
  returned 200. Authenticated browser checks verified no horizontal overflow at 360/768/1024/1440, 23
  generated field-help nodes with ARIA associations, correct light/dark/system rendering,
  Vietnamese/English/Simplified-Chinese live locale changes, masked/empty Antigravity secret state,
  provider-specific secret bounds, and ArrowRight focus/selection from Antigravity to AI Studio;
  the browser console was empty. English literal leaks discovered in advanced provider forms were
  corrected before closing this checkpoint.
- W3.1 evidence: the versioned immutable audit contract now validates actor/action/target/outcome
  vocabularies, HMAC-redacts actor and target identifiers before the repository boundary, bounds
  change summaries and retention/query inputs, provides exact fingerprint filters, and signs
  opaque cursors against tampering. The repository protocol exposes append, query, and policy-
  driven prune only—never individual update/delete. Two RED cycles proved the missing module and
  direct-construction redaction bypass before implementation; 8 focused tests and all 542 tests
  passed.
- W3.2 evidence: additive, append-only audit repositories now exist for SQLite (`c722f9b`),
  PostgreSQL (`343903d`), and MongoDB (`bdf766f`). All three enforce unique event IDs, stable
  newest-first ordering, exact bounded filters, signed cursor pagination, strict stored-record
  revalidation, and policy-only age/count pruning. SQL writes and filters are parameterized;
  PostgreSQL prunes transactionally; MongoDB deliberately has no TTL index so records cannot be
  deleted outside the explicit retention policy. Commit `55dfce4` exposes the selected repository
  through the existing storage adapter without persisting its cursor-signing key. Backend parity,
  restart persistence, UTC boundaries, duplicate normalization, corrupted-record failure, and
  uninitialized fail-closed behavior are covered; all 562 tests passed with Ruff and compileall
  clean.
- W3.3 evidence: commit `d42ba90` adds a declarative coverage gate for all 57 control-plane write
  routes. Fifty durable mutations resolve through one correlated response boundary, single/batch
  credential actions bridge the existing per-target W2 evidence without duplicating idempotent
  retries, and the five remaining preview/OAuth-start routes are explicitly proven side-effect
  free. Actor, action, target, outcome, and change vocabularies are allowlisted; semantic provider,
  credential, key, configuration, and model targets are HMAC-redacted before append. A generated
  internal master key persists across restart and derives separate fingerprint/cursor keys without
  entering management config responses. Startup fails closed if audit cannot initialize, while
  append outages are surfaced with secret-free critical evidence. Commit `7024f4e` resolves targets
  before route execution. All 577 tests, Ruff, compileall, and diff-check passed. Runtime smoke found
  and removed stale PID 3540, then verified PID 11312 as the only listener; health/ready returned
  200 and request `w3-committed-smoke` persisted one `auth.logout` success event in SQLite.
- W3.4 evidence: commits `a274a5b`, `bf74e17`, and `6c6e541` add a strict durable retention
  policy service, authenticated audit query/retention routes, and bounded JSONL/CSV export.
  Repeated exact filters cover time, actor, action, target, outcome, and request ID; pages use
  signed opaque cursors and a 200-event maximum. Retention is persisted before exact policy prune
  and commit `cb2bd95` enforces it after every append. Exports reject rather than truncate above
  10,000 events or 8 MiB, CSV cells are formula-safe, filenames are server-generated, and only
  redacted event records cross the response boundary. Successful exports append correlated
  `audit.export` evidence before release. Fresh review commit `f49a5a6` added typed OpenAPI
  responses, CSV-header byte enforcement, and fail-closed startup ordering. All 596 tests passed;
  Ruff, compileall, focused format, pip consistency, 36 JavaScript syntax checks, and diff-check
  are clean. The maintained API contract is `docs/audit-api.md`.
- W3.5/W3-A evidence: commit `9d581ae` adds `/audit` under an Observability navigation
  group with exact action/actor/target/outcome/time/request/fingerprint filters, session-only
  opaque cursor history, redacted event detail, request-ID copy/pivot, confirmed retention updates,
  and bounded JSONL/CSV downloads. Only category filters and page size enter local storage. The
  client strictly revalidates all 11 event fields and vocabulary values, renders untrusted records
  with `textContent`, allowlists export filenames, and cancels stale queries so older responses
  cannot replace newly filtered evidence. A dedicated keyed catalog supplies curated copy for all
  15 supported locales. Static contracts forbid sensitive fields and unsafe DOM insertion; all 603
  tests, Ruff lint/format, compileall, pip consistency, vulnerability audit, 38 JavaScript syntax
  checks, and runtime audit/health/readiness smoke tests pass. The authenticated real-browser
  closure covered 360/768/1024/1440 widths with no horizontal overflow and correct mobile/desktop
  navigation; light/dark/system themes; all 15 supported locales with correct `html lang` and no
  untranslated audit keys; semantic headings, labels, live regions, tab order, native dialog focus
  containment and return; request-ID pivot, outcome filtering and clear; retention warning followed
  by cancel with unchanged 90-day/1,000,000-event policy; and a successful JSONL export that added
  `audit.export` to the refreshed stream. The console had no warning/error entries, every visible
  control had an accessible name, every `aria-labelledby` relationship resolved, and the Audit DOM
  contained no password/secret-named inputs or recognized key-like plaintext. W3.5 and W3-A are
  complete; the original Phase 4 append-only audit item is also complete.
- W3.6 evidence: commits `1bb6596` and `f8513cf` add schema-version-2 virtual-key records,
  backward-compatible migration, protocol-specific inference and explicit management scopes,
  fail-closed scope and model-pattern validation, status/last-used metadata, and bounded unknown-
  pricing policy. Existing unversioned keys retain all prior inference access and gain no
  management permission; new keys default to inference-only access. Scoped management Bearer keys
  are separated into read/write methods and management audit evidence is attributed to the stable
  key ID before fingerprinting. The maintained contract is `docs/virtual-key-api.md`. All 623 tests,
  Ruff lint/format, compileall, pip consistency, vulnerability audit, 38 JavaScript syntax checks,
  and diff-check pass. W3.8 lifecycle concurrency and W3.9 UI remain intentionally open.
- W3.7 evidence: commits `bb3bd74` and `5b38c71` add an atomic state-store semantic boundary for
  RPM, TPM, daily/monthly budget, estimate-to-actual commit, idempotent release, reservation expiry,
  and durable-ledger reconciliation. Authentication reserves worst-case candidate-model capacity
  before provider work; primary and Vertex success paths commit actual tokens and policy cost;
  provider failure, stream cancellation, and response errors release capacity. Missing pricing
  follows deny/warn/fallback only when a hard budget needs a price, and unavailable spend storage
  fails closed with HTTP 503 rather than appearing as zero. Low-cardinality Prometheus evidence
  covers quota decisions without key IDs. Concurrency, cancellation, retry/idempotency, expiry,
  reconciliation, overspend, fallback pricing, and ledger-outage tests pass; all 646 repository
  tests, Ruff lint/format, compileall, dependency consistency, vulnerability audit, 38 JavaScript
  syntax checks, and diff-check are clean. Redis coordination and multiple workers remain inactive.
- W3.8 evidence: the safe lifecycle slice adds monotonic revisions, stale-write conflicts,
  stable-ID atomic rotation, terminal revocation, one-time create/rotate reveal, and bounded audit
  classifications. Plaintext never enters persisted or non-reveal records; rotation races produce
  one winner; revoke and stale-write replays are rejected. All 653 backend tests and focused Ruff
  checks pass, while existing PATCH clients remain compatible without an expected revision.
- W3.9/W3-B evidence: `49db870` completes the 75-key Access vocabulary for every supported locale
  and `8379d9c` adds the responsive lifecycle console without disturbing root integration or SDK
  guidance. The console supports list/search/filter, create/edit, usage, atomic rotate, terminal
  revoke, explicit unknown-pricing policy, revision conflict recovery, and one-time secret reveal;
  write scope implies read scope and fallback price is enabled only for fallback policy. Static
  contracts prove plaintext cleanup on close/copy and prohibit persistence APIs. The authenticated
  browser matrix passed at 360/768/1024/1440 with no horizontal overflow, light/dark/system themes,
  all 15 locales with no raw `access.*` keys, keyboard focus containment and Escape close, clean
  console, accessible controls, and correct responsive filters. The isolated browser runtime and
  its temporary data were stopped and removed after verification. All 659 tests and W3-B gates
  pass; `bf5cc99` independently restores the repository-wide formatter gate.
- W3.10 evidence: `fdbe2ea` adds a strict schema-version-1 trace with closed protocol, outcome,
  category/action/result/reason vocabularies and at most 64 decisions. Middleware correlates the
  same bounded public request ID across OpenAI, Responses, Anthropic, Gemini, and Vertex success,
  failure, streaming, and cancellation lifecycles. Allowlisted hooks cover routing/fallback,
  retry/cooldown, compression, guardrails, cache, quota, upstream, tokens, cost, latency, and final
  outcome. Request/response content, secrets, credential filenames, exception text, and arbitrary
  metadata have no schema field and corrupted records fail closed. Additive SQLite, PostgreSQL,
  and MongoDB repositories survive restart and use a separate 7-day/100,000-trace default policy
  with bounded signed pagination. All 679 tests, full Ruff lint/format, compileall, and diff-check
  pass. The maintained contract is `docs/request-traces.md`.
- W3.11 evidence: `b52b1a3` adds authenticated trace query/detail/retention/export APIs with exact
  filters, signed pagination, formula-safe CSV, a 10,000-trace/16-MiB hard export bound, and audit
  evidence for retention changes and successful exports. `/logs` now opens a localized Request
  traces console with request-ID pivots and ordered decision detail; raw WebSocket logs remain in a
  visually and semantically separate diagnostic-only region. The client persists only protocol,
  outcome, and page size and strictly revalidates the closed schema before text-only rendering.
  All 691 tests pass. The authenticated browser gate verified a real denied request trace and its
  two-step timeline, filters/pivot/export, WebSocket separation, Escape/focus return, no overflow
  at 360/768/1024/1440, light/dark/system, all 15 locale labels, and a clean console. Temporary
  runtime data were removed and the browser viewport was reset after verification.
- W3.12/W3-C evidence: `4b775b9` adds a bounded cached RED snapshot, p50/p95/p99 latency,
  service-error and rejection separation, provider/model route health, and quota/budget/rate-limit
  exhaustion evidence to the authenticated dashboard. Prometheus and OTLP/HTTP JSON export are
  disabled by default, reject unsafe explicit configuration, use fixed low-cardinality dimensions,
  and never export request content or secrets. Deployment rules cover service errors, P95 latency,
  exhaustion, storage readiness, and unknown pricing with linked symptom-based runbooks. All 709
  tests and repository gates pass; dependency audit reports no known vulnerabilities. The real
  browser verified a denied request without falsely degrading the service-error SLO, responsive
  layouts, light/dark/system themes, all 15 locale catalogs, accessible text-only rendering, and a
  clean console. Temporary runtime/cache data were removed after verification.
- Wave 3 acceptance: the human accepted W3-C on 2026-08-26 by instructing the agent to start the
  project and execute the next plan after receiving the completion evidence. Runtime was started
  again from checkpoint `76315e7` before Wave 4 planning.
- W4.1 planning evidence: `docs/specs/enterprise-identity-and-ha.md` plus ADR-007 and
  ADR-008 record the current password/JWT and process-local constraints, explicit principals and
  permission bundles, OIDC Authorization Code + PKCE/state/nonce validation, opaque revocable
  sessions, local recovery, the approved W4.7 `PyJWT[crypto]` dependency change,
  durable/coordinated state split,
  fail-closed Redis reconciliation, staged activation, measurable HA targets, and rollback. The
  detailed W4.2–W4.19 queue does not claim any Phase 6 runtime behavior is active. Local-link and
  diff checks pass, and the unchanged runtime remains covered by all 709 regression tests.
- W4.2 authorization evidence: `c745e18` adds the closed `local_owner`, `oidc_user`, `virtual_key`,
  and `system` principal types; four exact immutable role bundles; typed allow/deny decisions;
  direct-binding versus claim-mapping owner protection; bounded malformed-input handling; explicit
  legacy read/write allowlists; inventory markers; and additive granular permission scopes. No
  route uses the new domain yet. Fifteen focused tests and all 724 backend tests pass, with
  repository-wide Ruff lint/format and compileall clean.
- W4.3 route-authorization evidence: `627514d` adds one immutable manifest for all 93 protected
  OpenAPI operations and `/api/logs/stream`; exact typed permissions are enforced through the
  existing common FastAPI dependency before handlers and immediately after the WebSocket cookie
  handshake. The dependency uses FastAPI's trusted `path_format`, stores the resolved principal in
  request state, returns generic denials, records virtual-key last use only after authorization,
  and fails closed if a protected route lacks policy. Generated matrices cover all human roles,
  every legacy safe/write route, duplicates, malformed route inputs, WebSocket denial, and
  `{model_id:path}` normalization. Review split root-key disclosure into owner-only
  `root_key.read` versus `root_key.rotate`; legacy read keys retain their prior GET access and gain
  no identity, owner-assignment, recovery, or HA rights. Ruff, diff-check, and all 741 tests pass.
- W4.4 durable-identity evidence: `563fb9d` adds closed immutable identity, role-binding,
  OIDC-policy revision, and migration records plus a storage-agnostic repository protocol. Email
  and profile data have no contract field; OIDC identity is exact case-sensitive `(issuer,
  subject)`, generated resource IDs are opaque, record sizes/types/versions/timestamps are bounded,
  and normal representations and errors do not expose issuer/subject. `5a81b83` adds an atomic,
  additive SQLite implementation in the existing `credentials.db`; it enables foreign keys per
  connection, preserves legacy tables, bootstraps one enabled immutable local owner, revalidates
  every stored pair, and exposes no delete path. Identity, binding, and OIDC-policy resources use
  conditional revisions; authorization changes advance epochs; two concurrent writers produce one
  winner. Restart, corruption, owner-lockout, rollback, bounds, redaction, and independent-resource
  revision regressions are covered by 21 focused tests. All 762 tests and repository gates pass.
- W4.5 shared-backend evidence: `65335bc` extracts one backend-neutral parity fixture; `3d47e9d`
  and `6ec265b` implement PostgreSQL and MongoDB repositories; `12ff59e` wires all three managers
  through the storage adapter and adds isolated opt-in live suites. PostgreSQL uses additive
  normalized tables, transactions for multi-table mutations, parameterized revision CAS, exact
  collation, and UTC datetime encoding at the asyncpg boundary. MongoDB embeds each identity and
  binding for atomic authorization changes, applies simple-collation partial uniqueness only to
  OIDC documents, and keeps policy/migration checkpoints separate. Review commits `c610cd7` and
  `b3352b5` close security-admin schema parity and timestamp portability regressions. Forty-six
  focused tests execute locally, fourteen live tests skip without explicit URIs, and all 801 tests
  plus Ruff lint/format, compileall, pip consistency, and diff-check pass.
- W4.6/W4-A evidence: `849da03` adds the semantic session-store contract and 256-bit opaque,
  HMAC-indexed in-process implementation; `a29dec1` binds issuance and resolution to the durable
  immutable local owner and its authorization epoch; `4dd7bbb` activates the store across setup,
  login, logout, password rotation, and independently throttled recovery. Review fix `6010e71`
  bounds the process-local store with expired-record pruning and LRU revocation. Idle/absolute expiry,
  atomic rotation/revocation, concurrent password proof, corrupted master-key failure, generic
  auth errors, origin/cookie protections, and bounded legacy-JWT migration are covered. Provider
  OAuth transactions receive only an ephemeral HMAC request reference and their external state
  contains no bearer/session value. Low-cardinality metrics and `auth.recovery` audit evidence add
  no identifiers or secrets. Expired records are pruned and the bounded store revokes the least
  recently used session at capacity. All 829 tests pass with 14 opt-in live-backend skips;
  repository gates and committed-runtime health/readiness smoke are clean.
  `docs/management-sessions.md` records the process-restart reauthentication posture and keeps
  shared coordination gated to W4.16.
- W4.7 OIDC-foundation evidence: `407ecac`, `c32e369`, and `247ada8` add a versioned immutable
  disabled-by-default policy, environment/file-only secret handling, pinned-address verified HTTPS
  discovery transport, exact reduced metadata validation, and bounded atomic JWKS rotation.
  `55c81d6` closes duplicate-JSON, secret-file replacement-race, forged-JWKS-URI, and concurrent
  failed-refresh gaps; `d0874f7` simplifies the reviewed control flow without changing behavior.
  Thirty-eight focused tests cover invalid configuration, SSRF/mixed DNS, redirects, timeouts,
  oversized or poisoned metadata/JWKS, key bounds/rotation, and refresh coalescing. Runtime smoke
  then exposed a FastAPI nested-router prefix regression; `3ce001b` restores authorization against
  the framework's trusted effective route template and adds an ASGI regression test. All 868 tests
  pass on Python 3.12 and Python 3.14 with 14 opt-in live-backend skips; Ruff lint/format, compile,
  route-contract, dependency consistency, and vulnerability gates are clean.
  `docs/oidc-foundation.md` records the
  operator and activation boundary. No login, callback, token verification, or OIDC session path is
  active; local-owner recovery and the single-worker/single-replica boundary are unchanged. The
  post-fix fresh-setup runtime smoke passed end-to-end in isolated storage, and the committed primary
  runtime reports HTTP 200 for both `/health` and `/ready` on port 4283.
- W4.8 ID-Token-verifier evidence: `5b40d51` adds bounded clock-skew/token-age policy; `e7d5911`
  prevents configurable identity claims from colliding with OIDC protocol claims; `9dcfa51` adds
  strict RS256/PS256/ES256 verification with exact issuer, audience, `azp`, nonce, time, subject,
  optional UserInfo, allowlisted-output, malformed-input, rotation, and outage behavior. `dbd2914`
  closes review findings around cache trust-configuration binding, provider-controlled exception
  chains, and cancellation coverage. Unknown keys receive one bounded rotation attempt without
  refresh storms; failed rotations preserve fresh known keys. Thirty-four focused tests and all
  880 tests pass on Python 3.12 and Python 3.14 with 14 opt-in live-backend skips. Ruff lint/format,
  compile, pip consistency, locked installation, diff, and vulnerability gates pass. No login,
  callback, token exchange, or OIDC session route is active.
- W4.9 Authorization-Code evidence: `e28cbab` requires discovery to advertise PKCE S256;
  `41795bc` adds the bounded atomic one-time transaction service; `4d849c0` adds pinned bounded form
  POST with exact Basic/Post client authentication; `0b70c3a` adds strict raw callback parsing,
  single-use code exchange, and verified-only output. Replay, CSRF/browser mismatch, mix-up,
  malformed/duplicate/query-token input, provider error, outage, cancellation, stale trust snapshot,
  and token-response bounds are covered. The external adversarial review was reconciled before
  closure. Seventy-four focused OIDC tests and all 904 tests pass on Python 3.12 and Python 3.14
  with 14 opt-in live-backend skips; Ruff, format, compile, pip consistency, clean locked install,
  diff, and vulnerability gates pass. The temporary validation environments were removed. No
  browser-facing route or OIDC session is active: W4.10 must deny or map the exact issuer/subject
  before issuing a revocable session.
- W4.10 role/session/browser evidence: `f56781a` adds an immutable bounded JSON group mapping and
  direct-binding-first exact issuer/subject resolver; `b5d7e66` binds OIDC sessions to independent
  identity and policy authorization epochs and authorizes the real OIDC principal; `0c4ed63`
  composes discovery, transaction, verification, identity, and session services lazily behind the
  disabled-by-default browser routes. Claim-derived owner is structurally impossible; unmapped,
  malformed, oversized, ambiguous, stale, or disabled identities deny. Login-time role downgrade,
  callback/path/cookie isolation, clean 303 redirects, provider outage, start abuse, local recovery,
  and revision invalidation are covered. `a02d0af` reconciles the fresh-context adversarial review:
  verified sessions cannot fall back to local-owner authority, failed discovery is shared behind a
  bounded waiter gate and negative-cache backoff, and a rejected claim re-evaluation advances the
  identity authorization epoch so older privileged sessions become stale. All 929 tests pass on
  Python 3.14; the 40 affected tests and compileall pass on Python 3.12, following the prior full
  926-test dual-interpreter checkpoint. Repository-wide Ruff lint/format, compileall, pip
  consistency, hash-locked install dry run, diff, and vulnerability audit pass. OIDC remains false
  by default; W4.12 and checkpoint W4-B still gate enterprise management/audit/UI activation.
- W4.11 identity-management evidence: `798d2ae` adds exact typed routes for current principal, OIDC
  readiness, direct identities, active sessions, revocation, policy-epoch advancement, and recovery
  status. Stable bounded pagination, optimistic revisions, owner-transition permission checks,
  durable authorization invalidation, HMAC-derived non-secret session references, verified-principal
  denial attribution, and closed audit vocabularies are enforced without returning bearer tokens,
  internal digests, provider tokens, profile claims, groups, or configured secrets. The independent
  adversarial review corrected recovery ingress reporting and added the SQLite pagination-order
  index. All 946 tests pass on Python 3.14.6 with 14 opt-in live-backend skips; Ruff lint/format,
  compileall, pip consistency, 42 JavaScript syntax checks, diff, and vulnerability gates pass.
  The API contract is consumed by the W4.12 Identity console.
- W4.12/W4-B Identity-console evidence: `0d1f608` adds a dedicated localized destination for
  current authority, OIDC and recovery readiness, direct identities, and active sessions. Controls
  are permission-derived; collections and cursors are bounded; risky mutations are confirmed;
  revisions preserve operator drafts; and authentication reset aborts stale responses. The
  external review corrected pagination re-entrancy and create-conflict semantics. Authenticated
  browser closure corrected verified-token wrapper normalization, legacy dialog-alias lookup, and
  explicit Escape cleanup with regression tests. All 960 tests pass with 14 opt-in live-backend
  skips; Ruff lint/format, compileall, pip consistency, dependency audit, 45 JavaScript syntax
  checks, and diff-check pass. The browser matrix has no horizontal overflow at
  360/768/1024/1440, passes system/light/dark and vi/en/zh-CN, exposes localized dialog names,
  restores focus on Escape, returns HTTP 200 from every Identity resource, and has no console
  warning/error. OIDC remains disabled by default and distributed runtime activation remains
  gated by W4-C.
- W4.13 durable-migration evidence: `ed707cc` closes and versions the semantic inventory;
  `691984b` adds the bounded resumable copy/streaming-verification runner; `6ed71e8` persists strict
  checkpoints through SQLite, PostgreSQL, and MongoDB storage adapters; and `f7ba28b` reconciles the
  fresh-context adversarial review. The hardening binds the canonical manifest and exact endpoint
  instances, requires a source mutation barrier and put-if-absent-or-equal target writes, records
  only safe numeric offsets, requires explicit-empty evidence, streams keyed digests, and removes
  the forgeable rollback boolean. Usage and reservation families remain explicitly not ready, so
  runtime authority activation is structurally unreachable in W4.13. All 987 tests pass with 14
  opt-in live-backend skips; 17 dependency-free focused tests and compileall pass on Python 3.12.
  Ruff lint/format, Python compile, pip consistency/audit, YAML/shell syntax, 45 JavaScript syntax,
  secret, and whitespace gates pass. No W4.13 source was sent to an external model.
- W4.15 Redis-semantic evidence: commits from `a60dcf9` through `be5e3b7` define the typed shared
  contract, bounded in-process reference, fixed application-owned Redis Lua, quota lifecycle,
  operability evidence, and adversarial hardening. Partial initialization, stale fencing, corrupt
  state, duplicate delivery, expired replay, large signed-63 token counts, cleanup backlog, and
  close cancellation fail safely. All 1,147 tests pass with 25 explicit opt-in live-backend skips;
  every repository gate and dependency audit is clean. `be5e3b7` restarted as exactly one listener
  (PID 26300) with HTTP 200 `/health` and `/ready`. Redis is not selected by runtime, no caller was
  migrated, and W4.19 still blocks activation until the O(n) quota scan has measured evidence and
  a supported cap or redesign.
- W4.16 Task 2 in-process security coordination: the standalone reference now implements fenced
  session issue/resolve/touch/rotate/revoke/list operations, category-isolated attempt admission,
  and one-time browser-bound OIDC transactions under a lock and store clock. Exact indexed expiry
  heaps provide bounded preflight cleanup without copying or scanning the full store; stable replay
  evidence, complete reverse-index validation, regressing-clock rejection, and post-close failure
  prevent stale privilege, identifier reuse, corrupt-index authorization, and replay resurrection.
  Reviewer findings were first reproduced as failing tests and reconciled. The 101-test focused
  matrix and 1,169-test full suite pass. This reference is not wired into runtime yet; Redis and HA
  activation remain gated.
- W4.16 security coordination: Redis now has fixed server-time Lua parity for session,
  attempt-admission, and OIDC transaction state; the standalone session, login/recovery/OIDC-start,
  and OIDC transaction services use the typed boundary. Operation evidence uses only bounded
  backend/operation/result labels. The opt-in live suite uses a unique namespace and proves
  cross-client visibility, atomic admission, one-winner consumption, and fencing; it explicitly
  skips without `OMNI_TEST_REDIS_URI`. The 253-test focused W4.15–W4.16 matrix passes with 11 live
  skips, and Ruff, format, compileall, and diff checks are clean. Runtime Redis selection remains
  inactive. Fresh-context review fixed false-valued-backend fallback and non-default fencing-epoch
  propagation. All 1,195 tests pass with 29 explicit live skips; repository and committed-runtime
  gates pass. The maintained reconciliation is `docs/reviews/w4.16-adversarial-review.md`.

## Approved vs. Proposed Scope

### Already approved and complete

- Everything checked in Phases 0–2 of `tasks/todo.md`.

### Approved and complete

- Wave 2 slices W2.1–W2.11 in `tasks/plan.md`.
- Phase 3 completion: provider capability contract, safe single/batch operations, fleet filtering,
  contextual toolbar, and complete provider-form audit.
- Minimal credential-scoped audit and operation telemetry foundations required to make new batch
  mutations diagnosable and safe.

### Approved and complete

- Wave 3 slices W3.1–W3.12 in `tasks/plan.md`.
- Phase 4: complete audit coverage, durable audit storage, virtual-key governance, reservation-
  aware enforcement, and the Access lifecycle.
- Phase 5: bounded request traces, Observability separation, health/SLO views, safe exporters,
  alert rules, and runbooks.

### Approved and in progress

- The Phase 6 specification, ADR-007, ADR-008, and Wave 4 execution queue.
- W4.1–W4.16 and checkpoints W4-A/W4-B are complete; W4.17 is the active next slice.

### Approved for staged implementation, not active yet

- Redis coordination, durable HA migration, and multiple workers/replicas remain gated by
  W4.13–W4.19 and checkpoint W4-C. OIDC code is complete but remains disabled by default until an
  operator supplies the accepted configuration.
- Phase 7 release activation, production deployment, or destructive migration.

Foundations borrowed from Phase 4 or Phase 5 remain partial and must not cause those phase
checkboxes to be marked complete.

## Wave 4 Checkpoint Protocol

1. W4-A: authorization coverage, durable identity parity, revocable sessions, local-owner
   compatibility, and recovery gates.
2. W4-B: OIDC flow, identity APIs/UI, audit, i18n, accessibility, and browser gates.
3. W4-C: durable ledgers, Redis semantics, coordinated failure/load evidence, activation, and
   rollback gates.
4. At each checkpoint: focused tests, full regression tests, Ruff/compile/JS/i18n gates, diff and
   secret review, atomic commit, clean worktree, and runtime smoke when applicable.
5. Browser-facing checkpoints require 360/768/1024/1440 widths, light/dark/system themes,
   representative locales, keyboard/accessibility verification, and clean console/network.
6. At the Wave 4 boundary: restart from the committed checkpoint, verify health, report evidence,
   and pause for human acceptance before Wave 5.

## Immediate Next Action

Execute W4.17 from
`docs/superpowers/plans/2026-09-02-wave-4-continuous-completion.md`: inventory and coordinate every
routing-, governance-, quota-, cooldown-, and cache-affecting process-local state behind strict
bounded in-memory/Redis semantics without selecting Redis at runtime.
Continue without a task-boundary pause under the accepted Wave 4 completion plan. Keep the
transport inactive and preserve `WORKERS=1`, one replica, disabled-by-default OIDC, source
authority, and every HA activation gate.

## Update Rule

Update this file whenever a checkpoint is committed, a blocker changes, scope is approved, or a
verification claim changes. Keep only current handoff state here; durable product decisions belong
in the spec or an ADR, and granular completion belongs in `tasks/todo.md`.
