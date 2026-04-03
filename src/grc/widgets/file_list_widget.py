import glob
import os

# https://pythonspot.com/pyqt5-treeview/
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QToolButton,
    QTreeView,
    QVBoxLayout,
)


class FileListWidget(QGroupBox):
    FILENAME, PATH = range(2)

    def __init__(self, title="Files"):
        super(QGroupBox, self).__init__(title)

        self.layout = QVBoxLayout(self)

        # Header row with label and contextual help button
        header_layout = QHBoxLayout()
        self.loaded_directory_label = QLabel("Click 'Open' to select an image folder.", self)
        self.help_button = QToolButton(self)
        self.help_button.setText("?")
        self.help_button.setFixedSize(20, 20)
        self.help_button.setStyleSheet(
            "QToolButton { border: 1px solid #888; border-radius: 10px; font-weight: bold; }"
        )
        self.help_button.setToolTip(
            "Select a folder that contains the images you want to annotate.\n"
            "GRC will list JPG/PNG files and keep them in the order they appear here."
        )
        self.help_button.clicked.connect(self.show_help)
        header_layout.addWidget(self.loaded_directory_label)
        header_layout.addWidget(self.help_button)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)

        self.dataView = QTreeView()
        self.dataView.setRootIsDecorated(False)
        self.dataView.setAlternatingRowColors(True)
        self.layout.addWidget(self.dataView)

        model = self.create_file_list_model(self)
        self.dataView.setModel(model)

        self.data_dir = None

        self.btnOpen = QPushButton("Open Folder…", self)
        self.btnOpen.setToolTip("Browse for a folder of images to annotate.")
        self.btnOpen.clicked.connect(self.load_data_directory)
        self.layout.addWidget(self.btnOpen)

        self.setLayout(self.layout)

        # Store reference to parent app for image list updates
        self.parent_app = None

    def show_help(self):
        """Show a help dialog explaining the image folder selector."""
        QMessageBox.information(
            self,
            "Image Folder",
            "Use 'Open Folder…' to choose the directory that contains the images you "
            "want to annotate. GRC will list JPG/PNG files from that folder and use "
            "their order here for Previous/Next navigation.",
        )

    def load_data_directory(self):
        d = QFileDialog.getExistingDirectory(self, "Select Directory")
        if not d:
            return ""

        self.data_dir = d
        self.loaded_directory_label.setText(self.data_dir)

        # Load all encountered files
        files = []
        allowed_extensions = ["jpg", "jpeg", "png", "bmp", "tiff", "tif", "webp", "gif"]
        for ext in allowed_extensions:
            files.extend(glob.glob(os.path.join(d, "*." + ext)))
            files.extend(glob.glob(os.path.join(d, "*." + ext.upper())))

        # Sort files for consistent ordering
        files.sort()

        # Update parent app's image files list
        if self.parent_app:
            self.parent_app.image_files = files
            self.parent_app.current_image_index = 0

        # Clear existing data and rebuild model in correct order
        model = self.dataView.model()
        model.removeRows(0, model.rowCount())

        # Add files in the same order as the files array
        for file in files:
            self.add_file_entry(model, file)

        # Load the first image if available
        if self.parent_app and files:
            self.parent_app.load_current_image()

        return d

    def create_file_list_model(self, parent):
        model = QStandardItemModel(0, 2, parent)
        model.setHeaderData(self.FILENAME, Qt.Horizontal, "Filename")
        model.setHeaderData(self.PATH, Qt.Horizontal, "Path")
        return model

    def add_file_entry(self, model, path):
        filename = os.path.basename(path)
        # Add at the end of the model to maintain order consistency
        row = model.rowCount()
        model.insertRow(row)
        model.setData(model.index(row, self.FILENAME), filename)
        model.setData(model.index(row, self.PATH), path)
