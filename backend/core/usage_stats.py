import os
import json
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional

from log import log
from paths import DEFAULT_CREDENTIALS_DIR


db_lock = threading.Lock()
db_path = str(DEFAULT_CREDENTIALS_DIR / "usage_stats.db")
UNASSIGNED_USAGE_FILENAME = "__gateway_unassigned__.json"
USAGE_PERIODS = {
    "1d": {"seconds": 86400, "label": "Last 24 hours"},
    "7d": {"seconds": 7 * 86400, "label": "Last 7 days"},
    "30d": {"seconds": 30 * 86400, "label": "Last 30 days"},
    "all": {"seconds": None, "label": "All time"},
}


TOKEN_COLUMNS = {
    "model": "TEXT DEFAULT ''",
    "provider": "TEXT DEFAULT ''",
    "status_code": "INTEGER DEFAULT 200",
    "success": "INTEGER DEFAULT 1",
    "input_tokens": "INTEGER DEFAULT 0",
    "output_tokens": "INTEGER DEFAULT 0",
    "total_tokens": "INTEGER DEFAULT 0",
    "cached_tokens": "INTEGER DEFAULT 0",
    "reasoning_tokens": "INTEGER DEFAULT 0",
    "estimated_input_tokens": "INTEGER DEFAULT 0",
    "estimated_tokens_saved": "INTEGER DEFAULT 0",
    "compressed_messages": "INTEGER DEFAULT 0",
}


def _int_value(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _provider_display_name(value: Any) -> str:
    normalized = str(value or "").strip().lower().replace("-", "_")
    if normalized in {"primary", "provider", "antigravity"}:
        return "Antigravity"
    if normalized == "code_assist":
        return "Code Assist"
    if not normalized:
        return "Provider"
    return " ".join(part.capitalize() for part in normalized.split("_") if part)


def normalize_usage_period(period: str = "1d") -> str:
    normalized = str(period or "1d").strip().lower()
    return normalized if normalized in USAGE_PERIODS else "1d"


def get_usage_period_metadata(period: str = "1d") -> Dict[str, str]:
    normalized = normalize_usage_period(period)
    return {
        "value": normalized,
        "label": str(USAGE_PERIODS[normalized]["label"]),
    }


def _empty_usage_record(metadata: Dict[str, str]) -> Dict[str, Any]:
    return {
        "user_email": metadata.get("user_email", ""),
        "provider": metadata.get("provider", "Antigravity"),
        "calls": 0,
        "successful_calls": 0,
        "failed_calls": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "cached_tokens": 0,
        "reasoning_tokens": 0,
        "estimated_input_tokens": 0,
        "estimated_tokens_saved": 0,
        "compressed_messages": 0,
        "calls_24h": 0,
        "successful_calls_24h": 0,
        "failed_calls_24h": 0,
        "input_tokens_24h": 0,
        "output_tokens_24h": 0,
        "total_tokens_24h": 0,
        "cached_tokens_24h": 0,
        "reasoning_tokens_24h": 0,
        "estimated_input_tokens_24h": 0,
        "estimated_tokens_saved_24h": 0,
        "compressed_messages_24h": 0,
    }


def _usage_record(
    *,
    existing: Dict[str, Any],
    provider: Any,
    calls: int,
    successful_calls: int,
    failed_calls: int,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    cached_tokens: int,
    reasoning_tokens: int,
    estimated_input_tokens: int,
    estimated_tokens_saved: int,
    compressed_messages: int,
) -> Dict[str, Any]:
    record = {
        "user_email": existing.get("user_email", ""),
        "provider": existing.get("provider") or _provider_display_name(provider),
        "calls": calls,
        "successful_calls": successful_calls,
        "failed_calls": failed_calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cached_tokens": cached_tokens,
        "reasoning_tokens": reasoning_tokens,
        "estimated_input_tokens": estimated_input_tokens,
        "estimated_tokens_saved": estimated_tokens_saved,
        "compressed_messages": compressed_messages,
    }
    record.update({
        "calls_24h": calls,
        "successful_calls_24h": successful_calls,
        "failed_calls_24h": failed_calls,
        "input_tokens_24h": input_tokens,
        "output_tokens_24h": output_tokens,
        "total_tokens_24h": total_tokens,
        "cached_tokens_24h": cached_tokens,
        "reasoning_tokens_24h": reasoning_tokens,
        "estimated_input_tokens_24h": estimated_input_tokens,
        "estimated_tokens_saved_24h": estimated_tokens_saved,
        "compressed_messages_24h": compressed_messages,
    })
    return record


def normalize_token_usage(usage: Optional[Dict[str, Any]]) -> Dict[str, int]:
    usage = usage or {}
    prompt_details = usage.get("prompt_tokens_details") or {}
    completion_details = usage.get("completion_tokens_details") or {}

    input_tokens = _int_value(
        usage.get("promptTokenCount", usage.get("input_tokens", usage.get("prompt_tokens")))
    )
    output_tokens = _int_value(
        usage.get("candidatesTokenCount", usage.get("output_tokens", usage.get("completion_tokens")))
    )
    cached_tokens = _int_value(
        usage.get(
            "cachedContentTokenCount",
            usage.get("cache_read_input_tokens", prompt_details.get("cached_tokens")),
        )
    )
    reasoning_tokens = _int_value(
        usage.get("thoughtsTokenCount", completion_details.get("reasoning_tokens"))
    )
    total_tokens = _int_value(usage.get("totalTokenCount", usage.get("total_tokens")))

    if total_tokens == 0:
        total_tokens = input_tokens + output_tokens + reasoning_tokens

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "cached_tokens": cached_tokens,
        "reasoning_tokens": reasoning_tokens,
    }


