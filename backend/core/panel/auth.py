import os

import config
from core.auth import (
    asyncio_complete_auth_flow,
    complete_auth_flow_from_callback_url,
    create_auth_url,
    get_auth_status,
    get_auth_status_by_state,
    verify_password,
)
from core.models import (
    AuthCallbackRequest,
    AuthCallbackUrlRequest,
    AuthStartRequest,
    LoginRequest,
    SetupRequest,
)
from core.passwords import hash_password
from core.storage_adapter import get_storage_adapter
from core.utils import (
    PANEL_SESSION_COOKIE,
    clear_panel_session_cookie,
    create_panel_session_token,
    set_panel_session_cookie,
    verify_panel_token,
    verify_panel_token_value,
)
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from log import log

from .auth_support import (
    _assert_login_allowed,
    _auth_success_content,
    _clear_login_failures,
    _client_identity,
    _record_login_failure,
)
from .setup_security import get_setup_access_policy, verify_setup_access
from .utils import internal_server_error, validate_mode

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
async def login(payload: LoginRequest, request: Request):
    try:
        if not await config.has_password_configured():
            raise HTTPException(status_code=428, detail="Initial setup is required before login.")

        client_id = _client_identity(request)
        _assert_login_allowed(client_id)

        if await verify_password(payload.password):
            _clear_login_failures(client_id)
            response = JSONResponse(content={"message": "Signed in."})
            set_panel_session_cookie(
                response,
                await create_panel_session_token(),
                request,
            )
            return response

        _record_login_failure(client_id)
        raise HTTPException(status_code=401, detail="Incorrect password.")
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Login failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to sign in because of an internal service error.",
        ) from e


@router.get("/setup/status")
async def setup_status(request: Request):
    """Return whether the control panel still needs first-run setup."""
    try:
        setup_required = not await config.has_password_configured()
        policy = get_setup_access_policy(request)
        authenticated = False
        session_token = request.cookies.get(PANEL_SESSION_COOKIE)
        if session_token and not setup_required:
            try:
                await verify_panel_token_value(session_token)
                authenticated = True
            except HTTPException:
                authenticated = False
        return JSONResponse(
            content={
                "setup_required": setup_required,
                "setup_token_required": setup_required and policy.token_required,
                "authenticated": authenticated,
            }
        )
    except Exception as e:
        log.error(f"Failed to determine setup status: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to determine the initial setup status.",
        ) from e


@router.post("/setup")
async def complete_setup(payload: SetupRequest, request: Request):
    """Create the first control-panel password when no password exists yet."""
    try:
        if await config.has_password_configured():
            raise HTTPException(status_code=409, detail="Initial setup has already been completed.")

        verify_setup_access(request, payload.setup_token)

        password = payload.password.strip()
        confirm_password = (payload.confirm_password or payload.password).strip()

        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")

        if password != confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match.")

        storage_adapter = await get_storage_adapter()
        await storage_adapter.set_config("panel_password", hash_password(password))

        await config.reload_config()

        response = JSONResponse(
            content={
                "message": "Initial setup completed.",
                "setup_required": False,
            },
        )
        set_panel_session_cookie(
            response,
            await create_panel_session_token(),
            request,
        )
        return response
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Initial setup failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Unable to complete initial setup because of an internal service error.",
        ) from e


@router.post("/logout")
async def logout():
    """Expire the browser control-panel session."""
    response = JSONResponse(content={"message": "Signed out."})
    clear_panel_session_cookie(response)
    return response


@router.post("/start")
async def start_auth(request: AuthStartRequest, token: str = Depends(verify_panel_token)):
    try:
        project_id = request.project_id
        if not project_id:
            log.info("No Project ID was provided; auto-detection will be used.")

        user_session = token if token else None
        mode = validate_mode(request.mode)
        result = await create_auth_url(
            project_id,
            user_session,
            mode=mode,
        )

        if result["success"]:
            return JSONResponse(
                content={
                    "auth_url": result["auth_url"],
                    "state": result["state"],
                    "callback_url": result.get("callback_url"),
                    "auto_project_detection": result.get("auto_project_detection", False),
                    "detected_project_id": result.get("detected_project_id"),
                }
            )
        else:
            error_message = result.get("error", "Unable to start authentication flow.")
            status_code = 400 if result.get("error_code") == "missing_oauth_client_config" else 500
            raise HTTPException(status_code=status_code, detail=error_message)

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to start authentication flow: {e}")
        raise internal_server_error() from e


