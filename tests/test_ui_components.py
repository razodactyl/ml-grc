"""
Unit tests for UI components.

Tests the modern UI components including status bar, controls, and styling.
"""

import sys
import unittest

import pytest

sys.path.append("/Users/jonathan/Projects/ml-grc/src")

from grc.widgets.styles import COLORS, MODERN_DARK_THEME


@pytest.mark.skip(reason="Status bar tests require QApplication and GUI environment")
class TestModernStatusBar(unittest.TestCase):
    """Test ModernStatusBar functionality."""

    def test_status_bar_initialization(self):
        """Test that status bar initializes with default values."""
        from grc.widgets.status_bar import ModernStatusBar

        bar = ModernStatusBar()
        self.assertIsNotNone(bar.image_info)
        self.assertIsNotNone(bar.zoom_label)
        self.assertIsNotNone(bar.annotation_count)
        self.assertIsNotNone(bar.position_label)
        self.assertIsNotNone(bar.hints_label)

    def test_update_image_info(self):
        """Test updating image info display."""
        from grc.widgets.status_bar import ModernStatusBar

        bar = ModernStatusBar()
        bar.update_image_info("test.jpg", 5, 10)
        self.assertIn("test.jpg", bar.image_info.text())
        self.assertIn("5", bar.image_info.text())
        self.assertIn("10", bar.image_info.text())

    def test_update_zoom(self):
        """Test updating zoom display."""
        from grc.widgets.status_bar import ModernStatusBar

        bar = ModernStatusBar()
        bar.update_zoom(1.5)
        self.assertIn("150", bar.zoom_label.text())

        bar.update_zoom(0.5)
        self.assertIn("50", bar.zoom_label.text())

    def test_update_annotation_count(self):
        """Test updating annotation count."""
        from grc.widgets.status_bar import ModernStatusBar

        bar = ModernStatusBar()
        bar.update_annotation_count(5)
        self.assertIn("5", bar.annotation_count.text())

    def test_update_position(self):
        """Test updating cursor position."""
        from grc.widgets.status_bar import ModernStatusBar

        bar = ModernStatusBar()
        bar.update_position(100, 200)
        self.assertIn("100", bar.position_label.text())
        self.assertIn("200", bar.position_label.text())

    def test_clear_position(self):
        """Test clearing position display."""
        from grc.widgets.status_bar import ModernStatusBar

        bar = ModernStatusBar()
        bar.update_position(100, 200)
        bar.clear_position()
        self.assertIn("-", bar.position_label.text())


class TestStyles(unittest.TestCase):
    """Test style definitions."""

    def test_dark_theme_exists(self):
        """Test that dark theme stylesheet is defined."""
        self.assertIsInstance(MODERN_DARK_THEME, str)
        self.assertIn("QWidget", MODERN_DARK_THEME)
        self.assertIn("QPushButton", MODERN_DARK_THEME)
        self.assertIn("QTabWidget", MODERN_DARK_THEME)

    def test_colors_defined(self):
        """Test that color palette is defined."""
        self.assertIsInstance(COLORS, dict)
        self.assertIn("background", COLORS)
        self.assertIn("surface", COLORS)
        self.assertIn("accent", COLORS)
        self.assertIn("text", COLORS)

    def test_colors_format(self):
        """Test that colors are in hex format."""
        for name, color in COLORS.items():
            self.assertTrue(color.startswith("#"), f"Color {name} should start with #")
            self.assertEqual(len(color), 7, f"Color {name} should be 7 characters (#RRGGBB)")


class TestDarkThemeStyles(unittest.TestCase):
    """Test that dark theme contains expected styling elements."""

    def test_button_styles(self):
        """Test button styling is present."""
        self.assertIn("QPushButton", MODERN_DARK_THEME)
        self.assertIn("border-radius", MODERN_DARK_THEME)
        self.assertIn("background-color", MODERN_DARK_THEME)

    def test_tab_styles(self):
        """Test tab styling is present."""
        self.assertIn("QTabWidget", MODERN_DARK_THEME)
        self.assertIn("QTabBar::tab", MODERN_DARK_THEME)
        self.assertIn("selected", MODERN_DARK_THEME)

    def test_input_styles(self):
        """Test input field styling is present."""
        self.assertIn("QLineEdit", MODERN_DARK_THEME)
        self.assertIn("QComboBox", MODERN_DARK_THEME)

    def test_list_styles(self):
        """Test list widget styling is present."""
        self.assertIn("QListWidget", MODERN_DARK_THEME)
        self.assertIn("QListWidget::item", MODERN_DARK_THEME)

    def test_scroll_bar_styles(self):
        """Test scroll bar styling is present."""
        self.assertIn("QScrollBar", MODERN_DARK_THEME)

    def test_menu_styles(self):
        """Test menu styling is present."""
        self.assertIn("QMenuBar", MODERN_DARK_THEME)
        self.assertIn("QMenu", MODERN_DARK_THEME)

    def test_status_bar_styles(self):
        """Test status bar styling is present."""
        self.assertIn("QStatusBar", MODERN_DARK_THEME)

    def test_accent_color_used(self):
        """Test that accent color (#64ffda) is used in theme."""
        self.assertIn("#64ffda", MODERN_DARK_THEME)


if __name__ == "__main__":
    unittest.main()
