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
test selections. Use `--dry-run` or `--list` to inspect a gate without executing it.

The required Chromium harness is `python tools/browser_smoke.py`. Install its isolated dependency
with `python -m pip install -r requirements-browser.txt` and its browser with
`python -m playwright install chromium`. It starts a fresh loopback-only runtime, uses disposable
SQLite state, blocks real provider traffic with deterministic in-browser fixtures, and exercises
all nine critical journeys plus an 11-route accessibility/overflow sweep at 360, 768, 1024, and
1440 pixels. The release runner executes it locally; CI installs Chromium with its Linux system
dependencies in a dedicated required job.

The application and container smokes remain required CI evidence; the release runner labels them
as CI-owned instead of pretending to execute them locally. The release checklist requires the
application, browser, and container jobs to pass for the same candidate commit.

The phase/release configuration contracts also run the versioned R1 compatibility guard and load
the pre-R1 SQLite upgrade fixture. See [Compatibility and deprecation](compatibility.md).

## Required Versus Non-Required

CI names production-blocking verification jobs and steps with `Required:`. The production release
plan never contains any of these separately reported suites:

| Suite | Classification | Command/evidence | Owner |
| --- | --- | --- | --- |
| Live PostgreSQL/MongoDB contracts | Optional | `python -m unittest backend.tests.test_durable_family_migration backend.tests.test_identity_repository_live backend.tests.test_usage_ledger_live -v` | P5.1 |
| Live provider checks | Optional/manual | `docs/release-checklist.md#manual-provider-checks` | P2.1/P2.2 |

List the canonical classifications at any time:

```text
python tools/quality_gate.py --list-suites
```

Skipping or failing an optional suite must be reported under that classification, but
cannot change the Core production verdict. Conversely, no skipped test may cover a Core production
journey.

## Fixed Cadence

- Task: one fast gate plus focused modules after the final relevant edit.
- Phase: one affected integration/DOM/browser slice. Phase 0 additionally runs the complete current
  Core suite once, as specified in `tasks/plan.md`.
- Release: one complete required gate on the immutable candidate. After failure, rerun only the
  failed slice until corrected, then repeat the complete gate once.
- Multi-replica and Kubernetes matrices are outside the product boundary; live providers and every
  optional storage backend remain outside the required cadence.
