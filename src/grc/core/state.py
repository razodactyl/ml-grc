"""
Application state management for GRC.
"""

from collections import namedtuple


State = namedtuple('State', 'mouse_pos drag_start_pos drag_end_pos dragging bounding_boxes selected_class drag_mode drag_box_index drag_handle')


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
        selected_class=0,
        drag_mode=None,  # None, 'move', 'resize'
        drag_box_index=-1,  # Index of box being dragged (-1 if none)
        drag_handle=None  # None, 'nw', 'ne', 'sw', 'se', 'n', 's', 'e', 'w' for resize handles
    )
