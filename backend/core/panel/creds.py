"""Internal implementation detail."""

import asyncio
import io
import json
import os
import time
import zipfile
from typing import Any, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, Response
from fastapi.responses import JSONResponse

from log import log
from core.credential_pool import deduplicate_credentials_by_account_email, parse_credential_expiry, resolve_credential_email
from core.credential_manager import credential_manager
from core.models import (
    CredFileActionRequest,
    CredFileBatchActionRequest
)
from core.storage_adapter import get_storage_adapter
from core.utils import verify_panel_token, CODE_ASSIST_USER_AGENT
from core.api.primary import fetch_quota_info
from core.google_ai_studio import (
    GoogleAIStudioError,
    build_api_key_headers,
    build_generation_url,
    validate_api_key,
)
from core.google_oauth_api import Credentials, fetch_project_id_and_tier, get_user_projects, select_default_project, enable_required_apis
from core.provider_registry import (
    GOOGLE_ANTIGRAVITY,
    GOOGLE_AI_STUDIO,
    get_credential_provider,
    normalize_provider_id,
)
from config import (
    get_antigravity_api_url,
    get_antigravity_user_agent,
    get_code_assist_endpoint,
    get_google_ai_studio_api_url,
)
from .utils import validate_mode



router = APIRouter(prefix="/api/creds", tags=["credentials"])


# =============================================================================

# =============================================================================


async def extract_json_files_from_zip(zip_file: UploadFile) -> List[dict]:
    """Internal implementation detail."""
    try:

        zip_content = await zip_file.read()



        files_data = []

        with zipfile.ZipFile(io.BytesIO(zip_content), "r") as zip_ref:

            file_list = zip_ref.namelist()
            json_files = [
                f for f in file_list if f.endswith(".json") and not f.startswith("__MACOSX/")
            ]

            if not json_files:
                raise HTTPException(status_code=400, detail="No JSON files were found in the ZIP archive.")

            log.info(f"Found {len(json_files)} JSON files in ZIP archive {zip_file.filename}.")

            for json_filename in json_files:
                try:

                    with zip_ref.open(json_filename) as json_file:
                        content = json_file.read()

                        try:
                            content_str = content.decode("utf-8")
                        except UnicodeDecodeError:
                            log.warning(f"Skipping file with encoding error: {json_filename}")
                            continue


                        filename = os.path.basename(json_filename)
                        files_data.append({"filename": filename, "content": content_str})

                except Exception as e:
                    log.warning(f"Error processing file {json_filename} in ZIP: {e}")
                    continue

        log.info(f"Extracted {len(files_data)} valid JSON files from the ZIP archive.")
        return files_data

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file format.")
    except Exception as e:
        log.error(f"Failed to process ZIP file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process ZIP file: {str(e)}")


async def clear_all_model_cooldowns_for_credential(
    storage_adapter: Any,
    filename: str,
    mode: str,
) -> None:
    """Internal implementation detail."""
    try:
        cleared = await storage_adapter._backend.clear_all_model_cooldowns(filename, mode=mode)
        if not cleared:
            log.warning(f"Failed to clear model cooldowns or credential does not exist: {filename} (mode={mode})")
    except Exception as e:
        log.warning(f"Failed to clear model cooldowns for {filename} (mode={mode}): {e}")


def _incoming_credential_is_better(candidate: dict, current: dict) -> bool:
    candidate_expiry = candidate.get("expiry")
    current_expiry = current.get("expiry")
    if candidate_expiry is None:
        return False
    if current_expiry is None:
        return True
    return candidate_expiry > current_expiry


async def _prepare_upload_candidates(files_data: List[dict]) -> tuple[List[dict], List[dict]]:
    candidates = []
    immediate_results = []
    best_by_email = {}

    for file_data in files_data:
        filename = os.path.basename(file_data["filename"])
        try:
            credential_data = json.loads(file_data["content"])
        except json.JSONDecodeError as e:
            immediate_results.append(
                {
                    "filename": file_data["filename"],
                    "status": "error",
                    "message": f"JSON format error: {str(e)}.",
                }
            )
            continue

        email = await resolve_credential_email(credential_data)
        if email:
            credential_data["user_email"] = email

        candidate = {
            "filename": filename,
            "source_filename": filename,
            "credential_data": credential_data,
            "email": email,
            "expiry": parse_credential_expiry(credential_data),
        }

        if not candidate["email"]:
            candidates.append(candidate)
            continue

        current = best_by_email.get(candidate["email"])
        if current is None:
            best_by_email[candidate["email"]] = candidate
            continue

        if _incoming_credential_is_better(candidate, current):
            immediate_results.append(
                {
                    "filename": current["filename"],
                    "source_filename": current["source_filename"],
                    "status": "skipped",
                    "action": "skipped",
                    "email": current["email"],
                    "message": "Skipped because another uploaded credential has the same email with a later expiry.",
                }
            )
            best_by_email[candidate["email"]] = candidate
        else:
            immediate_results.append(
                {
                    "filename": candidate["filename"],
                    "source_filename": candidate["source_filename"],
                    "status": "skipped",
                    "action": "skipped",
                    "email": candidate["email"],
                    "message": "Skipped because another uploaded credential has the same email with an equal or later expiry.",
                }
            )

    candidates.extend(best_by_email.values())
    return candidates, immediate_results


