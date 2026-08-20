"""Gemini CLI management console routes."""

from __future__ import annotations

import io
import json
import zipfile
from typing import List, Tuple

import config
from core.gemini_cli import (
    GeminiCliError,
    complete_gemini_cli_oauth,
    create_gemini_cli_oauth_flow,
    normalize_gemini_cli_api_url,
)
from core.models import ConfigSaveRequest, GeminiCliOAuthCodeRequest
from core.pool_import import restore_gemini_cli_credential
from core.provider_registry import GEMINI_CLI
from core.storage_adapter import get_storage_adapter
from core.utils import verify_panel_token
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from log import log

from ..utils import get_env_locked_keys
from .import_utils import (
    MAX_PROVIDER_IMPORT_ENTRIES,
    MAX_PROVIDER_IMPORT_FILE_BYTES,
    MAX_PROVIDER_IMPORT_UNCOMPRESSED_BYTES,
    _safe_import_name,
)

router = APIRouter(tags=["provider-gemini-cli"])

GEMINI_CLI_CONFIG_KEYS = {
    "gemini_cli_api_url",
    "gemini_cli_oauth_authorize_url",
    "gemini_cli_oauth_token_url",
    "gemini_cli_client_id",
    "gemini_cli_client_secret",
}


async def _current_gemini_cli_config() -> dict:
    client_id, client_secret = await config.get_gemini_cli_oauth_client_config()
    return {
        "gemini_cli_api_url": await config.get_gemini_cli_api_url(),
        "gemini_cli_oauth_authorize_url": await config.get_gemini_cli_oauth_authorize_url(),
        "gemini_cli_oauth_token_url": await config.get_gemini_cli_oauth_token_url(),
        "gemini_cli_client_id": client_id,
        "gemini_cli_client_secret": client_secret,
    }


@router.get("/api/providers/gemini_cli/config")
async def get_gemini_cli_config(token: str = Depends(verify_panel_token)):
    env_locked = get_env_locked_keys() & GEMINI_CLI_CONFIG_KEYS
    return JSONResponse(
        content={
            "config": await _current_gemini_cli_config(),
            "env_locked": sorted(env_locked),
        }
    )


