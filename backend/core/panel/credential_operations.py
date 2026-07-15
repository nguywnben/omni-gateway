import asyncio
import io
import json
import os
import stat
import zipfile
from typing import Any, List

from config import (
    get_antigravity_api_url,
    get_antigravity_user_agent,
)
from core.credential_manager import credential_manager
from core.credential_pool import (
    deduplicate_credentials_by_account_email,
    get_known_credential_email,
    parse_credential_expiry,
    resolve_credential_email,
)
from core.google_ai_studio import (
    GoogleAIStudioError,
    validate_api_key,
)
from core.google_oauth_api import (
    Credentials,
    enable_required_apis,
    fetch_project_id_and_tier,
    get_user_projects,
    select_default_project,
)
from core.pool_import import (
    MAX_POOL_ARCHIVE_BYTES,
    MAX_POOL_ARCHIVE_ENTRIES,
    MAX_POOL_ENTRY_BYTES,
    MAX_POOL_UNCOMPRESSED_BYTES,
)
from core.provider_registry import (
    GOOGLE_AI_STUDIO,
    GOOGLE_ANTIGRAVITY,
    XAI,
    canonicalize_antigravity_credential_filename,
    get_credential_provider,
    get_declared_credential_models,
    normalize_provider_id,
)
from core.storage_adapter import get_storage_adapter
from core.xai import XaiError, fetch_xai_model_ids, refresh_xai_oauth_credential
from fastapi import HTTPException, Response, UploadFile
from fastapi.responses import JSONResponse
from log import log

from .utils import INTERNAL_SERVER_ERROR_DETAIL, validate_credential_filename, validate_mode


