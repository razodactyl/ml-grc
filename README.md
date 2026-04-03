# GRC - Glorified Rectangle Creator

A modern PyQt5-based image annotation tool for creating bounding box annotations, designed for machine learning training data preparation with a professional dark theme UI.

![GRC Screenshot](docs/screenshot.png)

## Features

### Modern User Interface
- **Professional Dark Theme**: Carefully crafted dark UI with accent colors for reduced eye strain during long annotation sessions
- **Status Bar**: Real-time display of image info, zoom level, annotation count, and cursor position
- **Keyboard Shortcut Hints**: In-app guidance for efficient workflow
- **Responsive Layout**: Clean, organized workspace with proper spacing and visual hierarchy

### Annotation Capabilities
- **Interactive Image Annotation**: Draw bounding boxes directly on images with mouse interactions
- **Multi-tab Interface**: Separate configuration and annotation workspaces
- **File Management**: Browse and select image directories with support for JPG, JPEG, PNG, BMP, TIFF, WebP, and GIF formats
- **Class Management**: Define and manage object classes for annotations with search/filter
- **Real-time Rendering**: Smooth, threaded rendering with live preview of annotations
- **Zoom and Pan**: Zoom in/out (+/- keys or Ctrl+scroll) and pan (middle-click drag) for detailed annotation
- **Multiple Export Formats**: Export annotations to YOLO, COCO, or native GRC JSON format
- **Batch Processing**: Export all annotations to a chosen format in one operation
- **Annotation Statistics**: Track progress with statistics showing total images, annotated count, and class distribution
- **Undo/Redo**: Full undo/redo support for annotation changes
- **Keyboard Shortcuts**: Efficient workflow with keyboard navigation and actions
- **Cross-platform**: Works on Windows, macOS, and Linux

## Quick Start

### Prerequisites

