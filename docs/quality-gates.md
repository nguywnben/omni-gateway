# Quality Gates

Omni Gateway uses one gate runner with increasing scope. Run commands from the repository root with
the active project virtual environment.

## Gate Selection

| Situation | Command | Scope |
| --- | --- | --- |
| While editing | `python tools/quality_gate.py fast` | Lint, format, compile, suite partition, recursive JavaScript syntax, YAML, shell syntax, whitespace |
| End of one task | `python tools/quality_gate.py task --test-module backend.tests.test_config_security` | Fast gate plus only explicitly affected core test modules |
| Phase boundary | `python tools/quality_gate.py phase --test-module backend.tests.test_product_surface_inventory` | Fast gate, config contracts, translation audits, and the affected integration/DOM slice |
| Release candidate | `python tools/quality_gate.py release` | One complete required core, dependency, application, browser, and container gate |

Repeat `--test-module` for every directly affected module. Task and phase commands reject empty
test selections and reject modules assigned to the experimental HA suite. Use `--dry-run` or
`--list` to inspect a gate without executing it.

P5.4 owns the required real-browser harness. Until that task supplies it, the release plan labels
`browser-smoke` as `pending` and the non-dry release command fails before running expensive checks.
The application and container smokes are already implemented as required CI evidence; the release
runner labels them as CI-owned instead of pretending to execute them locally. The release checklist
requires both jobs to pass for the same candidate commit.

## Required Versus Non-Required

CI names production-blocking verification jobs and steps with `Required:`. The production release
plan never contains any of these separately reported suites:

| Suite | Classification | Command/evidence | Owner |
| --- | --- | --- | --- |
| Live PostgreSQL/MongoDB contracts | Optional | `python -m unittest backend.tests.test_durable_family_migration backend.tests.test_identity_repository_live backend.tests.test_usage_ledger_live -v` | P5.1 |
| Live provider checks | Optional/manual | `docs/release-checklist.md#manual-provider-checks` | P2.1/P2.2 |
| Redis coordination and topology | Experimental | `python -m backend.tests --suite experimental-ha` | Post-R1 |

List the canonical classifications at any time:

```text
python tools/quality_gate.py --list-suites
```

Skipping or failing an optional/experimental suite must be reported under that classification, but
cannot change the Core production verdict. Conversely, no skipped test may cover a Core production
journey.

## Fixed Cadence

- Task: one fast gate plus focused modules after the final relevant edit.
- Phase: one affected integration/DOM/browser slice. Phase 0 additionally runs the complete current
  Core suite once, as specified in `tasks/plan.md`.
- Release: one complete required gate on the immutable candidate. After failure, rerun only the
  failed slice until corrected, then repeat the complete gate once.
- Experimental HA, two-replica matrices, live providers, and every optional storage backend are
  always outside the required cadence.
