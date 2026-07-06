"""Credential pool write policy."""

import asyncio
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from log import log
from core.storage_adapter import get_storage_adapter


_POOL_LOCKS: Dict[str, asyncio.Lock] = {
    "code_assist": asyncio.Lock(),
    "primary": asyncio.Lock(),
}


def _normalize_mode(mode: str) -> str:
    return "primary" if mode in ("primary", "provider") else "code_assist"


def _safe_filename(filename: str, fallback_prefix: str = "credential") -> str:
    basename = os.path.basename(str(filename or "").strip())
    if basename:
        return basename
    return f"{fallback_prefix}-{int(time.time())}.json"


def normalize_project_id(credential_data: Dict[str, Any]) -> str:
    project_id = credential_data.get("project_id") or credential_data.get("quota_project_id") or ""
    return str(project_id).strip().lower()


def normalize_credential_email(value: Any) -> str:
    return str(value or "").strip().lower()


def get_known_credential_email(credential_data: Dict[str, Any]) -> str:
    for key in ("user_email", "email", "account_email", "client_email"):
        email = normalize_credential_email(credential_data.get(key))
        if email:
            return email
    return ""


async def resolve_credential_email(credential_data: Dict[str, Any]) -> str:
    email = get_known_credential_email(credential_data)
    if email:
        return email

    try:
        from core.google_oauth_api import Credentials, get_user_email

        credentials = Credentials.from_dict(credential_data)
        if not credentials:
            return ""
        return normalize_credential_email(await get_user_email(credentials))
    except Exception as e:
        log.warning(f"Unable to resolve credential email from token: {e}")
        return ""


def parse_credential_expiry(credential_data: Dict[str, Any]) -> Optional[datetime]:
    expiry = credential_data.get("expiry")
    if not expiry:
        return None

    try:
        if isinstance(expiry, datetime):
            parsed = expiry
        else:
            expiry_text = str(expiry).strip()
            if expiry_text.endswith("Z"):
                expiry_text = expiry_text[:-1] + "+00:00"
            parsed = datetime.fromisoformat(expiry_text)

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception:
        return None


def _is_incoming_newer(incoming: Optional[datetime], existing: Optional[datetime]) -> bool:
    if incoming is None:
        return False
    if existing is None:
        return True
    return incoming > existing


def _best_expiry_key(item: Dict[str, Any]) -> tuple[datetime, int]:
    return (
        item["expiry"] or datetime.min.replace(tzinfo=timezone.utc),
        -item["index"],
    )


async def _find_unique_filename(storage_adapter, requested_filename: str, credential_data: Dict[str, Any], mode: str) -> str:
    filename = _safe_filename(requested_filename, normalize_project_id(credential_data) or "credential")
    stem, ext = os.path.splitext(filename)
    if not ext:
        ext = ".json"

    existing_names = set(await storage_adapter.list_credentials(mode=mode))
    if filename not in existing_names:
        return filename

    existing_data = await storage_adapter.get_credential(filename, mode=mode)
    if get_known_credential_email(existing_data or {}) == get_known_credential_email(credential_data):
        return filename

    index = 2
    while True:
        candidate = f"{stem}-{index}{ext}"
        if candidate not in existing_names:
            return candidate
        index += 1


async def _get_existing_email(storage_adapter, filename: str, credential_data: Dict[str, Any], mode: str) -> str:
    try:
        state = await storage_adapter.get_credential_state(filename, mode=mode)
        email = normalize_credential_email(state.get("user_email"))
        if email:
            return email
    except Exception:
        pass
    return get_known_credential_email(credential_data)


async def _store_with_email_state(storage_adapter, filename: str, credential_data: Dict[str, Any], email: str, mode: str) -> None:
    success = await storage_adapter.store_credential(filename, credential_data, mode=mode)
    if not success:
        raise RuntimeError("Storage adapter rejected the credential.")
    if email:
        await storage_adapter.update_credential_state(filename, {"user_email": email}, mode=mode)


