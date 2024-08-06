"""User service example module."""

from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from eolic import Eolic
from eolic.integrations.fastapi import FastAPIIntegration

app = FastAPI()
eolic = Eolic(
    remote_targets=[
        "http://127.0.0.1:8001/user-events",
    ]
)


class User(BaseModel):
    """User model."""

    id: int
    name: str
    email: str


users: List[User] = []


@app.post("/users")
async def create_user(user: User):
    """Endpoint to create a user."""
    if any(u.id == user.id for u in users):
        raise HTTPException(status_code=400, detail="User already exists")
    users.append(user)
    eolic.emit("user_created", user.id, user.name, user.email)
    return user


# Create an instance of FastAPIIntegration with a custom event route
fastapi_integration = FastAPIIntegration(app, event_route="/user-events")
# Set up the integration
eolic.setup_integration(fastapi_integration)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
