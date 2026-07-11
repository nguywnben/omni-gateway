"""Internal implementation detail."""

import base64
import binascii
import json
import os
import re
import time
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import JSONResponse

import config
from log import log
from core.auth import (
    asyncio_complete_auth_flow,
    complete_auth_flow_from_callback_url,
    create_auth_url,
    get_auth_status_by_state,
    get_auth_status,
    verify_password,
)
from core.models import (
    LoginRequest,
    SetupRequest,
    AuthStartRequest,
    AuthCallbackRequest,
    AuthCallbackUrlRequest,
)
from core.credential_pool import upsert_credential_by_email
from core.passwords import hash_password
from core.storage_adapter import get_storage_adapter
from core.utils import (
    clear_panel_session_cookie,
    create_panel_session_token,
    set_panel_session_cookie,
    verify_panel_token,
)
from .utils import public_mode_name, validate_mode



router = APIRouter(prefix="/api/auth", tags=["auth"])

ENV_CREDENTIAL_SOURCE = "environment"
ENV_CREDENTIAL_PATTERN = re.compile(
    r"^(CREDENTIALS|CODE_ASSIST_CREDENTIALS)"
    r"(?:_(JSON|B64))?(?:_\d+)?$"
)


def _env_int(name: str, default: int, minimum: int, maximum: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        value = default
    return max(minimum, min(value, maximum))


LOGIN_WINDOW_SECONDS = _env_int("PANEL_LOGIN_WINDOW_SECONDS", 300, 30, 3600)
LOGIN_MAX_ATTEMPTS = _env_int("PANEL_LOGIN_MAX_ATTEMPTS", 10, 3, 100)
_login_failures: Dict[str, List[float]] = {}


def _client_identity(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def _recent_failures(client_id: str) -> List[float]:
    now = time.time()
    cutoff = now - LOGIN_WINDOW_SECONDS
    failures = [ts for ts in _login_failures.get(client_id, []) if ts >= cutoff]
    _login_failures[client_id] = failures
    return failures


def _assert_login_allowed(client_id: str) -> None:
    if len(_recent_failures(client_id)) >= LOGIN_MAX_ATTEMPTS:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Please wait before trying again.",
        )


def _record_login_failure(client_id: str) -> None:
    failures = _recent_failures(client_id)
    failures.append(time.time())
    _login_failures[client_id] = failures


def _clear_login_failures(client_id: str) -> None:
    _login_failures.pop(client_id, None)


def _safe_filename(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return name[:120] or "credential"


def _credential_mode_from_env_name(env_name: str) -> str:
    return "code_assist" if env_name.startswith("CODE_ASSIST_CREDENTIALS") else "provider"


def _credential_result_message(result: Dict[str, Any]) -> str:
    action = result.get("credential_action")
    if action == "replaced":
        return "Authentication completed. The existing credential was renewed with a later expiry."
    if action == "skipped":
        return "Authentication completed, but the credential was not added because the pool already has the same email with an equal or later expiry."
    return "Authentication completed. Credential saved."


def _auth_success_content(result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "credentials": result["credentials"],
        "file_path": result["file_path"],
        "message": _credential_result_message(result),
        "auto_detected_project": result.get("auto_detected_project", False),
        "credential_saved": result.get("credential_saved", True),
        "credential_action": result.get("credential_action", "created"),
        "credential_message": result.get("credential_message"),
        "email": result.get("email"),
        "existing_expiry": result.get("existing_expiry"),
        "incoming_expiry": result.get("incoming_expiry"),
        "deleted_duplicates": result.get("deleted_duplicates", []),
    }


def _decode_env_credential_payload(env_name: str, raw_value: str) -> Any:
    value = raw_value.strip()
    if not value:
        raise ValueError(f"{env_name} is empty.")

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        pass

    try:
        padded = value + ("=" * ((4 - len(value) % 4) % 4))
        decoded = base64.b64decode(padded, validate=True).decode("utf-8")
        return json.loads(decoded)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{env_name} must contain JSON or base64-encoded JSON.") from exc


def _extract_credential_entries(payload: Any) -> List[Dict[str, Any]]:
    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        credentials = payload.get("credentials")
        if isinstance(credentials, list):
            entries = []
            for item in credentials:
                if isinstance(item, dict) and isinstance(item.get("credential"), dict):
                    entry = dict(item)
                    entry.setdefault("mode", payload.get("mode"))
                    entries.append(entry)
                else:
                    entries.append(
                        {
                            "mode": item.get("mode", payload.get("mode")) if isinstance(item, dict) else payload.get("mode"),
                            "filename": item.get("filename") if isinstance(item, dict) else None,
                            "credential": item,
                        }
                    )
            return entries
        if isinstance(credentials, dict):
            return [{"mode": payload.get("mode"), "filename": payload.get("filename"), "credential": credentials}]
        if isinstance(payload.get("credential"), dict):
            return [payload]
        return [payload]

    raise ValueError("Credential payload must be a JSON object or array.")


def _normalize_env_credential(env_name: str, index: int, entry: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError("Credential entry must be an object.")

    default_mode = _credential_mode_from_env_name(env_name)
    requested_mode = entry.get("mode")
    mode = validate_mode(requested_mode or default_mode)

    credential = entry.get("credential") if isinstance(entry.get("credential"), dict) else entry
    credential_data = dict(credential)

    if not (credential_data.get("token") or credential_data.get("access_token") or credential_data.get("refresh_token")):
        raise ValueError("Credential must contain token, access_token, or refresh_token.")

    if credential_data.get("access_token") and not credential_data.get("token"):
        credential_data["token"] = credential_data["access_token"]
    if credential_data.get("token") and not credential_data.get("access_token"):
        credential_data["access_token"] = credential_data["token"]
    if credential_data.get("quota_project_id") and not credential_data.get("project_id"):
        credential_data["project_id"] = credential_data["quota_project_id"]

    credential_data["source"] = ENV_CREDENTIAL_SOURCE
    credential_data["env_var"] = env_name
    credential_data["env_index"] = index

    filename = entry.get("filename") or credential_data.get("filename")
    if not filename:
        project_id = credential_data.get("project_id") or credential_data.get("quota_project_id") or env_name.lower()
        filename = f"env_{public_mode_name(mode)}_{project_id}_{index}.json"
    filename = _safe_filename(os.path.basename(str(filename)))
    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    credential_data.pop("filename", None)

    return {"mode": mode, "filename": filename, "credential": credential_data}


def _collect_env_credentials() -> List[Dict[str, Any]]:
    collected: List[Dict[str, Any]] = []
    for env_name, raw_value in sorted(os.environ.items()):
        if not ENV_CREDENTIAL_PATTERN.match(env_name):
            continue

        payload = _decode_env_credential_payload(env_name, raw_value)
        entries = _extract_credential_entries(payload)
        for index, entry in enumerate(entries, start=1):
            collected.append(_normalize_env_credential(env_name, index, entry))

    return collected


async def _list_imported_env_credentials() -> List[Dict[str, str]]:
    from core.storage_adapter import get_storage_adapter

    storage_adapter = await get_storage_adapter()
    imported: List[Dict[str, str]] = []

    for mode in ("code_assist", "primary"):
        for filename in await storage_adapter.list_credentials(mode=mode):
            credential_data = await storage_adapter.get_credential(filename, mode=mode)
            if credential_data and credential_data.get("source") == ENV_CREDENTIAL_SOURCE:
                imported.append(
                    {
                        "mode": public_mode_name(mode),
                        "filename": filename,
                        "env_var": credential_data.get("env_var", ""),
                    }
                )

    return imported


def _build_env_status() -> Dict[str, Any]:
    available_env_vars: Dict[str, Any] = {}
    for env_name, raw_value in sorted(os.environ.items()):
        if not ENV_CREDENTIAL_PATTERN.match(env_name):
            continue

        try:
            payload = _decode_env_credential_payload(env_name, raw_value)
            entries = _extract_credential_entries(payload)
            available_env_vars[env_name] = {
                "mode": _credential_mode_from_env_name(env_name),
                "credential_count": len(entries),
                "valid": True,
            }
        except Exception as exc:
            available_env_vars[env_name] = {
                "mode": _credential_mode_from_env_name(env_name),
                "credential_count": 0,
                "valid": False,
                "error": str(exc),
            }

    return available_env_vars


@router.post("/login")
async def login(payload: LoginRequest, request: Request):
    """Internal implementation detail."""
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/setup/status")
async def setup_status():
    """Return whether the control panel still needs first-run setup."""
    try:
        return JSONResponse(content={"setup_required": not await config.has_password_configured()})
    except Exception as e:
        log.error(f"Failed to determine setup status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/setup")
async def complete_setup(payload: SetupRequest, request: Request):
    """Create the first control-panel password when no password exists yet."""
    try:
        if await config.has_password_configured():
            raise HTTPException(status_code=409, detail="Initial setup has already been completed.")

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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout")
async def logout():
    """Expire the browser control-panel session."""
    response = JSONResponse(content={"message": "Signed out."})
    clear_panel_session_cookie(response)
    return response


@router.post("/start")
async def start_auth(request: AuthStartRequest, token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/callback")
async def auth_callback(request: AuthCallbackRequest, token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:

        project_id = request.project_id


        user_session = token if token else None

        result = await asyncio_complete_auth_flow(
            project_id, user_session, mode=validate_mode(request.mode)
        )

        if result["success"]:

            return JSONResponse(
                content=_auth_success_content(result)
            )
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
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/callback-url")
async def auth_callback_url(request: AuthCallbackUrlRequest, token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:

        if not request.callback_url or not request.callback_url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Please provide a valid callback URL.")


        result = await complete_auth_flow_from_callback_url(
            request.callback_url, request.project_id, mode=validate_mode(request.mode)
        )

        if result["success"]:

            return JSONResponse(
                content=_auth_success_content(result)
            )
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{project_id}")
async def check_auth_status(project_id: str, token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:
        if not project_id:
            raise HTTPException(status_code=400, detail="Project ID cannot be empty.")

        status = get_auth_status(project_id)
        return JSONResponse(content=status)

    except Exception as e:
        log.error(f"Failed to check authentication status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys")
async def get_api_keys(token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:
        from config import get_api_key
        api_key = await get_api_key()
        managed_by_env = bool(os.getenv("API_KEY", "").strip())
        return JSONResponse(content={
            "success": True,
            "api_key": api_key,
            "managed_by_env": managed_by_env,
        })
    except Exception as e:
        log.error(f"Failed to get API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keys/reset")
async def reset_api_key(token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:
        import secrets
        from core.storage_adapter import get_storage_adapter
        from config import API_KEY_PREFIX, _config_cache

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

        return JSONResponse(content={
            "success": True,
            "api_key": new_key,
            "managed_by_env": False,
        })
    except Exception as e:
        log.error(f"Failed to reset API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/env-creds-status")
async def get_env_credentials_status(token: str = Depends(verify_panel_token)):
    """Return available environment credential variables and imported env credentials."""
    try:
        imported = await _list_imported_env_credentials()
        return JSONResponse(
            content={
                "available_env_vars": _build_env_status(),
                "auto_load_enabled": False,
                "existing_env_files_count": len(imported),
                "existing_env_files": [f"{item['mode']}:{item['filename']}" for item in imported],
                "existing_env_credentials": imported,
            }
        )
    except Exception as e:
        log.error(f"Failed to inspect environment credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load-env-creds")
async def load_env_credentials(token: str = Depends(verify_panel_token)):
    """Import credentials from supported * environment variables."""
    try:
        try:
            env_credentials = _collect_env_credentials()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        if not env_credentials:
            return JSONResponse(
                content={
                    "loaded_count": 0,
                    "total_count": 0,
                    "results": [],
                    "message": "No supported environment credential variables were found.",
                }
            )

        from core.storage_adapter import get_storage_adapter

        results = []
        loaded_count = 0
        skipped_count = 0

        for item in env_credentials:
            filename = item["filename"]
            mode = item["mode"]
            try:
                write_result = await upsert_credential_by_email(filename, item["credential"], mode=mode)
                if write_result.get("stored"):
                    loaded_count += 1
                    results.append(
                        {
                            "filename": write_result.get("filename", filename),
                            "mode": public_mode_name(mode),
                            "env_var": item["credential"].get("env_var", ""),
                            "status": "success",
                            "action": write_result.get("action"),
                            "message": write_result.get("message") or "Imported.",
                        }
                    )
                else:
                    skipped_count += 1
                    results.append(
                        {
                            "filename": write_result.get("filename", filename),
                            "mode": public_mode_name(mode),
                            "env_var": item["credential"].get("env_var", ""),
                            "status": "skipped",
                            "action": write_result.get("action"),
                            "message": write_result.get("message") or "Import skipped.",
                        }
                    )
            except Exception as item_error:
                results.append(
                    {
                        "filename": filename,
                        "mode": public_mode_name(mode),
                        "status": "error",
                        "message": str(item_error),
                    }
                )

        return JSONResponse(
            content={
                "loaded_count": loaded_count,
                "skipped_count": skipped_count,
                "total_count": len(env_credentials),
                "results": results,
                "message": f"Imported {loaded_count}/{len(env_credentials)} environment credentials; skipped {skipped_count} duplicates.",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to import environment credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/env-creds")
async def clear_env_credentials(token: str = Depends(verify_panel_token)):
    """Delete credentials that were imported from environment variables."""
    try:
        from core.storage_adapter import get_storage_adapter

        storage_adapter = await get_storage_adapter()
        imported = await _list_imported_env_credentials()
        deleted_count = 0
        results = []

        for item in imported:
            filename = item["filename"]
            mode = validate_mode(item["mode"])
            try:
                success = await storage_adapter.delete_credential(filename, mode=mode)
                if success:
                    deleted_count += 1
                    results.append({"filename": filename, "mode": public_mode_name(mode), "status": "success"})
                else:
                    results.append(
                        {
                            "filename": filename,
                            "mode": public_mode_name(mode),
                            "status": "error",
                            "message": "Credential was not deleted.",
                        }
                    )
            except Exception as item_error:
                results.append(
                    {
                        "filename": filename,
                        "mode": public_mode_name(mode),
                        "status": "error",
                        "message": str(item_error),
                    }
                )

        return JSONResponse(
            content={
                "deleted_count": deleted_count,
                "total_count": len(imported),
                "results": results,
                "message": f"Deleted {deleted_count}/{len(imported)} environment credentials.",
            }
        )

    except Exception as e:
        log.error(f"Failed to clear environment credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))