@router.post("/callback")
async def auth_callback(request: AuthCallbackRequest, token: str = Depends(verify_panel_token)):
    try:
        project_id = request.project_id

        user_session = token if token else None

        result = await asyncio_complete_auth_flow(
            project_id, user_session, mode=validate_mode(request.mode)
        )

        if result["success"]:
            return JSONResponse(content=_auth_success_content(result))
        else:
            if result.get("requires_manual_project_id"):
                return JSONResponse(
                    status_code=400,
                    content={"error": result["error"], "requires_manual_project_id": True},
                )
            elif result.get("requires_project_selection"):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": result["error"],
                        "requires_project_selection": True,
                        "available_projects": result["available_projects"],
                    },
                )
            else:
                raise HTTPException(status_code=400, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to process authentication callback: {e}")
        raise internal_server_error() from e


@router.post("/callback-url")
async def auth_callback_url(
    request: AuthCallbackUrlRequest, token: str = Depends(verify_panel_token)
):
    try:
        if not request.callback_url or not request.callback_url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Please provide a valid callback URL.")

        result = await complete_auth_flow_from_callback_url(
            request.callback_url, request.project_id, mode=validate_mode(request.mode)
        )

        if result["success"]:
            return JSONResponse(content=_auth_success_content(result))
        else:
            if result.get("requires_manual_project_id"):
                return JSONResponse(
                    status_code=400,
                    content={"error": result["error"], "requires_manual_project_id": True},
                )
            elif result.get("requires_project_selection"):
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": result["error"],
                        "requires_project_selection": True,
                        "available_projects": result["available_projects"],
                    },
                )
            else:
                raise HTTPException(status_code=400, detail=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to handle authentication from callback URL: {e}")
        raise internal_server_error() from e


@router.get("/status/{project_id}")
async def check_auth_status(project_id: str, token: str = Depends(verify_panel_token)):
    try:
        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID cannot be empty.")

        status = get_auth_status(project_id)
        return JSONResponse(content=status)

    except Exception as e:
        log.error(f"Failed to check authentication status: {e}")
        raise internal_server_error() from e


@router.get("/status")
async def check_auth_flow_status(
    state: str = Query(..., min_length=1),
    token: str = Depends(verify_panel_token),
):
    """Return OAuth callback status for the active browser session without waiting."""
    try:
        return JSONResponse(content=get_auth_status_by_state(state, token))
    except Exception as e:
        log.error(f"Failed to check authentication flow status: {e}")
        raise internal_server_error() from e


@router.get("/keys")
async def get_api_keys(token: str = Depends(verify_panel_token)):
    try:
        from config import get_api_key

        api_key = await get_api_key()
        managed_by_env = bool(os.getenv("API_KEY", "").strip())
        return JSONResponse(
            content={
                "success": True,
                "api_key": api_key,
                "managed_by_env": managed_by_env,
            }
        )
    except Exception as e:
        log.error(f"Failed to get API key: {e}")
        raise internal_server_error() from e


@router.post("/keys/reset")
async def reset_api_key(token: str = Depends(verify_panel_token)):
    try:
        import secrets

        from config import API_KEY_PREFIX, _config_cache
        from core.storage_adapter import get_storage_adapter

        env_key = os.getenv("API_KEY", "").strip()
        if env_key:
            return JSONResponse(
                status_code=409,
                content={
                    "success": False,
                    "api_key": env_key,
                    "managed_by_env": True,
                    "message": "API key is managed by the API_KEY environment variable and cannot be regenerated from the console.",
                },
            )

        storage_adapter = await get_storage_adapter()

        new_key = f"{API_KEY_PREFIX}{secrets.token_hex(20)}"
        await storage_adapter.set_config("api_key", new_key)
        _config_cache["api_key"] = new_key

        return JSONResponse(
            content={
                "success": True,
                "api_key": new_key,
                "managed_by_env": False,
            }
        )
    except Exception as e:
        log.error(f"Failed to reset API key: {e}")
        raise internal_server_error() from e
