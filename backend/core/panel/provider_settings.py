"""Provider-specific control-panel configuration and credential routes."""

import io
import json
import zipfile
from typing import Any, Dict, List, Tuple

import config
from core.google_ai_studio import (
    GoogleAIStudioError,
    normalize_api_base_url,
    parse_api_key_import_payload,
    validate_api_key,
)
from core.models import (
    ConfigSaveRequest,
    GoogleAIStudioCredentialRequest,
    XaiCredentialRequest,
    XaiOAuthCodeRequest,
)
from core.pool_import import (
    PoolImportError,
    classify_pool_credential,
    restore_xai_credential,
)
from core.provider_registry import (
    GOOGLE_AI_STUDIO,
    XAI,
    api_key_fingerprint,
    list_provider_capabilities,
)
from core.provider_store import (
    store_google_ai_studio_credential,
    store_xai_api_key_credential,
)
from core.storage_adapter import get_storage_adapter
from core.utils import verify_panel_token
from core.xai import (
    XaiError,
    complete_xai_oauth,
    create_xai_oauth_url,
    normalize_xai_api_url,
    normalize_xai_issuer,
    validate_xai_api_key,
)
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from log import log

from .utils import get_env_locked_keys, internal_server_error

router = APIRouter(tags=["provider-settings"])

MAX_PROVIDER_IMPORT_FILE_BYTES = 2 * 1024 * 1024
MAX_PROVIDER_IMPORT_UNCOMPRESSED_BYTES = 5 * 1024 * 1024
MAX_PROVIDER_IMPORT_ENTRIES = 200

