"""
æ—¥å¿—æ¨¡å— - ä½¿ç”¨ç¯å¢ƒå˜é‡é…ç½®
"""

import os
import sys
import threading
from datetime import datetime
from collections import deque
import atexit

from paths import DEFAULT_LOG_FILE

# æ—¥å¿—çº§åˆ«å®ä¹‰
LOG_LEVELS = {"debug": 0, "info": 1, "warning": 2, "error": 3, "critical": 4}

# æ–‡ä»¶å†™å…¥ç¶æ€æ ‡å¿—ï¼ˆä»…ç”± writer çº¿ç¨‹ä¿®æ”¹ï¼Œæ— éœ€é”ä¿æ¤ï¼‰
_file_writing_disabled = False
_disable_reason = None

# å…¨å±€æ–‡ä»¶å¥æŸ„ï¼ˆä»…ç”± writer çº¿ç¨‹è®¿é—®ï¼Œæ— éœ€æ–‡ä»¶é”ï¼‰
_log_file_handle = None

# -----------------------------------------------------------------
# é«˜æ€§èƒ½æ— é”é˜Ÿåˆ—ï¼ç”¨ deque + Condition æ›¿ä»£ Queue
# deque.append / deque.popleft åœ¨ CPython ä¸­å— GIL ä¿æ¤ï¼Œæ˜¯åŸå­æ“ä½œï¼Œ
# ä¸éœ€è¦é¢å¤–ç„ Lock åå…¥é˜Ÿä¿æ¤ï¼Œåªç”¨ Condition å"æœ‰æ•°æ®"é€çŸ¥ă€‚
# -----------------------------------------------------------------
_log_deque: deque = deque()
_deque_condition = threading.Condition(threading.Lock())
_writer_thread = None
_writer_running = False

# -----------------------------------------------------------------
# ç¼“å­˜æ—¥å¿—çº§åˆ«ï¼Œé¿å…æ¯æ¬¡éƒ½è¯» os.getenvï¼ˆé«˜å¹¶å‘çƒ­è·¯å¾„ï¼‰
# -----------------------------------------------------------------
_cached_log_level: int = LOG_LEVELS["info"]
_cached_log_file: str = str(DEFAULT_LOG_FILE)
# OGW_ENABLE_LOG=0/false/no/off æ—¶å½»åº•å…³é—­æ—¥å¿—
_log_enabled: bool = True


def _refresh_config():
    """ä»ç¯å¢ƒå˜é‡åˆ·æ–°ç¼“å­˜é…ç½®ï¼ˆæ¨¡å—å è½½æ—¶åéœ€è¦æ—¶è°ƒç”¨ï¼‰"""
    global _cached_log_level, _cached_log_file, _log_enabled
    level = os.getenv("OGW_LOG_LEVEL", "info").lower()
    _cached_log_level = LOG_LEVELS.get(level, LOG_LEVELS["info"])
    _cached_log_file = os.getenv("OGW_LOG_FILE", str(DEFAULT_LOG_FILE))
    _log_enabled = os.getenv("OGW_ENABLE_LOG", "1").strip().lower() not in ("0", "false", "no", "off")


def _get_current_log_level() -> int:
    return _cached_log_level


def _get_log_file_path() -> str:
    return _cached_log_file


# -----------------------------------------------------------------
# æ–‡ä»¶å¥æŸ„ç®¡ç†ï¼ˆä»…åœ¨ writer çº¿ç¨‹å†…è°ƒç”¨ï¼Œä¸éœ€è¦ _file_lockï¼‰
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
        # ä½¿ç”¨è¾ƒå¤§ç¼“å†²åŒºï¼ˆ64 KBï¼‰ï¼Œç”± writer çº¿ç¨‹å®æœŸ flushï¼Œå‡å°‘ç³»ç»Ÿè°ƒç”¨
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
    """æ¸…ç©ºæ—¥å¿—æ–‡ä»¶ï¼ˆå¯å¨æ—¶è°ƒç”¨ï¼Œæ­¤æ—¶ writer çº¿ç¨‹å°æœªå¯å¨ï¼Œç›´æ¥æ“ä½œå®‰å…¨ï¼‰"""
    global _file_writing_disabled, _disable_reason
    try:
        log_dir = os.path.dirname(os.path.abspath(_cached_log_file))
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(_cached_log_file, "w", encoding="utf-8") as f:
            pass  # è¦†ç›–æ¸…ç©º
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
# Writer çº¿ç¨‹ï¼æ‰¹é‡ä» deque å–å‡ºå¹¶å†™å…¥ï¼Œå‡å°‘ç³»ç»Ÿè°ƒç”¨æ¬¡æ•°
# -----------------------------------------------------------------
_BATCH_SIZE = 1000          # å•æ¬¡æœ€å¤æ‰¹é‡å†™å…¥æ¡æ•°
_FLUSH_INTERVAL = 2      # ç§’ï¼æ— æ–°æ¶ˆæ¯æ—¶å¼ºåˆ¶ flush å‘¨æœŸ


