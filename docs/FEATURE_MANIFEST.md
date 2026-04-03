# GRC Feature Manifest

**Date:** 2026-04-03
**Purpose:** Comprehensive audit of existing functionality and roadmap for future development

---

## Overview

GRC (Glorified Rectangle Creator) is a desktop annotation tool for creating bounding box annotations on images. This manifest catalogs implemented features, identifies gaps, and proposes a prioritized feature roadmap.

---

## Implemented Features

### Core Annotation

| Feature | Status | Description |
|---------|--------|-------------|
| Bounding Box Creation | ✅ Complete | Click-drag to create rectangular annotations |
| Bounding Box Selection | ✅ Complete | Single and multi-select (Ctrl+click) |
| Bounding Box Movement | ✅ Complete | Drag selected boxes to reposition |
| Bounding Box Resize | ✅ Complete | 8-point handle resize (corners + edges) |
| Bounding Box Deletion | ✅ Complete | Delete key removes selected boxes |
| Class Assignment | ✅ Complete | Assign class to new/selected annotations |
| Minimum Size Enforcement | ✅ Complete | Minimum 20px area prevents accidental boxes |

### Navigation & Image Management

| Feature | Status | Description |
|---------|--------|-------------|
| Directory Loading | ✅ Complete | Load all images from a folder |
| Image Navigation | ✅ Complete | Previous/Next buttons + keyboard (←/→, A/D) |
| Image File List | ✅ Complete | Tree view of loaded images |
| Click-to-Select Image | ✅ Complete | Click image in list to load it |
| Supported Formats | ✅ Complete | JPG, JPEG, PNG, BMP, TIFF, WEBP, GIF |

### Zoom & Pan

| Feature | Status | Description |
|---------|--------|-------------|
| Zoom In/Out | ✅ Complete | Buttons, keyboard (+/-), Ctrl+scroll |
| Zoom Reset | ✅ Complete | Keyboard (0) or button |
| Pan Navigation | ✅ Complete | Middle-click drag to pan |
| Zoom Level Display | ✅ Complete | Status bar + button shows current zoom |

### Undo/Redo

| Feature | Status | Description |
|---------|--------|-------------|
| Undo | ✅ Complete | Ctrl+Z to undo last annotation change |
| Redo | ✅ Complete | Ctrl+Y to redo undone changes |
| History Stack | ✅ Complete | Up to 100 history states |

### Class Management

| Feature | Status | Description |
|---------|--------|-------------|
| Class File Loading | ✅ Complete | Load classes from text file |
| Class Selection | ✅ Complete | Dropdown/list to select active class |
| Class Search/Filter | ✅ Complete | Search box to filter classes |
| Class Change for Selected | ✅ Complete | Change class of selected annotations |

### Annotation Formats

| Feature | Status | Description |
|---------|--------|-------------|
| GRC Format (JSON) | ✅ Complete | Native format with full metadata |
| YOLO Format (TXT) | ✅ Complete | Standard YOLO annotation format |
| COCO Format (JSON) | ✅ Complete | COCO-style JSON format |
| Format Selection | ✅ Complete | Switch between annotation formats |
| Format Conflict Handling | ✅ Complete | User dialog when switching formats with existing annotations |

### Batch Operations

| Feature | Status | Description |
|---------|--------|-------------|
| Batch Export | ✅ Complete | Export all annotations to YOLO/COCO |
| Progress Tracking | ✅ Complete | Progress bar during batch export |
| Cancel Batch | ✅ Complete | Cancel ongoing batch operation |

### Statistics & Progress

| Feature | Status | Description |
|---------|--------|-------------|
| Image Count | ✅ Complete | Total images in dataset |
| Annotated Count | ✅ Complete | Images with annotations |
| Annotation Count | ✅ Complete | Total bounding boxes |
| Class Distribution | ✅ Complete | Table showing count per class |
| Progress Bar | ✅ Complete | Visual progress indicator |
| Refresh Statistics | ✅ Complete | Manual refresh button |

### User Interface

| Feature | Status | Description |
|---------|--------|-------------|
| Modern Dark Theme | ✅ Complete | Professional dark UI theme |
| Tabbed Interface | ✅ Complete | Configure tab + Annotate tab |
| Status Bar | ✅ Complete | Shows image info, zoom, annotations, cursor position |
| Keyboard Shortcuts Help | ✅ Complete | Help menu with shortcuts |
| Workflow Help | ✅ Complete | Help menu with workflow guide |
| Format Help | ✅ Complete | Help menu explaining formats |

