"""
BoundingBox data model for image annotations.
"""

from PyQt5.QtCore import Qt


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
