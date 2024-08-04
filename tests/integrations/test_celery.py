import importlib.util
from enum import Enum

import pytest
from celery import Celery

from eolic.base import Eolic
from eolic.helpers.modules import get_module
from eolic.integrations.celery import CeleryIntegration
from eolic.model import EventDTO, EventRemoteCeleryTarget
from eolic.remote import (
    EventRemoteTargetHandler,
    EventRemoteCeleryDispatcher,
    EventRemoteDispatcherFactory,
)


@pytest.fixture
def app():
    """
    Fixture for creating a Celery app instance.

    Returns:
        Celery: An instance of Celery.
    """
    return Celery()


@pytest.fixture
def eolic():
    """
    Fixture for creating an Eolic instance.

    Returns:
        Eolic: An instance of Eolic.
    """
    return Eolic()


@pytest.fixture
def target_handler() -> EventRemoteTargetHandler:
    """
    Fixture to provide an instance of EventRemoteTargetHandler.

    Returns:
        EventRemoteTargetHandler: An instance of EventRemoteTargetHandler.
    """
    handler = EventRemoteTargetHandler()
    return handler


@pytest.fixture
def event_remote_celery_target() -> EventRemoteCeleryTarget:
    """
    Fixture to provide an instance of EventRemoteCeleryTarget.

    Returns:
        EventRemoteCeleryTarget: An instance of EventRemoteCeleryTarget.
    """
    return EventRemoteCeleryTarget(type="celery", address="amqp://localhost:5672")


@pytest.fixture
def target_celery_handler(
    event_remote_celery_target: EventRemoteCeleryTarget,
) -> EventRemoteCeleryDispatcher:
    """
    Fixture to provide an instance of EventRemoteTargetHandler.

    Args:
        event_remote_celery_target (EventRemoteCeleryTarget): The EventRemoteCeleryTarget instance.

    Returns:
        EventRemoteTargetHandler: An instance of EventRemoteTargetHandler.
    """
    event_remote_celery_dispatcher = EventRemoteCeleryDispatcher(
        event_remote_celery_target
    )

    return event_remote_celery_dispatcher


@pytest.fixture
def event_dto():
    """
    Fixture for creating an EventDTO instance.

    Returns:
        EventDTO: An instance of EventDTO with predefined attributes.
    """
    return EventDTO(event="test_event", args=("arg1",), kwargs={"key": "value"})


def test_celery_integration_init(eolic: Eolic, app: Celery):
    """
    Test initialization of CeleryIntegration.

    Args:
        eolic (Eolic): The Eolic instance.
        app (Celery): The Celery app instance.
    """
    integration = CeleryIntegration(app=app)
    eolic.setup_integration(integration)

    assert integration.eolic is not None
    assert integration.app == app
    assert integration.event_function == "events"
    assert integration.queue_name == "eolic"


def test_celery_integration_no_app():
    """
    Test that an exception is raised when CeleryIntegration is initialized with no app.
    """
    with pytest.raises(
        Exception, match="Please declare you app to setup the integration."
    ):
        CeleryIntegration(app=None)


def test_celery_not_installed(
    monkeypatch: pytest.MonkeyPatch,
    app: Celery,
    target_celery_handler: EventRemoteCeleryDispatcher,
    event_remote_celery_target: EventRemoteCeleryTarget,
):
    """
    Test that an exception is raised when Celery is not installed.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
        app (Celery): The Celery app instance.
        target_celery_handler (EventRemoteCeleryDispatcher): The EventRemoteCeleryDispatcher instance.
        event_remote_celery_target (EventRemoteCeleryTarget): The EventRemoteCeleryTarget instance.
    """
    monkeypatch.setattr(importlib.util, "find_spec", lambda _: None)

    with pytest.raises(Exception, match="Celery Integration is not installed.*"):
        CeleryIntegration(app=app)

    with pytest.raises(Exception, match="Celery Integration is not installed.*"):
        EventRemoteCeleryDispatcher(event_remote_celery_target)


def test_celery_empty_event_function(eolic: Eolic, app: Celery):
    """
    Test that an exception is raised when event_route is None.

    Args:
        eolic (Eolic): The Eolic instance.
        app (Celery): The Celery app instance.
    """
    integration = CeleryIntegration(app, event_function=None)
    with pytest.raises(
        Exception, match="Event function is required for Celery integration."
    ):
        eolic.setup_integration(integration)


def test_celery_listener_event(
    monkeypatch: pytest.MonkeyPatch, eolic: Eolic, app: Celery
):
    """
    Test that an exception is raised when event_route is None.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
        eolic (Eolic): The Eolic instance.
        app (Celery): The Celery app instance.
    """
    integration = CeleryIntegration(app, event_function="event")
    integration.setup(eolic)

    def mock_lambda_handler(event, *args, **kwargs):
        return event, args, kwargs

    monkeypatch.setattr(integration, "forward_event", mock_lambda_handler)

    integration.app.tasks["event"]("test_event", "arg1", key="value")


def test_celery_module(eolic: Eolic, app: Celery):
    """
    Test that an exception is raised when event_route is None.

    Args:
        eolic (Eolic): The Eolic instance.
        app (Celery): The Celery app instance.
    """
    assert isinstance(get_module("celery").Celery(), Celery)


def test_parse_celery_target(target_handler: EventRemoteTargetHandler) -> None:
    """
    Test parsing a dictionary target.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    target = {
        "type": "celery",
        "address": "amqp://localhost:5672",
        "queue_name": "q",
        "function_name": "f",
    }

    parsed_target = target_handler._parse_target(target)

    assert isinstance(parsed_target, EventRemoteCeleryTarget)
    assert parsed_target.address == "amqp://localhost:5672"
    assert parsed_target.function_name == "f"
    assert parsed_target.queue_name == "q"


@pytest.mark.asyncio
async def test_target_celery_handler(
    monkeypatch: pytest.MonkeyPatch,
    target_celery_handler: EventRemoteCeleryDispatcher,
) -> None:
    """
    Test parsing a dictionary target.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
        target_celery_handler (EventRemoteCeleryDispatcher): An instance of EventRemoteCeleryDispatcher.
    """

    class Events(str, Enum):

        event = "event"

    def send_task_mock(function_name: str, *args, **kwargs):
        print("{} - {} - {}".format(function_name, args, kwargs))

    monkeypatch.setattr(target_celery_handler.celery, "send_task", send_task_mock)

    await target_celery_handler.dispatch(Events.event, "1", "2", "3", k={"4": "4"})


async def test_event_remote_dispatcher_factory(
    target_celery_handler: EventRemoteCeleryDispatcher,
    event_remote_celery_target: EventRemoteCeleryTarget,
) -> None:
    """
    Test parsing a dictionary target.

    Args:
        target_celery_handler (EventRemoteCeleryDispatcher): An instance of EventRemoteCeleryDispatcher.
        event_remote_celery_target (EventRemoteCeleryTarget): The EventRemoteCeleryTarget instance.
    """

    EventRemoteDispatcherFactory().create(event_remote_celery_target)
