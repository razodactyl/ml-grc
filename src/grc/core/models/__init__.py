"""
Domain models for GRC application.

Models are pure data structures with no dependencies on
UI frameworks or external services.
"""

from .annotation import Annotation
from .session_state import SessionState

__all__ = ["Annotation", "SessionState"]
