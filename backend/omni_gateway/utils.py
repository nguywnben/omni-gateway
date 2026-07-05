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
    """ç”Ÿæˆå¨æ€ User-Agent: Code Assist/{version}/{model} ({platform}; {arch}; {surface})"""
    if model:
        return f"Code Assist/{OGW_CODE_ASSIST_VERSION}/{model} ({OGW_CODE_ASSIST_PLATFORM}; {OGW_CODE_ASSIST_ARCH}; {OGW_CODE_ASSIST_SURFACE})"
    return f"Code Assist/{OGW_CODE_ASSIST_VERSION} ({OGW_CODE_ASSIST_PLATFORM}; {OGW_CODE_ASSIST_ARCH}; {OGW_CODE_ASSIST_SURFACE})"

# é™æ€å¸¸é‡
OGW_CODE_ASSIST_USER_AGENT = get_code_assist_user_agent()

# Omni CLI å®¢æˆ·ç«¯ä»¿çœŸå¸¸é‡
OGW_CLI_VERSION = os.getenv("OGW_CLI_VERSION", "1.0.1")
OGW_CLI_PLATFORM = os.getenv("OGW_CLI_PLATFORM", "windows/amd64")
OGW_USER_AGENT = os.getenv("OGW_USER_AGENT", f"omni-gateway/cli/{OGW_CLI_VERSION} {OGW_CLI_PLATFORM}")

# OAuth Configuration - æ ‡å‡†æ¨¡å¼
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

# ç»Ÿä¸€ç„ Token URLï¼ˆä¸¤ç§æ¨¡å¼ç›¸åŒï¼‰
TOKEN_URL = "https://oauth2.googleapis.com/token"

# å›è°ƒæœå¡å™¨é…ç½®
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
    return model_name.startswith("å‡æµå¼/")


def is_anti_truncation_model(model_name: str) -> bool:
    """Check if model name indicates anti-truncation should be used."""
    return model_name.startswith("æµå¼æ—æˆªæ–­/")


