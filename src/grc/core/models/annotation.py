"""
Annotation model - pure data class for bounding box annotations.

This model contains only data, no rendering logic.
Rendering is handled by BoundingBoxRenderer in the UI layer.
"""

from dataclasses import dataclass


@dataclass
class Annotation:
    """
    Pure data model for a bounding box annotation.

    This is a dataclass version of BoundingBox that focuses
    on immutability and type safety. Use this for new code;
    BoundingBox is retained for backward compatibility.
    """

    x: int
    y: int
    width: int
    height: int
    class_id: int = 0
    class_name: str = "Unknown"
    selected: bool = False

    @property
    def area(self) -> int:
        """Calculate area of the annotation."""
        return self.width * self.height

    @property
    def right(self) -> int:
        """Get right edge x coordinate."""
        return self.x + self.width

    @property
    def bottom(self) -> int:
        """Get bottom edge y coordinate."""
        return self.y + self.height

    @property
    def center(self) -> tuple:
        """Get center point as (x, y) tuple."""
        return (self.x + self.width // 2, self.y + self.height // 2)

    def contains_point(self, px: int, py: int) -> bool:
        """Check if a point is inside this annotation."""
        return self.x <= px <= self.right and self.y <= py <= self.bottom

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "x": self.x,
            "y": self.y,
            "w": self.width,
            "h": self.height,
            "class_id": self.class_id,
            "class_name": self.class_name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Annotation":
        """Create from dictionary."""
        return cls(
            x=data.get("x", 0),
            y=data.get("y", 0),
            width=data.get("w", 0),
            height=data.get("h", 0),
            class_id=data.get("class_id", 0),
            class_name=data.get("class_name", "Unknown"),
        )

    def to_yolo(self, image_width: int, image_height: int) -> str:
        """
        Convert to YOLO format string.

        Args:
            image_width: Image width for normalization
            image_height: Image height for normalization

        Returns:
            YOLO format string: "class_id x_center y_center width height class_name"
        """
        x_center = (self.x + self.width / 2) / image_width
        y_center = (self.y + self.height / 2) / image_height
        norm_width = self.width / image_width
        norm_height = self.height / image_height

        # Clamp values
        x_center = max(0.0, min(1.0, x_center))
        y_center = max(0.0, min(1.0, y_center))
        norm_width = max(0.001, min(1.0, norm_width))
        norm_height = max(0.001, min(1.0, norm_height))

        return f"{self.class_id} {x_center:.8f} {y_center:.8f} {norm_width:.8f} {norm_height:.8f} {self.class_name}"


@dataclass
class AnnotationList:
    """Collection of annotations with helper methods."""

    annotations: list  # List[Annotation]

    @property
    def count(self) -> int:
        """Get total annotation count."""
        return len(self.annotations)

    @property
    def selected(self) -> list:
        """Get list of selected annotations."""
        return [a for a in self.annotations if a.selected]

    @property
    def selected_indices(self) -> list:
        """Get indices of selected annotations."""
        return [i for i, a in enumerate(self.annotations) if a.selected]

    def get_by_class(self, class_id: int) -> list:
        """Get annotations filtered by class ID."""
        return [a for a in self.annotations if a.class_id == class_id]

    def get_class_distribution(self) -> dict:
        """Get distribution of annotations by class name."""
        from collections import Counter

        return dict(Counter(a.class_name for a in self.annotations))

    def clear_selection(self) -> None:
        """Deselect all annotations."""
        for a in self.annotations:
            a.selected = False

    def select_all(self) -> None:
        """Select all annotations."""
        for a in self.annotations:
            a.selected = True

    def select_by_index(self, indices: list, exclusive: bool = True) -> None:
        """
        Select annotations by indices.

        Args:
            indices: List of indices to select
            exclusive: If True, deselect others first
        """
        if exclusive:
            self.clear_selection()

        for idx in indices:
            if 0 <= idx < len(self.annotations):
                self.annotations[idx].selected = True

    def remove_selected(self) -> int:
        """
        Remove all selected annotations.

        Returns:
            Number of annotations removed
        """
        original_count = len(self.annotations)
        self.annotations = [a for a in self.annotations if not a.selected]
        return original_count - len(self.annotations)
