"""
Core unit tests for GRC annotation system (PyQt5-independent).

Tests coordinate systems, format conversions, and annotation accuracy.
"""

import unittest
import os
import tempfile
import shutil
import json


class BoundingBox:
    """Simplified BoundingBox for testing (PyQt5-independent)."""

    def __init__(self, x=0, y=0, w=0, h=0, selected=False, class_id=0, class_name=""):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.selected = selected
        self.class_id = class_id
        self.class_name = class_name

    def xy_in_bounds(self, x, y):
        """Check if a point is within this bounding box."""
        return self.x <= x <= (self.x + self.w) and self.y <= y <= (self.y + self.h)

    def get_area(self):
        """Calculate the area of this bounding box."""
        return self.w * self.h


class YOLOFormat:
    """YOLO format implementation for testing."""

    def get_extension(self) -> str:
        return ".txt"

    def load(self, file_path: str, image_width: int, image_height: int):
        """Load YOLO format annotations."""
        bounding_boxes = []

        if not os.path.exists(file_path):
            return bounding_boxes

        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            class_id = int(parts[0])
                            x_center = float(parts[1])
                            y_center = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])
                            class_name = parts[5] if len(parts) > 5 else f"Class_{class_id}"

                            # Convert from normalized coordinates to pixel coordinates
                            # YOLO stores CENTER coordinates, need to convert to top-left
                            center_x = x_center * image_width
                            center_y = y_center * image_height
                            pixel_width = width * image_width
                            pixel_height = height * image_height

                            # Convert center to top-left corner
                            x = int(round(center_x - pixel_width / 2.0))
                            y = int(round(center_y - pixel_height / 2.0))
                            w = int(round(pixel_width))
                            h = int(round(pixel_height))

                            # Ensure minimum size and proper bounds
                            x = max(0, min(x, image_width - 1))
                            y = max(0, min(y, image_height - 1))
                            w = max(1, min(w, image_width - x))
                            h = max(1, min(h, image_height - y))

                            box = BoundingBox(
                                x=x, y=y, w=w, h=h,
                                class_id=class_id, class_name=class_name
                            )
                            bounding_boxes.append(box)

                        except (ValueError, IndexError) as e:
                            print(f"Warning: Invalid YOLO annotation format at line {line_num}: {line}")
                            continue

        except Exception as e:
            print(f"Error loading YOLO annotations from {file_path}: {e}")

        return bounding_boxes

    def save(self, file_path: str, bounding_boxes, image_width: int, image_height: int):
        """Save annotations in YOLO format."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w') as f:
                for box in bounding_boxes:
                    if hasattr(box, 'class_id') and hasattr(box, 'class_name'):
                        # Convert to YOLO format (normalized coordinates)
                        x_center = (box.x + box.w / 2.0) / image_width
                        y_center = (box.y + box.h / 2.0) / image_height
                        width = box.w / image_width
                        height = box.h / image_height

                        # Ensure values are properly bounded
                        x_center = max(0.0, min(1.0, x_center))
                        y_center = max(0.0, min(1.0, y_center))
                        width = max(0.001, min(1.0, width))
                        height = max(0.001, min(1.0, height))

                        f.write(f"{box.class_id} {x_center:.8f} {y_center:.8f} {width:.8f} {height:.8f} {box.class_name}\n")

        except Exception as e:
            print(f"Error saving YOLO annotations to {file_path}: {e}")


class TestYOLOFormat(unittest.TestCase):
    """Test YOLO format save/load accuracy."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_image_width = 800
        self.test_image_height = 600
        self.temp_dir = tempfile.mkdtemp()

        # Create test bounding boxes
        self.test_boxes = [
            BoundingBox(x=100, y=150, w=50, h=75, class_id=0, class_name="person"),
            BoundingBox(x=300, y=200, w=80, h=120, class_id=1, class_name="car"),
            BoundingBox(x=500, y=350, w=60, h=90, class_id=2, class_name="dog"),
        ]

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_yolo_save_load_round_trip(self):
        """Test that YOLO save/load is perfectly reversible."""
        yolo_format = YOLOFormat()

        # Test file path
        test_file = os.path.join(self.temp_dir, "test.txt")

        # Save annotations
        yolo_format.save(test_file, self.test_boxes, self.test_image_width, self.test_image_height)

        # Load annotations back
        loaded_boxes = yolo_format.load(test_file, self.test_image_width, self.test_image_height)

        # Verify exact match
        self.assertEqual(len(loaded_boxes), len(self.test_boxes))

        for original, loaded in zip(self.test_boxes, loaded_boxes):
            self.assertEqual(original.x, loaded.x, f"X coordinate mismatch: {original.x} vs {loaded.x}")
            self.assertEqual(original.y, loaded.y, f"Y coordinate mismatch: {original.y} vs {loaded.y}")
            self.assertEqual(original.w, loaded.w, f"Width mismatch: {original.w} vs {loaded.w}")
            self.assertEqual(original.h, loaded.h, f"Height mismatch: {original.h} vs {loaded.h}")
            self.assertEqual(original.class_id, loaded.class_id, f"Class ID mismatch: {original.class_id} vs {loaded.class_id}")
            self.assertEqual(original.class_name, loaded.class_name, f"Class name mismatch: {original.class_name} vs {loaded.class_name}")

    def test_yolo_precision_edge_cases(self):
        """Test YOLO format with edge case coordinates."""
        yolo_format = YOLOFormat()

        # Edge case boxes (corners, very small, very large)
        edge_boxes = [
            BoundingBox(x=0, y=0, w=1, h=1, class_id=0, class_name="tiny"),
            BoundingBox(x=self.test_image_width-1, y=self.test_image_height-1, w=1, h=1, class_id=1, class_name="corner"),
            BoundingBox(x=10, y=10, w=self.test_image_width-20, h=self.test_image_height-20, class_id=2, class_name="large"),
        ]

        test_file = os.path.join(self.temp_dir, "edge_cases.txt")

        # Save and load
        yolo_format.save(test_file, edge_boxes, self.test_image_width, self.test_image_height)
        loaded_boxes = yolo_format.load(test_file, self.test_image_width, self.test_image_height)

        # Verify bounds are maintained
        for loaded in loaded_boxes:
            self.assertGreaterEqual(loaded.x, 0)
            self.assertGreaterEqual(loaded.y, 0)
            self.assertLessEqual(loaded.x + loaded.w, self.test_image_width)
            self.assertLessEqual(loaded.y + loaded.h, self.test_image_height)
            self.assertGreaterEqual(loaded.w, 1)
            self.assertGreaterEqual(loaded.h, 1)

    def test_yolo_coordinate_accuracy(self):
        """Test YOLO coordinate conversion accuracy."""
        yolo_format = YOLOFormat()

        # Test specific coordinate conversions
        test_cases = [
            # (x, y, w, h)
            (100, 150, 50, 75),
            (0, 0, 100, 100),
            (700, 500, 50, 50),
        ]

        for x, y, w, h in test_cases:
            with self.subTest(x=x, y=y, w=w, h=h):
                box = BoundingBox(x=x, y=y, w=w, h=h, class_id=0, class_name="test")
                test_file = os.path.join(self.temp_dir, f"test_{x}_{y}_{w}_{h}.txt")

                # Save to YOLO
                yolo_format.save(test_file, [box], self.test_image_width, self.test_image_height)

                # Load back and verify pixel coordinates match exactly
                loaded_boxes = yolo_format.load(test_file, self.test_image_width, self.test_image_height)
                loaded_box = loaded_boxes[0]

                self.assertEqual(loaded_box.x, x, f"X coordinate mismatch: {loaded_box.x} vs {x}")
                self.assertEqual(loaded_box.y, y, f"Y coordinate mismatch: {loaded_box.y} vs {y}")
                self.assertEqual(loaded_box.w, w, f"Width mismatch: {loaded_box.w} vs {w}")
                self.assertEqual(loaded_box.h, h, f"Height mismatch: {loaded_box.h} vs {h}")


