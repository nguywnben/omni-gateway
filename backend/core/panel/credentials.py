import json
import os
import time
from typing import List

from config import (
    get_antigravity_api_url,
    get_code_assist_endpoint,
    get_google_ai_studio_api_url,
)
from core.api.primary import fetch_quota_info
from core.credential_manager import credential_manager
from core.google_ai_studio import (
    build_api_key_headers,
    build_generation_url,
)
from core.google_oauth_api import (
    Credentials,
)
from core.model_pool import ModelPoolError, model_catalog_service, normalize_model_id
from core.models import (
    CredentialModelTestRequest,
    CredFileActionRequest,
    CredFileBatchActionRequest,
)
from core.pool_import import PoolImportError, restore_pool_archive
from core.provider_registry import (
    GOOGLE_AI_STUDIO,
    GOOGLE_ANTIGRAVITY,
    get_credential_provider,
    get_declared_credential_models,
)
from core.storage_adapter import get_storage_adapter
from core.utils import CODE_ASSIST_USER_AGENT, verify_panel_token
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from log import log

from .credential_operations import (
    _get_download_filename,
    clear_all_model_cooldowns_for_credential,
    deduplicate_credentials_by_email_common,
    download_all_creds_common,
    fetch_user_email_common,
    get_creds_status_common,
    refresh_all_user_emails_common,
    upload_credentials_common,
    verify_credential_project_common,
)
from .utils import (
    internal_server_error,
    public_error_detail,
    validate_credential_filename,
    validate_mode,
)

router = APIRouter(tags=["credentials"])


async def _get_available_credential_models(credential_data: dict) -> list[str]:
    """Return models that can be selected for one credential test."""
    declared_models = get_declared_credential_models(credential_data)
    if declared_models:
        return declared_models

    provider_id = get_credential_provider(credential_data)
    catalog = await model_catalog_service.get_catalog()
    return [entry.model_id for entry in catalog if provider_id in entry.providers]


@router.post("/upload")
async def upload_credentials(
    files: List[UploadFile] = File(...),
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist",
):
    try:
        mode = validate_mode(mode)
        return await upload_credentials_common(files, mode=mode)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Batch upload failed: {e}")
        raise internal_server_error() from e


@router.get("/status")
async def get_creds_status(
    token: str = Depends(verify_panel_token),
    offset: int = 0,
    limit: int = 50,
    status_filter: str = "all",
    error_code_filter: str = "all",
    cooldown_filter: str = "all",
    preview_filter: str = "all",
    tier_filter: str = "all",
    provider_filter: str = "all",
    mode: str = "code_assist",
):
    try:
        mode = validate_mode(mode)
        return await get_creds_status_common(
            offset,
            limit,
            status_filter,
            mode=mode,
            error_code_filter=error_code_filter,
            cooldown_filter=cooldown_filter,
            preview_filter=preview_filter,
            tier_filter=tier_filter,
            provider_filter=provider_filter,
        )
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve credential status: {e}")
        raise internal_server_error() from e


@router.get("/models/{filename}")
async def get_credential_models(
    filename: str,
    token: str = Depends(verify_panel_token),
    mode: str = "primary",
):
    """Return public model metadata for one credential without exposing secrets."""
    try:
        mode = validate_mode(mode)
        filename = validate_credential_filename(filename)
        storage_adapter = await get_storage_adapter()
        credential_data = await storage_adapter.get_credential(filename, mode=mode)
        if not credential_data:
            raise HTTPException(status_code=404, detail="Credential does not exist.")

        model_ids = await _get_available_credential_models(credential_data)
        return JSONResponse(
            content={
                "success": True,
                "filename": filename,
                "provider": get_credential_provider(credential_data),
                "model_count": len(model_ids),
                "model_ids": model_ids,
            }
        )
    except HTTPException:
        raise
    except Exception as exc:
        log.error(f"Failed to retrieve credential models: {exc}")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve credential models.",
        ) from exc


