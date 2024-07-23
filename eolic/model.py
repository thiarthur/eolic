"""Module for eolic models."""

from enum import Enum
from typing import Mapping, Tuple, Any, Callable, Dict, List, Optional

from pydantic import BaseModel


class EventDTO(BaseModel):
    """
    Model for event data transfer objects.

    Attributes:
        event: The event to be emitted.
        data: The data to be sent with the event.
    """

    event: Any
    args: Tuple = ()
    kwargs: Mapping = {}


class EventRemoteTargetType(str, Enum):
    """
    Enum for types of event remote targets.

    Attributes:
        url: URL type target.
        celery: Celery type target.
        rabbitmq: RabbitMQ type target.
    """

    url = "url"
    celery = "celery"
    rabbitmq = "rabbitmq"


class EventRemoteTarget(BaseModel):
    """
    Base model for event remote targets.

    Attributes:
        type: The type of the remote target.
        address: The address of the remote target.
        events: Optional list of events that the target is interested in.
    """

    type: EventRemoteTargetType
    address: str
    events: Optional[List[Any]] = None


class EventRemoteURLTarget(EventRemoteTarget):
    """
    Model for URL event remote targets.

    Attributes:
        headers: Dictionary of headers to include in requests to the target.
    """

    headers: Dict[str, Any] = {}


class EventListener(BaseModel):
    """
    Model for event listeners.

    Attributes:
        event: The event the listener is associated with.
        listener: The callback function to be executed when the event is emitted.
    """

    event: Any
    listener: Callable[..., None]
