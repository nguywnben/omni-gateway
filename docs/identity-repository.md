# Management Identity Repository

## Status and Scope

Wave 4 slice W4.4 provides the versioned storage-agnostic identity contract and its standalone
SQLite implementation. It does not activate OIDC login, add identity APIs, replace browser
sessions, or change the supported single-worker/single-replica topology. PostgreSQL and MongoDB
parity and storage-adapter selection belong to W4.5.

## Durable Records

The repository owns four schema-version-1 record families:

- management identities: local owner or OIDC user, enabled state, resource revision, and
  authorization epoch;
- one role binding per identity, with its own revision and an explicit `local_bootstrap`,
  `direct_binding`, or `claim_mapping` source;
- one OIDC policy revision/authorization epoch checkpoint;
- the fixed `management_identity_v1` additive migration checkpoint.

OIDC identity is the exact, case-sensitive `(issuer, subject)` pair. Email, display name, group
labels, secrets, tokens, and presentation profile data have no field in the durable contract.
Opaque generated `idn_…` and `rbd_…` identifiers prevent raw identity attributes from entering
resource URLs, errors, or normal record representations.

All records have a closed shape, strict primitive and enum types, bounded identifiers and
timestamps, UTC timestamps, and a supported schema version. Stored rows are reconstructed through
the same validators used for new records; unknown, malformed, incomplete, or contradictory rows
fail closed as store corruption.

## Concurrency and Owner Safety

Identity state, role bindings, and OIDC policy are separate optimistic-concurrency resources.
Callers must provide the current revision for the resource being changed. SQLite writers use an
immediate write transaction and a conditional revision update, so concurrent writes with the same
revision produce exactly one winner. Authorization-affecting identity or role changes also advance
the identity authorization epoch; OIDC policy changes advance the policy authorization epoch.

The backward-compatible `local-owner` identity and `binding-local-owner` owner binding are created
idempotently. The bootstrap identity remains enabled and its binding is immutable. Claim mapping
cannot assign `owner`. W4.4 intentionally exposes no delete operation, so rollback leaves identity
and migration evidence intact.

## SQLite Migration

`SQLiteIdentityRepository.initialize()` opens the selected `credentials.db`, enables WAL and
foreign-key enforcement, begins one immediate transaction, and creates only additive tables and
indexes:

- `management_identities`;
- `management_role_bindings`;
- `oidc_policy_revision`;
- `identity_migrations`.

It then inserts missing bootstrap records without overwriting existing rows, validates every
identity/binding pair plus the singleton checkpoints, and commits only if the complete store is
consistent. Failure rolls the transaction back and leaves pre-existing credential/configuration
tables untouched. Foreign keys are enabled on every repository connection, and dynamic values are
always passed as SQL parameters.

## Verification Contract

The W4.4 tests cover exact issuer/subject matching, duplicate rejection without attribute leakage,
closed record shapes, page bounds, additive/idempotent initialization, restart persistence,
sequential and concurrent revision conflicts, independent identity/binding revisions, atomic role
updates, policy revisions, local-owner lockout prevention, claim-to-owner rejection, rollback, and
corrupted-row failure during reads and restart.

The repository is not yet a runtime authentication source. W4.5 must implement the same observable
contract for PostgreSQL and MongoDB and connect repository selection through the existing storage
adapter before sessions or OIDC consume it.

## Implementation References

- SQLite transaction semantics: <https://sqlite.org/lang_transaction.html>
- SQLite foreign-key activation and indexing: <https://www.sqlite.org/foreignkeys.html>
- SQLite table constraints: <https://www.sqlite.org/lang_createtable.html>
- aiosqlite connection and transaction API: <https://aiosqlite.omnilib.dev/en/stable/api.html>
