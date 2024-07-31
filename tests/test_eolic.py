"""
Module for testing the Eolic base class functionality.

This module includes tests for initializing Eolic, registering targets and listeners,
emitting events, and handling remote targets.
"""

from unittest.mock import patch
from tests.common import GameEvents
from pydantic import ValidationError
from pytest_mock import MockFixture
import pytest
from eolic import Eolic

from eolic.listener import EventListenerHandler
from eolic.remote import EventRemoteTargetHandler


@pytest.fixture
def eolic_instance() -> Eolic:
    """
    Fixture to provide an instance of Eolic with a predefined remote target.

    Returns:
        Eolic: An instance of Eolic.
    """
    return Eolic(
        remote_targets=[
            {
                "type": "url",
                "address": "https://a/test-url",
                "headers": {"X-Api-Key": "test"},
                "events": [GameEvents.ON_PLAYER_JOIN],
            }
        ]
    )


# Initialization
@pytest.mark.order(1)
def test_initialization(eolic_instance: Eolic) -> None:
    """
    Test initialization of Eolic.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    assert isinstance(eolic_instance.remote_target_handler, EventRemoteTargetHandler)
    assert isinstance(eolic_instance.listener_handler, EventListenerHandler)


# Registering Targets
@pytest.mark.order(2)
def test_register_single_target(eolic_instance: Eolic) -> None:
    """
    Test registering a single remote target.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    target = {
        "type": "url",
        "address": "https://a/another-url",
        "headers": {"X-Api-Key": "another"},
        "events": [GameEvents.ON_MONSTER_DEFEATED],
    }
    eolic_instance.register_target(target)
    assert len(eolic_instance.remote_target_handler.targets) == 2


@pytest.mark.order(3)
def test_register_multiple_targets(eolic_instance: Eolic) -> None:
    """
    Test registering multiple remote targets.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    targets = [
        {
            "type": "url",
            "address": "https://a/target1",
            "headers": {"X-Api-Key": "key1"},
        },
        {
            "type": "url",
            "address": "https://a/target2",
            "headers": {"X-Api-Key": "key2"},
        },
    ]
    for target in targets:
        eolic_instance.register_target(target)

    assert len(eolic_instance.remote_target_handler.targets) == 4

    eolic_instance.remote_target_handler.clear()


@pytest.mark.order(4)
def test_register_invalid_target(eolic_instance: Eolic) -> None:
    """
    Test handling of invalid remote target registration.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    with pytest.raises(TypeError):
        eolic_instance.register_target(123)  # Invalid type


# Registering Listeners
@pytest.mark.order(5)
def test_register_single_listener(eolic_instance: Eolic) -> None:
    """
    Test registering a single event listener.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """

    def dummy_listener(*args, **kwargs):
        pass

    eolic_instance.register_listener(GameEvents.ON_PLAYER_JOIN, dummy_listener)
    listeners = eolic_instance.listener_handler._listener_map[GameEvents.ON_PLAYER_JOIN]
    assert dummy_listener in listeners


@pytest.mark.order(6)
def test_register_multiple_listeners(eolic_instance: Eolic) -> None:
    """
    Test registering multiple event listeners for the same event.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """

    def listener1(*args, **kwargs):
        pass

    def listener2(*args, **kwargs):
        pass

    eolic_instance.register_listener(GameEvents.ON_PLAYER_JOIN, listener1)
    eolic_instance.register_listener(GameEvents.ON_PLAYER_JOIN, listener2)
    listeners = eolic_instance.listener_handler._listener_map[GameEvents.ON_PLAYER_JOIN]
    assert listener1 in listeners and listener2 in listeners


