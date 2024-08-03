"""Module for handling taslk in Eolic."""

import asyncio
from typing import Any, Callable
from eolic.helpers.coroutines import run_coroutine


class TaskManager:
    """Handles the creation and management of asynchronous tasks."""

    def create_task(self, func: Callable[..., Any], *args, **kwargs) -> None:
        """Create a new asynchronous task."""

        async def _async_func():
            if not asyncio.iscoroutinefunction(func):
                func(*args, **kwargs)
            else:
                await func(*args, **kwargs)

        asyncio.create_task(_async_func())

    def wait_for_all(self) -> None:
        """Wait for all asynchronous tasks to complete."""
        run_coroutine(self._wait_for_all_async)

    async def _wait_for_all_async(self) -> None:
        """Asynchronously wait for all tasks to complete."""
        pending = asyncio.all_tasks() - {asyncio.current_task()}
        await asyncio.gather(*pending)
