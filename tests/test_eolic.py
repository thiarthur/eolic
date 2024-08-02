"""
Module for testing the Eolic base class functionality.

This module includes tests for initializing Eolic, registering targets and listeners,
emitting events, and handling remote targets.
"""

from unittest.mock import patch
from tests.common import GameEvents
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


@pytest.fixture(autouse=True)
def clear_instance(eolic_instance: Eolic) -> None:
    """
    Fixture to clear targets before each test.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    eolic_instance.listener_handler.clear()
    eolic_instance.remote_target_handler.clear()


def test_instance_with_remote_targets() -> None:
    Eolic._instances.clear()
    eolic = Eolic(
        remote_targets=[
            {
                "type": "url",
                "address": "https://a/test-url",
                "headers": {"X-Api-Key": "test"},
                "events": [GameEvents.ON_PLAYER_JOIN],
            }
        ]
    )

    assert len(eolic.remote_target_handler.targets) == 1
    assert eolic.remote_target_handler.targets[0].address == "https://a/test-url"


def test_initialization(eolic_instance: Eolic) -> None:
    """
    Test initialization of Eolic.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    assert isinstance(eolic_instance.remote_target_handler, EventRemoteTargetHandler)
    assert isinstance(eolic_instance.listener_handler, EventListenerHandler)


def test_register_listener(eolic_instance: Eolic) -> None:
    eolic_instance.register_listener(GameEvents.ON_PLAYER_JOIN, lambda: None)
    assert len(eolic_instance.listener_handler.listeners) == 1


def test_register_invalid_target(eolic_instance: Eolic) -> None:
    """
    Test handling of invalid remote target registration.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    with pytest.raises(TypeError):
        eolic_instance.register_target(123)  # Invalid type


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


def test_emit_event_to_async_listeners(eolic_instance: Eolic) -> None:
    """
    Test emitting an event to multiple listeners.

    Args:
        eolic_instance (Eolic): An instance of Eolic.
    """
    results1 = []
    results2 = []

    @eolic_instance.on(GameEvents.ON_PLAYER_JOIN)
    async def listener1(player_name):
        results1.append(player_name)

    @eolic_instance.on(GameEvents.ON_PLAYER_JOIN)
    async def listener2(player_name):
        results2.append(player_name)

    eolic_instance.emit(GameEvents.ON_PLAYER_JOIN, "Archer")
    assert "Archer" in results1 and "Archer" in results2


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
