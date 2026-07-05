"""
å…±äº«å·¥å…·æ¨¡å— - åŒ…å«WebSocketè¿æ¥ç®¡ç†ă€å·¥å…·å‡½æ•°ç­‰
"""

import os
import time
from collections import deque
from typing import Set

from fastapi import HTTPException, WebSocket
from starlette.websockets import WebSocketState

import config
from log import log


# =============================================================================
# WebSocketè¿æ¥ç®¡ç†
# =============================================================================


class ConnectionManager:
    def __init__(self, max_connections: int = 3):  # è¿›ä¸€æ­¥é™ä½æœ€å¤§è¿æ¥æ•°
        # ä½¿ç”¨åŒç«¯é˜Ÿåˆ—ä¸¥æ ¼é™åˆ¶å†…å­˜ä½¿ç”¨
        self.active_connections: deque = deque(maxlen=max_connections)
        self.max_connections = max_connections
        self._last_cleanup = 0
        self._cleanup_interval = 120  # 120ç§’æ¸…ç†ä¸€æ¬¡æ­»è¿æ¥

    async def connect(self, websocket: WebSocket):
        # è‡ªå¨æ¸…ç†æ­»è¿æ¥
        self._auto_cleanup()

        # é™åˆ¶æœ€å¤§è¿æ¥æ•°ï¼Œé˜²æ­¢å†…å­˜æ— é™å¢é•¿
        if len(self.active_connections) >= self.max_connections:
            await websocket.close(code=1008, reason="Too many connections")
            return False

        await websocket.accept()
        self.active_connections.append(websocket)
        log.debug(f"WebSocket connection established, current connections: {len(self.active_connections)}")
        return True

    def disconnect(self, websocket: WebSocket):
        # ä½¿ç”¨æ›´é«˜æ•ˆç„æ–¹å¼ç§»é™¤è¿æ¥
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass  # è¿æ¥å·²ä¸å­˜åœ¨
        log.debug(f"WebSocket disconnected, number of current connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        # ä½¿ç”¨æ›´é«˜æ•ˆç„æ–¹å¼å¤„ç†å¹¿æ’­ï¼Œé¿å…ç´¢å¼•æ“ä½œ
        dead_connections = []
        for conn in self.active_connections:
            try:
                await conn.send_text(message)
            except Exception:
                dead_connections.append(conn)

        # æ‰¹é‡ç§»é™¤æ­»è¿æ¥
        for dead_conn in dead_connections:
            self.disconnect(dead_conn)

    def _auto_cleanup(self):
        """è‡ªå¨æ¸…ç†æ­»è¿æ¥"""
        current_time = time.time()
        if current_time - self._last_cleanup > self._cleanup_interval:
            self.cleanup_dead_connections()
            self._last_cleanup = current_time

    def cleanup_dead_connections(self):
        """æ¸…ç†å·²æ–­å¼€ç„è¿æ¥"""
        original_count = len(self.active_connections)
        # ä½¿ç”¨åˆ—è¡¨æ¨å¯¼å¼è¿‡æ»¤æ´»è·ƒè¿æ¥ï¼Œæ›´é«˜æ•ˆ
        alive_connections = deque(
            [
                conn
                for conn in self.active_connections
                if hasattr(conn, "client_state")
                and conn.client_state != WebSocketState.DISCONNECTED
            ],
            maxlen=self.max_connections,
        )

        self.active_connections = alive_connections
        cleaned = original_count - len(self.active_connections)
        if cleaned > 0:
            log.debug(f"Cleaned up {cleaned} dead connections, remaining connections: {len(self.active_connections)}")


# =============================================================================
# å·¥å…·å‡½æ•°
# =============================================================================


def is_mobile_user_agent(user_agent: str) -> bool:
    """æ£€æµ‹æ˜¯å¦ä¸ºç§»å¨è®¾å¤‡ç”¨æˆ·ä»£ç†"""
    if not user_agent:
        return False

    user_agent_lower = user_agent.lower()
    mobile_keywords = [
        "mobile",
        "android",
        "iphone",
        "ipad",
        "ipod",
        "blackberry",
        "windows phone",
        "samsung",
        "htc",
        "motorola",
        "nokia",
        "palm",
        "webos",
        "opera mini",
        "opera mobi",
        "fennec",
        "minimo",
        "symbian",
        "psp",
        "nintendo",
        "tablet",
    ]

    return any(keyword in user_agent_lower for keyword in mobile_keywords)


def validate_mode(mode: str = "code_assist") -> str:
    """
    éªŒè¯ mode å‚æ•°

    Args:
        mode: æ¨¡å¼å­—ç¬¦ä¸² ("code_assist" æˆ– "omni")

    Returns:
        str: éªŒè¯åç„ mode å­—ç¬¦ä¸²

    Raises:
        HTTPException: å¦‚æœ mode å‚æ•°æ— æ•ˆ
    """
    if mode not in ["code_assist", "omni"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid mode parameter: '{mode}'; only 'code_assist' or 'omni' are supported"
        )
    return mode


def get_env_locked_keys() -> Set:
    """è·å–è¢«ç¯å¢ƒå˜é‡é”å®ç„é…ç½®é”®é›†åˆ"""
    env_locked_keys = set()

    # ä½¿ç”¨ config.py ä¸­ç»Ÿä¸€ç»´æ¤ç„æ˜ å°„è¡¨
    for env_key, config_key in config.ENV_MAPPINGS.items():
        if os.getenv(env_key):
            env_locked_keys.add(config_key)

    return env_locked_keys
