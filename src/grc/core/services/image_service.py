"""
Image service for managing image loading and navigation.

Encapsulates all image-related business logic including:
- Image loading and validation
- Navigation between images
- Image metadata retrieval
"""

import os
from typing import List, Optional, Tuple

from PyQt5.QtGui import QImage

from ..events import EventBus, ImageChangedEvent, ImageLoadedEvent, NavigationEvent


class ImageService:
    """
    Service for image management.

    Responsibilities:
    - Load and validate images
    - Manage image navigation state
    - Provide image metadata
    - Coordinate image file discovery
    """

    SUPPORTED_EXTENSIONS = ["jpg", "jpeg", "png", "bmp", "tiff", "tif", "webp", "gif"]

    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize image service.

        Args:
            event_bus: Optional event bus for publishing events
        """
        self.event_bus = event_bus

        # Image state
        self._image_files: List[str] = []
        self._current_index: int = 0
        self._data_dir: str = ""
        self._current_image: Optional[QImage] = None

    @property
    def image_files(self) -> List[str]:
        """Get list of loaded image files."""
        return self._image_files

    @image_files.setter
    def image_files(self, files: List[str]) -> None:
        """Set image files list."""
        self._image_files = files
        self._current_index = 0 if files else -1

    @property
    def current_index(self) -> int:
        """Get current image index."""
        return self._current_index

    @current_index.setter
    def current_index(self, index: int) -> None:
        """Set current image index."""
        if 0 <= index < len(self._image_files):
            self._current_index = index

    @property
    def data_dir(self) -> str:
        """Get current data directory."""
        return self._data_dir

    @data_dir.setter
    def data_dir(self, path: str) -> None:
        """Set data directory."""
        self._data_dir = path

    @property
    def current_image_path(self) -> Optional[str]:
        """Get path to current image."""
        if self._image_files and 0 <= self._current_index < len(self._image_files):
            return self._image_files[self._current_index]
        return None

    @property
    def has_images(self) -> bool:
        """Check if images are loaded."""
        return bool(self._image_files)

    @property
    def total_images(self) -> int:
        """Get total number of images."""
        return len(self._image_files)

    def load_directory(self, directory: str) -> List[str]:
        """
        Load all supported images from a directory.

        Args:
            directory: Path to directory

        Returns:
            List of image file paths
        """
        import glob

        if not os.path.isdir(directory):
            print(f"Directory not found: {directory}")
            return []

        self._data_dir = directory
        files = []

        for ext in self.SUPPORTED_EXTENSIONS:
            files.extend(glob.glob(os.path.join(directory, f"*.{ext}")))
            files.extend(glob.glob(os.path.join(directory, f"*.{ext.upper()}")))

        files.sort()
        self._image_files = files
        self._current_index = 0 if files else -1

        return files

    def load_image(self, image_path: str) -> Optional[QImage]:
        """
        Load an image file.

        Args:
            image_path: Path to image file

        Returns:
            QImage if successful, None otherwise
        """
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return None

        image = QImage(image_path)
        if image.isNull():
            print(f"Failed to load image: {image_path}")
            return None

        self._current_image = image

        if self.event_bus:
            self.event_bus.publish(
                ImageLoadedEvent(
                    source=self,
                    image_path=image_path,
                    width=image.width(),
                    height=image.height(),
                )
            )

        return image

    def get_image_dimensions(
        self, image_path: Optional[str] = None, default_width: int = 800, default_height: int = 600
    ) -> Tuple[int, int]:
        """
        Get dimensions of an image.

        Args:
            image_path: Optional path to image (uses current if not provided)
            default_width: Default width if image not available
            default_height: Default height if image not available

        Returns:
            Tuple of (width, height)
        """
        if image_path is None:
            image_path = self.current_image_path

        if image_path and os.path.exists(image_path):
            image = QImage(image_path)
            if not image.isNull():
                return image.width(), image.height()

        return default_width, default_height

    def previous_image(self) -> Optional[str]:
        """
        Navigate to previous image.

        Returns:
            Path to previous image, or None if at beginning
        """
        if not self._image_files or self._current_index <= 0:
            return None

        old_index = self._current_index
        self._current_index -= 1

        if self.event_bus:
            self.event_bus.publish(
                NavigationEvent(
                    source=self,
                    direction="previous",
                    from_index=old_index,
                    to_index=self._current_index,
                )
            )

        return self.current_image_path

    def next_image(self) -> Optional[str]:
        """
        Navigate to next image.

        Returns:
            Path to next image, or None if at end
        """
        if not self._image_files or self._current_index >= len(self._image_files) - 1:
            return None

        old_index = self._current_index
        self._current_index += 1

        if self.event_bus:
            self.event_bus.publish(
                NavigationEvent(
                    source=self,
                    direction="next",
                    from_index=old_index,
                    to_index=self._current_index,
                )
            )

        return self.current_image_path

    def go_to_image(self, index: int) -> Optional[str]:
        """
        Navigate to specific image by index.

        Args:
            index: Image index

        Returns:
            Path to image, or None if index invalid
        """
        if not self._image_files or not (0 <= index < len(self._image_files)):
            return None

        old_index = self._current_index
        self._current_index = index

        if self.event_bus and old_index != index:
            self.event_bus.publish(
                ImageChangedEvent(
                    source=self,
                    image_path=self.current_image_path or "",
                    image_index=index,
                    total_images=len(self._image_files),
                )
            )

        return self.current_image_path

    def can_navigate_previous(self) -> bool:
        """Check if can navigate to previous image."""
        return bool(self._image_files) and self._current_index > 0

    def can_navigate_next(self) -> bool:
        """Check if can navigate to next image."""
        return bool(self._image_files) and self._current_index < len(self._image_files) - 1

    def get_image_info(self) -> dict:
        """
        Get information about current image state.

        Returns:
            Dict with current_index, total_images, current_path, data_dir
        """
        return {
            "current_index": self._current_index,
            "total_images": len(self._image_files),
            "current_path": self.current_image_path,
            "data_dir": self._data_dir,
            "can_previous": self.can_navigate_previous(),
            "can_next": self.can_navigate_next(),
        }
