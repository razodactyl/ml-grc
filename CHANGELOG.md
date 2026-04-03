# Changelog

All notable changes to GRC (Glorified Rectangle Creator) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- **UV Package Manager**: Fast Python package installer and resolver for dependency management
- **Ruff Linter/Formatter**: Fast Python linter and formatter for code quality
- **pyproject.toml**: Modern Python project configuration replacing setup.py
- **Makefile targets**: `lint`, `format`, `check` commands for code quality
- **Zoom and Pan Functionality**: Detailed annotation support with zoom in/out (+/-) and pan (middle-click drag)
- **Additional Image Format Support**: BMP, TIFF, WebP, and GIF formats now supported alongside JPG/PNG
- **Annotation Statistics Widget**: Progress tracking showing total images, annotated count, and class distribution
- **Batch Export Widget**: Export all annotations to YOLO or COCO format in one operation
- **Keyboard shortcuts for zoom**: +/- for zoom, 0 to reset, Ctrl+scroll for zoom

### Changed
- Minimum Python version increased to 3.8 for better compatibility with modern tooling
- Installation now uses UV instead of pip directly

### Fixed
- Previous/Next navigation buttons now correctly trigger image navigation
- Class selection dropdown properly updates based on annotation selection
- Directory creation now handles empty paths safely in annotation format savers
- Zoom state is now reset when loading a new image for consistent UX

## [1.0.0] - Initial Release

### Added
- PyQt5-based GUI for image annotation
- Multi-threaded rendering for smooth UI performance
- Bounding box creation, selection, movement, and resizing
- Support for multiple annotation formats (YOLO, COCO, GRC JSON)
- Undo/redo functionality for annotation changes
- Keyboard shortcuts for navigation and annotation
- Class-based annotation with customizable class definitions
- Annotation persistence in GRC native JSON format
