"""
Global task lifecycle management module
ç®¡ç†åº”ç”¨ç¨‹åºä¸­æ‰€æœ‰å¼‚æ­¥ä»»å¡ç„ç”Ÿå‘½å‘¨æœŸï¼Œç¡®ä¿æ­£ç¡®æ¸…ç†
"""

import asyncio
import weakref
from typing import Any, Dict, Set

from log import log


class TaskManager:
    """å…¨å±€å¼‚æ­¥ä»»å¡ç®¡ç†å™¨ - å•ä¾‹æ¨¡å¼"""

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._tasks: Set[asyncio.Task] = set()
        self._resources: Set[Any] = set()  # éœ€è¦å…³é—­ç„èµ„æº
        self._shutdown_event = asyncio.Event()
        self._initialized = True
        log.debug("TaskManager initialized")

    def register_task(self, task: asyncio.Task, description: str = None) -> asyncio.Task:
        """æ³¨å†Œä¸€ä¸ªä»»å¡ä¾›ç”Ÿå‘½å‘¨æœŸç®¡ç†"""
        self._tasks.add(task)
        task.add_done_callback(lambda t: self._tasks.discard(t))

        if description:
            task.set_name(description)

        log.debug(f"Registered task: {task.get_name() or 'unnamed'}")
        return task

    def create_task(self, coro, *, name: str = None) -> asyncio.Task:
        """åˆ›å»ºå¹¶æ³¨å†Œä¸€ä¸ªä»»å¡"""
        task = asyncio.create_task(coro, name=name)
        return self.register_task(task, name)

    def register_resource(self, resource: Any) -> Any:
        """æ³¨å†Œä¸€ä¸ªéœ€è¦æ¸…ç†ç„èµ„æºï¼ˆå¦‚HTTPå®¢æˆ·ç«¯ă€æ–‡ä»¶å¥æŸ„ç­‰ï¼‰"""
        # ä½¿ç”¨å¼±å¼•ç”¨é¿å…å¾ªç¯å¼•ç”¨
        self._resources.add(weakref.ref(resource))
        log.debug(f"Registered resource: {type(resource).__name__}")
        return resource

    async def shutdown(self, timeout: float = 30.0):
        """å…³é—­æ‰€æœ‰ä»»å¡å’Œèµ„æº"""
        log.info("TaskManager shutdown initiated")

        # è®¾ç½®å…³é—­æ ‡å¿—
        self._shutdown_event.set()

        # å–æ¶ˆæ‰€æœ‰æœªå®Œæˆç„ä»»å¡
        cancelled_count = 0
        for task in list(self._tasks):
            if not task.done():
                task.cancel()
                cancelled_count += 1

        if cancelled_count > 0:
            log.info(f"Cancelled {cancelled_count} pending tasks")

        # ç­‰å¾…æ‰€æœ‰ä»»å¡å®Œæˆï¼ˆåŒ…æ‹¬å–æ¶ˆï¼‰
        if self._tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._tasks, return_exceptions=True), timeout=timeout
                )
            except asyncio.TimeoutError:
                log.warning(f"Some tasks did not complete within {timeout}s timeout")

        # æ¸…ç†èµ„æº - æ”¹è¿›å¼±å¼•ç”¨å¤„ç†
        cleaned_resources = 0
        failed_resources = 0
        for resource_ref in list(self._resources):
            resource = resource_ref()
            if resource is not None:
                try:
                    if hasattr(resource, "close"):
                        if asyncio.iscoroutinefunction(resource.close):
                            await resource.close()
                        else:
                            resource.close()
                    elif hasattr(resource, "aclose"):
                        await resource.aclose()
                    cleaned_resources += 1
                except Exception as e:
                    log.warning(f"Failed to close resource {type(resource).__name__}: {e}")
                    failed_resources += 1
            # å¦‚æœå¼±å¼•ç”¨å·²å¤±æ•ˆï¼Œèµ„æºå·²ç»è¢«è‡ªå¨å›æ”¶ï¼Œæ— éœ€æ“ä½œ

        if cleaned_resources > 0:
            log.info(f"Cleaned up {cleaned_resources} resources")
        if failed_resources > 0:
            log.warning(f"Failed to clean {failed_resources} resources")

        self._tasks.clear()
        self._resources.clear()
        log.info("TaskManager shutdown completed")

    @property
    def is_shutdown(self) -> bool:
        """æ£€æŸ¥æ˜¯å¦å·²ç»å¼€å§‹å…³é—­"""
        return self._shutdown_event.is_set()

    def get_stats(self) -> Dict[str, int]:
        """è·å–ä»»å¡ç®¡ç†ç»Ÿè®¡ä¿¡æ¯"""
        return {
            "active_tasks": len(self._tasks),
            "registered_resources": len(self._resources),
            "is_shutdown": self.is_shutdown,
        }


# å…¨å±€ä»»å¡ç®¡ç†å™¨å®ä¾‹
task_manager = TaskManager()


def create_managed_task(coro, *, name: str = None) -> asyncio.Task:
    """åˆ›å»ºä¸€ä¸ªè¢«ç®¡ç†ç„å¼‚æ­¥ä»»å¡ç„ä¾¿æ·å‡½æ•°"""
    return task_manager.create_task(coro, name=name)


def register_resource(resource: Any) -> Any:
    """æ³¨å†Œèµ„æºç„ä¾¿æ·å‡½æ•°"""
    return task_manager.register_resource(resource)


async def shutdown_all_tasks(timeout: float = 30.0):
    """å…³é—­æ‰€æœ‰ä»»å¡ç„ä¾¿æ·å‡½æ•°"""
    await task_manager.shutdown(timeout)
