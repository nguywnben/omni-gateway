# HA runtime lifecycle contract

## Status

Accepted implementation specification for W4.18. It defines configuration, ownership, readiness,
reconciliation, and rollback without granting the W4.19 activation record or production release.

## Closed runtime policy

`OMNI_RUNTIME_MODE` accepts only `standalone` (default) or `coordinated`.

Standalone requires `WORKERS=1` and `OMNI_REPLICA_COUNT=1`. Redis coordination settings are
rejected rather than ignored when the mode is standalone, except the legacy `REDIS_URL` cache
setting while coordinated activation remains unavailable. The lifecycle creates one in-process
state store and injects that same fenced store into authentication admission, sessions, OIDC,
provider/device authorization, credential-batch coordination, credential routing, virtual-key
quota, governance invalidation, and exact-cache
metadata. Provider conversation metadata uses the same lifecycle service with HMAC-derived keys and
fenced compare-and-set updates; it never creates a second Redis client or falls back after a
coordination error.

Coordinated configuration requires all of the following:

- `WORKERS=1`; one worker per process is a permanent v1 semantic constraint.
- `OMNI_REPLICA_COUNT=1`. W4.19 recorded no tested multi-replica ceiling.
- exactly one external durable backend: `POSTGRESQL_URI` or `MONGODB_URI`, never SQLite or both;
- `REDIS_URL` using `redis`, `rediss`, or `unix` transport;
- a validated lowercase/hyphen `OMNI_COORDINATION_NAMESPACE` and stable
  `OMNI_DEPLOYMENT_ID`;
- a base64url `OMNI_COORDINATION_KEY` decoding to 32-64 bytes;
- positive `OMNI_COORDINATION_EPOCH` matching the durable binding and Redis ready epoch;
- an exact durable migration manifest/checkpoint and an activation record compiled into a future
  release only after every required external failure/load gate passes. W4.19 produced no record.

Unknown values, empty required fields, contradictory backends, unsafe counts, or a supplied but
incomplete coordinated group reject startup. There is no local fallback after coordinated mode is
selected. MongoDB's legacy Redis acceleration is disabled in coordinated mode: the coordination
URI is reserved for the versioned namespaced adapter and never receives unnamespaced credential or
configuration cache keys.

## Persistent binding and namespace-loss defense

The durable backend is the source of a versioned coordination binding containing only deployment
ID, namespace digest, identifier-key fingerprint, fencing epoch, manifest checksum, and activation
record revision. Redis contains a matching fixed-key fenced marker. Neither side stores the raw
namespace key or Redis URI.

The lifecycle requires both records to exist and match before constructing consumers. A missing
Redis marker with an existing durable binding means namespace loss and fails readiness/startup; it
must never initialize a fresh deployment silently. A missing durable binding requires the explicit
bootstrap command, which is itself blocked until the canonical durable inventory and W4.19
activation record are ready. Partial bootstrap is resumable from the stable deployment ID and
fingerprints, never by deleting either side.

## Lifecycle states and readiness

States are `starting`, `standalone_ready`, `coordinated_ready`, `draining`, `reconciling`,
`unavailable`, and `closed`. Only the two ready states permit `/ready` HTTP 200. `/health` remains a
content-free process-liveness probe and never touches Redis or durable storage.

Coordinated readiness verifies the durable backend, selected usage ledger, coordination service,
exact epoch state, binding match, and not-draining state. Dependency failure immediately returns a
content-free 503 projection. Recovery requires a successful probe; stale/reconciling epochs never
become ready automatically.

## Operator transitions

The lifecycle exposes bounded commands for `status`, `drain`, `advance-epoch`, `reconcile`,
`mark-ready`, and `rollback-plan`.

- Mutating commands require explicit apply mode; dry-run is the default.
- Operation IDs are caller supplied or persisted so retries are idempotent.
- Drain writes the persistent typed admission fence. Each distributed admission checks that record
  under its mutation lock or Redis script, so nothing linearized after the drain write can acquire
  new capacity or admit a new security mutation. A valid fence raises a bounded admission-fenced
  error; corrupt or mismatched records fail closed. Existing CAS revisions alone are not settlement
  proof. Quota settlement, OIDC consume, and CAS domain settlement with a verified prior admission
  operation remain available while the same epoch is ready.
  Unknown settlement identities do not allocate new negative replay records while drained;
  expired admission evidence cannot authorize a fresh settlement operation.
- Epoch advance moves exactly `ready(N)` to `reconciling(N+1)`.
- Reconciliation validates bindings and durable authority; it never copies, switches, or deletes
  durable data automatically.
- Mark-ready accepts only the exact reconciling epoch after reconciliation evidence. If a crash
  occurs after marking the epoch ready but before removing the drain, retrying the identical
  mark-ready operation completes removal without advancing/changing the epoch. Removal compares
  the exact completed prior-epoch drain, binding, ready epoch, and successful retained operation
  replay atomically. A different operation or mismatched/replaced drain remains an error. Dry-run
  never removes the drain. A fully completed transition with no remaining drain remains retry-safe.
  Crash completion requires the original mark-ready operation replay to remain retained.
- Rollback emits and validates a plan to one standalone worker/replica. It never changes durable
  authority, clears Redis, or edits deployment configuration automatically.

## Deployment and evidence boundary

Compose, Helm, and container defaults remain one worker/replica and standalone. Coordinated values
are explicit and secrets use environment/Secret references. Termination grace must allow drain;
probes remain `/health` and `/ready`.

W4.18 tests configuration matrices, lifecycle transitions, namespace-loss/partial-binding defense,
readiness, secret-free metrics, rendered manifests, and unchanged standalone startup. W4.19 owns
forced-failure/load evidence and the only activation record. Without its complete evidence, Omni
Gateway remains supported only in standalone mode even though the coordinated implementation is
present.
