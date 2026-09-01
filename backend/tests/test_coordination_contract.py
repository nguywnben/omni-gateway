"""Validation and wire-contract tests for coordination primitives."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.coordination import (
    MAX_PAYLOAD_BYTES,
    CasRequest,
    CasResult,
    Epoch,
    EpochState,
    InvalidationRequest,
    InvalidationResult,
    decode_cas_result,
    decode_epoch,
    decode_invalidation_result,
)


class CoordinationDomainTests(unittest.TestCase):
    def test_requests_reject_boolean_integer_fields(self) -> None:
        with self.assertRaises(ValueError):
            Epoch(epoch=True, state=EpochState.READY)
        with self.assertRaises(ValueError):
            CasRequest("key", 0, b"payload", 1.0, 1, True)
        with self.assertRaises(ValueError):
            InvalidationRequest("scope", 1, "op", replay_ttl_seconds=True)

    def test_requests_reject_non_finite_and_out_of_range_values(self) -> None:
        for value in (math.nan, math.inf, -math.inf, 0.0, 30 * 86_400 + 1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                CasRequest("key", 0, b"payload", value, 1, "op")
        for revision in (-1, 2**63):
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                CasRequest("key", revision, b"payload", 1.0, 1, "op")
        for epoch in (0, -1, 2**63):
            with self.subTest(epoch=epoch), self.assertRaises(ValueError):
                InvalidationRequest("scope", epoch, "op")

    def test_requests_reject_malformed_identifiers_and_oversized_payloads(self) -> None:
        for identifier in ("", "\n", "has\x00control", "x" * 129):
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                CasRequest(identifier, 0, b"payload", 1.0, 1, "op")
        with self.assertRaises(ValueError):
            CasRequest("key", 0, b"x" * (MAX_PAYLOAD_BYTES + 1), 1.0, 1, "op")
        with self.assertRaises(ValueError):
            InvalidationRequest("scope", 1, "\tbad")

    def test_stored_reply_decoders_require_exact_schema_and_types(self) -> None:
        self.assertEqual(
            decode_epoch({"schema_version": 1, "epoch": 2, "state": "ready"}),
            Epoch(epoch=2, state=EpochState.READY),
        )
        self.assertEqual(
            decode_cas_result(
                {
                    "schema_version": 1,
                    "applied": True,
                    "revision": 2,
                    "idempotent": False,
                }
            ),
            CasResult(applied=True, revision=2),
        )
        self.assertEqual(
            decode_invalidation_result(
                {
                    "schema_version": 1,
                    "applied": True,
                    "generation": 2,
                    "idempotent": True,
                }
            ),
            InvalidationResult(applied=True, generation=2, idempotent=True),
        )
        for reply in (
            {"schema_version": 1, "epoch": 2, "state": "ready", "extra": "no"},
            {"schema_version": 1, "epoch": True, "state": "ready"},
            {"schema_version": 1, "epoch": 2, "state": "unknown"},
        ):
            with self.subTest(reply=reply), self.assertRaises(ValueError):
                decode_epoch(reply)

    def test_representations_never_include_payload_or_operation_id(self) -> None:
        secret = "Bearer top-secret-token"
        values = (
            CasRequest("key", 0, secret.encode(), 1.0, 1, secret),
            InvalidationRequest("scope", 1, secret),
        )
        for value in values:
            with self.subTest(value=type(value).__name__):
                self.assertNotIn(secret, repr(value))


if __name__ == "__main__":
    unittest.main()
