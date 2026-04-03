"""
Navigation controller for image navigation.

Handles navigation between images, coordinating with
ImageService and publishing navigation events.
"""

from typing import Callable, Optional

from ...core.events import EventBus, ImageChangedEvent
from ...core.services.image_service import ImageService


class NavigationController:
    """
    Controller for image navigation.

    Responsibilities:
    - Handle navigation requests (previous/next)
    - Coordinate with ImageService
    - Publish navigation events
    - Update UI state
    """

    def __init__(
        self,
        image_service: ImageService,
        event_bus: Optional[EventBus] = None,
    ):
        """
        Initialize navigation controller.

        Args:
            image_service: Service for image management
            event_bus: Optional event bus for publishing events
        """
        self.image_service = image_service
        self.event_bus = event_bus

        # Callbacks for UI updates
        self._on_image_changed: Optional[Callable] = None
        self._on_navigation_state_changed: Optional[Callable] = None

    def set_callbacks(
        self,
        on_image_changed: Optional[Callable] = None,
        on_navigation_state_changed: Optional[Callable] = None,
    ) -> None:
        """
        Set callbacks for UI updates.

        Args:
            on_image_changed: Called when image changes with (image_path, index, total)
            on_navigation_state_changed: Called when nav state changes with (can_prev, can_next)
        """
        self._on_image_changed = on_image_changed
        self._on_navigation_state_changed = on_navigation_state_changed

    def previous(self) -> Optional[str]:
        """
        Navigate to previous image.

        Returns:
            Path to previous image, or None if at beginning
        """
        image_path = self.image_service.previous_image()

        if image_path:
            self._notify_image_changed(image_path)
            self._notify_navigation_state_changed()

        return image_path

    def next(self) -> Optional[str]:
        """
        Navigate to next image.

        Returns:
            Path to next image, or None if at end
        """
        image_path = self.image_service.next_image()

        if image_path:
            self._notify_image_changed(image_path)
            self._notify_navigation_state_changed()

        return image_path

    def go_to(self, index: int) -> Optional[str]:
        """
        Navigate to specific image by index.

        Args:
            index: Image index (0-based)

        Returns:
            Path to image, or None if invalid index
        """
        image_path = self.image_service.go_to_image(index)

        if image_path:
            self._notify_image_changed(image_path)
            self._notify_navigation_state_changed()

        return image_path

    def load_directory(self, directory: str) -> bool:
        """
        Load images from a directory.

        Args:
            directory: Path to directory

        Returns:
            True if images were loaded
        """
        files = self.image_service.load_directory(directory)

        if files:
            self._notify_image_changed(files[0])
            self._notify_navigation_state_changed()
            return True

        return False

    def can_previous(self) -> bool:
        """Check if can navigate to previous image."""
        return self.image_service.can_navigate_previous()

    def can_next(self) -> bool:
        """Check if can navigate to next image."""
        return self.image_service.can_navigate_next()

    def get_navigation_state(self) -> dict:
        """
        Get current navigation state.

        Returns:
            Dict with current_index, total, can_previous, can_next
        """
        info = self.image_service.get_image_info()
        return {
            "current_index": info["current_index"],
            "total": info["total_images"],
            "current_path": info["current_path"],
            "can_previous": info["can_previous"],
            "can_next": info["can_next"],
        }

    def _notify_image_changed(self, image_path: str) -> None:
        """Notify listeners of image change."""
        info = self.image_service.get_image_info()

        if self.event_bus:
            self.event_bus.publish(
                ImageChangedEvent(
                    source=self,
                    image_path=image_path,
                    image_index=info["current_index"],
                    total_images=info["total_images"],
                )
            )

        if self._on_image_changed:
            self._on_image_changed(
                image_path,
                info["current_index"] + 1,  # 1-based for display
                info["total_images"],
            )

    def _notify_navigation_state_changed(self) -> None:
        """Notify listeners of navigation state change."""
        if self._on_navigation_state_changed:
            self._on_navigation_state_changed(
                self.can_previous(),
                self.can_next(),
            )
