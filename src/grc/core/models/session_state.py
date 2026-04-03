"""
Session state model for tracking application session.

Encapsulates all session-level state including:
- Loaded images
- Classes configuration
- Current selection state
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class SessionState:
    """
    Immutable session state container.

    Represents the complete state of an annotation session.
    Use _replace() to create modified copies (namedtuple-style).
    """

    # Image state
    image_files: List[str] = field(default_factory=list)
    current_image_index: int = -1
    data_dir: str = ""

    # Class state
    classes: List[Tuple[int, str]] = field(default_factory=list)
    current_class_id: int = 0
    current_class_name: str = "Unknown"

    # Annotation state (per-image, managed by AnnotationService)
    annotations_modified: bool = False

    # UI state
    current_format: str = "grc"
    zoom_level: float = 1.0

    @property
    def has_images(self) -> bool:
        """Check if images are loaded."""
        return bool(self.image_files)

    @property
    def total_images(self) -> int:
        """Get total number of images."""
        return len(self.image_files)

    @property
    def current_image_path(self) -> Optional[str]:
        """Get path to current image."""
        if self.image_files and 0 <= self.current_image_index < len(self.image_files):
            return self.image_files[self.current_image_index]
        return None

    @property
    def has_classes(self) -> bool:
        """Check if classes are loaded."""
        return bool(self.classes)

    @property
    def class_count(self) -> int:
        """Get number of classes."""
        return len(self.classes)

    @property
    def class_names(self) -> List[str]:
        """Get list of class names."""
        return [name for _, name in self.classes]

    @property
    def class_ids(self) -> List[int]:
        """Get list of class IDs."""
        return [cid for cid, _ in self.classes]

    def get_class_name(self, class_id: int) -> str:
        """Get class name for a given ID."""
        for cid, name in self.classes:
            if cid == class_id:
                return name
        return f"Class_{class_id}"

    def get_class_id(self, class_name: str) -> int:
        """Get class ID for a given name."""
        for cid, name in self.classes:
            if name == class_name:
                return cid
        return 0

    def is_valid_class(self, class_id: int, class_name: str) -> bool:
        """Check if class ID and name match."""
        return any(cid == class_id and name == class_name for cid, name in self.classes)

    def can_navigate_previous(self) -> bool:
        """Check if can go to previous image."""
        return self.has_images and self.current_image_index > 0

    def can_navigate_next(self) -> bool:
        """Check if can go to next image."""
        return self.has_images and self.current_image_index < len(self.image_files) - 1

    def get_progress_info(self) -> Dict:
        """Get progress information for display."""
        return {
            "current": self.current_image_index + 1 if self.has_images else 0,
            "total": self.total_images,
            "has_previous": self.can_navigate_previous(),
            "has_next": self.can_navigate_next(),
        }

    def _replace(self, **kwargs) -> "SessionState":
        """
        Create a copy with modified fields.

        Mimics namedtuple _replace behavior for immutable updates.
        """
        current = {
            "image_files": self.image_files,
            "current_image_index": self.current_image_index,
            "data_dir": self.data_dir,
            "classes": self.classes,
            "current_class_id": self.current_class_id,
            "current_class_name": self.current_class_name,
            "annotations_modified": self.annotations_modified,
            "current_format": self.current_format,
            "zoom_level": self.zoom_level,
        }
        current.update(kwargs)
        return SessionState(**current)


def create_default_session() -> SessionState:
    """Create a default empty session state."""
    return SessionState()
