# ADR-002: Secure First Run and Enforce Single-Worker Operation

- Status: Accepted
- Date: 2026-07-12

## Context

An unconfigured instance previously allowed the first browser that reached the setup endpoint to establish the console password. That is convenient on localhost but unsafe when a new container is immediately exposed on a public VPS. The service also accepted `WORKERS` values greater than one even though credential reservations, cooldowns, sessions, and usage counters were not coordinated across processes.

## Decision

Direct setup through a loopback client and loopback host remains token-free. Every remote setup request must present a bootstrap token. Operators can configure `SETUP_TOKEN`; otherwise the process generates a high-entropy token and prints it to the application or container logs. The token is useful only while no console password exists.

The 1.x runtime accepts exactly one worker and one application replica. MongoDB and PostgreSQL remain optional storage backends, but they do not imply horizontal-scaling support. A future multi-worker design must provide distributed credential reservations, cooldown state, session invalidation, and centralized usage aggregation before this restriction is relaxed.

## Consequences

- A public first deployment cannot be claimed by an unauthenticated visitor who does not possess the bootstrap token.
- Local development keeps its existing setup flow.
- Remote operators must read the startup logs or set `SETUP_TOKEN` before setup.
- Invalid scale-out configurations fail early with an actionable message.
- Horizontal scaling is deferred rather than represented as production-ready prematurely.
