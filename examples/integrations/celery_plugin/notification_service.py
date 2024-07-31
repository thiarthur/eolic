"""Notification service example module."""

from celery import Celery

from eolic import Eolic
from eolic.integrations.celery import CeleryIntegration

app = Celery(
    "tasks",
    backend=False,
)

eolic = Eolic()


# Create an instance of CeleryIntegration with a custom event function
celery_integration = CeleryIntegration(app)
# Set up the integration
eolic.setup_integration(celery_integration)


@eolic.on("user_created")
def handle_user_created(id_: int, name: str, email: str):
    """Handle the user created event."""
    # Handle the user created event (e.g., send a notification)
    print(f"Notification: [{id_}] User {name} with email {email} was created!")
    # TODO: Send-email for email confirmation
    return {}