@router.get("/detail/{filename}")
async def get_cred_detail(
    filename: str, token: str = Depends(verify_panel_token), mode: str = "code_assist"
):
    try:
        mode = validate_mode(mode)
        filename = validate_credential_filename(filename)

        storage_adapter = await get_storage_adapter()
        backend_info = await storage_adapter.get_backend_info()
        backend_type = backend_info.get("backend_type", "unknown")

        credential_data = await storage_adapter.get_credential(filename, mode=mode)
        if not credential_data:
            raise HTTPException(status_code=404, detail="Credential does not exist")

        file_status = await storage_adapter.get_credential_state(filename, mode=mode)
        if not file_status:
            file_status = {
                "error_codes": [],
                "disabled": False,
                "last_success": time.time(),
                "user_email": None,
            }

        result = {
            "status": file_status,
            "content": credential_data,
            "filename": os.path.basename(filename),
            "backend_type": backend_type,
            "user_email": file_status.get("user_email"),
            "model_cooldowns": file_status.get("model_cooldowns", {}),
        }

        if mode == "code_assist":
            result["preview"] = file_status.get("preview", True)
        else:
            result["enable_credit"] = file_status.get("enable_credit", False)

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve credential details {filename}: {e}")
        raise internal_server_error() from e


@router.post("/action")
async def creds_action(
    request: CredFileActionRequest,
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist",
):
    try:
        mode = validate_mode(mode)

        log.info(f"Received request: {request}")

        filename = validate_credential_filename(request.filename)
        action = request.action

        log.info(f"Performing action '{action}' on file: {filename} (mode={mode})")

        storage_adapter = await get_storage_adapter()

        if action != "delete":
            credential_data = await storage_adapter.get_credential(filename, mode=mode)
            if not credential_data:
                log.error(f"Credential not found: {filename} (mode={mode})")
                raise HTTPException(status_code=404, detail="Credential file does not exist.")

        if action == "enable":
            log.info(f"Web request: enable file {filename} (mode = {mode})")
            result = await credential_manager.set_cred_disabled(filename, False, mode=mode)
            log.info(f"[WebRoute] set_cred_disabled result: {result}")
            if result:
                log.info(f"Web request: credential {filename} enabled (mode = {mode}).")
                return JSONResponse(
                    content={"message": f"Enabled credential {os.path.basename(filename)}."}
                )
            else:
                log.error(f"Web request: File {filename} enable failed (mode = {mode})")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to enable the credential. It may no longer exist.",
                )

        elif action == "disable":
            log.info(f"Web request: Disable file {filename} (mode = {mode})")
            result = await credential_manager.set_cred_disabled(filename, True, mode=mode)
            log.info(f"[WebRoute] set_cred_disabled result: {result}")
            if result:
                log.info(f"Web request: credential {filename} disabled (mode = {mode}).")
                return JSONResponse(
                    content={"message": f"Disabled credential {os.path.basename(filename)}."}
                )
            else:
                log.error(f"Web request: file {filename} disable failed (mode = {mode})")
                raise HTTPException(
                    status_code=500,
                    detail="Failed to disable the credential. It may no longer exist.",
                )

        elif action == "delete":
            try:
                # Use CredentialManager to delete credential (synced queue/state)
                success = await credential_manager.remove_credential(filename, mode=mode)
                if success:
                    log.info(f"Deleted credential via manager: {filename} (mode={mode}).")
                    return JSONResponse(
                        content={
                            "success": True,
                            "deleted": True,
                            "history_retained_anonymously": True,
                            "message": "Credential deleted. Historical usage was retained anonymously.",
                        }
                    )
                else:
                    raise HTTPException(status_code=500, detail="Failed to delete the credential.")
            except Exception as e:
                log.error(f"Error deleting credential {filename}: {e}")
                raise internal_server_error() from e

        elif action == "enable_credit":
            if mode != "primary" or get_credential_provider(credential_data) != GOOGLE_ANTIGRAVITY:
                raise HTTPException(
                    status_code=400,
                    detail="Credit mode is only available for Google Antigravity credentials.",
                )
            updated = await storage_adapter.update_credential_state(
                filename, {"enable_credit": True}, mode=mode
            )
            if updated:
                await clear_all_model_cooldowns_for_credential(storage_adapter, filename, mode)
                return JSONResponse(
                    content={"message": f"Enabled credit mode for {os.path.basename(filename)}."}
                )
            raise HTTPException(
                status_code=500,
                detail="Failed to enable credit mode. The credential may no longer exist.",
            )

        elif action == "disable_credit":
            if mode != "primary" or get_credential_provider(credential_data) != GOOGLE_ANTIGRAVITY:
                raise HTTPException(
                    status_code=400,
                    detail="Credit mode is only available for Google Antigravity credentials.",
                )
            updated = await storage_adapter.update_credential_state(
                filename, {"enable_credit": False}, mode=mode
            )
            if updated:
                await clear_all_model_cooldowns_for_credential(storage_adapter, filename, mode)
                return JSONResponse(
                    content={"message": f"Disabled credit mode for {os.path.basename(filename)}."}
                )
            raise HTTPException(
                status_code=500,
                detail="Failed to disable credit mode. The credential may no longer exist.",
            )

        else:
            raise HTTPException(status_code=400, detail="Invalid credential action.")

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Credential file operation failed: {e}")
        raise internal_server_error() from e


