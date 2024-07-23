"""
Module for handling remote event targets and dispatchers in Eolic.

This module includes classes for managing remote event targets, dispatching events
to remote targets, and handling different types of event remote targets.
"""

from __future__ import annotations

from enum import Enum
import logging
from abc import ABC, abstractmethod
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Dict, List

import requests

from .model import (
    EventDTO,
    EventRemoteTarget,
    EventRemoteTargetType,
    EventRemoteURLTarget,
)


class EventRemoteTargetHandler:
    """
    Handles registration and emission of events to remote targets.

    Attributes:
        targets (List[EventRemoteTarget]): List of registered remote targets.
        futures (List[Future]): List of futures for asynchronous tasks.
        executor (ThreadPoolExecutor): Executor for handling asynchronous tasks.
    """

    targets: List[EventRemoteTarget] = []
    futures: List[Future] = []
    executor: ThreadPoolExecutor

    def __init__(self) -> None:
        """Initialize the EventRemoteTargetHandler with a thread pool executor."""
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.futures = []

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
        self.futures.clear()

    def emit(self, event: Any, *args, **kwargs) -> None:
        """
        Emit an event to all registered remote targets.

        Args:
            event (Any): The event to emit.
            *args: Variable length argument list for the event.
            **kwargs: Arbitrary keyword arguments for the event.
        """
        for target in self.targets:
            if target.events is None or event in target.events:
                dispatcher = EventRemoteDispatcherFactory().create(target)
                future = self.executor.submit(
                    dispatcher.dispatch, event, *args, **kwargs
                )
                self.futures.append(future)

    def wait_for_all(self) -> None:
        """Wait for all asynchronous tasks to complete."""
        for future in self.futures:
            future.result()
        self.futures.clear()


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
    def dispatch(self, event: Any, *args, **kwargs) -> None:
        """
        Dispatch an event to the remote target.

        Args:
            event (Any): The event to dispatch.
            *args: Variable length argument list for the event.
            **kwargs: Arbitrary keyword arguments for the event.
        """
        pass


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

    def dispatch(self, event: Any, *args, **kwargs) -> None:
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
