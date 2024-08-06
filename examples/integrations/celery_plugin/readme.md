# Eolic Celery Integration Example

This example demonstrates how to integrate Eolic Celery to handle events, such as sending notifications between a User Service and a Notification Service.

## Overview

- **User Service**: Create a new user and emit an event.
- **Notification Service**: Listens for user creation events and handles them by sending a notification.

## Prerequisites

- Python 3.8+
- Celery
- Eolic with Celery extras: eolic[**celery**]

## Installation

1. **Clone the repository**:
   ```bash
   git clone git@github.com:thiarthur/eolic.git
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

**Note:** To run Celery, you will need a queue service or any other backend to run it. In this example, we are using [RabbitMQ](https://www.rabbitmq.com/tutorials). See more at the [Celery documentation](https://docs.celeryq.dev/en/stable/getting-started/introduction.html).


1. **Start the Notification Service**:
    ```bash
    celery -A 'examples.integrations.celery_plugin.celery_notification_service' worker --loglevel=INFO -Q eolic
    ```

2. **Create a New User**:

    ```bash
    python examples/integrations/celery_plugin/celery_user_service.py
    ```

3. **Check Notifications**:
Check the output of the Notification Service to see the notification for the new user creation.



## Conclusion

This example illustrates the process of setting up and using Celery integration with Eolic to efficiently handle events across microservices, ensuring smooth and reliable communication between services.
