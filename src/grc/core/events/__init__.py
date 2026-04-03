"""
Event system for decoupled component communication.

Provides an EventBus for publish/subscribe pattern,
allowing components to communicate without direct coupling.
"""

from .event_bus import Event, EventBus
from .events import (
    AnnotationAddedEvent,
    AnnotationChangedEvent,
    AnnotationRemovedEvent,
    AnnotationsSavedEvent,
    ClassChangedEvent,
    FormatChangedEvent,
    ImageChangedEvent,
    ImageLoadedEvent,
    NavigationEvent,
    SessionLoadedEvent,
    ZoomChangedEvent,
)

__all__ = [
    "EventBus",
    "Event",
    "ImageChangedEvent",
    "ImageLoadedEvent",
    "AnnotationAddedEvent",
    "AnnotationRemovedEvent",
    "AnnotationChangedEvent",
    "ZoomChangedEvent",
    "ClassChangedEvent",
    "NavigationEvent",
    "FormatChangedEvent",
    "SessionLoadedEvent",
    "AnnotationsSavedEvent",
]
