"""
UI package for GRC application.

Contains controllers, renderers, and other UI-related components.
"""

from .controllers import AnnotationController, NavigationController
from .renderers import BoundingBoxRenderer

__all__ = [
    "NavigationController",
    "AnnotationController",
    "BoundingBoxRenderer",
]
