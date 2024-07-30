"""File containing utility functions for various tasks."""

import importlib.util
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from celery import Celery


def is_module_installed(module_name: str) -> bool:
    """
    Check if a Python module is installed.

    Args:
        module_name (str): The name of the module to check.

    Returns:
        bool: True if the module is installed, False otherwise.
    """
    return importlib.util.find_spec(module_name) is not None


def get_celery(*args, **kwargs) -> "Celery":
    """
    Return an instance of the 'Celery' class from 'celery' package.

    Args:
        *args: Positional arguments to be passed to the `Celery` class constructor.
        **kwargs: Keyword arguments to be passed to the `Celery` class constructor.

    Returns:
        Celery: An instance of the `Celery` class from the 'celery' package.
    """
    return importlib.import_module("celery").Celery(*args, **kwargs)
