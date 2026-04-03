"""
Batch processing widget for GRC.
"""

import os
from typing import List

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)


class BatchExportThread(QThread):
    """Thread for batch exporting annotations."""

    progress = pyqtSignal(int, int)  # current, total
    finished = pyqtSignal(int)  # count of exported images
    error = pyqtSignal(str)  # error message

    def __init__(self, image_files: List[str], format_manager, target_format: str):
        super().__init__()
        self.image_files = image_files
        self.format_manager = format_manager
        self.target_format = target_format
        self._is_cancelled = False

    def run(self):
        from PyQt5.QtGui import QImage

        exported_count = 0

        for i, image_path in enumerate(self.image_files):
            if self._is_cancelled:
                break

            self.progress.emit(i + 1, len(self.image_files))

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
                image_path, boxes, width, height, format_name=self.target_format
            )
            exported_count += 1

        self.finished.emit(exported_count)

    def cancel(self):
        self._is_cancelled = True


class BatchWidget(QGroupBox):
    """Widget for batch processing operations."""

    def __init__(self, title="Batch Processing"):
        super().__init__(title)
        self.layout = QVBoxLayout(self)
        self.parent_app = None
        self._batch_thread = None
        self._init_ui()

    def _init_ui(self):
        # Export section
        self.layout.addWidget(QLabel("Batch Export:"))

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["YOLO", "COCO"])
        format_layout.addWidget(self.format_combo)
        format_layout.addStretch()
        self.layout.addLayout(format_layout)

        # Options
        self.include_unannotated = QCheckBox("Include unannotated images")
        self.include_unannotated.setChecked(False)
        self.layout.addWidget(self.include_unannotated)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m")
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        # Buttons
        button_layout = QHBoxLayout()
        self.export_button = QPushButton("Export All Annotations")
        self.export_button.clicked.connect(self._start_batch_export)
        button_layout.addWidget(self.export_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._cancel_batch)
        self.cancel_button.setVisible(False)
        button_layout.addWidget(self.cancel_button)

        self.layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        self.setLayout(self.layout)

    def _start_batch_export(self):
        """Start batch export process."""
        if not self.parent_app or not hasattr(self.parent_app, "image_files"):
            QMessageBox.warning(self, "Error", "No images loaded.")
            return

        if not self.parent_app.image_files:
            QMessageBox.warning(self, "Error", "No images loaded.")
            return

        target_format = self.format_combo.currentText().lower()

        self._batch_thread = BatchExportThread(
            self.parent_app.image_files, self.parent_app.format_manager, target_format
        )

        self._batch_thread.progress.connect(self._on_progress)
        self._batch_thread.finished.connect(self._on_finished)
        self._batch_thread.error.connect(self._on_error)

        self.export_button.setEnabled(False)
        self.cancel_button.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(self.parent_app.image_files))
        self.progress_bar.setValue(0)
        self.status_label.setText("Exporting...")

        self._batch_thread.start()

    def _cancel_batch(self):
        """Cancel batch operation."""
        if self._batch_thread:
            self._batch_thread.cancel()
            self.status_label.setText("Cancelling...")

    def _on_progress(self, current: int, total: int):
        """Update progress bar."""
        self.progress_bar.setValue(current)

    def _on_finished(self, count: int):
        """Handle batch completion."""
        self.export_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Exported {count} annotation(s)")
        self._batch_thread = None

    def _on_error(self, message: str):
        """Handle batch error."""
        self.export_button.setEnabled(True)
        self.cancel_button.setVisible(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Error: {message}")
        self._batch_thread = None

    def update_formats(self, formats: List[str]):
        """Update available formats in combo box."""
        self.format_combo.clear()
        for fmt in formats:
            if fmt.lower() != "grc":
                self.format_combo.addItem(fmt.upper())
