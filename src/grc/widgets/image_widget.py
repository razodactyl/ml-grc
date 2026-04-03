import os

import numpy as np
from PyQt5.QtCore import (
    QMutex,
    QMutexLocker,
    QRect,
    Qt,
    QThread,
    QWaitCondition,
    pyqtSignal,
)
from PyQt5.QtGui import QBrush, QColor, QCursor, QImage, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy

from ..core.bounding_box import BoundingBox
from ..core.state import make_default_state


class RenderThread(QThread):
    renderedImage = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mutex = QMutex()
        self.state = make_default_state()
        self.condition = QWaitCondition()
        self.restart = False
        self.abort = False

        self.base_image = None
        self.canvas = self.make_canvas(800, 600)
        self.animation_phase = 0.0

    def __del__(self):
        # Guard against Qt C++ object already being destroyed
        try:
            self.mutex.lock()
            self.abort = True
            self.condition.wakeOne()
            self.mutex.unlock()
            self.wait()
        except RuntimeError:
            # Qt object already deleted, nothing to do
            pass

    def make_canvas(self, width, height):
        im_np = np.ones((width, height, 3), dtype=np.uint8)
        im_np = np.transpose(im_np, (1, 0, 2)).copy()
        canvas = QImage(im_np, im_np.shape[1], im_np.shape[0], QImage.Format_RGB888)
        return canvas

    def load_image(self, path):
        image = QImage(path)
        self.mutex.lock()
        self.base_image = image

        self.canvas = self.make_canvas(self.base_image.width(), self.base_image.height())

        self.mutex.unlock()

    def render(self, state=None):
        QMutexLocker(self.mutex)

        # update renderable state
        if state:
            # print("Update render state")
            # print("state =>", state)
            self.state = state

        if not self.isRunning():
            self.start(QThread.LowPriority)
        else:
            self.restart = True
            self.condition.wakeOne()

    def run(self):
        while not self.abort:
            self.mutex.lock()
            state = self.state
            canvas = self.canvas
            base_image = self.base_image
            self.mutex.unlock()

            # Ensure canvas is valid
            if canvas is None or canvas.isNull():
                continue

            painter = QPainter()

            if painter.begin(canvas):
                # Draw the base image if available
                if base_image and not base_image.isNull():
                    painter.drawImage(canvas.rect(), base_image)
                else:
                    # Fill with black background if no image
                    painter.fillRect(canvas.rect(), Qt.black)

                brush = QBrush(QColor("#FF00FF"))
                painter.setBrush(brush)
                painter.setPen(Qt.white)

                if state.dragging:
                    painter.setOpacity(0.4)
                    # Preview rectangle while drawing; uses the same coordinate
                    # space as stored in the state (image coordinates).
                    x = state.drag_start_pos[0]
                    y = state.drag_start_pos[1]
                    w = state.mouse_pos[0] - state.drag_start_pos[0]
                    h = state.mouse_pos[1] - state.drag_start_pos[1]
                    pen = QPen(Qt.white, 1, Qt.DashLine)
                    pen.setDashPattern([4, 4])
                    pen.setDashOffset(self.animation_phase)
                    painter.setPen(pen)
                    painter.drawRect(x, y, w, h)

                for box in state.bounding_boxes:
                    box.draw(painter, phase=self.animation_phase)

                painter.end()

            if not self.restart and not self.abort:
                self.renderedImage.emit(self.canvas)

            self.mutex.lock()
            # Advance animation phase for marching ants
            self.animation_phase = (self.animation_phase + 1.0) % 8.0
            if not self.restart and not self.abort:
                self.condition.wait(self.mutex)
            self.restart = False
            self.mutex.unlock()


