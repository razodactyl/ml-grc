"""
Main entry point for GRC application.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# Add the src directory to the Python path for relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

try:
    from grc.core.app import App
except ImportError:
    # Fallback for relative import when run as module
    from .core.app import App


def main():
    """Main entry point for the GRC application."""
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
