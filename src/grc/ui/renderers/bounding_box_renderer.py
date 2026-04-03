"""
BoundingBox renderer - separates rendering logic from the BoundingBox model.

This renderer handles all visual representation of bounding boxes,
including selection states, resize handles, and labels.
"""

from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen

from ...core.bounding_box import BoundingBox


class BoundingBoxRenderer:
    """
    Renderer for BoundingBox objects.

    Handles all visual rendering including:
    - Box outlines with selection states
    - Animated "marching ants" for selected boxes
    - Resize handles
    - Class labels with coordinates
    """

    # Rendering constants
    HANDLE_SIZE = 8
    CORNER_HANDLE_COLOR = "#FFFF00"  # Yellow
    SIDE_HANDLE_COLOR = "#00FFFF"  # Cyan
    HANDLE_BORDER_COLOR = "#000000"  # Black

    SELECTED_OPACITY = 0.5
    UNSELECTED_OPACITY = 0.2
    LABEL_OPACITY = 1.0

    def __init__(self):
        """Initialize the renderer with default settings."""
        self.handle_size = self.HANDLE_SIZE

    def draw_box(self, painter: QPainter, box: BoundingBox, phase: float = 0.0) -> None:
        """
        Draw a single bounding box.

        Args:
            painter: QPainter to draw with
            box: BoundingBox to render
            phase: Animation phase for marching ants (0.0 - 8.0)
        """
        if box.selected:
            self._draw_selected_box(painter, box, phase)
        else:
            self._draw_unselected_box(painter, box)

        # Draw label
        self._draw_label(painter, box)

        # Draw resize handles if selected
        if box.selected:
            self._draw_resize_handles(painter, box)

    def draw_boxes(
        self, painter: QPainter, boxes: List[BoundingBox], phase: float = 0.0
    ) -> None:
        """
        Draw multiple bounding boxes.

        Args:
            painter: QPainter to draw with
            boxes: List of BoundingBox objects
            phase: Animation phase for marching ants
        """
        for box in boxes:
            self.draw_box(painter, box, phase)

    def _draw_selected_box(
        self, painter: QPainter, box: BoundingBox, phase: float
    ) -> None:
        """Draw a selected box with marching ants animation."""
        painter.setOpacity(self.SELECTED_OPACITY)

        # Animated "marching ants" style
        pen = QPen(Qt.white, 2, Qt.DashLine)
        pen.setDashPattern([4, 4])
        pen.setDashOffset(phase)
        painter.setPen(pen)

        painter.drawRect(box.x, box.y, box.w, box.h)

    def _draw_unselected_box(self, painter: QPainter, box: BoundingBox) -> None:
        """Draw an unselected box with simple outline."""
        painter.setOpacity(self.UNSELECTED_OPACITY)
        painter.setPen(Qt.white)
        painter.drawRect(box.x, box.y, box.w, box.h)

    def _draw_label(self, painter: QPainter, box: BoundingBox) -> None:
        """Draw class label with coordinates above the box."""
        painter.setOpacity(self.LABEL_OPACITY)
        painter.setPen(Qt.white)

        # Create label text
        label_text = f"{box.class_name} ({box.x},{box.y},{box.w},{box.h})"

        # Get text dimensions
        font_metrics = painter.fontMetrics()
        text_rect = font_metrics.boundingRect(label_text)
        text_rect.moveTo(box.x, box.y - text_rect.height())

        # Draw background
        painter.fillRect(text_rect, Qt.black)

        # Draw text
        painter.drawText(text_rect, Qt.AlignCenter, label_text)

    def _draw_resize_handles(self, painter: QPainter, box: BoundingBox) -> None:
        """Draw resize handles at corners and sides."""
        painter.setOpacity(self.LABEL_OPACITY)

        # Corner handles (yellow)
        painter.setBrush(QBrush(QColor(self.CORNER_HANDLE_COLOR)))
        painter.setPen(QPen(QColor(self.HANDLE_BORDER_COLOR), 1))

        corner_handles = self._get_corner_handle_positions(box)
        for hx, hy in corner_handles:
            painter.drawRect(hx, hy, self.handle_size, self.handle_size)

        # Side handles (cyan)
        painter.setBrush(QBrush(QColor(self.SIDE_HANDLE_COLOR)))

        side_handles = self._get_side_handle_positions(box)
        for hx, hy in side_handles:
            painter.drawRect(hx, hy, self.handle_size, self.handle_size)

    def _get_corner_handle_positions(self, box: BoundingBox) -> List[tuple]:
        """Get positions for corner resize handles."""
        half = self.handle_size // 2
        return [
            (box.x - half, box.y - half),  # NW
            (box.x + box.w - half, box.y - half),  # NE
            (box.x - half, box.y + box.h - half),  # SW
            (box.x + box.w - half, box.y + box.h - half),  # SE
        ]

    def _get_side_handle_positions(self, box: BoundingBox) -> List[tuple]:
        """Get positions for side resize handles."""
        half = self.handle_size // 2
        return [
            (box.x + box.w // 2 - half, box.y - half),  # N
            (box.x + box.w // 2 - half, box.y + box.h - half),  # S
            (box.x + box.w - half, box.y + box.h // 2 - half),  # E
            (box.x - half, box.y + box.h // 2 - half),  # W
        ]

    def get_handle_at_point(
        self, box: BoundingBox, x: int, y: int
    ) -> Optional[str]:
        """
        Check if a point is over a resize handle.

        Args:
            box: BoundingBox to check
            x: X coordinate to check
            y: Y coordinate to check

        Returns:
            Handle name ('nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w') or None
        """
        half = self.handle_size // 2

        # Corner handles
        handles = {
            "nw": (box.x - half, box.y - half),
            "ne": (box.x + box.w - half, box.y - half),
            "sw": (box.x - half, box.y + box.h - half),
            "se": (box.x + box.w - half, box.y + box.h - half),
            "n": (box.x + box.w // 2 - half, box.y - half),
            "s": (box.x + box.w // 2 - half, box.y + box.h - half),
            "e": (box.x + box.w - half, box.y + box.h // 2 - half),
            "w": (box.x - half, box.y + box.h // 2 - half),
        }

        for handle_name, (hx, hy) in handles.items():
            if hx <= x <= hx + self.handle_size and hy <= y <= hy + self.handle_size:
                return handle_name

        return None

    def get_cursor_for_handle(self, handle: str) -> Qt.CursorShape:
        """
        Get the appropriate cursor shape for a handle.

        Args:
            handle: Handle name

        Returns:
            Qt cursor shape
        """
        if handle in ["nw", "se"]:
            return Qt.SizeFDiagCursor
        elif handle in ["ne", "sw"]:
            return Qt.SizeBDiagCursor
        elif handle in ["n", "s"]:
            return Qt.SizeVerCursor
        elif handle in ["e", "w"]:
            return Qt.SizeHorCursor
        return Qt.CrossCursor


# Singleton instance for convenience
_default_renderer: Optional[BoundingBoxRenderer] = None


def get_renderer() -> BoundingBoxRenderer:
    """Get the default BoundingBoxRenderer instance."""
    global _default_renderer
    if _default_renderer is None:
        _default_renderer = BoundingBoxRenderer()
    return _default_renderer
