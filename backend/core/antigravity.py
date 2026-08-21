"""Google Antigravity provider metadata and authentication helpers."""

from __future__ import annotations

from typing import Any

import httpx
from config import get_antigravity_api_url, get_antigravity_user_agent
from core.httpx_client import post_async


class AntigravityError(Exception):
    """Raised when Antigravity provider metadata cannot be retrieved."""

    def __init__(self, message: str, *, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code


async def build_antigravity_headers(
    access_token: str,
    *,
    user_agent: str | None = None,
) -> dict[str, str]:
    """Build the common request headers used by Antigravity upstream calls."""
    resolved_user_agent = user_agent or await get_antigravity_user_agent()
    return {
        "User-Agent": resolved_user_agent,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
    }


def parse_antigravity_model_ids(payload: Any) -> list[str]:
    """Return a deterministic model catalog from an Antigravity response."""
    models = payload.get("models") if isinstance(payload, dict) else None
    if not isinstance(models, dict):
        return []

    model_ids = {
        str(model_id).strip().split("/")[-1]
        for model_id in models
        if isinstance(model_id, str) and str(model_id).strip()
    }

    # Antigravity accepts these public aliases even when only one variant is listed.
    if "claude-sonnet-4-6" in model_ids:
        model_ids.add("claude-sonnet-4-6-thinking")
    if "claude-opus-4-6-thinking" in model_ids:
        model_ids.add("claude-opus-4-6")

    return sorted(model_ids)


async def fetch_antigravity_model_ids(
    access_token: str,
    *,
    api_base_url: str | None = None,
    user_agent: str | None = None,
) -> list[str]:
    """Discover the models available to one Antigravity credential."""
    if not str(access_token or "").strip():
        raise AntigravityError(
            "Antigravity credential does not contain an access token.", status_code=401
        )

    resolved_base_url = (api_base_url or await get_antigravity_api_url()).rstrip("/")
    try:
        response = await post_async(
            url=f"{resolved_base_url}/v1internal:fetchAvailableModels",
            json={},
            headers=await build_antigravity_headers(
                str(access_token),
                user_agent=user_agent,
            ),
            timeout=30.0,
        )
    except (httpx.HTTPError, OSError) as exc:
        raise AntigravityError(
            "Unable to reach Google Antigravity. Check outbound network and proxy settings.",
            status_code=502,
        ) from exc

    if response.status_code != 200:
        raise AntigravityError(
            f"Unable to retrieve Antigravity models (HTTP {response.status_code}).",
            status_code=response.status_code,
        )

    try:
        model_ids = parse_antigravity_model_ids(response.json())
    except (TypeError, ValueError) as exc:
        raise AntigravityError(
            "Google Antigravity returned an invalid model response.",
            status_code=502,
        ) from exc
    if not model_ids:
        raise AntigravityError("Antigravity returned an empty model catalog.", status_code=502)
    return model_ids
