"""
Module for handling remote event targets and dispatchers in Eolic.

This module includes classes for managing remote event targets, dispatching events
to remote targets, and handling different types of event remote targets.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import requests

from .task_manager import TaskManager

from .helpers.coroutines import run_coroutine

from .model import (
    EventDTO,
    EventRemoteTarget,
    EventRemoteTargetType,
    EventRemoteURLTarget,
    EventRemoteCeleryTarget,
)
from .helpers.modules import is_module_installed, get_module


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

    @staticmethod
    def _parse_target(target: Union[str, Dict[str, Any]]) -> EventRemoteTarget:
        """
        Parse and convert a target to an EventRemoteTarget instance.

        Args:
            target (Any): The target to parse, can be a string or a dictionary.

        Returns:
            EventRemoteTarget: Parsed remote target.
        """
        if isinstance(target, str):
            target = {"type": "url", "address": target}

        if not isinstance(target, dict):
            raise TypeError(
                "Target needs to be of type str or Dict[str, str] but received {}".format(
                    type(target)
                )
            )

        target_type = target.get("type")

        if not isinstance(target_type, str):
            raise TypeError(
                "Target type needs to be of type str but received {}".format(
                    type(target_type)
                )
            )

        event_remote_target_type = EventRemoteTargetType[target_type]

        if event_remote_target_type == EventRemoteTargetType.url:
            return EventRemoteURLTarget(
                type=event_remote_target_type,
                address=target["address"],
                headers=target.get("headers", {}),
                events=target.get("events"),
            )

        elif event_remote_target_type == EventRemoteTargetType.celery:
            address = str(target["address"])
            events: Optional[List[Any]] = target.get("events")
            queue_name = str(target.get("queue_name"))
            function_name = str(target.get("function_name"))

            return EventRemoteCeleryTarget(
                type=event_remote_target_type,
                address=address,
                events=events,
                queue_name=queue_name,
                function_name=function_name,
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

        if isinstance(target, EventRemoteCeleryTarget):
            return EventRemoteCeleryDispatcher(target)

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


class EventRemoteCeleryDispatcher(EventRemoteDispatcher):
    """Dispatcher for Celery remote targets."""

    def __init__(self, target: EventRemoteCeleryTarget) -> None:
        """
        Initialize the Celery dispatcher with a target.

        Args:
            target (EventRemoteCeleryTarget): The Celery remote target.
        """
        self.target = target

        if not is_module_installed("celery"):
            raise Exception(
                "Celery Integration is not installed. "
                "Please install eolic[celery] (using celery extras) to use this integration."
            )

        self.celery = get_module("celery").Celery(self.target.address)

    async def dispatch(self, event: Any, *args, **kwargs) -> None:
        """
        Dispatch the event to the URL remote target.

        Args:
            event (Any): The event to dispatch.
            *args: Variable length argument list for the event.
            **kwargs: Arbitrary keyword arguments for the event.
        """
        event_value = str(event)

        if isinstance(event, Enum):
            event_value = event.value

        task = self.celery.send_task(
            self.target.function_name,
            args=[event_value, *args],
            kwargs=kwargs,
            queue=self.target.queue_name,
        )

        logging.debug(f"Celery task id {task}")
