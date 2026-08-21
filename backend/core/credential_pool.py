"""Credential pool write policy."""

import asyncio
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from core.provider_registry import (
    GOOGLE_ANTIGRAVITY,
    canonicalize_antigravity_credential_filename,
    get_credential_provider,
    get_static_credential_identity,
)
from core.storage_adapter import get_storage_adapter
from log import log

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
    if get_static_credential_identity(credential_data):
        return ""

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


async def _find_unique_filename(
    storage_adapter, requested_filename: str, credential_data: Dict[str, Any], mode: str
) -> str:
    filename = _safe_filename(
        requested_filename, normalize_project_id(credential_data) or "credential"
    )
    stem, ext = os.path.splitext(filename)
    if not ext:
        ext = ".json"

    existing_names = set(await storage_adapter.list_credentials(mode=mode))
    if filename not in existing_names:
        return filename

    existing_data = await storage_adapter.get_credential(filename, mode=mode)
    if get_credential_provider(existing_data or {}) == get_credential_provider(
        credential_data
    ) and get_known_credential_email(existing_data or {}) == get_known_credential_email(
        credential_data
    ):
        return filename

    index = 2
    while True:
        candidate = f"{stem}-{index}{ext}"
        if candidate not in existing_names:
            return candidate
        index += 1


async def _get_existing_email(
    storage_adapter, filename: str, credential_data: Dict[str, Any], mode: str
) -> str:
    try:
        state = await storage_adapter.get_credential_state(filename, mode=mode)
        email = normalize_credential_email(state.get("user_email"))
        if email:
            return email
    except Exception:
        pass
    return get_known_credential_email(credential_data)


async def _store_with_email_state(
    storage_adapter, filename: str, credential_data: Dict[str, Any], email: str, mode: str
) -> None:
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
    """Store one credential per account or API-key identity."""
    storage_adapter = await get_storage_adapter()
    mode = _normalize_mode(mode)
    is_antigravity = (
        mode == "primary" and get_credential_provider(credential_data) == GOOGLE_ANTIGRAVITY
    )
    lock = _POOL_LOCKS[mode]

    async with lock:
        static_identity = get_static_credential_identity(credential_data)
        if static_identity:
            matches = []
            for index, existing_filename in enumerate(
                await storage_adapter.list_credentials(mode=mode)
            ):
                existing_data = await storage_adapter.get_credential(existing_filename, mode=mode)
                if get_static_credential_identity(existing_data or {}) == static_identity:
                    matches.append(
                        {
                            "filename": existing_filename,
                            "data": existing_data or {},
                            "index": index,
                        }
                    )

            if not matches:
                target_filename = await _find_unique_filename(
                    storage_adapter, filename, credential_data, mode
                )
                await _store_with_email_state(
                    storage_adapter, target_filename, credential_data, "", mode
                )
                return {
                    "action": "created",
                    "stored": True,
                    "filename": target_filename,
                    "email": None,
                    "identity": static_identity,
                    "message": "API key added to the provider pool.",
                }

            keep = min(matches, key=lambda item: item["index"])
            keep_filename = keep["filename"]
            if keep["data"].get("created_at") and not credential_data.get("created_at"):
                credential_data["created_at"] = keep["data"]["created_at"]
            await _store_with_email_state(storage_adapter, keep_filename, credential_data, "", mode)
            deleted_duplicates = []
            for item in matches:
                if item["filename"] == keep_filename:
                    continue
                if await storage_adapter.delete_credential(item["filename"], mode=mode):
                    deleted_duplicates.append(item["filename"])
            return {
                "action": "updated",
                "stored": True,
                "filename": keep_filename,
                "email": None,
                "identity": static_identity,
                "deleted_duplicates": deleted_duplicates,
                "message": "The existing API key credential was revalidated and updated.",
            }

        email = await resolve_credential_email(credential_data)
        incoming_expiry = parse_credential_expiry(credential_data)

        if email:
            credential_data["user_email"] = email

        if is_antigravity:
            filename = canonicalize_antigravity_credential_filename(
                filename,
                credential_data,
                email=email,
            )

        if not email:
            target_filename = await _find_unique_filename(
                storage_adapter, filename, credential_data, mode
            )
            await _store_with_email_state(
                storage_adapter, target_filename, credential_data, "", mode
            )
            return {
                "action": "created",
                "stored": True,
                "filename": target_filename,
                "email": None,
                "message": "Credential added to the pool. Email was not available, so duplicate detection was skipped.",
            }

        matches: List[Dict[str, Any]] = []
        for index, existing_filename in enumerate(
            await storage_adapter.list_credentials(mode=mode)
        ):
            existing_data = await storage_adapter.get_credential(existing_filename, mode=mode)
            if get_credential_provider(existing_data or {}) != get_credential_provider(
                credential_data
            ):
                continue
            existing_email = await _get_existing_email(
                storage_adapter, existing_filename, existing_data or {}, mode
            )
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
            target_filename = await _find_unique_filename(
                storage_adapter, filename, credential_data, mode
            )
            await _store_with_email_state(
                storage_adapter, target_filename, credential_data, email, mode
            )
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
            await _store_with_email_state(
                storage_adapter, keep_filename, credential_data, email, mode
            )

            for item in matches:
                if item["filename"] == keep_filename:
                    continue
                if await storage_adapter.delete_credential(item["filename"], mode=mode):
                    deleted_duplicates.append(item["filename"])

            log.info(
                f"Replaced credential for email={email} with a later expiry. Kept filename={keep_filename}."
            )
            return {
                "action": "replaced",
                "stored": True,
                "filename": keep_filename,
                "email": email,
                "incoming_expiry": incoming_expiry.isoformat() if incoming_expiry else None,
                "existing_expiry": best_existing["expiry"].isoformat()
                if best_existing["expiry"]
                else None,
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
            "existing_expiry": best_existing["expiry"].isoformat()
            if best_existing["expiry"]
            else None,
            "deleted_duplicates": deleted_duplicates,
            "message": "Credential was not added because the pool already has the same email with an equal or later expiry.",
        }


