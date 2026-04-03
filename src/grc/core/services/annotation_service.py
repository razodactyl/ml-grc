"""
Annotation service for managing bounding box annotations.

Encapsulates all annotation-related business logic including:
- Loading annotations from various formats
- Saving annotations
- Format conversion and management
- Annotation state coordination
"""

import os
from typing import Callable, List, Optional, Tuple

from PyQt5.QtWidgets import QMessageBox

from ..bounding_box import BoundingBox
from ..events import AnnotationAddedEvent, AnnotationRemovedEvent, AnnotationsSavedEvent, EventBus


class AnnotationService:
    """
    Service for annotation management.

    Responsibilities:
    - Load/save annotations in various formats
    - Coordinate annotation state
    - Handle format switching logic
    - Provide annotation statistics
    """

    def __init__(self, format_manager, event_bus: Optional[EventBus] = None):
        """
        Initialize annotation service.

        Args:
            format_manager: AnnotationFormatManager instance
            event_bus: Optional event bus for publishing events
        """
        self.format_manager = format_manager
        self.event_bus = event_bus

        # Current annotation state
        self._bounding_boxes: List[BoundingBox] = []
        self._current_image_path: str = ""
        self._image_width: int = 800
        self._image_height: int = 600

    @property
    def bounding_boxes(self) -> List[BoundingBox]:
        """Get current bounding boxes."""
        return self._bounding_boxes

    @bounding_boxes.setter
    def bounding_boxes(self, boxes: List[BoundingBox]) -> None:
        """Set bounding boxes."""
        self._bounding_boxes = boxes

    def load_annotations_for_image(
        self,
        image_path: str,
        image_width: int,
        image_height: int,
    ) -> List[BoundingBox]:
        """
        Load annotations for an image using the current format.

        Args:
            image_path: Path to the image file
            image_width: Image width in pixels
            image_height: Image height in pixels

        Returns:
            List of BoundingBox objects
        """
        self._current_image_path = image_path
        self._image_width = image_width
        self._image_height = image_height

        try:
            annotation_path = self.format_manager.get_annotation_path(
                image_path, self.format_manager.default_format
            )
            format_handler = self.format_manager.get_format(self.format_manager.default_format)

            print(
                f"Loading annotations from {annotation_path} "
                f"(format: {self.format_manager.default_format})"
            )

            boxes = format_handler.load(annotation_path, image_width, image_height)
            self._bounding_boxes = boxes

            print(f"Loaded {len(boxes)} annotations for {os.path.basename(image_path)}")

            return boxes

        except Exception as e:
            print(f"Error loading annotations for {image_path}: {e}")
            self._bounding_boxes = []
            return []

    def save_annotations(
        self,
        image_path: str,
        bounding_boxes: List[BoundingBox],
        image_width: int,
        image_height: int,
        format_name: Optional[str] = None,
    ) -> bool:
        """
        Save annotations for an image.

        Args:
            image_path: Path to the image file
            bounding_boxes: List of BoundingBox objects to save
            image_width: Image width in pixels
            image_height: Image height in pixels
            format_name: Optional format name (defaults to current format)

        Returns:
            True if save was successful
        """
        if format_name is None:
            format_name = self.format_manager.default_format

        try:
            self.format_manager.save_annotations(
                image_path, bounding_boxes, image_width, image_height, format_name=format_name
            )

            if self.event_bus:
                self.event_bus.publish(
                    AnnotationsSavedEvent(
                        source=self,
                        image_path=image_path,
                        annotation_count=len(bounding_boxes),
                        format_name=format_name,
                    )
                )

            return True

        except Exception as e:
            print(f"Error saving annotations: {e}")
            return False

    def set_annotation_format(
        self,
        format_name: str,
        current_image_path: str,
        current_boxes: List[BoundingBox],
        image_width: int,
        image_height: int,
        parent_widget=None,
    ) -> Tuple[str, List[BoundingBox]]:
        """
        Set annotation format with user interaction for conflict resolution.

        Args:
            format_name: New format name
            current_image_path: Path to current image
            current_boxes: Current bounding boxes in memory
            image_width: Image width
            image_height: Image height
            parent_widget: Parent widget for dialogs (optional)

        Returns:
            Tuple of (action_taken, resulting_boxes)
            action_taken: "loaded", "kept", "merged", "cleared", "cancelled"
        """
        old_format = self.format_manager.default_format

        if old_format == format_name:
            return "no_change", current_boxes

        # Check if annotation file exists in new format
        new_format_path = self.format_manager.get_annotation_path(
            current_image_path, format_name
        )
        new_format_exists = os.path.exists(new_format_path)

        # Determine action based on current state and new format availability
        if current_boxes and new_format_exists:
            # Both exist - need user decision
            if parent_widget:
                return self._handle_format_conflict(
                    format_name,
                    old_format,
                    current_image_path,
                    current_boxes,
                    image_width,
                    image_height,
                    parent_widget,
                )
            else:
                # No parent - default to loading from new format
                self.format_manager.set_default_format(format_name)
                boxes = self.load_annotations_for_image(
                    current_image_path, image_width, image_height
                )
                return "loaded", boxes

        elif current_boxes and not new_format_exists:
            # Current boxes exist, no new format file
            self.format_manager.set_default_format(format_name)
            return "kept", current_boxes

        elif not current_boxes and new_format_exists:
            # No current boxes, file exists - load it
            self.format_manager.set_default_format(format_name)
            boxes = self.load_annotations_for_image(
                current_image_path, image_width, image_height
            )
            return "loaded", boxes

        else:
            # Neither exist - just switch format
            self.format_manager.set_default_format(format_name)
            return "switched", []

    def _handle_format_conflict(
        self,
        format_name: str,
        old_format: str,
        current_image_path: str,
        current_boxes: List[BoundingBox],
        image_width: int,
        image_height: int,
        parent_widget,
    ) -> Tuple[str, List[BoundingBox]]:
        """Handle format conflict with user dialog."""
        reply = QMessageBox.question(
            parent_widget,
            "Format Switch",
            f"You have {len(current_boxes)} annotation(s) in memory.\n\n"
            f"An annotation file exists in {format_name.upper()} format.\n\n"
            f"What would you like to do?\n\n"
            f"• Yes: Load annotations from {format_name.upper()} file (discard current)\n"
            f"• No: Keep current annotations (can save to {format_name.upper()} later)\n"
            f"• Cancel: Revert to {old_format.upper()} format",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.No,
        )

        if reply == QMessageBox.Cancel:
            return "cancelled", current_boxes

        elif reply == QMessageBox.Yes:
            # Load from new format file
            self.format_manager.set_default_format(format_name)
            boxes = self.load_annotations_for_image(
                current_image_path, image_width, image_height
            )
            return "loaded", boxes

        else:  # QMessageBox.No
            # Ask about merging
            merge_reply = QMessageBox.question(
                parent_widget,
                "Merge Annotations?",
                f"Would you like to also load and merge the annotations from the "
                f"{format_name.upper()} file?\n\n"
                f"This will add {len(current_boxes)} current annotations + "
                f"annotations from file.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )

            self.format_manager.set_default_format(format_name)

            if merge_reply == QMessageBox.Yes:
                # Load and merge
                format_handler = self.format_manager.get_format(format_name)
                new_format_path = self.format_manager.get_annotation_path(
                    current_image_path, format_name
                )
                file_annotations = format_handler.load(
                    new_format_path, image_width, image_height
                )

                if file_annotations:
                    merged_boxes = current_boxes + file_annotations
                    return "merged", merged_boxes
                else:
                    return "kept", current_boxes
            else:
                return "kept", current_boxes

    def get_annotation_statistics(
        self,
        image_files: List[str],
        get_annotations_func: Callable[[str], List[BoundingBox]],
    ) -> dict:
        """
        Calculate annotation statistics for a set of images.

        Args:
            image_files: List of image file paths
            get_annotations_func: Function to get annotations for an image

        Returns:
            Dict with statistics: total_images, annotated_count, total_annotations,
                                  class_distribution
        """
        from collections import Counter

        total_images = len(image_files)
        annotated_count = 0
        total_annotations = 0
        class_counter = Counter()

        for image_path in image_files:
            annotations = get_annotations_func(image_path)
            if annotations:
                annotated_count += 1
                total_annotations += len(annotations)
                for box in annotations:
                    class_counter[box.class_name] += 1

        return {
            "total_images": total_images,
            "annotated_count": annotated_count,
            "total_annotations": total_annotations,
            "class_distribution": dict(class_counter),
        }

    def add_annotation(self, box: BoundingBox) -> None:
        """Add a new annotation and emit event."""
        self._bounding_boxes.append(box)

        if self.event_bus:
            self.event_bus.publish(
                AnnotationAddedEvent(
                    source=self,
                    annotation_id=len(self._bounding_boxes) - 1,
                    class_id=box.class_id,
                    class_name=box.class_name,
                    x=box.x,
                    y=box.y,
                    width=box.w,
                    height=box.h,
                )
            )

    def remove_annotations(self, indices: List[int]) -> None:
        """Remove annotations by indices and emit event."""
        # Remove in reverse order to maintain indices
        for idx in sorted(indices, reverse=True):
            if 0 <= idx < len(self._bounding_boxes):
                del self._bounding_boxes[idx]

        if self.event_bus:
            self.event_bus.publish(
                AnnotationRemovedEvent(
                    source=self,
                    annotation_ids=indices,
                )
            )

    def clear_annotations(self) -> None:
        """Clear all annotations."""
        if self._bounding_boxes:
            indices = list(range(len(self._bounding_boxes)))
            self._bounding_boxes = []

            if self.event_bus:
                self.event_bus.publish(
                    AnnotationRemovedEvent(
                        source=self,
                        annotation_ids=indices,
                    )
                )
