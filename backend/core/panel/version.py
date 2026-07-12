"""Runtime build metadata and release update discovery."""

from __future__ import annotations

import os
import subprocess
from dataclasses import asdict, dataclass

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from log import log
from paths import PROJECT_ROOT

router = APIRouter(prefix="/api/version", tags=["version"])
LATEST_COMMIT_URL = "https://api.github.com/repos/nguywnben/omni-gateway/commits/main"


@dataclass(frozen=True)
class BuildMetadata:
    version: str
    full_hash: str
    message: str
    date: str


def _run_git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=PROJECT_ROOT,
        capture_output=True,
        check=True,
        text=True,
        timeout=2,
    )
    return result.stdout.strip()


def get_build_metadata() -> BuildMetadata:
    """Resolve immutable container metadata, then source-checkout metadata."""
    revision = os.getenv("BUILD_REVISION", "").strip()
    version = os.getenv("BUILD_VERSION", "").strip()
    build_date = os.getenv("BUILD_DATE", "").strip()
    if revision or version:
        display_version = version
        if version.lower() in {"", "dev", "latest", "main"} and revision:
            display_version = revision[:7]
        return BuildMetadata(
            version=display_version or "development",
            full_hash="" if revision == "unknown" else revision,
            message="Container build",
            date=build_date,
        )

    try:
        revision = _run_git("rev-parse", "HEAD")
        return BuildMetadata(
            version=revision[:7],
            full_hash=revision,
            message=_run_git("log", "-1", "--pretty=%s"),
            date=_run_git("log", "-1", "--pretty=%cI"),
        )
    except (OSError, subprocess.SubprocessError):
        return BuildMetadata(
            version="development",
            full_hash="",
            message="Development build",
            date="",
        )


def _remote_metadata(payload: dict) -> BuildMetadata:
    revision = str(payload.get("sha") or "").strip()
    commit = payload.get("commit") if isinstance(payload.get("commit"), dict) else {}
    committer = commit.get("committer") if isinstance(commit.get("committer"), dict) else {}
    message = str(commit.get("message") or "").splitlines()[0]
    return BuildMetadata(
        version=revision[:7] or "unknown",
        full_hash=revision,
        message=message,
        date=str(committer.get("date") or ""),
    )


@router.get("/info")
async def get_version_info(check_update: bool = False):
    current = get_build_metadata()
    response_data = {"success": True, **asdict(current)}

    if not check_update:
        return JSONResponse(response_data)

    try:
        from core.httpx_client import get_async

        response = await get_async(
            LATEST_COMMIT_URL,
            headers={"Accept": "application/vnd.github+json"},
            timeout=10.0,
        )
        if response.status_code != 200:
            raise RuntimeError(f"GitHub returned HTTP {response.status_code}")

        latest = _remote_metadata(response.json())
        response_data.update(
            {
                "check_update": True,
                "has_update": (
                    current.full_hash != latest.full_hash
                    if current.full_hash and latest.full_hash
                    else None
                ),
                "latest_version": latest.version,
                "latest_hash": latest.full_hash,
                "latest_message": latest.message,
                "latest_date": latest.date,
            }
        )
    except Exception as exc:
        log.debug(f"Update check failed: {exc}")
        response_data.update(
            {
                "check_update": False,
                "update_error": "Unable to check for updates.",
            }
        )

    return JSONResponse(response_data)
