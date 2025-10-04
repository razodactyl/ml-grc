# GRC Usage Guide

This guide provides comprehensive examples and tutorials for using GRC effectively.

## Quick Start Examples

### 1. Basic Annotation Workflow

1. **Start GRC**:

   ```bash
   grc
   ```

2. **Load Images**:

   - Go to "Configure" tab
   - Click "Open" in Files section
   - Select directory containing your images

3. **Load Classes**:

   - Click "Open" in Classes section
   - Select your class definition file

4. **Annotate**:
   - Switch to "Annotate" tab
   - Click and drag to create bounding boxes
   - Use Previous/Next buttons to navigate

### 2. Using Sample Data

The `examples/` directory contains sample data to get you started:

```bash
# Copy sample images to your working directory
cp -r examples/sample_images/* data/images/

# Copy sample classes
cp examples/sample_classes.txt data/classes/

# Copy sample annotations for reference
cp -r examples/sample_annotations/* data/annotations/
```

## Configuration Examples

### Custom Class Definitions

Create a custom class file (`my_classes.txt`):

```
0 person
1 car
2 bicycle
3 dog
4 cat
5 tree
6 building
7 sign
8 traffic_light
9 stop_sign
```

### Project Configuration

Create a project configuration file (`project_config.json`):

```json
{
  "project_name": "My Annotation Project",
  "image_directory": "data/images",
  "annotation_directory": "data/annotations",
  "class_file": "data/classes/my_classes.txt",
  "export_format": "yolo",
  "auto_save": true
}
```

## Annotation Formats

### YOLO Format

Each image has a corresponding `.txt` file:

```
# class_id center_x center_y width height (all normalized 0-1)
1 0.5 0.5 0.2 0.3
0 0.3 0.7 0.1 0.2
```

### COCO Format

Complete JSON dataset:

```json
{
  "images": [...],
  "annotations": [...],
  "categories": [...]
}
```

### GRC Native Format

Internal JSON format with metadata:

```json
{
  "images": [
    {
      "filename": "image.jpg",
      "annotations": [
        {
          "class_id": 1,
          "bbox": { "x": 100, "y": 100, "width": 200, "height": 150 }
        }
      ]
    }
  ]
}
```

## Utility Scripts

### Convert Between Formats

Convert YOLO to COCO:

```bash
python scripts/convert_annotations.py \
  --format yolo-to-coco \
  --input data/annotations \
  --output data/coco_annotations.json \
  --classes data/classes/my_classes.txt
```

Convert COCO to YOLO:

```bash
python scripts/convert_annotations.py \
  --format coco-to-yolo \
  --input data/coco_annotations.json \
  --output data/yolo_annotations \
  --classes data/classes/my_classes.txt
```

### Batch Processing

Resize all images:

```bash
python scripts/batch_process.py \
  --resize \
  --input-dir data/raw_images \
  --output-dir data/images \
  --target-size 800 600
```

Validate annotations:

```bash
python scripts/batch_process.py \
  --validate \
  --input-dir data/images \
  --annotation-dir data/annotations
```

Generate dataset report:

```bash
python scripts/batch_process.py \
  --report \
  --input-dir data/images \
  --annotation-dir data/annotations
```

## Best Practices

### 1. File Organization

```
project/
├── images/           # Source images
├── annotations/      # Annotation files
├── classes/          # Class definitions
├── config/           # Configuration files
└── exports/          # Exported datasets
```

### 2. Naming Conventions

- Images: `image_001.jpg`, `image_002.jpg`, ...
- Annotations: `image_001.txt`, `image_002.txt`, ...
- Classes: `classes.txt` or `project_classes.txt`

### 3. Annotation Guidelines

- Ensure bounding boxes are tight around objects
- Use consistent class IDs across all annotations
- Validate annotations regularly
- Keep backup copies of annotation files

### 4. Quality Control

- Review annotations periodically
- Use validation scripts to check format consistency
- Generate reports to monitor annotation progress
- Maintain consistent annotation standards

## Troubleshooting

### Common Issues

1. **Images not loading**:

   - Check file formats (JPG, PNG supported)
   - Verify file permissions
   - Ensure images are not corrupted

2. **Annotations not saving**:

   - Check write permissions on annotation directory
   - Verify disk space availability
   - Ensure proper file naming

3. **Performance issues**:
   - Use smaller image sizes for better performance
   - Close other applications
   - Check available RAM

### Getting Help

- Check the documentation in `docs/`
- Review example files in `examples/`
- Use validation scripts to diagnose issues
- Check log files for error messages
