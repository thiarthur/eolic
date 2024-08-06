"""Module for FastAPI integration."""

from typing import TYPE_CHECKING, Optional

from ..base import Integration
from ..model import EventDTO
from ..helpers.modules import is_module_installed

if TYPE_CHECKING:
    from fastapi import FastAPI
    from ..base import Eolic


class FastAPIIntegration(Integration):
    """Class for FastAPI integration setup with Eolic."""

    def __init__(self, app: Optional["FastAPI"], event_route: str = "/events") -> None:
        """
        Initialize the FastAPI integration.

        Args:
            app (FastAPI): The FastAPI app instance.
            event_route (str): The event hook route for event receiving.

        Raises:
            Exception: If FastAPI extra is is not installed.
            Exception: If FastAPI is None.
        """
        if not is_module_installed("fastapi"):
            raise Exception(
                """FastAPI Integration is not installed.
                    Please install eolic[fastapi] (using fastapi extras) to use this integration."""
            )

        if app is None:
            raise Exception("Please declare you app to setup the integration.")

        super().__init__()
        self.app = app
        self.event_route = event_route

    def setup(self, eolic: "Eolic") -> None:
        """
        Apply the FastAPI integration setup.

        Args:
            eolic (Eolic): The Eolic instance to integrate with.
        """
        self.eolic = eolic
        event_route = self.event_route

        if event_route is None:
            raise Exception("Event route is required for FastAPI integration.")

        @self.app.post(event_route)
        async def emit_event(event: EventDTO):
            self.forward_event(event)
            return {}
