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

        self.classSelect = QComboBox(self)
        self.classSelect.addItem("Test")
        self.classSelect.activated[str].connect(self.combo_changed)

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

    def combo_changed(self, text):
        print(f"Class selection changed to: {text}")
        # Forward the class change to the parent app
        if hasattr(self, 'parent_app') and self.parent_app:
            self.parent_app.on_class_changed(text)
        else:
            print("No parent app available for class change")
