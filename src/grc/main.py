"""
Main entry point for GRC application.
"""

import sys
from PyQt5.QtWidgets import QApplication

from .core.app import App


def main():
    """Main entry point for the GRC application."""
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