def extract_token_usage_from_response(value: Any) -> Dict[str, int]:
    if value is None:
        return normalize_token_usage(None)

    if isinstance(value, (bytes, bytearray)):
        try:
            value = value.decode("utf-8")
        except UnicodeDecodeError:
            return normalize_token_usage(None)

    if isinstance(value, str):
        try:
            value = json.loads(value)
        except Exception:
            return normalize_token_usage(None)

    if not isinstance(value, dict):
        return normalize_token_usage(None)

    response_value = value.get("response") if isinstance(value.get("response"), dict) else value
    candidate = {}
    candidates = response_value.get("candidates") if isinstance(response_value, dict) else None
    if isinstance(candidates, list) and candidates:
        candidate = candidates[0] if isinstance(candidates[0], dict) else {}

    usage = (
        response_value.get("usageMetadata")
        or candidate.get("usageMetadata")
        or value.get("usage")
        or {}
    )
    return normalize_token_usage(usage if isinstance(usage, dict) else {})


def extract_token_usage_from_stream_chunk(chunk: Any) -> Dict[str, int]:
    if isinstance(chunk, bytes):
        try:
            chunk = chunk.decode("utf-8")
        except UnicodeDecodeError:
            return normalize_token_usage(None)

    if not isinstance(chunk, str):
        return normalize_token_usage(None)

    text = chunk.strip()
    if not text:
        return normalize_token_usage(None)

    if text.startswith("data:"):
        text = text[5:].strip()

    if not text or text == "[DONE]":
        return normalize_token_usage(None)

    try:
        payload = json.loads(text)
    except Exception:
        return normalize_token_usage(None)

    return extract_token_usage_from_response(payload)


def init_db():
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    with db_lock:
        conn = sqlite3.connect(db_path)
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    timestamp REAL NOT NULL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON usage_logs(timestamp);")
            existing_columns = {
                row[1] for row in conn.execute("PRAGMA table_info(usage_logs)").fetchall()
            }
            for column_name, column_type in TOKEN_COLUMNS.items():
                if column_name not in existing_columns:
                    conn.execute(f"ALTER TABLE usage_logs ADD COLUMN {column_name} {column_type};")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_filename ON usage_logs(filename);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_usage_model ON usage_logs(model);")
            conn.commit()
        except Exception as e:
            log.error(f"Failed to initialize usage database: {e}")
        finally:
            conn.close()