async def upload_credentials_common(
    files: List[UploadFile], mode: str = "code_assist"
) -> JSONResponse:
    """Internal implementation detail."""
    mode = validate_mode(mode)

    if not files:
        raise HTTPException(status_code=400, detail="Please select files to upload.")


    if len(files) > 100:
        raise HTTPException(
            status_code=400, detail=f"Too many files. A maximum of 100 files is supported; current count: {len(files)}."
        )

    files_data = []
    for file in files:

        if file.filename.endswith(".zip"):
            zip_files_data = await extract_json_files_from_zip(file)
            files_data.extend(zip_files_data)
            log.info(f"Extracted {len(zip_files_data)} JSON files from ZIP archive {file.filename}.")

        elif file.filename.endswith(".json"):

            content_chunks = []
            while True:
                chunk = await file.read(8192)
                if not chunk:
                    break
                content_chunks.append(chunk)

            content = b"".join(content_chunks)
            try:
                content_str = content.decode("utf-8")
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400, detail=f"File '{file.filename}' encoding is not supported."
                )

            files_data.append({"filename": file.filename, "content": content_str})
        else:
            raise HTTPException(
                status_code=400, detail=f"File format '{file.filename}' is not supported. Only JSON and ZIP files are supported."
            )

    upload_candidates, preprocessed_results = await _prepare_upload_candidates(files_data)

    mode_label = "provider" if mode == "primary" else "Code Assist"
    batch_size = 1000
    all_results = list(preprocessed_results)
    total_success = 0

    for i in range(0, len(upload_candidates), batch_size):
        batch_files = upload_candidates[i : i + batch_size]

        async def process_single_file(file_data):
            try:
                filename = file_data["filename"]

                filename = os.path.basename(filename)
                credential_data = file_data["credential_data"]


                if mode == "primary":
                    write_result = await credential_manager.add_primary_credential(filename, credential_data)
                else:
                    write_result = await credential_manager.add_credential(filename, credential_data)

                stored = write_result.get("stored", False)
                action = write_result.get("action", "created")
                status = "success" if stored else "skipped"
                saved_filename = write_result.get("filename", filename)
                log.debug(f"Credential upload result: {action} ({saved_filename}, mode={mode})")
                return {
                    "filename": saved_filename,
                    "source_filename": filename,
                    "status": status,
                    "action": action,
                    "email": write_result.get("email"),
                    "message": write_result.get("message") or ("Credential imported." if stored else "Credential skipped."),
                }

            except Exception as e:
                return {
                    "filename": file_data["filename"],
                    "status": "error",
                    "message": f"Processing failed: {str(e)}.",
                }

        log.info(f"Starting concurrent processing for {len(batch_files)} {mode} files.")
        concurrent_tasks = [process_single_file(file_data) for file_data in batch_files]
        batch_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)

        processed_results = []
        batch_uploaded_count = 0
        batch_skipped_count = 0
        for result in batch_results:
            if isinstance(result, Exception):
                processed_results.append(
                    {
                        "filename": "unknown",
                        "status": "error",
                        "message": f"Processing exception: {str(result)}.",
                    }
                )
            else:
                processed_results.append(result)
                if result["status"] == "success":
                    batch_uploaded_count += 1
                elif result["status"] == "skipped":
                    batch_skipped_count += 1

        all_results.extend(processed_results)
        total_success += batch_uploaded_count
        total_skipped = sum(1 for result in all_results if result.get("status") == "skipped")

        batch_num = (i // batch_size) + 1
        total_batches = (len(upload_candidates) + batch_size - 1) // batch_size
        log.info(
            f"Batch {batch_num}/{total_batches} complete: saved or renewed "
            f"{batch_uploaded_count}/{len(batch_files)} {mode_label} credential files; skipped {batch_skipped_count}."
        )

    total_skipped = sum(1 for result in all_results if result.get("status") == "skipped")
    if total_success > 0 or total_skipped > 0:
        message = (
            f"Batch upload complete: saved or renewed {total_success}/{len(files_data)} {mode_label} credential files; "
            f"skipped {total_skipped} duplicate credential files with an equal or shorter expiry."
        )
        return JSONResponse(
            content={
                "uploaded_count": total_success,
                "skipped_count": total_skipped,
                "total_count": len(files_data),
                "results": all_results,
                "message": message,
            }
        )
    else:
        raise HTTPException(status_code=400, detail=f"No {mode_label} credential files were imported.")


async def get_creds_status_common(
    offset: int, limit: int, status_filter: str, mode: str = "code_assist",
    error_code_filter: str = None, cooldown_filter: str = None,
    preview_filter: str = None, tier_filter: str = None,
    provider_filter: str = None,
) -> JSONResponse:
    """Internal implementation detail."""
    mode = validate_mode(mode)

    if offset < 0:
        raise HTTPException(status_code=400, detail="Offset must be greater than or equal to 0.")
    if limit not in [20, 50, 100, 200, 500, 1000]:
        raise HTTPException(status_code=400, detail="Limit must be 20, 50, 100, 200, 500, or 1000.")
    if status_filter not in ["all", "enabled", "disabled"]:
        raise HTTPException(status_code=400, detail="Status filter must be all, enabled, or disabled.")
    if cooldown_filter and cooldown_filter not in ["all", "in_cooldown", "no_cooldown"]:
        raise HTTPException(status_code=400, detail="Cooldown filter must be all, in_cooldown, or no_cooldown.")
    if preview_filter and preview_filter not in ["all", "preview", "no_preview"]:
        raise HTTPException(status_code=400, detail="Preview filter must be all, preview, or no_preview.")
    if tier_filter and tier_filter not in ["all", "free", "pro", "ultra"]:
        raise HTTPException(status_code=400, detail="Tier filter must be all, free, pro, or ultra.")

    normalized_provider_filter = "all"
    if provider_filter and str(provider_filter).strip().lower() != "all":
        normalized_provider_filter = normalize_provider_id(provider_filter)
        if mode != "primary" or normalized_provider_filter not in {
            GOOGLE_ANTIGRAVITY,
            GOOGLE_AI_STUDIO,
        }:
            raise HTTPException(
                status_code=400,
                detail="Provider filter must be all, google_antigravity, or google_ai_studio.",
            )


    dedupe_result = await deduplicate_credentials_by_account_email(mode=mode)

    storage_adapter = await get_storage_adapter()
    backend_info = await storage_adapter.get_backend_info()
    backend_type = backend_info.get("backend_type", "unknown")


    filter_by_provider = normalized_provider_filter != "all"
    result = await storage_adapter._backend.get_credentials_summary(
        offset=0 if filter_by_provider else offset,
        limit=None if filter_by_provider else limit,
        status_filter=status_filter,
        mode=mode,
        error_code_filter=error_code_filter if error_code_filter and error_code_filter != "all" else None,
        cooldown_filter=cooldown_filter if cooldown_filter and cooldown_filter != "all" else None,
        preview_filter=preview_filter if preview_filter and preview_filter != "all" else None,
        tier_filter=tier_filter if tier_filter and tier_filter != "all" else None
    )

    matching_creds = []
    for summary in result["items"]:
        filename = os.path.basename(summary["filename"])
        credential_data = await storage_adapter.get_credential(filename, mode=mode) or {}
        provider_id = get_credential_provider(credential_data)
        if filter_by_provider and provider_id != normalized_provider_filter:
            continue
        cred_info = {
            "filename": filename,
            "user_email": summary["user_email"],
            "credential_label": credential_data.get("credential_label"),
            "credential_type": credential_data.get("credential_type", "oauth"),
            "provider": provider_id,
            "disabled": summary["disabled"],
            "error_codes": summary["error_codes"],
            "last_success": summary["last_success"],
            "backend_type": backend_type,
            "model_cooldowns": summary.get("model_cooldowns", {}),
            "tier": summary.get("tier", "pro"),
        }

        if mode == "code_assist":
            cred_info["preview"] = summary.get("preview", True)
        else:
            cred_info["enable_credit"] = summary.get("enable_credit", False)

        matching_creds.append(cred_info)

    if filter_by_provider:
        total_count = len(matching_creds)
        creds_list = matching_creds[offset:offset + limit]
        stats = {
            "total": total_count,
            "normal": sum(1 for item in matching_creds if not item["disabled"]),
            "disabled": sum(1 for item in matching_creds if item["disabled"]),
        }
    else:
        total_count = result["total"]
        creds_list = matching_creds
        stats = result.get("stats", {"total": 0, "normal": 0, "disabled": 0})

    return JSONResponse(content={
        "items": creds_list,
        "total": total_count,
        "offset": offset,
        "limit": limit,
        "has_more": (offset + limit) < total_count,
        "stats": stats,
        "provider_filter": normalized_provider_filter,
        "deduplicated_count": dedupe_result.get("deleted_count", 0),
    })


async def download_all_creds_common(mode: str = "code_assist") -> Response:
    """Internal implementation detail."""
    mode = validate_mode(mode)
    zip_filename = "provider_credentials.zip" if mode == "primary" else "credentials.zip"

    await deduplicate_credentials_by_account_email(mode=mode)

    storage_adapter = await get_storage_adapter()
    credential_filenames = await storage_adapter.list_credentials(mode=mode)

    if not credential_filenames:
        raise HTTPException(status_code=404, detail="No credential files are available to download.")

    log.info(f"Packaging {len(credential_filenames)} {mode} credential files.")

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        success_count = 0
        for idx, filename in enumerate(credential_filenames, 1):
            try:
                credential_data = await storage_adapter.get_credential(filename, mode=mode)
                if credential_data:
                    content = json.dumps(credential_data, ensure_ascii=False, indent=2)
                    zip_file.writestr(os.path.basename(filename), content)
                    success_count += 1

                    if idx % 10 == 0:
                        log.debug(f"Packaging progress: {idx}/{len(credential_filenames)}")

            except Exception as e:
                log.warning(f"Error processing {mode} credential file {filename}: {e}")
                continue

    log.info(f"Credential package created with {success_count}/{len(credential_filenames)} files.")

    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={zip_filename}"},
    )


