"""Notification service example module."""

from fastapi import FastAPI
from eolic import Eolic
from eolic.integrations.fastapi import FastAPIIntegration

app = FastAPI()
eolic = Eolic()


@eolic.on("user_created")
def handle_user_created(id: int, name: str, email: str):
    """Handle the user created event."""
    # Handle the user created event (e.g., send a notification)
    print(f"Notification: User {name} with email {email} was created!")
    # TODO: Send-email for email confirmation
    return {}


# Create an instance of FastAPIIntegration with a custom event route
fastapi_integration = FastAPIIntegration(app, event_route="/user-events")
# Set up the integration
eolic.setup_integration(fastapi_integration)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
