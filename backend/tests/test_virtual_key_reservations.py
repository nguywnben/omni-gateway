"""Reservation-aware virtual-key enforcement contracts for W3.7."""

from __future__ import annotations

import asyncio
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.state_store import InMemoryStateStore
from core.virtual_keys import VirtualKey, VirtualKeyManager
from fastapi import HTTPException


class VirtualKeyReservationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.manager = VirtualKeyManager(state_store=InMemoryStateStore())
        self.manager._loaded = True

    @staticmethod
    def _key(**overrides) -> VirtualKey:
        values = {
            "id": "vk_reservation",
            "name": "reservation",
            "key_hash": "hash",
            "key_preview": "sk-ogw-vk-...tion",
            "enabled": True,
            "created_at": time.time(),
        }
        values.update(overrides)
        return VirtualKey(**values)

    @staticmethod
    def _body(*, model: str = "gpt-4o-mini", max_tokens: int = 20) -> dict:
        return {
            "model": model,
            "messages": [{"role": "user", "content": "Explain atomic reservations."}],
            "max_tokens": max_tokens,
        }

    async def test_concurrent_requests_cannot_cross_rpm_limit(self):
        record = self._key(rpm_limit=1)

        async def reserve(reservation_id: str):
            try:
                return await self.manager.enforce(
                    record,
                    requested_model="gpt-4o-mini",
                    request_body=self._body(),
                    reservation_id=reservation_id,
                    now=1000.0,
                )
            except HTTPException as exc:
                return exc

        results = await asyncio.gather(reserve("request-a"), reserve("request-b"))

        self.assertEqual(sum(isinstance(item, str) for item in results), 1)
        rejection = next(item for item in results if isinstance(item, HTTPException))
        self.assertEqual(rejection.status_code, 429)
        self.assertIn("Retry-After", rejection.headers)

    async def test_release_after_provider_failure_returns_reserved_capacity(self):
        record = self._key(rpm_limit=1)
        reservation_id = await self.manager.enforce(
            record,
            request_body=self._body(),
            reservation_id="failed-request",
            now=1000.0,
        )

        self.assertTrue(await self.manager.release_reservation(reservation_id, now=1001.0))
        replacement = await self.manager.enforce(
            record,
            request_body=self._body(),
            reservation_id="replacement-request",
            now=1001.0,
        )

        self.assertEqual(replacement, "replacement-request")

    async def test_tpm_is_reserved_from_estimated_input_and_output(self):
        record = self._key(tpm_limit=5)

        with self.assertRaises(HTTPException) as raised:
            await self.manager.enforce(
                record,
                request_body=self._body(max_tokens=20),
                reservation_id="too-large",
                now=1000.0,
            )

        self.assertEqual(raised.exception.status_code, 429)
        self.assertIn("Token rate limit", raised.exception.detail)

    async def test_deny_unknown_pricing_fails_closed_for_hard_budget(self):
        record = self._key(budget_daily_usd=1.0, unknown_pricing_policy="deny")

        with self.assertRaises(HTTPException) as raised:
            await self.manager.enforce(
                record,
                requested_model="unpriced-enterprise-model",
                candidate_models=["unpriced-enterprise-model"],
                request_body=self._body(model="unpriced-enterprise-model"),
                reservation_id="unpriced-denied",
                now=1000.0,
            )

        self.assertEqual(raised.exception.status_code, 429)
        self.assertIn("pricing", raised.exception.detail.lower())

    async def test_warn_unknown_pricing_allows_bounded_reservation(self):
        record = self._key(budget_daily_usd=1.0, unknown_pricing_policy="warn")
        with patch("core.usage_stats.get_spend_since", return_value={"cost_usd": 0.0}):
            reservation_id = await self.manager.enforce(
                record,
                requested_model="unpriced-enterprise-model",
                candidate_models=["unpriced-enterprise-model"],
                request_body=self._body(model="unpriced-enterprise-model"),
                reservation_id="unpriced-warning",
                now=1000.0,
            )

        self.assertEqual(reservation_id, "unpriced-warning")

    async def test_fallback_pricing_reserves_cost_for_unknown_model(self):
        record = self._key(
            budget_daily_usd=0.000001,
            unknown_pricing_policy="fallback",
            fallback_price_usd_per_million=10.0,
        )
        with patch("core.usage_stats.get_spend_since", return_value={"cost_usd": 0.0}):
            with self.assertRaises(HTTPException) as raised:
                await self.manager.enforce(
                    record,
                    requested_model="unpriced-enterprise-model",
                    candidate_models=["unpriced-enterprise-model"],
                    request_body=self._body(model="unpriced-enterprise-model"),
                    reservation_id="fallback-priced",
                    now=1000.0,
                )

        self.assertEqual(raised.exception.status_code, 429)
        self.assertIn("Budget", raised.exception.detail)

    async def test_hard_budget_fails_closed_when_ledger_is_unavailable(self):
        record = self._key(budget_daily_usd=10.0)
        with patch(
            "core.usage_stats.get_spend_since",
            return_value={"cost_usd": 0.0, "available": False},
        ):
            with self.assertRaises(HTTPException) as raised:
                await self.manager.enforce(
                    record,
                    requested_model="gpt-4o-mini",
                    request_body=self._body(),
                    reservation_id="ledger-unavailable",
                    now=1000.0,
                )

        self.assertEqual(raised.exception.status_code, 503)

    async def test_commit_replaces_estimate_with_actual_usage(self):
        record = self._key(tpm_limit=100)
        reservation_id = await self.manager.enforce(
            record,
            request_body=self._body(max_tokens=20),
            reservation_id="completed-request",
            now=1000.0,
        )

        result = await self.manager.commit_reservation(
            reservation_id,
            actual_tokens=150,
            actual_cost_usd=0.25,
            durable_cost_recorded=True,
            now=1001.0,
        )

        self.assertTrue(result.committed)
        self.assertTrue(result.overspent)


if __name__ == "__main__":
    unittest.main()
