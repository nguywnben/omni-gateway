"""Internal implementation detail."""

import os
import re
import sys
import threading
from datetime import datetime
from collections import deque
import atexit

from paths import DEFAULT_LOG_FILE


LOG_LEVELS = {"debug": 0, "info": 1, "warning": 2, "error": 3, "critical": 4}


_REDACTION_PATTERNS = [
    (re.compile(r"(?i)(Authorization:\s*Bearer\s+)[A-Za-z0-9._~+/=-]+"), r"\1<redacted>"),
    (re.compile(r"sk-ogw-[A-Za-z0-9._-]+"), "sk-ogw-<redacted>"),
    (re.compile(r"(?i)(x-api-key['\"]?\s*[:=]\s*['\"]?)[A-Za-z0-9._~+/=-]+"), r"\1<redacted>"),
    (re.compile(r"(?i)(x-goog-api-key['\"]?\s*[:=]\s*['\"]?)[A-Za-z0-9._~+/=-]+"), r"\1<redacted>"),
    (
        re.compile(
            r"(?i)(['\"](?:access_token|refresh_token|id_token|client_secret|api_key|password|token)['\"]\s*:\s*['\"])[^'\"]+(['\"])",
        ),
        r"\1<redacted>\2",
    ),
]


def redact_text(value: object) -> str:
    """Redact sensitive tokens before logs reach stdout, files, or streams."""
    text = str(value)
    for pattern, replacement in _REDACTION_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


_file_writing_disabled = False
_disable_reason = None


_log_file_handle = None

# -----------------------------------------------------------------



# -----------------------------------------------------------------
_log_deque: deque = deque()
_deque_condition = threading.Condition(threading.Lock())
_writer_thread = None
_writer_running = False

# -----------------------------------------------------------------

# -----------------------------------------------------------------
_cached_log_level: int = LOG_LEVELS["info"]
_cached_log_file: str = str(DEFAULT_LOG_FILE)

_log_enabled: bool = True


def _refresh_config():
    """Internal implementation detail."""
    global _cached_log_level, _cached_log_file, _log_enabled
    level = os.getenv("LOG_LEVEL", "info").lower()
    _cached_log_level = LOG_LEVELS.get(level, LOG_LEVELS["info"])
    _cached_log_file = os.getenv("LOG_FILE", str(DEFAULT_LOG_FILE))
    _log_enabled = os.getenv("ENABLE_LOG", "1").strip().lower() not in ("0", "false", "no", "off")


def _get_current_log_level() -> int:
    return _cached_log_level


def _get_log_file_path() -> str:
    return _cached_log_file


# -----------------------------------------------------------------

# -----------------------------------------------------------------

def _close_log_file():
    global _log_file_handle
    if _log_file_handle is not None:
        try:
            _log_file_handle.flush()
            _log_file_handle.close()
        except Exception:
            pass
        finally:
            _log_file_handle = None


def _open_log_file(mode: str = "a") -> bool:
    global _log_file_handle, _file_writing_disabled, _disable_reason
    _close_log_file()
    try:

        log_dir = os.path.dirname(os.path.abspath(_cached_log_file))
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        _log_file_handle = open(_cached_log_file, mode, encoding="utf-8", buffering=65536)
        return True
    except (PermissionError, OSError, IOError) as e:
        _file_writing_disabled = True
        _disable_reason = str(e)
        print(f"Warning: Cannot open log file, disabling file writing: {e}", file=sys.stderr)
        print("Log messages will continue to display in console only.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Warning: Failed to open log file: {e}", file=sys.stderr)
        return False


def _clear_log_file():
    """Internal implementation detail."""
    global _file_writing_disabled, _disable_reason
    try:
        log_dir = os.path.dirname(os.path.abspath(_cached_log_file))
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(_cached_log_file, "w", encoding="utf-8") as f:
            pass
        _open_log_file("a")
    except (PermissionError, OSError, IOError) as e:
        _file_writing_disabled = True
        _disable_reason = str(e)
        print(
            f"Warning: File system appears to be read-only or permission denied. "
            f"Disabling log file writing: {e}",
            file=sys.stderr,
        )
        print("Log messages will continue to display in console only.", file=sys.stderr)
    except Exception as e:
        print(f"Warning: Failed to clear log file: {e}", file=sys.stderr)


