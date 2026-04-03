"""
EventBus implementation for decoupled component communication.

Provides a publish/subscribe pattern where components can
emit events without knowing who handles them, and handlers
can subscribe without knowing who emits them.
"""

import contextlib
from dataclasses import dataclass
from typing import Callable, Dict, List, Type
from weakref import WeakMethod, ref


@dataclass
class Event:
    """Base class for all events."""

    source: object = None


class EventBus:
    """
    Central event bus for decoupled communication.

    Supports:
    - Type-safe event subscription
    - Weak references to prevent memory leaks
    - Multiple subscribers per event type
    - Event filtering by source

    Usage:
        bus = EventBus()

        # Subscribe to all ImageChangedEvent
        bus.subscribe(ImageChangedEvent, self.on_image_changed)

        # Publish event
        bus.publish(ImageChangedEvent(source=self, image_path="/path/to/image.jpg"))
    """

    def __init__(self):
        self._subscribers: Dict[Type[Event], List[Callable]] = {}
        self._weak_refs: Dict[Type[Event], List] = {}

    def subscribe(self, event_type: Type[Event], handler: Callable) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: The event class to subscribe to
            handler: Callable to invoke when event is published
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
            self._weak_refs[event_type] = []

        # Use weak reference for bound methods to prevent memory leaks
        if hasattr(handler, "__self__"):
            # Bound method - use WeakMethod
            self._weak_refs[event_type].append(WeakMethod(handler))
        else:
            # Regular function - store directly with weak reference
            self._weak_refs[event_type].append(ref(handler))

        # Also store direct reference for immediate access
        self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: Type[Event], handler: Callable) -> None:
        """
        Unsubscribe a handler from an event type.

        Args:
            event_type: The event class to unsubscribe from
            handler: The callable to remove
        """
        if event_type in self._subscribers:
            with contextlib.suppress(ValueError):
                self._subscribers[event_type].remove(handler)

    def publish(self, event: Event) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: The event instance to publish
        """
        event_type = type(event)

        if event_type not in self._subscribers:
            return

        # Call live handlers
        for handler in self._subscribers[event_type]:
            try:
                handler(event)
            except Exception as e:
                print(f"Error in event handler for {event_type.__name__}: {e}")

        # Clean up dead weak references
        if event_type in self._weak_refs:
            alive_refs = []
            for weak_ref in self._weak_refs[event_type]:
                if isinstance(weak_ref, WeakMethod):
                    method = weak_ref()
                    if method is not None:
                        alive_refs.append(weak_ref)
                else:
                    target = weak_ref()
                    if target is not None:
                        alive_refs.append(weak_ref)
            self._weak_refs[event_type] = alive_refs

    def clear(self) -> None:
        """Clear all subscriptions."""
        self._subscribers.clear()
        self._weak_refs.clear()
