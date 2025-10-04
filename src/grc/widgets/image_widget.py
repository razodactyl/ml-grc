import numpy as np
import os

from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMutex, QMutexLocker, QWaitCondition, QPoint
from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtGui import QImage, QPixmap, QPainter, QBrush, QColor, QCursor

from ..core.state import State, make_default_state
from ..core.bounding_box import BoundingBox


class RenderThread(QThread):
    renderedImage = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super(RenderThread, self).__init__(parent)

        self.mutex = QMutex()
        self.state = make_default_state()
        self.condition = QWaitCondition()
        self.restart = False
        self.abort = False

        self.base_image = None
        self.canvas = self.make_canvas(800, 600)

    def __del__(self):
        self.mutex.lock()
        self.abort = True
        self.condition.wakeOne()
        self.mutex.unlock()

        self.wait()

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
        locker = QMutexLocker(self.mutex)

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
        while True:
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
                    painter.setOpacity(0.2)
                    painter.drawRect(
                        state.drag_start_pos[0],
                        state.drag_start_pos[1],
                        state.mouse_pos[0] - state.drag_start_pos[0],
                        state.mouse_pos[1] - state.drag_start_pos[1]
                    )

                for box in state.bounding_boxes:
                    box.draw(painter)

                painter.end()

            if not self.restart:
                self.renderedImage.emit(self.canvas)

            self.mutex.lock()
            if not self.restart:
                self.condition.wait(self.mutex)
            self.restart = False
            self.mutex.unlock()


