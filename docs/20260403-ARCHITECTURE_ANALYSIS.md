# GRC Architecture Analysis Report

**Date:** 2026-04-03
**Author:** Cascade AI Assistant
**Status:** Analysis Complete, Implementation In Progress

---

## Executive Summary

The GRC application has significant architectural issues that impede maintainability, testability, and extensibility. The primary concerns are a **God Object** (`App` class at 882 lines), **tight coupling** between components, and **multiple SOLID principle violations**.

This document outlines the current issues and provides a detailed restructuring plan following MVP (Model-View-Presenter) architecture with a service layer.

---

## Current Architecture Overview

```
src/grc/
├── core/
│   ├── app.py          # 882 lines - God Object ❌
│   ├── annotation_formats.py  # 402 lines - Reasonable
│   ├── bounding_box.py # 198 lines - Data + Rendering mixed ❌
│   └── state.py        # 31 lines - Good ✅
├── widgets/
│   ├── image_widget.py # 794 lines - Too large ❌
│   ├── batch_widget.py # 192 lines
│   ├── class_list_widget.py
│   ├── file_list_widget.py
│   ├── image_controls.py
│   ├── stats_widget.py
│   ├── status_bar.py
│   ├── styles.py
│   └── table_widget.py
└── main.py
```

---

## SOLID Principle Violations

### 1. Single Responsibility Principle (SRP) - **CRITICAL**

**`App` class** (`src/grc/core/app.py:35-882`)
- Handles: UI layout, navigation, file I/O, annotation management, statistics, menus, dialogs, state coordination, image loading, format conversion
- **8+ responsibilities in one class**

**`ImageWidget`** (`src/grc/widgets/image_widget.py:135-794`)
- Handles: Rendering thread management, mouse events, coordinate mapping, zoom/pan, undo/redo, keyboard shortcuts, cursor management
- **7+ responsibilities**

**`BoundingBox`** (`src/grc/core/bounding_box.py:9-198`)
- Mixes data model with rendering logic (`draw()`, `draw_resize_handles()`)
- Violates separation of concerns

### 2. Open/Closed Principle (OCP) - **MODERATE**

**Hard-coded format detection** (`src/grc/core/annotation_formats.py:325-334`)
```python
def detect_format(self, file_path: str) -> str:
    if file_path.endswith("-grc.json"):
        return "grc"
    elif file_path.endswith(".json"):
        return "coco"
    # Adding new formats requires modifying this method
```

**Hard-coded navigation key handling** in `ImageWidget.keyPressEvent` - adding new shortcuts requires modifying the widget.

### 3. Liskov Substitution Principle (LSP) - **MINOR**

No significant violations detected.

### 4. Interface Segregation Principle (ISP) - **MODERATE**

Widgets depend on `parent_app` with no interface contract:
```python
# Multiple widgets do this:
self.parent_app.previous_image()
self.parent_app.next_image()
self.parent_app.save_annotations_for_current_image()
```
No abstraction exists - widgets are forced to depend on the full `App` interface.

### 5. Dependency Inversion Principle (DIP) - **CRITICAL**

**Tight coupling throughout:**
```python
# Widgets directly reference concrete App class
self.parent_app = parent  # No interface/protocol

# App directly instantiates concrete widgets
self.image_panel = ImageWidget(self)
self.file_list = FileListWidget()
```

High-level modules depend on low-level modules with no abstractions.

---

## Code Smells

### God Object
- **`App` class**: 882 lines, 40+ methods
- **`ImageWidget`**: 794 lines, 25+ methods

### Feature Envy
Widgets constantly call parent methods:
- `src/grc/widgets/image_controls.py:107-152` - All click handlers delegate to `parent_app`
- `src/grc/widgets/batch_widget.py:131-158` - Accesses `parent_app.image_files`, `parent_app.format_manager`

### Primitive Obsession
- `src/grc/core/state.py:7-10` - Uses namedtuple with list primitives for positions
- Coordinate tuples `[x, y]` throughout instead of `Point` or `Coordinate` objects

### Long Methods
- `set_annotation_format()`: 128 lines (`src/grc/core/app.py:391-519`)
- `mouseMoveEvent()`: 90+ lines (`src/grc/widgets/image_widget.py:212-302`)
- `mousePressEvent()`: 80+ lines (`src/grc/widgets/image_widget.py:304-390`)

### Inappropriate Intimacy
- Widgets directly modify parent state: `self.parent_app.image_files = files`
- Widgets call parent methods for UI updates: `self.parent_app.update_dropdown_for_selection()`

### Dead Code
- `openFileNamesDialog()` (`src/grc/core/app.py:867-875`) - Marked as "currently unused"

### DRY Violations

**Repeated `hasattr` checks:**
```python
# Appears 20+ times across files
if hasattr(self, "image_panel") and self.image_panel:
if hasattr(self, "parent_app") and self.parent_app:
if hasattr(self.image_panel, "state") and self.image_panel.state:
```

