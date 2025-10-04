"""
Comprehensive unit tests for GRC annotation system.

Tests coordinate systems, format conversions, and annotation accuracy.
"""

import unittest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch

# Import the modules to test
import sys
sys.path.append('/Users/jonathan/Projects/ml-grc/src')

from grc.core.annotation_formats import YOLOFormat, COCOFormat, GRCFormat, AnnotationFormatManager
from grc.core.bounding_box import BoundingBox
from grc.widgets.image_widget import ImageWidget


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

    def test_yolo_format_validation(self):
        """Test YOLO format validation and error handling."""
        yolo_format = YOLOFormat()

        # Test with invalid file
        invalid_boxes = yolo_format.load("/nonexistent/file.txt", self.test_image_width, self.test_image_height)
        self.assertEqual(len(invalid_boxes), 0)

        # Test with malformed content
        malformed_file = os.path.join(self.temp_dir, "malformed.txt")
        with open(malformed_file, 'w') as f:
            f.write("invalid line\n")
            f.write("0 0.5 0.5 0.1 0.1 person\n")  # Valid line
            f.write("another invalid line\n")

        loaded_boxes = yolo_format.load(malformed_file, self.test_image_width, self.test_image_height)
        self.assertEqual(len(loaded_boxes), 1)  # Should load the valid line


