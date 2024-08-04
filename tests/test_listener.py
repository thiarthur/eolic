"""
Module for testing the EventListenerHandler class.

This module includes tests for registering listeners, validating the listener map structure,
and executing listeners with and without arguments.
"""

import pytest
from eolic.listener import EventListenerHandler
from tests.common import GameEvents


@pytest.fixture
def listener_handler() -> EventListenerHandler:
    """
    Fixture to provide an instance of EventListenerHandler.

    Returns:
        EventListenerHandler: An instance of EventListenerHandler.
    """
    return EventListenerHandler()


@pytest.fixture(autouse=True)
def clear_targets(listener_handler: EventListenerHandler) -> None:
    """
    Fixture to clear listeners before each test.

    Args:
        listener_handler (EventListenerHandler): An instance of EventListenerHandler.
    """
    listener_handler.clear()


# Registering Listeners


def test_register_single_listener(listener_handler: EventListenerHandler) -> None:
    """
    Test registering a single event listener.

    Args:
        listener_handler (EventListenerHandler): An instance of EventListenerHandler.
    """

    def dummy_listener(*args, **kwargs):
        pass

    listener_handler.register(GameEvents.ON_PLAYER_JOIN, dummy_listener)
    listeners = listener_handler._listener_map[GameEvents.ON_PLAYER_JOIN]
    assert len(listeners) == 1
    assert dummy_listener in listeners


def test_register_multiple_listeners(listener_handler: EventListenerHandler) -> None:
    """
    Test registering multiple event listeners for the same event.

    Args:
        listener_handler (EventListenerHandler): An instance of EventListenerHandler.
    """

    def listener1(*args, **kwargs):
        pass

    def listener2(*args, **kwargs):
        pass

    listener_handler.register(GameEvents.ON_PLAYER_JOIN, listener1)
    listener_handler.register(GameEvents.ON_PLAYER_JOIN, listener2)
    listeners = listener_handler._listener_map[GameEvents.ON_PLAYER_JOIN]
    assert len(listeners) == 2
    assert listener1 in listeners
    assert listener2 in listeners


def test_register_async_listeners(listener_handler: EventListenerHandler) -> None:
    """
    Test registering async event listeners for the same event.

    Args:
        listener_handler (EventListenerHandler): An instance of EventListenerHandler.
    """

    async def listener(*args, **kwargs):
        pass

    listener_handler.register(GameEvents.ON_PLAYER_JOIN, listener)

    listeners = listener_handler._listener_map[GameEvents.ON_PLAYER_JOIN]
    assert len(listeners) == 1


def test_register_listeners_for_different_events(
    listener_handler: EventListenerHandler,
) -> None:
    """
    Test registering listeners for different events.

    Args:
        listener_handler (EventListenerHandler): An instance of EventListenerHandler.
    """

    def listener1(*args, **kwargs):
        pass

    def listener2(*args, **kwargs):
        pass

    listener_handler.register(GameEvents.ON_PLAYER_JOIN, listener1)
    listener_handler.register(GameEvents.ON_PLAYER_ATTACK, listener2)
    listeners_join = listener_handler._listener_map[GameEvents.ON_PLAYER_JOIN]
    listeners_attack = listener_handler._listener_map[GameEvents.ON_PLAYER_ATTACK]
    assert len(listeners_join) == 1
    assert listener1 in listeners_join
    assert len(listeners_attack) == 1
    assert listener2 in listeners_attack


# Event Listener Map


def test_listener_map_structure(listener_handler: EventListenerHandler) -> None:
    """
    Test the structure of the listener map.

    Args:
        listener_handler (EventListenerHandler): An instance of EventListenerHandler.
    """

    def dummy_listener(*args, **kwargs):
        pass

    listener_handler.register(GameEvents.ON_PLAYER_JOIN, dummy_listener)
    assert isinstance(listener_handler._listener_map, dict)
    assert GameEvents.ON_PLAYER_JOIN in listener_handler._listener_map
    listeners = listener_handler._listener_map[GameEvents.ON_PLAYER_JOIN]
    assert isinstance(listeners, list)
    assert dummy_listener in listeners


# Listener Execution


def test_listener_execution(listener_handler: EventListenerHandler) -> None:
    """
    Test the execution of a registered listener.

    Args:
        listener_handler (EventListenerHandler): An instance of EventListenerHandler.
    """
    results = []

    def dummy_listener(*args, **kwargs):
        results.append("executed")

    listener_handler.register(GameEvents.ON_PLAYER_JOIN, dummy_listener)
    listeners = listener_handler._listener_map[GameEvents.ON_PLAYER_JOIN]
    for listener in listeners:
        listener()
    assert "executed" in results


def test_listener_execution_with_arguments(
    listener_handler: EventListenerHandler,
) -> None:
    """
    Test the execution of a registered listener with arguments.

    Args:
        listener_handler (EventListenerHandler): An instance of EventListenerHandler.
    """
    results = []

    def dummy_listener(arg1, arg2):
        results.append((arg1, arg2))

    listener_handler.register(GameEvents.ON_PLAYER_JOIN, dummy_listener)
    listeners = listener_handler._listener_map[GameEvents.ON_PLAYER_JOIN]
    for listener in listeners:
        listener("arg1_value", "arg2_value")
    assert ("arg1_value", "arg2_value") in results
