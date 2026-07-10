"""Provider-specific control-panel configuration and credential routes."""

import io
import json
import zipfile
from datetime import datetime, timezone
from typing import List, Tuple

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

import config
from core.credential_manager import credential_manager
from core.google_ai_studio import (
    GoogleAIStudioError,
    normalize_api_base_url,
    parse_api_key_import_payload,
    validate_api_key,
)
from core.models import ConfigSaveRequest, GoogleAIStudioCredentialRequest
from core.provider_registry import (
    GOOGLE_AI_STUDIO,
    api_key_fingerprint,
)
from core.storage_adapter import get_storage_adapter
from core.utils import verify_panel_token
from log import log

from .utils import get_env_locked_keys


router = APIRouter(tags=["provider-settings"])

MAX_AI_STUDIO_IMPORT_FILE_BYTES = 2 * 1024 * 1024
MAX_AI_STUDIO_IMPORT_UNCOMPRESSED_BYTES = 5 * 1024 * 1024
MAX_AI_STUDIO_IMPORT_ENTRIES = 200

ANTIGRAVITY_CONFIG_KEYS = {
    "antigravity_client_id",
    "antigravity_client_secret",
    "api_url",
    "oauth_url",
    "google_apis_url",
    "resource_manager_url",
    "service_usage_url",
    "antigravity_user_agent",
    "antigravity_payload_user_agent",
    "stream_to_nonstream",
    "switch_credential_enabled",
}

STRING_KEYS = {
    "antigravity_client_id",
    "antigravity_client_secret",
    "api_url",
    "oauth_url",
    "google_apis_url",
    "resource_manager_url",
    "service_usage_url",
    "antigravity_user_agent",
    "antigravity_payload_user_agent",
}

BOOLEAN_KEYS = {
    "stream_to_nonstream",
    "switch_credential_enabled",
}


async def _current_antigravity_config() -> dict:
    client_id, client_secret = await config.get_antigravity_oauth_client_config()
    return {
        "antigravity_client_id": client_id,
        "antigravity_client_secret": client_secret,
        "api_url": await config.get_antigravity_api_url(),
        "oauth_url": await config.get_oauth_proxy_url(),
        "google_apis_url": await config.get_googleapis_proxy_url(),
        "resource_manager_url": await config.get_resource_manager_api_url(),
        "service_usage_url": await config.get_service_usage_api_url(),
        "antigravity_user_agent": await config.get_antigravity_user_agent(),
        "antigravity_payload_user_agent": await config.get_antigravity_payload_user_agent(),
        "stream_to_nonstream": await config.get_antigravity_stream_to_nonstream(),
        "switch_credential_enabled": await config.get_antigravity_switch_credential_enabled(),
    }


@router.get("/api/providers/antigravity/config")
async def get_antigravity_config(token: str = Depends(verify_panel_token)):
    """Return Google Antigravity provider settings for the provider setup UI."""
    try:
        env_locked = get_env_locked_keys() & ANTIGRAVITY_CONFIG_KEYS
        return JSONResponse(
            content={
                "config": await _current_antigravity_config(),
                "env_locked": sorted(env_locked),
            }
        )
    except Exception as e:
        log.error(f"Failed to retrieve Google Antigravity configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/providers/antigravity/config")