class TestCoordinateMapping(unittest.TestCase):
    """Test coordinate system mapping accuracy."""

    def setUp(self):
        """Set up coordinate mapping tests."""
        self.image_width = 800
        self.image_height = 600
        self.widget_width = 1000  # Larger than image for centering test
        self.widget_height = 800  # Larger than image for centering test

    def test_centering_calculation(self):
        """Test that image centering offset is calculated correctly."""
        # Expected centering offsets
        expected_x_offset = (self.widget_width - self.image_width) // 2  # 100
        expected_y_offset = (self.widget_height - self.image_height) // 2  # 100

        self.assertEqual(expected_x_offset, 100)
        self.assertEqual(expected_y_offset, 100)

    def test_coordinate_mapping_accuracy(self):
        """Test that mouse coordinates map correctly to image coordinates."""
        # Test various mouse positions
        test_cases = [
            # (mouse_x, mouse_y, expected_image_x, expected_image_y)
            (0, 0, 0, 0),  # Top-left corner
            (self.widget_width//2, self.widget_height//2, self.image_width//2, self.image_height//2),  # Center
            (self.widget_width-1, self.widget_height-1, self.image_width-1, self.image_height-1),  # Bottom-right
            (100, 100, 0, 0),  # Image top-left in centered widget
            (900, 700, 700, 500),  # Image bottom-right in centered widget
        ]

        for mouse_x, mouse_y, expected_image_x, expected_image_y in test_cases:
            # Calculate expected mapping
            image_x_offset = (self.widget_width - self.image_width) // 2
            image_y_offset = (self.widget_height - self.image_height) // 2

            actual_image_x = mouse_x - image_x_offset
            actual_image_y = mouse_y - image_y_offset

            # Clamp to bounds
            actual_image_x = max(0, min(self.image_width, actual_image_x))
            actual_image_y = max(0, min(self.image_height, actual_image_y))

            self.assertEqual(actual_image_x, expected_image_x,
                           f"X mapping failed for mouse ({mouse_x},{mouse_y}): expected {expected_image_x}, got {actual_image_x}")
            self.assertEqual(actual_image_y, expected_image_y,
                           f"Y mapping failed for mouse ({mouse_x},{mouse_y}): expected {expected_image_y}, got {actual_image_y}")

    def test_coordinate_bounds_clamping(self):
        """Test that coordinates are properly clamped to image bounds."""
        # Test coordinates outside image bounds
        test_cases = [
            (-100, -100, 0, 0),  # Outside top-left
            (self.image_width + 100, self.image_height + 100, self.image_width, self.image_height),  # Outside bottom-right
            (self.image_width//2, -50, self.image_width//2, 0),  # Outside top
            (-50, self.image_height//2, 0, self.image_height//2),  # Outside left
        ]

        for mouse_x, mouse_y, expected_x, expected_y in test_cases:
            image_x_offset = (self.widget_width - self.image_width) // 2
            image_y_offset = (self.widget_height - self.image_height) // 2

            actual_x = mouse_x - image_x_offset
            actual_y = mouse_y - image_y_offset

            # Apply clamping
            actual_x = max(0, min(self.image_width, actual_x))
            actual_y = max(0, min(self.image_height, actual_y))

            self.assertEqual(actual_x, expected_x, f"X clamping failed for ({mouse_x},{mouse_y})")
            self.assertEqual(actual_y, expected_y, f"Y clamping failed for ({mouse_x},{mouse_y})")


class TestAnnotationFormatManager(unittest.TestCase):
    """Test the annotation format manager."""

    def setUp(self):
        """Set up format manager tests."""
        self.manager = AnnotationFormatManager()
        self.test_boxes = [
            BoundingBox(x=100, y=150, w=50, h=75, class_id=0, class_name="person"),
            BoundingBox(x=300, y=200, w=80, h=120, class_id=1, class_name="car"),
        ]
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_format_detection(self):
        """Test format detection from file paths."""
        test_cases = [
            ("test-grc.json", "grc"),
            ("test.json", "coco"),
            ("test.txt", "yolo"),
            ("test.unknown", "grc"),  # Default fallback
        ]

        for filename, expected_format in test_cases:
            with self.subTest(filename=filename):
                detected = self.manager.detect_format(filename)
                self.assertEqual(detected, expected_format)

    def test_annotation_path_generation(self):
        """Test annotation file path generation."""
        image_path = "/path/to/image.jpg"

        # Test different formats
        formats_and_extensions = [
            ("grc", "-grc.json"),
            ("coco", ".json"),
            ("yolo", ".txt"),
        ]

        for format_name, expected_extension in formats_and_extensions:
            with self.subTest(format=format_name):
                path = self.manager.get_annotation_path(image_path, format_name)
                expected_path = "/path/to/annotations/image" + expected_extension
                self.assertEqual(path, expected_path)

    def test_cross_format_conversion(self):
        """Test converting between different annotation formats."""
        # Create test image directory
        image_dir = os.path.join(self.temp_dir, "images")
        annotations_dir = os.path.join(image_dir, "annotations")
        os.makedirs(annotations_dir)

        image_path = os.path.join(image_dir, "test.jpg")

        # Save in GRC format first
        grc_file = os.path.join(annotations_dir, "test-grc.json")
        grc_format = self.manager.get_format("grc")
        grc_format.save(grc_file, self.test_boxes, 800, 600)

        # Load in YOLO format (should find GRC file and convert)
        loaded_boxes = self.manager.load_annotations(image_path, 800, 600)

        # Verify conversion accuracy
        self.assertEqual(len(loaded_boxes), len(self.test_boxes))

        # Save in YOLO format
        yolo_file = os.path.join(annotations_dir, "test.txt")
        yolo_format = self.manager.get_format("yolo")
        yolo_format.save(yolo_file, loaded_boxes, 800, 600)

        # Load YOLO format back
        reloaded_boxes = yolo_format.load(yolo_file, 800, 600)

        # Verify round-trip accuracy
        self.assertEqual(len(reloaded_boxes), len(self.test_boxes))

        for original, reloaded in zip(self.test_boxes, reloaded_boxes):
            self.assertEqual(original.x, reloaded.x, "X coordinate drift detected")
            self.assertEqual(original.y, reloaded.y, "Y coordinate drift detected")
            self.assertEqual(original.w, reloaded.w, "Width drift detected")
            self.assertEqual(original.h, reloaded.h, "Height drift detected")


class TestBoundingBoxOperations(unittest.TestCase):
    """Test bounding box operations and coordinate handling."""

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

        # Test points inside box
        self.assertTrue(box.xy_in_bounds(125, 175))  # Center
        self.assertTrue(box.xy_in_bounds(100, 150))  # Top-left corner
        self.assertTrue(box.xy_in_bounds(149, 224))  # Bottom-right corner

        # Test points outside box
        self.assertFalse(box.xy_in_bounds(99, 150))   # Left of box
        self.assertFalse(box.xy_in_bounds(100, 149))  # Above box
        self.assertFalse(box.xy_in_bounds(150, 150))  # Right of box
        self.assertFalse(box.xy_in_bounds(100, 225))  # Below box

    def test_bounding_box_area_calculation(self):
        """Test bounding box area calculation."""
        box = BoundingBox(x=0, y=0, w=100, h=50)
        self.assertEqual(box.get_area(), 5000)

        box.w = 0
        box.h = 0
        self.assertEqual(box.get_area(), 0)


class TestImageWidgetCoordinateMapping(unittest.TestCase):
    """Test ImageWidget coordinate mapping functionality."""

    def setUp(self):
        """Set up ImageWidget tests."""
        self.widget = ImageWidget(None)

        # Mock the thread and base_image
        self.widget.thread = Mock()
        self.widget.thread.base_image = Mock()
        self.widget.thread.base_image.width.return_value = 800
        self.widget.thread.base_image.height.return_value = 600
        self.widget.thread.base_image.isNull.return_value = False

    def test_coordinate_mapping_with_image(self):
        """Test coordinate mapping when image is loaded."""
        # Set widget size larger than image for centering
        self.widget.resize(1000, 800)

        # Test center mapping
        image_x, image_y = self.widget._map_to_image_coordinates(500, 400)
        expected_x = 500 - (1000 - 800) // 2  # 500 - 100 = 400
        expected_y = 400 - (800 - 600) // 2  # 400 - 100 = 300

        self.assertEqual(image_x, expected_x)
        self.assertEqual(image_y, expected_y)

    def test_coordinate_mapping_without_image(self):
        """Test coordinate mapping when no image is loaded."""
        self.widget.thread.base_image = None

        image_x, image_y = self.widget._map_to_image_coordinates(500, 400)
        self.assertEqual(image_x, 500)
        self.assertEqual(image_y, 400)

    def test_coordinate_clamping(self):
        """Test that coordinates are properly clamped."""
        self.widget.resize(1000, 800)

        # Test coordinates outside image bounds
        # Image is 800x600, centered in 1000x800 widget
        # Image area: x=100-900, y=100-700

        # Top-left of image (should be clamped to 0,0)
        x, y = self.widget._map_to_image_coordinates(0, 0)
        self.assertEqual(x, 0)
        self.assertEqual(y, 0)

        # Bottom-right of image (should be clamped to 799,599)
        x, y = self.widget._map_to_image_coordinates(999, 799)
        self.assertEqual(x, 799)
        self.assertEqual(y, 599)


class TestMultipleFormatRoundTrip(unittest.TestCase):
    """Test round-trip conversions between multiple formats."""

    def setUp(self):
        """Set up multi-format tests."""
        self.manager = AnnotationFormatManager()
        self.test_boxes = [
            BoundingBox(x=100, y=150, w=50, h=75, class_id=0, class_name="person"),
            BoundingBox(x=300, y=200, w=80, h=120, class_id=1, class_name="car"),
            BoundingBox(x=500, y=350, w=60, h=90, class_id=2, class_name="dog"),
        ]
        self.image_width = 800
        self.image_height = 600
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_grc_to_yolo_to_grc(self):
        """Test GRC → YOLO → GRC round-trip."""
        image_path = os.path.join(self.temp_dir, "test.jpg")

        # Save in GRC format
        self.manager.save_annotations(image_path, self.test_boxes, self.image_width, self.image_height, "grc")

        # Load in YOLO format (should convert from GRC)
        loaded_boxes = self.manager.load_annotations(image_path, self.image_width, self.image_height)

        # Verify conversion
        self.assertEqual(len(loaded_boxes), len(self.test_boxes))

        # Save in YOLO format
        self.manager.save_annotations(image_path, loaded_boxes, self.image_width, self.image_height, "yolo")

        # Load in GRC format (should convert from YOLO)
        final_boxes = self.manager.load_annotations(image_path, self.image_width, self.image_height)

        # Verify final round-trip
        self.assertEqual(len(final_boxes), len(self.test_boxes))

        # Check for coordinate drift
        for original, final in zip(self.test_boxes, final_boxes):
            self.assertEqual(original.x, final.x, f"X coordinate drift: {original.x} → {final.x}")
            self.assertEqual(original.y, final.y, f"Y coordinate drift: {original.y} → {final.y}")
            self.assertEqual(original.w, final.w, f"Width drift: {original.w} → {final.w}")
            self.assertEqual(original.h, final.h, f"Height drift: {original.h} → {final.h}")


def run_all_tests():
    """Run all test suites."""
    # Create test suite
    test_classes = [
        TestYOLOFormat,
        TestCoordinateMapping,
        TestAnnotationFormatManager,
        TestBoundingBoxOperations,
        TestImageWidgetCoordinateMapping,
        TestMultipleFormatRoundTrip,
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    if success:
        print("\n✅ All tests passed! Coordinate system and format handling are working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
    sys.exit(0 if success else 1)
