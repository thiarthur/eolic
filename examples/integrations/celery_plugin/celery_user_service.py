"""User service example with celery."""

from typing import List

from pydantic import BaseModel

from eolic import Eolic

eolic = Eolic(remote_targets=[{"type": "celery", "address": "amqp://localhost:5672"}])


class User(BaseModel):
    """User model."""

    id: int
    name: str
    email: str


users: List[User] = []


def create_user(user: User):
    """Endpoint to create a user."""
    if any(u.id == user.id for u in users):
        raise NotImplementedError("User already exists")

    users.append(user)
    eolic.emit("user_created", user.id, user.name, user.email)

    return user


create_user(User(id=1, name="Name", email="email@example.com"))