@router.post("/batch-action")
async def creds_batch_action(
    request: CredFileBatchActionRequest,
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist",
):
    try:
        mode = validate_mode(mode)

        action = request.action
        filenames = request.filenames

        if not filenames:
            raise HTTPException(
                status_code=400,
                detail="Select at least one credential file before running a batch action.",
            )

        log.info(f"Performing batch operation on {len(filenames)} files with action: {action}")

        success_count = 0
        errors = []

        storage_adapter = await get_storage_adapter()

        for filename in filenames:
            try:
                try:
                    filename = validate_credential_filename(filename)
                except HTTPException:
                    errors.append("A selected credential has an invalid file name.")
                    continue

                # For delete actions, we don't need to check data integrity
                # For other actions, ensure the credential exists
                if action != "delete":
                    credential_data = await storage_adapter.get_credential(filename, mode=mode)
                    if not credential_data:
                        errors.append(f"{filename}: credential does not exist")
                        continue

                # Execute action
                if action == "enable":
                    await credential_manager.set_cred_disabled(filename, False, mode=mode)
                    success_count += 1

                elif action == "disable":
                    await credential_manager.set_cred_disabled(filename, True, mode=mode)
                    success_count += 1

                elif action == "delete":
                    try:
                        delete_success = await credential_manager.remove_credential(
                            filename, mode=mode
                        )
                        if delete_success:
                            success_count += 1
                            log.info(f"Deleted credential from batch: {filename}.")
                        else:
                            errors.append(f"{filename}: delete failed")
                            continue
                    except Exception:
                        errors.append(f"{filename}: delete failed")
                        continue
                elif action == "enable_credit":
                    if (
                        mode != "primary"
                        or get_credential_provider(credential_data) != GOOGLE_ANTIGRAVITY
                    ):
                        errors.append(
                            f"{filename}: credit mode is only available for Google Antigravity credentials"
                        )
                        continue
                    updated = await storage_adapter.update_credential_state(
                        filename, {"enable_credit": True}, mode=mode
                    )
                    if updated:
                        await clear_all_model_cooldowns_for_credential(
                            storage_adapter, filename, mode
                        )
                        success_count += 1
                    else:
                        errors.append(f"{filename}: failed to enable credit mode")
                        continue
                elif action == "disable_credit":
                    if (
                        mode != "primary"
                        or get_credential_provider(credential_data) != GOOGLE_ANTIGRAVITY
                    ):
                        errors.append(
                            f"{filename}: credit mode is only available for Google Antigravity credentials"
                        )
                        continue
                    updated = await storage_adapter.update_credential_state(
                        filename, {"enable_credit": False}, mode=mode
                    )
                    if updated:
                        await clear_all_model_cooldowns_for_credential(
                            storage_adapter, filename, mode
                        )
                        success_count += 1
                    else:
                        errors.append(f"{filename}: failed to disable credit mode")
                        continue
                else:
                    errors.append(f"{filename}: invalid credential action")
                    continue

            except Exception as e:
                log.error(f"Error processing {filename}: {e}")
                errors.append(f"{filename}: processing failed")
                continue

        # Build response message
        result_message = f"Batch operation complete: processed {success_count}/{len(filenames)} credential files."
        if errors:
            result_message += "\nError details:\n" + "\n".join(errors)

        response_data = {
            "success_count": success_count,
            "total_count": len(filenames),
            "errors": errors,
            "message": result_message,
        }
        if action == "delete" and success_count > 0:
            response_data["history_retained_anonymously"] = True

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Batch credential file operation failed: {e}")
        raise internal_server_error() from e