@router.post("/api/providers/gemini_cli/config")
async def save_gemini_cli_config(
    request: ConfigSaveRequest,
    token: str = Depends(verify_panel_token),
):
    new_config = request.config or {}
    unknown_keys = sorted(set(new_config) - GEMINI_CLI_CONFIG_KEYS)
    if unknown_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported Gemini CLI setting(s): {', '.join(unknown_keys)}.",
        )
    current = await _current_gemini_cli_config()
    locked = get_env_locked_keys() & GEMINI_CLI_CONFIG_KEYS
    candidate = {
        key: current[key] if key in locked else new_config.get(key, current[key])
        for key in GEMINI_CLI_CONFIG_KEYS
    }
    try:
        api_url = normalize_gemini_cli_api_url(str(candidate["gemini_cli_api_url"] or ""))
        authorize_url = config.validate_https_url(
            str(candidate["gemini_cli_oauth_authorize_url"] or ""),
            "Gemini CLI authorization endpoint",
        )
        token_url = config.validate_https_url(
            str(candidate["gemini_cli_oauth_token_url"] or ""),
            "Gemini CLI token endpoint",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    client_id = str(candidate.get("gemini_cli_client_id") or "").strip()
    client_secret = str(candidate.get("gemini_cli_client_secret") or "").strip()
    if not client_id:
        raise HTTPException(status_code=400, detail="Gemini CLI OAuth client ID cannot be empty.")

    storage_adapter = await get_storage_adapter()
    updates = {
        "gemini_cli_api_url": api_url,
        "gemini_cli_oauth_authorize_url": authorize_url,
        "gemini_cli_oauth_token_url": token_url,
        "gemini_cli_client_id": client_id,
        "gemini_cli_client_secret": client_secret,
    }
    for key, value in updates.items():
        if key not in locked:
            await storage_adapter.set_config(key, value)
    await config.reload_config()
    log.info("Gemini CLI provider configuration updated.")
    return JSONResponse(
        content={
            "success": True,
            "message": "Gemini CLI configuration saved.",
            "config": await _current_gemini_cli_config(),
            "env_locked": sorted(locked),
        }
    )


@router.post("/api/providers/gemini_cli/config/reset")
async def reset_gemini_cli_config(token: str = Depends(verify_panel_token)):
    locked = get_env_locked_keys() & GEMINI_CLI_CONFIG_KEYS
    storage_adapter = await get_storage_adapter()
    for key in GEMINI_CLI_CONFIG_KEYS:
        if key not in locked:
            await storage_adapter.delete_config(key)
    await config.reload_config()
    log.info("Gemini CLI provider configuration reset to defaults.")
    return JSONResponse(
        content={
            "success": True,
            "message": "Gemini CLI configuration reset to defaults.",
            "config": await _current_gemini_cli_config(),
            "env_locked": sorted(locked),
        }
    )


@router.post("/api/providers/gemini_cli/oauth/start")
async def start_gemini_cli_oauth(token: str = Depends(verify_panel_token)):
    try:
        url, state = await create_gemini_cli_oauth_flow()
        return JSONResponse(
            content={
                "success": True,
                "authorization_url": url,
                "state": state,
                "provider": GEMINI_CLI,
            }
        )
    except GeminiCliError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except Exception as exc:
        log.error(f"Failed to generate Gemini CLI authorization link: {exc}")
        raise HTTPException(status_code=500, detail="Failed to initialize OAuth flow.") from exc


@router.post("/api/providers/gemini_cli/oauth/save")
async def save_gemini_cli_oauth(
    request: GeminiCliOAuthCodeRequest,
    token: str = Depends(verify_panel_token),
):
    try:
        saved = await complete_gemini_cli_oauth(
            code=request.code,
            state=request.state or "",
        )
        return JSONResponse(
            content={
                "success": True,
                "message": "Gemini CLI OAuth credential saved to pool.",
                "credential": saved,
            }
        )
    except GeminiCliError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    except Exception as exc:
        log.error(f"Failed to save Gemini CLI OAuth credential: {exc}")
        raise HTTPException(
            status_code=400, detail="Failed to complete Gemini CLI authorization."
        ) from exc


@router.post("/api/providers/gemini_cli/import")
async def import_gemini_cli_files(
    files: List[UploadFile] = File(...),
    token: str = Depends(verify_panel_token),
):
    if not files:
        raise HTTPException(status_code=400, detail="No files selected for import.")

    candidates: List[Tuple[str, dict]] = []
    results: List[dict] = []

    for file in files:
        filename = str(file.filename or "").strip()
        try:
            content = await file.read()
            if len(content) > MAX_PROVIDER_IMPORT_FILE_BYTES:
                raise ValueError("File exceeds maximum size limit (10 MB).")

            if filename.lower().endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    entries = [e for e in zf.infolist() if not e.is_dir()]
                    if len(entries) > MAX_PROVIDER_IMPORT_ENTRIES:
                        raise ValueError(f"ZIP archive contains too many entries (max {MAX_PROVIDER_IMPORT_ENTRIES}).")
                    total_uncompressed = sum(e.file_size for e in entries)
                    if total_uncompressed > MAX_PROVIDER_IMPORT_UNCOMPRESSED_BYTES:
                        raise ValueError("ZIP uncompressed size exceeds limit (25 MB).")

                    for entry in entries:
                        safe_name = _safe_import_name(entry.filename)
                        if safe_name.lower().endswith(".json"):
                            entry_data = json.loads(zf.read(entry).decode("utf-8"))
                            candidates.append((safe_name, entry_data))
            elif filename.lower().endswith(".json"):
                data = json.loads(content.decode("utf-8"))
                candidates.append((filename, data))
            else:
                raise ValueError("Unsupported file format. Please upload .json or .zip files.")
        except Exception as exc:
            results.append(
                {
                    "status": "error",
                    "source_filename": filename,
                    "provider": GEMINI_CLI,
                    "message": str(exc),
                }
            )

    for source_name, payload in candidates:
        try:
            res = await restore_gemini_cli_credential(
                {
                    "filename": source_name,
                    "payload": payload,
                    "source_filename": source_name,
                }
            )
            results.append(
                {
                    **res,
                    "source_filename": source_name,
                    "provider": GEMINI_CLI,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "status": "error",
                    "source_filename": source_name,
                    "provider": GEMINI_CLI,
                    "message": str(exc),
                }
            )

    imported_count = sum(1 for r in results if r.get("status") == "success")
    error_count = sum(1 for r in results if r.get("status") == "error")

    return JSONResponse(
        content={
            "success": error_count == 0,
            "imported_count": imported_count,
            "error_count": error_count,
            "total_count": len(results),
            "results": results,
            "message": f"Import complete: {imported_count} imported, {error_count} failed.",
        }
    )
