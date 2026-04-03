"""
Modern tab widget for GRC application.

Provides a clean, professional interface with Configure and Annotate tabs.
"""

from PyQt5.QtWidgets import QHBoxLayout, QTabWidget, QVBoxLayout, QWidget


class TableWidget(QWidget):
    """Main tab container with Configure and Annotate workspaces."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("centralWidget")
        self._init_ui()

    def _init_ui(self):
        """Initialize the tab widget UI."""
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(0)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.North)

        # Create tabs
        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabs.addTab(self.tab1, "⚙ Configure")
        self.tabs.addTab(self.tab2, "✏ Annotate")

        # Configure tab: horizontal layout for side-by-side panels
        self.tab1.layout = QHBoxLayout(self.tab1)
        self.tab1.layout.setContentsMargins(8, 8, 8, 8)
        self.tab1.layout.setSpacing(12)

        # Annotate tab: vertical layout for image workspace
        self.tab2.layout = QVBoxLayout(self.tab2)
        self.tab2.layout.setContentsMargins(0, 0, 0, 0)
        self.tab2.layout.setSpacing(0)

        self.layout.addWidget(self.tabs)
