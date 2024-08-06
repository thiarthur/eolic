"""File containing helpers for modules."""

import importlib.util

from typing import Any


def is_module_installed(module_name: str) -> bool:
    """
    Check if a Python module is installed.

    Args:
        module_name (str): The name of the module to check.

    Returns:
        bool: True if the module is installed, False otherwise.
    """
    return importlib.util.find_spec(module_name) is not None


def get_module(module_name: str) -> Any:
    """
    Import and returns a module by its name.

    Args:
        module_name (str): The name of the module to import, as a string.
    Returns:
        Any: The imported module.
    """
    return importlib.import_module(module_name)
