"""Module for handling event listeners in Eolic."""

from ast import Tuple
from typing import Any, Callable, Dict, List, Mapping

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

        for listener in listeners:
            listener(*args, **kwargs)

    def clear(self) -> None:
        """
        Clear all registered listeners and their mappings.

        This method removes all listeners and clears the listener map.
        """
        self.listeners.clear()
        self._listener_map.clear()
