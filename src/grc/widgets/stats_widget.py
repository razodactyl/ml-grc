"""
Annotation statistics and progress tracking widget.
"""

from collections import Counter
from typing import List, Tuple

from PyQt5.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)


class StatsWidget(QGroupBox):
    """Widget for displaying annotation statistics and progress tracking."""

    def __init__(self, title="Statistics"):
        super().__init__(title)
        self.layout = QVBoxLayout(self)
        self.parent_app = None
        self._init_ui()

    def _init_ui(self):
        # Progress section
        progress_layout = QHBoxLayout()
        self.progress_label = QLabel("Progress:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%v / %m (%p%)")
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        self.layout.addLayout(progress_layout)

        # Summary labels
        self.total_images_label = QLabel("Total Images: 0")
        self.annotated_images_label = QLabel("Annotated Images: 0")
        self.total_annotations_label = QLabel("Total Annotations: 0")

        self.layout.addWidget(self.total_images_label)
        self.layout.addWidget(self.annotated_images_label)
        self.layout.addWidget(self.total_annotations_label)

        # Class distribution table
        self.layout.addWidget(QLabel("Class Distribution:"))
        self.class_table = QTableWidget()
        self.class_table.setColumnCount(3)
        self.class_table.setHorizontalHeaderLabels(["Class", "Count", "Percentage"])
        self.class_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.class_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.class_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.class_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.class_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.layout.addWidget(self.class_table)

        # Refresh button
        self.refresh_button = QPushButton("Refresh Statistics")
        self.refresh_button.clicked.connect(self.refresh_stats)
        self.layout.addWidget(self.refresh_button)

        self.setLayout(self.layout)

    def update_stats(
        self,
        image_files: List[str],
        annotations_dir: str,
        get_annotations_func,
        classes: List[Tuple[int, str]] = None,
    ):
        """
        Update statistics based on current dataset.

        Args:
            image_files: List of image file paths
            annotations_dir: Directory containing annotations
            get_annotations_func: Function to get annotations for an image
            classes: Optional list of (class_id, class_name) tuples
        """
        total_images = len(image_files)
        annotated_count = 0
        total_annotations = 0
        class_counter = Counter()

        for image_path in image_files:
            annotations = get_annotations_func(image_path)
            if annotations:
                annotated_count += 1
                total_annotations += len(annotations)
                for box in annotations:
                    class_counter[box.class_name] += 1

        # Update progress bar
        self.progress_bar.setMaximum(total_images)
        self.progress_bar.setValue(annotated_count)

        # Update labels
        self.total_images_label.setText(f"Total Images: {total_images}")
        self.annotated_images_label.setText(f"Annotated Images: {annotated_count}")
        self.total_annotations_label.setText(f"Total Annotations: {total_annotations}")

        # Update class distribution table
        self.class_table.setRowCount(len(class_counter))

        for row, (class_name, count) in enumerate(sorted(class_counter.items())):
            percentage = (count / total_annotations * 100) if total_annotations > 0 else 0

            self.class_table.setItem(row, 0, QTableWidgetItem(class_name))
            self.class_table.setItem(row, 1, QTableWidgetItem(str(count)))
            self.class_table.setItem(row, 2, QTableWidgetItem(f"{percentage:.1f}%"))

    def refresh_stats(self):
        """Refresh statistics from parent app."""
        if self.parent_app:
            self.parent_app.refresh_statistics()

    def clear_stats(self):
        """Clear all statistics."""
        self.progress_bar.setValue(0)
        self.total_images_label.setText("Total Images: 0")
        self.annotated_images_label.setText("Annotated Images: 0")
        self.total_annotations_label.setText("Total Annotations: 0")
        self.class_table.setRowCount(0)
