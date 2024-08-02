"""Module for coroutine helpers."""

import asyncio
from typing import Any, Callable


def run_coroutine(coroutine: Callable[..., Any], *args, **kwargs) -> Any:
    """
    Run a coroutine in the appropriate context.

    Args:
        coroutine (Awaitable[Any]): The coroutine to run.

    Returns:
        Any: The result of the coroutine.
    """
    loop = asyncio.get_event_loop()
    if loop.is_running():
        return asyncio.ensure_future(coroutine(*args, **kwargs))
    else:
        return loop.run_until_complete(coroutine(*args, **kwargs))
