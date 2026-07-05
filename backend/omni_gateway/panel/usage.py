import sqlite3
import os
import time
import threading
from typing import Dict, Any, List

from log import log
from paths import DEFAULT_CREDENTIALS_DIR

db_lock = threading.Lock()
db_path = str(DEFAULT_CREDENTIALS_DIR / "usage_stats.db")

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
            conn.commit()
        except Exception as e:
            log.error(f"Failed to initialize usage database: {e}")
        finally:
            conn.close()

def record_call(filename: str):
    filename = os.path.basename(filename)
    init_db()
    with db_lock:
        conn = sqlite3.connect(db_path)
        try:
            conn.execute(
                "INSERT INTO usage_logs (filename, timestamp) VALUES (?, ?)",
                (filename, time.time())
            )
            conn.commit()
        except Exception as e:
            log.error(f"Failed to record call in database for {filename}: {e}")
        finally:
            conn.close()

async def get_total_files_count() -> int:
    try:
        from omni_gateway.storage_adapter import get_storage_adapter
        storage_adapter = await get_storage_adapter()
        ag_summary = await storage_adapter._backend.get_credentials_summary(limit=10000, mode="omni")

        filenames = set()
        for item in ag_summary.get("items", []):
            filenames.add(os.path.basename(item["filename"]))

        return len(filenames)
    except Exception as e:
        log.error(f"Error counting credentials for usage aggregation: {e}")
        return 0

async def get_all_credential_filenames() -> List[str]:
    try:
        from omni_gateway.storage_adapter import get_storage_adapter
        storage_adapter = await get_storage_adapter()
        ag_summary = await storage_adapter._backend.get_credentials_summary(limit=10000, mode="omni")

        filenames = set()
        for item in ag_summary.get("items", []):
            filenames.add(os.path.basename(item["filename"]))

        return sorted(list(filenames))
    except Exception as e:
        log.error(f"Error getting credential filenames for usage: {e}")
        return []

async def get_stats_24h() -> Dict[str, Dict[str, int]]:
    init_db()
    since = time.time() - 86400
    res = {}

    # Pre-populate all existing filenames with 0 calls
    filenames = await get_all_credential_filenames()
    for name in filenames:
        res[name] = {"calls_24h": 0}

    with db_lock:
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.execute(
                "SELECT filename, COUNT(*) FROM usage_logs WHERE timestamp >= ? GROUP BY filename",
                (since,)
            )
            for row in cursor.fetchall():
                res[row[0]] = {"calls_24h": row[1]}
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