def _zip_entry_is_symlink(entry: zipfile.ZipInfo) -> bool:
    file_mode = (entry.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(file_mode)


async def extract_json_files_from_zip(zip_file: UploadFile) -> List[dict]:
    try:
        zip_content = await zip_file.read(MAX_POOL_ARCHIVE_BYTES + 1)
        if len(zip_content) > MAX_POOL_ARCHIVE_BYTES:
            raise HTTPException(status_code=400, detail="ZIP archive exceeds the 10 MB limit.")

        files_data = []
        extracted_bytes = 0

        with zipfile.ZipFile(io.BytesIO(zip_content), "r") as zip_ref:
            entries = [entry for entry in zip_ref.infolist() if not entry.is_dir()]
            if len(entries) > MAX_POOL_ARCHIVE_ENTRIES:
                raise HTTPException(
                    status_code=400,
                    detail=f"ZIP archive contains more than {MAX_POOL_ARCHIVE_ENTRIES} files.",
                )
            json_files = [
                entry
                for entry in entries
                if entry.filename.lower().endswith(".json")
                and not entry.filename.startswith("__MACOSX/")
            ]

            if not json_files:
                raise HTTPException(
                    status_code=400, detail="No JSON files were found in the ZIP archive."
                )

            declared_size = sum(entry.file_size for entry in json_files)
            if declared_size > MAX_POOL_UNCOMPRESSED_BYTES:
                raise HTTPException(
                    status_code=400,
                    detail="ZIP archive exceeds the 25 MB uncompressed limit.",
                )

            log.info(f"Found {len(json_files)} JSON files in an uploaded ZIP archive.")

            for entry in json_files:
                json_filename = entry.filename
                try:
                    if entry.flag_bits & 0x1:
                        raise HTTPException(
                            status_code=400,
                            detail="Encrypted ZIP entries are not supported.",
                        )
                    if _zip_entry_is_symlink(entry):
                        raise HTTPException(
                            status_code=400,
                            detail="Symbolic-link ZIP entries are not supported.",
                        )
                    if entry.file_size > MAX_POOL_ENTRY_BYTES:
                        raise HTTPException(
                            status_code=400,
                            detail="Credential file exceeds the 2 MB limit.",
                        )

                    with zip_ref.open(entry) as json_file:
                        content = json_file.read(MAX_POOL_ENTRY_BYTES + 1)
                    if len(content) > MAX_POOL_ENTRY_BYTES:
                        raise HTTPException(
                            status_code=400,
                            detail="Credential file exceeds the 2 MB limit.",
                        )
                    extracted_bytes += len(content)
                    if extracted_bytes > MAX_POOL_UNCOMPRESSED_BYTES:
                        raise HTTPException(
                            status_code=400,
                            detail="ZIP archive exceeds the 25 MB uncompressed limit.",
                        )

                    try:
                        content_str = content.decode("utf-8")
                    except UnicodeDecodeError:
                        log.warning(f"Skipping ZIP entry with invalid UTF-8: {json_filename}")
                        continue

                    filename = os.path.basename(json_filename.replace("\\", "/"))
                    files_data.append({"filename": filename, "content": content_str})

                except HTTPException:
                    raise
                except Exception as e:
                    log.warning(f"Error processing file {json_filename} in ZIP: {e}")
                    continue

        log.info(f"Extracted {len(files_data)} valid JSON files from the ZIP archive.")
        return files_data

    except HTTPException:
        raise
    except zipfile.BadZipFile as exc:
        raise HTTPException(status_code=400, detail="Invalid ZIP file format.") from exc
    except Exception as e:
        log.error(f"Failed to process ZIP file: {e}")
        raise HTTPException(status_code=500, detail="Failed to process ZIP archive.") from e


async def clear_all_model_cooldowns_for_credential(
    storage_adapter: Any,
    filename: str,
    mode: str,
) -> None:
    try:
        cleared = await storage_adapter._backend.clear_all_model_cooldowns(filename, mode=mode)
        if not cleared:
            log.warning(
                f"Failed to clear model cooldowns or credential does not exist: {filename} (mode={mode})"
            )
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
        try:
            filename = validate_credential_filename(os.path.basename(file_data["filename"]))
        except HTTPException as exc:
            immediate_results.append(
                {
                    "filename": "Invalid credential file",
                    "status": "error",
                    "message": f"{exc.detail}",
                }
            )
            continue
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
    mode = validate_mode(mode)

    if not files:
        raise HTTPException(status_code=400, detail="Please select files to upload.")

    if len(files) > 100:
        raise HTTPException(
            status_code=400,
            detail=f"Too many files. A maximum of 100 files is supported; current count: {len(files)}.",
        )

    files_data = []
    uploaded_bytes = 0
    for file in files:
        upload_name = os.path.basename(str(file.filename or "").replace("\\", "/"))
        normalized_name = upload_name.lower()
        if normalized_name.endswith(".zip"):
            zip_files_data = await extract_json_files_from_zip(file)
            uploaded_bytes += sum(len(item["content"].encode("utf-8")) for item in zip_files_data)
            files_data.extend(zip_files_data)
            log.info(f"Extracted {len(zip_files_data)} JSON files from an uploaded ZIP archive.")

        elif normalized_name.endswith(".json"):
            content = await file.read(MAX_POOL_ENTRY_BYTES + 1)
            if len(content) > MAX_POOL_ENTRY_BYTES:
                raise HTTPException(
                    status_code=400,
                    detail=f"Credential file '{upload_name}' exceeds the 2 MB limit.",
                )
            try:
                content_str = content.decode("utf-8")
            except UnicodeDecodeError:
                raise HTTPException(
                    status_code=400, detail=f"File '{file.filename}' encoding is not supported."
                )

            uploaded_bytes += len(content)
            files_data.append({"filename": upload_name, "content": content_str})
        else:
            raise HTTPException(
                status_code=400,
                detail=f"File format '{upload_name}' is not supported. Only JSON and ZIP files are supported.",
            )

        if len(files_data) > MAX_POOL_ARCHIVE_ENTRIES:
            raise HTTPException(
                status_code=400,
                detail=f"Upload contains more than {MAX_POOL_ARCHIVE_ENTRIES} credential files.",
            )
        if uploaded_bytes > MAX_POOL_UNCOMPRESSED_BYTES:
            raise HTTPException(
                status_code=400,
                detail="Upload exceeds the 25 MB uncompressed limit.",
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
                    write_result = await credential_manager.add_primary_credential(
                        filename, credential_data
                    )
                else:
                    write_result = await credential_manager.add_credential(
                        filename, credential_data
                    )

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
                    "message": write_result.get("message")
                    or ("Credential imported." if stored else "Credential skipped."),
                }

            except Exception:
                return {
                    "filename": file_data["filename"],
                    "status": "error",
                    "message": "Credential processing failed.",
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
                        "message": "Credential processing failed.",
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
        raise HTTPException(
            status_code=400, detail=f"No {mode_label} credential files were imported."
        )


async def get_creds_status_common(
    offset: int,
    limit: int,
    status_filter: str,
    mode: str = "code_assist",
    error_code_filter: str = None,
    cooldown_filter: str = None,
    preview_filter: str = None,
    tier_filter: str = None,
    provider_filter: str = None,
) -> JSONResponse:
    mode = validate_mode(mode)

    if offset < 0:
        raise HTTPException(status_code=400, detail="Offset must be greater than or equal to 0.")
    if limit not in [20, 50, 100, 200, 500, 1000]:
        raise HTTPException(status_code=400, detail="Limit must be 20, 50, 100, 200, 500, or 1000.")
    if status_filter not in ["all", "enabled", "disabled"]:
        raise HTTPException(
            status_code=400, detail="Status filter must be all, enabled, or disabled."
        )
    if cooldown_filter and cooldown_filter not in ["all", "in_cooldown", "no_cooldown"]:
        raise HTTPException(
            status_code=400, detail="Cooldown filter must be all, in_cooldown, or no_cooldown."
        )
    if preview_filter and preview_filter not in ["all", "preview", "no_preview"]:
        raise HTTPException(
            status_code=400, detail="Preview filter must be all, preview, or no_preview."
        )
    if tier_filter and tier_filter not in ["all", "free", "pro", "ultra"]:
        raise HTTPException(status_code=400, detail="Tier filter must be all, free, pro, or ultra.")

    normalized_provider_filter = "all"
    credential_type_filter = ""
    raw_provider_filter = str(provider_filter or "all").strip().lower()
    if raw_provider_filter != "all":
        if raw_provider_filter in {"grok", "xai_oauth"}:
            normalized_provider_filter = XAI
            credential_type_filter = "oauth"
        elif raw_provider_filter in {"xai_console", "xai_api_key"}:
            normalized_provider_filter = XAI
            credential_type_filter = "api_key"
        else:
            normalized_provider_filter = normalize_provider_id(provider_filter)
        if mode != "primary" or normalized_provider_filter not in {
            GOOGLE_ANTIGRAVITY,
            GOOGLE_AI_STUDIO,
            XAI,
        }:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Provider filter must be all, google_antigravity, google_ai_studio, "
                    "grok, xai_console, or xai."
                ),
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
        error_code_filter=error_code_filter
        if error_code_filter and error_code_filter != "all"
        else None,
        cooldown_filter=cooldown_filter if cooldown_filter and cooldown_filter != "all" else None,
        preview_filter=preview_filter if preview_filter and preview_filter != "all" else None,
        tier_filter=tier_filter if tier_filter and tier_filter != "all" else None,
    )

    matching_creds = []
    for summary in result["items"]:
        filename = os.path.basename(summary["filename"])
        credential_data = await storage_adapter.get_credential(filename, mode=mode) or {}
        provider_id = get_credential_provider(credential_data)
        if filter_by_provider and provider_id != normalized_provider_filter:
            continue
        if (
            credential_type_filter
            and str(credential_data.get("credential_type") or "oauth").strip().lower()
            != credential_type_filter
        ):
            continue
        cred_info = {
            "filename": filename,
            "user_email": summary["user_email"],
            "credential_label": credential_data.get("credential_label"),
            "credential_type": credential_data.get("credential_type", "oauth"),
            "provider": provider_id,
            "model_count": len(get_declared_credential_models(credential_data)),
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
        creds_list = matching_creds[offset : offset + limit]
        stats = {
            "total": total_count,
            "normal": sum(1 for item in matching_creds if not item["disabled"]),
            "disabled": sum(1 for item in matching_creds if item["disabled"]),
        }
    else:
        total_count = result["total"]
        creds_list = matching_creds
        stats = result.get("stats", {"total": 0, "normal": 0, "disabled": 0})

    return JSONResponse(
        content={
            "items": creds_list,
            "total": total_count,
            "offset": offset,
            "limit": limit,
            "has_more": (offset + limit) < total_count,
            "stats": stats,
            "provider_filter": raw_provider_filter,
            "deduplicated_count": dedupe_result.get("deleted_count", 0),
        }
    )


async def _get_download_filename(
    storage_adapter,
    filename: str,
    credential_data: dict,
    mode: str,
) -> str:
    download_filename = os.path.basename(filename)
    if mode != "primary" or get_credential_provider(credential_data) != GOOGLE_ANTIGRAVITY:
        return download_filename

    email = get_known_credential_email(credential_data)
    if not email:
        try:
            state = await storage_adapter.get_credential_state(filename, mode=mode)
            email = str(state.get("user_email") or "").strip().lower()
        except Exception:
            email = ""
    return canonicalize_antigravity_credential_filename(
        download_filename,
        credential_data,
        email=email,
    )


async def download_all_creds_common(mode: str = "code_assist") -> Response:
    mode = validate_mode(mode)
    zip_filename = "provider_credentials.zip" if mode == "primary" else "credentials.zip"

    await deduplicate_credentials_by_account_email(mode=mode)

    storage_adapter = await get_storage_adapter()
    credential_filenames = await storage_adapter.list_credentials(mode=mode)

    if not credential_filenames:
        raise HTTPException(
            status_code=404, detail="No credential files are available to download."
        )

    log.info(f"Packaging {len(credential_filenames)} {mode} credential files.")

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        success_count = 0
        archive_names = set()
        for idx, filename in enumerate(credential_filenames, 1):
            try:
                credential_data = await storage_adapter.get_credential(filename, mode=mode)
                if credential_data:
                    content = json.dumps(credential_data, ensure_ascii=False, indent=2)
                    download_filename = await _get_download_filename(
                        storage_adapter,
                        filename,
                        credential_data,
                        mode,
                    )
                    candidate_name = download_filename
                    stem, extension = os.path.splitext(candidate_name)
                    suffix = 2
                    while download_filename in archive_names:
                        download_filename = f"{stem}-{suffix}{extension}"
                        suffix += 1
                    archive_names.add(download_filename)
                    zip_file.writestr(download_filename, content)
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
    mode = validate_mode(mode)

    filename_only = validate_credential_filename(filename)

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
                results.append(
                    {
                        "filename": os.path.basename(filename),
                        "user_email": cached_email,
                        "success": True,
                        "skipped": True,
                    }
                )
                continue

            email = await credential_manager.get_or_fetch_user_email(filename, mode=mode)
            if email:
                success_count += 1
                results.append(
                    {
                        "filename": os.path.basename(filename),
                        "user_email": email,
                        "success": True,
                    }
                )
            else:
                results.append(
                    {
                        "filename": os.path.basename(filename),
                        "user_email": None,
                        "success": False,
                        "error": "Unable to retrieve email.",
                    }
                )
        except Exception:
            results.append(
                {
                    "filename": os.path.basename(filename),
                    "user_email": None,
                    "success": False,
                    "error": "Unable to retrieve email.",
                }
            )

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
                "deleted_files": [
                    os.path.basename(filename) for filename in group.get("deleted_files", [])
                ],
                "duplicate_count": group.get(
                    "duplicate_count", len(group.get("deleted_files", []))
                ),
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
                "message": INTERNAL_SERVER_ERROR_DETAIL,
            },
        )


