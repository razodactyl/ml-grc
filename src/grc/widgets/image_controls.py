from PyQt5.QtWidgets import QWidget, QHBoxLayout, QGroupBox, QPushButton, QComboBox, QSizePolicy


class ImageControlsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.classes = []

        self.init_ui()

    def init_ui(self):
        self.prevButton = QPushButton("Previous")
        self.nextButton = QPushButton("Next")

        self.classSelect = QComboBox(self)
        self.classSelect.addItem("Test")
        self.classSelect.activated[str].connect(self.combo_changed)

        self.prevButton.clicked.connect(self.clicked_prev)
        self.nextButton.clicked.connect(self.clicked_next)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        hbox = QHBoxLayout()
        hbox.addWidget(self.prevButton)
        hbox.addWidget(self.nextButton)
        hbox.addWidget(self.classSelect)

        self.setLayout(hbox)

    def clicked_prev(self):
        print("Clicked prev button.")

    def clicked_next(self):
        print("Clicked next button.")

    def combo_changed(self, text):
        print(text)