async def upsert_credential_by_email(
    filename: str,
    credential_data: Dict[str, Any],
    mode: str = "code_assist",
) -> Dict[str, Any]:
    """Store one credential per email, keeping the entry with the latest expiry."""
    storage_adapter = await get_storage_adapter()
    mode = _normalize_mode(mode)
    lock = _POOL_LOCKS[mode]

    async with lock:
        email = await resolve_credential_email(credential_data)
        incoming_expiry = parse_credential_expiry(credential_data)

        if email:
            credential_data["user_email"] = email

        if not email:
            target_filename = await _find_unique_filename(storage_adapter, filename, credential_data, mode)
            await _store_with_email_state(storage_adapter, target_filename, credential_data, "", mode)
            return {
                "action": "created",
                "stored": True,
                "filename": target_filename,
                "email": None,
                "message": "Credential added to the pool. Email was not available, so duplicate detection was skipped.",
            }

        matches: List[Dict[str, Any]] = []
        for index, existing_filename in enumerate(await storage_adapter.list_credentials(mode=mode)):
            existing_data = await storage_adapter.get_credential(existing_filename, mode=mode)
            existing_email = await _get_existing_email(storage_adapter, existing_filename, existing_data or {}, mode)
            if existing_email == email:
                matches.append(
                    {
                        "filename": existing_filename,
                        "data": existing_data or {},
                        "expiry": parse_credential_expiry(existing_data or {}),
                        "index": index,
                    }
                )

        if not matches:
            target_filename = await _find_unique_filename(storage_adapter, filename, credential_data, mode)
            await _store_with_email_state(storage_adapter, target_filename, credential_data, email, mode)
            return {
                "action": "created",
                "stored": True,
                "filename": target_filename,
                "email": email,
                "incoming_expiry": incoming_expiry.isoformat() if incoming_expiry else None,
                "message": "Credential added to the pool.",
            }

        best_existing = max(matches, key=_best_expiry_key)
        keep_filename = best_existing["filename"]
        deleted_duplicates = []

        if _is_incoming_newer(incoming_expiry, best_existing["expiry"]):
            await _store_with_email_state(storage_adapter, keep_filename, credential_data, email, mode)

            for item in matches:
                if item["filename"] == keep_filename:
                    continue
                if await storage_adapter.delete_credential(item["filename"], mode=mode):
                    deleted_duplicates.append(item["filename"])

            log.info(f"Replaced credential for email={email} with a later expiry. Kept filename={keep_filename}.")
            return {
                "action": "replaced",
                "stored": True,
                "filename": keep_filename,
                "email": email,
                "incoming_expiry": incoming_expiry.isoformat() if incoming_expiry else None,
                "existing_expiry": best_existing["expiry"].isoformat() if best_existing["expiry"] else None,
                "deleted_duplicates": deleted_duplicates,
                "message": "Credential replaced because the new expiry is later.",
            }

        for item in matches:
            if item["filename"] == keep_filename:
                continue
            if await storage_adapter.delete_credential(item["filename"], mode=mode):
                deleted_duplicates.append(item["filename"])

        return {
            "action": "skipped",
            "stored": False,
            "filename": keep_filename,
            "email": email,
            "incoming_expiry": incoming_expiry.isoformat() if incoming_expiry else None,
            "existing_expiry": best_existing["expiry"].isoformat() if best_existing["expiry"] else None,
            "deleted_duplicates": deleted_duplicates,
            "message": "Credential was not added because the pool already has the same email with an equal or later expiry.",
        }


async def deduplicate_credentials_by_account_email(mode: str = "code_assist") -> Dict[str, Any]:
    """Remove existing duplicate credentials by email, keeping the latest expiry."""
    storage_adapter = await get_storage_adapter()
    mode = _normalize_mode(mode)
    lock = _POOL_LOCKS[mode]

    async with lock:
        grouped: Dict[str, List[Dict[str, Any]]] = {}
        no_email_count = 0
        total_count = 0

        for index, filename in enumerate(await storage_adapter.list_credentials(mode=mode)):
            total_count += 1
            credential_data = await storage_adapter.get_credential(filename, mode=mode)
            email = await _get_existing_email(storage_adapter, filename, credential_data or {}, mode)
            if not email:
                no_email_count += 1
                continue

            grouped.setdefault(email, []).append(
                {
                    "filename": filename,
                    "data": credential_data or {},
                    "expiry": parse_credential_expiry(credential_data or {}),
                    "index": index,
                }
            )

        deleted_count = 0
        groups = []

        for email, items in grouped.items():
            if len(items) < 2:
                continue

            keep_item = max(items, key=_best_expiry_key)
            deleted_files = []

            for item in items:
                if item["filename"] == keep_item["filename"]:
                    continue
                if await storage_adapter.delete_credential(item["filename"], mode=mode):
                    deleted_files.append(item["filename"])
                    deleted_count += 1

            groups.append(
                {
                    "email": email,
                    "kept_file": keep_item["filename"],
                    "kept_expiry": keep_item["expiry"].isoformat() if keep_item["expiry"] else None,
                    "deleted_files": deleted_files,
                    "duplicate_count": len(deleted_files),
                }
            )

        if deleted_count:
            log.info(f"Deduplicated {deleted_count} credential(s) in {mode} pool by email.")

        return {
            "deleted_count": deleted_count,
            "kept_count": total_count - deleted_count,
            "total_count": total_count,
            "unique_emails_count": len(grouped),
            "no_email_count": no_email_count,
            "duplicate_groups": groups,
        }


upsert_credential_by_project_id = upsert_credential_by_email
deduplicate_credentials_by_project_id = deduplicate_credentials_by_account_email
