"""Root routes for the management console."""

import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from log import log
from paths import FRONTEND_DIR


router = APIRouter(tags=["root"])


@router.get("/", response_class=HTMLResponse)
@router.get("/login", response_class=HTMLResponse)
@router.get("/setup", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
@router.get("/code_assist", response_class=HTMLResponse)
@router.get("/pool", response_class=HTMLResponse)
@router.get("/providers", response_class=HTMLResponse)
@router.get("/provider", response_class=HTMLResponse)
@router.get("/oauth", response_class=HTMLResponse)
@router.get("/upload", response_class=HTMLResponse)
@router.get("/config", response_class=HTMLResponse)
@router.get("/logs", response_class=HTMLResponse)
@router.get("/about", response_class=HTMLResponse)
async def serve_control_panel():
    """Serve the single responsive console entry point for public app routes."""
    try:
        with open(FRONTEND_DIR / "control_panel.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        asset_version = int(max(
            (FRONTEND_DIR / "control_panel.css").stat().st_mtime,
            (FRONTEND_DIR / "common.js").stat().st_mtime,
        ))
        html_content = re.sub(
            r'href="/frontend/control_panel\.css(?:\?v=[^"]*)?"',
            f'href="/frontend/control_panel.css?v={asset_version}"',
            html_content,
        )
        html_content = re.sub(
            r'src="/frontend/common\.js(?:\?v=[^"]*)?"',
            f'src="/frontend/common.js?v={asset_version}"',
            html_content,
        )
        return HTMLResponse(content=html_content)
    except Exception as e:
        log.error(f"Failed to load control panel page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
