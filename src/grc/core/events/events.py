"""
Typed event definitions for GRC application.

Each event represents a specific occurrence in the application
that other components may want to react to.
"""

from dataclasses import dataclass
from typing import List

from .event_bus import Event


@dataclass
class ImageChangedEvent(Event):
    """Emitted when the current image changes."""

    image_path: str = ""
    image_index: int = 0
    total_images: int = 0


@dataclass
class ImageLoadedEvent(Event):
    """Emitted when an image is successfully loaded."""

    image_path: str = ""
    width: int = 0
    height: int = 0


@dataclass
class AnnotationAddedEvent(Event):
    """Emitted when a new annotation is added."""

    annotation_id: int = -1
    class_id: int = 0
    class_name: str = ""
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0


@dataclass
class AnnotationRemovedEvent(Event):
    """Emitted when an annotation is removed."""

    annotation_ids: List[int] = None

    def __post_init__(self):
        if self.annotation_ids is None:
            self.annotation_ids = []


@dataclass
class AnnotationChangedEvent(Event):
    """Emitted when an annotation is modified (moved, resized, class changed)."""

    annotation_id: int = -1
    change_type: str = ""  # "move", "resize", "class_change"


@dataclass
class ZoomChangedEvent(Event):
    """Emitted when zoom level changes."""

    zoom_level: float = 1.0
    min_zoom: float = 0.1
    max_zoom: float = 10.0


@dataclass
class ClassChangedEvent(Event):
    """Emitted when the active class for new annotations changes."""

    class_id: int = 0
    class_name: str = ""


@dataclass
class NavigationEvent(Event):
    """Emitted for navigation actions (previous/next image)."""

    direction: str = ""  # "previous", "next"
    from_index: int = 0
    to_index: int = 0


@dataclass
class FormatChangedEvent(Event):
    """Emitted when annotation format changes."""

    old_format: str = ""
    new_format: str = ""


@dataclass
class SessionLoadedEvent(Event):
    """Emitted when a session (folder + classes) is loaded."""

    image_count: int = 0
    class_count: int = 0
    data_dir: str = ""


@dataclass
class AnnotationsSavedEvent(Event):
    """Emitted when annotations are saved."""

    image_path: str = ""
    annotation_count: int = 0
    format_name: str = ""
