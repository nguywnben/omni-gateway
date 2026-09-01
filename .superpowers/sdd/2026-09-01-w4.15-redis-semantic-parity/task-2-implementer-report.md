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