async def deduplicate_credentials_by_account_email(mode: str = "code_assist") -> Dict[str, Any]:
    """Remove duplicate credentials by account email or API-key fingerprint."""
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
            static_identity = get_static_credential_identity(credential_data or {})
            email = await _get_existing_email(
                storage_adapter, filename, credential_data or {}, mode
            )
            provider_id = get_credential_provider(credential_data or {})
            identity = static_identity or (f"email:{provider_id}:{email}" if email else "")
            if not identity:
                no_email_count += 1
                continue

            grouped.setdefault(identity, []).append(
                {
                    "filename": filename,
                    "data": credential_data or {},
                    "expiry": parse_credential_expiry(credential_data or {}),
                    "index": index,
                    "email": email or None,
                    "identity": identity,
                }
            )

        deleted_count = 0
        groups = []

        for identity, items in grouped.items():
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
                    "email": keep_item.get("email"),
                    "identity": identity,
                    "kept_file": keep_item["filename"],
                    "kept_expiry": keep_item["expiry"].isoformat() if keep_item["expiry"] else None,
                    "deleted_files": deleted_files,
                    "duplicate_count": len(deleted_files),
                }
            )

        if deleted_count:
            credential_label = "credential" if deleted_count == 1 else "credentials"
            log.info(
                f"Deduplicated {deleted_count} {credential_label} in the {mode} pool "
                "by account identity."
            )

        return {
            "deleted_count": deleted_count,
            "kept_count": total_count - deleted_count,
            "total_count": total_count,
            "unique_emails_count": sum(1 for identity in grouped if identity.startswith("email:")),
            "unique_identities_count": len(grouped),
            "no_email_count": no_email_count,
            "duplicate_groups": groups,
        }


upsert_credential_by_project_id = upsert_credential_by_email
deduplicate_credentials_by_project_id = deduplicate_credentials_by_account_email
