"""
Renderers for UI components.

Renderers are responsible for drawing domain models
without the models knowing about rendering details.
"""

from .bounding_box_renderer import BoundingBoxRenderer

__all__ = ["BoundingBoxRenderer"]
