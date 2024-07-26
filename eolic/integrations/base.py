"""Module for the base integration class."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ..base import Eolic
    from ..model import EventDTO


class Integration(ABC):
    """Abstract class for integrations with Eolic."""

    def __init__(self):
        """Initialize the integration."""
        self.eolic: Optional[Eolic] = None

    @abstractmethod
    def setup(self, eolic: "Eolic") -> None:
        """
        Apply the integration setup.

        Args:
            eolic (Eolic): The Eolic instance to integrate with.

        """
        raise NotImplementedError("Setup method must be implemented")

    def forward_event(self, event: "EventDTO"):
        """
        Handle the forwarding of events from integration to the Eolic instance.

        Args:
            event (EventDTO): The received event to forward.
        """
        if self.eolic is None:
            raise Exception(
                """The Eolic instance is not set for the integration.
                Use eolic.add_integration(integration)"""
            )

        self.eolic.listener_handler.emit(event.event, *event.args, **event.kwargs)
