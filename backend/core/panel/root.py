"""Root routes for the management console."""

import re
from functools import lru_cache
from html import escape

from core.auth import accept_oauth_callback
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from log import log
from paths import FRONTEND_DIR

router = APIRouter(tags=["root"])

CONSOLE_FRAGMENT_PATHS = (
    "auth/login.html",
    "auth/setup.html",
    "layout/sidebar.html",
    "layout/mobile-header.html",
    "pages/dashboard.html",
    "pages/pool.html",
    "pages/models.html",
    "pages/providers.html",
    "pages/settings.html",
    "pages/logs.html",
    "pages/about.html",
    "layout/footer.html",
)

CONSOLE_STYLE_ASSETS = (
    "css/foundation.css",
    "css/shell.css",
    "css/providers-and-models.css",
    "css/forms-and-data.css",
    "css/components.css",
    "css/dialogs.css",
    "css/responsive.css",
)

CONSOLE_SCRIPT_ASSETS = (
    "js/core/i18n.js",
    "js/core/navigation.js",
    "js/core/credential-manager.js",
    "js/core/upload-manager.js",
    "js/core/state.js",
    "js/ui/notifications.js",
    "js/ui/api-integration.js",
    "js/ui/dialog-content.js",
    "js/ui/dialogs.js",
    "js/ui/credential-dialogs.js",
    "js/ui/credential-cards.js",
    "js/features/authentication.js",
    "js/features/navigation.js",
    "js/features/model-pool.js",
    "js/features/code-assist-authentication.js",
    "js/features/antigravity-authentication.js",
    "js/features/credential-pool.js",
    "js/features/credential-diagnostics.js",
    "js/features/credential-batch-actions.js",
    "js/features/logs.js",
    "js/features/environment-credentials.js",
    "js/features/provider-settings-shared.js",
    "js/features/google-ai-studio-settings.js",
    "js/features/xai-settings.js",
    "js/features/openai-settings.js",
    "js/features/antigravity-settings.js",
    "js/features/system-settings.js",
    "js/features/dashboard.js",
    "js/features/version.js",
    "js/features/mobile-navigation.js",
)


def _console_asset_paths():
    return tuple(
        FRONTEND_DIR / asset
        for asset in (
            *CONSOLE_STYLE_ASSETS,
            *CONSOLE_SCRIPT_ASSETS,
        )
    )


def _console_asset_version() -> int:
    return max(path.stat().st_mtime_ns for path in _console_asset_paths())


@lru_cache(maxsize=4)
def _read_console_bundle(asset_paths: tuple[str, ...], asset_version: int, separator: str) -> str:
    """Read a versioned bundle while keeping source files independently editable."""
    del asset_version
    return (
        separator.join(
            (FRONTEND_DIR / relative_path).read_text(encoding="utf-8").rstrip()
            for relative_path in asset_paths
        )
        + "\n"
    )


def _bundle_cache_headers(request: Request) -> dict[str, str]:
    if request.query_params.get("v"):
        return {"Cache-Control": "public, max-age=31536000, immutable"}
    return {"Cache-Control": "no-cache"}


def _assemble_console_html() -> str:
    """Assemble the console shell from its fixed, repository-owned fragments."""
    html_content = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")
    fragment_root = FRONTEND_DIR / "fragments"

    for relative_path in CONSOLE_FRAGMENT_PATHS:
        marker = f"<!-- include:fragments/{relative_path} -->"
        fragment = (fragment_root / relative_path).read_text(encoding="utf-8").rstrip()
        if marker not in html_content:
            raise RuntimeError(f"Console shell is missing the fragment marker: {marker}")
        html_content = html_content.replace(marker, fragment, 1)

    if "<!-- include:fragments/" in html_content:
        raise RuntimeError("Console shell contains an unresolved fragment marker.")
    return html_content


@router.get("/frontend/console.css", include_in_schema=False)
def serve_console_styles(request: Request):
    """Serve the ordered console styles as one cacheable response."""
    asset_version = _console_asset_version()
    content = _read_console_bundle(CONSOLE_STYLE_ASSETS, asset_version, "\n")
    return Response(
        content=content,
        media_type="text/css",
        headers=_bundle_cache_headers(request),
    )


@router.get("/frontend/console.js", include_in_schema=False)
def serve_console_scripts(request: Request):
    """Serve the ordered console modules as one cacheable classic script."""
    asset_version = _console_asset_version()
    content = _read_console_bundle(CONSOLE_SCRIPT_ASSETS, asset_version, "\n;\n")
    return Response(
        content=content,
        media_type="text/javascript",
        headers=_bundle_cache_headers(request),
    )


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
        html_content = _assemble_console_html()
        asset_version = _console_asset_version()
        html_content = re.sub(
            r'href="/frontend/console\.css(?:\?v=[^"]*)?"',
            f'href="/frontend/console.css?v={asset_version}"',
            html_content,
        )
        html_content = re.sub(
            r'src="/frontend/console\.js(?:\?v=[^"]*)?"',
            f'src="/frontend/console.js?v={asset_version}"',
            html_content,
        )
        return HTMLResponse(content=html_content)
    except Exception as e:
        log.error(f"Failed to load control panel page: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
