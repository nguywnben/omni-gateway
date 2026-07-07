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
}


def _int_value(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


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
):
    filename = os.path.basename(filename)
    if not filename:
        return

    tokens = normalize_token_usage(token_usage)
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
                    reasoning_tokens
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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


async def get_stats_24h() -> Dict[str, Dict[str, int]]:
    init_db()
    since = time.time() - 86400
    res = {}

    filenames = await get_all_credential_filenames()
    for name in filenames:
        res[name] = {
            "calls_24h": 0,
            "successful_calls_24h": 0,
            "failed_calls_24h": 0,
            "input_tokens_24h": 0,
            "output_tokens_24h": 0,
            "total_tokens_24h": 0,
            "cached_tokens_24h": 0,
            "reasoning_tokens_24h": 0,
        }

    with db_lock:
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute(
                """
                SELECT
                    filename,
                    COUNT(*),
                    COALESCE(SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END), 0),
                    COALESCE(SUM(input_tokens), 0),
                    COALESCE(SUM(output_tokens), 0),
                    COALESCE(SUM(total_tokens), 0),
                    COALESCE(SUM(cached_tokens), 0),
                    COALESCE(SUM(reasoning_tokens), 0)
                FROM usage_logs
                WHERE timestamp >= ?
                GROUP BY filename
                """,
                (since,)
            )
            for row in cursor.fetchall():
                res[row[0]] = {
                    "calls_24h": row[1],
                    "successful_calls_24h": row[2],
                    "failed_calls_24h": row[3],
                    "input_tokens_24h": row[4],
                    "output_tokens_24h": row[5],
                    "total_tokens_24h": row[6],
                    "cached_tokens_24h": row[7],
                    "reasoning_tokens_24h": row[8],
                }
        except Exception as e:
            log.error(f"Failed to fetch 24h stats: {e}")
        finally:
            conn.close()

    return res


def reset_stats(filename: str):
    init_db()
    filename = os.path.basename(filename)
    with db_lock:
        conn = sqlite3.connect(db_path)
        try:
            if filename == "all":
                conn.execute("DELETE FROM usage_logs")
            else:
                conn.execute("DELETE FROM usage_logs WHERE filename = ?", (filename,))
            conn.commit()
        except Exception as e:
            log.error(f"Failed to reset stats for {filename}: {e}")
        finally:
            conn.close()