async def fetch_user_email_common(filename: str, mode: str = "code_assist") -> JSONResponse:
    """Internal implementation detail."""
    mode = validate_mode(mode)

    filename_only = os.path.basename(filename)
    if not filename_only.endswith(".json"):
        raise HTTPException(status_code=404, detail="Invalid file name.")

    storage_adapter = await get_storage_adapter()
    credential_data = await storage_adapter.get_credential(filename_only, mode=mode)
    if not credential_data:
        raise HTTPException(status_code=404, detail="Credential file does not exist.")

    email = await credential_manager.get_or_fetch_user_email(filename_only, mode=mode)

    if email:
        return JSONResponse(
            content={
                "filename": filename_only,
                "user_email": email,
                "message": "Retrieved user email.",
            }
        )
    else:
        return JSONResponse(
            content={
                "filename": filename_only,
                "user_email": None,
                "message": "Unable to retrieve user email. The credential may be expired or missing required permissions.",
            },
            status_code=400,
        )


async def refresh_all_user_emails_common(mode: str = "code_assist") -> JSONResponse:
    """Refreshes user emails for all credentials where they are missing."""
    mode = validate_mode(mode)

    storage_adapter = await get_storage_adapter()

    # Bulk fetch states for all credentials
    all_states = await storage_adapter.get_all_credential_states(mode=mode)

    results = []
    success_count = 0
    skipped_count = 0

    # Filter in memory for credentials that need emails
    for filename, state in all_states.items():
        try:
            cached_email = state.get("user_email")

            if cached_email:
                skipped_count += 1
                results.append({
                    "filename": os.path.basename(filename),
                    "user_email": cached_email,
                    "success": True,
                    "skipped": True,
                })
                continue

            email = await credential_manager.get_or_fetch_user_email(filename, mode=mode)
            if email:
                success_count += 1
                results.append({
                    "filename": os.path.basename(filename),
                    "user_email": email,
                    "success": True,
                })
            else:
                results.append({
                    "filename": os.path.basename(filename),
                    "user_email": None,
                    "success": False,
                "error": "Unable to retrieve email.",
                })
        except Exception as e:
            results.append({
                "filename": os.path.basename(filename),
                "user_email": None,
                "success": False,
                "error": str(e),
            })

    total_count = len(all_states)
    return JSONResponse(
        content={
            "success_count": success_count,
            "total_count": total_count,
            "skipped_count": skipped_count,
            "results": results,
            "message": f"Retrieved {success_count}/{total_count} email addresses; skipped {skipped_count} credentials with existing emails.",
        }
    )


