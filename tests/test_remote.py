"""
Module for testing the EventRemoteTargetHandler class.

This module includes tests for parsing, registering, and emitting events
to remote targets using the EventRemoteTargetHandler class.
"""

import pytest
from eventipy.remote import EventRemoteTargetHandler, EventRemoteURLTarget
from unittest.mock import patch
from tests.common import GameEvents


@pytest.fixture
def target_handler() -> EventRemoteTargetHandler:
    """
    Fixture to provide an instance of EventRemoteTargetHandler.

    Returns:
        EventRemoteTargetHandler: An instance of EventRemoteTargetHandler.
    """
    handler = EventRemoteTargetHandler()
    return handler


@pytest.fixture(autouse=True)
def clear_targets(target_handler: EventRemoteTargetHandler) -> None:
    """
    Fixture to clear targets before each test.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    target_handler.clear()


# Parsing Targets


@pytest.mark.order(14)
def test_parse_string_target(target_handler: EventRemoteTargetHandler) -> None:
    """
    Test parsing a string target.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    target = "https://webhook.site/test-url"
    parsed_target = target_handler._parse_target(target)
    assert isinstance(parsed_target, EventRemoteURLTarget)
    assert parsed_target.address == "https://webhook.site/test-url"


@pytest.mark.order(15)
def test_parse_dict_target(target_handler: EventRemoteTargetHandler) -> None:
    """
    Test parsing a dictionary target.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    target = {
        "type": "url",
        "address": "https://webhook.site/test-url",
        "headers": {"X-Api-Key": "test"},
    }
    parsed_target = target_handler._parse_target(target)
    assert isinstance(parsed_target, EventRemoteURLTarget)
    assert parsed_target.address == "https://webhook.site/test-url"
    assert parsed_target.headers["X-Api-Key"] == "test"


@pytest.mark.order(16)
def test_parse_invalid_target(target_handler: EventRemoteTargetHandler) -> None:
    """
    Test handling of invalid target formats.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    with pytest.raises(TypeError):
        target_handler._parse_target(123)  # Invalid type


# Registering Targets


@pytest.mark.order(17)
def test_register_single_target(target_handler: EventRemoteTargetHandler) -> None:
    """
    Test registering a single target.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    target = "https://webhook.site/test-url"
    target_handler.register(target)
    assert len(target_handler.targets) == 1


@pytest.mark.order(18)
def test_register_multiple_targets(target_handler: EventRemoteTargetHandler) -> None:
    """
    Test registering multiple targets.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    targets = [
        "https://webhook.site/target1",
        {
            "type": "url",
            "address": "https://webhook.site/target2",
            "headers": {"X-Api-Key": "key2"},
        },
    ]
    for target in targets:
        target_handler.register(target)
    assert len(target_handler.targets) == 2


@pytest.mark.order(19)
def test_register_duplicate_targets(target_handler: EventRemoteTargetHandler) -> None:
    """
    Test handling of duplicate target registrations.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    target = "https://webhook.site/test-url"
    target_handler.register(target)
    target_handler.register(target)
    assert (
        len(target_handler.targets) == 2
    )  # This assumes duplicates are allowed. Adjust as needed.


# Emitting Events


@pytest.mark.order(20)
def test_emit_event_to_single_target(target_handler: EventRemoteTargetHandler) -> None:
    """
    Test emitting an event to a single target.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    with patch("requests.post") as mock_post:
        target = {
            "type": "url",
            "address": "https://webhook.site/test-url",
            "headers": {"X-Api-Key": "test"},
        }
        target_handler.register(target)
        target_handler.emit(GameEvents.ON_PLAYER_JOIN, "Archer")
        target_handler.wait_for_all()
        mock_post.assert_called_once_with(
            "https://webhook.site/test-url",
            json={
                "event": GameEvents.ON_PLAYER_JOIN.value,
                "args": ("Archer",),
                "data": {},
            },
            headers={"X-Api-Key": "test"},
            timeout=10,
        )


@pytest.mark.order(21)
def test_emit_event_to_multiple_targets(
    target_handler: EventRemoteTargetHandler,
) -> None:
    """
    Test emitting an event to multiple targets.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    with patch("requests.post") as mock_post:
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
            target_handler.register(target)
        target_handler.emit(GameEvents.ON_PLAYER_JOIN, "Archer")
        target_handler.wait_for_all()
        assert mock_post.call_count == 2


@pytest.mark.order(22)
def test_filter_targets_by_event(target_handler: EventRemoteTargetHandler) -> None:
    """
    Test filtering targets by specific events.

    Args:
        target_handler (EventRemoteTargetHandler): An instance of EventRemoteTargetHandler.
    """
    with patch("requests.post") as mock_post:
        targets = [
            {
                "type": "url",
                "address": "https://webhook.site/target1",
                "headers": {"X-Api-Key": "key1"},
                "events": [GameEvents.ON_PLAYER_JOIN],
            },
            {
                "type": "url",
                "address": "https://webhook.site/target2",
                "headers": {"X-Api-Key": "key2"},
                "events": [GameEvents.ON_MONSTER_DEFEATED],
            },
        ]
        for target in targets:
            target_handler.register(target)
        target_handler.emit(GameEvents.ON_PLAYER_JOIN, "Archer")
        target_handler.wait_for_all()
        mock_post.assert_called_once_with(
            "https://webhook.site/target1",
            json={
                "event": GameEvents.ON_PLAYER_JOIN.value,
                "args": ("Archer",),
                "data": {},
            },
            headers={"X-Api-Key": "key1"},
            timeout=10,
        )
