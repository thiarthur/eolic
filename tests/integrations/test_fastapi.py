import importlib.util

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from eolic.base import Eolic
from eolic.integrations.fastapi import FastAPIIntegration
from eolic.model import EventDTO


@pytest.fixture
def app():
    """
    Fixture for creating a FastAPI app instance.

    Returns:
        FastAPI: An instance of FastAPI.
    """
    return FastAPI()


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


def test_fastapi_integration_init(eolic: Eolic, app: FastAPI):
    """
    Test initialization of FastAPIIntegration.

    Args:
        eolic (Eolic): The Eolic instance.
        app (FastAPI): The FastAPI app instance.
    """
    integration = FastAPIIntegration(app=app)
    eolic.setup_integration(integration)

    assert integration.eolic is not None
    assert integration.app == app
    assert integration.event_route == "/events"


def test_fastapi_integration_setup(eolic: Eolic, app: FastAPI, event_dto: EventDTO):
    """
    Test the setup method of FastAPIIntegration.

    Args:
        eolic (Eolic): The Eolic instance.
        app (FastAPI): The FastAPI app instance.
        event_dto (EventDTO): The EventDTO instance.
    """
    integration = FastAPIIntegration(app=app)
    integration.setup(eolic)

    assert integration.eolic == eolic

    event_route = integration.event_route
    client = TestClient(app)
    response = client.post(event_route, json=event_dto.model_dump())

    assert response.status_code == 200
    assert response.json() == {}


def test_fastapi_integration_no_app():
    """
    Test that an exception is raised when FastAPIIntegration is initialized with no app.
    """
    with pytest.raises(
        Exception, match="Please declare you app to setup the integration"
    ):
        FastAPIIntegration(app=None)


def test_fastapi_not_installed(monkeypatch: pytest.MonkeyPatch, app: FastAPI):
    """
    Test that an exception is raised when FastAPI is not installed.

    Args:
        monkeypatch: The pytest monkeypatch fixture.
        app (FastAPI): The FastAPI app instance.
    """
    monkeypatch.setattr(importlib.util, "find_spec", lambda _: None)

    with pytest.raises(Exception, match="FastAPI Integration is not installed..*"):
        FastAPIIntegration(app=app)


def test_fastapi_empty_route(eolic: Eolic, app: FastAPI):
    """
    Test that an exception is raised when event_route is None.

    Args:
        eolic (Eolic): The Eolic instance.
        app (FastAPI): The FastAPI app instance.
    """
    integration = FastAPIIntegration(app, event_route=None)
    with pytest.raises(
        Exception, match="Event route is required for FastAPI integration."
    ):
        eolic.setup_integration(integration)