async def deduplicate_credentials_by_email_common(mode: str = "code_assist") -> JSONResponse:
    """Batch deduplicate credential files by email, keeping the latest expiry."""
    mode = validate_mode(mode)

    try:
        dedupe_result = await deduplicate_credentials_by_account_email(mode=mode)
        duplicate_groups = dedupe_result.get("duplicate_groups", [])
        total_count = dedupe_result.get("total_count", 0)

        if not duplicate_groups:
            return JSONResponse(
                content={
                    "deleted_count": 0,
                    "kept_count": total_count,
                    "total_count": total_count,
                    "unique_emails_count": dedupe_result.get("unique_emails_count", 0),
                    "no_email_count": dedupe_result.get("no_email_count", 0),
                    "duplicate_groups": [],
                    "delete_errors": [],
                    "message": "No duplicate credentials with the same email were found.",
                }
            )

        deleted_count = dedupe_result.get("deleted_count", 0)
        kept_count = dedupe_result.get("kept_count", total_count - deleted_count)
        result_duplicate_groups = [
            {
                "email": group["email"],
                "kept_file": os.path.basename(group["kept_file"]),
                "deleted_files": [os.path.basename(filename) for filename in group.get("deleted_files", [])],
                "duplicate_count": group.get("duplicate_count", len(group.get("deleted_files", []))),
            }
            for group in duplicate_groups
        ]

        return JSONResponse(
            content={
                "deleted_count": deleted_count,
                "kept_count": kept_count,
                "total_count": total_count,
                "unique_emails_count": dedupe_result.get("unique_emails_count", 0),
                "no_email_count": dedupe_result.get("no_email_count", 0),
                "duplicate_groups": result_duplicate_groups,
                "delete_errors": [],
                "message": f"Deduplication complete: deleted {deleted_count} duplicate credentials and kept {kept_count} credentials ({dedupe_result.get('unique_emails_count', 0)} unique emails).",
            }
        )

    except Exception as e:
        log.error(f"Error occurred while deduplicating credentials in batch: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "deleted_count": 0,
                "kept_count": 0,
                "total_count": 0,
                "message": f"Deduplication failed: {str(e)}",
            }
        )