async def save_antigravity_config(request: ConfigSaveRequest, token: str = Depends(verify_panel_token)):
    """Save Google Antigravity provider settings from the provider setup UI."""
    try:
        new_config = request.config or {}
        unknown_keys = sorted(set(new_config) - ANTIGRAVITY_CONFIG_KEYS)
        if unknown_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported Google Antigravity setting(s): {', '.join(unknown_keys)}.",
            )

        for key in STRING_KEYS & set(new_config):
            if not isinstance(new_config[key], str):
                raise HTTPException(status_code=400, detail=f"Google Antigravity setting '{key}' must be a string.")

        for key in BOOLEAN_KEYS & set(new_config):
            if not isinstance(new_config[key], bool):
                raise HTTPException(status_code=400, detail=f"Google Antigravity setting '{key}' must be a boolean.")

        env_locked = get_env_locked_keys() & ANTIGRAVITY_CONFIG_KEYS
        storage_adapter = await get_storage_adapter()

        saved_config = {}
        for key, value in new_config.items():
            if key in env_locked:
                continue
            await storage_adapter.set_config(key, value)
            saved_config[key] = value

        await config.reload_config()

        return JSONResponse(
            content={
                "message": "Google Antigravity settings saved.",
                "saved_config": saved_config,
                "env_locked": sorted(env_locked),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to save Google Antigravity configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/providers/antigravity/config/reset")
async def reset_antigravity_config(token: str = Depends(verify_panel_token)):
    """Reset Google Antigravity provider settings to built-in or environment defaults."""
    try:
        env_locked = get_env_locked_keys() & ANTIGRAVITY_CONFIG_KEYS
        storage_adapter = await get_storage_adapter()

        deleted_keys = []
        for key in sorted(ANTIGRAVITY_CONFIG_KEYS - env_locked):
            if await storage_adapter.delete_config(key):
                deleted_keys.append(key)

        await config.reload_config()

        return JSONResponse(
            content={
                "message": "Google Antigravity settings reset to defaults.",
                "config": await _current_antigravity_config(),
                "reset_config": deleted_keys,
                "env_locked": sorted(env_locked),
            }
        )
    except Exception as e:
        log.error(f"Failed to reset Google Antigravity configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


GOOGLE_AI_STUDIO_CONFIG_KEYS = {"google_ai_studio_api_url"}


async def _current_google_ai_studio_config() -> dict:
    return {"google_ai_studio_api_url": await config.get_google_ai_studio_api_url()}


@router.get("/api/providers/google-ai-studio/config")
async def get_google_ai_studio_config(token: str = Depends(verify_panel_token)):
    """Return Google AI Studio provider settings."""
    env_locked = get_env_locked_keys() & GOOGLE_AI_STUDIO_CONFIG_KEYS
    return JSONResponse(
        content={
            "config": await _current_google_ai_studio_config(),
            "env_locked": sorted(env_locked),
        }
    )


@router.post("/api/providers/google-ai-studio/config")
async def save_google_ai_studio_config(
    request: ConfigSaveRequest,
    token: str = Depends(verify_panel_token),
):
    """Save the Google AI Studio upstream endpoint."""
    new_config = request.config or {}
    unknown_keys = sorted(set(new_config) - GOOGLE_AI_STUDIO_CONFIG_KEYS)
    if unknown_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported Google AI Studio setting(s): {', '.join(unknown_keys)}.",
        )

    try:
        api_url = normalize_api_base_url(
            str(new_config.get("google_ai_studio_api_url") or "")
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    env_locked = get_env_locked_keys() & GOOGLE_AI_STUDIO_CONFIG_KEYS
    if "google_ai_studio_api_url" not in env_locked:
        storage_adapter = await get_storage_adapter()
        await storage_adapter.set_config("google_ai_studio_api_url", api_url)
        await config.reload_config()

    return JSONResponse(
        content={
            "message": "Google AI Studio settings saved.",
            "config": await _current_google_ai_studio_config(),
            "env_locked": sorted(env_locked),
        }
    )


@router.post("/api/providers/google-ai-studio/config/reset")
async def reset_google_ai_studio_config(token: str = Depends(verify_panel_token)):
    """Reset the Google AI Studio endpoint to its environment or built-in value."""
    env_locked = get_env_locked_keys() & GOOGLE_AI_STUDIO_CONFIG_KEYS
    if "google_ai_studio_api_url" not in env_locked:
        storage_adapter = await get_storage_adapter()
        await storage_adapter.delete_config("google_ai_studio_api_url")
        await config.reload_config()
    return JSONResponse(
        content={
            "message": "Google AI Studio settings reset to defaults.",
            "config": await _current_google_ai_studio_config(),
            "env_locked": sorted(env_locked),
        }
    )


@router.post("/api/providers/google-ai-studio/credentials")
async def add_google_ai_studio_credential(
    request: GoogleAIStudioCredentialRequest,
    token: str = Depends(verify_panel_token),
):
    """Validate and add one Google AI Studio API key to the provider pool."""
    api_key = request.api_key.strip()

    try:
        validation = await validate_api_key(api_key)
    except GoogleAIStudioError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc

    saved = await _store_google_ai_studio_credential(api_key, validation)
    action = saved["action"]
    message = (
        "Google AI Studio API key revalidated and updated in the provider pool."
        if action == "updated"
        else "Google AI Studio API key added to the provider pool."
    )
    return JSONResponse(
        status_code=200 if action == "updated" else 201,
        content={
            "success": True,
            "credential_saved": True,
            "credential_action": action,
            "filename": saved["filename"],
            "provider": GOOGLE_AI_STUDIO,
            "label": saved["label"],
            "model_count": validation.model_count,
            "message": message,
        },
    )


async def _store_google_ai_studio_credential(api_key: str, validation) -> dict:
    """Store one validated key without exposing it in the result."""
    fingerprint = api_key_fingerprint(api_key)
    credential_label = f"API key ending {api_key[-4:]}"
    credential_data = {
        "provider": GOOGLE_AI_STUDIO,
        "credential_type": "api_key",
        "api_key": api_key,
        "credential_label": credential_label,
        "key_fingerprint": fingerprint,
        "model_ids": validation.model_ids,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    filename = f"google-ai-studio-{fingerprint}.json"
    result = await credential_manager.add_primary_credential(filename, credential_data)
    action = result.get("action", "created")
    return {
        "action": action,
        "filename": result.get("filename", filename),
        "label": credential_label,
        "fingerprint": fingerprint,
    }


def _safe_import_name(value: str, fallback: str = "credential.json") -> str:
    normalized = str(value or "").replace("\\", "/").rstrip("/")
    return normalized.rsplit("/", 1)[-1] or fallback


def _parse_import_document(content: bytes, source_name: str) -> List[Tuple[str, str]]:
    try:
        payload = json.loads(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{source_name} is not valid UTF-8 JSON.") from exc

    api_keys = parse_api_key_import_payload(payload)
    return [
        (f"{source_name} #{index}" if len(api_keys) > 1 else source_name, api_key)
        for index, api_key in enumerate(api_keys, start=1)
    ]


async def _extract_ai_studio_import_file(
    upload: UploadFile,
) -> Tuple[List[Tuple[str, str]], List[dict]]:
    upload_name = _safe_import_name(upload.filename or "credential.json")
    content = await upload.read(MAX_AI_STUDIO_IMPORT_FILE_BYTES + 1)
    if len(content) > MAX_AI_STUDIO_IMPORT_FILE_BYTES:
        raise ValueError(f"{upload_name} exceeds the 2 MB file limit.")

    lower_name = upload_name.lower()
    if lower_name.endswith(".json"):
        return _parse_import_document(content, upload_name), []
    if not lower_name.endswith(".zip"):
        raise ValueError(f"{upload_name} must be a JSON file or ZIP archive.")

    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile as exc:
        raise ValueError(f"{upload_name} is not a valid ZIP archive.") from exc

    candidates: List[Tuple[str, str]] = []
    errors: List[dict] = []
    with archive:
        json_entries = [
            entry
            for entry in archive.infolist()
            if not entry.is_dir() and entry.filename.lower().endswith(".json")
        ]
        if not json_entries:
            raise ValueError(f"{upload_name} does not contain any JSON files.")
        if len(json_entries) > MAX_AI_STUDIO_IMPORT_ENTRIES:
            raise ValueError(
                f"{upload_name} contains more than {MAX_AI_STUDIO_IMPORT_ENTRIES} JSON files."
            )

        total_uncompressed = sum(entry.file_size for entry in json_entries)
        if total_uncompressed > MAX_AI_STUDIO_IMPORT_UNCOMPRESSED_BYTES:
            raise ValueError(f"{upload_name} exceeds the 5 MB uncompressed limit.")

        for entry in json_entries:
            entry_name = _safe_import_name(entry.filename)
            source_name = f"{upload_name} / {entry_name}"
            if entry.flag_bits & 0x1:
                errors.append(
                    {
                        "status": "error",
                        "source_filename": source_name,
                        "message": "Encrypted ZIP entries are not supported.",
                    }
                )
                continue
            try:
                entry_content = archive.read(entry)
                candidates.extend(_parse_import_document(entry_content, source_name))
            except (RuntimeError, ValueError, zipfile.BadZipFile) as exc:
                errors.append(
                    {
                        "status": "error",
                        "source_filename": source_name,
                        "message": str(exc),
                    }
                )
    return candidates, errors


@router.post("/api/providers/google-ai-studio/credentials/import")
async def import_google_ai_studio_credentials(
    files: List[UploadFile] = File(...),
    token: str = Depends(verify_panel_token),
):
    """Validate and import Google AI Studio API keys from JSON files or ZIP archives."""
    if not files:
        raise HTTPException(status_code=400, detail="Select at least one import file.")
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="A single import supports up to 50 files.")

    candidates: List[Tuple[str, str]] = []
    results: List[dict] = []
    for upload in files:
        try:
            extracted, extraction_errors = await _extract_ai_studio_import_file(upload)
            candidates.extend(extracted)
            results.extend(extraction_errors)
        except ValueError as exc:
            results.append(
                {
                    "status": "error",
                    "source_filename": _safe_import_name(upload.filename or "Import file"),
                    "message": str(exc),
                }
            )

    if len(candidates) > MAX_AI_STUDIO_IMPORT_ENTRIES:
        raise HTTPException(
            status_code=400,
            detail=f"A single import supports up to {MAX_AI_STUDIO_IMPORT_ENTRIES} API keys.",
        )

    seen_fingerprints = set()
    created_count = 0
    updated_count = 0
    skipped_count = 0

    for source_name, api_key in candidates:
        fingerprint = api_key_fingerprint(api_key)
        if fingerprint in seen_fingerprints:
            skipped_count += 1
            results.append(
                {
                    "status": "skipped",
                    "source_filename": source_name,
                    "message": "Duplicate API key in this import was skipped.",
                }
            )
            continue
        seen_fingerprints.add(fingerprint)

        try:
            validation = await validate_api_key(api_key)
            saved = await _store_google_ai_studio_credential(api_key, validation)
            action = saved["action"]
            if action == "updated":
                updated_count += 1
            else:
                created_count += 1
            results.append(
                {
                    "status": "success",
                    "action": action,
                    "filename": saved["filename"],
                    "source_filename": source_name,
                    "model_count": validation.model_count,
                    "message": (
                        "Existing API key was revalidated and updated."
                        if action == "updated"
                        else "API key was validated and added to the pool."
                    ),
                }
            )
        except GoogleAIStudioError as exc:
            results.append(
                {
                    "status": "error",
                    "source_filename": source_name,
                    "message": str(exc),
                }
            )
        except Exception as exc:
            log.error(f"Failed to import a Google AI Studio credential: {exc}")
            results.append(
                {
                    "status": "error",
                    "source_filename": source_name,
                    "message": "The API key could not be stored.",
                }
            )

    error_count = sum(1 for item in results if item.get("status") == "error")
    uploaded_count = created_count + updated_count
    message = (
        f"Import complete: added {created_count}, updated {updated_count}, "
        f"skipped {skipped_count}, and failed {error_count}."
    )
    return JSONResponse(
        content={
            "success": True,
            "uploaded_count": uploaded_count,
            "created_count": created_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
            "total_count": len(candidates),
            "results": results,
            "message": message,
        },
    )