def _log_writer_worker():
    global _writer_running

    last_flush_time = 0.0

    while True:
        # ç­‰å¾…æ•°æ®æˆ–è¶…æ—¶
        with _deque_condition:
            if not _log_deque and _writer_running:
                _deque_condition.wait(timeout=_FLUSH_INTERVAL)

            # æ‰¹é‡å–å‡º
            batch = []
            for _ in range(_BATCH_SIZE):
                if _log_deque:
                    batch.append(_log_deque.popleft())
                else:
                    break

        if batch and not _file_writing_disabled:
            # ä¸€æ¬¡ write è°ƒç”¨æå®æ•´æ‰¹ï¼Œæœ€å¤§åŒ–å‡å°‘ç³»ç»Ÿè°ƒç”¨
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

        # å®æ—¶ flush
        now = _now_ts()
        if now - last_flush_time >= _FLUSH_INTERVAL:
            if _log_file_handle is not None:
                try:
                    _log_file_handle.flush()
                except Exception:
                    pass
            last_flush_time = now

        # é€€å‡ºæ¡ä»¶ï¼å·²åœæ­¢ + deque å·²æ¸…ç©º
        if not _writer_running and not _log_deque:
            break

    # æœ€ç»ˆ flush & close
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
    # å”¤é†’ writer çº¿ç¨‹è®©å®ƒèƒ½æ„ŸçŸ¥é€€å‡ºä¿¡å·
    with _deque_condition:
        _deque_condition.notify_all()

    if _writer_thread and _writer_thread.is_alive():
        _writer_thread.join(timeout=3.0)


# -----------------------------------------------------------------
# å…¥é˜Ÿï¼ˆçƒ­è·¯å¾„ï¼Œæè½»é‡ï¼‰
# -----------------------------------------------------------------
_MAX_QUEUE_SIZE = 5000  # é˜²æ­¢æç«¯æƒ…å†µå†…å­˜æ— é™å¢é•¿


def _write_to_file(message: str):
    if _file_writing_disabled:
        return
    # deque.append åœ¨ CPython å— GIL ä¿æ¤ï¼Œæ— éœ€é¢å¤–é”
    if len(_log_deque) >= _MAX_QUEUE_SIZE:
        return  # è¿‡è½½ä¿æ¤ï¼ä¸¢å¼ƒè€Œéé˜»å¡
    _log_deque.append(message)
    # éé˜»å¡é€çŸ¥ writerï¼ˆacquire å¤±è´¥ç›´æ¥è·³è¿‡ï¼Œä¸å½±å“ä¸»çº¿ç¨‹ï¼‰
    if _deque_condition.acquire(blocking=False):
        try:
            _deque_condition.notify()
        finally:
            _deque_condition.release()


# -----------------------------------------------------------------
# æ ¸å¿ƒæ—¥å¿—å‡½æ•°ï¼ˆçƒ­è·¯å¾„ï¼‰
# -----------------------------------------------------------------