class ImageWidget(QLabel):
    def __init__(self, parent):
        super(QLabel, self).__init__(parent)
        self.parent_app = parent

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        self.setFocusPolicy(Qt.StrongFocus)  # Enable keyboard focus

        self.thread = RenderThread()
        self.pixmap = QPixmap()
        self.thread.renderedImage.connect(self.updatePixmap)

        self.thread.render()
        # https://stackoverflow.com/questions/7829829/pyqt4-mousemove-event-without-mousepress

        self.state = make_default_state()

        # Don't auto-load any image initially - wait for explicit loading

    def load_image(self, image_path):
        """Load an image from the given path."""
        if os.path.exists(image_path):
            print(f"Loading image: {image_path}")
            self.thread.load_image(image_path)
        else:
            print(f"Image not found: {image_path}")

    def mouseMoveEvent(self, event):
        mouse_x = event.pos().x()
        mouse_y = event.pos().y()

        if self.state.dragging and self.state.drag_mode:
            boxes = self.state.bounding_boxes

            if self.state.drag_mode == 'move' and self.state.drag_box_index >= 0:
                # Handle box movement
                box = boxes[self.state.drag_box_index]
                if box.selected:
                    dx = mouse_x - self.state.drag_start_pos[0]
                    dy = mouse_y - self.state.drag_start_pos[1]

                    # Update box position
                    box.x = max(0, box.x + dx)
                    box.y = max(0, box.y + dy)

                    # Update drag start position for smooth dragging
                    self.state = self.state._replace(drag_start_pos=[mouse_x, mouse_y])

            elif self.state.drag_mode == 'resize' and self.state.drag_box_index >= 0:
                # Handle box resizing
                box = boxes[self.state.drag_box_index]
                if box.selected and self.state.drag_handle:
                    dx = mouse_x - self.state.drag_start_pos[0]
                    dy = mouse_y - self.state.drag_start_pos[1]

                    # Resize based on handle
                    if self.state.drag_handle == 'nw':
                        box.x = max(0, box.x + dx)
                        box.y = max(0, box.y + dy)
                        box.w = max(10, box.w - dx)
                        box.h = max(10, box.h - dy)
                    elif self.state.drag_handle == 'ne':
                        box.y = max(0, box.y + dy)
                        box.w = max(10, box.w + dx)
                        box.h = max(10, box.h - dy)
                    elif self.state.drag_handle == 'sw':
                        box.x = max(0, box.x + dx)
                        box.w = max(10, box.w - dx)
                        box.h = max(10, box.h + dy)
                    elif self.state.drag_handle == 'se':
                        box.w = max(10, box.w + dx)
                        box.h = max(10, box.h + dy)
                    elif self.state.drag_handle == 'n':
                        box.y = max(0, box.y + dy)
                        box.h = max(10, box.h - dy)
                    elif self.state.drag_handle == 's':
                        box.h = max(10, box.h + dy)
                    elif self.state.drag_handle == 'e':
                        box.w = max(10, box.w + dx)
                    elif self.state.drag_handle == 'w':
                        box.x = max(0, box.x + dx)
                        box.w = max(10, box.w - dx)

                    # Update drag start position
                    self.state = self.state._replace(drag_start_pos=[mouse_x, mouse_y])

            self.state = self.state._replace(bounding_boxes=boxes)
            self.thread.render(self.state)
        else:
            # Update cursor based on what's under the mouse
            self.update_cursor(event.pos().x(), event.pos().y())

        self.state = self.state._replace(mouse_pos=[event.pos().x(), event.pos().y()])
        self.thread.render(self.state)

    def mousePressEvent(self, event):
        mouse_x = event.pos().x()
        mouse_y = event.pos().y()

        # event.buttons() => bitmask of ALL buttons - i.e we can perform multi click etc.
        if event.buttons() & Qt.LeftButton:
            boxes = self.state.bounding_boxes

            # Check if Ctrl is pressed for multi-selection
            ctrl_pressed = event.modifiers() & Qt.ControlModifier

            # Check if clicking on resize handles first
            clicked_on_handle = False
            if not ctrl_pressed:
                for i, box in enumerate(boxes):
                    if box.selected:
                        handle = box.get_resize_handle_at_point(mouse_x, mouse_y)
                        if handle:
                            # Start resize operation
                            self.state = self.state._replace(
                                drag_mode='resize',
                                drag_box_index=i,
                                drag_handle=handle,
                                drag_start_pos=[mouse_x, mouse_y],
                                dragging=True
                            )
                            clicked_on_handle = True
                            break

            if not clicked_on_handle:
                # Check for box selection or dragging
                selected_any = False
                for box in boxes:
                    if box.xy_in_bounds(mouse_x, mouse_y):
                        if ctrl_pressed:
                            # Multi-selection mode: toggle selection of clicked box
                            box.selected = not box.selected
                        else:
                            # Single selection mode: select only clicked box, deselect others
                            for b in boxes:
                                b.selected = (b is box)
                        selected_any = True
                        break

                if not selected_any:
                    # Clicking on empty space - deselect all if not Ctrl
                    if not ctrl_pressed:
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
                        drag_mode='move',
                        drag_box_index=boxes.index(selected_boxes[0]) if len(selected_boxes) == 1 else -1,
                        drag_start_pos=[mouse_x, mouse_y],
                        dragging=True
                    )

            self.state = self.state._replace(
                drag_start_pos=[mouse_x, mouse_y],
                dragging=True,
            )

    def mouseReleaseEvent(self, event):
        # event.button() (lack of 's') => button that caused the event.
        if event.button() == Qt.LeftButton:
            if self.state.dragging:
                self.state = self.state._replace(
                    drag_end_pos=[event.pos().x(), event.pos().y()],
                    dragging=False,
                    drag_mode=None,
                    drag_box_index=-1,
                    drag_handle=None
                )

                bounding_boxes = self.state.bounding_boxes

                x1 = self.state.drag_start_pos[0]
                x2 = self.state.drag_end_pos[0]
                y1 = self.state.drag_start_pos[1]
                y2 = self.state.drag_end_pos[1]

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

                # Get current class selection
                class_id = 0
                class_name = "Unknown"
                if self.parent_app and hasattr(self.parent_app, 'image_panel_controls'):
                    current_text = self.parent_app.image_panel_controls.classSelect.currentText()
                    if current_text and ":" in current_text:
                        class_id = int(current_text.split(":")[0])
                        class_name = current_text.split(":", 1)[1].strip()

                box = BoundingBox(x=x, y=y, w=w, h=h, selected=True,
                                class_id=class_id, class_name=class_name)

                if box.get_area() > 20:
                    bounding_boxes.append(box)

                self.state = self.state._replace(
                    bounding_boxes=bounding_boxes
                )

    def update_cursor(self, mouse_x, mouse_y):
        """Update cursor based on what's under the mouse."""
        if not self.state.dragging:
            boxes = self.state.bounding_boxes

            # Check if over resize handles first
            for box in boxes:
                if box.selected:
                    handle = box.get_resize_handle_at_point(mouse_x, mouse_y)
                    if handle:
                        if handle in ['nw', 'se']:
                            self.setCursor(QCursor(Qt.SizeFDiagCursor))  # Diagonal resize
                        elif handle in ['ne', 'sw']:
                            self.setCursor(QCursor(Qt.SizeBDiagCursor))  # Other diagonal resize
                        elif handle in ['n', 's']:
                            self.setCursor(QCursor(Qt.SizeVerCursor))    # Vertical resize
                        elif handle in ['e', 'w']:
                            self.setCursor(QCursor(Qt.SizeHorCursor))    # Horizontal resize
                        return

            # Check if over selected boxes for moving
            for box in boxes:
                if box.selected and box.xy_in_bounds(mouse_x, mouse_y):
                    self.setCursor(QCursor(Qt.SizeAllCursor))  # Move cursor
                    return

            # Default cursor
            self.setCursor(QCursor(Qt.CrossCursor))

    def keyPressEvent(self, event):
        """Handle keyboard events."""
        if event.key() == Qt.Key_Delete:
            self.delete_selected_boxes()
        else:
            super().keyPressEvent(event)

    def delete_selected_boxes(self):
        """Delete all selected bounding boxes."""
        bounding_boxes = self.state.bounding_boxes
        # Keep only non-selected boxes
        remaining_boxes = [box for box in bounding_boxes if not box.selected]
        
        if len(remaining_boxes) != len(bounding_boxes):
            self.state = self.state._replace(bounding_boxes=remaining_boxes)
            self.thread.render(self.state)
            print(f"Deleted {len(bounding_boxes) - len(remaining_boxes)} annotation(s)")
            
            # Notify parent app about selection change
            if self.parent_app:
                self.parent_app.update_dropdown_for_selection()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)

        if self.pixmap.isNull():
            painter.setPen(Qt.white)
            painter.drawText(self.rect(), Qt.AlignCenter, "No image loaded...")
            return

        painter.drawPixmap(QPoint(), self.pixmap)

    def updatePixmap(self, image):
        self.pixmap = QPixmap.fromImage(image)
        self.update()
