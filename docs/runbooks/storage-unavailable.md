# Durable storage unavailable

1. Treat `/health` as process liveness only; confirm `/ready` returns 503 and
   `omni_storage_ready` is 0.
2. Check network/DNS/TLS and database availability for the configured backend. Never switch to a
   different implicit backend: explicit storage failures intentionally fail closed.
3. Restore the configured backend or credentials, then restart one gateway worker only.
4. Confirm `/ready` is 200 and audit/trace writes persist across one controlled restart before
   resolving.
