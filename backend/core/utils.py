import hashlib
import os
import secrets
import time
from typing import List, Optional
from urllib.parse import urlsplit

import jwt
from config import get_panel_password, trust_proxy_headers_enabled
from fastapi import Depends, Header, HTTPException, Query, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from log import log

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)

# ====================== OAuth Configuration ======================

CODE_ASSIST_VERSION = os.getenv("CODE_ASSIST_VERSION", "0.35.2")
CODE_ASSIST_PLATFORM = os.getenv("CODE_ASSIST_PLATFORM", "win32")
CODE_ASSIST_ARCH = os.getenv("CODE_ASSIST_ARCH", "x64")
CODE_ASSIST_SURFACE = os.getenv("CODE_ASSIST_SURFACE", "cloud-shell")


def get_code_assist_user_agent(model: str = "") -> str:
    if model:
        return f"Code Assist/{CODE_ASSIST_VERSION}/{model} ({CODE_ASSIST_PLATFORM}; {CODE_ASSIST_ARCH}; {CODE_ASSIST_SURFACE})"
    return f"Code Assist/{CODE_ASSIST_VERSION} ({CODE_ASSIST_PLATFORM}; {CODE_ASSIST_ARCH}; {CODE_ASSIST_SURFACE})"


CODE_ASSIST_USER_AGENT = get_code_assist_user_agent()


CODE_ASSIST_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/cclog",
    "https://www.googleapis.com/auth/experimentsandconfigs",
]


TOKEN_URL = "https://oauth2.googleapis.com/token"


CALLBACK_HOST = "localhost"

# Model name lists for different features
BASE_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-lite",
]


# ====================== Model Helper Functions ======================


def is_fake_streaming_model(model_name: str) -> bool:
    """Check if model name indicates fake streaming should be used."""
    return model_name.startswith("fake-streaming/")


def is_anti_truncation_model(model_name: str) -> bool:
    """Check if model name indicates anti-truncation should be used."""
    return model_name.startswith("streaming-anti-truncation/")


def get_base_model_from_feature_model(model_name: str) -> str:
    """Get base model name from feature model name."""
    # Remove feature prefixes
    for prefix in ["fake-streaming/", "streaming-anti-truncation/"]:
        if model_name.startswith(prefix):
            return model_name[len(prefix) :]
    return model_name


def get_available_models(router_type: str = "openai") -> List[str]:
    """
    Get available models with feature prefixes.

    Args:
        router_type: "openai" or "gemini"

    Returns:
        List of model names with feature prefixes
    """
    models = []

    for base_model in BASE_MODELS:
        models.append(base_model)

        models.append(f"fake-streaming/{base_model}")

        models.append(f"streaming-anti-truncation/{base_model}")

        thinking_suffixes = []

        if "gemini-2.5" in base_model:
            thinking_suffixes = ["-max", "-high", "-medium", "-low", "-minimal"]

        elif "gemini-3" in base_model:
            if "flash" in base_model:
                thinking_suffixes = ["-high", "-medium", "-low", "-minimal"]
            elif "pro" in base_model:
                thinking_suffixes = ["-low"]

        search_suffix = "-search"

        for thinking_suffix in thinking_suffixes:
            models.append(f"{base_model}{thinking_suffix}")
            models.append(f"fake-streaming/{base_model}{thinking_suffix}")
            models.append(f"streaming-anti-truncation/{base_model}{thinking_suffix}")

        models.append(f"{base_model}{search_suffix}")
        models.append(f"fake-streaming/{base_model}{search_suffix}")
        models.append(f"streaming-anti-truncation/{base_model}{search_suffix}")

        for thinking_suffix in thinking_suffixes:
            combined_suffix = f"{thinking_suffix}{search_suffix}"
            models.append(f"{base_model}{combined_suffix}")
            models.append(f"fake-streaming/{base_model}{combined_suffix}")
            models.append(f"streaming-anti-truncation/{base_model}{combined_suffix}")

    return models


# ====================== Authentication Functions ======================