def get_base_model_from_feature_model(model_name: str) -> str:
    """Get base model name from feature model name."""
    # Remove feature prefixes
    for prefix in ["å‡æµå¼/", "æµå¼æ—æˆªæ–­/"]:
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
        # åŸºç¡€æ¨¡å‹
        models.append(base_model)

        # å‡æµå¼æ¨¡å‹ (å‰ç¼€æ ¼å¼)
        models.append(f"å‡æµå¼/{base_model}")

        # æµå¼æ—æˆªæ–­æ¨¡å‹ (ä»…åœ¨æµå¼ä¼ è¾“æ—¶æœ‰æ•ˆï¼Œå‰ç¼€æ ¼å¼)
        models.append(f"æµå¼æ—æˆªæ–­/{base_model}")

        # å®ä¹‰æ€è€ƒåç¼€ï¼ˆæ ¹æ®æ¨¡å‹ç³»åˆ—ä¸åŒï¼‰
        thinking_suffixes = []

        # Gemini 2.5 ç³»åˆ—: ä½¿ç”¨æ€è€ƒé¢„ç®—åç¼€
        if "gemini-2.5" in base_model:
            thinking_suffixes = ["-max", "-high", "-medium", "-low", "-minimal"]
        # Gemini 3 ç³»åˆ—: ä½¿ç”¨æ€è€ƒç­‰çº§åç¼€
        elif "gemini-3" in base_model:
            if "flash" in base_model:
                # 3-flash-preview: æ”¯æŒ high/medium/low/minimal
                thinking_suffixes = ["-high", "-medium", "-low", "-minimal"]
            elif "pro" in base_model:
                # 3-pro-preview: æ”¯æŒ high/low
                thinking_suffixes = ["-low"]

        search_suffix = "-search"

        # 1. å•ç‹¬ç„ thinking åç¼€
        for thinking_suffix in thinking_suffixes:
            models.append(f"{base_model}{thinking_suffix}")
            models.append(f"å‡æµå¼/{base_model}{thinking_suffix}")
            models.append(f"æµå¼æ—æˆªæ–­/{base_model}{thinking_suffix}")

        # 2. å•ç‹¬ç„ search åç¼€
        models.append(f"{base_model}{search_suffix}")
        models.append(f"å‡æµå¼/{base_model}{search_suffix}")
        models.append(f"æµå¼æ—æˆªæ–­/{base_model}{search_suffix}")

        # 3. thinking + search ç»„åˆåç¼€
        for thinking_suffix in thinking_suffixes:
            combined_suffix = f"{thinking_suffix}{search_suffix}"
            models.append(f"{base_model}{combined_suffix}")
            models.append(f"å‡æµå¼/{base_model}{combined_suffix}")
            models.append(f"æµå¼æ—æˆªæ–­/{base_model}{combined_suffix}")

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
    """
    ç»Ÿä¸€ç„çµæ´»è®¤è¯å‡½æ•°ï¼Œæ”¯æŒå¤ç§è®¤è¯æ–¹å¼

    æ­¤å‡½æ•°å¯ä»¥ç›´æ¥ç”¨ä½œ FastAPI ç„ Depends ä¾èµ–

    æ”¯æŒç„è®¤è¯æ–¹å¼:
        - URL å‚æ•°: key
        - HTTP å¤´éƒ¨: Authorization (Bearer token)
        - HTTP å¤´éƒ¨: x-api-key
        - HTTP å¤´éƒ¨: access_token
        - HTTP å¤´éƒ¨: x-goog-api-key
        - HTTP å¤´éƒ¨: x-anthropic-auth-token
        - HTTP å¤´éƒ¨: anthropic-auth-token

    Args:
        request: FastAPI Request å¯¹è±¡
        authorization: Authorization å¤´éƒ¨å€¼ï¼ˆè‡ªå¨æ³¨å…¥ï¼‰
        x_api_key: x-api-key å¤´éƒ¨å€¼ï¼ˆè‡ªå¨æ³¨å…¥ï¼‰
        access_token: access_token å¤´éƒ¨å€¼ï¼ˆè‡ªå¨æ³¨å…¥ï¼‰
        x_goog_api_key: x-goog-api-key å¤´éƒ¨å€¼ï¼ˆè‡ªå¨æ³¨å…¥ï¼‰
        x_anthropic_auth_token: x-anthropic-auth-token å¤´éƒ¨å€¼ï¼ˆè‡ªå¨æ³¨å…¥ï¼‰
        anthropic_auth_token: anthropic-auth-token å¤´éƒ¨å€¼ï¼ˆè‡ªå¨æ³¨å…¥ï¼‰
        key: URL å‚æ•° keyï¼ˆè‡ªå¨æ³¨å…¥ï¼‰

    Returns:
        éªŒè¯é€è¿‡ç„token

    Raises:
        HTTPException: è®¤è¯å¤±è´¥æ—¶æ›å‡ºå¼‚å¸¸

    ä½¿ç”¨ç¤ºä¾‹:
        @router.post("/endpoint")
        async def endpoint(token: str = Depends(authenticate_flexible)):
            # token å·²éªŒè¯é€è¿‡
            pass
    """
    password = await get_api_password()
    token = None
    auth_method = None

    # 1. å°è¯•ä» URL å‚æ•° key è·å–ï¼ˆGoogle å®˜æ–¹æ ‡å‡†æ–¹å¼ï¼‰
    if key:
        token = key
        auth_method = "URL parameter 'key'"

    # 2. å°è¯•ä» x-goog-api-key å¤´éƒ¨è·å–ï¼ˆGoogle API æ ‡å‡†æ–¹å¼ï¼‰
    elif x_goog_api_key:
        token = x_goog_api_key
        auth_method = "x-goog-api-key header"

    # 3. å°è¯•ä» x-anthropic-auth-token å¤´éƒ¨è·å–ï¼ˆAnthropic æ ‡å‡†æ–¹å¼ï¼‰
    elif x_anthropic_auth_token:
        token = x_anthropic_auth_token
        auth_method = "x-anthropic-auth-token header"

    # 4. å°è¯•ä» anthropic-auth-token å¤´éƒ¨è·å–ï¼ˆAnthropic æ›¿ä»£æ–¹å¼ï¼‰
    elif anthropic_auth_token:
        token = anthropic_auth_token
        auth_method = "anthropic-auth-token header"

    # 5. å°è¯•ä» x-api-key å¤´éƒ¨è·å–
    elif x_api_key:
        token = x_api_key
        auth_method = "x-api-key header"

    # 6. å°è¯•ä» access_token å¤´éƒ¨è·å–
    elif access_token:
        token = access_token
        auth_method = "access_token header"

    # 7. å°è¯•ä» Authorization å¤´éƒ¨è·å–
    elif authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme. Use 'Bearer <token>'",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token = authorization[7:]  # ç§»é™¤ "Bearer " å‰ç¼€
        auth_method = "Authorization Bearer header"

    # æ£€æŸ¥æ˜¯å¦æä¾›äº†ä»»ä½•è®¤è¯å‡­æ®
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials. Use 'key' URL parameter, 'x-goog-api-key', 'x-anthropic-auth-token', 'anthropic-auth-token', 'x-api-key', 'access_token' header, or 'Authorization: Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # éªŒè¯ token
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


# ä¸ºäº†ä¿æŒå‘åå…¼å®¹ï¼Œä¿ç•™æ—§å‡½æ•°åä½œä¸ºåˆ«å
authenticate_bearer = authenticate_flexible
authenticate_gemini_flexible = authenticate_flexible


# ====================== Panel Authentication Functions ======================

async def verify_panel_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    ç®€åŒ–ç„æ§åˆ¶é¢æ¿å¯†ç éªŒè¯å‡½æ•°

    ç›´æ¥éªŒè¯Bearer tokenæ˜¯å¦ç­‰äºæ§åˆ¶é¢æ¿å¯†ç 

    Args:
        credentials: HTTPAuthorizationCredentials è‡ªå¨æ³¨å…¥

    Returns:
        éªŒè¯é€è¿‡ç„token

    Raises:
        HTTPException: Incorrect passwordæ—¶æ›å‡º401å¼‚å¸¸
    """

    password = await get_panel_password()
    if credentials.credentials != password:
        raise HTTPException(status_code=401, detail="Incorrect password")
    return credentials.credentials
