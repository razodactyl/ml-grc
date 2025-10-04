"""
BoundingBox data model for image annotations.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPen, QBrush


class BoundingBox(object):
    """Represents a rectangular bounding box annotation."""
    
    def __init__(self, x=0, y=0, w=0, h=0, selected=False, class_id=0, class_name=""):
        """
        Initialize a bounding box.
        
        Args:
            x (int): X coordinate of top-left corner
            y (int): Y coordinate of top-left corner
            w (int): Width of the box
            h (int): Height of the box
            selected (bool): Whether this box is currently selected
            class_id (int): Class ID for this annotation
            class_name (str): Class name for this annotation
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.selected = selected
        self.class_id = class_id
        self.class_name = class_name

    def xy_in_bounds(self, x, y):
        """
        Check if a point is within this bounding box.
        
        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            
        Returns:
            bool: True if point is within bounds
        """
        return self.x < x < (self.x + self.w) and self.y < y < (self.y + self.h)

    def get_area(self):
        """
        Calculate the area of this bounding box.
        
        Returns:
            int: Area of the box
        """
        return self.w * self.h

    def draw(self, painter):
        """
        Draw this bounding box on a QPainter.
        
        Args:
            painter (QPainter): The painter to draw on
        """
        if self.selected:
            painter.setOpacity(0.5)
        else:
            painter.setOpacity(0.2)
        
        # Draw the rectangle
        painter.drawRect(
            self.x,
            self.y,
            self.w,
            self.h
        )
        
        # Draw label with coordinates and class name
        painter.setOpacity(1.0)  # Full opacity for text
        painter.setPen(Qt.white)
        
        # Create label text
        label_text = f"{self.class_name} ({self.x},{self.y},{self.w},{self.h})"
        
        # Draw text background
        font_metrics = painter.fontMetrics()
        text_rect = font_metrics.boundingRect(label_text)
        text_rect.moveTo(self.x, self.y - text_rect.height())
        
        # Draw background rectangle for text
        painter.fillRect(text_rect, Qt.black)
        
        # Draw the text
        painter.drawText(text_rect, Qt.AlignCenter, label_text)

        # Draw resize handles if selected
        self.draw_resize_handles(painter)

    def get_resize_handle_at_point(self, x, y, handle_size=8):
        """
        Check if a point is over a resize handle.
        
        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            handle_size (int): Size of resize handles in pixels
            
        Returns:
            str or None: Handle name if point is over handle, None otherwise
        """
        handles = {
            'nw': (self.x - handle_size//2, self.y - handle_size//2, handle_size, handle_size),
            'ne': (self.x + self.w - handle_size//2, self.y - handle_size//2, handle_size, handle_size),
            'sw': (self.x - handle_size//2, self.y + self.h - handle_size//2, handle_size, handle_size),
            'se': (self.x + self.w - handle_size//2, self.y + self.h - handle_size//2, handle_size, handle_size),
            'n': (self.x + self.w//2 - handle_size//2, self.y - handle_size//2, handle_size, handle_size),
            's': (self.x + self.w//2 - handle_size//2, self.y + self.h - handle_size//2, handle_size, handle_size),
            'e': (self.x + self.w - handle_size//2, self.y + self.h//2 - handle_size//2, handle_size, handle_size),
            'w': (self.x - handle_size//2, self.y + self.h//2 - handle_size//2, handle_size, handle_size),
        }
        
        for handle_name, (hx, hy, hw, hh) in handles.items():
            if hx <= x <= hx + hw and hy <= y <= hy + hh:
                return handle_name
        
        return None

    def draw_resize_handles(self, painter, handle_size=8):
        """
        Draw resize handles for this bounding box.
        
        Args:
            painter (QPainter): The painter to draw on
            handle_size (int): Size of resize handles in pixels
        """
        if not self.selected:
            return
            
        painter.setOpacity(1.0)
        painter.setBrush(QBrush(QColor("#FFFF00")))  # Yellow handles
        painter.setPen(QPen(QColor("#000000"), 1))   # Black border
        
        # Corner handles
        corner_handles = [
            (self.x - handle_size//2, self.y - handle_size//2),  # NW
            (self.x + self.w - handle_size//2, self.y - handle_size//2),  # NE
            (self.x - handle_size//2, self.y + self.h - handle_size//2),  # SW
            (self.x + self.w - handle_size//2, self.y + self.h - handle_size//2),  # SE
        ]
        
        for hx, hy in corner_handles:
            painter.drawRect(hx, hy, handle_size, handle_size)
        
        # Side handles (optional, but good for precision)
        side_handles = [
            (self.x + self.w//2 - handle_size//2, self.y - handle_size//2),  # N
            (self.x + self.w//2 - handle_size//2, self.y + self.h - handle_size//2),  # S
            (self.x + self.w - handle_size//2, self.y + self.h//2 - handle_size//2),  # E
            (self.x - handle_size//2, self.y + self.h//2 - handle_size//2),  # W
        ]
        
        painter.setBrush(QBrush(QColor("#00FFFF")))  # Cyan for side handles
        for hx, hy in side_handles:
            painter.drawRect(hx, hy, handle_size, handle_size)
