"""Module for testing the Integration base module."""
import pytest
from unittest.mock import Mock, create_autospec
from eolic.base import Eolic, Integration
from eolic.model import EventDTO

class DummyIntegration(Integration):
    """
    A dummy implementation of the Integration abstract base class
    for testing purposes.
    """
    def setup(self, eolic):
        self.eolic = eolic

@pytest.fixture
def eolic():
    """
    Fixture for creating a mock Eolic instance with necessary attributes.
    
    Returns:
        Mock: A mocked Eolic instance.
    """
    eolic: Eolic = create_autospec('eolic.base.Eolic', instance=True)
    eolic.listener_handler = Mock()
    eolic.listener_handler.emit = Mock()
    return eolic

@pytest.fixture
def event_dto():
    """
    Fixture for creating a mock EventDTO instance.
    
    Returns:
        EventDTO: A mocked EventDTO instance with predefined attributes.
    """
    event_dto = EventDTO(
        event='test_event',
        args=('arg1',),
        kwargs={'key': 'value'}
    )
    return event_dto


def test_integration_setup(eolic):
    """
    Test that the setup method correctly sets the eolic instance.
    
    Args:
        eolic (Mock): The mocked Eolic instance.
    """
    integration = DummyIntegration()
    integration.setup(eolic)
    assert integration.eolic == eolic

def test_forward_event(eolic: Eolic, event_dto: EventDTO):
    """
    Test that forward_event calls the emit method on the eolic instance
    with the correct arguments.
    
    Args:
        eolic (Eolic): The mocked Eolic instance.
        event_dto (EventDTO): The mocked EventDTO instance.
    """
    integration = DummyIntegration()
    integration.setup(eolic)
    
    integration.forward_event(event_dto)
    eolic.listener_handler.emit.assert_called_once_with('test_event', 'arg1', key='value')

def test_forward_event_without_eolic():
    """
    Test that forward_event raises an exception if the eolic instance
    is not set.
    """
    event_dto = create_autospec('eolic.model.EventDTO', instance=True)
    integration = DummyIntegration()
    
    with pytest.raises(Exception, match="The Eolic instance is not set for the integration"):
        integration.forward_event(event_dto)
