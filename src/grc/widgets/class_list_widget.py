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


class ClassListWidget(QGroupBox):
    ID, NAME = range(2)

    def __init__(self, title="Classes"):
        super(QGroupBox, self).__init__(title)

        self.layout = QVBoxLayout(self)

        # Header row with label and contextual help button
        header_layout = QHBoxLayout()
        self.loaded_directory_label = QLabel("Click 'Open' to select a classes file.", self)
        self.help_button = QToolButton(self)
        self.help_button.setText("?")
        self.help_button.setFixedSize(20, 20)
        self.help_button.setStyleSheet(
            "QToolButton { border: 1px solid #888; border-radius: 10px; font-weight: bold; }"
        )
        self.help_button.setToolTip(
            "Choose a text file where each line defines a class as:\n"
            "  <id> <class name>\n"
            "Example: 0 person"
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

        self.btnOpen = QPushButton("Open Classes File…", self)
        self.btnOpen.setToolTip("Browse for a text file that defines your annotation classes.")
        self.btnOpen.clicked.connect(self.load_data_directory)
        self.layout.addWidget(self.btnOpen)

        self.setLayout(self.layout)

        # Store reference to parent app for class updates
        self.parent_app = None

    def load_data_directory(self):
        # Open file dialog to select a classes file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Classes File", "", "Text Files (*.txt);;All Files (*)"
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
            with open(file_path) as f:
                model = self.dataView.model()
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    parts = line.split()
                    if len(parts) >= 2:
                        class_id_str = parts[0]
                        class_name = " ".join(parts[1:])  # Join remaining parts as class name

                        # Convert class_id to int for consistency with BoundingBox
                        try:
                            class_id = int(class_id_str)
                        except ValueError:
                            print(
                                f"Warning: Invalid class_id '{class_id_str}' at line {line_num}: {line}"
                            )
                            continue

                        self.add_class_entry(model, class_id_str, class_name)
                        classes.append((class_id, class_name))  # Store as int for consistency
                    else:
                        print(f"Warning: Invalid class format at line {line_num}: {line}")

            # Notify parent app about loaded classes
            if self.parent_app:
                self.parent_app.update_classes(classes)

        except Exception as e:
            print(f"Error loading classes file: {e}")

    def add_class_entry(self, model, class_id, class_name):
        """Add a class entry to the model."""
        # Add at the end of the model to maintain order consistency
        row = model.rowCount()
        model.insertRow(row)
        model.setData(model.index(row, self.ID), class_id)
        model.setData(model.index(row, self.NAME), class_name)

    def add_file_entry(self, model, path):
        filename = os.path.basename(path)
        # Add at the end of the model to maintain order consistency
        row = model.rowCount()
        model.insertRow(row)
        model.setData(model.index(row, self.ID), filename)
        model.setData(model.index(row, self.NAME), path)

    def show_help(self):
        """Show a help dialog explaining the classes file selector."""
        QMessageBox.information(
            self,
            "Classes File",
            "Use 'Open Classes File…' to choose a text file defining your annotation "
            "classes. Each non-comment line should have the form:\n\n"
            "    <id> <class name>\n\n"
            "For example:\n"
            "    0 person\n"
            "    1 car\n"
            "    2 traffic_light",
        )
