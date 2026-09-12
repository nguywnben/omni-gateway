# Routing and cache coordination evidence

## Current activation status

The routing, quota, governance-invalidation, and exact-cache metadata boundary has deterministic
semantic coverage, but the production runtime does **not** select Redis or authorize more than one
application worker or replica. The supported topology remains the standalone in-process store with
`WORKERS=1` and one application replica. Experimental artifacts do not change that release limit.

Do not treat the presence of `REDIS_URL`, an available Redis server, or passing unit parity tests
as activation approval. Never place prompt, response, embedding, credential filename, model name,
virtual-key identifier, or provider error content in Redis.

## Evidence commands

Run the deterministic contract and fake-driver suites:

```powershell
& '.venv\Scripts\python.exe' -m unittest `
  backend.tests.test_routing_coordination `
  backend.tests.test_routing_coordination_redis `
  backend.tests.test_smart_routing `
  backend.tests.test_governance_coordination `
  backend.tests.test_response_cache `
  backend.tests.test_quota_lifecycle
```

For explicit live parity, supply a non-production Redis endpoint only for the command:

```powershell
$env:OMNI_TEST_REDIS_URI = '<dedicated test Redis URI>'
& '.venv\Scripts\python.exe' -m unittest backend.tests.test_routing_coordination_redis_live
Remove-Item Env:OMNI_TEST_REDIS_URI
```

The live suite derives a unique namespace and deletes only that namespace. Without the variable it
must report an explicit skip. Connection, fencing, semantic, or cleanup failures are real failures;
do not convert them to skips or fall back to local state.

## Failure interpretation

- An unavailable, stale-epoch, reconciling, corrupt, capacity-exhausted, or retry-exhausted
  coordination decision closes credential and quota admission.
- Exact-cache coordination failure is a cache miss: evict local derived bytes and forward through
  the normal provider path. It must never serve an unverified local hit.
- An acquire cancelled after an unknown CAS outcome may leave one bounded lease. Its server-time
  expiry is the recovery mechanism; do not manually edit or delete shared records.
- More than 100 credential candidates fails selection before provider or coordination reads.
  Split the deployment or reduce the eligible set rather than increasing the bound ad hoc.
- A credential record admits at most 128 active leases and a route record retains at most 10
  latency samples. CAS operations retry at most eight times.

## Telemetry

`omni_routing_coordination_events_total{operation,result}` exposes only fixed semantic labels.
Investigate growth in `rejected` or `conflict` alongside the lower-level
`omni_coordination_operations_total{backend,operation,result}` counter. Neither counter contains
raw identifiers or errors. In W4.17 these counters are per process and diagnostic only; W4.18 owns
readiness and alerts for a selected backend.

## Bounded reference measurement

On 2026-09-04, the deterministic in-memory test admitted 128 leases, rejected the 129th, verified
the payload stayed below 16 KiB, and completed that test in 78 ms on the development host. This is
only a regression ceiling for the reference adapter. It is not a Redis benchmark, production SLO,
multi-replica load result, or evidence for enabling HA; W4.19 owns those measurements.

## Safe recovery before activation

Keep the single-worker/single-replica deployment and restart the committed application normally.
Do not advance an epoch, clear a Redis namespace, edit CAS payloads, or switch backends manually.
W4.18 will add the supported drain, epoch, reconciliation, and rollback lifecycle before Redis can
be selected.