async def verify_credential_project_common(
    filename: str, mode: str = "code_assist"
) -> JSONResponse:
    mode = validate_mode(mode)
    filename = validate_credential_filename(filename)

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

    if mode == "primary" and provider_id == XAI:
        try:
            if str(credential_data.get("credential_type") or "").lower() == "oauth":
                credential_data = await refresh_xai_oauth_credential(credential_data)
            access_token = (
                credential_data.get("api_key")
                or credential_data.get("access_token")
                or credential_data.get("token")
            )
            model_ids = await fetch_xai_model_ids(str(access_token or ""))
        except XaiError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "success": False,
                    "filename": filename,
                    "provider": provider_id,
                    "message": str(exc),
                },
            )
        credential_data["model_ids"] = model_ids
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
                "model_count": len(model_ids),
                "message": (
                    "xAI credential verified. Available models were refreshed, the credential "
                    "was enabled, and recorded errors were cleared."
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

        state_update = {"disabled": False, "error_codes": []}

        state_update["tier"] = subscription_tier

        if mode == "code_assist":
            state_update["preview"] = True

        await storage_adapter.update_credential_state(filename, state_update, mode=mode)

        log.info(
            f"Verified {mode} credential: {filename}. Project ID: {project_id}. Tier: {subscription_tier}. Disabled status removed and error codes cleared."
        )

        response_data = {
            "success": True,
            "filename": filename,
            "project_id": project_id,
            "subscription_tier": subscription_tier,
            "message": "Verification complete. Project ID was updated, the credential was re-enabled, and recorded error codes were cleared.",
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
                "message": "Verification failed. Unable to retrieve a Project ID. Check whether the credential is still valid.",
            },
        )


# =============================================================================

# =============================================================================