- Python 3.8 or higher
- [UV](https://docs.astral.sh/uv/) - Fast Python package installer and resolver

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd ml-grc
   ```

2. **Install UV** (if not already installed):

   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Setup environment and install dependencies**:

   ```bash
   make setup
   ```

   Or manually:

   ```bash
   uv venv
   uv pip install -e ".[dev]"
   ```

4. **Run the application**:

   ```bash
   make dev
   ```

   Or:

   ```bash
   uv run python -m grc.main
   ```

### First Steps

1. **Configure your workspace**:

   - Click on the "Configure" tab
   - Use the "Files" section to select a directory containing your images
   - Use the "Classes" section to load or define your object classes

2. **Start annotating**:
   - Switch to the "Annotate" tab
   - The image viewer will display your images
   - Click and drag to create bounding boxes
   - Use the control panel to navigate between images and select classes

## Detailed Usage

### Configuration Tab

#### File Management

- **Open Directory**: Click "Open" in the Files section to select a directory containing your images
- **Supported Formats**: JPG, JPEG, PNG, BMP, TIFF, WebP, GIF
- **File List**: View all available images in a tree structure

#### Class Management

- **Load Classes**: Click "Open" in the Classes section to load class definitions from text files
- **Class Structure**: Each class should be defined with an ID and name

#### Statistics

- **Progress Tracking**: View total images, annotated images, and annotation count
- **Class Distribution**: See breakdown of annotations by class
- **Refresh**: Click "Refresh Statistics" to update progress

#### Batch Processing

- **Batch Export**: Export all annotations to YOLO or COCO format at once
- **Format Selection**: Choose target format from dropdown

### Annotation Tab

#### Image Interaction

- **Drawing Bounding Boxes**:
  - Click and drag to create rectangular annotations
  - Minimum area threshold prevents accidental tiny annotations
- **Selecting Boxes**: Click on existing bounding boxes to select them
- **Visual Feedback**: Selected boxes appear with different opacity

#### Navigation Controls

- **Previous/Next**: Navigate between images in your dataset
- **Class Selection**: Choose the current class for new annotations using the dropdown

### Keyboard Shortcuts

**Navigation:**
- `←` / `A` : Previous image
- `→` / `D` : Next image

**Annotations:**
- `Delete` : Delete selected boxes
- `Ctrl+Z` : Undo last annotation change
- `Ctrl+Y` : Redo last undone change

**Saving:**
- `S` : Save annotations for current image
- `R` : Reload annotations from disk

**Zoom & Pan:**
- `+` / `=` : Zoom in
- `-` / `_` : Zoom out
- `0` : Reset zoom
- `Ctrl+Scroll` : Zoom in/out
- `Middle-click drag` : Pan image

**Mouse Interactions:**
- **Left-click drag** : Create new bounding box
- **Click** : Select existing bounding box
- **Ctrl+Click** : Multi-select bounding boxes
- **Crosshair Cursor** : Indicates annotation mode

## Technical Details

### Architecture

The application uses a multi-threaded architecture for smooth performance:

- **Main Thread**: Handles UI interactions and user input
- **Render Thread**: Manages image rendering and annotation overlays
- **Thread Safety**: Uses mutexes and signals for safe inter-thread communication

### File Structure

```
ml-grc/
├── src/grc/                      # Main package
│   ├── core/                     # Core application logic
│   │   ├── app.py                # Main App class
│   │   ├── state.py              # Application state management
│   │   ├── annotation_formats.py # Format handling (YOLO, COCO, GRC)
│   │   └── bounding_box.py       # BoundingBox data model
│   ├── widgets/                  # UI components
│   │   ├── image_widget.py       # Core image display and annotation logic
│   │   ├── image_controls.py     # Navigation, zoom, and action controls
│   │   ├── table_widget.py       # Tab-based interface layout
│   │   ├── file_list_widget.py   # File browser and management
│   │   ├── class_list_widget.py  # Class definition management
│   │   ├── status_bar.py         # Modern status bar with info display
│   │   ├── styles.py             # Dark theme styling and color palette
│   │   ├── stats_widget.py       # Annotation statistics display
│   │   └── batch_widget.py       # Batch export functionality
│   ├── utils/                    # Utility functions
│   ├── config/                   # Configuration management
│   └── main.py                   # Application entry point
├── tests/                        # Test files
│   ├── test_annotation_system.py # Annotation and format tests
│   ├── test_ui_components.py     # UI component tests
│   └── test_core_system.py       # Core functionality tests
├── pyproject.toml                # Project configuration (UV, Ruff, dependencies)
├── Makefile                      # Development commands
└── README.md                     # This file
```

### Dependencies

- **PyQt5**: GUI framework
- **NumPy**: Numerical operations
- **OpenCV**: Image processing
- **Pillow**: Image handling
- **SciPy**: Scientific computing

### Development Tools

- **[UV](https://docs.astral.sh/uv/)**: Fast Python package installer and resolver
- **[Ruff](https://docs.astral.sh/ruff/)**: Fast Python linter and formatter

## Development

### Available Commands

```bash
make setup    # Create virtual environment and install dependencies
make dev      # Start the GRC application
make lint     # Run Ruff linter to check code
make format   # Run Ruff formatter to format code
make check    # Run both lint and format check
make test     # Run the test suite
make clean    # Remove virtual environment and cache files
```

### Code Quality

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
# Check for issues
make lint

# Auto-format code
make format

# Check formatting without changes
make check
```

Configuration is in `pyproject.toml` under `[tool.ruff]`.

### Running from Source

1. Run `make setup` to install dependencies
2. Run `make dev` to start the application
3. The application will start with a default window size of 1280x800

### Customization

- **Window Size**: Modify the geometry settings in `app.py` (default: 1280x800)
- **Theme Colors**: Edit `src/grc/widgets/styles.py` to customize the color palette
- **Supported Formats**: Update the `allowed_extensions` list in `file_list_widget.py`
- **Minimum Box Size**: Adjust the area threshold in `image_widget.py`

### UI Color Palette

The application uses a carefully selected dark theme with the following key colors:

| Element | Color | Usage |
|---------|-------|-------|
| Background | `#1a1a2e` | Main window background |
| Surface | `#16213e` | Panels, cards, group boxes |
| Surface Dark | `#0f0f23` | Input fields, lists |
| Border | `#2d2d44` | Subtle separators |
| Text | `#ccd6f6` | Primary text color |
| Text Muted | `#8892b0` | Secondary text, labels |
| Accent | `#64ffda` | Highlights, selection, active states |
| Danger | `#ff6b6b` | Destructive actions, warnings |

To customize, edit `src/grc/widgets/styles.py` and modify the `COLORS` dictionary or `MODERN_DARK_THEME` stylesheet.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed via `pip install -r requirements.txt`
2. **Image Not Loading**: Check that the hardcoded image path in `image_widget.py` exists
3. **Performance Issues**: Large images may cause rendering delays; consider resizing images beforehand

### System Requirements

- **RAM**: Minimum 4GB recommended
- **Storage**: Varies based on image dataset size
- **Display**: Minimum 1024x768 resolution

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

See LICENSE file for details.

## Future Enhancements

- Auto-save functionality
- Polygon and segmentation annotation support
- Image filtering and search capabilities
- Collaborative annotation features
- Custom annotation attributes and metadata
- Integration with cloud storage services
