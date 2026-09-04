# Operational observability

The Overview page derives a 15-minute RED snapshot from bounded, content-free request decision
traces. It shows request rate, error ratio, p50/p95/p99 duration, model-route health, and quota,
budget, rate-limit, cooldown, and capacity pressure. The API reads at most 5,000 traces and exposes
at most 50 routes; the dashboard renders the ten busiest routes and marks a truncated sample.
Caller errors and policy/authentication denials are counted as rejections but excluded from the
service error ratio so invalid traffic cannot create a false availability incident.

## External export controls

Both external exporters are disabled by default. Neither exporter transmits prompts, responses,
request IDs, trace IDs, credential identifiers, exception text, or model-route dimensions.

Prometheus requires both `PROMETHEUS_EXPORT_ENABLED=true` and a `METRICS_TOKEN` of at least 32
UTF-8 bytes. Scrapes of `GET /metrics` must send `Authorization: Bearer <token>`. The endpoint
returns 404 while disabled, 503 for an unsafe enabled configuration, and compares tokens in
constant time. Provider is the only deployment-derived label on spend counters. Durable-ledger
operation counters use only closed backend, operation, and result labels; RED metrics use only fixed
quantile, category, and status vocabularies. No virtual-key ID, request ID, credential reference,
model, cost, or driver error becomes a metric label.

OpenTelemetry requires `OTEL_EXPORT_ENABLED=true` and an HTTPS
`OTEL_EXPORTER_OTLP_ENDPOINT`. The gateway sends aggregate OTLP/HTTP JSON gauges to `/v1/metrics`
every `OTEL_EXPORT_INTERVAL_SECONDS` (15–300, default 60). Optional
`OTEL_EXPORTER_OTLP_PROTOCOL` is fixed to the standard `http/json` transport. Optional
`OTEL_EXPORTER_OTLP_HEADERS` accepts at most eight comma-separated `authorization`, `api-key`, or
`x-api-key` values. Credentials embedded in the endpoint, plaintext HTTP, arbitrary headers, and
line breaks fail startup. Header values and full endpoint paths are never returned to the console.

The reference rules are in `deploy/observability/prometheus-alerts.yml`. Tune thresholds only
after establishing a traffic baseline; the supplied error and latency alerts require a minimum
sample so idle or new installations do not page.

## Coordination evidence

`omni_coordination_operations_total{backend,operation,result}` is a process-local counter for the
currently supplied coordination store. `backend` is fixed to `in_memory`, `redis`, or `unknown`.
`operation` is one of the fixed coordination, quota, and identity-security lifecycle calls (for
example `reserve_quota`, `commit_quota`, `reserve_security_attempt`, `consume_oidc_transaction`,
`resolve_security_session`, `compare_and_set`, or `close`). `result` is fixed to `success`,
`rejected`, `idempotent`, `unavailable`, `corrupt`, `reconciliation_required`, or `unexpected`.
No session digest, principal index, client index, throttle bucket, OIDC state/browser digest, or
operation ID is a label. The renderer always emits its HELP and TYPE metadata, including before
any operation occurs.

Use the counter to ask: is Redis becoming unavailable, are corruption or reconciliation-required
outcomes increasing, are quota admissions being rejected unexpectedly, and is a process closing
repeatedly? The lifecycle boundary also retains an in-process, content-free health snapshot with
only backend class, availability/closed state, failure count, fixed error category, and timestamps.
It never places a logical key, scope, reservation, operation ID, provider, Redis URI, or exception
message in metric labels or health evidence.

The semantic Redis execution suites are opt-in: set `OMNI_TEST_REDIS_URI` and run
`backend.tests.test_coordination_redis_live` plus
`backend.tests.test_security_coordination_redis_live`. With the variable absent, unittest reports
each live test as an explicit skip; with it present, a connection failure is a real failure. The
security suite proves shared session visibility and revocation, atomic authentication-attempt
admission, one-winner OIDC transaction consumption, and exact ready-epoch fencing. Each run derives
a unique validated lowercase/hyphen namespace and teardown scans and deletes only keys under that
run's derived deployment prefix/hash tag. It never uses `FLUSHDB`, broad deletion, or `SCRIPT
FLUSH`; the latter is server-global and therefore not safe for a shared endpoint.

The normal opt-in suite verifies registered Lua execution against a real endpoint. Separate,
deterministic driver-boundary tests inject cancellation only after the stateful script has applied
its mutation and replay record, proving a retried operation is replayed rather than applied twice.
They are not timing-based live cancellation tests. Both paths keep Redis URIs, credentials, and
driver exception text out of diagnostics and metric labels.

This evidence does not activate HA Redis selection, `/ready` checks, deployment changes,
multi-worker/replica operation, or caller migration. W4.18 activation still requires an explicit
runtime-selection and lifecycle design, readiness and failure-policy review, safe deployment and
rollback procedures, multi-worker/replica validation, and migrated callers.

## Symptom runbooks

- [High error rate](runbooks/high-error-rate.md)
- [High latency](runbooks/high-latency.md)
- [Quota, budget, or capacity exhaustion](runbooks/capacity-exhaustion.md)
- [Storage unavailable](runbooks/storage-unavailable.md)
- [Unknown model pricing](runbooks/unknown-pricing.md)
