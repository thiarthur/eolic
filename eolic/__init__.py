"""Eolic is a Python package for event-driven programming."""

from .base import Eolic
from .integrations.fastapi import FastAPIIntegration

__all__ = ["Eolic", "FastAPIIntegration"]
