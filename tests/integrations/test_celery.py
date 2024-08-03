import importlib.util

import pytest
from celery import Celery

from eolic.base import Eolic
from eolic.integrations.celery import CeleryIntegration
from eolic.model import EventDTO
from eolic.utils import get_module


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


def test_celery_not_installed(monkeypatch: pytest.MonkeyPatch, app: Celery):
    """
    Test that an exception is raised when Celery is not installed.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
        app (Celery): The Celery app instance.
    """
    monkeypatch.setattr(importlib.util, "find_spec", lambda _: None)

    with pytest.raises(Exception, match="Celery Integration is not installed.*"):
        CeleryIntegration(app=app)


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
        eolic (Eolic): The Eolic instance.
        app (Celery): The Celery app instance.
    """
    integration = CeleryIntegration(app, event_function="event")
    integration.setup(eolic)

    def mock_lambda_handler(event, *args, **kwargs):
        return event, args, kwargs

    monkeypatch.setattr(integration, "forward_event", mock_lambda_handler)

    integration.app.tasks["event"]("test_event", "arg1", key="value")


def test_celery_module(monkeypatch: pytest.MonkeyPatch, eolic: Eolic, app: Celery):
    """
    Test that an exception is raised when event_route is None.

    Args:
        eolic (Eolic): The Eolic instance.
        app (Celery): The Celery app instance.
    """
    assert isinstance(get_module("celery").Celery(), Celery)
