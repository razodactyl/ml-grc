"""
Annotation controller for managing annotation interactions.

Handles annotation creation, selection, modification,
and coordinates between UI and AnnotationService.
"""

from typing import Callable, List, Optional, Tuple

from ...core.bounding_box import BoundingBox
from ...core.events import EventBus
from ...core.services.annotation_service import AnnotationService
from ...core.services.clipboard_service import ClipboardService


class AnnotationController:
    """
    Controller for annotation management.

    Responsibilities:
    - Handle annotation creation from user input
    - Manage selection state
    - Coordinate with AnnotationService
    - Handle undo/redo operations
    """

    # Minimum annotation area to create
    MIN_ANNOTATION_AREA = 20

    def __init__(
        self,
        annotation_service: AnnotationService,
        event_bus: Optional[EventBus] = None,
        clipboard_service: Optional[ClipboardService] = None,
    ):
        """
        Initialize annotation controller.

        Args:
            annotation_service: Service for annotation management
            event_bus: Optional event bus for publishing events
            clipboard_service: Optional clipboard service for copy/paste
        """
        self.annotation_service = annotation_service
        self.event_bus = event_bus
        self.clipboard_service = clipboard_service or ClipboardService()

        # Current class for new annotations
        self._current_class_id: int = 0
        self._current_class_name: str = "Unknown"

        # Image dimensions for coordinate clamping
        self._image_width: int = 800
        self._image_height: int = 600

        # Undo/redo stacks
        self._undo_stack: List[List[BoundingBox]] = []
        self._redo_stack: List[List[BoundingBox]] = []
        self._max_history: int = 100

        # Callbacks
        self._on_annotations_changed: Optional[Callable] = None
        self._on_selection_changed: Optional[Callable] = None

    def set_callbacks(
        self,
        on_annotations_changed: Optional[Callable] = None,
        on_selection_changed: Optional[Callable] = None,
    ) -> None:
        """
        Set callbacks for UI updates.

        Args:
            on_annotations_changed: Called when annotations change
            on_selection_changed: Called when selection changes
        """
        self._on_annotations_changed = on_annotations_changed
        self._on_selection_changed = on_selection_changed

    def set_current_class(self, class_id: int, class_name: str) -> None:
        """Set the current class for new annotations."""
        self._current_class_id = class_id
        self._current_class_name = class_name

    def get_current_class(self) -> Tuple[int, str]:
        """Get current class for new annotations."""
        return self._current_class_id, self._current_class_name

    def create_annotation(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        class_id: Optional[int] = None,
        class_name: Optional[str] = None,
    ) -> Optional[BoundingBox]:
        """
        Create a new annotation.

        Args:
            x: X coordinate (top-left)
            y: Y coordinate (top-left)
            width: Width
            height: Height
            class_id: Optional class ID (uses current if not provided)
            class_name: Optional class name (uses current if not provided)

        Returns:
            Created BoundingBox, or None if too small
        """
        # Check minimum area
        if abs(width * height) < self.MIN_ANNOTATION_AREA:
            return None

        # Normalize negative dimensions
        if width < 0:
            x = x + width
            width = abs(width)
        if height < 0:
            y = y + height
            height = abs(height)

        box = BoundingBox(
            x=x,
            y=y,
            w=width,
            h=height,
            selected=True,
            class_id=class_id if class_id is not None else self._current_class_id,
            class_name=class_name if class_name is not None else self._current_class_name,
        )

        # Save undo state
        self._push_undo_state()

        # Add to annotations
        self.annotation_service.add_annotation(box)

        # Notify
        self._notify_annotations_changed()

        return box

    def select_annotation(
        self,
        index: int,
        exclusive: bool = True,
        toggle: bool = False,
    ) -> bool:
        """
        Select an annotation by index.

        Args:
            index: Annotation index
            exclusive: If True, deselect others
            toggle: If True, toggle selection

        Returns:
            True if selection changed
        """
        boxes = self.annotation_service.bounding_boxes

        if not (0 <= index < len(boxes)):
            return False

        if exclusive:
            for i, box in enumerate(boxes):
                box.selected = i == index
        elif toggle:
            boxes[index].selected = not boxes[index].selected
        else:
            boxes[index].selected = True

        self._notify_selection_changed()
        return True

    def select_at_point(
        self,
        x: int,
        y: int,
        exclusive: bool = True,
        toggle: bool = False,
    ) -> Optional[int]:
        """
        Select annotation at a point.

        Args:
            x: X coordinate
            y: Y coordinate
            exclusive: If True, deselect others
            toggle: If True, toggle selection

        Returns:
            Index of selected annotation, or None
        """
        boxes = self.annotation_service.bounding_boxes

        # Check in reverse order (top-most first)
        for i in range(len(boxes) - 1, -1, -1):
            if boxes[i].xy_in_bounds(x, y):
                self.select_annotation(i, exclusive=exclusive, toggle=toggle)
                return i

        # Clicked on empty space
        if exclusive and not toggle:
            self.clear_selection()

        return None

    def clear_selection(self) -> None:
        """Clear all selection."""
        for box in self.annotation_service.bounding_boxes:
            box.selected = False
        self._notify_selection_changed()

    def select_all(self) -> None:
        """Select all annotations."""
        for box in self.annotation_service.bounding_boxes:
            box.selected = True
        self._notify_selection_changed()

    def get_selected_indices(self) -> List[int]:
        """Get indices of selected annotations."""
        return [
            i
            for i, box in enumerate(self.annotation_service.bounding_boxes)
            if box.selected
        ]

    def get_selected_boxes(self) -> List[BoundingBox]:
        """Get selected bounding boxes."""
        return [box for box in self.annotation_service.bounding_boxes if box.selected]

    def delete_selected(self) -> int:
        """
        Delete selected annotations.

        Returns:
            Number of annotations deleted
        """
        indices = self.get_selected_indices()

        if not indices:
            return 0

        self._push_undo_state()
        self.annotation_service.remove_annotations(indices)
        self._notify_annotations_changed()

        return len(indices)

    def move_selected(self, dx: int, dy: int) -> None:
        """Move selected annotations by delta."""
        for box in self.annotation_service.bounding_boxes:
            if box.selected:
                box.x = max(0, box.x + dx)
                box.y = max(0, box.y + dy)

        self._notify_annotations_changed()

    def change_class_of_selected(self, class_id: int, class_name: str) -> int:
        """
        Change class of selected annotations.

        Args:
            class_id: New class ID
            class_name: New class name

        Returns:
            Number of annotations changed
        """
        count = 0
        for box in self.annotation_service.bounding_boxes:
            if box.selected:
                box.class_id = class_id
                box.class_name = class_name
                count += 1

        if count > 0:
            self._notify_annotations_changed()

        return count

    def set_image_dimensions(self, width: int, height: int) -> None:
        """Set current image dimensions for coordinate clamping."""
        self._image_width = width
        self._image_height = height

    # --- Clipboard Operations ---

    def copy_selected(self) -> int:
        """
        Copy selected annotations to clipboard.

        Returns:
            Number of boxes copied
        """
        selected = self.get_selected_boxes()
        if selected:
            self.clipboard_service.copy(
                selected,
                image_width=self._image_width,
                image_height=self._image_height,
            )
            return len(selected)
        return 0

    def paste(self) -> int:
        """
        Paste annotations from clipboard.

        Returns:
            Number of boxes pasted
        """
        if not self.clipboard_service.has_content:
            return 0

        self._push_undo_state()

        pasted = self.clipboard_service.paste(
            target_image_width=self._image_width,
            target_image_height=self._image_height,
        )

        for box in pasted:
            self.annotation_service.add_annotation(box)

        self._notify_annotations_changed()
        return len(pasted)

    def duplicate_selected(self) -> int:
        """
        Duplicate selected annotations (copy + paste).

        Returns:
            Number of boxes duplicated
        """
        selected = self.get_selected_boxes()
        if not selected:
            return 0

        self._push_undo_state()

        duplicated = self.clipboard_service.duplicate(selected)

        for box in duplicated:
            self.annotation_service.add_annotation(box)

        self._notify_annotations_changed()
        return len(duplicated)

    def has_clipboard_content(self) -> bool:
        """Check if clipboard has content."""
        return self.clipboard_service.has_content

    # --- Keyboard Navigation ---

    def nudge_selected(self, dx: int, dy: int) -> None:
        """
        Nudge selected annotations by a small amount.

        Args:
            dx: X offset (pixels)
            dy: Y offset (pixels)
        """
        selected = self.get_selected_boxes()
        if not selected:
            return

        self._push_undo_state()

        for box in selected:
            new_x = box.x + dx
            new_y = box.y + dy

            # Clamp to image bounds
            new_x = max(0, min(new_x, self._image_width - box.w))
            new_y = max(0, min(new_y, self._image_height - box.h))

            box.x = new_x
            box.y = new_y

        self._notify_annotations_changed()

    def resize_selected(self, dw: int, dh: int) -> None:
        """
        Resize selected annotations.

        Args:
            dw: Width delta (pixels)
            dh: Height delta (pixels)
        """
        selected = self.get_selected_boxes()
        if not selected:
            return

        self._push_undo_state()

        for box in selected:
            new_w = max(10, box.w + dw)
            new_h = max(10, box.h + dh)

            # Clamp to image bounds
            if box.x + new_w > self._image_width:
                new_w = self._image_width - box.x
            if box.y + new_h > self._image_height:
                new_h = self._image_height - box.y

            box.w = max(10, new_w)
            box.h = max(10, new_h)

        self._notify_annotations_changed()

    # --- Undo/Redo ---

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return bool(self._undo_stack)

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return bool(self._redo_stack)

    def undo(self) -> bool:
        """
        Undo last annotation change.

        Returns:
            True if undo was performed
        """
        if not self._undo_stack:
            return False

        # Save current state to redo stack
        self._redo_stack.append(self._snapshot_boxes())

        # Restore from undo stack
        boxes = self._undo_stack.pop()
        self.annotation_service.bounding_boxes = boxes

        self._notify_annotations_changed()
        return True

    def redo(self) -> bool:
        """
        Redo last undone change.

        Returns:
            True if redo was performed
        """
        if not self._redo_stack:
            return False

        # Save current state to undo stack
        self._undo_stack.append(self._snapshot_boxes())

        # Restore from redo stack
        boxes = self._redo_stack.pop()
        self.annotation_service.bounding_boxes = boxes

        self._notify_annotations_changed()
        return True

    def _push_undo_state(self) -> None:
        """Push current state to undo stack."""
        self._undo_stack.append(self._snapshot_boxes())
        self._redo_stack.clear()

        # Limit history size
        if len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)

    def _snapshot_boxes(self) -> List[BoundingBox]:
        """Create a deep copy of current bounding boxes."""
        return [
            BoundingBox(
                x=box.x,
                y=box.y,
                w=box.w,
                h=box.h,
                selected=box.selected,
                class_id=box.class_id,
                class_name=box.class_name,
            )
            for box in self.annotation_service.bounding_boxes
        ]

    # --- Notifications ---

    def _notify_annotations_changed(self) -> None:
        """Notify listeners of annotation changes."""
        if self._on_annotations_changed:
            self._on_annotations_changed(self.annotation_service.bounding_boxes)

    def _notify_selection_changed(self) -> None:
        """Notify listeners of selection changes."""
        if self._on_selection_changed:
            self._on_selection_changed(self.get_selected_boxes())
