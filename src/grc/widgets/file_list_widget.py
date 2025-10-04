import os
import glob

# https://pythonspot.com/pyqt5-treeview/
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QPushButton, QFileDialog, QVBoxLayout, QLabel, QTreeView
from PyQt5.QtGui import QStandardItemModel


class FileListWidget(QGroupBox):

    FILENAME, PATH = range(2)

    def __init__(self, title="Files"):
        super(QGroupBox, self).__init__(title)

        self.layout = QVBoxLayout(self)

        self.dataView = QTreeView()
        self.dataView.setRootIsDecorated(False)
        self.dataView.setAlternatingRowColors(True)
        self.layout.addWidget(self.dataView)

        model = self.create_file_list_model(self)
        self.dataView.setModel(model)

        self.data_dir = None
        self.loaded_directory_label = QLabel("Click 'Open' to select a directory.", self)
        self.layout.addWidget(self.loaded_directory_label)

        self.btnOpen = QPushButton("Open", self)
        self.btnOpen.clicked.connect(self.load_data_directory)
        self.layout.addWidget(self.btnOpen)

        self.setLayout(self.layout)
        
        # Store reference to parent app for image list updates
        self.parent_app = None

    def load_data_directory(self):
        d = QFileDialog.getExistingDirectory(self, "Select Directory")
        self.data_dir = d
        self.loaded_directory_label.setText(self.data_dir)

        # Load all encountered files
        files = []
        allowed_extensions = ["jpg", "jpeg", "png"]
        for ext in allowed_extensions:
            files.extend(glob.glob(os.path.join(d, "*." + ext)))

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
            self.parent_app.image_panel.load_image(files[0])
            self.parent_app.load_annotations_for_image(files[0])

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
