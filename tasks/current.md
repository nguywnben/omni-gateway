# Omni Gateway — Current State

## Resume Here

- Updated: 2026-09-08 (Asia/Saigon)
- Active plan: `PROD-SELFHOST-R1`
- Target: production-quality self-hosting for one person or a trusted team, not enterprise service
  operation.
- Progress: **8/36 implementation tasks**; Phase 1 is in progress (2/6).
- Completed: **P1.2 — Minimal canonical Docker Compose profile**.
- Next task: **P1.3 — First-run setup and preflight**.
- Supported runtime today: standalone, one worker, one replica.
- Redis coordination, multi-replica HA, and Helm are experimental and no longer R1 release blockers.

## Why the Plan Was Reset

The prior enterprise plan delivered substantial credential, audit, access, identity, storage, and
coordination work, but its Wave 4 HA closure expanded repeatedly and over-weighted distributed
failure evidence relative to the needs of a personal/small-team self-hosted product. Completed code
is preserved. Unfinished enterprise activation is frozen rather than allowed to keep changing the
release denominator.

## Authoritative Reading Order

1. `CONSTRAINTS.md`
2. `docs/audits/production-baseline-2026-09-08.md`
3. `docs/specs/production-self-hosted.md`
4. `tasks/plan.md`
5. `tasks/todo.md`
6. `git status` and recent commits

Historical enterprise specs, ADRs, evidence, and git history remain useful context but cannot
override the current product boundary or completion rules.

## Working Tree Caution

Before starting the next task, inspect the working tree and preserve unrelated user-owned changes.
Do not push unless the user requests it.

## Fixed Verification Cadence

- Task: focused tests only.
- Phase: affected integration/browser gate once.
- Release candidate: full required gate once; rerun failed slices before another full pass.
- No HA topology matrix in R1.
- No cross-model review except one security pass for backup/restore or final auth/security closure,
  unless the user explicitly requests another.

## Latest Evidence

- `docs/evidence/p1.2-minimal-compose-profile.md`
- Default Compose now needs no external database or Redis, exposes only common production
  controls, and persists all application state in one named volume; advanced controls require an
  explicit override file.
- The canonical CI path performs fresh setup, force-recreate persistence, readiness, and graceful
  shutdown checks through Compose. Local Docker evidence passed both authenticated smoke runs;
  shutdown exited 0 in 0.96 seconds with a read-only root filesystem.
- `docs/evidence/p1.1-authoritative-configuration-schema.md`
- All 124 documented environment variables now have one typed Basic/Advanced/Experimental schema;
  startup validates scalar boundaries before storage initialization and warns on unknown `OMNI_*`
  controls.
- Settings field ownership, secret-safe metadata, environment locks, restart classification,
  writable/resettable keys, generated documentation, and `.env`/Compose parity derive from or are
  checked against the same contract.
- The focused P1.1 task gate passed without running the complete Core or experimental HA suites.
- `docs/evidence/p0.6-compatibility-deprecation-guard.md`
- The immutable `r1-v1` fixture protects 18 public inference operations, 112 management
  operations, console routes/aliases, config migrations, nine stored schema versions, and seven
  generated client examples.
- A populated pre-R1 SQLite fixture now upgrades without losing credentials or config. The fixture
  exposed and fixed SQLite's rejection of expression defaults during additive column migration.
- The Phase 0 gate passed configuration/inventory contracts, all translation audits (1,116 keys),
  and 71 affected tests. The 168-module Core suite was covered in order after fixes: 1,417 tests
  passed with 22 intentional optional/live skips. No HA topology matrix ran.
- `docs/evidence/p0.5-fixed-quality-gates.md`
- One runner now defines fast, focused task, affected phase, and single release scopes. The fast
  gate passed in seconds without the complete Core suite; the release dry-run lists 16 fixed steps.
- Required CI checks are visibly named, while optional storage/provider tests and experimental HA
  are listed separately and cannot change the production result.
- The focused gate contract passed 8 tests. The checked partition contained 167 Core modules and 13
  experimental-HA modules; no complete Core or HA topology run was added to P0.5.
- `docs/evidence/p0.4-risk-maintainability-baseline.md`
- The reproducible inventory records 9 modules at or above 1,500 lines, 7 parallel persistence
  families, 8 Pydantic v1-style sites, 480 broad exception handlers across 96 runtime files, 11
  conditional skip sites, 7 live/environment-gated modules, and the missing browser harness.
- All 12 bounded risks are owned by existing P0–P5 tasks or the post-R1 backlog. No file-size-only
  refactor, new task, wave, phase, or denominator was authorized.
- The focused baseline contract passed 5 tests and the independent inventory reproduction check
  matched the saved artifact.
- `docs/evidence/p0.3-experimental-ha-isolation.md`
- Default startup is standalone without Redis; coordinated startup is rejected before external I/O,
  and the compiled experimental activation allowlist remains empty.
- The P0.3 checked partition contained 165 core modules and 13 experimental-HA modules. The focused
  P0.3 gate passed 35 tests; the independently runnable experimental suite passed 109 tests and
  skipped 32 existing opt-in live cases.
- CI and the R1 release checklist now require the partition audit and core suite, not external
  two-replica evidence.
- `docs/evidence/p0.2-product-surface-inventory.md`
- Checked inventory: 11 pages/tabs, 134 OpenAPI operations, 24 Settings controls, 124 example
  environment variables, 16 advertised claims, and explicit locale ownership.
- Product copy now presents the fixed Core/Advanced/Compatibility/Experimental self-host boundary in
  both curated languages; Redis coordination and Kubernetes/Helm are explicitly experimental.
- P0.2 focused console/localization gate: 53 tests passed; all four localization audits passed.
- `docs/evidence/p0.1-capability-registry.md`
- Default runtime snapshot: 31 capabilities; only Core entries are active.
- Focused contract/runtime matrix: 45 tests passed.
- Full backend gate: 1,522 tests run; 1,468 passed and 54 existing optional/live-backend cases
  skipped.
- Ruff, compileall, runtime HTTP projection, and whitespace checks passed.