---

## Missing Features (High Value)

### Annotation Enhancements

| Feature | Status | Priority | Effort | Value | Description |
|---------|--------|----------|--------|-------|-------------|
| **Copy/Paste Annotations** | ✅ Complete | P1 | Low | High | Copy boxes between images (Ctrl+C/V) |
| **Duplicate Annotation** | ✅ Complete | P1 | Low | High | Duplicate selected box (Ctrl+D) |
| **Select All Annotations** | ✅ Complete | P2 | Low | Medium | Ctrl+A to select all boxes |
| **Annotation Labels Toggle** | ✅ Complete | P2 | Low | Medium | Show/hide class labels on boxes (H key) |
| **Annotation Opacity Control** | P3 | Medium | Low | Slider for box fill opacity |
| **Smart Bounding Box** | P3 | High | Medium | AI-assisted box suggestions |

### Navigation Enhancements

| Feature | Status | Priority | Effort | Value | Description |
|---------|--------|----------|--------|-------|-------------|
| **Jump to First/Last Image** | ✅ Complete | P2 | Low | Medium | Home/End keys for first/last image |
| **Go to Image Number** | P2 | Low | Medium | Ctrl+G dialog to jump to specific image |
| **Recent Folders** | P2 | Low | Medium | Remember recently opened folders |
| **Image Thumbnails** | P3 | Medium | Medium | Thumbnail grid view for image selection |
| **Filter by Annotation Status** | P2 | Low | High | Show only annotated/unannotated images |

### Editing Enhancements

| Feature | Status | Priority | Effort | Value | Description |
|---------|--------|----------|--------|-------|-------------|
| **Nudge with Arrow Keys** | ✅ Complete | P1 | Low | High | Move selected boxes with arrow keys (Shift for 10px) |
| **Resize with Keyboard** | P2 | Medium | Medium | Shift+arrows to resize selected box |
| **Aspect Ratio Lock** | P2 | Medium | Medium | Lock box to specific aspect ratio |
| **Snap to Grid** | P3 | Medium | Low | Snap boxes to configurable grid |
| **Box Coordinates Editor** | P2 | Medium | High | Manual entry of x, y, w, h values |

### Quality of Life

| Feature | Status | Priority | Effort | Value | Description |
|---------|--------|----------|--------|-------|-------------|
| **Auto-Save** | ✅ Complete | P1 | Low | High | Auto-save annotations on image change |
| **Auto-Advance After Annotation** | P2 | Low | High | Option to auto-navigate after creating box |
| **Confirm on Unsaved Changes** | ✅ Complete | P1 | Low | High | Warn before losing unsaved annotations |
| **Session Persistence** | P2 | Medium | High | Remember folder, classes, last image on restart |
| **Fullscreen Mode** | P3 | Low | Medium | F11 for distraction-free annotation |

### Visualization

| Feature | Status | Priority | Effort | Value | Description |
|---------|--------|----------|--------|-------|-------------|
| **Annotation Overlay Toggle** | ✅ Complete | P2 | Low | Medium | Show/hide all annotations (H key) |
| **Class Color Coding** | ✅ Complete | P1 | Low | High | Different colors per class |
| **Annotation Transparency** | ✅ Complete | P2 | Low | Medium | Semi-transparent box fills |
| **Crosshair Cursor** | P3 | Low | Low | Crosshair overlay for precise placement |
| **Ruler/Grid Overlay** | P3 | Medium | Low | Show measurement grid |

### Project Management

| Feature | Priority | Effort | Value | Description |
|---------|----------|--------|-------|-------------|
| **Project File** | P2 | Medium | High | Save/load project with all settings |
| **Multiple Class Files** | P3 | Low | Medium | Support multiple class configurations |
| **Annotation Statistics Export** | P3 | Low | Low | Export stats to CSV/JSON |
| **Dataset Split** | P2 | Medium | High | Train/val/test split functionality |

---

## Missing Features (Nice to Have)

### Advanced Annotation

| Feature | Priority | Effort | Value | Description |
|---------|----------|--------|-------|-------------|
| **Polygon Annotation** | P3 | High | Medium | Support polygon/segmentation masks |
| **Keypoint Annotation** | P3 | High | Low | Support keypoint/pose annotation |
| **Oriented Bounding Boxes** | P3 | High | Medium | Rotated rectangles for oriented objects |
| **3D Bounding Boxes** | P4 | Very High | Low | Cuboid annotations for 3D data |

