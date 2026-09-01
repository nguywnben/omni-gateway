# W4.15 Task 2 implementer report

## Implementation

Implemented `InMemoryStateStore` as the deterministic, lock-protected reference for epoch bootstrap/advance/ready fencing, CAS original-TTL replay, invalidation generations, idempotent close, and fail-closed use after close. Expiry uses one injected monotonic `clock` (default `time.monotonic`).

Canonical quota dataclasses now live in `core.coordination` and are re-exported from `core.state_store`. Existing construction remains compatible: `fencing_epoch=1` and optional `operation_id` were appended after existing fields. `release_quota` retains its current call form and has compatible keyword-only `fencing_epoch=1` and `operation_id=None` values.

Every caller mutation requires the exact ready epoch. Exact reserve/commit replays are idempotent; changed payloads conflict. Cleanup uses expiry heaps, removes at most 256 expired records per mutation, and fails closed when more work is due. Quota capacity is 100,000 records per virtual key; private `_quota_record_limit_for_testing` safely lowers this only for tests.

## Controller ruling applied

The controller authorized an out-of-brief `core/coordination.py` touch because the contract lacked the required typed cleanup signal. Added `CoordinationReconciliationRequiredError(CoordinationUnavailableError)`. Reserve reports `reason="reconciliation_required"`; commit/release and CAS/invalidation raise that typed error. The controller also authorized canonical quota types and release compatibility arguments.

## Files

- Modified `backend/core/coordination.py`
- Modified `backend/core/state_store.py`
- Added `backend/tests/test_coordination_in_memory.py`
- Modified `backend/tests/test_coordination_contract.py`
- Modified `backend/tests/test_quota_reservations.py`

## RED -> GREEN evidence

RED command: `.\.venv\Scripts\python.exe -m unittest backend.tests.test_coordination_in_memory backend.tests.test_quota_reservations backend.tests.test_coordination_contract -v`.

Observed expected missing-feature imports before implementation: `CoordinationReconciliationRequiredError` and canonical quota types were absent; the run ended `FAILED (errors=3)`.

GREEN command: `.\.venv\Scripts\python.exe -m unittest backend.tests.test_coordination_contract backend.tests.test_coordination_in_memory backend.tests.test_quota_reservations backend.tests.test_state_store backend.tests.test_virtual_key_reservations backend.tests.test_virtual_keys -v`.

Fresh result: `Ran 63 tests ... OK`.

Quality checks: `.\.venv\Scripts\ruff.exe check backend`; `.\.venv\Scripts\ruff.exe format --check backend`; `.\.venv\Scripts\python.exe -m compileall -q backend`; `git diff --check`.

Ruff: `All checks passed!`; format: `312 files already formatted`; compileall and diff check exited successfully.

Full discovery was invoked twice with `python -m unittest discover -s backend\\tests -p 'test_*.py'`. Both runs streamed broad normal progress and expected negative-path logs, but the execution wrapper omitted their final unittest summary/exit marker. This report does not claim a full-suite pass; the focused 63-test evidence above is complete.

## Self-review and compatibility

- Exact ready fencing covers CAS, invalidation, and quota reserve/commit/release.
- Cleanup has a shared 256-entry mutation budget; live records are not pruned for capacity admission.
- Existing `from core.state_store import Quota*` imports remain aliases to canonical types.
- Legacy release remains a boolean no-op retry (`False`), so it cannot surface an idempotency flag; this preserves existing callers.
- No Redis implementation, HA activation, runtime caller migration, deployment setting, or networking was added.

## Commit

`feat(coordination): add in-process reference semantics`

## Fix Round 1

Added strict validation for canonical quota request/result types, including boolean-as-integer rejection, identifier, TTL, epoch, amount, limit, and finite-number checks. Moved reserve fencing ahead of quota cleanup and durable reconciliation; commit and release now fence before cleanup. Stale reserve regression coverage proves it cannot mutate committed reconciliation flags.

Controller ruling 9 resolves the replay conflict: fencing/reconciling/unavailable denials do not create replay state because they are not admitted business decisions. The unchanged shared fixture therefore permits the same operation ID after reconciliation. Ready-state successful and business-decision replay behavior remains retained.

Fix RED: focused coordination/domain suite failed on missing quota validation and stale reserve changing reconciliation evidence. Fix GREEN: `python -m unittest backend.tests.test_coordination_contract backend.tests.test_coordination_in_memory backend.tests.test_quota_reservations backend.tests.test_state_store backend.tests.test_virtual_key_reservations -v` ran 47 tests and returned `OK`. Ruff, format check, compileall, and `git diff --check` passed.

