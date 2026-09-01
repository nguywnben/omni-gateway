# W4.15 Task 3 implementer report: Redis fenced primitives

## Scope and provenance

Base: `67dc863135c8cc785b8a8bf100b208c184c85ff1`.

This report finalizes the interrupted Task 3 artifact only:

- `backend/core/redis_state_store.py`
- `backend/core/state_store.py`
- `backend/tests/test_redis_state_store.py`

No runtime backend selection, coordinated-mode activation, readiness wiring, caller migration, or
Task 4 quota implementation was added. Redis quota methods remain fail-closed placeholders.

### Inherited RED evidence

The prior-agent handoff reported the expected pre-implementation RED as a
`ModuleNotFoundError` for the missing Redis implementation. That is inherited prior-agent
evidence, not an independently re-run result: the implementation was already present when this
finalization began.

Separately, my first requested `.venv` pytest invocation was blocked before collection by the
environment: `C:\\Users\\nben6\\workspace\\omni-gateway\\.venv\\Scripts\\python.exe: No module named pytest`.
This is a current `ModuleNotFoundError` for pytest itself, not a Task 3 code failure. The repository's
standard-library unittest runner is installed and was used for independent GREEN verification.

## Independent verification

Exact successful commands/results:

```text
.venv\\Scripts\\python.exe -m unittest backend.tests.test_redis_state_store backend.tests.test_state_store -v
Ran 22 tests in 0.428s
OK

.venv\\Scripts\\python.exe -m unittest -q backend.tests.test_coordination_contract backend.tests.test_coordination_in_memory backend.tests.test_state_store backend.tests.test_redis_state_store
Ran 57 tests in 1.101s
OK

.venv\\Scripts\\python.exe -m unittest -q backend.tests.test_coordination_contract backend.tests.test_coordination_in_memory backend.tests.test_quota_reservations backend.tests.test_quota_lifecycle backend.tests.test_state_store backend.tests.test_redis_state_store
Ran 73 tests in 5.592s
OK

.venv\\Scripts\\python.exe -m compileall -q backend\\core\\redis_state_store.py backend\\core\\state_store.py backend\\tests\\test_redis_state_store.py
exit 0

.venv\\Scripts\\ruff.exe check backend\\core\\redis_state_store.py backend\\core\\state_store.py backend\\tests\\test_redis_state_store.py
All checks passed!

.venv\\Scripts\\ruff.exe format --check backend\\core\\redis_state_store.py backend\\core\\state_store.py backend\\tests\\test_redis_state_store.py
3 files already formatted

.venv\\Scripts\\python.exe -m pip check
No broken requirements found.

git diff --check
exit 0
```

The installed client is `redis 8.1.0`; the repository range is
`redis>=8.1.0,<9.0` in `requirements.txt`.

## Implementation inventory

### Key layout

All Redis keys render as `omni:{sha256(deployment_namespace)}:v1:<category>[:sha256(logical)]`.
The deployment digest is the shared Redis Cluster hash tag, while every caller-provided logical
name is digested before it becomes a key suffix. Categories are `epoch`, `cas`, `invalidation`,
`generic`, `lock`, and bounded replay/expiry pairs for epoch advance, epoch ready, CAS, and
invalidation.

### Fixed Lua scripts

| Script | Purpose | Keys |
| --- | --- | --- |
| `epoch_read` | bootstrap/read epoch | epoch |
| `epoch_advance` | ready -> next reconciling epoch with replay | epoch, advance replay, advance expiry |
| `epoch_ready` | reconciling -> ready with replay | epoch, ready replay, ready expiry |
| `cas` | fenced opaque compare-and-set with replay | epoch, record, CAS replay, CAS expiry |
| `invalidation` | fenced monotonic generation with replay | epoch, generation, invalidation replay, invalidation expiry |
| `invalidation_read` | side-effect-free generation read | generation |
| `increment` | legacy atomic increment | generic key |
| `lock_release` | token-checked lock release | lock key |

Scripts are application-owned fixed source registered through redis-py's `register_script`, so
redis-py reloads and retries its known script after `NOSCRIPT`. All accessed keys are explicit
`KEYS` entries; input is passed in `ARGV`; scripts use Redis `TIME` for expiry, have no
`KEYS`/`SCAN`, and replay cleanup is limited to 256 due entries.

## Concrete fix during finalization

The replay-bearing scripts previously called `tonumber(replay_expiry)` immediately after checking
only presence symmetry between the replay hash and expiry ZSET. A malformed/non-integer score
could consequently produce a generic Lua execution error, normalized as unavailable, rather than
the contract's corruption error.

Added RED test: `RedisStateStoreTests.test_scripts_are_fixed_cluster_safe_and_bounded` asserted
that `epoch_advance`, `epoch_ready`, `cas`, and `invalidation` validate `replay_expiry` with their
strict integer codec before calling `tonumber()`. It failed for all four scripts. The scripts now
return `COORDINATION_CORRUPT` when a present score is not a valid bounded positive integer. The
focused test then passed, followed by the suites above.

## Self-review

- Correctness: verified strict reply codecs, epoch fencing, stale/reconciling behavior, replay,
  bounded cleanup/capacity, Redis server time, and quota placeholders against the Task 3 brief and
  coordination-store contract.
- Architecture: `redis_state_store.py` imports canonical coordination types only; it does not
  import `state_store.py`. `state_store.py` re-exports the Redis class only after defining
  `BaseStateStore` and registers its virtual subclass, avoiding a circular import.
- Security: the client is lazy and binary-safe (`decode_responses=False`); URL values are retained
  only privately and error/repr paths are secret-free; raw deployment/logical names do not enter
  rendered Redis keys; lock release compares the locally generated token atomically.
- Performance/bounds: no unbounded scan or script loop; all replay hashes have explicit caps;
  `ZRANGEBYSCORE` cleanup has a hard 257 fetch / 256 deletion budget and reports reconciliation
  required before exceeding it.
- Diff review: no runtime activation change and no production secrets. The only `secret` literals
  are intentionally synthetic test inputs that prove redaction behavior.

## Remaining concern

No live Redis server was configured for this local finalization, so Redis cluster runtime behavior
is covered by driver-boundary fakes plus static script inspection rather than an integration server.
Task 5 owns opt-in live Redis parity and operability evidence.