# -----------------------------------------------------------------

# -----------------------------------------------------------------
_BATCH_SIZE = 1000
_FLUSH_INTERVAL = 2


def _log_writer_worker():
    global _writer_running

    last_flush_time = 0.0

    while True:

        with _deque_condition:
            if not _log_deque and _writer_running:
                _deque_condition.wait(timeout=_FLUSH_INTERVAL)


            batch = []
            for _ in range(_BATCH_SIZE):
                if _log_deque:
                    batch.append(_log_deque.popleft())
                else:
                    break

        if batch and not _file_writing_disabled:

            chunk = "\n".join(batch) + "\n"
            try:
                if _log_file_handle is None:
                    _open_log_file("a")
                if _log_file_handle is not None:
                    _log_file_handle.write(chunk)
            except Exception as e:
                print(f"Warning: Failed to write log batch: {e}", file=sys.stderr)
                _close_log_file()
                try:
                    _open_log_file("a")
                except Exception:
                    pass


        now = _now_ts()
        if now - last_flush_time >= _FLUSH_INTERVAL:
            if _log_file_handle is not None:
                try:
                    _log_file_handle.flush()
                except Exception:
                    pass
            last_flush_time = now


        if not _writer_running and not _log_deque:
            break


    if _log_file_handle is not None:
        try:
            _log_file_handle.flush()
        except Exception:
            pass
    _close_log_file()


def _now_ts() -> float:
    import time
    return time.monotonic()


def _start_writer_thread():
    global _writer_thread, _writer_running

    if _writer_thread is None or not _writer_thread.is_alive():
        _writer_running = True
        _writer_thread = threading.Thread(target=_log_writer_worker, daemon=True, name="LogWriter")
        _writer_thread.start()


def _stop_writer_thread():
    global _writer_running

    _writer_running = False

    with _deque_condition:
        _deque_condition.notify_all()

    if _writer_thread and _writer_thread.is_alive():
        _writer_thread.join(timeout=3.0)


# -----------------------------------------------------------------

# -----------------------------------------------------------------
_MAX_QUEUE_SIZE = 5000


def _write_to_file(message: str):
    if _file_writing_disabled:
        return

    if len(_log_deque) >= _MAX_QUEUE_SIZE:
        return
    _log_deque.append(message)

    if _deque_condition.acquire(blocking=False):
        try:
            _deque_condition.notify()
        finally:
            _deque_condition.release()


# -----------------------------------------------------------------

# -----------------------------------------------------------------

def _log(level: str, message: str):

    if not _log_enabled:
        return

    level = level.lower()
    level_val = LOG_LEVELS.get(level)
    if level_val is None:
        print(f"Warning: Unknown log level '{level}'", file=sys.stderr)
        return


    if level_val < _cached_log_level:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level.upper()}] {redact_text(message)}"

    if level in ("error", "critical"):
        print(entry, file=sys.stderr)
    else:
        print(entry)

    _write_to_file(entry)


def set_log_level(level: str):
    """Internal implementation detail."""
    global _cached_log_level
    level = level.lower()
    if level not in LOG_LEVELS:
        print(f"Warning: Unknown log level '{level}'. Valid levels: {', '.join(LOG_LEVELS.keys())}")
        return False
    _cached_log_level = LOG_LEVELS[level]
    return True


class Logger:
    """Internal implementation detail."""
    def __call__(self, level: str, message: str):
        _log(level, message)

    def debug(self, message: str):
        _log("debug", message)

    def info(self, message: str):
        _log("info", message)

    def warning(self, message: str):
        _log("warning", message)

    def error(self, message: str):
        _log("error", message)

    def critical(self, message: str):
        _log("critical", message)

    def get_current_level(self) -> str:
        current_level = _get_current_log_level()
        for name, value in LOG_LEVELS.items():
            if value == current_level:
                return name
        return "info"

    def get_log_file(self) -> str:
        return _get_log_file_path()

    def close(self):
        """Internal implementation detail."""
        _stop_writer_thread()

    def get_queue_size(self) -> int:
        return len(_log_deque)



log = Logger()


__all__ = ["log", "set_log_level", "LOG_LEVELS", "redact_text"]


_refresh_config()
if _log_enabled:
    _clear_log_file()
    _start_writer_thread()


atexit.register(_stop_writer_thread)
