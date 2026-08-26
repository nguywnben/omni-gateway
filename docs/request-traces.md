# Request Decision Trace Contract

Omni Gateway persists one bounded, redacted decision trace for each supported inference request.
The trace is operational evidence, not a prompt-observability store: request content, response
content, authorization values, API keys, credential filenames, arbitrary metadata, and exception
text are outside the schema and fail strict record validation.

## Versioned summary

Schema version 1 records a generated trace ID, the public `X-Request-ID`, a closed protocol and
outcome, UTC start/completion timestamps, status and duration, bounded model/provider dimensions,
normalized token/cost totals, a truncation flag, and at most 64 ordered decisions. Supported
decision categories cover request admission, routing/fallback, retry, cooldown, compression,
guardrails, cache, quota, upstream execution, usage, and final outcome. Actions, results, and
reason codes are closed vocabularies; free-text detail cannot enter durable storage.

Supported request surfaces are OpenAI Chat Completions and Responses, Anthropic Messages and token
counting, Gemini generate/stream/count-token, and their Vertex equivalents. Management requests and
raw runtime logs are deliberately excluded.

## Lifecycle and storage

The request middleware creates the collector after validating or generating `X-Request-ID`.
Non-streaming traces are finalized with the response; streaming traces finalize after the body is
consumed or cancelled so deferred provider decisions and cleanup are included. Trace persistence
is best-effort and cannot alter the inference response, while a configured trace repository that
cannot initialize still fails application startup rather than silently disabling evidence.

SQLite, PostgreSQL, and MongoDB use additive `request_traces` storage with request, protocol/outcome,
route, and stable-order indexes. Records are revalidated on every read. Signed opaque cursors and
strict query types form the repository boundary used by the management API in W3.11.

Trace retention is independent from audit and raw-log retention. Its separate persisted default is
7 days or 100,000 traces, whichever limit is reached first; supported policy bounds are 1–90 days
and 1,000–1,000,000 traces. Age pruning runs before oldest-first count pruning after each append and
on policy update. No database TTL index bypasses this explicit policy.
