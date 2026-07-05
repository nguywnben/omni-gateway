"""Root routes for the Omni Gateway management console."""

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
@router.get("/omni", response_class=HTMLResponse)
@router.get("/oauth", response_class=HTMLResponse)
@router.get("/upload", response_class=HTMLResponse)
@router.get("/config", response_class=HTMLResponse)
@router.get("/logs", response_class=HTMLResponse)
@router.get("/about", response_class=HTMLResponse)
async def serve_control_panel():
    """Serve the single responsive console entry point for every app route."""
    try:
        with open(FRONTEND_DIR / "control_panel.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except Exception as e:
        log.error(f"Failed to load control panel page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
