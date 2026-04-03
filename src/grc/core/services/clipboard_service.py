"""
Clipboard service for copy/paste operations on annotations.

Provides a centralized clipboard for annotations that can be
copied and pasted between images or within the same image.
"""

from typing import List, Optional

from ..bounding_box import BoundingBox


class ClipboardService:
    """
    Service for managing annotation clipboard operations.

    Responsibilities:
    - Store copied annotations
    - Provide paste functionality with offset
    - Track clipboard state

    Follows SRP: Only handles clipboard operations.
    """

    # Default offset for pasted annotations (prevents overlap)
    PASTE_OFFSET_X = 20
    PASTE_OFFSET_Y = 20

    def __init__(self):
        """Initialize clipboard service."""
        self._clipboard: List[BoundingBox] = []
        self._source_image_width: Optional[int] = None
        self._source_image_height: Optional[int] = None

    @property
    def has_content(self) -> bool:
        """Check if clipboard has content."""
        return bool(self._clipboard)

    @property
    def count(self) -> int:
        """Get number of items in clipboard."""
        return len(self._clipboard)

    def copy(
        self,
        boxes: List[BoundingBox],
        image_width: Optional[int] = None,
        image_height: Optional[int] = None,
    ) -> int:
        """
        Copy annotations to clipboard.

        Args:
            boxes: List of BoundingBox objects to copy
            image_width: Optional source image width for coordinate clamping
            image_height: Optional source image height for coordinate clamping

        Returns:
            Number of boxes copied
        """
        if not boxes:
            self._clipboard = []
            return 0

        # Deep copy boxes to prevent reference issues
        self._clipboard = [
            BoundingBox(
                x=box.x,
                y=box.y,
                w=box.w,
                h=box.h,
                class_id=box.class_id,
                class_name=box.class_name,
                selected=False,  # Pasted boxes start unselected
            )
            for box in boxes
        ]

        self._source_image_width = image_width
        self._source_image_height = image_height

        return len(self._clipboard)

    def paste(
        self,
        offset_x: Optional[int] = None,
        offset_y: Optional[int] = None,
        target_image_width: Optional[int] = None,
        target_image_height: Optional[int] = None,
    ) -> List[BoundingBox]:
        """
        Paste annotations from clipboard.

        Args:
            offset_x: X offset for pasted boxes (default: PASTE_OFFSET_X)
            offset_y: Y offset for pasted boxes (default: PASTE_OFFSET_Y)
            target_image_width: Optional target image width for clamping
            target_image_height: Optional target image height for clamping

        Returns:
            List of new BoundingBox objects (deep copies)
        """
        if not self._clipboard:
            return []

        # Use default offsets if not provided
        dx = offset_x if offset_x is not None else self.PASTE_OFFSET_X
        dy = offset_y if offset_y is not None else self.PASTE_OFFSET_Y

        pasted_boxes = []

        for box in self._clipboard:
            new_x = box.x + dx
            new_y = box.y + dy

            # Clamp to target image bounds if provided
            if target_image_width is not None:
                new_x = min(new_x, target_image_width - box.w)
            if target_image_height is not None:
                new_y = min(new_y, target_image_height - box.h)

            # Ensure non-negative coordinates
            new_x = max(0, new_x)
            new_y = max(0, new_y)

            pasted_box = BoundingBox(
                x=new_x,
                y=new_y,
                w=box.w,
                h=box.h,
                class_id=box.class_id,
                class_name=box.class_name,
                selected=True,  # Pasted boxes are selected for immediate editing
            )
            pasted_boxes.append(pasted_box)

        return pasted_boxes

    def duplicate(self, boxes: List[BoundingBox]) -> List[BoundingBox]:
        """
        Duplicate annotations (copy + paste in one operation).

        Args:
            boxes: List of BoundingBox objects to duplicate

        Returns:
            List of duplicated BoundingBox objects
        """
        if not boxes:
            return []

        # Copy to clipboard and immediately paste
        self.copy(boxes)
        return self.paste()

    def clear(self) -> None:
        """Clear the clipboard."""
        self._clipboard = []
        self._source_image_width = None
        self._source_image_height = None

    def get_clipboard_info(self) -> dict:
        """
        Get information about clipboard contents.

        Returns:
            Dict with count, classes, and source dimensions
        """
        return {
            "count": len(self._clipboard),
            "classes": list({box.class_name for box in self._clipboard}),
            "source_width": self._source_image_width,
            "source_height": self._source_image_height,
        }
