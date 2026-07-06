import hashlib
import os
import secrets
import time
from typing import List, Optional

from config import get_api_password, get_panel_password
from fastapi import Depends, HTTPException, Header, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from log import log

# HTTP Bearer security scheme
security = HTTPBearer()

# ====================== OAuth Configuration ======================

CODE_ASSIST_VERSION = os.getenv("CODE_ASSIST_VERSION", "0.35.2")
CODE_ASSIST_PLATFORM = os.getenv("CODE_ASSIST_PLATFORM", "win32")
CODE_ASSIST_ARCH = os.getenv("CODE_ASSIST_ARCH", "x64")
CODE_ASSIST_SURFACE = os.getenv("CODE_ASSIST_SURFACE", "cloud-shell")

def get_code_assist_user_agent(model: str = "") -> str:
    """Internal implementation detail."""
    if model:
        return f"Code Assist/{CODE_ASSIST_VERSION}/{model} ({CODE_ASSIST_PLATFORM}; {CODE_ASSIST_ARCH}; {CODE_ASSIST_SURFACE})"
    return f"Code Assist/{CODE_ASSIST_VERSION} ({CODE_ASSIST_PLATFORM}; {CODE_ASSIST_ARCH}; {CODE_ASSIST_SURFACE})"


CODE_ASSIST_USER_AGENT = get_code_assist_user_agent()


CLI_VERSION = os.getenv("CLI_VERSION", "1.0.1")
CLI_PLATFORM = os.getenv("CLI_PLATFORM", "windows/amd64")
USER_AGENT = os.getenv("USER_AGENT", f"router/cli/{CLI_VERSION} {CLI_PLATFORM}")


DEFAULT_CODE_ASSIST_CLIENT_ID = "681255809395-oo8ft2oprdrnp9e3aqf6av3hmdib135j.apps.googleusercontent.com"
DEFAULT_ANTIGRAVITY_CLIENT_ID = "1071006060591-tmhssin2h21lcre235vtolojh4g403ep.apps.googleusercontent.com"


def _oauth_client_value(primary_name: str, default: str, fallback_name: str = "") -> str:
    """Return an OAuth client value from env, with an optional non-secret default."""
    return os.getenv(primary_name) or (os.getenv(fallback_name) if fallback_name else "") or default


CODE_ASSIST_CLIENT_ID = _oauth_client_value("CODE_ASSIST_CLIENT_ID", DEFAULT_CODE_ASSIST_CLIENT_ID)
CODE_ASSIST_CLIENT_SECRET = _oauth_client_value("CODE_ASSIST_CLIENT_SECRET", "")
CODE_ASSIST_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Antigravity provider OAuth configuration.
ANTIGRAVITY_CLIENT_ID = _oauth_client_value("ANTIGRAVITY_CLIENT_ID", DEFAULT_ANTIGRAVITY_CLIENT_ID, "CLIENT_ID")
ANTIGRAVITY_CLIENT_SECRET = _oauth_client_value(
    "ANTIGRAVITY_CLIENT_SECRET",
    "",
    "CLIENT_SECRET",
)
CLIENT_ID = ANTIGRAVITY_CLIENT_ID
CLIENT_SECRET = ANTIGRAVITY_CLIENT_SECRET
SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/cclog',
    'https://www.googleapis.com/auth/experimentsandconfigs'
]


TOKEN_URL = "https://oauth2.googleapis.com/token"


CALLBACK_HOST = "localhost"

# Model name lists for different features
BASE_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
    "gemini-3.1-pro-preview",
    "gemini-3.1-flash-lite"
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
    key: Optional[str] = Query(None)
) -> str:
    """Internal implementation detail."""
    password = await get_api_password()
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
                detail="Invalid authentication scheme. Use 'Bearer <token>'",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = authorization[7:]
        auth_method = "Authorization Bearer header"


    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials. Use 'key' URL parameter, 'x-goog-api-key', 'x-anthropic-auth-token', 'anthropic-auth-token', 'x-api-key', 'access_token' header, or 'Authorization: Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )


    from config import API_KEY_PREFIX, get_api_key
    api_key = await get_api_key()

    if not token.startswith(API_KEY_PREFIX):
        log.debug(f"Authentication failed using {auth_method}: invalid API key prefix")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"API key must start with {API_KEY_PREFIX}"
        )

    if not secrets.compare_digest(token, api_key):
        log.debug(f"Authentication failed using {auth_method}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    log.debug(f"Authentication successful using {auth_method}")
    return token



authenticate_bearer = authenticate_flexible
authenticate_gemini_flexible = authenticate_flexible


# ====================== Panel Authentication Functions ======================

PANEL_SESSION_AUDIENCE = "panel"
PANEL_SESSION_ALGORITHM = "HS256"


def _get_panel_session_ttl_seconds() -> int:
    raw_ttl = os.getenv("PANEL_SESSION_TTL_SECONDS", "86400")
    try:
        ttl = int(raw_ttl)
    except ValueError:
        ttl = 86400
    return max(300, min(ttl, 2592000))


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
        raise HTTPException(status_code=401, detail="Invalid session token")

    return token


async def verify_panel_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Validate the control-panel bearer session."""
    return await verify_panel_token_value(credentials.credentials)
