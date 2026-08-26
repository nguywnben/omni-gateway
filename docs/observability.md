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
constant time. Provider is the only deployment-derived label on ledger counters; RED metrics use
only fixed quantile, category, and status vocabularies.

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

## Symptom runbooks

- [High error rate](runbooks/high-error-rate.md)
- [High latency](runbooks/high-latency.md)
- [Quota, budget, or capacity exhaustion](runbooks/capacity-exhaustion.md)
- [Storage unavailable](runbooks/storage-unavailable.md)
- [Unknown model pricing](runbooks/unknown-pricing.md)
