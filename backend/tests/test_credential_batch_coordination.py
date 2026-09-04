"""Shared preview and idempotency contracts for credential batch operations."""

from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.credential_batch_coordination import (
    BatchIdempotencyConflictError,
    BatchIdempotencyInProgressError,
    BatchIdempotencyReplay,
    BatchIdempotencyReservation,
    CredentialBatchCoordinationError,
    CredentialBatchCoordinationService,
)
from core.state_store import InMemoryStateStore


class CredentialBatchCoordinationTests(unittest.IsolatedAsyncioTestCase):
    async def test_preview_and_completed_response_are_cross_client(self) -> None:
        store = InMemoryStateStore()
        first = CredentialBatchCoordinationService(store, key=b"a" * 32, fencing_epoch=1)
        second = CredentialBatchCoordinationService(store, key=b"a" * 32, fencing_epoch=1)
        fingerprint = "1" * 64

        preview = await first.issue_preview(fingerprint)
        self.assertTrue(await second.preview_matches(preview, fingerprint))
        self.assertFalse(await second.preview_matches(preview, "2" * 64))

        reservation = await first.reserve("request-key", fingerprint)
        self.assertIsInstance(reservation, BatchIdempotencyReservation)
        body = {"success": True, "results": [{"filename": "a.json"}]}
        await first.complete(reservation, 200, body)

        replay = await second.lookup("request-key", fingerprint)
        self.assertEqual(replay, BatchIdempotencyReplay(200, body))
        reserved_replay = await second.reserve("request-key", fingerprint)
        self.assertEqual(reserved_replay, replay)

    async def test_concurrent_reservation_has_one_owner(self) -> None:
        store = InMemoryStateStore()
        first = CredentialBatchCoordinationService(store, key=b"b" * 32, fencing_epoch=1)
        second = CredentialBatchCoordinationService(store, key=b"b" * 32, fencing_epoch=1)

        results = await asyncio.gather(
            first.reserve("concurrent-key", "3" * 64),
            second.reserve("concurrent-key", "3" * 64),
            return_exceptions=True,
        )

        self.assertEqual(sum(isinstance(item, BatchIdempotencyReservation) for item in results), 1)
        self.assertEqual(
            sum(isinstance(item, BatchIdempotencyInProgressError) for item in results),
            1,
        )

    async def test_conflict_release_and_owner_assertion_are_closed(self) -> None:
        store = InMemoryStateStore()
        service = CredentialBatchCoordinationService(store, key=b"c" * 32, fencing_epoch=1)
        reservation = await service.reserve("shared-key", "4" * 64)
        self.assertIsInstance(reservation, BatchIdempotencyReservation)

        with self.assertRaises(BatchIdempotencyConflictError):
            await service.lookup("shared-key", "5" * 64)
        await service.assert_owner(reservation)
        await service.release(reservation)
        with self.assertRaises(CredentialBatchCoordinationError):
            await service.assert_owner(reservation)
        replacement = await service.reserve("shared-key", "4" * 64)
        self.assertIsInstance(replacement, BatchIdempotencyReservation)

    async def test_large_response_is_chunked_and_reconstructed_exactly(self) -> None:
        store = InMemoryStateStore()
        first = CredentialBatchCoordinationService(store, key=b"d" * 32, fencing_epoch=1)
        second = CredentialBatchCoordinationService(store, key=b"d" * 32, fencing_epoch=1)
        reservation = await first.reserve("large-response-key", "6" * 64)
        self.assertIsInstance(reservation, BatchIdempotencyReservation)
        body = {
            "results": [
                {
                    "filename": f"{index:03}-" + (chr(33 + index % 80) * 240) + ".json",
                    "status": "succeeded",
                }
                for index in range(100)
            ]
        }

        await first.complete(reservation, 200, body)
        replay = await second.lookup("large-response-key", "6" * 64)

        self.assertEqual(replay, BatchIdempotencyReplay(200, body))

    async def test_stale_epoch_and_dependency_loss_fail_closed(self) -> None:
        store = InMemoryStateStore()
        stale = CredentialBatchCoordinationService(store, key=b"e" * 32, fencing_epoch=2)
        with self.assertRaises(CredentialBatchCoordinationError):
            await stale.reserve("stale-key", "7" * 64)

        service = CredentialBatchCoordinationService(store, key=b"e" * 32, fencing_epoch=1)
        await store.close()
        with self.assertRaises(CredentialBatchCoordinationError):
            await service.issue_preview("7" * 64)


if __name__ == "__main__":
    unittest.main()
