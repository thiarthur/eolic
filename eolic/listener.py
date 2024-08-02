"""Module for handling event listeners in Eolic."""

from ast import Tuple
import asyncio
import inspect
from typing import Any, Callable, Dict, List, Mapping

from .helpers.coroutines import run_coroutine

from .model import EventListener


class EventListenerHandler:
    """
    Handles the registration and management of event listeners.

    Attributes:
        listeners (List[EventListener]): List of all registered event listeners.
        _listener_map (Dict[Any, List[Callable[..., Any]]]): Mapping of events to their listeners.
    """

    listeners: List[EventListener] = []
    _listener_map: Dict[Any, List[Callable[..., Any]]] = {}

    def register(self, event: Any, fn: Callable[..., None]) -> None:
        """
        Register a listener for a specific event.

        Args:
            event (Any): The event to listen for.
            fn (Callable[..., None]): The function to call when the event is emitted.
        """
        self.listeners.append(EventListener(event=event, listener=fn))
        if event not in self._listener_map:
            self._listener_map[event] = [fn]
        else:
            self._listener_map[event].append(fn)

    def emit(self, event: Any, *args: Tuple, **kwargs: Mapping[str, Any]) -> None:
        """
        Emit an event to all registered event handlers.

        Args:
            event (Any): The event to emit.
            *args: Variable length argument list for the event.
            **kwargs: Arbitrary keyword arguments for the event.
        """
        listeners = self._listener_map.get(event, [])
        run_coroutine(self._emit_async, listeners, *args, **kwargs)

    async def _emit_async(
        self, listeners: List[Callable[..., Any]], *args, **kwargs
    ) -> None:
        """
        Asynchronously emit an event to all registered remote targets.

        Args:
            event (Any): The event to emit.
            *args: Variable length argument list for the event.
            **kwargs: Arbitrary keyword arguments for the event.
        """
        tasks: List[asyncio.Task] = []
        sync_tasks = []
        for listener in listeners:
            if inspect.iscoroutinefunction(listener):
                task: asyncio.Task = asyncio.create_task(listener(*args, **kwargs))
                tasks.append(task)
            else:
                sync_tasks.append(listener)

        for listener in sync_tasks:
            listener(*args, **kwargs)

        await asyncio.gather(*tasks)

    def clear(self) -> None:
        """
        Clear all registered listeners and their mappings.

        This method removes all listeners and clears the listener map.
        """
        self.listeners.clear()
        self._listener_map.clear()