async def verify_credential_project_common(filename: str, mode: str = "code_assist") -> JSONResponse:
    """Internal implementation detail."""
    mode = validate_mode(mode)


    if not filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Invalid file name.")


    storage_adapter = await get_storage_adapter()


    credential_data = await storage_adapter.get_credential(filename, mode=mode)
    if not credential_data:
        raise HTTPException(status_code=404, detail="Credential does not exist.")

    provider_id = get_credential_provider(credential_data)
    if mode == "primary" and provider_id == GOOGLE_AI_STUDIO:
        try:
            validation = await validate_api_key(str(credential_data.get("api_key") or ""))
        except GoogleAIStudioError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "filename": filename,
                    "provider": provider_id,
                    "message": str(exc),
                },
            )

        credential_data["model_ids"] = validation.model_ids
        await storage_adapter.store_credential(filename, credential_data, mode=mode)
        await storage_adapter.update_credential_state(
            filename,
            {"disabled": False, "error_codes": [], "error_messages": {}},
            mode=mode,
        )
        return JSONResponse(
            content={
                "success": True,
                "filename": filename,
                "provider": provider_id,
                "model_count": validation.model_count,
                "message": (
                    "Google AI Studio API key verified. Provider metadata was "
                    "refreshed, the credential was enabled, and recorded errors were cleared."
                ),
            }
        )


    credentials = Credentials.from_dict(credential_data)


    token_refreshed = await credentials.refresh_if_needed()


    if token_refreshed:
        log.info(f"Token automatically refreshed: {filename} (mode = {mode})")
        credential_data = credentials.to_dict()
        await storage_adapter.store_credential(filename, credential_data, mode=mode)


    if mode == "primary":
        api_base_url = await get_antigravity_api_url()
        user_agent = await get_antigravity_user_agent()
        project_id, subscription_tier, credit_amount = await fetch_project_id_and_tier(
            access_token=credentials.access_token,
            user_agent=user_agent,
            api_base_url=api_base_url,
            include_credits=True,
        )
    else:

        credit_amount = None
        subscription_tier = None
        user_projects = await get_user_projects(credentials)
        if user_projects:
            if len(user_projects) == 1:
                project_id = user_projects[0].get("projectId")
            else:
                project_id = await select_default_project(user_projects)
        else:
            project_id = None

        if project_id:
            log.info(f"Enabling required API services for project {project_id}.")
            try:
                await enable_required_apis(credentials, project_id)
            except Exception as e:
                log.warning(f"Failed to enable API service: {e}")

    if project_id:
        credential_data["project_id"] = project_id

    if project_id or subscription_tier:
        await storage_adapter.store_credential(filename, credential_data, mode=mode)


        state_update = {
            "disabled": False,
            "error_codes": []
        }


        state_update["tier"] = subscription_tier


        if mode == "code_assist":
            state_update["preview"] = True

        await storage_adapter.update_credential_state(filename, state_update, mode=mode)

        log.info(f"Verified {mode} credential: {filename}. Project ID: {project_id}. Tier: {subscription_tier}. Disabled status removed and error codes cleared.")

        response_data = {
            "success": True,
            "filename": filename,
            "project_id": project_id,
            "subscription_tier": subscription_tier,
            "message": "Verification complete. Project ID was updated, the credential was re-enabled, and recorded error codes were cleared."
        }

        if mode == "primary" and credit_amount is not None:
            response_data["credit_amount"] = credit_amount

        return JSONResponse(content=response_data)
    else:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "filename": filename,
                "message": "Verification failed. Unable to retrieve a Project ID. Check whether the credential is still valid."
            }
        )


# =============================================================================

# =============================================================================


