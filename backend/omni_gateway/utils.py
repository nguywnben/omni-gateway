from typing import List, Optional

import os

from config import get_api_password, get_panel_password
from fastapi import Depends, HTTPException, Header, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from log import log

# HTTP Bearer security scheme
security = HTTPBearer()

# ====================== OAuth Configuration ======================

OGW_CODE_ASSIST_VERSION = os.getenv("OGW_CODE_ASSIST_VERSION", "0.35.2")
OGW_CODE_ASSIST_PLATFORM = os.getenv("OGW_CODE_ASSIST_PLATFORM", "win32")
OGW_CODE_ASSIST_ARCH = os.getenv("OGW_CODE_ASSIST_ARCH", "x64")
OGW_CODE_ASSIST_SURFACE = os.getenv("OGW_CODE_ASSIST_SURFACE", "cloud-shell")

def get_code_assist_user_agent(model: str = "") -> str:
    """Internal implementation detail."""
    if model:
        return f"Code Assist/{OGW_CODE_ASSIST_VERSION}/{model} ({OGW_CODE_ASSIST_PLATFORM}; {OGW_CODE_ASSIST_ARCH}; {OGW_CODE_ASSIST_SURFACE})"
    return f"Code Assist/{OGW_CODE_ASSIST_VERSION} ({OGW_CODE_ASSIST_PLATFORM}; {OGW_CODE_ASSIST_ARCH}; {OGW_CODE_ASSIST_SURFACE})"


OGW_CODE_ASSIST_USER_AGENT = get_code_assist_user_agent()


OGW_CLI_VERSION = os.getenv("OGW_CLI_VERSION", "1.0.1")
OGW_CLI_PLATFORM = os.getenv("OGW_CLI_PLATFORM", "windows/amd64")
OGW_USER_AGENT = os.getenv("OGW_USER_AGENT", f"omni-gateway/cli/{OGW_CLI_VERSION} {OGW_CLI_PLATFORM}")


OGW_CODE_ASSIST_CLIENT_ID = os.getenv(
    "OGW_CODE_ASSIST_CLIENT_ID",
    "",
)
OGW_CODE_ASSIST_CLIENT_SECRET = os.getenv("OGW_CODE_ASSIST_CLIENT_SECRET", "")
OGW_CODE_ASSIST_SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Omni OAuth Configuration
OGW_CLIENT_ID = os.getenv("OGW_CLIENT_ID", "")
OGW_CLIENT_SECRET = os.getenv("OGW_CLIENT_SECRET", "")
OGW_SCOPES = [
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


    from config import get_api_key
    api_key = await get_api_key()

    if token != api_key:
        log.debug(f"Authentication failed using {auth_method}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect password"
        )

    log.debug(f"Authentication successful using {auth_method}")
    return token



authenticate_bearer = authenticate_flexible
authenticate_gemini_flexible = authenticate_flexible


# ====================== Panel Authentication Functions ======================

async def verify_panel_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Internal implementation detail."""

    password = await get_panel_password()
    if not password:
        raise HTTPException(status_code=428, detail="Initial setup is required")
    if credentials.credentials != password:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return credentials.credentials
