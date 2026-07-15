"""Root routes for the management console."""

import re
from html import escape

from core.auth import accept_oauth_callback
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from log import log
from paths import FRONTEND_DIR

router = APIRouter(tags=["root"])


def _oauth_callback_page(success: bool, title: str, message: str) -> HTMLResponse:
    safe_title = escape(title)
    safe_message = escape(message)
    html = f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{safe_title} - Omni Gateway</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Google+Sans:ital,opsz,wght@0,17..18,400..700;1,17..18,400..700&display=swap" rel="stylesheet">
    <style>
        :root {{
            color-scheme: light;
            --text: #111111;
            --muted: #666666;
            --border: #e5e5e5;
            --bg: #ffffff;
            --bg-subtle: #f7f7f7;
            --surface: #ffffff;
            --radius: 8px;
        }}
        * {{
            box-sizing: border-box;
        }}
        body {{
            min-height: 100vh;
            min-height: 100dvh;
            margin: 0;
            display: grid;
            place-items: center;
            padding: 16px;
            background: var(--bg-subtle);
            color: var(--text);
            font-family: "Google Sans", Arial, sans-serif;
        }}
        main {{
            width: min(100%, 480px);
            padding: 28px;
            border: 1px solid var(--border);
            border-radius: var(--radius);
            background: var(--surface);
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 18px;
        }}
        .brand-mark {{
            width: 22px;
            height: 22px;
            flex: 0 0 auto;
        }}
        .brand-mark img {{
            width: 100%;
            height: 100%;
            display: block;
            object-fit: contain;
        }}
        .brand-title {{
            font-size: 16px;
            font-weight: 700;
            line-height: 1.2;
            letter-spacing: 0;
        }}
        h1 {{
            margin: 0 0 8px;
            font-size: 28px;
            line-height: 1.1;
            font-weight: 700;
            letter-spacing: 0;
        }}
        p {{
            margin: 0;
            color: var(--muted);
            font-size: 14px;
            line-height: 1.55;
        }}
    </style>
</head>
<body>
    <main>
        <div class="brand">
            <span class="brand-mark" aria-hidden="true">
                <img src="/frontend/assets/logo.png" alt="">
            </span>
            <span class="brand-title">Omni Gateway</span>
        </div>
        <h1>{safe_title}</h1>
        <p>{safe_message}</p>
    </main>
</body>
</html>"""
    return HTMLResponse(content=html, status_code=200 if success else 400)


@router.get("/callback", response_class=HTMLResponse, include_in_schema=False)
async def serve_oauth_callback(request: Request):
    """Render the OAuth callback result page."""
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    error = request.query_params.get("error")

    if error:
        return _oauth_callback_page(
            False,
            "OAuth Authentication Failed",
            "Google returned an authorization error. Return to Omni Gateway and start the provider authentication flow again.",
        )

    accepted, message = accept_oauth_callback(code, state)
    if accepted:
        return _oauth_callback_page(
            True,
            "OAuth Authentication Successful",
            "Copy this page URL from the browser address bar, return to the Providers page, paste it into the Callback URL field, and save the credential.",
        )

    return _oauth_callback_page(
        False,
        "OAuth Authentication Failed",
        f"{message} Return to Omni Gateway and generate a new authorization link.",
    )


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
@router.get("/login", response_class=HTMLResponse, include_in_schema=False)
@router.get("/setup", response_class=HTMLResponse, include_in_schema=False)
@router.get("/dashboard", response_class=HTMLResponse, include_in_schema=False)
@router.get("/code_assist", response_class=HTMLResponse, include_in_schema=False)
@router.get("/pool", response_class=HTMLResponse, include_in_schema=False)
@router.get("/models", response_class=HTMLResponse, include_in_schema=False)
@router.get("/providers", response_class=HTMLResponse, include_in_schema=False)
@router.get("/provider", response_class=HTMLResponse, include_in_schema=False)
@router.get("/oauth", response_class=HTMLResponse, include_in_schema=False)
@router.get("/upload", response_class=HTMLResponse, include_in_schema=False)
@router.get("/config", response_class=HTMLResponse, include_in_schema=False)
@router.get("/logs", response_class=HTMLResponse, include_in_schema=False)
@router.get("/about", response_class=HTMLResponse, include_in_schema=False)
def serve_control_panel():
    """Serve the single responsive console entry point for public app routes."""
    try:
        with open(FRONTEND_DIR / "control-panel.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        script_assets = (
            "js/core.js",
            "js/ui.js",
            "js/console.js",
            "js/credentials.js",
            "js/settings.js",
            "js/dashboard.js",
        )
        asset_paths = (FRONTEND_DIR / "control-panel.css",) + tuple(
            FRONTEND_DIR / asset for asset in script_assets
        )
        asset_version = max(path.stat().st_mtime_ns for path in asset_paths)
        html_content = re.sub(
            r'href="/frontend/control-panel\.css(?:\?v=[^"]*)?"',
            f'href="/frontend/control-panel.css?v={asset_version}"',
            html_content,
        )
        for asset in script_assets:
            html_content = re.sub(
                rf'src="/frontend/{re.escape(asset)}(?:\?v=[^"]*)?"',
                f'src="/frontend/{asset}?v={asset_version}"',
                html_content,
            )
        return HTMLResponse(content=html_content)
    except Exception as e:
        log.error(f"Failed to load control panel page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
