# Omni Gateway Production Self-Hosted R1 — Fixed Checklist

Progress denominator: **3/36** implementation tasks. Planning artifacts do not count as completed
implementation. The denominator cannot change without an approved `CR-###` in `tasks/plan.md`.

## Approval Gate

- [x] User approved `CONSTRAINTS.md`, `docs/specs/production-self-hosted.md`, and `tasks/plan.md` on
  2026-09-08.

## Phase 0 — Scope Reset and Truthful Baseline (3/6)

- [x] P0.1 Capability registry and support tiers
- [x] P0.2 Product terminology and navigation inventory
- [x] P0.3 Isolate unfinished HA work
- [ ] P0.4 Risk and maintainability baseline
- [ ] P0.5 Fast, phase, and release gates
- [ ] P0.6 Compatibility and deprecation guard

## Phase 1 — Installation, Configuration, Recovery (0/6)

- [ ] P1.1 Authoritative typed configuration schema
- [ ] P1.2 Minimal canonical Docker Compose profile
- [ ] P1.3 First-run setup and preflight
- [ ] P1.4 Versioned backup, validation, and restore
- [ ] P1.5 Update and rollback workflow
- [ ] P1.6 Supported install matrix

## Phase 2 — Gateway Correctness and AI Quality (0/6)

- [ ] P2.1 Provider capability matrix
- [ ] P2.2 Connection tests and actionable provider errors
- [ ] P2.3 Cross-protocol contract corpus
- [ ] P2.4 Streaming, cancellation, timeout, and retry semantics
- [ ] P2.5 Routing, fallback, cooldown, and health
- [ ] P2.6 Compression and quality-policy hardening

## Phase 3 — Coherent Core Console (0/6)

- [ ] P3.1 Navigation and conditional complexity
- [ ] P3.2 Shared page states and accessible interaction
- [ ] P3.3 Production dashboard
- [ ] P3.4 Provider onboarding
- [ ] P3.5 Credential fleet operations
- [ ] P3.6 Models and routing workflow

## Phase 4 — Complete Product Workflows (0/6)

- [ ] P4.1 AI Quality console completion
- [ ] P4.2 Playground backend boundary
- [ ] P4.3 Playground interface
- [ ] P4.4 Access lifecycle completion
- [ ] P4.5 Unified Activity
- [ ] P4.6 Settings, Team access, About, and localization

## Phase 5 — Operational Hardening and Release (0/6)

- [ ] P5.1 Storage tiers and migrations
- [ ] P5.2 Authentication and security closure
- [ ] P5.3 Usage, cost, and observability closure
- [ ] P5.4 Browser test harness and CI balance
- [ ] P5.5 Fixed reliability and performance evidence
- [ ] P5.6 Release candidate, documentation, and handoff

## Scope Controls

- [ ] No unapproved `CR-###` exists.
- [ ] No new Wave, phase, suffix, hidden checklist, or alternate progress denominator exists.
- [ ] Experimental HA/Kubernetes work has not blocked a core-production task.
- [ ] Post-R1 backlog work has not entered the release candidate.
