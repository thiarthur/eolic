"""
Module for testing the EventRemoteDispatcherFactory and dispatchers.

This module includes tests for creating dispatchers, dispatching events,
handling errors, and validating event remote targets.
"""

from pydantic import ValidationError
import pytest
from eolic.model import EventRemoteTarget
from eolic.remote import (
    EventRemoteDispatcherFactory,
    EventRemoteURLDispatcher,
    EventRemoteURLTarget,
)
from tests.common import GameEvents
from pytest_mock import MockFixture


@pytest.fixture
def url_target() -> EventRemoteURLTarget:
    """
    Fixture to provide an instance of EventRemoteURLTarget.

    Returns:
        EventRemoteURLTarget: An instance of EventRemoteURLTarget.
    """
    return EventRemoteURLTarget(
        type="url",
        address="https://webhook.site/test-url",
        headers={"X-Api-Key": "test"},
        timeout=10,
    )


@pytest.fixture
def dispatcher_factory() -> EventRemoteDispatcherFactory:
    """
    Fixture to provide an instance of EventRemoteDispatcherFactory.

    Returns:
        EventRemoteDispatcherFactory: An instance of EventRemoteDispatcherFactory.
    """
    return EventRemoteDispatcherFactory()


# Dispatcher Creation


def test_create_url_dispatcher(
    dispatcher_factory: EventRemoteDispatcherFactory, url_target: EventRemoteURLTarget
) -> None:
    """
    Test creating a URL dispatcher.

    Args:
        dispatcher_factory (EventRemoteDispatcherFactory): An instance of EventRemoteDispatcherFactory.
        url_target (EventRemoteURLTarget): An instance of EventRemoteURLTarget.
    """
    dispatcher = dispatcher_factory.create(url_target)
    assert isinstance(dispatcher, EventRemoteURLDispatcher)
    assert dispatcher.target == url_target


# Dispatching Events


def test_dispatch_event_to_url(
    mocker: MockFixture, url_target: EventRemoteURLTarget
) -> None:
    """
    Test dispatching an event to a URL target.

    Args:
        mocker (MockFixture): The mock fixture for patching.
        url_target (EventRemoteURLTarget): An instance of EventRemoteURLTarget.
    """
    dispatcher = EventRemoteURLDispatcher(url_target)
    mock_post = mocker.patch("requests.post")
    dispatcher.dispatch(GameEvents.ON_PLAYER_JOIN, "Archer")
    mock_post.assert_called_once_with(
        "https://webhook.site/test-url",
        json={
            "event": GameEvents.ON_PLAYER_JOIN.value,
            "args": ("Archer",),
            "kwargs": {},
        },
        headers={"X-Api-Key": "test"},
        timeout=10,
    )


def test_dispatch_event_to_url_with_different_event(
    mocker: MockFixture, url_target: EventRemoteURLTarget
) -> None:
    """
    Test dispatching a different event to a URL target.

    Args:
        mocker (MockFixture): The mock fixture for patching.
        url_target (EventRemoteURLTarget): An instance of EventRemoteURLTarget.
    """
    dispatcher = EventRemoteURLDispatcher(url_target)
    mock_post = mocker.patch("requests.post")
    dispatcher.dispatch(GameEvents.ON_PLAYER_ATTACK, "Archer", "Goblin", 30)
    mock_post.assert_called_once_with(
        "https://webhook.site/test-url",
        json={
            "event": GameEvents.ON_PLAYER_ATTACK.value,
            "args": ("Archer", "Goblin", 30),
            "kwargs": {},
        },
        headers={"X-Api-Key": "test"},
        timeout=10,
    )


def test_dispatcher_error_handling(
    mocker: MockFixture, url_target: EventRemoteURLTarget
) -> None:
    """
    Test error handling in the dispatcher.

    Args:
        mocker (MockFixture): The mock fixture for patching.
        url_target (EventRemoteURLTarget): An instance of EventRemoteURLTarget.
    """
    dispatcher = EventRemoteURLDispatcher(url_target)
    mock_post = mocker.patch("requests.post", side_effect=Exception("Request failed"))
    with pytest.raises(Exception, match="Request failed"):
        dispatcher.dispatch(GameEvents.ON_PLAYER_JOIN, "Archer")
    mock_post.assert_called_once_with(
        "https://webhook.site/test-url",
        json={
            "event": GameEvents.ON_PLAYER_JOIN.value,
            "args": ("Archer",),
            "kwargs": {},
        },
        headers={"X-Api-Key": "test"},
        timeout=10,
    )


def test_invalid_event_remote_target() -> None:
    """
    Test validation of an invalid event remote target.

    Raises:
        ValidationError: If the target type is invalid.
    """
    with pytest.raises(ValidationError):
        EventRemoteTarget(type="invalid", address="")


def test_not_implemented_type() -> None:
    """
    Test handling of a not implemented target type.

    Raises:
        NotImplementedError: If the target type is not implemented.
    """
    from enum import Enum

    class TestEventRemoteTargetType(Enum):
        url = "url"
        celery = "celery"
        rabbitmq = "rabbitmq"
        invalid_type = "invalid_type"

    class TestEventRemoteTarget(EventRemoteTarget):
        type: TestEventRemoteTargetType

    with pytest.raises(NotImplementedError):
        EventRemoteDispatcherFactory().create(
            TestEventRemoteTarget(type="invalid_type", address="")
        )
