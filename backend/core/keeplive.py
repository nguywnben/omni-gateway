"""Internal implementation detail."""

import asyncio
from typing import Optional

from config import get_keepalive_interval, get_keepalive_url
from log import log
from core.httpx_client import get_async


class KeepAliveService:
    """Internal implementation detail."""
    def __init__(self):
        self._task: Optional[asyncio.Task] = None

    async def _run(self, url: str, interval: int):
        """Internal implementation detail."""
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
        """Internal implementation detail."""
        if self._task and not self._task.done():

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
        """Internal implementation detail."""
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            log.info("[KeepAlive] Keep-alive service stopped")
        self._task = None

    async def restart(self):
        """Internal implementation detail."""
        await self.stop()
        await self.start()

    @property
    def is_running(self) -> bool:
        """Internal implementation detail."""
        return self._task is not None and not self._task.done()



keepalive_service = KeepAliveService()
