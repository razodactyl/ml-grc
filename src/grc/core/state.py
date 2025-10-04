"""
Application state management for GRC.
"""

from collections import namedtuple


State = namedtuple('State', 'mouse_pos drag_start_pos drag_end_pos dragging bounding_boxes selected_class')


def make_default_state():
    """
    Create a default application state.
    
    Returns:
        State: Default state with initial values
    """
    return State(
        mouse_pos=[0, 0],
        drag_start_pos=[0, 0],
        drag_end_pos=[0, 0],
        dragging=False,
        bounding_boxes=[],
        selected_class=0
    )
