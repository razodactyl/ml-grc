"""
Modern image controls widget for GRC application.

Provides navigation, save/reload controls with keyboard shortcuts.
"""

from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)


class ImageControlsWidget(QWidget):
    """Control bar for image navigation and annotation actions."""

    def __init__(self):
        super().__init__()
        self.classes = []
        self.init_ui()

    def init_ui(self):
        """Initialize the control bar UI."""
        self.setObjectName("imageControls")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(56)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(8)

        # Navigation section
        nav_label = QLabel("Navigation")
        nav_label.setObjectName("subheading")
        layout.addWidget(nav_label)

        self.prevButton = self._create_button("◀ Previous", "Previous image (← / A)")
        self.nextButton = self._create_button("Next ▶", "Next image (→ / D)")

        layout.addWidget(self.prevButton)
        layout.addWidget(self.nextButton)

        # Spacer
        layout.addSpacerItem(QSpacerItem(20, 0))

        # Actions section
        actions_label = QLabel("Actions")
        actions_label.setObjectName("subheading")
        layout.addWidget(actions_label)

        self.saveButton = self._create_button("💾 Save", "Save annotations (S)", primary=True)
        self.reloadButton = self._create_button("🔄 Reload", "Reload from disk (R)")

        layout.addWidget(self.saveButton)
        layout.addWidget(self.reloadButton)

        # Stretch to push zoom controls to the right
        layout.addStretch()

        # Zoom section (right-aligned)
        zoom_label = QLabel("Zoom")
        zoom_label.setObjectName("subheading")
        layout.addWidget(zoom_label)

        self.zoomOutButton = self._create_button("−", "Zoom out (-)", small=True)
        self.zoomResetButton = self._create_button("100%", "Reset zoom (0)", small=True)
        self.zoomInButton = self._create_button("+", "Zoom in (+)", small=True)

        layout.addWidget(self.zoomOutButton)
        layout.addWidget(self.zoomResetButton)
        layout.addWidget(self.zoomInButton)

        # Connect signals
        self.prevButton.clicked.connect(self.clicked_prev)
        self.nextButton.clicked.connect(self.clicked_next)
        self.saveButton.clicked.connect(self.clicked_save)
        self.reloadButton.clicked.connect(self.clicked_reload)
        self.zoomInButton.clicked.connect(self.clicked_zoom_in)
        self.zoomOutButton.clicked.connect(self.clicked_zoom_out)
        self.zoomResetButton.clicked.connect(self.clicked_zoom_reset)

        self.setLayout(layout)

    def _create_button(
        self, text: str, tooltip: str, primary: bool = False, small: bool = False
    ) -> QPushButton:
        """Create a styled button."""
        btn = QPushButton(text)
        btn.setToolTip(tooltip)

        if primary:
            btn.setObjectName("primaryButton")
        if small:
            btn.setFixedSize(36, 32)
        else:
            btn.setMinimumWidth(90)

        return btn

    def update_zoom_display(self, zoom_level: float):
        """Update the zoom reset button text."""
        self.zoomResetButton.setText(f"{int(zoom_level * 100)}%")

    def clicked_prev(self):
        """Handle previous button click."""
        if hasattr(self, "parent_app") and self.parent_app:
            self.parent_app.previous_image()

    def clicked_next(self):
        """Handle next button click."""
        if hasattr(self, "parent_app") and self.parent_app:
            self.parent_app.next_image()

    def clicked_save(self):
        """Handle save button click."""
        if hasattr(self, "parent_app") and self.parent_app:
            self.parent_app.save_annotations_for_current_image()

    def clicked_reload(self):
        """Handle reload button click."""
        if hasattr(self, "parent_app") and self.parent_app:
            self.parent_app.reload_annotations_for_current_image()

    def clicked_zoom_in(self):
        """Handle zoom in button click."""
        if (
            hasattr(self, "parent_app")
            and self.parent_app
            and hasattr(self.parent_app, "image_panel")
        ):
            self.parent_app.image_panel.zoom_in()

    def clicked_zoom_out(self):
        """Handle zoom out button click."""
        if (
            hasattr(self, "parent_app")
            and self.parent_app
            and hasattr(self.parent_app, "image_panel")
        ):
            self.parent_app.image_panel.zoom_out()

    def clicked_zoom_reset(self):
        """Handle zoom reset button click."""
        if (
            hasattr(self, "parent_app")
            and self.parent_app
            and hasattr(self.parent_app, "image_panel")
        ):
            self.parent_app.image_panel.reset_zoom()