**Similar coordinate mapping logic** in multiple event handlers.

**Duplicated error handling pattern:**
```python
try:
    # ...
except Exception as e:
    print(f"Error in ...: {e}")
```

---

## Coupling Analysis

### Current Coupling (High)

```
┌─────────────────────────────────────────────────────────┐
│                        App                               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │Widgets  │←→│ State   │←→│ Formats │←→│ File I/O│    │
│  └────┬────┘  └─────────┘  └─────────┘  └─────────┘    │
│       │                                                 │
│       └────────── parent_app references ──────────────→ │
└─────────────────────────────────────────────────────────┘
         ↑
         └── Circular dependency via parent_app
```

### Coupling Metrics

| Component | Incoming Dependencies | Outgoing Dependencies |
|-----------|----------------------|----------------------|
| App | 8 widgets | All widgets, core modules |
| ImageWidget | App | App, BoundingBox, State, RenderThread |
| All other widgets | App | App (parent_app) |

---

## Proposed Architecture

### Target Structure

```
src/grc/
├── core/
│   ├── models/
│   │   ├── annotation.py      # BoundingBox data only
│   │   ├── image.py           # Image metadata
│   │   └── session.py         # Session state
│   ├── services/
│   │   ├── annotation_service.py    # Business logic
│   │   ├── image_service.py         # Image operations
│   │   └── export_service.py        # Export operations
│   ├── repositories/
│   │   ├── annotation_repository.py # Data access abstraction
│   │   └── image_repository.py
│   └── events/
│       └── event_bus.py       # Decoupled communication
├── ui/
│   ├── controllers/
│   │   ├── annotation_controller.py
│   │   ├── navigation_controller.py
│   │   └── zoom_controller.py
│   ├── presenters/
│   │   └── main_presenter.py
│   ├── views/
│   │   ├── main_window.py     # Shell only
│   │   ├── image_view.py      # Rendering only
│   │   └── controls_view.py
│   ├── renderers/
│   │   └── bounding_box_renderer.py  # Separated from model
│   └── widgets/               # Dumb UI components
├── infrastructure/
│   ├── formats/
│   │   ├── format_registry.py
│   │   └── plugins/           # Extensible format plugins
│   └── config/
│       └── settings.py
└── main.py
```

### Architecture Pattern: MVP (Model-View-Presenter) with Service Layer