ANTIGRAVITY_CONFIG_KEYS = {
    "antigravity_client_id",
    "antigravity_client_secret",
    "antigravity_api_url",
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
    "antigravity_api_url",
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


@router.get("/api/providers")
async def get_provider_catalog(token: str = Depends(verify_panel_token)):
    """Return provider capabilities without exposing stored credentials."""
    return JSONResponse(content={"providers": list_provider_capabilities()})


async def _current_antigravity_config() -> dict:
    client_id, client_secret = await config.get_antigravity_oauth_client_config()
    return {
        "antigravity_client_id": client_id,
        "antigravity_client_secret": client_secret,
        "antigravity_api_url": await config.get_antigravity_api_url(),
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
        raise internal_server_error() from e


@router.post("/api/providers/antigravity/config")
async def save_antigravity_config(
    request: ConfigSaveRequest, token: str = Depends(verify_panel_token)
):
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
                raise HTTPException(
                    status_code=400, detail=f"Google Antigravity setting '{key}' must be a string."
                )

        for key in BOOLEAN_KEYS & set(new_config):
            if not isinstance(new_config[key], bool):
                raise HTTPException(
                    status_code=400, detail=f"Google Antigravity setting '{key}' must be a boolean."
                )

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
        raise internal_server_error() from e


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
        raise internal_server_error() from e


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
        api_url = normalize_api_base_url(str(new_config.get("google_ai_studio_api_url") or ""))
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


XAI_CONFIG_KEYS = {"xai_api_url", "xai_oauth_issuer", "xai_client_id", "xai_user_agent"}
XAI_CONFIG_SCOPES = {
    "oauth": {"xai_oauth_issuer", "xai_client_id"},
    "api": {"xai_api_url", "xai_user_agent"},
}


async def _current_xai_config() -> dict:
    return {
        "xai_api_url": await config.get_xai_api_url(),
        "xai_oauth_issuer": await config.get_xai_oauth_issuer(),
        "xai_client_id": await config.get_xai_client_id(),
        "xai_user_agent": await config.get_xai_user_agent(),
    }


@router.get("/api/providers/xai/config")
async def get_xai_config(token: str = Depends(verify_panel_token)):
    env_locked = get_env_locked_keys() & XAI_CONFIG_KEYS
    return JSONResponse(
        content={"config": await _current_xai_config(), "env_locked": sorted(env_locked)}
    )


@router.post("/api/providers/xai/config")
async def save_xai_config(
    request: ConfigSaveRequest,
    token: str = Depends(verify_panel_token),
):
    new_config = request.config or {}
    unknown_keys = sorted(set(new_config) - XAI_CONFIG_KEYS)
    if unknown_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported xAI setting(s): {', '.join(unknown_keys)}.",
        )
    env_locked = get_env_locked_keys() & XAI_CONFIG_KEYS
    current_config = await _current_xai_config()
    candidate_config = {
        key: current_config[key] if key in env_locked else new_config.get(key, current_config[key])
        for key in XAI_CONFIG_KEYS
    }
    try:
        normalized = {
            "xai_api_url": normalize_xai_api_url(str(candidate_config["xai_api_url"] or "")),
            "xai_oauth_issuer": normalize_xai_issuer(
                str(candidate_config["xai_oauth_issuer"] or "")
            ),
            "xai_client_id": str(candidate_config["xai_client_id"] or "").strip(),
            "xai_user_agent": str(candidate_config["xai_user_agent"] or "").strip(),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not normalized["xai_client_id"] or not normalized["xai_user_agent"]:
        raise HTTPException(
            status_code=400,
            detail="Grok OAuth client ID and xAI HTTP User-Agent cannot be empty.",
        )
    storage_adapter = await get_storage_adapter()
    for key, value in normalized.items():
        if key not in env_locked and key in new_config:
            await storage_adapter.set_config(key, value)
    await config.reload_config()
    return JSONResponse(
        content={
            "message": "xAI settings saved.",
            "config": await _current_xai_config(),
            "env_locked": sorted(env_locked),
        }
    )


@router.post("/api/providers/xai/config/reset")
async def reset_xai_config(
    scope: str = "",
    token: str = Depends(verify_panel_token),
):
    normalized_scope = str(scope or "").strip().lower()
    if normalized_scope and normalized_scope not in XAI_CONFIG_SCOPES:
        raise HTTPException(
            status_code=400,
            detail="xAI setting scope must be 'oauth' or 'api'.",
        )

    env_locked = get_env_locked_keys() & XAI_CONFIG_KEYS
    storage_adapter = await get_storage_adapter()
    reset_keys = XAI_CONFIG_SCOPES.get(normalized_scope, XAI_CONFIG_KEYS)
    for key in reset_keys - env_locked:
        await storage_adapter.delete_config(key)
    await config.reload_config()
    scope_label = {
        "oauth": "Grok settings",
        "api": "xAI transport settings",
    }.get(normalized_scope, "xAI settings")
    return JSONResponse(
        content={
            "message": f"{scope_label} reset to defaults.",
            "config": await _current_xai_config(),
            "env_locked": sorted(env_locked),
        }
    )


@router.post("/api/providers/xai/credentials")
async def add_xai_api_key_credential(
    request: XaiCredentialRequest,
    token: str = Depends(verify_panel_token),
):
    try:
        validation = await validate_xai_api_key(request.api_key)
        saved = await store_xai_api_key_credential(request.api_key, validation)
    except XaiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    action = saved["action"]
    return JSONResponse(
        status_code=200 if action == "updated" else 201,
        content={
            "success": True,
            "credential_saved": True,
            "credential_action": action,
            "filename": saved["filename"],
            "provider": XAI,
            "label": saved["label"],
            "model_count": validation.model_count,
            "message": (
                "xAI Console API key revalidated and updated in the provider pool."
                if action == "updated"
                else "xAI Console API key added to the provider pool."
            ),
        },
    )


@router.post("/api/providers/xai/oauth/start")
async def start_xai_oauth(token: str = Depends(verify_panel_token)):
    try:
        result = await create_xai_oauth_url()
        return JSONResponse(content={"success": True, **result})
    except XaiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc


@router.post("/api/providers/xai/oauth/complete")
async def save_xai_oauth_credential(
    request: XaiOAuthCodeRequest,
    token: str = Depends(verify_panel_token),
):
    try:
        result = await complete_xai_oauth(request.code, request.state)
    except XaiError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    return JSONResponse(
        status_code=200 if result["action"] == "updated" else 201,
        content={
            "success": True,
            "credential_saved": True,
            "credential_action": result["action"],
            "provider": XAI,
            **result,
            "message": (
                "Grok OAuth credential renewed in the provider pool."
                if result["action"] == "updated"
                else "Grok OAuth credential added to the provider pool."
            ),
        },
    )


async def _store_google_ai_studio_credential(api_key: str, validation) -> dict:
    """Store one validated key without exposing it in the result."""
    return await store_google_ai_studio_credential(api_key, validation)


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
    content = await upload.read(MAX_PROVIDER_IMPORT_FILE_BYTES + 1)
    if len(content) > MAX_PROVIDER_IMPORT_FILE_BYTES:
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
        if len(json_entries) > MAX_PROVIDER_IMPORT_ENTRIES:
            raise ValueError(
                f"{upload_name} contains more than {MAX_PROVIDER_IMPORT_ENTRIES} JSON files."
            )

        total_uncompressed = sum(entry.file_size for entry in json_entries)
        if total_uncompressed > MAX_PROVIDER_IMPORT_UNCOMPRESSED_BYTES:
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

    if len(candidates) > MAX_PROVIDER_IMPORT_ENTRIES:
        raise HTTPException(
            status_code=400,
            detail=f"A single import supports up to {MAX_PROVIDER_IMPORT_ENTRIES} API keys.",
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
        f"Import completed. Results: {created_count} added, {updated_count} updated, "
        f"{skipped_count} skipped, and {error_count} failed."
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


def _parse_xai_import_document(content: bytes, source_name: str) -> Dict[str, Any]:
    try:
        payload = json.loads(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{source_name} is not valid UTF-8 JSON.") from exc

    try:
        provider_id = classify_pool_credential(payload)
    except PoolImportError as exc:
        raise ValueError(f"{source_name}: {exc}") from exc
    if provider_id != XAI:
        raise ValueError(f"{source_name} does not contain a Grok or xAI Console credential.")

    return {
        "source_filename": source_name,
        "filename": _safe_import_name(source_name),
        "provider": XAI,
        "payload": payload,
    }


async def _extract_xai_import_file(
    upload: UploadFile,
) -> Tuple[List[Dict[str, Any]], List[dict]]:
    upload_name = _safe_import_name(upload.filename or "credential.json")
    content = await upload.read(MAX_PROVIDER_IMPORT_FILE_BYTES + 1)
    if len(content) > MAX_PROVIDER_IMPORT_FILE_BYTES:
        raise ValueError(f"{upload_name} exceeds the 2 MB file limit.")

    lower_name = upload_name.lower()
    if lower_name.endswith(".json"):
        return [_parse_xai_import_document(content, upload_name)], []
    if not lower_name.endswith(".zip"):
        raise ValueError(f"{upload_name} must be a JSON file or ZIP archive.")

    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile as exc:
        raise ValueError(f"{upload_name} is not a valid ZIP archive.") from exc

    candidates: List[Dict[str, Any]] = []
    errors: List[dict] = []
    with archive:
        json_entries = [
            entry
            for entry in archive.infolist()
            if not entry.is_dir() and entry.filename.lower().endswith(".json")
        ]
        if not json_entries:
            raise ValueError(f"{upload_name} does not contain any JSON files.")
        if len(json_entries) > MAX_PROVIDER_IMPORT_ENTRIES:
            raise ValueError(
                f"{upload_name} contains more than {MAX_PROVIDER_IMPORT_ENTRIES} JSON files."
            )

        total_uncompressed = sum(entry.file_size for entry in json_entries)
        if total_uncompressed > MAX_PROVIDER_IMPORT_UNCOMPRESSED_BYTES:
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
                with archive.open(entry) as entry_stream:
                    entry_content = entry_stream.read(MAX_PROVIDER_IMPORT_FILE_BYTES + 1)
                if len(entry_content) > MAX_PROVIDER_IMPORT_FILE_BYTES:
                    raise ValueError(f"{source_name} exceeds the 2 MB entry limit.")
                candidates.append(_parse_xai_import_document(entry_content, source_name))
            except (RuntimeError, ValueError, zipfile.BadZipFile) as exc:
                errors.append(
                    {
                        "status": "error",
                        "source_filename": source_name,
                        "message": str(exc),
                    }
                )
    return candidates, errors


def _xai_import_identity(candidate: Dict[str, Any]) -> str:
    payload = candidate["payload"]
    credential_type = str(payload.get("credential_type") or "").strip().lower()
    if credential_type == "api_key":
        identity = str(payload.get("api_key") or "").strip()
    else:
        identity = str(
            payload.get("account_fingerprint")
            or payload.get("user_email")
            or payload.get("refresh_token")
            or payload.get("access_token")
            or payload.get("credential_label")
            or ""
        ).strip()
    return f"{credential_type}:{api_key_fingerprint(identity)}"


@router.post("/api/providers/xai/credentials/import")
async def import_xai_credentials(
    files: List[UploadFile] = File(...),
    credential_type: str = "",
    token: str = Depends(verify_panel_token),
):
    """Import bounded Grok OAuth or xAI Console API key credentials."""
    normalized_type = str(credential_type or "").strip().lower()
    if normalized_type not in {"", "oauth", "api_key"}:
        raise HTTPException(
            status_code=400,
            detail="Credential type must be 'oauth' or 'api_key'.",
        )
    if not files:
        raise HTTPException(status_code=400, detail="Select at least one import file.")
    if len(files) > 50:
        raise HTTPException(status_code=400, detail="A single import supports up to 50 files.")

    candidates: List[Dict[str, Any]] = []
    results: List[dict] = []
    for upload in files:
        try:
            extracted, extraction_errors = await _extract_xai_import_file(upload)
            results.extend(extraction_errors)
            for candidate in extracted:
                candidate_type = (
                    str(candidate["payload"].get("credential_type") or "").strip().lower()
                )
                if normalized_type and candidate_type != normalized_type:
                    expected_label = (
                        "Grok OAuth credential"
                        if normalized_type == "oauth"
                        else "xAI Console API key"
                    )
                    results.append(
                        {
                            "status": "error",
                            "source_filename": candidate["source_filename"],
                            "message": (
                                f"{candidate['source_filename']} is not a {expected_label}."
                            ),
                        }
                    )
                    continue
                candidates.append(candidate)
        except ValueError as exc:
            results.append(
                {
                    "status": "error",
                    "source_filename": _safe_import_name(upload.filename or "Import file"),
                    "message": str(exc),
                }
            )

    if len(candidates) > MAX_PROVIDER_IMPORT_ENTRIES:
        raise HTTPException(
            status_code=400,
            detail=f"A single import supports up to {MAX_PROVIDER_IMPORT_ENTRIES} credentials.",
        )

    counts = {"created": 0, "updated": 0, "replaced": 0, "skipped": 0}
    seen_identities = set()
    for candidate in candidates:
        identity = _xai_import_identity(candidate)
        if identity in seen_identities:
            counts["skipped"] += 1
            results.append(
                {
                    "status": "skipped",
                    "action": "skipped",
                    "source_filename": candidate["source_filename"],
                    "message": "A duplicate provider credential in this import was skipped.",
                }
            )
            continue
        seen_identities.add(identity)

        try:
            restored = await restore_xai_credential(candidate)
            action = str(restored.get("action") or "created")
            status = str(restored.get("status") or "success")
            counter = action if action in {"created", "updated", "replaced"} else "skipped"
            if status == "skipped":
                counter = "skipped"
            counts[counter] += 1
            results.append(
                {
                    "status": status,
                    "action": action,
                    "filename": restored.get("filename", candidate["filename"]),
                    "source_filename": candidate["source_filename"],
                    "model_count": restored.get("model_count"),
                    "message": restored.get("message") or "Provider credential imported.",
                }
            )
        except XaiError as exc:
            results.append(
                {
                    "status": "error",
                    "source_filename": candidate["source_filename"],
                    "message": str(exc),
                }
            )
        except Exception as exc:
            log.error(f"Failed to import a Grok or xAI Console credential: {exc}")
            results.append(
                {
                    "status": "error",
                    "source_filename": candidate["source_filename"],
                    "message": "The provider credential could not be stored.",
                }
            )

    error_count = sum(1 for item in results if item.get("status") == "error")
    uploaded_count = counts["created"] + counts["updated"] + counts["replaced"]
    message = (
        f"Import completed. Results: {counts['created']} added, {counts['updated']} updated, "
        f"{counts['replaced']} renewed, {counts['skipped']} skipped, and {error_count} failed."
    )
    return JSONResponse(
        content={
            "success": True,
            "uploaded_count": uploaded_count,
            "created_count": counts["created"],
            "updated_count": counts["updated"],
            "replaced_count": counts["replaced"],
            "skipped_count": counts["skipped"],
            "error_count": error_count,
            "total_count": len(candidates),
            "credential_type": normalized_type or "all",
            "results": results,
            "message": message,
        }
    )
