"""Reusable semantic assertions for every CoordinationStore implementation."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from core.coordination import (
    CasRequest,
    CoordinationUnavailableError,
    EpochState,
    InvalidationRequest,
)

if TYPE_CHECKING:
    from core.coordination import CoordinationStore


class CoordinationStoreContract:
    """Mixin for async tests; implementations provide ``self.store``."""

    store: CoordinationStore

    async def assert_epoch_cas_and_invalidation_contract(
        self, *, expire_cas: Callable[[], Awaitable[None]]
    ) -> None:
        """Assert parity using an implementation-supplied, server-safe expiry hook."""
        epoch = await self.store.read_epoch()
        self.assertEqual(epoch.epoch, 1)
        self.assertEqual(epoch.state, EpochState.READY)

        advanced = await self.store.advance_epoch(1, "advance-1")
        self.assertEqual(advanced.epoch, 2)
        self.assertEqual(advanced.state, EpochState.RECONCILING)
        self.assertEqual(await self.store.advance_epoch(1, "advance-1"), advanced)
        self.assertEqual(await self.store.advance_epoch(2, "advance-1"), advanced)
        self.assertEqual(await self.store.advance_epoch(1, "advance-conflict"), advanced)

        stale_cas = await self.store.compare_and_set(
            CasRequest("contract-key", 0, b"value", 1.0, 2, "cas-1")
        )
        self.assertFalse(stale_cas.applied)

        self.assertEqual(await self.store.mark_epoch_ready(1, "ready-stale"), advanced)
        ready = await self.store.mark_epoch_ready(2, "ready-1")
        self.assertEqual(ready.state, EpochState.READY)
        self.assertEqual(await self.store.mark_epoch_ready(2, "ready-1"), ready)
        self.assertEqual(await self.store.mark_epoch_ready(1, "ready-1"), ready)
        self.assertEqual(await self.store.mark_epoch_ready(1, "ready-conflict"), ready)

        cas = await self.store.compare_and_set(
            CasRequest("contract-key", 0, b"value", 1.0, 2, "cas-1")
        )
        self.assertTrue(cas.applied)
        self.assertEqual(cas.revision, 1)
        replayed_cas = await self.store.compare_and_set(
            CasRequest("contract-key", 0, b"value", 1.0, 2, "cas-1")
        )
        self.assertEqual(replayed_cas.revision, 1)
        self.assertTrue(replayed_cas.idempotent)
        conflicting_cas = await self.store.compare_and_set(
            CasRequest("contract-key", 1, b"different", 1.0, 2, "cas-1")
        )
        self.assertFalse(conflicting_cas.applied)
        updated_cas = await self.store.compare_and_set(
            CasRequest("contract-key", 1, b"updated", 1.0, 2, "cas-2")
        )
        self.assertEqual(updated_cas.revision, 2)

        expiring_cas = await self.store.compare_and_set(
            CasRequest("expiry-key", 0, b"value", 1.0, 2, "expiry-1")
        )
        self.assertEqual(expiring_cas.revision, 1)
        await expire_cas()
        expired_cas = await self.store.compare_and_set(
            CasRequest("expiry-key", 0, b"replacement", 1.0, 2, "expiry-2")
        )
        self.assertEqual(expired_cas.revision, 1)

        self.assertIsNone(
            (await self.store.read_invalidation_generation("contract-scope")).generation
        )
        invalidation = await self.store.invalidate(
            InvalidationRequest("contract-scope", 2, "invalidate-1")
        )
        self.assertTrue(invalidation.applied)
        self.assertEqual(invalidation.generation, 1)
        replayed_invalidation = await self.store.invalidate(
            InvalidationRequest("contract-scope", 2, "invalidate-1")
        )
        self.assertEqual(replayed_invalidation.generation, 1)
        self.assertTrue(replayed_invalidation.idempotent)
        conflicting_invalidation = await self.store.invalidate(
            InvalidationRequest("contract-scope", 2, "invalidate-1", replay_ttl_seconds=2.0)
        )
        self.assertFalse(conflicting_invalidation.applied)
        incremented_invalidation = await self.store.invalidate(
            InvalidationRequest("contract-scope", 2, "invalidate-2")
        )
        self.assertEqual(incremented_invalidation.generation, 2)
        self.assertEqual(
            (await self.store.read_invalidation_generation("contract-scope")).generation, 2
        )

        await self.store.close()
        await self.store.close()
        with self.assertRaises(CoordinationUnavailableError):
            await self.store.read_epoch()