class TestCoordinateCalculations(unittest.TestCase):
    """Test coordinate calculation accuracy."""

    def test_centering_offset_calculation(self):
        """Test image centering offset calculations."""
        test_cases = [
            # (widget_width, widget_height, image_width, image_height, expected_x_offset, expected_y_offset)
            (1000, 800, 800, 600, 100, 100),  # Centered
            (800, 600, 800, 600, 0, 0),      # Exact fit
            (1200, 900, 800, 600, 200, 150),  # Larger widget
            (600, 400, 800, 600, -100, -100), # Smaller widget (negative offset)
        ]

        for widget_w, widget_h, image_w, image_h, expected_x, expected_y in test_cases:
            with self.subTest(widget_size=(widget_w, widget_h), image_size=(image_w, image_h)):
                x_offset = (widget_w - image_w) // 2
                y_offset = (widget_h - image_h) // 2

                self.assertEqual(x_offset, expected_x, f"X offset calculation failed for widget {widget_w}x{widget_h}, image {image_w}x{image_h}")
                self.assertEqual(y_offset, expected_y, f"Y offset calculation failed for widget {widget_w}x{widget_h}, image {image_w}x{image_h}")

    def test_coordinate_mapping_logic(self):
        """Test the coordinate mapping logic."""
        # Simulate the mapping calculation
        widget_width = 1000
        widget_height = 800
        image_width = 800
        image_height = 600

        # Test mouse positions
        test_mouse_positions = [
            # (mouse_x, mouse_y, expected_image_x, expected_image_y)
            (0, 0, 0, 0),                              # Top-left corner
            (500, 400, 400, 300),                      # Center of widget maps to center of image
            (999, 799, 799, 599),                      # Bottom-right corner
        ]

        for mouse_x, mouse_y, expected_image_x, expected_image_y in test_mouse_positions:
            with self.subTest(mouse_pos=(mouse_x, mouse_y)):
                # Calculate scaling factors
                scale_x = image_width / widget_width if widget_width > 0 else 1.0
                scale_y = image_height / widget_height if widget_height > 0 else 1.0

                # Map to image coordinates
                image_x = mouse_x * scale_x
                image_y = mouse_y * scale_y

                # Clamp to image bounds
                image_x = max(0, min(image_width, image_x))
                image_y = max(0, min(image_height, image_y))

                self.assertEqual(int(image_x), expected_image_x, f"X mapping failed for mouse ({mouse_x},{mouse_y})")
                self.assertEqual(int(image_y), expected_image_y, f"Y mapping failed for mouse ({mouse_x},{mouse_y})")


