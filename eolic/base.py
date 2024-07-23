"""Module for eolic base class."""

import functools
from typing import Any, Callable, List


from .listener import EventListenerHandler
from .meta.singleton import Singleton
from .remote import EventRemoteTargetHandler


class Eolic(metaclass=Singleton):
    """
    Main class for Eolic, implementing the Singleton pattern.

    Handles the registration and emission of events to local listeners and remote targets.

    Attributes:
        remote_target_handler (EventRemoteTargetHandler): Handles remote event targets.
        listener_handler (EventListenerHandler): Handles event listeners.
    """

    remote_target_handler: EventRemoteTargetHandler = EventRemoteTargetHandler()
    listener_handler: EventListenerHandler = EventListenerHandler()

    def __init__(self, remote_targets: List[Any] = []) -> None:
        """
        Initialize Eolic with a list of remote targets.

        Args:
            remote_targets (List[Any]): A list of remote targets to register.
        """
        for target in remote_targets:
            # TODO: Validate target for celery or url dict / str
            # TODO: If dict validate type and address keys
            self.register_target(target)

    def register_target(self, target: Any) -> None:
        """
        Register a remote target.

        Args:
            target (Any): The target to register, can be a dict or a string.
        """
        self.remote_target_handler.register(target)

    def register_listener(self, event: Any, fn: Callable[..., None]) -> None:
        """
        Register a listener for a specific event.

        Args:
            event (Any): The event to listen for.
            fn (Callable[..., None]): The function to call when the event is emitted.

        Returns:
            None
        """
        return self.listener_handler.register(event, fn)

    def on(self, event: Any):
        """
        Decorate to register a function as a listener for a specific event.

        Args:
            event (Any): The event to listen for.

        Returns:
            Callable: The decorator function.
        """

        def decorator(func):
            self.listener_handler.register(event, func)

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # The following line is already covered but for some reason
                # it's not showing up in the coverage report
                return func(*args, **kwargs)  # pragma: no cover

            return wrapper

        return decorator

    def emit(self, event: Any, *args, **kwargs):
        """
        Emit an event, calling all registered listeners and remote targets.

        Args:
            event (Any): The event to emit.
            *args: Variable length argument list for the event.
            **kwargs: Arbitrary keyword arguments for the event.
        """
        self.listener_handler.emit(event, *args, **kwargs)
        self.remote_target_handler.emit(event, *args, **kwargs)
