"""
Main application class for GRC.
"""

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDesktopWidget

from ..widgets.table_widget import TableWidget
from ..widgets.image_widget import ImageWidget
from ..widgets.image_controls import ImageControlsWidget
from ..widgets.file_list_widget import FileListWidget
from ..widgets.class_list_widget import ClassListWidget


class App(QMainWindow):
    """Main application window for GRC."""
    
    def __init__(self):
        super().__init__()

        self.title = "Glorified Rectangle Creator"
        self.setWindowTitle(self.title)

        self.data_dir = ""
        self.current_image_index = 0
        self.image_files = []

        self.left = 0
        self.top = 0
        self.width = 1024
        self.height = 768
        self.setGeometry(self.left, self.top, self.width, self.height)

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
        self.tab_panel.tab2.layout.addWidget(self.image_panel)
        self.tab_panel.tab2.layout.addWidget(self.image_panel_controls)
        
        # Connect file list to image panel
        self.file_list.dataView.clicked.connect(self.on_image_selected)
        
        # Connect navigation buttons
        self.image_panel_controls.prevButton.clicked.connect(self.previous_image)
        self.image_panel_controls.nextButton.clicked.connect(self.next_image)
        
        # Connect class selection
        self.image_panel_controls.classSelect.activated.connect(self.on_class_changed)

        self.setCentralWidget(self.tab_panel)

        self.center()

        self.show()

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

    def update_classes(self, classes):
        """Update the class dropdown with loaded classes."""
        self.classes = classes
        self.image_panel_controls.classSelect.clear()
        for class_id, class_name in classes:
            self.image_panel_controls.classSelect.addItem(f"{class_id}: {class_name}")

    def on_class_changed(self, class_name):
        """Handle class selection change."""
        print(f"Class changed to: {class_name}")
        
        # Get selected bounding boxes
        selected_boxes = [box for box in self.image_panel.state.bounding_boxes if box.selected]
        
        if not selected_boxes:
            print("No annotations selected")
            return
            
        # Parse class information
        if ":" in class_name:
            class_id = int(class_name.split(":")[0])
            new_class_name = class_name.split(":", 1)[1].strip()
        else:
            class_id = 0
            new_class_name = class_name
            
        # Check if multiple boxes are selected
        if len(selected_boxes) > 1:
            # Show confirmation dialog for bulk change
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
        
        # Update selected boxes
        for box in selected_boxes:
            box.class_id = class_id
            box.class_name = new_class_name
            
        # Re-render the image
        self.image_panel.thread.render(self.image_panel.state)
        print(f"Updated {len(selected_boxes)} annotation(s) to class: {new_class_name}")
        
        # Update dropdown to reflect the change
        self.update_dropdown_for_selection()

    def update_dropdown_for_selection(self):
        """Update dropdown based on current selection."""
        selected_boxes = [box for box in self.image_panel.state.bounding_boxes if box.selected]
        
        if not selected_boxes:
            # No selection, reset to first class
            if self.classes:
                self.image_panel_controls.classSelect.setCurrentIndex(0)
        elif len(selected_boxes) == 1:
            # Single selection, show that class
            box = selected_boxes[0]
            for i, (class_id, class_name) in enumerate(self.classes):
                if class_id == box.class_id and class_name == box.class_name:
                    self.image_panel_controls.classSelect.setCurrentIndex(i)
                    break
        else:
            # Multiple selections, check if all same class
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
                self.image_panel_controls.classSelect.setCurrentText("- Multiple Selected -")

    def openFileNamesDialog(self):
        """Open a file selection dialog (currently unused)."""
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        files = QFileDialog.getExistingDirectory(self, "Select Directory")
        # files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
        #                                         "All Files (*);;Python Files (*.py)", options=options)
        if files:
            print(files)
