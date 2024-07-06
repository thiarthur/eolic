"""
Module for testing the Eventipy base class functionality.

This module includes tests for initializing Eventipy, registering targets and listeners,
emitting events, and handling remote targets.
"""

from tests.common import GameEvents
from pydantic import ValidationError
from pytest_mock import MockFixture
import pytest
import requests
from eventipy import Eventipy

from eventipy.listener import EventListenerHandler
from eventipy.remote import EventRemoteTargetHandler


@pytest.fixture
def eventipy_instance() -> Eventipy:
    """
    Fixture to provide an instance of Eventipy with a predefined remote target.

    Returns:
        Eventipy: An instance of Eventipy.
    """
    return Eventipy(
        remote_targets=[
            {
                "type": "url",
                "address": "https://webhook.site/test-url",
                "headers": {"X-Api-Key": "test"},
                "events": [GameEvents.ON_PLAYER_JOIN],
            }
        ]
    )


# Initialization
@pytest.mark.order(1)
def test_initialization(eventipy_instance: Eventipy) -> None:
    """
    Test initialization of Eventipy.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """
    assert isinstance(eventipy_instance.remote_target_handler, EventRemoteTargetHandler)
    assert isinstance(eventipy_instance.listener_handler, EventListenerHandler)


# Registering Targets
@pytest.mark.order(2)
def test_register_single_target(eventipy_instance: Eventipy) -> None:
    """
    Test registering a single remote target.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """
    target = {
        "type": "url",
        "address": "https://webhook.site/another-url",
        "headers": {"X-Api-Key": "another"},
        "events": [GameEvents.ON_MONSTER_DEFEATED],
    }
    eventipy_instance.register_target(target)
    assert len(eventipy_instance.remote_target_handler.targets) == 2


@pytest.mark.order(3)
def test_register_multiple_targets(eventipy_instance: Eventipy) -> None:
    """
    Test registering multiple remote targets.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """
    targets = [
        {
            "type": "url",
            "address": "https://webhook.site/target1",
            "headers": {"X-Api-Key": "key1"},
        },
        {
            "type": "url",
            "address": "https://webhook.site/target2",
            "headers": {"X-Api-Key": "key2"},
        },
    ]
    for target in targets:
        eventipy_instance.register_target(target)

    assert len(eventipy_instance.remote_target_handler.targets) == 4


@pytest.mark.order(4)
def test_register_invalid_target(eventipy_instance: Eventipy) -> None:
    """
    Test handling of invalid remote target registration.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """
    with pytest.raises(TypeError):
        eventipy_instance.register_target(123)  # Invalid type


# Registering Listeners
@pytest.mark.order(5)
def test_register_single_listener(eventipy_instance: Eventipy) -> None:
    """
    Test registering a single event listener.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """

    def dummy_listener(*args, **kwargs):
        pass

    eventipy_instance.register_listener(GameEvents.ON_PLAYER_JOIN, dummy_listener)
    listeners = eventipy_instance.listener_handler._listener_map[
        GameEvents.ON_PLAYER_JOIN
    ]
    assert dummy_listener in listeners


@pytest.mark.order(6)
def test_register_multiple_listeners(eventipy_instance: Eventipy) -> None:
    """
    Test registering multiple event listeners for the same event.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """

    def listener1(*args, **kwargs):
        pass

    def listener2(*args, **kwargs):
        pass

    eventipy_instance.register_listener(GameEvents.ON_PLAYER_JOIN, listener1)
    eventipy_instance.register_listener(GameEvents.ON_PLAYER_JOIN, listener2)
    listeners = eventipy_instance.listener_handler._listener_map[
        GameEvents.ON_PLAYER_JOIN
    ]
    assert listener1 in listeners and listener2 in listeners


@pytest.mark.order(7)
def test_register_invalid_listener(eventipy_instance: Eventipy) -> None:
    """
    Test handling of invalid event listener registration.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """
    with pytest.raises(ValidationError):
        eventipy_instance.register_listener(
            GameEvents.ON_PLAYER_JOIN, "not a function"
        )  # Invalid listener


