"""Module for Celery integration."""

import sys
from typing import TYPE_CHECKING, Optional

from ..base import Integration
from ..model import EventDTO

if TYPE_CHECKING:
    from celery import Celery
    from ..base import Eolic


class CeleryIntegration(Integration):
    """Class for CeleryIntegration integration setup with Eolic."""

    def __init__(
        self,
        app: Optional["Celery"],
        event_function: str = "events",
        queue_name: str = "eolic",
    ) -> None:
        """
        Initialize the Celery integration.

        Args:
            app (Celery): The Celery app instance.
            event_function (str): The event hook function event receiving.

        Raises:
            Exception: If Celery extra is not installed.
            Exception: If Celery is None.
        """
        if "celery" not in sys.modules:
            raise Exception(
                """Celery Integration is not installed.
                    Please install eolic[celery] (using celery extras) to use this integration."""
            )

        if app is None:
            raise Exception("Please declare you app to setup the integration.")

        super().__init__()
        self.app = app
        self.event_function = event_function
        self.queue_name = queue_name

    def setup(self, eolic: "Eolic") -> None:
        """
        Apply the Celery integration setup.

        Args:
            eolic (Eolic): The Eolic instance to integrate with.
        """
        self.eolic = eolic
        event_function = self.event_function

        if event_function is None:
            raise Exception("Event function is required for Celery integration.")

        def listener_event(event_name: str, *args, **kwargs):
            event = EventDTO(event=event_name, args=args, kwargs=kwargs)
            self.forward_event(event)

        self.app.task(listener_event, name=self.event_function, queue=self.queue_name)
