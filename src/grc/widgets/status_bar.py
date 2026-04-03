"""
Modern status bar widget for GRC application.

Displays image info, zoom level, annotation count, and keyboard hints.
"""

from PyQt5.QtWidgets import QLabel, QStatusBar, QWidget


class ModernStatusBar(QStatusBar):
    """Status bar with image info, zoom, and annotation stats."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizeGripEnabled(False)

        # Create status sections
        self._create_sections()

    def _create_sections(self):
        """Create status bar sections."""
        # Image info section
        self.image_info = QLabel("No image loaded")
        self.image_info.setObjectName("statusImageInfo")
        self.addWidget(self.image_info)

        self.addWidget(self._separator())

        # Zoom level
        self.zoom_label = QLabel("Zoom: 100%")
        self.zoom_label.setObjectName("statusZoom")
        self.addWidget(self.zoom_label)

        self.addWidget(self._separator())

        # Annotation count
        self.annotation_count = QLabel("Annotations: 0")
        self.annotation_count.setObjectName("statusAnnotations")
        self.addWidget(self.annotation_count)

        self.addWidget(self._separator())

        # Position indicator
        self.position_label = QLabel("Position: -")
        self.position_label.setObjectName("statusPosition")
        self.addWidget(self.position_label)

        # Spacer to push hints to the right
        spacer = QWidget()
        spacer.setMinimumWidth(50)
        self.addWidget(spacer, 1)

        # Keyboard hints (right side)
        self.hints_label = QLabel("Press ? for shortcuts")
        self.hints_label.setObjectName("statusHints")
        self.hints_label.setStyleSheet("color: #64ffda;")
        self.addPermanentWidget(self.hints_label)

    def _separator(self) -> QWidget:
        """Create a vertical separator."""
        sep = QWidget()
        sep.setFixedWidth(1)
        sep.setStyleSheet("background-color: #2d2d44; margin: 4px 8px;")
        return sep

    def update_image_info(self, filename: str, index: int, total: int):
        """Update image filename and position."""
        self.image_info.setText(f"📷 {filename} ({index}/{total})")

    def update_zoom(self, zoom_level: float):
        """Update zoom level display."""
        self.zoom_label.setText(f"🔍 {int(zoom_level * 100)}%")

    def update_annotation_count(self, count: int):
        """Update annotation count."""
        self.annotation_count.setText(f"📦 {count} annotations")

    def update_position(self, x: int, y: int):
        """Update cursor position display."""
        self.position_label.setText(f"📍 {x}, {y}")

    def update_status(self, message: str, timeout: int = 3000):
        """Show a temporary status message."""
        self.showMessage(message, timeout)

    def clear_position(self):
        """Clear position display."""
        self.position_label.setText("📍 -")
