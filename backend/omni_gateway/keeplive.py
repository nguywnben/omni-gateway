"""
ä¿æ´»æœå¡æ¨¡å—
å®æœŸå‘é…ç½®ç„URLå‘é€GETè¯·æ±‚ï¼Œä¿æŒæœå¡åœ¨çº¿
æœªé…ç½®ä¿æ´»URLæ—¶ä¸å¯å¨ä»»ä½•ä»»å¡ï¼Œé›¶èµ„æºå ç”¨
"""

import asyncio
from typing import Optional

from config import get_keepalive_interval, get_keepalive_url
from log import log
from omni_gateway.httpx_client import get_async


class KeepAliveService:
    """ä¿æ´»æœå¡ï¼å®æœŸå‘æŒ‡å®URLå‘é€GETè¯·æ±‚"""

    def __init__(self):
        self._task: Optional[asyncio.Task] = None

    async def _run(self, url: str, interval: int):
        """ä¿æ´»å¾ªç¯ï¼Œè¯»å–åˆ°æœ‰æ•ˆURLæ‰ä¼è¢«è°ƒç”¨"""
        log.info(f"[KeepAlive] Keep-alive task started, URL={url}, interval={interval}s")
        while True:
            try:
                response = await get_async(url, timeout=30.0)
                log.info(f"[KeepAlive] GET {url} -> {response.status_code}")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.warning(f"[KeepAlive] GET {url} failed: {e}")

            try:
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                raise

    async def start(self):
        """
        å¯å¨ä¿æ´»æœå¡ă€‚
        ä»…å½“é…ç½®äº†æœ‰æ•ˆç„ä¿æ´»URLæ—¶æ‰åˆ›å»ºåå°ä»»å¡ï¼Œå¦åˆ™é›¶å¼€é”€ă€‚
        """
        if self._task and not self._task.done():
            # å·²æœ‰ä»»å¡åœ¨è¿è¡Œï¼Œä¸é‡å¤å¯å¨
            return

        url = await get_keepalive_url()
        interval = await get_keepalive_interval()

        if not url or not url.strip():
            log.debug("[KeepAlive] No keep-alive URL configured, service will not start")
            return

        if interval <= 0:
            log.warning(f"[KeepAlive] Invalid keep-alive interval ({interval}), service will not start")
            return

        self._task = asyncio.create_task(
            self._run(url.strip(), interval), name="keepalive_service"
        )

    async def stop(self):
        """åœæ­¢ä¿æ´»æœå¡"""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            log.info("[KeepAlive] Keep-alive service stopped")
        self._task = None

    async def restart(self):
        """
        é‡å¯ä¿æ´»æœå¡ă€‚
        é…ç½®å˜æ›´æ—¶è°ƒç”¨ï¼Œä¼åœæ­¢æ—§ä»»å¡å¹¶æ ¹æ®æœ€æ–°é…ç½®å†³å®æ˜¯å¦å¯å¨æ–°ä»»å¡ă€‚
        """
        await self.stop()
        await self.start()

    @property
    def is_running(self) -> bool:
        """å½“å‰ä¿æ´»ä»»å¡æ˜¯å¦åœ¨è¿è¡Œ"""
        return self._task is not None and not self._task.done()


# å…¨å±€ä¿æ´»æœå¡å®ä¾‹
keepalive_service = KeepAliveService()