@pytest.mark.order(7)
def test_register_invalid_listener(eolic_instance: Eolic) -> None:
    """
    Test handling of invalid event listener registration.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    with pytest.raises(ValidationError):
        eolic_instance.register_listener(
            GameEvents.ON_PLAYER_JOIN, "not a function"
        )  # Invalid listener


# Event Emission
@pytest.mark.order(8)
def test_emit_event_to_single_listener(eolic_instance: Eolic) -> None:
    """
    Test emitting an event to a single listener.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    results = []

    @eolic_instance.on(GameEvents.ON_PLAYER_JOIN)
    def handle_player_join(player_name):
        results.append(player_name)

    eolic_instance.emit(GameEvents.ON_PLAYER_JOIN, "Archer")
    assert "Archer" in results


@pytest.mark.order(9)
def test_emit_event_to_multiple_listeners(eolic_instance: Eolic) -> None:
    """
    Test emitting an event to multiple listeners.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    results1 = []
    results2 = []

    @eolic_instance.on(GameEvents.ON_PLAYER_JOIN)
    def listener1(player_name):
        results1.append(player_name)

    @eolic_instance.on(GameEvents.ON_PLAYER_JOIN)
    def listener2(player_name):
        results2.append(player_name)

    eolic_instance.emit(GameEvents.ON_PLAYER_JOIN, "Archer")
    assert "Archer" in results1 and "Archer" in results2


@pytest.mark.order(10)
def test_emit_event_with_arguments(eolic_instance: Eolic) -> None:
    """
    Test emitting an event with arguments to a listener.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    results = []

    @eolic_instance.on(GameEvents.ON_PLAYER_ATTACK)
    def handle_player_attack(player_name, monster_name, damage):
        results.append((player_name, monster_name, damage))

    eolic_instance.emit(GameEvents.ON_PLAYER_ATTACK, "Archer", "Goblin", 30)
    assert ("Archer", "Goblin", 30) in results


# Decorator Functionality
@pytest.mark.order(11)
def test_decorator_functionality(eolic_instance: Eolic) -> None:
    """
    Test the functionality of the decorator for registering listeners.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    results = []

    @eolic_instance.on(GameEvents.ON_PLAYER_JOIN)
    def handle_player_join(player_name):
        results.append(player_name)

    eolic_instance.emit(GameEvents.ON_PLAYER_JOIN, "Archer")
    assert "Archer" in results


@pytest.mark.order(12)
def test_decorator_preserves_function_properties(eolic_instance: Eolic) -> None:
    """
    Test that the decorator preserves the original function properties.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """

    @eolic_instance.on(GameEvents.ON_PLAYER_JOIN)
    def handle_player_join(player_name):
        """Create dummy callback for testing."""
        return player_name

    assert handle_player_join.__name__ == "handle_player_join"
    assert handle_player_join.__doc__ == "Create dummy callback for testing."


# Remote Target Handling
@pytest.mark.order(13)
def test_remote_target_receives_event(
    eolic_instance: Eolic, mocker: MockFixture
) -> None:
    """
    Test that remote targets receive emitted events.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
        mocker (MockFixture): The mock fixture for patching.
    """

    eolic_instance.register_target(
        {
            "type": "url",
            "address": "https://a/test-url",
            "headers": {"X-Api-Key": "test"},
        }
    )

    with patch("requests.post") as mock_post:
        eolic_instance.emit(GameEvents.ON_PLAYER_JOIN, "Archer")

        eolic_instance.remote_target_handler.wait_for_all()

        mock_post.assert_called_once_with(
            "https://a/test-url",
            json={
                "event": GameEvents.ON_PLAYER_JOIN.value,
                "args": ("Archer",),
                "kwargs": {},
            },
            headers={"X-Api-Key": "test"},
            timeout=10,
        )

    with patch("requests.post") as mock_post:
        eolic_instance.emit(GameEvents.ON_MONSTER_DEFEATED, "Archer")
        eolic_instance.remote_target_handler.wait_for_all()

        mock_post.assert_called_once_with(
            "https://a/test-url",
            json={
                "event": GameEvents.ON_MONSTER_DEFEATED.value,
                "args": ("Archer",),
                "kwargs": {},
            },
            headers={"X-Api-Key": "test"},
            timeout=10,
        )