async def authenticate_flexible(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="x-api-key"),
    access_token: Optional[str] = Header(None, alias="access_token"),
    x_goog_api_key: Optional[str] = Header(None, alias="x-goog-api-key"),
    x_anthropic_auth_token: Optional[str] = Header(None, alias="x-anthropic-auth-token"),
    anthropic_auth_token: Optional[str] = Header(None, alias="anthropic-auth-token"),
    key: Optional[str] = Query(None),
) -> str:
    token = None
    auth_method = None

    if key:
        token = key
        auth_method = "URL parameter 'key'"

    elif x_goog_api_key:
        token = x_goog_api_key
        auth_method = "x-goog-api-key header"

    elif x_anthropic_auth_token:
        token = x_anthropic_auth_token
        auth_method = "x-anthropic-auth-token header"

    elif anthropic_auth_token:
        token = anthropic_auth_token
        auth_method = "anthropic-auth-token header"

    elif x_api_key:
        token = x_api_key
        auth_method = "x-api-key header"

    elif access_token:
        token = access_token
        auth_method = "access_token header"

    elif authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer <token>'.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = authorization[7:]
        auth_method = "Authorization Bearer header"

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials. Use the 'key' URL parameter, the 'x-goog-api-key', 'x-anthropic-auth-token', 'anthropic-auth-token', 'x-api-key', or 'access_token' header, or 'Authorization: Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from config import API_KEY_PREFIX, get_api_key

    api_key = await get_api_key()

    if not token.startswith(API_KEY_PREFIX):
        log.debug(f"Authentication failed using {auth_method}: invalid API key prefix")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"API key must start with {API_KEY_PREFIX}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not secrets.compare_digest(token, api_key):
        log.debug(f"Authentication failed using {auth_method}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    log.debug(f"Authentication successful using {auth_method}")
    return token


authenticate_bearer = authenticate_flexible
authenticate_gemini_flexible = authenticate_flexible


# ====================== Panel Authentication Functions ======================

PANEL_SESSION_AUDIENCE = "panel"
PANEL_SESSION_ALGORITHM = "HS256"
PANEL_SESSION_COOKIE = "panel_session"
PANEL_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def _get_panel_session_ttl_seconds() -> int:
    raw_ttl = os.getenv("PANEL_SESSION_TTL_SECONDS", "86400")
    try:
        ttl = int(raw_ttl)
    except ValueError:
        ttl = 86400
    return max(300, min(ttl, 2592000))


def _panel_cookie_is_secure(request: Request) -> bool:
    configured = os.getenv("PANEL_COOKIE_SECURE", "").strip().lower()
    if configured in {"1", "true", "yes", "on"}:
        return True
    if configured in {"0", "false", "no", "off"}:
        return False
    forwarded_proto = request.headers.get("x-forwarded-proto", "")
    if forwarded_proto and trust_proxy_headers_enabled():
        return forwarded_proto.split(",", 1)[0].strip().lower() == "https"
    return request.url.scheme == "https"


def set_panel_session_cookie(
    response: Response,
    token: str,
    request: Request,
) -> None:
    """Set the control-panel session as a browser-only cookie."""
    response.set_cookie(
        key=PANEL_SESSION_COOKIE,
        value=token,
        max_age=_get_panel_session_ttl_seconds(),
        httponly=True,
        secure=_panel_cookie_is_secure(request),
        samesite="lax",
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"


def clear_panel_session_cookie(response: Response) -> None:
    """Expire the control-panel session cookie."""
    response.delete_cookie(
        key=PANEL_SESSION_COOKIE,
        path="/",
        httponly=True,
        samesite="lax",
    )
    response.headers["Cache-Control"] = "no-store"


async def _get_panel_session_secret() -> bytes:
    password = await get_panel_password()
    if not password:
        raise HTTPException(status_code=428, detail="Initial setup is required")
    return hashlib.sha256(password.encode("utf-8")).digest()


async def create_panel_session_token() -> str:
    """Create a signed control-panel session token."""
    secret = await _get_panel_session_secret()

    now = int(time.time())
    payload = {
        "sub": "panel",
        "aud": PANEL_SESSION_AUDIENCE,
        "iat": now,
        "exp": now + _get_panel_session_ttl_seconds(),
    }
    return jwt.encode(payload, secret, algorithm=PANEL_SESSION_ALGORITHM)


async def verify_panel_token_value(token: str) -> str:
    """Validate a signed control-panel session token."""

    secret = await _get_panel_session_secret()

    try:
        jwt.decode(
            token,
            secret,
            algorithms=[PANEL_SESSION_ALGORITHM],
            audience=PANEL_SESSION_AUDIENCE,
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired. Please sign in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session token.")

    return token


def _normalize_http_origin(value: str) -> str:
    try:
        parsed = urlsplit(value.strip())
    except ValueError:
        return ""
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return ""
    default_port = 80 if parsed.scheme == "http" else 443
    port = parsed.port or default_port
    suffix = "" if port == default_port else f":{port}"
    return f"{parsed.scheme}://{parsed.hostname.lower()}{suffix}"


def _request_origin(request: Request) -> str:
    scheme = request.url.scheme
    host = request.headers.get("host", "") or request.url.netloc
    if trust_proxy_headers_enabled():
        forwarded_proto = request.headers.get("x-forwarded-proto", "")
        forwarded_host = request.headers.get("x-forwarded-host", "")
        if forwarded_proto:
            scheme = forwarded_proto.split(",", 1)[0].strip()
        if forwarded_host:
            host = forwarded_host.split(",", 1)[0].strip()
    return _normalize_http_origin(f"{scheme}://{host}")


def _verify_cookie_request_origin(request: Request) -> None:
    if request.method.upper() in PANEL_SAFE_METHODS:
        return

    fetch_site = request.headers.get("sec-fetch-site", "").strip().lower()
    if fetch_site == "cross-site":
        raise HTTPException(status_code=403, detail="Cross-site console request rejected.")

    supplied_origin = request.headers.get("origin", "").strip()
    if not supplied_origin:
        return
    if _normalize_http_origin(supplied_origin) != _request_origin(request):
        raise HTTPException(status_code=403, detail="Cross-site console request rejected.")


async def verify_panel_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """Validate a cookie session, with Bearer support for legacy clients."""
    token = request.cookies.get(PANEL_SESSION_COOKIE)
    if token:
        _verify_cookie_request_origin(request)
    elif credentials:
        token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return await verify_panel_token_value(token)
