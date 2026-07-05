"""Internal implementation detail."""

import asyncio
import weakref
from typing import Any, Dict, Set

from log import log


class TaskManager:
    """Internal implementation detail."""
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
        self._resources: Set[Any] = set()
        self._shutdown_event = asyncio.Event()
        self._initialized = True
        log.debug("TaskManager initialized")

    def register_task(self, task: asyncio.Task, description: str = None) -> asyncio.Task:
        """Internal implementation detail."""
        self._tasks.add(task)
        task.add_done_callback(lambda t: self._tasks.discard(t))

        if description:
            task.set_name(description)

        log.debug(f"Registered task: {task.get_name() or 'unnamed'}")
        return task

    def create_task(self, coro, *, name: str = None) -> asyncio.Task:
        """Internal implementation detail."""
        task = asyncio.create_task(coro, name=name)
        return self.register_task(task, name)

    def register_resource(self, resource: Any) -> Any:
        """Internal implementation detail."""
        self._resources.add(weakref.ref(resource))
        log.debug(f"Registered resource: {type(resource).__name__}")
        return resource

    async def shutdown(self, timeout: float = 30.0):
        """Internal implementation detail."""
        log.info("TaskManager shutdown initiated")


        self._shutdown_event.set()


        cancelled_count = 0
        for task in list(self._tasks):
            if not task.done():
                task.cancel()
                cancelled_count += 1

        if cancelled_count > 0:
            log.info(f"Cancelled {cancelled_count} pending tasks")


        if self._tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*self._tasks, return_exceptions=True), timeout=timeout
                )
            except asyncio.TimeoutError:
                log.warning(f"Some tasks did not complete within {timeout}s timeout")


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


        if cleaned_resources > 0:
            log.info(f"Cleaned up {cleaned_resources} resources")
        if failed_resources > 0:
            log.warning(f"Failed to clean {failed_resources} resources")

        self._tasks.clear()
        self._resources.clear()
        log.info("TaskManager shutdown completed")

    @property
    def is_shutdown(self) -> bool:
        """Internal implementation detail."""
        return self._shutdown_event.is_set()

    def get_stats(self) -> Dict[str, int]:
        """Internal implementation detail."""
        return {
            "active_tasks": len(self._tasks),
            "registered_resources": len(self._resources),
            "is_shutdown": self.is_shutdown,
        }



task_manager = TaskManager()


def create_managed_task(coro, *, name: str = None) -> asyncio.Task:
    """Internal implementation detail."""
    return task_manager.create_task(coro, name=name)


def register_resource(resource: Any) -> Any:
    """Internal implementation detail."""
    return task_manager.register_resource(resource)


async def shutdown_all_tasks(timeout: float = 30.0):
    """Internal implementation detail."""
    await task_manager.shutdown(timeout)
