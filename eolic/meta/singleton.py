"""
Module for implementing the Singleton metaclass.

This module provides a Singleton metaclass that ensures a class has only one instance.
"""

from __future__ import annotations

import typing as t

_T = t.TypeVar("_T")


class Singleton(type, t.Generic[_T]):
    """
    Metaclass for creating a Singleton.

    This metaclass ensures that a class has only one instance and provides a global
    point of access to it.

    Attributes:
        _instances (dict): Dictionary to store the singleton instances.
    """

    _instances: dict[Singleton[_T], _T] = {}

    def __call__(cls, *args: t.Any, **kwargs: t.Any) -> _T:
        """
        Call method to control the creation of the singleton instance.

        If the instance does not exist, it is created and stored in the _instances dictionary.
        If it already exists, the existing instance is returned.

        Args:
            *args (t.Any): Variable length argument list for the constructor.
            **kwargs (t.Any): Arbitrary keyword arguments for the constructor.

        Returns:
            _T: The singleton instance of the class.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
