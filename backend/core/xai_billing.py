"""Grok Build OAuth account quota retrieval and normalization."""

from __future__ import annotations

import base64
import binascii
import json
import math
from datetime import datetime
from typing import Any, Dict, Optional

import httpx
from core.httpx_client import get_async
from core.xai import XaiError

XAI_BILLING_API_URL = "https://cli-chat-proxy.grok.com/v1"


def parse_xai_access_tier(access_token: str) -> Optional[str]:
    """Read the display-only access tier issued in a Grok Build JWT."""
    token = str(access_token or "").strip()
    parts = token.split(".")
    if len(parts) != 3 or len(parts[1]) > 16_384:
        return None
    try:
        padding = "=" * (-len(parts[1]) % 4)
        claims = json.loads(base64.urlsafe_b64decode(parts[1] + padding))
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return None
    if not isinstance(claims, dict):
        return None
    tier = claims.get("tier")
    if isinstance(tier, bool) or not isinstance(tier, int) or not 0 <= tier <= 99:
        return None
    return str(tier)


def _finite_number(value: Any) -> Optional[float]:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _display_number(value: float) -> int | float:
    return int(value) if value.is_integer() else value


def _percentage(value: float) -> int:
    return max(0, min(100, int(math.floor(value + 0.5))))


def _valid_timestamp(value: Any) -> Optional[str]:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip()
    try:
        datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        return None
    return normalized


def parse_xai_monthly_usage(payload: Any) -> Dict[str, Any]:
    """Normalize the required monthly billing response from Grok Build."""
    config = payload.get("config") if isinstance(payload, dict) else None
    if not isinstance(config, dict):
        raise XaiError("Grok Build returned an invalid billing response.", 502)

    limit_container = config.get("monthlyLimit")
    used_container = config.get("used")
    limit = _finite_number(
        limit_container.get("val") if isinstance(limit_container, dict) else None
    )
    used = _finite_number(used_container.get("val") if isinstance(used_container, dict) else None)
    reset_time = _valid_timestamp(config.get("billingPeriodEnd"))
    if limit is None or used is None or limit < 0 or used < 0 or reset_time is None:
        raise XaiError("Grok Build returned an invalid billing response.", 502)

    remaining = max(0.0, limit - used)
    used_percentage = _percentage((used / limit) * 100) if limit > 0 else (100 if used else 0)
    return {
        "limit": _display_number(limit),
        "used": _display_number(used),
        "remaining": _display_number(remaining),
        "used_percentage": used_percentage,
        "remaining_percentage": 100 - used_percentage,
        "reset_time": reset_time,
    }


def parse_xai_weekly_usage(payload: Any) -> Optional[Dict[str, Any]]:
    """Normalize the optional weekly usage response from Grok Build."""
    config = payload.get("config") if isinstance(payload, dict) else None
    if not isinstance(config, dict):
        return None
    current_period = config.get("currentPeriod")
    if not isinstance(current_period, dict) or current_period.get("type") != (
        "USAGE_PERIOD_TYPE_WEEKLY"
    ):
        return None
    reset_time = _valid_timestamp(config.get("billingPeriodEnd"))
    if reset_time is None:
        return None
    raw_percentage = config.get("creditUsagePercent")
    used_percentage = 0 if raw_percentage is None else _finite_number(raw_percentage)
    if used_percentage is None:
        return None
    normalized_percentage = _percentage(used_percentage)
    return {
        "used_percentage": normalized_percentage,
        "remaining_percentage": 100 - normalized_percentage,
        "reset_time": reset_time,
    }


def _billing_headers(access_token: str) -> Dict[str, str]:
    token = str(access_token or "").strip()
    if not token:
        raise XaiError("Grok Build OAuth credential does not contain an access token.")
    return {
        "Authorization": f"Bearer {token}",
        "x-xai-token-auth": "xai-grok-cli",
        "Accept": "application/json",
    }


async def _fetch_optional_weekly_usage(headers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    try:
        response = await get_async(
            f"{XAI_BILLING_API_URL}/billing?format=credits",
            headers=headers,
            timeout=30.0,
        )
        if response.status_code != 200:
            return None
        return parse_xai_weekly_usage(response.json())
    except (httpx.HTTPError, OSError, ValueError, XaiError):
        return None


async def fetch_xai_billing_usage(access_token: str) -> Dict[str, Any]:
    """Fetch required monthly and optional weekly quota for Grok Build OAuth."""
    headers = _billing_headers(access_token)
    try:
        response = await get_async(
            f"{XAI_BILLING_API_URL}/billing",
            headers=headers,
            timeout=30.0,
        )
    except (httpx.HTTPError, OSError) as exc:
        raise XaiError(
            "Unable to reach Grok Build billing. Check outbound network and proxy settings.",
            502,
        ) from exc

    if response.status_code in {401, 403}:
        raise XaiError(
            "Grok Build rejected this OAuth credential while retrieving quota.",
            response.status_code,
        )
    if response.status_code != 200:
        raise XaiError(
            f"Grok Build billing failed with HTTP {response.status_code}.",
            502 if response.status_code >= 500 else 400,
        )
    try:
        monthly = parse_xai_monthly_usage(response.json())
    except ValueError as exc:
        raise XaiError("Grok Build returned an invalid billing response.", 502) from exc

    access_tier = parse_xai_access_tier(access_token)
    return {
        "quota_type": "account_billing",
        "plan": f"Tier {access_tier}" if access_tier is not None else None,
        "monthly": monthly,
        "weekly": await _fetch_optional_weekly_usage(headers),
    }