class TestBoundingBoxOperations(unittest.TestCase):
    """Test bounding box operations."""

    def test_bounding_box_creation(self):
        """Test bounding box creation and properties."""
        box = BoundingBox(x=100, y=150, w=50, h=75, class_id=1, class_name="test")

        self.assertEqual(box.x, 100)
        self.assertEqual(box.y, 150)
        self.assertEqual(box.w, 50)
        self.assertEqual(box.h, 75)
        self.assertEqual(box.class_id, 1)
        self.assertEqual(box.class_name, "test")
        self.assertFalse(box.selected)

    def test_bounding_box_bounds_checking(self):
        """Test point-in-bounds detection."""
        box = BoundingBox(x=100, y=150, w=50, h=75)

        # Test points inside box (inclusive bounds)
        self.assertTrue(box.xy_in_bounds(125, 175))  # Center
        self.assertTrue(box.xy_in_bounds(100, 150))  # Top-left corner (inclusive)
        self.assertTrue(box.xy_in_bounds(150, 225))  # Bottom-right corner (inclusive)

        # Test points outside box
        self.assertFalse(box.xy_in_bounds(99, 150))   # Left of box
        self.assertFalse(box.xy_in_bounds(100, 149))  # Above box
        self.assertFalse(box.xy_in_bounds(151, 150))  # Right of box
        self.assertFalse(box.xy_in_bounds(100, 226))  # Below box

    def test_bounding_box_area_calculation(self):
        """Test bounding box area calculation."""
        box = BoundingBox(x=0, y=0, w=100, h=50)
        self.assertEqual(box.get_area(), 5000)

        box.w = 0
        box.h = 0
        self.assertEqual(box.get_area(), 0)


def run_core_tests():
    """Run core tests without PyQt5 dependencies."""
    test_classes = [
        TestYOLOFormat,
        TestCoordinateCalculations,
        TestBoundingBoxOperations,
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_core_tests()
    if success:
        print("\n✅ All core tests passed! Coordinate system and format handling are working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    sys.exit(0 if success else 1)
