"""Tests for Grok Build OAuth billing quota retrieval."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from core.xai import XaiError
from core.xai_billing import (
    XAI_BILLING_API_URL,
    fetch_xai_billing_usage,
    parse_xai_access_tier,
    parse_xai_monthly_usage,
    parse_xai_weekly_usage,
)


class FakeResponse:
    def __init__(self, status_code: int, payload: dict):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class XaiBillingTests(unittest.IsolatedAsyncioTestCase):
    def test_access_tier_is_read_from_the_provider_token(self):
        token = "header.eyJ0aWVyIjo0fQ.signature"

        self.assertEqual(parse_xai_access_tier(token), "4")

    def test_access_tier_rejects_malformed_or_unsupported_claims(self):
        self.assertIsNone(parse_xai_access_tier("not-a-jwt"))
        self.assertIsNone(parse_xai_access_tier("header.eyJ0aWVyIjp0cnVlfQ.signature"))
        self.assertIsNone(parse_xai_access_tier("header.eyJ0aWVyIjoiUHJvIn0.signature"))

    def test_monthly_usage_is_normalized_for_the_console(self):
        usage = parse_xai_monthly_usage(
            {
                "config": {
                    "monthlyLimit": {"val": 4000},
                    "used": {"val": 1421},
                    "billingPeriodEnd": "2026-08-01T00:00:00+00:00",
                }
            }
        )

        self.assertEqual(usage["limit"], 4000)
        self.assertEqual(usage["used"], 1421)
        self.assertEqual(usage["remaining"], 2579)
        self.assertEqual(usage["used_percentage"], 36)
        self.assertEqual(usage["remaining_percentage"], 64)

    def test_monthly_usage_rejects_malformed_provider_data(self):
        with self.assertRaisesRegex(XaiError, "invalid billing response"):
            parse_xai_monthly_usage(
                {
                    "config": {
                        "monthlyLimit": {"val": "4000"},
                        "used": {"val": 1421},
                        "billingPeriodEnd": "not-a-date",
                    }
                }
            )

    def test_weekly_usage_defaults_to_zero_at_the_start_of_a_period(self):
        usage = parse_xai_weekly_usage(
            {
                "config": {
                    "currentPeriod": {"type": "USAGE_PERIOD_TYPE_WEEKLY"},
                    "billingPeriodEnd": "2026-07-25T00:00:00+00:00",
                }
            }
        )

        self.assertEqual(usage["used_percentage"], 0)
        self.assertEqual(usage["remaining_percentage"], 100)

    async def test_fetch_uses_grok_build_billing_contract(self):
        tier_token = "header.eyJ0aWVyIjo0fQ.signature"
        request = AsyncMock(
            side_effect=[
                FakeResponse(
                    200,
                    {
                        "config": {
                            "monthlyLimit": {"val": 4000},
                            "used": {"val": 1421},
                            "billingPeriodEnd": "2026-08-01T00:00:00+00:00",
                        }
                    },
                ),
                FakeResponse(
                    200,
                    {
                        "config": {
                            "currentPeriod": {"type": "USAGE_PERIOD_TYPE_WEEKLY"},
                            "creditUsagePercent": 28.4,
                            "billingPeriodEnd": "2026-07-25T00:00:00+00:00",
                        }
                    },
                ),
            ]
        )
        with patch("core.xai_billing.get_async", request):
            usage = await fetch_xai_billing_usage(tier_token)

        self.assertEqual(request.await_args_list[0].args[0], f"{XAI_BILLING_API_URL}/billing")
        self.assertEqual(
            request.await_args_list[1].args[0],
            f"{XAI_BILLING_API_URL}/billing?format=credits",
        )
        headers = request.await_args_list[0].kwargs["headers"]
        self.assertEqual(headers["Authorization"], f"Bearer {tier_token}")
        self.assertEqual(headers["x-xai-token-auth"], "xai-grok-cli")
        self.assertNotIn("x-user-id", headers)
        self.assertEqual(usage["quota_type"], "account_billing")
        self.assertEqual(usage["plan"], "Tier 4")
        self.assertEqual(usage["weekly"]["used_percentage"], 28)

    async def test_weekly_quota_is_optional_when_the_endpoint_is_unavailable(self):
        request = AsyncMock(
            side_effect=[
                FakeResponse(
                    200,
                    {
                        "config": {
                            "monthlyLimit": {"val": 4000},
                            "used": {"val": 100},
                            "billingPeriodEnd": "2026-08-01T00:00:00+00:00",
                        }
                    },
                ),
                FakeResponse(503, {"error": "unavailable"}),
            ]
        )
        with patch("core.xai_billing.get_async", request):
            usage = await fetch_xai_billing_usage("oauth-access-token")

        self.assertIsNone(usage["weekly"])

    async def test_rejected_token_returns_a_sanitized_error(self):
        with patch(
            "core.xai_billing.get_async",
            AsyncMock(return_value=FakeResponse(401, {"secret": "upstream details"})),
        ):
            with self.assertRaisesRegex(XaiError, "rejected this OAuth credential") as context:
                await fetch_xai_billing_usage("expired-token")

        self.assertEqual(context.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()
