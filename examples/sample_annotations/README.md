# GRC Annotation Format Examples

This directory contains examples of different annotation formats that GRC can work with.

## Supported Formats

### 1. YOLO Format

Each image has a corresponding `.txt` file with the same name.

Format: `class_id center_x center_y width height`

- All coordinates are normalized (0.0 to 1.0)
- `center_x, center_y` are the center of the bounding box
- `width, height` are the width and height of the bounding box

### 2. COCO Format

JSON format with complete dataset information.

### 3. Pascal VOC Format

XML format with detailed annotation information.

### 4. GRC Native Format

Simple JSON format used internally by GRC.
