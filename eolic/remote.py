"""
Module for handling remote event targets and dispatchers in Eolic.

This module includes classes for managing remote event targets, dispatching events
to remote targets, and handling different types of event remote targets.
"""

from __future__ import annotations

from enum import Enum
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List
import requests

from eolic.task_manager import TaskManager

from .helpers.coroutines import run_coroutine

from .model import (
    EventDTO,
    EventRemoteTarget,
    EventRemoteTargetType,
    EventRemoteURLTarget,
)


class EventRemoteTargetHandler(TaskManager):
    """
    Handles registration and emission of events to remote targets.

    Attributes:
        targets (List[EventRemoteTarget]): List of registered remote targets.
        futures (List[Future]): List of futures for asynchronous tasks.
        executor (ThreadPoolExecutor): Executor for handling asynchronous tasks.
    """

    targets: List[EventRemoteTarget] = []

    def __init__(self) -> None:
        """Initialize the EventRemoteTargetHandler."""
        super().__init__()

    def _parse_target(self, target: Any) -> EventRemoteTarget:
        """
        Parse and convert a target to an EventRemoteTarget instance.

        Args:
            target (Any): The target to parse, can be a string or a dictionary.

        Returns:
            EventRemoteTarget: Parsed remote target.
        """
        if isinstance(target, str):
            return EventRemoteURLTarget(
                type=EventRemoteTargetType("url"), address=target
            )

        if isinstance(target, dict):
            return EventRemoteURLTarget(
                type=EventRemoteTargetType("url"),
                address=target["address"],
                headers=target.get("headers", {}),
                events=target.get("events"),
            )

        return EventRemoteTarget(**target)

    def register(self, target: Any) -> None:
        """
        Register a new remote target.

        Args:
            target (Any): The target to register.
        """
        self.targets.append(self._parse_target(target))

    def clear(self) -> None:
        """Clear all registered targets and futures."""
        self.targets.clear()

    def emit(self, event: Any, *args, **kwargs) -> None:
        """
        Emit an event to all registered remote targets.

        Args:
            event (Any): The event to emit.
            *args: Variable length argument list for the event.
            **kwargs: Arbitrary keyword arguments for the event.
        """
        run_coroutine(self._emit_async, event, *args, **kwargs)

    async def _emit_async(self, event: Any, *args, **kwargs) -> None:
        """
        Asynchronously emit an event to all registered remote targets.

        Args:
            event (Any): The event to emit.
            *args: Variable length argument list for the event.
            **kwargs: Arbitrary keyword arguments for the event.
        """
        dispatcher_factory = EventRemoteDispatcherFactory()

        for target in self.targets:
            dispatcher = dispatcher_factory.create(target)

            if target.events is None or event in target.events:
                self.create_task(dispatcher.dispatch, event, *args, **kwargs)


class EventRemoteDispatcherFactory:
    """Factory class for creating event remote dispatchers."""

    def create(self, target: EventRemoteTarget) -> EventRemoteDispatcher:
        """
        Create a dispatcher for a given remote target.

        Args:
            target (EventRemoteTarget): The remote target for which to create a dispatcher.

        Returns:
            EventRemoteDispatcher: The created dispatcher.

        Raises:
            NotImplementedError: If the target type is not implemented.
        """
        if isinstance(target, EventRemoteURLTarget):
            return EventRemoteURLDispatcher(target)

        raise NotImplementedError(
            f"EventRemoteDispatcher for {target.type} not implemented"
        )


class EventRemoteDispatcher(ABC):
    """Abstract base class for event remote dispatchers."""

    @abstractmethod
    async def dispatch(self, event: Any, *args, **kwargs) -> None:
        """
        Dispatch an event to the remote target.

        Args:
            event (Any): The event to dispatch.
            *args: Variable length argument list for the event.
            **kwargs: Arbitrary keyword arguments for the event.

        Raises:
            NotImplementedError: If the abstract method is not implemented.
        """
        raise NotImplementedError("Dispatch should be implemented.")


class EventRemoteURLDispatcher(EventRemoteDispatcher):
    """Dispatcher for URL remote targets."""

    def __init__(self, target: EventRemoteURLTarget) -> None:
        """
        Initialize the URL dispatcher with a target.

        Args:
            target (EventRemoteURLTarget): The URL remote target.
        """
        self.target = target

    def _build_request(self, event: Any, *args, **kwargs) -> Dict[str, Any]:
        """
        Build the request payload for the event.

        Args:
            event (Any): The event to dispatch.
            *args: Variable length argument list for the event.
            **kwargs: Arbitrary keyword arguments for the event.

        Returns:
            Dict[str, Any]: The payload to send to the remote target.
        """
        event_value = str(event)

        if isinstance(event, Enum):
            event_value = event.value

        dto = EventDTO(event=event_value, args=args, kwargs=kwargs)
        return dto.model_dump()

    async def dispatch(self, event: Any, *args, **kwargs) -> None:
        """
        Dispatch the event to the URL remote target.

        Args:
            event (Any): The event to dispatch.
            *args: Variable length argument list for the event.
            **kwargs: Arbitrary keyword arguments for the event.
        """
        response = requests.post(
            self.target.address,
            json=self._build_request(event, *args, **kwargs),
            headers=self.target.headers,
            timeout=10,
        )
        logging.debug(f"Response from {self.target.address}: {response.status_code}")