# Event Emission
@pytest.mark.order(8)
def test_emit_event_to_single_listener(eventipy_instance: Eventipy) -> None:
    """
    Test emitting an event to a single listener.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """
    results = []

    @eventipy_instance.on(GameEvents.ON_PLAYER_JOIN)
    def handle_player_join(player_name):
        results.append(player_name)

    eventipy_instance.emit(GameEvents.ON_PLAYER_JOIN, "Archer")
    assert "Archer" in results


@pytest.mark.order(9)
def test_emit_event_to_multiple_listeners(eventipy_instance: Eventipy) -> None:
    """
    Test emitting an event to multiple listeners.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """
    results1 = []
    results2 = []

    @eventipy_instance.on(GameEvents.ON_PLAYER_JOIN)
    def listener1(player_name):
        results1.append(player_name)

    @eventipy_instance.on(GameEvents.ON_PLAYER_JOIN)
    def listener2(player_name):
        results2.append(player_name)

    eventipy_instance.emit(GameEvents.ON_PLAYER_JOIN, "Archer")
    assert "Archer" in results1 and "Archer" in results2


@pytest.mark.order(10)
def test_emit_event_with_arguments(eventipy_instance: Eventipy) -> None:
    """
    Test emitting an event with arguments to a listener.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """
    results = []

    @eventipy_instance.on(GameEvents.ON_PLAYER_ATTACK)
    def handle_player_attack(player_name, monster_name, damage):
        results.append((player_name, monster_name, damage))

    eventipy_instance.emit(GameEvents.ON_PLAYER_ATTACK, "Archer", "Goblin", 30)
    assert ("Archer", "Goblin", 30) in results


# Decorator Functionality
@pytest.mark.order(11)
def test_decorator_functionality(eventipy_instance: Eventipy) -> None:
    """
    Test the functionality of the decorator for registering listeners.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """
    results = []

    @eventipy_instance.on(GameEvents.ON_PLAYER_JOIN)
    def handle_player_join(player_name):
        results.append(player_name)

    eventipy_instance.emit(GameEvents.ON_PLAYER_JOIN, "Archer")
    assert "Archer" in results


@pytest.mark.order(12)
def test_decorator_preserves_function_properties(eventipy_instance: Eventipy) -> None:
    """
    Test that the decorator preserves the original function properties.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
    """

    @eventipy_instance.on(GameEvents.ON_PLAYER_JOIN)
    def handle_player_join(player_name):
        """Create dummy callback for testing."""
        return player_name

    assert handle_player_join.__name__ == "handle_player_join"
    assert handle_player_join.__doc__ == "Create dummy callback for testing."


# Remote Target Handling
@pytest.mark.order(13)
def test_remote_target_receives_event(
    eventipy_instance: Eventipy, mocker: MockFixture
) -> None:
    """
    Test that remote targets receive emitted events.

    Args:
        eventipy_instance (Eventipy): An instance of Eventipy.
        mocker (MockFixture): The mock fixture for patching.
    """
    mocker.patch("requests.post")
    eventipy_instance.emit(GameEvents.ON_PLAYER_JOIN, "Archer")

    eventipy_instance.remote_target_handler.wait_for_all()

    requests.post.assert_any_call(
        "https://webhook.site/test-url",
        json={
            "event": GameEvents.ON_PLAYER_JOIN.value,
            "args": ("Archer",),
            "data": {},
        },
        headers={"X-Api-Key": "test"},
        timeout=10,
    )

    eventipy_instance.emit(GameEvents.ON_MONSTER_DEFEATED, "Archer")
    requests.post.assert_any_call(
        "https://webhook.site/test-url",
        json={
            "event": GameEvents.ON_PLAYER_JOIN.value,
            "args": ("Archer",),
            "data": {},
        },
        headers={"X-Api-Key": "test"},
        timeout=10,
    )