```
┌──────────────────────────────────────────────────────────────┐
│                        View Layer                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ MainWindow  │  │ ImageView   │  │ ControlsView│          │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘          │
│         │                │                │                  │
│         └────────────────┼────────────────┘                  │
│                          │ Events/Signals                    │
│                          ▼                                   │
├──────────────────────────────────────────────────────────────┤
│                     Presenter Layer                           │
│                  ┌───────────────┐                           │
│                  │ MainPresenter │                           │
│                  └───────┬───────┘                           │
│                          │                                    │
├──────────────────────────┼───────────────────────────────────┤
│                      Service Layer                           │
│  ┌─────────────────┐  ┌──┴──────────────┐  ┌─────────────┐ │
│  │AnnotationService│  │  ImageService   │  │ExportService│ │
│  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘ │
│           │                    │                  │         │
├───────────┼────────────────────┼──────────────────┼─────────┤
│                      Repository Layer                        │
│           ┌──────────┴─────────┴──────────────────┘         │
│           │                                                │
│  ┌────────┴────────┐  ┌─────────────────┐                 │
│  │AnnotationRepo   │  │  ImageRepo      │                 │
│  └────────┬────────┘  └────────┬────────┘                 │
│           │                    │                           │
├───────────┼────────────────────┼───────────────────────────┤
│                      Model Layer                             │
│  ┌────────┴────────┐  ┌───────┴────────┐                  │
│  │Annotation       │  │Image           │                  │
│  │(BoundingBox)    │  │(metadata only) │                  │
│  └─────────────────┘  └────────────────┘                  │
└──────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: Extract Services (High Impact, Medium Effort)

1. **Extract `AnnotationService`** from `App`
   - Move: `load_annotations_for_image`, `save_annotations_for_current_image`, `set_annotation_format`
   - Benefits: Testable annotation logic, single responsibility

2. **Extract `ImageService`** from `App`
   - Move: `load_current_image`, `previous_image`, `next_image`, `_get_image_dimensions`
   - Benefits: Navigation logic isolated

3. **Extract `ExportService`** from `App`
   - Move: `_export_annotations`, batch export logic
   - Benefits: Export operations decoupled

### Phase 2: Introduce Event System (High Impact, Low Effort)

1. **Create `EventBus`** with typed events
   ```python
   class EventBus:
       def subscribe(self, event_type: Type[Event], handler: Callable)
       def publish(self, event: Event)
   
   # Events
   class ImageChangedEvent(Event): ...
   class AnnotationAddedEvent(Event): ...
   class ZoomChangedEvent(Event): ...
   ```

2. **Replace `parent_app` calls with event subscriptions**
   - Widgets publish events instead of calling parent methods
   - Controllers subscribe and handle business logic

### Phase 3: Separate Rendering from Models (Medium Impact, Low Effort)

1. **Create `BoundingBoxRenderer`**
   - Move `draw()`, `draw_resize_handles()` from `BoundingBox`
   - `BoundingBox` becomes pure data class

2. **Create `ImageRenderer`**
   - Separate `RenderThread` from `ImageWidget`
   - `ImageWidget` becomes view-only

### Phase 4: Extract Controllers (Medium Impact, Medium Effort)

1. **`NavigationController`**
   - Handle previous/next image logic
   - Manage image index state

2. **`AnnotationController`**
   - Handle box creation, selection, modification
   - Manage annotation state

3. **`ZoomController`**
   - Handle zoom/pan operations
   - Manage viewport state

### Phase 5: Refactor `App` to `MainWindow` (High Impact, High Effort)

1. **Create `MainPresenter`**
   - Orchestrate services and controllers
   - Handle view updates

2. **Slim `MainWindow`**
   - UI layout only
   - Delegate all logic to presenter

---

## Implementation Priority

| Priority | Task | Effort | Impact | Risk |
|----------|------|--------|--------|------|
| 1 | Extract AnnotationService | 2-3 days | High | Low |
| 2 | Extract ImageService | 1-2 days | High | Low |
| 3 | Create EventBus | 1 day | High | Low |
| 4 | Extract BoundingBoxRenderer | 1 day | Medium | Low |
| 5 | Extract NavigationController | 1 day | Medium | Low |
| 6 | Extract AnnotationController | 2 days | Medium | Medium |
| 7 | Create MainPresenter | 2-3 days | High | Medium |
| 8 | Refactor App to MainWindow | 2-3 days | High | Medium |

**Total estimated effort:** 12-16 days

---

## Quick Wins (Immediate Implementation)

1. **Remove dead code**: Delete `openFileNamesDialog()`
2. **Extract constants**: Move magic numbers (20 for minimum box area, 100 for max history) to config
3. **Add type hints**: Many methods lack return type annotations
4. **Extract coordinate mapping**: Create `CoordinateMapper` class
5. **Replace `hasattr` checks**: Use null object pattern or dependency injection

---

## Testing Strategy

Current test coverage appears minimal. Proposed test structure:

```
tests/
├── unit/
│   ├── services/
│   │   ├── test_annotation_service.py
│   │   └── test_image_service.py
│   ├── models/
│   │   └── test_bounding_box.py
│   └── controllers/
│       └── test_navigation_controller.py
├── integration/
│   └── test_annotation_workflow.py
└── ui/
    └── test_image_widget.py  # Qt test framework
```

---

## Expected Outcomes

After full implementation:

- **Reduce coupling** by 70%+ (eliminate parent_app references)
- **Improve testability** by isolating business logic in services
- **Enable extensibility** through proper abstraction layers
- **Reduce App.py** from 882 lines to ~200 lines (UI shell only)
- **Single responsibility** for all classes (each class < 200 lines)
- **Dependency injection** ready for testing and future enhancements

---

## Appendix: File Analysis

### App.py Method Breakdown

| Method | Lines | Responsibility | Target |
|--------|-------|----------------|--------|
| `__init__` | 112 | UI Layout | MainWindow |
| `loadDataDirectory` | 18 | File I/O | ImageService |
| `on_image_selected` | 15 | Navigation | ImageService |
| `previous_image` | 5 | Navigation | NavigationController |
| `next_image` | 5 | Navigation | NavigationController |
| `load_current_image` | 26 | Navigation | ImageService |
| `load_annotations_for_image` | 38 | Annotations | AnnotationService |
| `save_annotations_for_current_image` | 30 | Annotations | AnnotationService |
| `set_annotation_format` | 128 | Annotations | AnnotationService |
| `refresh_statistics` | 26 | Statistics | StatsService |
| `update_classes` | 20 | State | AnnotationService |
| `on_class_changed` | 130 | UI Logic | AnnotationController |
| `_export_annotations` | 60 | Export | ExportService |
| `closeEvent` | 5 | Lifecycle | MainWindow |

### ImageWidget.py Method Breakdown

| Method | Lines | Responsibility | Target |
|--------|-------|----------------|--------|
| `__init__` | 35 | Setup | ImageView |
| `mouseMoveEvent` | 90 | Input | AnnotationController |
| `mousePressEvent` | 80 | Input | AnnotationController |
| `mouseReleaseEvent` | 60 | Input | AnnotationController |
| `keyPressEvent` | 50 | Input | Controllers |
| `paintEvent` | 50 | Rendering | ImageRenderer |
| `_map_to_image_coordinates` | 40 | Coord Mapping | CoordinateMapper |
| `zoom_*` methods | 30 | Zoom | ZoomController |
| `undo/redo` | 20 | History | HistoryManager |

---

**Document Version:** 1.0
**Last Updated:** 2026-04-03