class ImageWidget(QLabel):
    def __init__(self, parent):
        super(QLabel, self).__init__(parent)
        self.parent_app = parent

        # Callback for zoom changes
        self.zoom_changed = None

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        self.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus

        self.thread = RenderThread()
        self.pixmap = QPixmap()
        self.thread.renderedImage.connect(self.updatePixmap)

        self.thread.render()
        self._cleanup_done = False
        # https://stackoverflow.com/questions/7829829/pyqt4-mousemove-event-without-mousepress

        self.state = make_default_state()

        # Simple history stacks for undo/redo of bounding box edits
        self.undo_stack = []
        self.redo_stack = []
        self.max_history = 100

        # Zoom and pan state
        self._zoom_level = 1.0
        self._pan_offset = [0, 0]  # x, y offset in widget coordinates
        self._is_panning = False
        self._pan_start_pos = None
        self._min_zoom = 0.1
        self._max_zoom = 10.0
        self._zoom_step = 1.2

        # Don't auto-load any image initially - wait for explicit loading

    def sizeHint(self):
        """Return the preferred size for the widget."""
        if (
            hasattr(self, "thread")
            and self.thread.base_image
            and not self.thread.base_image.isNull()
        ):
            return self.thread.base_image.size()
        return super().sizeHint()

    def minimumSizeHint(self):
        """Return the minimum size for the widget."""
        return self.sizeHint()

    def resizeEvent(self, event):
        """Handle widget resize events."""
        super().resizeEvent(event)
        # Let the layout control the widget size; just update geometry hints.
        self.updateGeometry()

    def load_image(self, image_path):
        """Load an image from the given path."""
        if os.path.exists(image_path):
            print(f"Loading image: {image_path}")
            self.thread.load_image(image_path)
            # Reset zoom and pan when loading new image
            self._zoom_level = 1.0
            self._pan_offset = [0, 0]
            # Update widget size to match image
            if (
                hasattr(self, "thread")
                and self.thread.base_image
                and not self.thread.base_image.isNull()
            ):
                self.updateGeometry()
        else:
            print(f"Image not found: {image_path}")

    def mouseMoveEvent(self, event):
        # Handle panning with middle button
        if self._is_panning and self._pan_start_pos:
            delta = event.pos() - self._pan_start_pos
            self._pan_offset[0] += delta.x()
            self._pan_offset[1] += delta.y()
            self._pan_start_pos = event.pos()
            self.update()
            event.accept()
            return

        mouse_x = event.pos().x()
        mouse_y = event.pos().y()

        # Map mouse coordinates to image coordinates
        image_mouse_x, image_mouse_y = self._map_to_image_coordinates(mouse_x, mouse_y)

        if self.state.dragging and self.state.drag_mode:
            boxes = self.state.bounding_boxes

            if self.state.drag_mode == "move" and self.state.drag_box_index >= 0:
                # Handle box movement
                box = boxes[self.state.drag_box_index]
                if box.selected:
                    # Map drag start position to image coordinates
                    start_x, start_y = self._map_to_image_coordinates(
                        self.state.drag_start_pos[0], self.state.drag_start_pos[1]
                    )

                    dx = image_mouse_x - start_x
                    dy = image_mouse_y - start_y

                    # Update box position (ensure integer coordinates)
                    box.x = max(0, int(box.x + dx))
                    box.y = max(0, int(box.y + dy))

                    # Update drag start position for smooth dragging
                    self.state = self.state._replace(drag_start_pos=[mouse_x, mouse_y])

            elif self.state.drag_mode == "resize" and self.state.drag_box_index >= 0:
                # Handle box resizing
                box = boxes[self.state.drag_box_index]
                if box.selected and self.state.drag_handle:
                    # Map drag start position to image coordinates
                    start_x, start_y = self._map_to_image_coordinates(
                        self.state.drag_start_pos[0], self.state.drag_start_pos[1]
                    )

                    dx = image_mouse_x - start_x
                    dy = image_mouse_y - start_y

                    # Resize based on handle
                    if self.state.drag_handle == "nw":
                        box.x = max(0, int(box.x + dx))
                        box.y = max(0, int(box.y + dy))
                        box.w = max(10, int(box.w - dx))
                        box.h = max(10, int(box.h - dy))
                    elif self.state.drag_handle == "ne":
                        box.y = max(0, int(box.y + dy))
                        box.w = max(10, int(box.w + dx))
                        box.h = max(10, int(box.h - dy))
                    elif self.state.drag_handle == "sw":
                        box.x = max(0, int(box.x + dx))
                        box.w = max(10, int(box.w - dx))
                        box.h = max(10, int(box.h + dy))
                    elif self.state.drag_handle == "se":
                        box.w = max(10, int(box.w + dx))
                        box.h = max(10, int(box.h + dy))
                    elif self.state.drag_handle == "n":
                        box.y = max(0, int(box.y + dy))
                        box.h = max(10, int(box.h - dy))
                    elif self.state.drag_handle == "s":
                        box.h = max(10, int(box.h + dy))
                    elif self.state.drag_handle == "e":
                        box.w = max(10, int(box.w + dx))
                    elif self.state.drag_handle == "w":
                        box.x = max(0, int(box.x + dx))
                        box.w = max(10, int(box.w - dx))

                    # Update drag start position
                    self.state = self.state._replace(drag_start_pos=[mouse_x, mouse_y])

            self.state = self.state._replace(bounding_boxes=boxes)
            # Render using image-space positions for preview rectangle
            self.thread.render(self._state_for_render(image_mouse_x, image_mouse_y))
        else:
            # Update cursor based on what's under the mouse
            self.update_cursor(mouse_x, mouse_y)

        self.state = self.state._replace(mouse_pos=[mouse_x, mouse_y])
        self.thread.render(self._state_for_render(image_mouse_x, image_mouse_y))

    def mousePressEvent(self, event):
        # Handle middle button for panning
        if event.button() == Qt.MiddleButton:
            self._is_panning = True
            self._pan_start_pos = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
            event.accept()
            return

        mouse_x = event.pos().x()
        mouse_y = event.pos().y()

        # Map mouse coordinates to image coordinates
        image_mouse_x, image_mouse_y = self._map_to_image_coordinates(mouse_x, mouse_y)

        # event.buttons() => bitmask of ALL buttons - i.e we can perform multi click etc.
        if event.buttons() & Qt.LeftButton:
            # Snapshot state once at the start of an interaction for undo
            self._push_undo_state()

            boxes = self.state.bounding_boxes

            # Check if Ctrl is pressed for multi-selection
            ctrl_pressed = event.modifiers() & Qt.ControlModifier

            # Check if clicking on resize handles first
            clicked_on_handle = False
            if not ctrl_pressed:
                for i, box in enumerate(boxes):
                    if box.selected:
                        handle = box.get_resize_handle_at_point(image_mouse_x, image_mouse_y)
                        if handle:
                            # Start resize operation
                            self.state = self.state._replace(
                                drag_mode="resize",
                                drag_box_index=i,
                                drag_handle=handle,
                                drag_start_pos=[mouse_x, mouse_y],
                                dragging=True,
                            )
                            clicked_on_handle = True
                            break

            if not clicked_on_handle:
                # Check for box selection or dragging
                selected_any = False
                for box in boxes:
                    if box.xy_in_bounds(image_mouse_x, image_mouse_y):
                        if ctrl_pressed:
                            # Multi-selection mode: toggle selection of clicked box
                            box.selected = not box.selected
                        else:
                            # Single selection mode: select only clicked box, deselect others
                            for b in boxes:
                                b.selected = b is box
                        selected_any = True
                        break

                if not selected_any and not ctrl_pressed:
                    # Clicking on empty space - deselect all
                    for box in boxes:
                        box.selected = False

                self.thread.render(self.state)
                self.state = self.state._replace(bounding_boxes=boxes)

                # Notify parent app about selection change
                if self.parent_app:
                    self.parent_app.update_dropdown_for_selection()

                # Start dragging if a box is selected
                selected_boxes = [box for box in boxes if box.selected]
                if selected_boxes and not ctrl_pressed:
                    self.state = self.state._replace(
                        drag_mode="move",
                        drag_box_index=boxes.index(selected_boxes[0])
                        if len(selected_boxes) == 1
                        else -1,
                        drag_start_pos=[mouse_x, mouse_y],
                        dragging=True,
                    )

            self.state = self.state._replace(
                drag_start_pos=[mouse_x, mouse_y],
                dragging=True,
            )

    def mouseReleaseEvent(self, event):
        # Handle middle button release for panning
        if event.button() == Qt.MiddleButton and self._is_panning:
            self._is_panning = False
            self._pan_start_pos = None
            self.setCursor(QCursor(Qt.CrossCursor))
            event.accept()
            return

        # event.button() (lack of 's') => button that caused the event.
        if event.button() == Qt.LeftButton and self.state.dragging:
            self.state = self.state._replace(
                drag_end_pos=[event.pos().x(), event.pos().y()],
                dragging=False,
                drag_mode=None,
                drag_box_index=-1,
                drag_handle=None,
            )

            bounding_boxes = self.state.bounding_boxes

            # Map mouse coordinates to image coordinates for annotation creation
            start_x, start_y = self._map_to_image_coordinates(
                self.state.drag_start_pos[0], self.state.drag_start_pos[1]
            )
            end_x, end_y = self._map_to_image_coordinates(event.pos().x(), event.pos().y())

            x1 = int(start_x)
            x2 = int(end_x)
            y1 = int(start_y)
            y2 = int(end_y)

            # Normalize coordinates (remove difference between start corner and end corner):
            # top left, bottom right => x,y,w,h

            min_x = min(x1, x2)
            min_y = min(y1, y2)
            max_x = max(x1, x2)
            max_y = max(y1, y2)

            x = min_x
            y = min_y
            w = max_x - min_x
            h = max_y - min_y

            # Get current class selection from the parent app
            class_id = 0
            class_name = "Unknown"
            if self.parent_app and hasattr(self.parent_app, "get_current_class"):
                class_id, class_name = self.parent_app.get_current_class()

            box = BoundingBox(
                x=x, y=y, w=w, h=h, selected=True, class_id=class_id, class_name=class_name
            )

            if box.get_area() > 20:
                bounding_boxes.append(box)

            self.state = self.state._replace(bounding_boxes=bounding_boxes)

    def update_cursor(self, mouse_x, mouse_y):
        """Update cursor based on what's under the mouse."""
        if not self.state.dragging:
            # Map mouse coordinates to image coordinates
            image_mouse_x, image_mouse_y = self._map_to_image_coordinates(mouse_x, mouse_y)

            boxes = self.state.bounding_boxes

            # Check if over resize handles first
            for box in boxes:
                if box.selected:
                    handle = box.get_resize_handle_at_point(image_mouse_x, image_mouse_y)
                    if handle:
                        if handle in ["nw", "se"]:
                            self.setCursor(QCursor(Qt.SizeFDiagCursor))  # Diagonal resize
                        elif handle in ["ne", "sw"]:
                            self.setCursor(QCursor(Qt.SizeBDiagCursor))  # Other diagonal resize
                        elif handle in ["n", "s"]:
                            self.setCursor(QCursor(Qt.SizeVerCursor))  # Vertical resize
                        elif handle in ["e", "w"]:
                            self.setCursor(QCursor(Qt.SizeHorCursor))  # Horizontal resize
                        return

            # Check if over selected boxes for moving
            for box in boxes:
                if box.selected and box.xy_in_bounds(image_mouse_x, image_mouse_y):
                    self.setCursor(QCursor(Qt.SizeAllCursor))  # Move cursor
                    return

            # Default cursor
            self.setCursor(QCursor(Qt.CrossCursor))

    def _map_to_image_coordinates(self, mouse_x, mouse_y):
        """
        Map mouse coordinates from widget space to image space.

        Args:
            mouse_x (int): Mouse X coordinate in widget space
            mouse_y (int): Mouse Y coordinate in widget space

        Returns:
            tuple: (image_x, image_y) coordinates in image space as integers
        """
        if (
            not hasattr(self, "thread")
            or not self.thread.base_image
            or self.thread.base_image.isNull()
        ):
            return int(mouse_x), int(mouse_y)

        image_width = self.thread.base_image.width()
        image_height = self.thread.base_image.height()

        # Use the displayed image rect (letterboxed + centered), if available
        display_rect = getattr(self, "_display_rect", self.rect())
        if display_rect.width() <= 0 or display_rect.height() <= 0:
            return int(mouse_x), int(mouse_y)

        # If the mouse is outside the drawn image area, clamp to the nearest edge
        if mouse_x < display_rect.left():
            mouse_x = display_rect.left()
        elif mouse_x > display_rect.left() + display_rect.width():
            mouse_x = display_rect.left() + display_rect.width()

        if mouse_y < display_rect.top():
            mouse_y = display_rect.top()
        elif mouse_y > display_rect.top() + display_rect.height():
            mouse_y = display_rect.top() + display_rect.height()

        # Calculate scaling factors from displayed rect to image
        scale_x = image_width / float(display_rect.width())
        scale_y = image_height / float(display_rect.height())

        # Map to image coordinates relative to top-left of displayed rect
        image_x = (mouse_x - display_rect.left()) * scale_x
        image_y = (mouse_y - display_rect.top()) * scale_y

        # Clamp to image bounds (valid pixel range is 0 to width-1, 0 to height-1)
        image_x = max(0, min(image_width - 1, image_x))
        image_y = max(0, min(image_height - 1, image_y))

        return int(image_x), int(image_y)

    def keyPressEvent(self, event):
        """Handle keyboard events."""
        key = event.key()
        modifiers = event.modifiers()

        # Delete selected annotations
        if key == Qt.Key_Delete:
            self.delete_selected_boxes()
            return

        # Undo / Redo
        if modifiers & Qt.ControlModifier and key == Qt.Key_Z:
            self.undo()
            return
        if modifiers & Qt.ControlModifier and key == Qt.Key_Y:
            self.redo()
            return

        # Copy / Paste / Duplicate
        if modifiers & Qt.ControlModifier and key == Qt.Key_C:
            self.copy_selected_boxes()
            return
        if modifiers & Qt.ControlModifier and key == Qt.Key_V:
            self.paste_boxes()
            return
        if modifiers & Qt.ControlModifier and key == Qt.Key_D:
            self.duplicate_selected_boxes()
            return

        # Select All
        if modifiers & Qt.ControlModifier and key == Qt.Key_A:
            self.select_all_boxes()
            return

        # Nudge with arrow keys (when not in drag mode)
        if not self.state.dragging:
            nudge_amount = 1 if not (modifiers & Qt.ShiftModifier) else 10
            if key == Qt.Key_Up:
                self.nudge_selected_boxes(0, -nudge_amount)
                return
            if key == Qt.Key_Down:
                self.nudge_selected_boxes(0, nudge_amount)
                return
            if key == Qt.Key_Left:
                self.nudge_selected_boxes(-nudge_amount, 0)
                return
            if key == Qt.Key_Right:
                self.nudge_selected_boxes(nudge_amount, 0)
                return

        # Image navigation (A/D for prev/next, arrows for nudge)
        # Only use A/D for navigation when no boxes are selected
        selected_count = sum(1 for box in self.state.bounding_boxes if box.selected)
        if selected_count == 0:
            if key == Qt.Key_A:
                if self.parent_app:
                    self.parent_app.previous_image()
                return
            if key == Qt.Key_D:
                if self.parent_app:
                    self.parent_app.next_image()
                return

        # Home / End for first/last image
        if key == Qt.Key_Home:
            if self.parent_app:
                self.parent_app.go_to_first_image()
            return
        if key == Qt.Key_End:
            if self.parent_app:
                self.parent_app.go_to_last_image()
            return

        # Save / Reload
        if key == Qt.Key_S:
            if self.parent_app:
                self.parent_app.save_annotations_for_current_image()
            return
        if key == Qt.Key_R:
            if self.parent_app:
                self.parent_app.reload_annotations_for_current_image()
            return

        # Zoom controls (+/- or Ctrl+scroll)
        if key in (Qt.Key_Plus, Qt.Key_Equal):
            self.zoom_in()
            return
        if key in (Qt.Key_Minus, Qt.Key_Underscore):
            self.zoom_out()
            return
        if key == Qt.Key_0:
            self.reset_zoom()
            return

        # Toggle annotation visibility
        if key == Qt.Key_H:
            self.toggle_annotations_visible()
            return

        super().keyPressEvent(event)

    def delete_selected_boxes(self):
        """Delete all selected bounding boxes."""
        bounding_boxes = self.state.bounding_boxes
        # Keep only non-selected boxes
        remaining_boxes = [box for box in bounding_boxes if not box.selected]

        if len(remaining_boxes) != len(bounding_boxes):
            self._push_undo_state()
            self.state = self.state._replace(bounding_boxes=remaining_boxes)
            self.thread.render(self._state_for_render())
            print(f"Deleted {len(bounding_boxes) - len(remaining_boxes)} annotation(s)")

            # Notify parent app about selection change
            if self.parent_app:
                self.parent_app.update_dropdown_for_selection()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)

        if self.pixmap.isNull():
            painter.setPen(Qt.white)
            painter.drawText(
                self.rect(),
                Qt.AlignCenter,
                "No image loaded.\n\nUse the Configure tab to:\n"
                "  • Open a folder of images\n"
                "  • Open a classes file\n\nThen return here to start annotating.",
            )
            return

        # Scale pixmap to fit inside the widget while keeping aspect ratio,
        # and center it within the available space.
        widget_rect = self.rect()
        if widget_rect.width() <= 0 or widget_rect.height() <= 0:
            return

        # Apply zoom transformation
        base_scaled = self.pixmap.scaled(
            widget_rect.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        # Apply zoom to the base scaled size
        zoomed_width = int(base_scaled.width() * self._zoom_level)
        zoomed_height = int(base_scaled.height() * self._zoom_level)

        # Re-scale from original pixmap at zoomed size
        zoomed = self.pixmap.scaled(
            zoomed_width,
            zoomed_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        # Calculate center position with pan offset
        x = widget_rect.left() + (widget_rect.width() - zoomed.width()) // 2 + self._pan_offset[0]
        y = widget_rect.top() + (widget_rect.height() - zoomed.height()) // 2 + self._pan_offset[1]
        target_rect = QRect(x, y, zoomed.width(), zoomed.height())

        # Remember where the image is actually drawn so hit-testing and
        # coordinate mapping can take letterboxing into account.
        self._display_rect = target_rect

        painter.drawPixmap(target_rect, zoomed)

    def updatePixmap(self, image):
        if self._cleanup_done:
            return
        self.pixmap = QPixmap.fromImage(image)
        self.update()

    def cleanup(self):
        """Stop the render thread and disconnect signals. Call before destruction."""
        if self._cleanup_done:
            return
        self._cleanup_done = True
        self.thread.renderedImage.disconnect(self.updatePixmap)
        self.thread.mutex.lock()
        self.thread.abort = True
        self.thread.condition.wakeOne()
        self.thread.mutex.unlock()
        self.thread.wait()

    # --- Undo / Redo helpers -------------------------------------------------

    def _snapshot_boxes(self):
        """Create a deep copy snapshot of current bounding boxes."""
        if not hasattr(self, "state") or not self.state:
            return []
        snapshot = []
        for box in self.state.bounding_boxes:
            snapshot.append(
                BoundingBox(
                    x=box.x,
                    y=box.y,
                    w=box.w,
                    h=box.h,
                    selected=box.selected,
                    class_id=box.class_id,
                    class_name=box.class_name,
                )
            )
        return snapshot

    def _push_undo_state(self):
        """Push current boxes to undo stack and clear redo."""
        if not hasattr(self, "state") or not self.state:
            return
        self.undo_stack.append(self._snapshot_boxes())
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def _restore_boxes(self, boxes):
        """Restore boxes and re-render."""
        self.state = self.state._replace(bounding_boxes=boxes)
        self.thread.render(self._state_for_render())
        if self.parent_app:
            self.parent_app.update_dropdown_for_selection()

    def undo(self):
        """Undo the last change to bounding boxes."""
        if not self.undo_stack:
            print("Nothing to undo")
            return
        current = self._snapshot_boxes()
        previous = self.undo_stack.pop()
        self.redo_stack.append(current)
        self._restore_boxes(previous)
        print("Undid last annotation change")

    def redo(self):
        """Redo the last undone change."""
        if not self.redo_stack:
            print("Nothing to redo")
            return
        current = self._snapshot_boxes()
        next_state = self.redo_stack.pop()
        self.undo_stack.append(current)
        self._restore_boxes(next_state)
        print("Redid last annotation change")

    # --- Clipboard Operations ---

    def copy_selected_boxes(self):
        """Copy selected boxes to internal clipboard."""
        selected = [box for box in self.state.bounding_boxes if box.selected]
        if not selected:
            print("No boxes selected to copy")
            return
        self._clipboard = selected
        print(f"Copied {len(selected)} box(es) to clipboard")

    def paste_boxes(self):
        """Paste boxes from clipboard with offset."""
        if not hasattr(self, '_clipboard') or not self._clipboard:
            print("No boxes in clipboard to paste")
            return

        self._push_undo_state()

        # Paste with offset to avoid exact overlap
        offset = 20
        new_boxes = []
        for box in self._clipboard:
            new_box = BoundingBox(
                x=box.x + offset,
                y=box.y + offset,
                w=box.w,
                h=box.h,
                selected=True,  # Pasted boxes are selected
                class_id=box.class_id,
                class_name=box.class_name,
            )
            new_boxes.append(new_box)

        # Deselect all existing boxes, then add pasted boxes
        for box in self.state.bounding_boxes:
            box.selected = False

        self.state = self.state._replace(
            bounding_boxes=self.state.bounding_boxes + new_boxes
        )
        self.thread.render(self._state_for_render())
        print(f"Pasted {len(new_boxes)} box(es)")

        if self.parent_app:
            self.parent_app.update_dropdown_for_selection()

    def duplicate_selected_boxes(self):
        """Duplicate selected boxes in place."""
        selected = [box for box in self.state.bounding_boxes if box.selected]
        if not selected:
            print("No boxes selected to duplicate")
            return

        self._push_undo_state()

        # Copy to clipboard and paste
        self._clipboard = selected
        self.paste_boxes()

    # --- Selection Operations ---

    def select_all_boxes(self):
        """Select all bounding boxes."""
        count = 0
        for box in self.state.bounding_boxes:
            box.selected = True
            count += 1

        if count > 0:
            self.thread.render(self._state_for_render())
            print(f"Selected all {count} box(es)")
            if self.parent_app:
                self.parent_app.update_dropdown_for_selection()

    # --- Nudge Operations ---

    def nudge_selected_boxes(self, dx: int, dy: int):
        """Move selected boxes by delta pixels."""
        selected = [box for box in self.state.bounding_boxes if box.selected]
        if not selected:
            return

        self._push_undo_state()

        for box in selected:
            box.x = max(0, box.x + dx)
            box.y = max(0, box.y + dy)

        self.thread.render(self._state_for_render())

    # --- Visibility Toggle ---

    def toggle_annotations_visible(self):
        """Toggle visibility of all annotations."""
        if not hasattr(self, '_annotations_visible'):
            self._annotations_visible = True

        self._annotations_visible = not self._annotations_visible

        # Store original boxes and clear/restore based on visibility
        if self._annotations_visible:
            if hasattr(self, '_hidden_boxes'):
                self.state = self.state._replace(bounding_boxes=self._hidden_boxes)
                delattr(self, '_hidden_boxes')
            print("Annotations visible")
        else:
            self._hidden_boxes = list(self.state.bounding_boxes)
            self.state = self.state._replace(bounding_boxes=[])
            print("Annotations hidden")

        self.thread.render(self._state_for_render())

    def _state_for_render(self, image_mouse_x=None, image_mouse_y=None):
        """
        Build a copy of the current state where positional fields are in
        image coordinates, suitable for the render thread.
        """
        s = self.state
        # Use latest mapped mouse position if provided, otherwise map from state
        if image_mouse_x is None or image_mouse_y is None:
            image_mouse_x, image_mouse_y = self._map_to_image_coordinates(
                s.mouse_pos[0], s.mouse_pos[1]
            )

        drag_start_x, drag_start_y = self._map_to_image_coordinates(
            s.drag_start_pos[0], s.drag_start_pos[1]
        )

        return s._replace(
            mouse_pos=[image_mouse_x, image_mouse_y],
            drag_start_pos=[drag_start_x, drag_start_y],
        )

    # --- Zoom and Pan methods -------------------------------------------------

    def zoom_in(self):
        """Zoom in on the image."""
        if self._zoom_level < self._max_zoom:
            self._zoom_level *= self._zoom_step
            self._zoom_level = min(self._zoom_level, self._max_zoom)
            self._notify_zoom_changed()
            self.update()

    def zoom_out(self):
        """Zoom out from the image."""
        if self._zoom_level > self._min_zoom:
            self._zoom_level /= self._zoom_step
            self._zoom_level = max(self._zoom_level, self._min_zoom)
            self._notify_zoom_changed()
            self.update()

    def reset_zoom(self):
        """Reset zoom to 1.0 and center the image."""
        self._zoom_level = 1.0
        self._pan_offset = [0, 0]
        self._notify_zoom_changed()
        self.update()

    def _notify_zoom_changed(self):
        """Notify parent app of zoom level change."""
        if hasattr(self, "zoom_changed") and callable(self.zoom_changed):
            self.zoom_changed(self._zoom_level)

    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        modifiers = event.modifiers()

        # Ctrl + wheel for zoom
        if modifiers & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
            event.accept()
        else:
            super().wheelEvent(event)
