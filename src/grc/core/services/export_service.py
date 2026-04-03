"""
Export service for batch annotation export operations.

Encapsulates all export-related business logic including:
- Batch export to different formats
- Progress tracking
- Error handling
"""

import os
from typing import Callable, List, Optional

from PyQt5.QtGui import QImage

from ..bounding_box import BoundingBox
from ..events import EventBus


class ExportService:
    """
    Service for annotation export operations.

    Responsibilities:
    - Export annotations to various formats
    - Batch processing of multiple images
    - Progress reporting
    """

    def __init__(self, format_manager, event_bus: Optional[EventBus] = None):
        """
        Initialize export service.

        Args:
            format_manager: AnnotationFormatManager instance
            event_bus: Optional event bus for publishing events
        """
        self.format_manager = format_manager
        self.event_bus = event_bus

        # Export state
        self._is_exporting = False
        self._cancelled = False

    @property
    def is_exporting(self) -> bool:
        """Check if export is in progress."""
        return self._is_exporting

    def cancel_export(self) -> None:
        """Cancel current export operation."""
        self._cancelled = True

    def export_annotations(
        self,
        image_files: List[str],
        target_format: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        source_format: str = "grc",
    ) -> dict:
        """
        Export annotations for multiple images to a target format.

        Args:
            image_files: List of image file paths
            target_format: Format to export to (e.g., "yolo", "coco")
            progress_callback: Optional callback(current, total) for progress
            source_format: Format to read annotations from (default: grc)

        Returns:
            Dict with export results: exported_count, skipped_count, errors
        """
        self._is_exporting = True
        self._cancelled = False

        exported_count = 0
        skipped_count = 0
        errors = []

        total = len(image_files)

        for i, image_path in enumerate(image_files):
            if self._cancelled:
                break

            if progress_callback:
                progress_callback(i + 1, total)

            if not os.path.exists(image_path):
                skipped_count += 1
                continue

            # Get image dimensions
            image = QImage(image_path)
            if image.isNull():
                skipped_count += 1
                continue

            width = image.width()
            height = image.height()

            try:
                # Load annotations from source format
                boxes = self.format_manager.load_annotations(
                    image_path, width, height, preferred_format=source_format
                )

                if not boxes:
                    skipped_count += 1
                    continue

                # Save in target format
                self.format_manager.save_annotations(
                    image_path, boxes, width, height, format_name=target_format
                )
                exported_count += 1

            except Exception as e:
                errors.append({"image": image_path, "error": str(e)})
                skipped_count += 1

        self._is_exporting = False

        return {
            "exported_count": exported_count,
            "skipped_count": skipped_count,
            "errors": errors,
            "cancelled": self._cancelled,
        }

    def export_single_image(
        self,
        image_path: str,
        bounding_boxes: List[BoundingBox],
        image_width: int,
        image_height: int,
        target_format: str,
    ) -> bool:
        """
        Export annotations for a single image.

        Args:
            image_path: Path to image file
            bounding_boxes: List of BoundingBox objects
            image_width: Image width
            image_height: Image height
            target_format: Format to export to

        Returns:
            True if successful
        """
        try:
            self.format_manager.save_annotations(
                image_path, bounding_boxes, image_width, image_height, format_name=target_format
            )
            return True
        except Exception as e:
            print(f"Error exporting annotations for {image_path}: {e}")
            return False

    def get_available_export_formats(self) -> List[str]:
        """
        Get list of available export formats (excludes internal format).

        Returns:
            List of format names
        """
        return [fmt for fmt in self.format_manager.list_formats() if fmt.lower() != "grc"]