def _log(level: str, message: str):
    # æœ€å¿«çŸ­è·¯ï¼æ—¥å¿—æ•´ä½“å·²ç¦ç”¨æ—¶ç›´æ¥è¿”å›ï¼Œé›¶å¼€é”€
    if not _log_enabled:
        return

    level = level.lower()
    level_val = LOG_LEVELS.get(level)
    if level_val is None:
        print(f"Warning: Unknown log level '{level}'", file=sys.stderr)
        return

    # çƒ­è·¯å¾„ï¼ç›´æ¥ä¸ç¼“å­˜å€¼æ¯”è¾ƒï¼Œæ— å‡½æ•°è°ƒç”¨å¼€é”€
    if level_val < _cached_log_level:
        return

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [{level.upper()}] {message}"

    if level in ("error", "critical"):
        print(entry, file=sys.stderr)
    else:
        print(entry)

    _write_to_file(entry)


def set_log_level(level: str):
    """å¨æ€è®¾ç½®æ—¥å¿—çº§åˆ«ï¼ˆåŒæ—¶æ›´æ–°ç¼“å­˜ï¼‰"""
    global _cached_log_level
    level = level.lower()
    if level not in LOG_LEVELS:
        print(f"Warning: Unknown log level '{level}'. Valid levels: {', '.join(LOG_LEVELS.keys())}")
        return False
    _cached_log_level = LOG_LEVELS[level]
    return True


class Logger:
    """æ”¯æŒ log('info', 'msg') å’Œ log.info('msg') ä¸¤ç§è°ƒç”¨æ–¹å¼"""

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
        """æ‰‹å¨å…³é—­ï¼ˆä¼˜é›…é€€å‡ºç”¨ï¼‰"""
        _stop_writer_thread()

    def get_queue_size(self) -> int:
        return len(_log_deque)


# å¯¼å‡ºå…¨å±€æ—¥å¿—å®ä¾‹
log = Logger()

# å¯¼å‡ºç„å…¬å…±æ¥å£
__all__ = ["log", "set_log_level", "LOG_LEVELS"]

# æ¨¡å—å è½½æ—¶ï¼è¯»å–é…ç½®ç¼“å­˜ â†’ æ¸…ç©ºæ—¥å¿—æ–‡ä»¶ â†’ å¯å¨ writer çº¿ç¨‹
_refresh_config()
if _log_enabled:
    _clear_log_file()
    _start_writer_thread()

# æ³¨å†Œé€€å‡ºæ¸…ç†
atexit.register(_stop_writer_thread)

# ä½¿ç”¨è¯´æ˜:
# 1. è®¾ç½®æ—¥å¿—çº§åˆ«: export OGW_LOG_LEVEL=debug  (æˆ–åœ¨ .env ä¸­è®¾ç½®)
# 2. è®¾ç½®æ—¥å¿—æ–‡ä»¶: export OGW_LOG_FILE=backend/data/logs/omni-gateway.log (æˆ–åœ¨ .env ä¸­è®¾ç½®)
# 3. æ—¥å¿—çº§åˆ«å·²ç¼“å­˜ï¼Œçƒ­è·¯å¾„é›¶ os.getenv è°ƒç”¨
# 4. å†™å…¥çº¿ç¨‹æ‰¹é‡å¤„ç†ï¼ˆæœ€å¤ 200 æ¡/æ¬¡ï¼‰ï¼Œ64 KB ç¼“å†²åŒºï¼Œæ¯ 0.5 s flush ä¸€æ¬¡
# 5. é˜Ÿåˆ—ä¸é™ 5000 æ¡ï¼Œè¶…å‡ºæ—¶ä¸¢å¼ƒæ–°æ—¥å¿—ï¼ˆè¿‡è½½ä¿æ¤ï¼Œä¸é˜»å¡ä¸»çº¿ç¨‹ï¼‰
# 6. å¨æ€è°ƒæ•´çº§åˆ«ï¼set_log_level('debug') ç«‹å³ç”Ÿæ•ˆ
# 7. å½»åº•å…³é—­æ—¥å¿—ï¼ˆæœ€é«˜æ€§èƒ½ï¼‰ï¼export OGW_ENABLE_LOG=0  (æˆ– false/no/off)
#    å…³é—­åä¸ä¼å¯å¨ writer çº¿ç¨‹ă€ä¸å†™æ–‡ä»¶ă€ä¸æ‰“å°æ§åˆ¶å°ï¼Œ_log ç›´æ¥ return
