"""Module for handling tasks in Eolic."""

import asyncio
import atexit
import signal
from typing import Any, Callable
from .helpers.coroutines import run_coroutine


class TaskManager:
    """Handles the creation and management of asynchronous tasks."""

    def __init__(self) -> None:
        """Initialize the TaskManager."""
        self._register_cleanup()

    def _register_cleanup(self) -> None:
        """Register cleanup functions for the task manager to run before exiting the application."""
        atexit.register(self._cleanup)
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _cleanup(self):
        """Clean up the task manager."""
        self.wait_for_all()

    def _handle_signal(self, *_) -> None:
        """Handle termination signals."""
        self._cleanup()

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
