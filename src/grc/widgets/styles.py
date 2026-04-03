"""
Modern UI styling for GRC application.

Provides a professional dark theme with accent colors and consistent styling.
"""

MODERN_DARK_THEME = """
/* Global Settings */
QWidget {
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
}

/* Main Window */
QMainWindow {
    background-color: #1a1a2e;
}

/* Central Widget */
QWidget#centralWidget {
    background-color: #1a1a2e;
}

/* Tab Widget */
QTabWidget::pane {
    border: 1px solid #2d2d44;
    background-color: #16213e;
    border-radius: 8px;
    margin-top: -1px;
}

QTabWidget::tab-bar {
    alignment: left;
}

QTabBar::tab {
    background-color: #1a1a2e;
    color: #8892b0;
    border: 1px solid #2d2d44;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 20px;
    margin-right: 2px;
    font-weight: 500;
}

QTabBar::tab:selected {
    background-color: #16213e;
    color: #64ffda;
    border-color: #64ffda;
    border-bottom: 2px solid #64ffda;
}

QTabBar::tab:hover:!selected {
    background-color: #2d2d44;
    color: #ccd6f6;
}

/* Group Boxes */
QGroupBox {
    background-color: #16213e;
    border: 1px solid #2d2d44;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: 600;
    color: #ccd6f6;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    background-color: #16213e;
    color: #64ffda;
}

/* Buttons */
QPushButton {
    background-color: #2d2d44;
    color: #ccd6f6;
    border: 1px solid #3d3d5c;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #3d3d5c;
    border-color: #64ffda;
    color: #64ffda;
}

QPushButton:pressed {
    background-color: #1a1a2e;
}

QPushButton:disabled {
    background-color: #1a1a2e;
    color: #4a4a6a;
    border-color: #2d2d44;
}

/* Primary Action Button */
QPushButton#primaryButton, QPushButton[class="primary"] {
    background-color: #64ffda;
    color: #1a1a2e;
    border: none;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #7dffdd;
}

QPushButton#primaryButton:pressed {
    background-color: #4de6c4;
}

/* Danger Button */
QPushButton#dangerButton, QPushButton[class="danger"] {
    background-color: #ff6b6b;
    color: #1a1a2e;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #ff8787;
}

/* Line Edit / Text Input */
QLineEdit {
    background-color: #0f0f23;
    color: #ccd6f6;
    border: 1px solid #2d2d44;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #64ffda;
    selection-color: #1a1a2e;
}

QLineEdit:focus {
    border-color: #64ffda;
}

QLineEdit:disabled {
    background-color: #1a1a2e;
    color: #4a4a6a;
}

QLineEdit::placeholder {
    color: #4a4a6a;
}

/* List Widget */
QListWidget {
    background-color: #0f0f23;
    color: #ccd6f6;
    border: 1px solid #2d2d44;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}

QListWidget::item {
    padding: 8px 12px;
    border-radius: 4px;
    margin: 2px 0;
}

QListWidget::item:selected {
    background-color: #64ffda;
    color: #1a1a2e;
}

QListWidget::item:hover:!selected {
    background-color: #2d2d44;
}

/* Scroll Bars */
QScrollBar:vertical {
    background-color: #16213e;
    width: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background-color: #3d3d5c;
    border-radius: 6px;
    min-height: 30px;
    margin: 2px;
}

QScrollBar::handle:vertical:hover {
    background-color: #64ffda;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
    background: none;
}

QScrollBar:horizontal {
    background-color: #16213e;
    height: 12px;
    border-radius: 6px;
    margin: 0;
}

QScrollBar::handle:horizontal {
    background-color: #3d3d5c;
    border-radius: 6px;
    min-width: 30px;
    margin: 2px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #64ffda;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0;
    background: none;
}

/* Splitter */
QSplitter::handle {
    background-color: #2d2d44;
}

QSplitter::handle:hover {
    background-color: #64ffda;
}

/* Labels */
QLabel {
    color: #ccd6f6;
    background: transparent;
}

QLabel#heading {
    font-size: 16px;
    font-weight: 600;
    color: #64ffda;
}

QLabel#subheading {
    font-size: 12px;
    color: #8892b0;
}

/* Status Bar */
QStatusBar {
    background-color: #0f0f23;
    color: #8892b0;
    border-top: 1px solid #2d2d44;
    padding: 4px 8px;
}

QStatusBar::item {
    border: none;
}

QStatusBar QLabel {
    color: #8892b0;
    padding: 0 12px;
}

/* Menu Bar */
QMenuBar {
    background-color: #1a1a2e;
    color: #ccd6f6;
    border-bottom: 1px solid #2d2d44;
    padding: 4px;
}

QMenuBar::item {
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #2d2d44;
    color: #64ffda;
}

QMenuBar::item:pressed {
    background-color: #64ffda;
    color: #1a1a2e;
}

/* Menu */
QMenu {
    background-color: #16213e;
    color: #ccd6f6;
    border: 1px solid #2d2d44;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #64ffda;
    color: #1a1a2e;
}

QMenu::separator {
    height: 1px;
    background-color: #2d2d44;
    margin: 4px 8px;
}

/* Progress Bar */
QProgressBar {
    background-color: #0f0f23;
    border: 1px solid #2d2d44;
    border-radius: 6px;
    text-align: center;
    color: #ccd6f6;
    height: 8px;
}

QProgressBar::chunk {
    background-color: #64ffda;
    border-radius: 4px;
}

/* Table Widget */
QTableWidget {
    background-color: #0f0f23;
    color: #ccd6f6;
    border: 1px solid #2d2d44;
    border-radius: 6px;
    gridline-color: #2d2d44;
}

QTableWidget::item {
    padding: 8px;
}

QTableWidget::item:selected {
    background-color: #64ffda;
    color: #1a1a2e;
}

QHeaderView::section {
    background-color: #16213e;
    color: #64ffda;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #2d2d44;
    font-weight: 600;
}

/* Tooltip */
QToolTip {
    background-color: #16213e;
    color: #ccd6f6;
    border: 1px solid #64ffda;
    border-radius: 4px;
    padding: 6px 10px;
}

/* ComboBox */
QComboBox {
    background-color: #0f0f23;
    color: #ccd6f6;
    border: 1px solid #2d2d44;
    border-radius: 6px;
    padding: 8px 12px;
    min-width: 100px;
}

QComboBox:hover {
    border-color: #64ffda;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #64ffda;
    margin-right: 8px;
}

QComboBox QAbstractItemView {
    background-color: #16213e;
    color: #ccd6f6;
    border: 1px solid #2d2d44;
    border-radius: 6px;
    selection-background-color: #64ffda;
    selection-color: #1a1a2e;
}

/* SpinBox */
QSpinBox, QDoubleSpinBox {
    background-color: #0f0f23;
    color: #ccd6f6;
    border: 1px solid #2d2d44;
    border-radius: 6px;
    padding: 8px 12px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #64ffda;
}

/* CheckBox */
QCheckBox {
    color: #ccd6f6;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #2d2d44;
    background-color: #0f0f23;
}

QCheckBox::indicator:checked {
    background-color: #64ffda;
    border-color: #64ffda;
}

QCheckBox::indicator:hover {
    border-color: #64ffda;
}

/* Scroll Area */
QScrollArea {
    background-color: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background-color: transparent;
}

/* Dock Widget */
QDockWidget {
    color: #ccd6f6;
    titlebar-close-icon: none;
    titlebar-normal-icon: none;
}

QDockWidget::title {
    background-color: #16213e;
    padding: 8px;
}

/* Frame */
QFrame {
    border: none;
}

QFrame#panel {
    background-color: #16213e;
    border: 1px solid #2d2d44;
    border-radius: 8px;
}

/* Image Widget Area */
ImageWidget, ImageWidget QWidget {
    background-color: #0f0f23;
}
"""

# Color palette for programmatic use
COLORS = {
    "background": "#1a1a2e",
    "surface": "#16213e",
    "surface_dark": "#0f0f23",
    "border": "#2d2d44",
    "border_light": "#3d3d5c",
    "text": "#ccd6f6",
    "text_muted": "#8892b0",
    "text_disabled": "#4a4a6a",
    "accent": "#64ffda",
    "accent_hover": "#7dffdd",
    "accent_pressed": "#4de6c4",
    "danger": "#ff6b6b",
    "warning": "#ffd93d",
    "success": "#6bcb77",
    "info": "#4d96ff",
}

# Class color palette for annotation visualization
CLASS_COLORS = [
    "#ff6b6b",  # Red
    "#4ecdc4",  # Teal
    "#ffe66d",  # Yellow
    "#95e1d3",  # Mint
    "#f38181",  # Coral
    "#aa96da",  # Purple
    "#fcbad3",  # Pink
    "#a8d8ea",  # Light Blue
    "#ff9a8b",  # Peach
    "#88d8b0",  # Sage
]
