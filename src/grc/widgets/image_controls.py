from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGroupBox, QPushButton, QComboBox, QSizePolicy


class ImageControlsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.classes = []

        self.init_ui()

    def init_ui(self):
        self.prevButton = QPushButton("Previous")
        self.nextButton = QPushButton("Next")

        self.saveButton = QPushButton("Save")
        self.reloadButton = QPushButton("Reload")

        self.formatSelect = QComboBox(self)
        self.formatSelect.addItem("GRC (.json)", "grc")
        self.formatSelect.addItem("YOLO (.txt)", "yolo")
        self.formatSelect.addItem("COCO (.json)", "coco")
        self.formatSelect.setCurrentIndex(0)  # Default to GRC format
        self.formatSelect.activated[str].connect(self.format_changed)

        self.classSelect = QComboBox(self)
        self.classSelect.addItem("Test")
        self.classSelect.activated[str].connect(self.class_changed)

        self.prevButton.clicked.connect(self.clicked_prev)
        self.nextButton.clicked.connect(self.clicked_next)
        self.saveButton.clicked.connect(self.clicked_save)
        self.reloadButton.clicked.connect(self.clicked_reload)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        hbox = QHBoxLayout()
        hbox.addWidget(self.prevButton)
        hbox.addWidget(self.nextButton)
        hbox.addWidget(self.saveButton)
        hbox.addWidget(self.reloadButton)
        hbox.addWidget(self.formatSelect)
        hbox.addWidget(self.classSelect)

        self.setLayout(hbox)

    def clicked_prev(self):
        print("Clicked prev button.")

    def clicked_next(self):
        print("Clicked next button.")

    def clicked_save(self):
        print("Clicked save button.")
        if hasattr(self, 'parent_app') and self.parent_app:
            self.parent_app.save_annotations_for_current_image()

    def clicked_reload(self):
        print("Clicked reload button.")
        if hasattr(self, 'parent_app') and self.parent_app:
            self.parent_app.reload_annotations_for_current_image()

    def format_changed(self, text):
        """Handle format selection change."""
        format_name = self.formatSelect.currentData()
        print(f"Format changed to: {format_name}")
        if hasattr(self, 'parent_app') and self.parent_app:
            self.parent_app.set_annotation_format(format_name)
        else:
            print("No parent app available for format change")

    def class_changed(self, text):
        """Handle class selection change."""
        print(f"Class selection changed to: {text}")
        # Forward the class change to the parent app
        if hasattr(self, 'parent_app') and self.parent_app:
            self.parent_app.on_class_changed(text)
        else:
            print("No parent app available for class change")
