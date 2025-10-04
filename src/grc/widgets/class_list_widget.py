import os
import glob

# https://pythonspot.com/pyqt5-treeview/
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QPushButton, QFileDialog, QVBoxLayout, QLabel, QTreeView
from PyQt5.QtGui import QStandardItemModel


class ClassListWidget(QGroupBox):

    ID, NAME = range(2)

    def __init__(self, title="Classes"):
        super(QGroupBox, self).__init__(title)

        self.layout = QVBoxLayout(self)

        self.dataView = QTreeView()
        self.dataView.setRootIsDecorated(False)
        self.dataView.setAlternatingRowColors(True)
        self.layout.addWidget(self.dataView)

        model = self.create_file_list_model(self)
        self.dataView.setModel(model)

        self.data_dir = None
        self.loaded_directory_label = QLabel("Click 'Open' to select a file.", self)
        self.layout.addWidget(self.loaded_directory_label)

        self.btnOpen = QPushButton("Open", self)
        self.btnOpen.clicked.connect(self.load_data_directory)
        self.layout.addWidget(self.btnOpen)

        self.setLayout(self.layout)
        
        # Store reference to parent app for class updates
        self.parent_app = None

    def load_data_directory(self):
        # Open file dialog to select a classes file
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Classes File", 
            "", 
            "Text Files (*.txt);;All Files (*)"
        )
        
        if file_path:
            self.data_dir = file_path
            self.loaded_directory_label.setText(f"Classes file: {os.path.basename(file_path)}")
            
            # Clear existing data
            model = self.dataView.model()
            model.removeRows(0, model.rowCount())
            
            # Load classes from file
            self.load_classes_from_file(file_path)
            
        return file_path

    def create_file_list_model(self, parent):
        model = QStandardItemModel(0, 2, parent)
        model.setHeaderData(self.ID, Qt.Horizontal, "ID")
        model.setHeaderData(self.NAME, Qt.Horizontal, "Name")
        return model

    def load_classes_from_file(self, file_path):
        """Load classes from a text file."""
        classes = []
        try:
            with open(file_path, 'r') as f:
                model = self.dataView.model()
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split()
                    if len(parts) >= 2:
                        class_id = parts[0]
                        class_name = ' '.join(parts[1:])  # Join remaining parts as class name
                        self.add_class_entry(model, class_id, class_name)
                        classes.append((class_id, class_name))
                    else:
                        print(f"Warning: Invalid class format at line {line_num}: {line}")
            
            # Notify parent app about loaded classes
            if self.parent_app:
                self.parent_app.update_classes(classes)
                        
        except Exception as e:
            print(f"Error loading classes file: {e}")

    def add_class_entry(self, model, class_id, class_name):
        """Add a class entry to the model."""
        model.insertRow(0)
        model.setData(model.index(0, self.ID), class_id)
        model.setData(model.index(0, self.NAME), class_name)

    def add_file_entry(self, model, path):
        filename = os.path.basename(path)
        model.insertRow(0)
        model.setData(model.index(0, self.ID), filename)
        model.setData(model.index(0, self.NAME), path)