### Collaboration

| Feature | Priority | Effort | Value | Description |
|---------|----------|--------|-------|-------------|
| **Annotation Comments** | P3 | Medium | Low | Add notes/comments to annotations |
| **Review Mode** | P3 | Medium | Medium | Mark annotations as reviewed/flagged |
| **Multi-user Conflict Detection** | P4 | High | Low | Detect conflicting annotations |

### Automation

| Feature | Priority | Effort | Value | Description |
|---------|----------|--------|-------|-------------|
| **Auto-Detection** | P3 | Very High | High | ML model for auto-annotation |
| **Tracking** | P4 | Very High | Medium | Object tracking across video frames |
| **Interpolation** | P3 | High | Medium | Interpolate boxes between frames |

---

## Keyboard Shortcuts Reference

### Current Shortcuts

| Key | Action |
|-----|--------|
| `←` / `→` | Nudge selected boxes (1px, or 10px with Shift) |
| `A` / `D` | Previous/Next image (when no boxes selected) |
| `Home` / `End` | First/Last image |
| `Delete` | Delete selected annotations |
| `Ctrl+Z` | Undo |
| `Ctrl+Y` | Redo |
| `Ctrl+C` | Copy selected annotations |
| `Ctrl+V` | Paste annotations |
| `Ctrl+D` | Duplicate selected annotations |
| `Ctrl+A` | Select all annotations |
| `S` | Save annotations |
| `R` | Reload annotations |
| `+` / `=` | Zoom in |
| `-` / `_` | Zoom out |
| `0` | Reset zoom |
| `H` | Toggle annotation visibility |
| `Ctrl+Scroll` | Zoom in/out |
| `Middle-click drag` | Pan image |

### Proposed Shortcuts

| Key | Action | Priority |
|-----|--------|----------|
| `Ctrl+G` | Go to image number | P2 |
| `Shift+Arrows` | Resize selected box | P2 |
| `F11` | Toggle fullscreen | P3 |
| `Ctrl+S` | Save (alternative to S) | P1 |

---

## Recommended Implementation Order

### Phase 1: Essential Quality of Life (1-2 days)

1. **Copy/Paste Annotations** - Critical for efficient workflow
2. **Nudge with Arrow Keys** - Precise positioning
3. **Auto-Save** - Prevent data loss
4. **Confirm on Unsaved Changes** - Safety net
5. **Class Color Coding** - Visual distinction

### Phase 2: Workflow Efficiency (2-3 days)

1. **Select All Annotations**
2. **Jump to First/Last Image**
3. **Go to Image Number**
4. **Annotation Labels Toggle**
5. **Filter by Annotation Status**
6. **Auto-Advance After Annotation**

### Phase 3: Import/Export (2-3 days)

1. **Import Annotations** (from YOLO/COCO)
2. **Pascal VOC Format Support**
3. **Project File Save/Load**
4. **Dataset Split Functionality**

### Phase 4: Advanced Features (3-5 days)

1. **Box Coordinates Editor**
2. **Aspect Ratio Lock**
3. **Session Persistence**
4. **Recent Folders**
5. **Image Thumbnails**

---

## Metrics

### Current Codebase Statistics

- **Total Lines:** ~3,500 (excluding tests)
- **Widgets:** 8
- **Services:** 3
- **Controllers:** 2
- **Supported Formats:** 3 (GRC, YOLO, COCO)
- **Keyboard Shortcuts:** 13

### Feature Completion

| Category | Implemented | Missing | Completion |
|----------|-------------|---------|------------|
| Core Annotation | 7 | 5 | 58% |
| Navigation | 5 | 5 | 50% |
| Editing | 5 | 5 | 50% |
| Import/Export | 5 | 5 | 50% |
| Quality of Life | 0 | 5 | 0% |
| Visualization | 0 | 5 | 0% |

---

## Conclusion

GRC has a solid foundation for basic annotation workflows. The highest-impact improvements are:

1. **Copy/Paste functionality** - Essential for efficient annotation
2. **Auto-save and unsaved changes warning** - Prevents data loss
3. **Class color coding** - Improves visual feedback
4. **Keyboard-based box manipulation** - Speeds up fine-tuning
5. **Import existing annotations** - Critical for continuing work

These features would bring GRC to parity with mainstream annotation tools while maintaining its lightweight, focused design philosophy.

---

**Document Version:** 1.0
**Last Updated:** 2026-04-03