## Fix Round 4 (fresh implementer escalation)

Resumed the intentional dirty handoff after the prior escalation session was interrupted. The added discriminating tests were preserved and reconciled with rulings 8-10. Tests that released a one-second reservation exactly at `expires_at` were corrected to exercise an actually active reservation, and the former cross-key cleanup expectation was inverted because target-key operations must not scan or reconcile unrelated keys. The preliminary dual active/committed maps and global expiry heaps were removed rather than extended.

### RED -> GREEN evidence

The required unchanged focused command was first run with system Python:

`python -m unittest backend.tests.test_coordination_contract backend.tests.test_coordination_in_memory backend.tests.test_quota_reservations backend.tests.test_state_store backend.tests.test_virtual_key_reservations backend.tests.test_virtual_keys -v`

It produced a real RED: `Ran 40 tests ... FAILED (failures=5, errors=6)`. The semantic failures covered accepted-ID reactivation, ready-denied CAS/reserve replay flipping, missing terminal tombstones, and commit/release operation conflicts. Four lifecycle tests errored on the missing `_quota_records`/replay-cap implementation. The remaining two errors were environment-only imports because system Python lacked `aiosqlite` and `fastapi`; subsequent verification used the checked-in `.venv`.

Final GREEN with the same six modules under the repository environment:

`.\.venv\Scripts\python.exe -m unittest backend.tests.test_coordination_contract backend.tests.test_coordination_in_memory backend.tests.test_quota_reservations backend.tests.test_state_store backend.tests.test_virtual_key_reservations backend.tests.test_virtual_keys -v`

Fresh result: `Ran 74 tests ... OK`.

### Data model and complexity bounds

- `_QuotaLifecycleRecord` is the single authoritative accepted-reservation record. Its explicit state is `active`, `committed`, `released`, or `expired`; it owns the original reserve fingerprint/result, current committed evidence, active expiry, and terminal `retained_until`.
- `_quota_ids_by_key` bounds all RPM/TPM/budget scans to the target virtual key and the enforced lifecycle cap: 100,000 in production or `_quota_record_limit_for_testing`.
- Lifecycle expiry uses one per-key heap and a current `next_expiry_at`; superseded entries are stale by construction rather than a second source of truth.
- Commit/release/rejected-reserve replay evidence uses a separate per-key map/count/expiry heap bounded at 100,000 in production or `_quota_replay_limit_for_testing`. Unknown reservation operations share one bounded orphan bucket.
- Each mutation shares one 256-pop budget across the directly addressed lifecycle/replay heaps. Every due pop consumes work, including stale nodes. Remaining due work fails closed before business mutation.
- Replay-cap exhaustion returns `reconciliation_required` (or raises the typed reconciliation error where no typed result channel exists) before quota business state changes. Exact retries do not extend expiry.
- Accepted retention uses the longest applicable 60-second/daily/monthly evidence window, capped at 30 days; active records also remain through their active TTL. Commit anchors usage retention at commit time, while release preserves the accepted fingerprint window.

### Files

- Modified `backend/core/state_store.py`: coherent lifecycle, bounded per-key replay evidence, shared cleanup accounting, ready-denied CAS replay, fencing-before-replay ordering, and strict raw release validation.
- Modified `backend/tests/test_coordination_in_memory.py`: discriminating lifecycle, replay, capacity, cleanup, fencing, conflict, and release-validation coverage.
- Modified `backend/tests/test_quota_reservations.py`: target-key cleanup isolation expectation and authoritative lifecycle inspection.
- Modified `backend/tests/test_virtual_key_reservations.py`: private test inspection now reads the authoritative lifecycle record.

No Redis implementation, activation, caller, or deployment behavior changed. Public quota imports, request/result types, defaults, and boolean release contract remain compatible.

### Quality checks and review

- `.\.venv\Scripts\ruff.exe check backend`: `All checks passed!`
- `.\.venv\Scripts\ruff.exe format --check backend`: `312 files already formatted`
- `.\.venv\Scripts\python.exe -m compileall -q backend`: exited successfully
- `git diff --check`: exited successfully
- Secret-pattern diff review found only quota field names such as `estimated_tokens`; no credentials or secrets were added.
- Five-axis self-review found no remaining correctness, security, architecture, or unbounded-work blocker. The focused run still emits pre-existing Python 3.14 deprecation/resource warnings from `test_virtual_keys`; they do not fail the suite and are outside this fix.

### Commit

`fix(coordination): retain bounded quota lifecycle`