@router.post("/upload")
async def upload_credentials(
    files: List[UploadFile] = File(...),
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)
        return await upload_credentials_common(files, mode=mode)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Batch upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)
        return await get_creds_status_common(
            offset, limit, status_filter, mode=mode,
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
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detail/{filename}")
async def get_cred_detail(
    filename: str,
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)

        if not filename.endswith(".json"):
            raise HTTPException(status_code=400, detail="Invalid file name.")



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

        if backend_type == "file" and os.path.exists(filename):
            result.update({
                "size": os.path.getsize(filename),
                "modified_time": os.path.getmtime(filename),
            })

        return JSONResponse(content=result)

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve credential details {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/action")
async def creds_action(
    request: CredFileActionRequest,
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)

        log.info(f"Received request: {request}")

        filename = request.filename
        action = request.action

        log.info(f"Performing action '{action}' on file: {filename} (mode={mode})")


        if not filename.endswith(".json"):
            log.error(f"Invalid filename: {filename} (not a .json file)")
            raise HTTPException(status_code=400, detail=f"Invalid file name: {filename}")


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
                return JSONResponse(content={"message": f"Enabled credential {os.path.basename(filename)}."})
            else:
                log.error(f"Web request: File {filename} enable failed (mode = {mode})")
                raise HTTPException(status_code=500, detail="Failed to enable the credential. It may no longer exist.")

        elif action == "disable":
            log.info(f"Web request: Disable file {filename} (mode = {mode})")
            result = await credential_manager.set_cred_disabled(filename, True, mode=mode)
            log.info(f"[WebRoute] set_cred_disabled result: {result}")
            if result:
                log.info(f"Web request: credential {filename} disabled (mode = {mode}).")
                return JSONResponse(content={"message": f"Disabled credential {os.path.basename(filename)}."})
            else:
                log.error(f"Web request: file {filename} disable failed (mode = {mode})")
                raise HTTPException(status_code=500, detail="Failed to disable the credential. It may no longer exist.")

        elif action == "delete":
            try:
                # Use CredentialManager to delete credential (synced queue/state)
                success = await credential_manager.remove_credential(filename, mode=mode)
                if success:
                    log.info(f"Deleted credential via manager: {filename} (mode={mode}).")
                    return JSONResponse(
                        content={"message": f"Deleted credential {os.path.basename(filename)}."}
                    )
                else:
                    raise HTTPException(status_code=500, detail="Failed to delete the credential.")
            except Exception as e:
                log.error(f"Error deleting credential {filename}: {e}")
                raise HTTPException(status_code=500, detail=f"Failed to delete the credential: {str(e)}")

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
                return JSONResponse(content={"message": f"Enabled credit mode for {os.path.basename(filename)}."})
            raise HTTPException(status_code=500, detail="Failed to enable credit mode. The credential may no longer exist.")

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
                return JSONResponse(content={"message": f"Disabled credit mode for {os.path.basename(filename)}."})
            raise HTTPException(status_code=500, detail="Failed to disable credit mode. The credential may no longer exist.")

        else:
            raise HTTPException(status_code=400, detail="Invalid credential action.")

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Credential file operation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-action")
async def creds_batch_action(
    request: CredFileBatchActionRequest,
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)

        action = request.action
        filenames = request.filenames

        if not filenames:
            raise HTTPException(status_code=400, detail="Select at least one credential file before running a batch action.")

        log.info(f"Performing batch operation on {len(filenames)} files with action: {action}")

        success_count = 0
        errors = []

        storage_adapter = await get_storage_adapter()

        for filename in filenames:
            try:
                # Validate filename safety
                if not filename.endswith(".json"):
                    errors.append(f"{filename}: invalid file type")
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
                        delete_success = await credential_manager.remove_credential(filename, mode=mode)
                        if delete_success:
                            success_count += 1
                            log.info(f"Deleted credential from batch: {filename}.")
                        else:
                            errors.append(f"{filename}: delete failed")
                            continue
                    except Exception as e:
                        errors.append(f"{filename}: delete failed - {str(e)}")
                        continue
                elif action == "enable_credit":
                    if mode != "primary" or get_credential_provider(credential_data) != GOOGLE_ANTIGRAVITY:
                        errors.append(
                            f"{filename}: credit mode is only available for Google Antigravity credentials"
                        )
                        continue
                    updated = await storage_adapter.update_credential_state(
                        filename, {"enable_credit": True}, mode=mode
                    )
                    if updated:
                        await clear_all_model_cooldowns_for_credential(storage_adapter, filename, mode)
                        success_count += 1
                    else:
                        errors.append(f"{filename}: failed to enable credit mode")
                        continue
                elif action == "disable_credit":
                    if mode != "primary" or get_credential_provider(credential_data) != GOOGLE_ANTIGRAVITY:
                        errors.append(
                            f"{filename}: credit mode is only available for Google Antigravity credentials"
                        )
                        continue
                    updated = await storage_adapter.update_credential_state(
                        filename, {"enable_credit": False}, mode=mode
                    )
                    if updated:
                        await clear_all_model_cooldowns_for_credential(storage_adapter, filename, mode)
                        success_count += 1
                    else:
                        errors.append(f"{filename}: failed to disable credit mode")
                        continue
                else:
                    errors.append(f"{filename}: invalid credential action")
                    continue

            except Exception as e:
                log.error(f"Error processing {filename}: {e}")
                errors.append(f"{filename}: processing failed - {str(e)}")
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

        return JSONResponse(content=response_data)

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Batch credential file operation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{filename}")
async def download_cred_file(
    filename: str,
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)

        if not filename.endswith(".json"):
            raise HTTPException(status_code=404, detail="Invalid file name.")


        storage_adapter = await get_storage_adapter()


        credential_data = await storage_adapter.get_credential(filename, mode=mode)
        if not credential_data:
            raise HTTPException(status_code=404, detail="Credential file does not exist.")


        content = json.dumps(credential_data, ensure_ascii=False, indent=2)

        from fastapi.responses import Response

        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to download credential file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-email/{filename}")
async def fetch_user_email(
    filename: str,
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)
        return await fetch_user_email_common(filename, mode=mode)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve user email: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-all-emails")
async def refresh_all_user_emails(
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)
        return await refresh_all_user_emails_common(mode=mode)
    except Exception as e:
        log.error(f"Failed to retrieve user emails in batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deduplicate-by-email")
async def deduplicate_credentials_by_email(
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)
        return await deduplicate_credentials_by_email_common(mode=mode)
    except Exception as e:
        log.error(f"Failed to deduplicate credentials in batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download-all")
async def download_all_creds(
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)
        return await download_all_creds_common(mode=mode)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to download package: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-project/{filename}")
async def verify_credential_project(
    filename: str,
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)
        return await verify_credential_project_common(filename, mode=mode)
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to verify credential Project ID {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@router.get("/errors/{filename}")
async def get_credential_errors(
    filename: str,
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)


        if not filename.endswith(".json"):
            raise HTTPException(status_code=400, detail="Invalid file name.")

        storage_adapter = await get_storage_adapter()


        if not hasattr(storage_adapter._backend, 'get_credential_errors'):
            raise HTTPException(
                status_code=501,
            detail="The current storage backend does not support retrieving credential error messages."
            )


        error_info = await storage_adapter._backend.get_credential_errors(filename, mode=mode)

        return JSONResponse(content=error_info)

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve credential error information {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quota/{filename}")
async def get_credential_quota(
    filename: str,
    token: str = Depends(verify_panel_token),
    mode: str = "provider"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)

        if not filename.endswith(".json"):
            raise HTTPException(status_code=400, detail="Invalid file name.")


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
            raise HTTPException(status_code=400, detail="Credential does not contain an access token.")


        quota_info = await fetch_quota_info(access_token)

        if quota_info.get("success"):
            return JSONResponse(content={
                "success": True,
                "filename": filename,
                "models": quota_info.get("models", {})
            })
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "filename": filename,
                    "error": quota_info.get("error", "Unknown error.")
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to retrieve credential quota {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve quota details: {str(e)}")


@router.post("/configure-preview/{filename}")
async def configure_preview_channel(
    filename: str,
    token: str = Depends(verify_panel_token),
    mode: str = "code_assist"
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)


        if mode != "code_assist":
            raise HTTPException(
                status_code=400,
                detail="The Preview channel can only be configured for Code Assist credentials."
            )


        if not filename.endswith(".json"):
            raise HTTPException(status_code=400, detail="Invalid file name.")

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
            raise HTTPException(status_code=400, detail="Credential does not contain an access token.")
        if not project_id:
            raise HTTPException(status_code=400, detail="Credential does not contain a Project ID.")





        from core.httpx_client import post_async
        import uuid


        setting_id = f"preview-setting-{uuid.uuid4().hex[:8]}"
        binding_id = f"preview-binding-{uuid.uuid4().hex[:8]}"

        base_url = f"https://cloudaicompanion.googleapis.com/v1/projects/{project_id}/locations/global"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        log.info(f"Starting configuration of preview channel: {filename} (project_id={project_id})")


        setting_url = f"{base_url}/releaseChannelSettings"
        setting_response = await post_async(
            url=setting_url,
            json={"release_channel": "EXPERIMENTAL"},
            headers=headers,
            params={"release_channel_setting_id": setting_id},
            timeout=30.0
        )

        setting_status = setting_response.status_code





        from core.httpx_client import post_async, get_async
        import uuid


        setting_id = f"preview-setting-{uuid.uuid4().hex[:8]}"
        binding_id = f"preview-binding-{uuid.uuid4().hex[:8]}"

        base_url = f"https://cloudaicompanion.googleapis.com/v1/projects/{project_id}/locations/global"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        log.info(f"Starting configuration of preview channel: {filename} (project_id={project_id})")


        setting_url = f"{base_url}/releaseChannelSettings"
        setting_response = await post_async(
            url=setting_url,
            json={"release_channel": "EXPERIMENTAL"},
            headers=headers,
            params={"release_channel_setting_id": setting_id},
            timeout=30.0
        )

        setting_status = setting_response.status_code

        if setting_status == 200 or setting_status == 201:
            log.info(f"Step 1/2: Release channel setting created (setting_id={setting_id}).")
        elif setting_status == 409:

            log.info("Step 1/2: Release channel setting already exists; retrieving the existing setting ID.")
            list_response = await get_async(
                url=setting_url,
                headers=headers,
                timeout=30.0
            )
            if list_response.status_code == 200:
                try:
                    list_data = list_response.json()
                    settings = list_data.get("releaseChannelSettings", [])
                    if settings:
                        existing_name = settings[0].get("name", "")
                        setting_id = existing_name.split("/")[-1]
                        log.info(f"Step 1/2: Retrieved existing setting_id={setting_id}")
                    else:
                        log.warning("Step 1/2: the list response was empty; keeping the generated setting ID.")
                except Exception as e:
                    log.warning(f"Step 1/2: failed to parse the list response: {e}. Keeping the generated setting ID.")
            else:
                log.warning(f"Step 1/2: list request failed (status={list_response.status_code}); keeping the generated setting ID.")
        else:

            error_text = setting_response.text if hasattr(setting_response, 'text') else ""
            log.error(f"Step 1/2 failed: {filename} - Status: {setting_status}, Error: {error_text}")

            return JSONResponse(
                status_code=setting_status,
                content={
                    "success": False,
                    "filename": filename,
                    "preview": False,
                    "message": f"Failed to create Release Channel Setting: HTTP {setting_status}",
                    "error": error_text,
                    "step": "create_setting"
                }
            )

        # Step 2: Create Setting Binding (bind to project)
        binding_url = f"{base_url}/releaseChannelSettings/{setting_id}/settingBindings"
        binding_response = await post_async(
            url=binding_url,
            json={
                "target": f"projects/{project_id}",
                "product": "GEMINI_CODE_ASSIST"
            },
            headers=headers,
            params={"setting_binding_id": binding_id},
            timeout=30.0
        )

        binding_status = binding_response.status_code

        if binding_status == 200 or binding_status == 201:
            await storage_adapter.update_credential_state(filename, {
                "preview": True
            }, mode=mode)

            log.info(f"Step 2/2: Setting binding created. Preview channel configuration completed for {filename}.")

            return JSONResponse(content={
                "success": True,
                "filename": filename,
                "preview": True,
                "message": "Preview channel configured, and Preview mode is now enabled.",
                "setting_id": setting_id,
                "binding_id": binding_id
            })
        elif binding_status == 409:
            # Binding already exists, meaning it was configured already
            await storage_adapter.update_credential_state(filename, {
                "preview": True
            }, mode=mode)

            log.info(f"Step 2/2: Setting Binding already exists - Preview channel is configured: {filename}")

            return JSONResponse(content={
                "success": True,
                "filename": filename,
                "preview": True,
                "message": "Preview channel configuration already exists, and preview mode is enabled."
            })
        else:
            # Step 2 failed
            error_text = binding_response.text if hasattr(binding_response, 'text') else ""
            log.error(f"Step 2/2 failed: {filename} - Status: {binding_status}, Error: {error_text}")

            return JSONResponse(
                status_code=binding_status,
                content={
                    "success": False,
                    "filename": filename,
                    "preview": False,
                    "message": f"Failed to create Setting Binding: HTTP {binding_status}",
                    "error": error_text,
                    "step": "create_binding"
                }
            )

    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Failed to configure preview channel {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Configuration failed: {str(e)}")


@router.post("/test/{filename}")
async def test_credential(
    filename: str,
    mode: str = "code_assist",
    _token: str = Depends(verify_panel_token)
):
    """Internal implementation detail."""
    try:
        mode = validate_mode(mode)


        if not filename.endswith(".json"):
            raise HTTPException(status_code=400, detail="Invalid file name.")

        storage_adapter = await get_storage_adapter()


        credential_data = await storage_adapter.get_credential(filename, mode=mode)
        if not credential_data:
            raise HTTPException(status_code=404, detail="Credential does not exist.")


        from core.httpx_client import post_async
        provider_id = get_credential_provider(credential_data)
        available_models = credential_data.get("model_ids") or []
        test_model = (
            "gemini-2.5-flash"
            if "gemini-2.5-flash" in available_models or not available_models
            else str(available_models[0])
        )

        test_request = {
            "contents": [{"role": "user", "parts": [{"text": "hi"}]}],
            "generationConfig": {"maxOutputTokens": 1}
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
            url=request_url,
            json=request_body,
            headers=headers,
            timeout=30.0
        )


        status_code = response.status_code

        if status_code == 200 or status_code == 429:
            log.info(f"Credential test successful: {filename} (mode={mode}, model={test_model}, status={status_code})")

            if status_code == 200:
                await storage_adapter.update_credential_state(filename, {
                    "error_codes": [],
                    "error_messages": {}
                }, mode=mode)


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
                                    "generationConfig": {"maxOutputTokens": 1}
                                }
                            },
                            headers=headers,
                            timeout=30.0
                        )

                        preview_status = preview_response.status_code

                        if preview_status == 200 or preview_status == 429:

                            log.info(f"Preview model test passed: {filename} (status = {preview_status}).")
                            await storage_adapter.update_credential_state(filename, {
                                "preview": True
                            }, mode=mode)
                        elif preview_status == 404:

                            log.warning(f"Preview model is not supported for {filename} (status = 404)")
                            await storage_adapter.update_credential_state(filename, {
                                "preview": False
                            }, mode=mode)
                        else:

                            log.warning(f"Preview model test failed: {filename} (status = {preview_status})")
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
                }
            )
        else:
            log.warning(f"Credential test failed: {filename} (mode={mode}, status={status_code})")

            try:
                error_text = response.text if hasattr(response, 'text') else ""


                log.error(f"Credential test error details - file: {filename}, mode: {mode}, status code: {status_code}, error: {error_text}")


                error_codes = [status_code]
                error_messages = {str(status_code): error_text if error_text else f"HTTP {status_code}"}


                await storage_adapter.update_credential_state(filename, {
                    "error_codes": error_codes,
                    "error_messages": error_messages
                }, mode=mode)

                log.info(f"Saved test error info: {filename} - error code {status_code}")
            except Exception as e:
                log.error(f"Failed to save test error message: {e}")


        error_text = response.text if hasattr(response, 'text') else ""

        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "status_code": status_code,
                "message": f"Test failed: HTTP {status_code}",
                "error": error_text,
                "filename": filename
            }
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
                "error": str(e),
                "detail": f"Test failed: {str(e)}",
                "filename": filename,
            }
        )
