"""File containing utility functions for various tasks."""

import importlib.util


def is_module_installed(module_name: str) -> bool:
    """
    Check if a Python module is installed.

    Args:
        module_name (str): The name of the module to check.

    Returns:
        bool: True if the module is installed, False otherwise.
    """
    return importlib.util.find_spec(module_name) is not None
