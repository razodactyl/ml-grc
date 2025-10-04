"""
Main application class for GRC.
"""

import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QTabWidget, QDesktopWidget
from PyQt5.QtCore import Qt

from ..widgets.table_widget import TableWidget
from ..widgets.file_list_widget import FileListWidget
from ..widgets.class_list_widget import ClassListWidget
from ..widgets.image_widget import ImageWidget
from ..widgets.image_controls import ImageControlsWidget
from .annotation_formats import AnnotationFormatManager
from .bounding_box import BoundingBox


class App(QMainWindow):
    """Main application window for GRC."""
    
    def __init__(self):
        super().__init__()
        self.title = "Glorified Rectangle Creator"
        self.setWindowTitle(self.title)

        self.data_dir = ""
        self.current_image_index = 0
        self.left = 0
        self.top = 0
        self.width = 1024
        self.height = 768
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Initialize annotation format manager
        self.format_manager = AnnotationFormatManager()

        self.tab_panel = TableWidget(self)

        # Create widgets and store references
        self.file_list = FileListWidget()
        self.file_list.parent_app = self  # Connect to app for image list updates
        self.tab_panel.tab1.layout.addWidget(self.file_list)

        self.class_list = ClassListWidget()
        self.class_list.parent_app = self  # Connect to app for class updates
        self.tab_panel.tab1.layout.addWidget(self.class_list)

        self.image_panel = ImageWidget(self)
        self.image_panel_controls = ImageControlsWidget()
        # Set parent app reference for signal forwarding
        self.image_panel_controls.parent_app = self
        self.tab_panel.tab2.layout.addWidget(self.image_panel)
        self.tab_panel.tab2.layout.addWidget(self.image_panel_controls)
        # Connect file list to image panel
        self.file_list.dataView.clicked.connect(self.on_image_selected)
        
        # Connect navigation buttons
        self.image_panel_controls.prevButton.clicked.connect(self.previous_image)
        self.image_panel_controls.nextButton.clicked.connect(self.next_image)

        self.setCentralWidget(self.tab_panel)

        self.center()

        self.show()

        # Format selector will be updated when format is set

    def center(self):
        """Center the application window on the screen."""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width()-size.width())/2), int((screen.height()-size.height())/2))

    def loadDataDirectory(self):
        """
        Open a directory selection dialog.
        
        Returns:
            str: Selected directory path
        """
        d = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.data_dir = d
        self.loaded_directory_label.setText(self.data_dir)
        return d

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
        if self.image_files and self.current_image_index > 0:
            self.current_image_index -= 1
            self.load_current_image()

    def next_image(self):
        """Navigate to next image."""
        if self.image_files and self.current_image_index < len(self.image_files) - 1:
            self.current_image_index += 1
            self.load_current_image()

    def load_current_image(self):
        """Load the current image based on index."""
        if self.image_files and 0 <= self.current_image_index < len(self.image_files):
            image_path = self.image_files[self.current_image_index]
            self.image_panel.load_image(image_path)
            print(f"Loading image {self.current_image_index + 1}/{len(self.image_files)}: {image_path}")

            # Load annotations for this image
            self.load_annotations_for_image(image_path)

    def load_annotations_for_image(self, image_path):
        """Load annotations for the given image using format manager."""
        try:
            # Get image dimensions for format conversion
            image_width = 800  # Default width, should be updated when image loads
            image_height = 600  # Default height, should be updated when image loads

            # Check if image panel has the actual dimensions
            if hasattr(self.image_panel, 'thread') and self.image_panel.thread.base_image:
                if not self.image_panel.thread.base_image.isNull():
                    image_width = self.image_panel.thread.base_image.width()
                    image_height = self.image_panel.thread.base_image.height()

            # Use format manager to load annotations from current format
            annotation_path = self.format_manager.get_annotation_path(image_path, self.format_manager.default_format)
            format_handler = self.format_manager.get_format(self.format_manager.default_format)
            
            print(f"Loading annotations from {annotation_path} (format: {self.format_manager.default_format})")
            bounding_boxes = format_handler.load(annotation_path, image_width, image_height)

            # Clear existing bounding boxes and update with loaded ones
            if hasattr(self.image_panel, 'state') and self.image_panel.state:
                # Create new state with empty bounding boxes
                from .state import make_default_state
                new_state = make_default_state()
                # Copy over any existing properties but set loaded bounding boxes
                new_state = new_state._replace(bounding_boxes=bounding_boxes)
                self.image_panel.state = new_state

            print(f"Loaded {len(bounding_boxes)} annotations for {os.path.basename(image_path)}")

            # Re-render the image
            if hasattr(self.image_panel, 'thread') and self.image_panel.thread:
                self.image_panel.thread.render(self.image_panel.state)

        except Exception as e:
            print(f"Error loading annotations for {image_path}: {e}")

    def save_annotations_for_current_image(self):
        """Save annotations for the current image using format manager."""
        try:
            if not self.image_files or self.current_image_index >= len(self.image_files):
                print("No current image to save annotations for")
                return

            current_image_path = self.image_files[self.current_image_index]

            # Get image dimensions for format conversion
            image_width = 800  # Default width
            image_height = 600  # Default height

            # Check if image panel has the actual dimensions
            if hasattr(self.image_panel, 'thread') and self.image_panel.thread.base_image:
                if not self.image_panel.thread.base_image.isNull():
                    image_width = self.image_panel.thread.base_image.width()
                    image_height = self.image_panel.thread.base_image.height()

            # Get current bounding boxes
            if not hasattr(self.image_panel, 'state') or not self.image_panel.state:
                print("No image state available for saving")
                return

            bounding_boxes = self.image_panel.state.bounding_boxes

            # Use format manager to save annotations
            self.format_manager.save_annotations(
                current_image_path, bounding_boxes, image_width, image_height
            )

        except Exception as e:
            print(f"Error saving annotations: {e}")

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

    def set_annotation_format(self, format_name):
        """Set the annotation format and handle annotation loading with user confirmation."""
        from PyQt5.QtWidgets import QMessageBox
        
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
            current_boxes = self.image_panel.state.bounding_boxes if hasattr(self.image_panel, 'state') else []
            
            # Check if annotation file exists in new format
            new_format_path = self.format_manager.get_annotation_path(current_image_path, format_name)
            new_format_exists = os.path.exists(new_format_path)
            
            if current_boxes and new_format_exists:
                # Both current annotations and new format file exist - ask user what to do
                reply = QMessageBox.question(
                    self,
                    'Format Switch',
                    f'You have {len(current_boxes)} annotation(s) in memory.\n\n'
                    f'An annotation file exists in {format_name.upper()} format.\n\n'
                    f'What would you like to do?\n\n'
                    f'• Yes: Load annotations from {format_name.upper()} file (discard current)\n'
                    f'• No: Keep current annotations (can save to {format_name.upper()} later)\n'
                    f'• Cancel: Revert to {old_format.upper()} format',
                    QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Cancel:
                    # Revert format change
                    self.format_manager.set_default_format(old_format)
                    # Update UI to reflect reverted format
                    if hasattr(self, 'image_panel_controls') and hasattr(self.image_panel_controls, 'formatSelect'):
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
                        'Merge Annotations?',
                        f'Would you like to also load and merge the annotations from the {format_name.upper()} file?\n\n'
                        f'This will add {len(current_boxes)} current annotations + annotations from file.',
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )
                    
                    if merge_reply == QMessageBox.Yes:
                        # Load annotations from new format file for merging
                        print(f"Loading and merging annotations from {format_name} file")
                        
                        # Get image dimensions for format conversion
                        image_width = 800  # Default width
                        image_height = 600  # Default height

                        # Check if image panel has the actual dimensions
                        if hasattr(self.image_panel, 'thread') and self.image_panel.thread.base_image:
                            if not self.image_panel.thread.base_image.isNull():
                                image_width = self.image_panel.thread.base_image.width()
                                image_height = self.image_panel.thread.base_image.height()

                        # Load annotations from the new format file
                        format_handler = self.format_manager.get_format(format_name)
                        file_annotations = format_handler.load(new_format_path, image_width, image_height)
                        
                        if file_annotations:
                            # Merge file annotations with current annotations
                            merged_boxes = current_boxes + file_annotations
                            self.image_panel.state = self.image_panel.state._replace(bounding_boxes=merged_boxes)
                            self.image_panel.thread.render(self.image_panel.state)
                            print(f"Merged {len(file_annotations)} file annotations with {len(current_boxes)} current annotations = {len(merged_boxes)} total")
                        else:
                            print("No annotations loaded from file for merging")
                    else:
                        # Just keep current annotations
                        print(f"Keeping current annotations, format switched to {format_name}")
                    
            elif current_boxes and not new_format_exists:
                # Current annotations exist but no file in new format - ask if they want to keep them
                reply = QMessageBox.question(
                    self,
                    'Format Switch',
                    f'You have {len(current_boxes)} annotation(s) in memory.\n\n'
                    f'No annotation file exists in {format_name.upper()} format.\n\n'
                    f'Keep current annotations?\n\n'
                    f'• Yes: Keep annotations (can save to {format_name.upper()} later)\n'
                    f'• No: Clear annotations',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
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
    def update_classes(self, classes):
        """Update the class dropdown with loaded classes."""
        try:
            if not classes:
                print("Warning: No classes provided to update_classes")
                return

            self.classes = classes

            if not hasattr(self, 'image_panel_controls') or not self.image_panel_controls:
                print("Image panel controls not available for class update")
                return

            if not hasattr(self.image_panel_controls, 'classSelect'):
                print("Class select dropdown not available for class update")
                return

            try:
                self.image_panel_controls.classSelect.clear()
                for class_id, class_name in classes:
                    self.image_panel_controls.classSelect.addItem(f"{class_id}: {class_name}")
                print(f"Updated class dropdown with {len(classes)} classes")
            except Exception as e:
                print(f"Error updating class dropdown: {e}")

        except Exception as e:
            print(f"Error in update_classes: {e}")

    def on_class_changed(self, class_name):
        """Handle class selection change."""
        print(f"Class changed to: '{class_name}'")

        # Validate class_name parameter
        if not class_name or not isinstance(class_name, str):
            print("Invalid class name provided")
            return

        # Get selected bounding boxes
        if not hasattr(self, 'image_panel') or not self.image_panel:
            print("Image panel not available")
            return

        if not hasattr(self.image_panel, 'state') or not self.image_panel.state:
            print("Image state not available")
            return

        selected_boxes = [box for box in self.image_panel.state.bounding_boxes if box.selected]

        if not selected_boxes:
            print("No annotations selected")
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
                    if hasattr(self, 'classes') and self.classes:
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

        # Check if multiple boxes are selected
        if len(selected_boxes) > 1:
            # Show confirmation dialog for bulk change
            try:
                from PyQt5.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    'Confirm Class Change',
                    f'Change class of {len(selected_boxes)} selected annotations to "{new_class_name}"?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply != QMessageBox.Yes:
                    return
            except Exception as e:
                print(f"Error showing confirmation dialog: {e}")
                return

        # Update selected boxes
        try:
            for box in selected_boxes:
                if hasattr(box, 'class_id') and hasattr(box, 'class_name'):
                    print(f"Updating box: old class_id={box.class_id}, old class_name='{box.class_name}'")
                    box.class_id = class_id
                    box.class_name = new_class_name
                    print(f"Updated box: new class_id={box.class_id}, new class_name='{box.class_name}'")
                else:
                    print(f"Warning: Bounding box missing class attributes: {box}")
        except Exception as e:
            print(f"Error updating bounding boxes: {e}")
            return

        # Re-render the image with error handling
        try:
            if hasattr(self.image_panel, 'thread') and self.image_panel.thread:
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
        """Update dropdown based on current selection."""
        try:
            # Check if required components exist
            if not hasattr(self, 'image_panel') or not self.image_panel:
                print("Image panel not available for dropdown update")
                return

            if not hasattr(self.image_panel, 'state') or not self.image_panel.state:
                print("Image state not available for dropdown update")
                return

            if not hasattr(self, 'image_panel_controls') or not self.image_panel_controls:
                print("Image panel controls not available for dropdown update")
                return

            if not hasattr(self.image_panel_controls, 'classSelect'):
                print("Class select dropdown not available")
                return

            selected_boxes = [box for box in self.image_panel.state.bounding_boxes if box.selected]
            print(f"update_dropdown_for_selection: {len(selected_boxes)} boxes selected")

            if not selected_boxes:
                # No selection, reset to first class
                if hasattr(self, 'classes') and self.classes:
                    try:
                        print(f"Resetting to first class: {self.classes[0]}")
                        self.image_panel_controls.classSelect.setCurrentIndex(0)
                    except Exception as e:
                        print(f"Error resetting dropdown index: {e}")
            elif len(selected_boxes) == 1:
                # Single selection, show that class
                if hasattr(self, 'classes') and self.classes:
                    try:
                        box = selected_boxes[0]
                        print(f"Single selection - box class: id={box.class_id}, name='{box.class_name}'")
                        print(f"Available classes: {self.classes}")

                        for i, (class_id, class_name) in enumerate(self.classes):
                            print(f"Comparing with class {i}: id={class_id}, name='{class_name}'")
                            if class_id == box.class_id and class_name == box.class_name:
                                print(f"Found match at index {i}")
                                self.image_panel_controls.classSelect.setCurrentIndex(i)
                                break
                        else:
                            print("No matching class found in self.classes!")
                    except Exception as e:
                        print(f"Error updating single selection dropdown: {e}")
            else:
                # Multiple selections, check if all same class
                if hasattr(self, 'classes') and self.classes:
                    try:
                        first_box = selected_boxes[0]
                        all_same_class = all(box.class_id == first_box.class_id and
                                           box.class_name == first_box.class_name
                                           for box in selected_boxes)

                        if all_same_class:
                            # All same class, show that class
                            for i, (class_id, class_name) in enumerate(self.classes):
                                if class_id == first_box.class_id and class_name == first_box.class_name:
                                    self.image_panel_controls.classSelect.setCurrentIndex(i)
                                    break
                        else:
                            # Mixed classes, show "- Multiple Selected -"
                            try:
                                self.image_panel_controls.classSelect.setCurrentText("- Multiple Selected -")
                            except Exception as e:
                                print(f"Error setting multiple selection text: {e}")
                    except Exception as e:
                        print(f"Error handling multiple selection dropdown: {e}")

        except Exception as e:
            print(f"Error in update_dropdown_for_selection: {e}")

    def openFileNamesDialog(self):
        """Open a file selection dialog (currently unused)."""
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        files = QFileDialog.getExistingDirectory(self, "Select Directory")
        # files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
        #                                         "All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)
