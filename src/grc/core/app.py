"""
Main application class for GRC.

This class serves as the main window and coordinator for the application.
Business logic is delegated to services and controllers.
"""

import os
from typing import List, Optional, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import (
    QDesktopWidget,
    QFileDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ..ui.controllers import AnnotationController, NavigationController
from ..widgets.batch_widget import BatchWidget
from ..widgets.class_list_widget import ClassListWidget
from ..widgets.file_list_widget import FileListWidget
from ..widgets.image_controls import ImageControlsWidget
from ..widgets.image_widget import ImageWidget
from ..widgets.stats_widget import StatsWidget
from ..widgets.status_bar import ModernStatusBar
from ..widgets.styles import MODERN_DARK_THEME
from ..widgets.table_widget import TableWidget
from .annotation_formats import AnnotationFormatManager
from .events import EventBus
from .services import AnnotationService, ExportService, ImageService


class App(QMainWindow):
    """Main application window for GRC."""

    def __init__(self):
        super().__init__()
        self.title = "GRC - Glorified Rectangle Creator"
        self.setWindowTitle(self.title)

        # Apply modern dark theme
        self.setStyleSheet(MODERN_DARK_THEME)

        # Window geometry
        self.left = 0
        self.top = 0
        self.width = 1280
        self.height = 800
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Initialize core infrastructure
        self._init_services()

        # Legacy state (for backward compatibility with widgets)
        self.data_dir: str = ""
        self.current_image_index: int = 0
        self.image_files: List[str] = []
        self.classes: List[Tuple[int, str]] = []
        self.current_class_id: int = 0
        self.current_class_name: str = "Unknown"
        
        # Auto-save and unsaved changes tracking
        self._has_unsaved_changes: bool = False
        self._auto_save_enabled: bool = True  # Can be toggled in settings

        self.tab_panel = TableWidget(self)

        # Create widgets and store references
        self.file_list = FileListWidget()
        self.file_list.parent_app = self  # TODO: Replace with event bus
        self.tab_panel.tab1.layout.addWidget(self.file_list)

        self.class_list = ClassListWidget()
        self.class_list.parent_app = self  # Connect to app for class updates
        self.tab_panel.tab1.layout.addWidget(self.class_list)

        # Statistics widget
        self.stats_widget = StatsWidget()
        self.stats_widget.parent_app = self
        self.tab_panel.tab1.layout.addWidget(self.stats_widget)

        # Batch processing widget
        self.batch_widget = BatchWidget()
        self.batch_widget.parent_app = self
        self.batch_widget.update_formats(self.format_manager.list_formats())
        self.tab_panel.tab1.layout.addWidget(self.batch_widget)

        self.image_panel = ImageWidget(self)
        self.image_panel_controls = ImageControlsWidget()
        # Set parent app reference for signal forwarding
        self.image_panel_controls.parent_app = self

        # Build annotate workspace layout: left class list + right image area
        # Left: class selection with search
        self.class_search = QLineEdit()
        self.class_search.setPlaceholderText("🔍 Search classes…")
        self.class_search.textChanged.connect(self._filter_classes)
        # Filtering and jumping to annotations can be added here later if desired
        self.class_list_widget = QListWidget()
        self.class_list_widget.currentTextChanged.connect(self.on_class_changed)

        class_panel = QWidget()
        class_panel.setObjectName("classPanel")
        class_panel_layout = QVBoxLayout(class_panel)
        class_panel_layout.setContentsMargins(8, 8, 8, 8)
        class_panel_layout.setSpacing(8)

        class_label = QLabel("Classes")
        class_label.setObjectName("heading")
        class_panel_layout.addWidget(class_label)
        class_panel_layout.addWidget(self.class_search)
        class_panel_layout.addWidget(self.class_list_widget)

        # Right: image and controls stacked vertically
        image_panel_container = QWidget()
        image_panel_layout = QVBoxLayout(image_panel_container)
        image_panel_layout.addWidget(self.image_panel)
        image_panel_layout.addWidget(self.image_panel_controls)

        # Use a splitter so the class panel is left-docked, resizable,
        # and by default occupies roughly 10% of the available width.
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(class_panel)
        splitter.addWidget(image_panel_container)

        # Set initial sizes: ~20% for classes, 80% for image area
        splitter.setSizes([200, 800])

        # Let the right-hand side grow more aggressively
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self.tab_panel.tab2.layout.addWidget(splitter)
        # Connect file list to image panel
        self.file_list.dataView.clicked.connect(self.on_image_selected)

        # Connect navigation buttons
        self.image_panel_controls.prevButton.clicked.connect(self.previous_image)
        self.image_panel_controls.nextButton.clicked.connect(self.next_image)

        self.setCentralWidget(self.tab_panel)

        # Initialize status bar
        self._init_status_bar()

        # Initialize menus and navigation controls
        self._init_menus()
        self._update_navigation_controls()

        self.center()

        self.show()

        # Format selector will be updated when format is set

    def _init_services(self) -> None:
        """Initialize services, controllers, and event bus."""
        # Event bus for decoupled communication
        self.event_bus = EventBus()

        # Format manager
        self.format_manager = AnnotationFormatManager()

        # Services
        self.image_service = ImageService(event_bus=self.event_bus)
        self.annotation_service = AnnotationService(
            format_manager=self.format_manager,
            event_bus=self.event_bus,
        )
        self.export_service = ExportService(
            format_manager=self.format_manager,
            event_bus=self.event_bus,
        )

        # Controllers
        self.navigation_controller = NavigationController(
            image_service=self.image_service,
            event_bus=self.event_bus,
        )
        self.annotation_controller = AnnotationController(
            annotation_service=self.annotation_service,
            event_bus=self.event_bus,
        )

        # Set up controller callbacks
        self.navigation_controller.set_callbacks(
            on_image_changed=self._on_image_changed,
            on_navigation_state_changed=self._on_navigation_state_changed,
        )
        self.annotation_controller.set_callbacks(
            on_annotations_changed=self._on_annotations_changed,
            on_selection_changed=self._on_selection_changed,
        )

    def _on_image_changed(self, image_path: str, index: int, total: int) -> None:
        """Handle image change from navigation controller."""
        self.current_image_index = index - 1  # Convert to 0-based
        if self.image_panel:
            self.image_panel.load_image(image_path)
            self.load_annotations_for_image(image_path)

        # Update status bar
        filename = os.path.basename(image_path)
        self.status_bar.update_image_info(filename, index, total)

    def _on_navigation_state_changed(self, can_previous: bool, can_next: bool) -> None:
        """Handle navigation state change."""
        self._update_navigation_controls()

    def _on_annotations_changed(self, boxes: list) -> None:
        """Handle annotations change from annotation controller."""
        if hasattr(self.image_panel, "state") and self.image_panel.state:
            self.image_panel.state = self.image_panel.state._replace(bounding_boxes=boxes)
            if hasattr(self.image_panel, "thread"):
                self.image_panel.thread.render(self.image_panel.state)

    def _on_selection_changed(self, selected_boxes: list) -> None:
        """Handle selection change from annotation controller."""
        self.update_dropdown_for_selection()

    def _init_status_bar(self) -> None:
        """Create the modern status bar."""
        self.status_bar = ModernStatusBar()
        self.setStatusBar(self.status_bar)

        # Connect zoom updates from image panel
        self.image_panel.zoom_changed = self._on_zoom_changed

    def _on_zoom_changed(self, zoom_level: float) -> None:
        """Handle zoom level change."""
        self.image_panel_controls.update_zoom_display(zoom_level)
        self.status_bar.update_zoom(zoom_level)

    def _filter_classes(self, text: str) -> None:
        """Filter class list based on search text."""
        for i in range(self.class_list_widget.count()):
            item = self.class_list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _init_menus(self) -> None:
        """Create the Help menu with basic guidance."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        export_action = file_menu.addAction("Export Annotations…")
        export_action.triggered.connect(self._export_annotations)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        shortcuts_action = help_menu.addAction("Keyboard Shortcuts")
        shortcuts_action.triggered.connect(self._show_shortcuts_help)

        workflow_action = help_menu.addAction("Annotation Workflow")
        workflow_action.triggered.connect(self._show_workflow_help)

        formats_action = help_menu.addAction("Annotation Formats")
        formats_action.triggered.connect(self._show_formats_help)

    def center(self):
        """Center the application window on the screen."""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2)
        )

    def loadDataDirectory(self):
        """
        Open a directory selection dialog.

        Returns:
            str: Selected directory path
        """
        d = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not d:
            return ""

        self.data_dir = d

        # Prefer to delegate directory display to the file list widget if available
        if hasattr(self, "file_list") and hasattr(self.file_list, "loaded_directory_label"):
            self.file_list.loaded_directory_label.setText(self.data_dir)

        return self.data_dir

    def on_image_selected(self, index):
        """Handle image selection from file list."""
        model = self.file_list.dataView.model()
        if index.isValid():
            # Get the file path from the model
            path_index = model.index(index.row(), self.file_list.PATH)
            file_path = model.data(path_index)
            if file_path:
                print(f"Loading image: {file_path}")
                # Update current index and load the image
                self.current_image_index = index.row()
                self.image_panel.load_image(file_path)

                # Load annotations for this image
                self.load_annotations_for_image(file_path)

    def previous_image(self):
        """Navigate to previous image."""
        # Use navigation controller if available
        if hasattr(self, 'navigation_controller'):
            image_path = self.navigation_controller.previous()
            if image_path:
                self.current_image_index = self.image_service.current_index
                self.image_files = self.image_service.image_files
        else:
            # Fallback to legacy behavior
            if self.image_files and self.current_image_index > 0:
                self.current_image_index -= 1
                self.load_current_image()

    def next_image(self):
        """Navigate to next image."""
        # Use navigation controller if available
        if hasattr(self, 'navigation_controller'):
            image_path = self.navigation_controller.next()
            if image_path:
                self.current_image_index = self.image_service.current_index
                self.image_files = self.image_service.image_files
        else:
            # Fallback to legacy behavior
            if self.image_files and self.current_image_index < len(self.image_files) - 1:
                self.current_image_index += 1
                self.load_current_image()

    def go_to_first_image(self):
        """Navigate to the first image."""
        if self.image_files and self.current_image_index != 0:
            self.current_image_index = 0
            self.load_current_image()

    def go_to_last_image(self):
        """Navigate to the last image."""
        if self.image_files and self.current_image_index != len(self.image_files) - 1:
            self.current_image_index = len(self.image_files) - 1
            self.load_current_image()

    def load_current_image(self):
        """Load the current image based on index."""
        # Sync with image service if available
        if hasattr(self, 'image_service'):
            self.image_service.image_files = self.image_files
            image_path = self.image_service.go_to_image(self.current_image_index)
            if image_path:
                self.image_panel.load_image(image_path)
                print(f"Loading image {self.current_image_index + 1}/{len(self.image_files)}: {image_path}")

                # Update status bar
                filename = os.path.basename(image_path)
                self.status_bar.update_image_info(filename, self.current_image_index + 1, len(self.image_files))

                # Load annotations for this image
                self.load_annotations_for_image(image_path)

                # Refresh statistics when images are loaded
                self.refresh_statistics()
            else:
                print("No images available to load")
                self.status_bar.update_image_info("No image loaded", 0, 0)
        else:
            # Legacy behavior
            if self.image_files and 0 <= self.current_image_index < len(self.image_files):
                image_path = self.image_files[self.current_image_index]
                self.image_panel.load_image(image_path)
                print(f"Loading image {self.current_image_index + 1}/{len(self.image_files)}: {image_path}")

                filename = os.path.basename(image_path)
                self.status_bar.update_image_info(filename, self.current_image_index + 1, len(self.image_files))
                self.load_annotations_for_image(image_path)
                self.refresh_statistics()
            else:
                print("No images available to load")
                self.status_bar.update_image_info("No image loaded", 0, 0)

        self._update_navigation_controls()

    def load_annotations_for_image(self, image_path):
        """Load annotations for the given image using annotation service."""
        try:
            # Auto-save before loading new image if there are unsaved changes
            self._auto_save_if_needed()
            
            # Get image dimensions for format conversion
            image_width, image_height = self._get_image_dimensions(
                default_width=800, default_height=600
            )

            # Use annotation service if available
            if hasattr(self, 'annotation_service'):
                bounding_boxes = self.annotation_service.load_annotations_for_image(
                    image_path, image_width, image_height
                )
            else:
                # Fallback to direct format manager
                annotation_path = self.format_manager.get_annotation_path(
                    image_path, self.format_manager.default_format
                )
                format_handler = self.format_manager.get_format(self.format_manager.default_format)
                print(f"Loading annotations from {annotation_path} (format: {self.format_manager.default_format})")
                bounding_boxes = format_handler.load(annotation_path, image_width, image_height)

            # Clear existing bounding boxes and update with loaded ones
            if hasattr(self.image_panel, "state") and self.image_panel.state:
                from .state import make_default_state
                new_state = make_default_state()
                new_state = new_state._replace(bounding_boxes=bounding_boxes)
                self.image_panel.state = new_state

            print(f"Loaded {len(bounding_boxes)} annotations for {os.path.basename(image_path)}")
            
            # Reset unsaved changes flag after loading
            self._has_unsaved_changes = False

            # Re-render the image
            if hasattr(self.image_panel, "thread") and self.image_panel.thread:
                self.image_panel.thread.render(self.image_panel.state)

        except Exception as e:
            print(f"Error loading annotations for {image_path}: {e}")

    def save_annotations_for_current_image(self):
        """Save annotations for the current image using annotation service."""
        try:
            if not self.image_files or self.current_image_index >= len(self.image_files):
                print("No current image to save annotations for")
                return

            current_image_path = self.image_files[self.current_image_index]

            # Get image dimensions for format conversion
            image_width, image_height = self._get_image_dimensions(
                default_width=800, default_height=600
            )

            # Get current bounding boxes
            if not hasattr(self.image_panel, "state") or not self.image_panel.state:
                print("No image state available for saving")
                return

            bounding_boxes = self.image_panel.state.bounding_boxes

            # Use annotation service if available
            if hasattr(self, 'annotation_service'):
                self.annotation_service.save_annotations(
                    current_image_path, bounding_boxes, image_width, image_height, format_name="grc"
                )
            else:
                # Fallback to direct format manager
                self.format_manager.save_annotations(
                    current_image_path, bounding_boxes, image_width, image_height, format_name="grc"
                )

            # Mark as saved
            self._has_unsaved_changes = False
            print(f"Saved annotations for {os.path.basename(current_image_path)}")

        except Exception as e:
            print(f"Error saving annotations: {e}")

    def _auto_save_if_needed(self) -> bool:
        """
        Auto-save current annotations if there are unsaved changes.
        
        Returns:
            True if save was performed or not needed, False if save failed
        """
        if not self._has_unsaved_changes:
            return True
            
        if not self._auto_save_enabled:
            # Prompt user if auto-save is disabled
            return self._prompt_save_changes()
        
        # Auto-save silently
        try:
            self.save_annotations_for_current_image()
            return True
        except Exception as e:
            print(f"Auto-save failed: {e}")
            return False

    def _prompt_save_changes(self) -> bool:
        """
        Prompt user to save unsaved changes.
        
        Returns:
            True if user saved or discarded, False if cancelled
        """
        if not self._has_unsaved_changes:
            return True
            
        reply = QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved annotations. Would you like to save them?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )
        
        if reply == QMessageBox.Save:
            self.save_annotations_for_current_image()
            return True
        elif reply == QMessageBox.Discard:
            self._has_unsaved_changes = False
            return True
        else:
            return False

    def mark_unsaved_changes(self) -> None:
        """Mark that there are unsaved annotation changes."""
        self._has_unsaved_changes = True

    def reload_annotations_for_current_image(self):
        """Reload annotations for the current image."""
        try:
            if not self.image_files or self.current_image_index >= len(self.image_files):
                print("No current image to reload annotations for")
                return

            current_image_path = self.image_files[self.current_image_index]
            print(f"Reloading annotations for: {current_image_path}")

            # Force reload from current format specifically
            self.load_annotations_for_image(current_image_path)

        except Exception as e:
            print(f"Error reloading annotations: {e}")

    def _update_navigation_controls(self) -> None:
        """Enable/disable navigation buttons based on current image index."""
        if not hasattr(self, "image_panel_controls"):
            return

        has_images = bool(self.image_files)
        at_first = has_images and self.current_image_index <= 0
        at_last = has_images and self.current_image_index >= len(self.image_files) - 1

        self.image_panel_controls.prevButton.setEnabled(has_images and not at_first)
        self.image_panel_controls.nextButton.setEnabled(has_images and not at_last)

    def _get_image_dimensions(
        self, default_width: int = 800, default_height: int = 600
    ) -> Tuple[int, int]:
        """
        Safely determine the dimensions of the current image displayed in the image panel.

        Falls back to provided defaults if no image is currently loaded.
        """
        image_width = default_width
        image_height = default_height

        if hasattr(self, "image_panel") and hasattr(self.image_panel, "thread"):
            base_image = getattr(self.image_panel.thread, "base_image", None)
            if base_image is not None and not base_image.isNull():
                image_width = base_image.width()
                image_height = base_image.height()

        return image_width, image_height

    def set_annotation_format(self, format_name):
        """Set the annotation format and handle annotation loading with user confirmation."""
        old_format = self.format_manager.default_format

        # If format hasn't changed, do nothing
        if old_format == format_name:
            return

        self.format_manager.set_default_format(format_name)

        # If we have a current image, handle format switching
        if self.image_files and self.current_image_index < len(self.image_files):
            current_image_path = self.image_files[self.current_image_index]
            print(f"Switching format from {old_format} to {format_name}")

            # Check if there are current annotations in memory
            current_boxes = (
                self.image_panel.state.bounding_boxes if hasattr(self.image_panel, "state") else []
            )

            # Check if annotation file exists in new format
            new_format_path = self.format_manager.get_annotation_path(
                current_image_path, format_name
            )
            new_format_exists = os.path.exists(new_format_path)

            if current_boxes and new_format_exists:
                # Both current annotations and new format file exist - ask user what to do
                reply = QMessageBox.question(
                    self,
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
                    # Revert format change
                    self.format_manager.set_default_format(old_format)
                    # Update UI to reflect reverted format
                    if hasattr(self, "image_panel_controls") and hasattr(
                        self.image_panel_controls, "formatSelect"
                    ):
                        self.image_panel_controls.formatSelect.blockSignals(True)
                        self.image_panel_controls.formatSelect.setCurrentText(old_format.upper())
                        self.image_panel_controls.formatSelect.blockSignals(False)
                    print(f"Format change cancelled, staying with {old_format}")
                    return
                elif reply == QMessageBox.Yes:
                    # Load from new format file
                    print(f"Loading annotations from {format_name} file")
                    self.load_annotations_for_image(current_image_path)
                else:  # QMessageBox.No - Keep current annotations
                    # Ask if they want to merge with file annotations
                    merge_reply = QMessageBox.question(
                        self,
                        "Merge Annotations?",
                        f"Would you like to also load and merge the annotations from the {format_name.upper()} file?\n\n"
                        f"This will add {len(current_boxes)} current annotations + annotations from file.",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes,
                    )

                    if merge_reply == QMessageBox.Yes:
                        # Load annotations from new format file for merging
                        print(f"Loading and merging annotations from {format_name} file")

                        # Get image dimensions for format conversion
                        image_width, image_height = self._get_image_dimensions(
                            default_width=800, default_height=600
                        )

                        # Load annotations from the new format file
                        format_handler = self.format_manager.get_format(format_name)
                        file_annotations = format_handler.load(
                            new_format_path, image_width, image_height
                        )

                        if file_annotations:
                            # Merge file annotations with current annotations
                            merged_boxes = current_boxes + file_annotations
                            self.image_panel.state = self.image_panel.state._replace(
                                bounding_boxes=merged_boxes
                            )
                            self.image_panel.thread.render(self.image_panel.state)
                            print(
                                f"Merged {len(file_annotations)} file annotations with {len(current_boxes)} current annotations = {len(merged_boxes)} total"
                            )
                        else:
                            print("No annotations loaded from file for merging")
                    else:
                        # Just keep current annotations
                        print(f"Keeping current annotations, format switched to {format_name}")

            elif current_boxes and not new_format_exists:
                # Current annotations exist but no file in new format - ask if they want to keep them
                reply = QMessageBox.question(
                    self,
                    "Format Switch",
                    f"You have {len(current_boxes)} annotation(s) in memory.\n\n"
                    f"No annotation file exists in {format_name.upper()} format.\n\n"
                    f"Keep current annotations?\n\n"
                    f"• Yes: Keep annotations (can save to {format_name.upper()} later)\n"
                    f"• No: Clear annotations",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )

                if reply == QMessageBox.No:
                    # Clear annotations
                    self.image_panel.state = self.image_panel.state._replace(bounding_boxes=[])
                    self.image_panel.thread.render(self.image_panel.state)
                    print("Annotations cleared")
                else:
                    print(f"Keeping current annotations, format switched to {format_name}")

            elif not current_boxes and new_format_exists:
                # No current annotations but file exists in new format - just load it
                print(f"Loading annotations from {format_name} file")
                self.load_annotations_for_image(current_image_path)
            else:
                # No current annotations and no file in new format - nothing to do
                print(f"Format switched to {format_name}, no annotations to load")

    def get_current_class(self) -> Tuple[int, str]:
        """Return the currently active (class_id, class_name) for new annotations."""
        return self.current_class_id, self.current_class_name

    def _show_shortcuts_help(self) -> None:
        """Show a dialog describing useful keyboard shortcuts."""
        message = (
            "Keyboard shortcuts:\n\n"
            "Navigation:\n"
            "  ← / A : Previous image\n"
            "  → / D : Next image\n\n"
            "Annotations:\n"
            "  Delete : Delete selected boxes\n"
            "  Ctrl+Z : Undo last annotation change\n"
            "  Ctrl+Y : Redo last undone change\n\n"
            "Saving:\n"
            "  S      : Save annotations for current image\n"
            "  R      : Reload annotations from disk\n\n"
            "Zoom & Pan:\n"
            "  + / =  : Zoom in\n"
            "  - / _  : Zoom out\n"
            "  0      : Reset zoom\n"
            "  Ctrl+Scroll : Zoom in/out\n"
            "  Middle-click drag : Pan image"
        )
        QMessageBox.information(self, "Keyboard Shortcuts", message)

    def _show_workflow_help(self) -> None:
        """Show a dialog explaining the typical annotation workflow."""
        message = (
            "Typical annotation workflow:\n\n"
            "1. Configure tab:\n"
            "   • Use 'Open Folder…' to select the image directory.\n"
            "   • Use 'Open Classes File…' to load your class definitions.\n\n"
            "2. Annotate tab:\n"
            "   • Use the mouse to drag rectangles over objects of interest.\n"
            "   • Use the class dropdown to choose the active class.\n"
            "   • Use Previous/Next or the arrow keys to move between images.\n\n"
            "3. Save:\n"
            "   • Choose an annotation format (GRC / YOLO / COCO).\n"
            "   • Click 'Save' (or press S) to write annotations to disk."
        )
        QMessageBox.information(self, "Annotation Workflow", message)

    def _show_formats_help(self) -> None:
        """Show a dialog describing supported annotation formats."""
        message = (
            "Supported annotation formats:\n\n"
            "• GRC (.json):\n"
            "  - Native format used internally for saving annotations.\n"
            "  - Stores image size and a list of bounding boxes with class_id and class_name.\n\n"
            "• YOLO (.txt):\n"
            "  - One line per box: class_id x_center y_center width height [class_name].\n"
            "  - Coordinates are normalized (0–1) relative to image width/height.\n\n"
            "• COCO (.json):\n"
            "  - Standard COCO-style JSON with categories and annotations.\n"
            "  - Bounding boxes are stored as [x, y, width, height] in pixels."
        )
        QMessageBox.information(self, "Annotation Formats", message)

    def _export_annotations(self) -> None:
        """Export annotations from the internal format to another format."""
        from PyQt5.QtWidgets import QInputDialog

        available_formats = [name for name in self.format_manager.list_formats() if name != "grc"]
        if not available_formats:
            QMessageBox.information(self, "Export Annotations", "No export formats are available.")
            return

        items = [name.upper() for name in available_formats]
        selected_text, ok = QInputDialog.getItem(
            self,
            "Export Annotations",
            "Choose export format:",
            items,
            0,
            False,
        )
        if not ok or not selected_text:
            return

        # Map text back to format key
        selected_index = items.index(selected_text)
        target_format = available_formats[selected_index]

        if not self.image_files:
            QMessageBox.information(
                self, "Export Annotations", "No images are loaded to export annotations for."
            )
            return

        exported_count = 0
        for image_path in self.image_files:
            if not os.path.exists(image_path):
                continue

            # Determine image dimensions
            image = QImage(image_path)
            if image.isNull():
                continue
            width = image.width()
            height = image.height()

            # Load annotations from the internal GRC format
            boxes = self.format_manager.load_annotations(
                image_path, width, height, preferred_format="grc"
            )
            if not boxes:
                continue

            # Save in the selected export format
            self.format_manager.save_annotations(
                image_path, boxes, width, height, format_name=target_format
            )
            exported_count += 1

        QMessageBox.information(
            self,
            "Export Annotations",
            f"Exported annotations for {exported_count} image(s) to {target_format.upper()} format.",
        )

    def refresh_statistics(self):
        """Refresh annotation statistics for the stats widget."""
        if not self.image_files:
            self.stats_widget.clear_stats()
            return

        def get_annotations_for_image(image_path):
            """Helper to get annotations for an image."""
            try:
                image = QImage(image_path)
                if image.isNull():
                    return []
                width, height = image.width(), image.height()
                return self.format_manager.load_annotations(
                    image_path, width, height, preferred_format="grc"
                )
            except Exception:
                return []

        self.stats_widget.update_stats(
            self.image_files,
            None,  # annotations_dir not needed with get_annotations_func
            get_annotations_for_image,
            self.classes,
        )

    def update_classes(self, classes):
        """Update the class dropdown with loaded classes."""
        try:
            if not classes:
                print("Warning: No classes provided to update_classes")
                return

            self.classes = classes
            # Default to the first class when classes are loaded
            self.current_class_id, self.current_class_name = self.classes[0]

            # Populate the class list widget on the annotate tab
            if hasattr(self, "class_list_widget"):
                self.class_list_widget.clear()
                for class_id, class_name in classes:
                    self.class_list_widget.addItem(f"{class_id}: {class_name}")
                print(f"Updated class list with {len(classes)} classes")

        except Exception as e:
            print(f"Error in update_classes: {e}")

    def on_class_changed(self, class_name):
        """Handle class selection change."""
        print(f"Class changed to: '{class_name}'")

        # Validate class_name parameter
        if not class_name or not isinstance(class_name, str):
            print("Invalid class name provided")
            return

        # Parse class information with error handling
        try:
            if ":" in class_name:
                # Full format: "8: traffic_light"
                class_parts = class_name.split(":", 1)
                if len(class_parts) >= 1:
                    class_id = int(class_parts[0])
                    new_class_name = class_parts[1].strip() if len(class_parts) > 1 else ""
                else:
                    class_id = 0
                    new_class_name = class_name
            else:
                # Just the ID: "8" - look up the name from self.classes
                try:
                    class_id = int(class_name)
                    new_class_name = ""
                    # Find the class name in self.classes
                    if hasattr(self, "classes") and self.classes:
                        for cid, cname in self.classes:
                            if cid == class_id:
                                new_class_name = cname
                                break
                        if not new_class_name:
                            print(f"Warning: No class name found for ID {class_id}")
                            new_class_name = f"Class_{class_id}"
                    else:
                        print("No classes loaded")
                        new_class_name = f"Class_{class_id}"
                except ValueError:
                    print(f"Invalid class ID: {class_name}")
                    return

            # Validate parsed values
            if not new_class_name:
                new_class_name = "Unknown"

        except (ValueError, IndexError) as e:
            print(f"Error parsing class name '{class_name}': {e}")
            return

        print(f"Parsed class: id={class_id}, name='{new_class_name}'")

        # Update the current active class for new annotations
        self.current_class_id = class_id
        self.current_class_name = new_class_name

        # Get selected bounding boxes (if any)
        if not hasattr(self, "image_panel") or not self.image_panel:
            print("Image panel not available")
            return

        if not hasattr(self.image_panel, "state") or not self.image_panel.state:
            print("Image state not available")
            return

        selected_boxes = [box for box in self.image_panel.state.bounding_boxes if box.selected]

        if not selected_boxes:
            # It's fine to change the current class even if no boxes are selected
            print("No annotations selected; updated active class only")
            return

        # Check if multiple boxes are selected
        if len(selected_boxes) > 1:
            # Show confirmation dialog for bulk change
            try:
                from PyQt5.QtWidgets import QMessageBox

                reply = QMessageBox.question(
                    self,
                    "Confirm Class Change",
                    f'Change class of {len(selected_boxes)} selected annotations to "{new_class_name}"?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if reply != QMessageBox.Yes:
                    return
            except Exception as e:
                print(f"Error showing confirmation dialog: {e}")
                return

        # Update selected boxes
        try:
            # Snapshot state for undo support
            if hasattr(self, "image_panel") and hasattr(self.image_panel, "_push_undo_state"):
                self.image_panel._push_undo_state()

            for box in selected_boxes:
                if hasattr(box, "class_id") and hasattr(box, "class_name"):
                    print(
                        f"Updating box: old class_id={box.class_id}, old class_name='{box.class_name}'"
                    )
                    box.class_id = class_id
                    box.class_name = new_class_name
                    print(
                        f"Updated box: new class_id={box.class_id}, new class_name='{box.class_name}'"
                    )
                else:
                    print(f"Warning: Bounding box missing class attributes: {box}")
        except Exception as e:
            print(f"Error updating bounding boxes: {e}")
            return

        # Re-render the image with error handling
        try:
            if hasattr(self.image_panel, "thread") and self.image_panel.thread:
                self.image_panel.thread.render(self.image_panel.state)
                print(f"Updated {len(selected_boxes)} annotation(s) to class: {new_class_name}")
            else:
                print("Render thread not available")
        except Exception as e:
            print(f"Error rendering image: {e}")
            return

        # Don't call update_dropdown_for_selection here - it will override the user's selection
        # The dropdown should remain on the class the user just selected

    def update_dropdown_for_selection(self):
        """Update class list widget selection based on current annotation selection."""
        try:
            # Check if required components exist
            if not hasattr(self, "image_panel") or not self.image_panel:
                return

            if not hasattr(self.image_panel, "state") or not self.image_panel.state:
                return

            if not hasattr(self, "class_list_widget") or not self.class_list_widget:
                return

            selected_boxes = [box for box in self.image_panel.state.bounding_boxes if box.selected]

            if not selected_boxes:
                # No selection, reset to first class
                if hasattr(self, "classes") and self.classes:
                    self.class_list_widget.setCurrentRow(0)
            elif len(selected_boxes) == 1:
                # Single selection, show that class
                if hasattr(self, "classes") and self.classes:
                    box = selected_boxes[0]
                    for i, (class_id, class_name) in enumerate(self.classes):
                        if class_id == box.class_id and class_name == box.class_name:
                            self.class_list_widget.setCurrentRow(i)
                            break
            else:
                # Multiple selections, check if all same class
                if hasattr(self, "classes") and self.classes:
                    first_box = selected_boxes[0]
                    all_same_class = all(
                        box.class_id == first_box.class_id
                        and box.class_name == first_box.class_name
                        for box in selected_boxes
                    )

                    if all_same_class:
                        # All same class, show that class
                        for i, (class_id, class_name) in enumerate(self.classes):
                            if (
                                class_id == first_box.class_id
                                and class_name == first_box.class_name
                            ):
                                self.class_list_widget.setCurrentRow(i)
                                break
                    # If mixed classes, leave selection as-is

        except Exception as e:
            print(f"Error in update_dropdown_for_selection: {e}")

    def closeEvent(self, event):
        """Handle application close - check for unsaved changes and clean up."""
        # Check for unsaved changes
        if self._has_unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved annotations. Would you like to save them before closing?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )
            
            if reply == QMessageBox.Save:
                self.save_annotations_for_current_image()
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
            # Discard: continue with close
        
        # Clean up render thread to prevent crash
        if hasattr(self, "image_panel") and self.image_panel:
            self.image_panel.cleanup()
        event.accept()