def record_call(
    filename: str,
    *,
    model: str = "",
    provider: str = "Antigravity",
    status_code: int = 200,
    success: bool = True,
    token_usage: Optional[Dict[str, Any]] = None,
    request_metrics: Optional[Dict[str, Any]] = None,
):
    filename = os.path.basename(filename)
    if not filename:
        return

    tokens = normalize_token_usage(token_usage)
    request_metrics = request_metrics or {}
    init_db()
    with db_lock:
        conn = sqlite3.connect(db_path)
        try:
            conn.execute(
                """
                INSERT INTO usage_logs (
                    filename,
                    timestamp,
                    model,
                    provider,
                    status_code,
                    success,
                    input_tokens,
                    output_tokens,
                    total_tokens,
                    cached_tokens,
                    reasoning_tokens,
                    estimated_input_tokens,
                    estimated_tokens_saved,
                    compressed_messages
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    filename,
                    time.time(),
                    model or "",
                    provider or "",
                    _int_value(status_code or 200),
                    1 if success else 0,
                    tokens["input_tokens"],
                    tokens["output_tokens"],
                    tokens["total_tokens"],
                    tokens["cached_tokens"],
                    tokens["reasoning_tokens"],
                    _int_value(request_metrics.get("estimated_input_tokens")),
                    _int_value(request_metrics.get("estimated_tokens_saved")),
                    _int_value(request_metrics.get("compressed_messages")),
                )
            )
            conn.commit()
        except Exception as e:
            log.error(f"Failed to record call in database for {filename}: {e}")
        finally:
            conn.close()


async def get_credential_counts() -> Dict[str, int]:
    try:
        from core.storage_adapter import get_storage_adapter

        storage_adapter = await get_storage_adapter()
        provider_summary = await storage_adapter._backend.get_credentials_summary(limit=None, mode="primary")
        summary_stats = provider_summary.get("stats") or {}

        filenames = set()
        for item in provider_summary.get("items", []):
            filenames.add(os.path.basename(item["filename"]))

        total = _int_value(summary_stats.get("total")) or len(filenames)
        active = _int_value(summary_stats.get("normal"))
        disabled = _int_value(summary_stats.get("disabled"))
        if active == 0 and total > disabled:
            active = total - disabled

        return {
            "total": total,
            "active": active,
            "disabled": disabled,
        }
    except Exception as e:
        log.error(f"Error counting credentials for usage aggregation: {e}")
        return {"total": 0, "active": 0, "disabled": 0}


async def get_total_files_count() -> int:
    counts = await get_credential_counts()
    return counts["total"]


async def get_credential_usage_metadata() -> Dict[str, Dict[str, str]]:
    try:
        from core.storage_adapter import get_storage_adapter

        storage_adapter = await get_storage_adapter()
        provider_summary = await storage_adapter._backend.get_credentials_summary(limit=None, mode="primary")

        metadata: Dict[str, Dict[str, str]] = {}
        for item in provider_summary.get("items", []):
            filename = os.path.basename(item.get("filename") or "")
            if not filename:
                continue

            metadata[filename] = {
                "user_email": str(item.get("user_email") or ""),
                "provider": _provider_display_name(
                    item.get("provider") or item.get("provider_name") or "Antigravity"
                ),
            }

        return metadata
    except Exception as e:
        log.error(f"Error getting credential metadata for usage: {e}")
        return {}


async def get_all_credential_filenames() -> List[str]:
    try:
        from core.storage_adapter import get_storage_adapter

        storage_adapter = await get_storage_adapter()
        provider_summary = await storage_adapter._backend.get_credentials_summary(limit=None, mode="primary")

        filenames = set()
        for item in provider_summary.get("items", []):
            filenames.add(os.path.basename(item["filename"]))

        return sorted(list(filenames))
    except Exception as e:
        log.error(f"Error getting credential filenames for usage: {e}")
        return []


async def get_stats_for_period(period: str = "1d") -> Dict[str, Dict[str, Any]]:
    init_db()
    normalized_period = normalize_usage_period(period)
    seconds = USAGE_PERIODS[normalized_period]["seconds"]
    since = time.time() - int(seconds) if seconds is not None else None
    res = {}

    metadata_by_filename = await get_credential_usage_metadata()
    filenames = await get_all_credential_filenames()
    for name in filenames:
        metadata = metadata_by_filename.get(name, {})
        res[name] = _empty_usage_record(metadata)

    with db_lock:
        conn = sqlite3.connect(db_path)
        try:
            where_clause = "WHERE timestamp >= ?" if since is not None else ""
            params = (since,) if since is not None else ()
            cursor = conn.execute(
                f"""
                SELECT
                    filename,
                    COUNT(*),
                    COALESCE(SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(input_tokens), 0),
                    COALESCE(SUM(output_tokens), 0),
                    COALESCE(SUM(total_tokens), 0),
                    COALESCE(SUM(cached_tokens), 0),
                    COALESCE(SUM(reasoning_tokens), 0),
                    COALESCE(SUM(estimated_input_tokens), 0),
                    COALESCE(SUM(estimated_tokens_saved), 0),
                    COALESCE(SUM(compressed_messages), 0),
                    COALESCE(MAX(NULLIF(provider, '')), '')
                FROM usage_logs
                {where_clause}
                GROUP BY filename
                """,
                params,
            )
            for row in cursor.fetchall():
                existing = res.get(row[0], {})
                res[row[0]] = _usage_record(
                    existing=existing,
                    provider=row[12],
                    calls=row[1],
                    successful_calls=row[2],
                    failed_calls=row[3],
                    input_tokens=row[4],
                    output_tokens=row[5],
                    total_tokens=row[6],
                    cached_tokens=row[7],
                    reasoning_tokens=row[8],
                    estimated_input_tokens=row[9],
                    estimated_tokens_saved=row[10],
                    compressed_messages=row[11],
                )
        except Exception as e:
            log.error(f"Failed to fetch usage stats for {normalized_period}: {e}")
        finally:
            conn.close()

    return res


async def get_stats_24h() -> Dict[str, Dict[str, Any]]:
    return await get_stats_for_period("1d")
