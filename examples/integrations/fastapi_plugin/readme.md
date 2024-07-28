# Eolic FastAPI Integration Example

This example demonstrates how to use Eolic to integrate event handling between two FastAPI microservices: a User Service and a Notification Service.

## Overview

- **User Service**: Manages user data and emits events when a new user is created.
- **Notification Service**: Listens for user creation events and handles them by sending a notification.

## Prerequisites

- Python 3.8+
- FastAPI
- Uvicorn
- Eolic with FastAPI extras: eolic[**fastapi**]

## Installation

1. **Clone the repository**:
   ```bash
   git clone git@github.com:thiarthur/eolic.git
   cd eolic/examples/integrations/fastapi_plugin
    ```

2. **Create a virtual env (optional)**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the dependencies**:
    ```bash
    pip install requirements.txt
    ```

## Running

1. **Start the User Service**:

    ```bash
    python user_service.py
    Start the Notification Service:
    ```

2. **Start the Notification Service**:
    ```bash
    python notification_service.py
    ```

3. **Create a New User**:

    Send a POST request to the User Service to create a new user:

    ```bash
    curl -X POST "http://localhost:8000/users" -H "Content-Type: application/json" -d '{"id": 1, "name": "John Doe", "email": "john@example.com"}'
    ```

4. **Check Notifications**:
Check the output of the Notification Service to see the notification for the new user creation.



## Conclusion
This example demonstrates how to set up and use the FastAPI integration with Eolic to handle events across microservices.