@router.get("/download/{filename}")
async def download_cred_file(
    filename: str, token: str = Depends(verify_panel_token), mode: str = "code_assist"
):
    try:
        mode = validate_mode(mode)
        filename = validate_credential_filename(filename)

        storage_adapter = await get_storage_adapter()

        credential_data = await storage_adapter.get_credential(filename, mode=mode)
        if not credential_data:
            raise HTTPException(status_code=404, detail="Credential file does not exist.")

        content = json.dumps(credential_data, ensure_ascii=False, indent=2)
        download_filename = await _get_download_filename(
            storage_adapter,
            filename,
            credential_data,
            mode,
        )

        from fastapi.responses import Response

        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={download_filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to download credential file: {e}")
        raise internal_server_error() from e


@router.post("/fetch-email/{filename}")
async def fetch_user_email(
    filename: str, token: str = Depends(verify_panel_token), mode: str = "code_assist"
):
    try:
        mode = validate_mode(mode)
        return await fetch_user_email_common(filename, mode=mode)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve user email: {e}")
        raise internal_server_error() from e


@router.post("/refresh-all-emails")
async def refresh_all_user_emails(
    token: str = Depends(verify_panel_token), mode: str = "code_assist"
):
    try:
        mode = validate_mode(mode)
        return await refresh_all_user_emails_common(mode=mode)
    except Exception as e:
        log.error(f"Failed to retrieve user emails in batch: {e}")
        raise internal_server_error() from e


@router.post("/deduplicate-by-email")
async def deduplicate_credentials_by_email(
    token: str = Depends(verify_panel_token), mode: str = "code_assist"
):
    try:
        mode = validate_mode(mode)
        return await deduplicate_credentials_by_email_common(mode=mode)
    except Exception as e:
        log.error(f"Failed to deduplicate credentials in batch: {e}")
        raise internal_server_error() from e


@router.get("/download-all")
async def download_all_creds(token: str = Depends(verify_panel_token), mode: str = "code_assist"):
    try:
        mode = validate_mode(mode)
        return await download_all_creds_common(mode=mode)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to download package: {e}")
        raise internal_server_error() from e


@router.post("/import")
async def import_pool_credentials(
    archive: UploadFile = File(...),
    token: str = Depends(verify_panel_token),
):
    """Restore a mixed-provider credential pool from one ZIP archive."""
    try:
        return JSONResponse(content=await restore_pool_archive(archive))
    except PoolImportError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        log.error(f"Pool restore failed: {exc}")
        raise HTTPException(status_code=500, detail="Pool archive could not be restored.") from exc


@router.post("/verify-project/{filename}")
async def verify_credential_project(
    filename: str, token: str = Depends(verify_panel_token), mode: str = "code_assist"
):
    try:
        mode = validate_mode(mode)
        return await verify_credential_project_common(filename, mode=mode)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to verify credential Project ID {filename}: {e}")
        raise internal_server_error() from e


@router.get("/errors/{filename}")
async def get_credential_errors(
    filename: str, token: str = Depends(verify_panel_token), mode: str = "code_assist"
):
    try:
        mode = validate_mode(mode)
        filename = validate_credential_filename(filename)

        storage_adapter = await get_storage_adapter()

        if not hasattr(storage_adapter._backend, "get_credential_errors"):
            raise HTTPException(
                status_code=501,
                detail="The current storage backend does not support retrieving credential error messages.",
            )

        error_info = await storage_adapter._backend.get_credential_errors(filename, mode=mode)

        return JSONResponse(content=error_info)

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve credential error information {filename}: {e}")
        raise internal_server_error() from e


@router.get("/quota/{filename}")
async def get_credential_quota(
    filename: str, token: str = Depends(verify_panel_token), mode: str = "provider"
):
    try:
        mode = validate_mode(mode)
        filename = validate_credential_filename(filename)

        storage_adapter = await get_storage_adapter()

        credential_data = await storage_adapter.get_credential(filename, mode=mode)
        if not credential_data:
            raise HTTPException(status_code=404, detail="Credential does not exist.")

        provider_id = get_credential_provider(credential_data)
        if provider_id == GOOGLE_AI_STUDIO:
            return JSONResponse(
                content={
                    "success": True,
                    "supported": False,
                    "filename": filename,
                    "provider": provider_id,
                    "models": {},
                    "message": (
                        "Google AI Studio does not expose per-key quota balances "
                        "through the Generative Language API."
                    ),
                }
            )

        from core.google_oauth_api import Credentials

        creds = Credentials.from_dict(credential_data)

        await creds.refresh_if_needed()

        updated_data = creds.to_dict()
        if updated_data != credential_data:
            log.info(f"Token automatically refreshed: {filename}")
            await storage_adapter.store_credential(filename, updated_data, mode=mode)
            credential_data = updated_data

        access_token = credential_data.get("access_token") or credential_data.get("token")
        if not access_token:
            raise HTTPException(
                status_code=400, detail="Credential does not contain an access token."
            )

        quota_info = await fetch_quota_info(access_token)

        if quota_info.get("success"):
            return JSONResponse(
                content={
                    "success": True,
                    "filename": filename,
                    "models": quota_info.get("models", {}),
                }
            )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "filename": filename,
                    "error": quota_info.get("error", "Unknown error."),
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve credential quota {filename}: {e}")
        raise internal_server_error() from e


@router.post("/configure-preview/{filename}")
async def configure_preview_channel(
    filename: str, token: str = Depends(verify_panel_token), mode: str = "code_assist"
):
    try:
        mode = validate_mode(mode)

        if mode != "code_assist":
            raise HTTPException(
                status_code=400,
                detail="The Preview channel can only be configured for Code Assist credentials.",
            )

        filename = validate_credential_filename(filename)

        storage_adapter = await get_storage_adapter()

        credential_data = await storage_adapter.get_credential(filename, mode=mode)
        if not credential_data:
            raise HTTPException(status_code=404, detail="Credential does not exist.")

        credentials = Credentials.from_dict(credential_data)
        token_refreshed = await credentials.refresh_if_needed()

        if token_refreshed:
            log.info(f"Token automatically refreshed: {filename}")
            credential_data = credentials.to_dict()
            await storage_adapter.store_credential(filename, credential_data, mode=mode)

        access_token = credential_data.get("access_token") or credential_data.get("token")
        project_id = credential_data.get("project_id", "")

        if not access_token:
            raise HTTPException(
                status_code=400, detail="Credential does not contain an access token."
            )
        if not project_id:
            raise HTTPException(status_code=400, detail="Credential does not contain a Project ID.")

        import uuid

        from core.httpx_client import get_async, post_async

        setting_id = f"preview-setting-{uuid.uuid4().hex[:8]}"
        binding_id = f"preview-binding-{uuid.uuid4().hex[:8]}"

        base_url = (
            f"https://cloudaicompanion.googleapis.com/v1/projects/{project_id}/locations/global"
        )
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        log.info(f"Starting configuration of preview channel: {filename} (project_id={project_id})")

        setting_url = f"{base_url}/releaseChannelSettings"
        setting_response = await post_async(
            url=setting_url,
            json={"release_channel": "EXPERIMENTAL"},
            headers=headers,
            params={"release_channel_setting_id": setting_id},
            timeout=30.0,
        )

        setting_status = setting_response.status_code

        if setting_status == 200 or setting_status == 201:
            log.info(f"Step 1/2: Release channel setting created (setting_id={setting_id}).")
        elif setting_status == 409:
            log.info(
                "Step 1/2: Release channel setting already exists; retrieving the existing setting ID."
            )
            list_response = await get_async(url=setting_url, headers=headers, timeout=30.0)
            if list_response.status_code == 200:
                try:
                    list_data = list_response.json()
                    settings = list_data.get("releaseChannelSettings", [])
                    if settings:
                        existing_name = settings[0].get("name", "")
                        setting_id = existing_name.split("/")[-1]
                        log.info(f"Step 1/2: Retrieved existing setting_id={setting_id}")
                    else:
                        log.warning(
                            "Step 1/2: the list response was empty; keeping the generated setting ID."
                        )
                except Exception as e:
                    log.warning(
                        f"Step 1/2: failed to parse the list response: {e}. Keeping the generated setting ID."
                    )
            else:
                log.warning(
                    f"Step 1/2: list request failed (status={list_response.status_code}); keeping the generated setting ID."
                )
        else:
            error_text = public_error_detail(
                setting_response.text if hasattr(setting_response, "text") else ""
            )
            log.error(
                f"Step 1/2 failed: {filename} - Status: {setting_status}, Error: {error_text}"
            )

            return JSONResponse(
                status_code=setting_status,
                content={
                    "success": False,
                    "filename": filename,
                    "preview": False,
                    "message": f"Failed to create Release Channel Setting: HTTP {setting_status}",
                    "error": error_text,
                    "step": "create_setting",
                },
            )

        # Step 2: Create Setting Binding (bind to project)
        binding_url = f"{base_url}/releaseChannelSettings/{setting_id}/settingBindings"
        binding_response = await post_async(
            url=binding_url,
            json={"target": f"projects/{project_id}", "product": "GEMINI_CODE_ASSIST"},
            headers=headers,
            params={"setting_binding_id": binding_id},
            timeout=30.0,
        )

        binding_status = binding_response.status_code

        if binding_status == 200 or binding_status == 201:
            await storage_adapter.update_credential_state(filename, {"preview": True}, mode=mode)

            log.info(
                f"Step 2/2: Setting binding created. Preview channel configuration completed for {filename}."
            )

            return JSONResponse(
                content={
                    "success": True,
                    "filename": filename,
                    "preview": True,
                    "message": "Preview channel configured, and Preview mode is now enabled.",
                    "setting_id": setting_id,
                    "binding_id": binding_id,
                }
            )
        elif binding_status == 409:
            # Binding already exists, meaning it was configured already
            await storage_adapter.update_credential_state(filename, {"preview": True}, mode=mode)

            log.info(
                f"Step 2/2: Setting Binding already exists - Preview channel is configured: {filename}"
            )

            return JSONResponse(
                content={
                    "success": True,
                    "filename": filename,
                    "preview": True,
                    "message": "Preview channel configuration already exists, and preview mode is enabled.",
                }
            )
        else:
            # Step 2 failed
            error_text = public_error_detail(
                binding_response.text if hasattr(binding_response, "text") else ""
            )
            log.error(
                f"Step 2/2 failed: {filename} - Status: {binding_status}, Error: {error_text}"
            )

            return JSONResponse(
                status_code=binding_status,
                content={
                    "success": False,
                    "filename": filename,
                    "preview": False,
                    "message": f"Failed to create Setting Binding: HTTP {binding_status}",
                    "error": error_text,
                    "step": "create_binding",
                },
            )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to configure preview channel {filename}: {e}")
        raise internal_server_error() from e


@router.post("/test/{filename}")
async def test_credential(
    filename: str,
    request: CredentialModelTestRequest,
    mode: str = "code_assist",
    _token: str = Depends(verify_panel_token),
):
    try:
        mode = validate_mode(mode)

        filename = validate_credential_filename(filename)

        storage_adapter = await get_storage_adapter()

        credential_data = await storage_adapter.get_credential(filename, mode=mode)
        if not credential_data:
            raise HTTPException(status_code=404, detail="Credential does not exist.")

        from core.httpx_client import post_async

        provider_id = get_credential_provider(credential_data)
        try:
            test_model = normalize_model_id(request.model)
        except ModelPoolError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        available_models = await _get_available_credential_models(credential_data)
        if not available_models:
            raise HTTPException(
                status_code=409,
                detail="No models are currently available for this credential.",
            )
        if test_model not in available_models:
            raise HTTPException(
                status_code=400,
                detail="The selected model is not available for this credential.",
            )

        test_request = {
            "contents": [{"role": "user", "parts": [{"text": "hi"}]}],
            "generationConfig": {"maxOutputTokens": 1},
        }

        if mode == "primary" and provider_id == GOOGLE_AI_STUDIO:
            api_key = str(credential_data.get("api_key") or "").strip()
            headers = build_api_key_headers(api_key)
            request_body = test_request
            request_url = build_generation_url(
                await get_google_ai_studio_api_url(), test_model, streaming=False
            )
            access_token = ""
            project_id = ""
        else:
            credentials = Credentials.from_dict(credential_data)
            token_refreshed = await credentials.refresh_if_needed()
            if token_refreshed:
                log.info(f"Token automatically refreshed: {filename} (mode = {mode})")
                credential_data = credentials.to_dict()
                await storage_adapter.store_credential(filename, credential_data, mode=mode)

            access_token = credential_data.get("access_token") or credential_data.get("token")
            if not access_token:
                raise HTTPException(
                    status_code=400,
                    detail="Credential does not contain an access token.",
                )
            project_id = credential_data.get("project_id", "")
            if not project_id:
                raise HTTPException(
                    status_code=400,
                    detail="Credential does not contain a Project ID.",
                )

        if mode == "primary" and provider_id != GOOGLE_AI_STUDIO:
            api_base_url = await get_antigravity_api_url()
            from core.api.primary import build_primary_headers

            headers = await build_primary_headers(access_token, test_model)
            request_body = {
                "model": test_model,
                "project": project_id,
                "request": test_request,
            }
            request_url = f"{api_base_url}/v1internal:generateContent"
        elif mode != "primary":
            api_base_url = await get_code_assist_endpoint()
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "User-Agent": CODE_ASSIST_USER_AGENT,
            }
            request_body = {
                "model": test_model,
                "project": project_id,
                "request": test_request,
            }
            request_url = f"{api_base_url}/v1internal:generateContent"

        response = await post_async(
            url=request_url, json=request_body, headers=headers, timeout=30.0
        )

        status_code = response.status_code

        if status_code == 200 or status_code == 429:
            log.info(
                f"Credential test successful: {filename} (mode={mode}, model={test_model}, status={status_code})"
            )

            if status_code == 200:
                await storage_adapter.update_credential_state(
                    filename, {"error_codes": [], "error_messages": {}}, mode=mode
                )

                if mode == "code_assist":
                    preview_model = "gemini-3-flash-preview"
                    log.info(f"Starting preview model test: {filename} (model={preview_model})")

                    try:
                        preview_response = await post_async(
                            url=f"{api_base_url}/v1internal:generateContent",
                            json={
                                "model": preview_model,
                                "project": project_id,
                                "request": {
                                    "contents": [{"role": "user", "parts": [{"text": "hi"}]}],
                                    "generationConfig": {"maxOutputTokens": 1},
                                },
                            },
                            headers=headers,
                            timeout=30.0,
                        )

                        preview_status = preview_response.status_code

                        if preview_status == 200 or preview_status == 429:
                            log.info(
                                f"Preview model test passed: {filename} (status = {preview_status})."
                            )
                            await storage_adapter.update_credential_state(
                                filename, {"preview": True}, mode=mode
                            )
                        elif preview_status == 404:
                            log.warning(
                                f"Preview model is not supported for {filename} (status = 404)"
                            )
                            await storage_adapter.update_credential_state(
                                filename, {"preview": False}, mode=mode
                            )
                        else:
                            log.warning(
                                f"Preview model test failed: {filename} (status = {preview_status})"
                            )
                    except Exception as e:
                        log.error(f"Preview model test failed for {filename}: {e}")

            message = (
                "Credential is valid, but the upstream provider is currently rate limited."
                if status_code == 429
                else "Test successful."
            )
            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "status_code": status_code,
                    "message": message,
                    "filename": filename,
                    "provider": provider_id,
                    "model": test_model,
                },
            )
        else:
            log.warning(f"Credential test failed: {filename} (mode={mode}, status={status_code})")

            try:
                error_text = public_error_detail(response.text if hasattr(response, "text") else "")

                log.error(
                    f"Credential test error details - file: {filename}, mode: {mode}, status code: {status_code}, error: {error_text}"
                )

                error_codes = [status_code]
                error_messages = {
                    str(status_code): error_text if error_text else f"HTTP {status_code}"
                }

                await storage_adapter.update_credential_state(
                    filename,
                    {"error_codes": error_codes, "error_messages": error_messages},
                    mode=mode,
                )

                log.info(f"Saved test error info: {filename} - error code {status_code}")
            except Exception as e:
                log.error(f"Failed to save test error message: {e}")

        error_text = public_error_detail(response.text if hasattr(response, "text") else "")

        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "status_code": status_code,
                "message": f"Test failed: HTTP {status_code}",
                "error": error_text,
                "filename": filename,
                "model": test_model,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to test credential {filename}: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "status_code": 500,
                "message": "Test failed.",
                "error": public_error_detail(e, "Credential testing failed."),
                "detail": public_error_detail(e, "Credential testing failed."),
                "filename": filename,
            },
        )
