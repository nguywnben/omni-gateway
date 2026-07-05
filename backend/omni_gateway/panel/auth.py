"""Internal implementation detail."""

import base64
import binascii
import json
import os
import re
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from log import log
from omni_gateway.auth import (
    asyncio_complete_auth_flow,
    complete_auth_flow_from_callback_url,
    create_auth_url,
    get_auth_status,
    verify_password,
)
from omni_gateway.models import (
    LoginRequest,
    AuthStartRequest,
    AuthCallbackRequest,
    AuthCallbackUrlRequest,
)
from omni_gateway.utils import verify_panel_token



router = APIRouter(prefix="/ogw/auth", tags=["auth"])

ENV_CREDENTIAL_SOURCE = "environment"
ENV_CREDENTIAL_PATTERN = re.compile(
    r"^(OGW_CREDENTIALS|OGW_CODE_ASSIST_CREDENTIALS)"
    r"(?:_(JSON|B64))?(?:_\d+)?$"
)


def _safe_filename(value: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return name[:120] or "credential"


def _credential_mode_from_env_name(env_name: str) -> str:
    return "code_assist" if env_name.startswith("OGW_CODE_ASSIST_CREDENTIALS") else "omni"


def _decode_env_credential_payload(env_name: str, raw_value: str) -> Any:
    value = raw_value.strip()
    if not value:
        raise ValueError(f"{env_name} is empty")

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        pass

    try:
        padded = value + ("=" * ((4 - len(value) % 4) % 4))
        decoded = base64.b64decode(padded, validate=True).decode("utf-8")
        return json.loads(decoded)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{env_name} must contain JSON or base64-encoded JSON") from exc


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

    raise ValueError("Credential payload must be a JSON object or array")


def _normalize_env_credential(env_name: str, index: int, entry: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(entry, dict):
        raise ValueError("Credential entry must be an object")

    default_mode = _credential_mode_from_env_name(env_name)
    requested_mode = entry.get("mode")
    mode = requested_mode if requested_mode in {"code_assist", "omni"} else default_mode

    credential = entry.get("credential") if isinstance(entry.get("credential"), dict) else entry
    credential_data = dict(credential)

    if not (credential_data.get("token") or credential_data.get("access_token") or credential_data.get("refresh_token")):
        raise ValueError("Credential must contain token, access_token, or refresh_token")

    if credential_data.get("access_token") and not credential_data.get("token"):
        credential_data["token"] = credential_data["access_token"]
    if credential_data.get("token") and not credential_data.get("access_token"):
        credential_data["access_token"] = credential_data["token"]
    if credential_data.get("quota_project_id") and not credential_data.get("project_id"):
        credential_data["project_id"] = credential_data["quota_project_id"]

    credential_data["ogw_source"] = ENV_CREDENTIAL_SOURCE
    credential_data["ogw_env_var"] = env_name
    credential_data["ogw_env_index"] = index

    filename = entry.get("filename") or credential_data.get("filename")
    if not filename:
        project_id = credential_data.get("project_id") or credential_data.get("quota_project_id") or env_name.lower()
        filename = f"env_{mode}_{project_id}_{index}.json"
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
    from omni_gateway.storage_adapter import get_storage_adapter

    storage_adapter = await get_storage_adapter()
    imported: List[Dict[str, str]] = []

    for mode in ("code_assist", "omni"):
        for filename in await storage_adapter.list_credentials(mode=mode):
            credential_data = await storage_adapter.get_credential(filename, mode=mode)
            if credential_data and credential_data.get("ogw_source") == ENV_CREDENTIAL_SOURCE:
                imported.append(
                    {
                        "mode": mode,
                        "filename": filename,
                        "env_var": credential_data.get("ogw_env_var", ""),
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
async def login(request: LoginRequest):
    """Internal implementation detail."""
    try:
        if await verify_password(request.password):
            # Directly use password as token, simplifying auth flow
            return JSONResponse(content={"token": request.password, "message": "Login successful"})
        else:
            raise HTTPException(status_code=401, detail="Incorrect password")
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/start")
async def start_auth(request: AuthStartRequest, token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:

        project_id = request.project_id
        if not project_id:
            log.info("User did not provide a project ID; auto-detection will be used hereafter...")


        user_session = token if token else None
        result = await create_auth_url(
            project_id, user_session, mode=request.mode
        )

        if result["success"]:
            return JSONResponse(
                content={
                    "auth_url": result["auth_url"],
                    "state": result["state"],
                    "auto_project_detection": result.get("auto_project_detection", False),
                    "detected_project_id": result.get("detected_project_id"),
                }
            )
        else:
            error_message = result.get("error", "Unable to start authentication flow")
            status_code = 400 if "Missing OAuth client configuration" in error_message else 500
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
            project_id, user_session, mode=request.mode
        )

        if result["success"]:

            return JSONResponse(
                content={
                    "credentials": result["credentials"],
                    "file_path": result["file_path"],
                    "message": "Authentication successful, credentials saved",
                    "auto_detected_project": result.get("auto_detected_project", False),
                }
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
            raise HTTPException(status_code=400, detail="Please provide a valid callback URL")


        result = await complete_auth_flow_from_callback_url(
            request.callback_url, request.project_id, mode=request.mode
        )

        if result["success"]:

            return JSONResponse(
                content={
                    "credentials": result["credentials"],
                    "file_path": result["file_path"],
                    "message": "Authentication successful from callback URL, credentials saved",
                    "auto_detected_project": result.get("auto_detected_project", False),
                }
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
            raise HTTPException(status_code=400, detail="Project ID cannot be empty")

        status = get_auth_status(project_id)
        return JSONResponse(content=status)

    except Exception as e:
        log.error(f"Failed to check authentication status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/keys")
async def get_api_keys(token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:
        from config import get_api_key
        api_key = await get_api_key()
        return JSONResponse(content={
            "success": True,
            "ogw_api_key": api_key
        })
    except Exception as e:
        log.error(f"Failed to get API key: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/keys/reset")
async def reset_api_key(token: str = Depends(verify_panel_token)):
    """Internal implementation detail."""
    try:
        import secrets
        from omni_gateway.storage_adapter import get_storage_adapter
        from config import _config_cache
        storage_adapter = await get_storage_adapter()

        new_key = f"sk-ogw-{secrets.token_hex(20)}"
        await storage_adapter.set_config("ogw_api_key", new_key)
        _config_cache["ogw_api_key"] = new_key

        return JSONResponse(content={
            "success": True,
            "ogw_api_key": new_key
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
    """Import credentials from supported OGW_* environment variables."""
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
                    "message": "No supported environment credential variables were found",
                }
            )

        from omni_gateway.storage_adapter import get_storage_adapter

        storage_adapter = await get_storage_adapter()
        results = []
        loaded_count = 0

        for item in env_credentials:
            filename = item["filename"]
            mode = item["mode"]
            try:
                success = await storage_adapter.store_credential(filename, item["credential"], mode=mode)
                if success:
                    loaded_count += 1
                    results.append(
                        {
                            "filename": filename,
                            "mode": mode,
                            "env_var": item["credential"].get("ogw_env_var", ""),
                            "status": "success",
                            "message": "Imported successfully",
                        }
                    )
                else:
                    results.append(
                        {
                            "filename": filename,
                            "mode": mode,
                            "status": "error",
                            "message": "Storage adapter rejected the credential",
                        }
                    )
            except Exception as item_error:
                results.append(
                    {
                        "filename": filename,
                        "mode": mode,
                        "status": "error",
                        "message": str(item_error),
                    }
                )

        return JSONResponse(
            content={
                "loaded_count": loaded_count,
                "total_count": len(env_credentials),
                "results": results,
                "message": f"Imported {loaded_count}/{len(env_credentials)} environment credential(s)",
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
        from omni_gateway.storage_adapter import get_storage_adapter

        storage_adapter = await get_storage_adapter()
        imported = await _list_imported_env_credentials()
        deleted_count = 0
        results = []

        for item in imported:
            filename = item["filename"]
            mode = item["mode"]
            try:
                success = await storage_adapter.delete_credential(filename, mode=mode)
                if success:
                    deleted_count += 1
                    results.append({"filename": filename, "mode": mode, "status": "success"})
                else:
                    results.append(
                        {
                            "filename": filename,
                            "mode": mode,
                            "status": "error",
                            "message": "Credential was not deleted",
                        }
                    )
            except Exception as item_error:
                results.append(
                    {
                        "filename": filename,
                        "mode": mode,
                        "status": "error",
                        "message": str(item_error),
                    }
                )

        return JSONResponse(
            content={
                "deleted_count": deleted_count,
                "total_count": len(imported),
                "results": results,
                "message": f"Deleted {deleted_count}/{len(imported)} environment credential(s)",
            }
        )

    except Exception as e:
        log.error(f"Failed to clear environment credentials: {e}")
        raise HTTPException(status_code=500, detail=str(e))
