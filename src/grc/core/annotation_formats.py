"""
Annotation format management for GRC.
Supports multiple annotation formats: YOLO, COCO, GRC JSON.
"""

import os
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .bounding_box import BoundingBox


class AnnotationFormat(ABC):
    """Base class for annotation formats."""

    @abstractmethod
    def load(self, file_path: str, image_width: int, image_height: int) -> List[BoundingBox]:
        """Load annotations from file."""
        pass

    @abstractmethod
    def save(self, file_path: str, bounding_boxes: List[BoundingBox], image_width: int, image_height: int):
        """Save annotations to file."""
        pass

    @abstractmethod
    def get_extension(self) -> str:
        """Get file extension for this format."""
        pass


class YOLOFormat(AnnotationFormat):
    """YOLO format: class_id x y width height"""

    def get_extension(self) -> str:
        return ".txt"

    def load(self, file_path: str, image_width: int, image_height: int) -> List[BoundingBox]:
        """Load YOLO format annotations."""
        bounding_boxes = []

        if not os.path.exists(file_path):
            return bounding_boxes

        try:
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            class_id = int(parts[0])
                            # YOLO format: class_id x_center y_center width height (normalized 0-1)
                            x_center = float(parts[1])
                            y_center = float(parts[2])
                            width = float(parts[3])
                            height = float(parts[4])
                            class_name = parts[5] if len(parts) > 5 else f"Class_{class_id}"

                            # Convert from normalized coordinates to pixel coordinates
                            # YOLO stores CENTER coordinates, need to convert to top-left
                            center_x = x_center * image_width
                            center_y = y_center * image_height
                            pixel_width = width * image_width
                            pixel_height = height * image_height

                            # Convert center to top-left corner
                            x = int(round(center_x - pixel_width / 2.0))
                            y = int(round(center_y - pixel_height / 2.0))
                            w = int(round(pixel_width))
                            h = int(round(pixel_height))

                            # Ensure minimum size and proper bounds
                            x = max(0, min(x, image_width - 1))
                            y = max(0, min(y, image_height - 1))
                            w = max(1, min(w, image_width - x))
                            h = max(1, min(h, image_height - y))

                            box = BoundingBox(
                                x=x, y=y, w=w, h=h,
                                class_id=class_id, class_name=class_name
                            )
                            bounding_boxes.append(box)

                        except (ValueError, IndexError) as e:
                            print(f"Warning: Invalid YOLO annotation format at line {line_num}: {line}")
                            continue

        except Exception as e:
            print(f"Error loading YOLO annotations from {file_path}: {e}")

        return bounding_boxes

    def save(self, file_path: str, bounding_boxes: List[BoundingBox], image_width: int, image_height: int):
        """Save annotations in YOLO format."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'w') as f:
                for box in bounding_boxes:
                    if hasattr(box, 'class_id') and hasattr(box, 'class_name'):
                        # Convert to YOLO format (normalized coordinates)
                        # YOLO format expects: class_id x_center y_center width height
                        # Where coordinates are normalized (0-1) relative to image dimensions
                        # Use higher precision to avoid rounding errors
                        x_center = (box.x + box.w / 2.0) / image_width
                        y_center = (box.y + box.h / 2.0) / image_height
                        width = box.w / image_width
                        height = box.h / image_height

                        # Ensure values are properly bounded
                        x_center = max(0.0, min(1.0, x_center))
                        y_center = max(0.0, min(1.0, y_center))
                        width = max(0.001, min(1.0, width))  # Minimum width to avoid zero
                        height = max(0.001, min(1.0, height))  # Minimum height to avoid zero

                        f.write(f"{box.class_id} {x_center:.8f} {y_center:.8f} {width:.8f} {height:.8f} {box.class_name}\n")

        except Exception as e:
            print(f"Error saving YOLO annotations to {file_path}: {e}")


class COCOFormat(AnnotationFormat):
    """COCO format: JSON with categories and annotations"""

    def get_extension(self) -> str:
        return ".json"

    def load(self, file_path: str, image_width: int, image_height: int) -> List[BoundingBox]:
        """Load COCO format annotations."""
        bounding_boxes = []

        if not os.path.exists(file_path):
            return bounding_boxes

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            # Extract categories mapping
            categories = {}
            if 'categories' in data:
                for cat in data['categories']:
                    categories[cat['id']] = cat['name']

            # Extract annotations
            if 'annotations' in data:
                for ann in data['annotations']:
                    if 'bbox' in ann and len(ann['bbox']) >= 4:
                        x, y, w, h = ann['bbox']
                        category_id = ann.get('category_id', 0)
                        class_name = categories.get(category_id, f"Class_{category_id}")

                        box = BoundingBox(
                            x=int(x), y=int(y), w=int(w), h=int(h),
                            class_id=category_id, class_name=class_name
                        )
                        bounding_boxes.append(box)

        except Exception as e:
            print(f"Error loading COCO annotations from {file_path}: {e}")

        return bounding_boxes

    def save(self, file_path: str, bounding_boxes: List[BoundingBox], image_width: int, image_height: int):
        """Save annotations in COCO format."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Group boxes by class
            categories = {}
            category_id = 1
            for box in bounding_boxes:
                class_name = box.class_name
                if class_name not in categories:
                    categories[class_name] = category_id
                    category_id += 1

            # Create COCO format data
            coco_data = {
                "images": [{"id": 1, "width": image_width, "height": image_height, "file_name": "image.jpg"}],
                "categories": [{"id": cid, "name": name} for name, cid in categories.items()],
                "annotations": []
            }

            annotation_id = 1
            for box in bounding_boxes:
                coco_data["annotations"].append({
                    "id": annotation_id,
                    "image_id": 1,
                    "category_id": categories[box.class_name],
                    "bbox": [box.x, box.y, box.w, box.h],
                    "area": box.w * box.h,
                    "iscrowd": 0
                })
                annotation_id += 1

            with open(file_path, 'w') as f:
                json.dump(coco_data, f, indent=2)

        except Exception as e:
            print(f"Error saving COCO annotations to {file_path}: {e}")


class GRCFormat(AnnotationFormat):
    """GRC native format: JSON with bounding boxes"""

    def get_extension(self) -> str:
        return "-grc.json"

    def load(self, file_path: str, image_width: int, image_height: int) -> List[BoundingBox]:
        """Load GRC format annotations."""
        bounding_boxes = []

        if not os.path.exists(file_path):
            return bounding_boxes

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            if 'bounding_boxes' in data:
                for box_data in data['bounding_boxes']:
                    box = BoundingBox(
                        x=box_data.get('x', 0),
                        y=box_data.get('y', 0),
                        w=box_data.get('w', 0),
                        h=box_data.get('h', 0),
                        class_id=box_data.get('class_id', 0),
                        class_name=box_data.get('class_name', 'Unknown')
                    )
                    bounding_boxes.append(box)

        except Exception as e:
            print(f"Error loading GRC annotations from {file_path}: {e}")

        return bounding_boxes

    def save(self, file_path: str, bounding_boxes: List[BoundingBox], image_width: int, image_height: int):
        """Save annotations in GRC format."""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            grc_data = {
                "image_width": image_width,
                "image_height": image_height,
                "bounding_boxes": []
            }

            for box in bounding_boxes:
                grc_data["bounding_boxes"].append({
                    "x": box.x,
                    "y": box.y,
                    "w": box.w,
                    "h": box.h,
                    "class_id": box.class_id,
                    "class_name": box.class_name
                })

            with open(file_path, 'w') as f:
                json.dump(grc_data, f, indent=2)

        except Exception as e:
            print(f"Error saving GRC annotations to {file_path}: {e}")


class AnnotationFormatManager:
    """Manages different annotation formats and handles format detection."""

    def __init__(self):
        self.formats = {
            'yolo': YOLOFormat(),
            'coco': COCOFormat(),
            'grc': GRCFormat()
        }
        self.default_format = 'grc'

    def set_default_format(self, format_name: str):
        """Set the default annotation format."""
        if format_name in self.formats:
            self.default_format = format_name
        else:
            print(f"Warning: Unknown format '{format_name}'. Using 'grc'.")

    def get_format(self, format_name: str) -> AnnotationFormat:
        """Get a format handler by name."""
        return self.formats.get(format_name, self.formats['grc'])

    def detect_format(self, file_path: str) -> str:
        """Detect annotation format from file path."""
        if file_path.endswith('-grc.json'):
            return 'grc'
        elif file_path.endswith('.json'):
            return 'coco'
        elif file_path.endswith('.txt'):
            return 'yolo'
        else:
            return self.default_format

    def get_annotation_path(self, image_path: str, format_name: str = None) -> str:
        """Get the annotation file path for an image."""
        if format_name is None:
            format_name = self.default_format

        image_name = os.path.splitext(os.path.basename(image_path))[0]
        image_dir = os.path.dirname(image_path)
        annotations_dir = os.path.join(image_dir, "annotations")

        format_handler = self.get_format(format_name)
        extension = format_handler.get_extension()

        return os.path.join(annotations_dir, f"{image_name}{extension}")

    def load_annotations(self, image_path: str, image_width: int, image_height: int, preferred_format: str = None) -> List[BoundingBox]:
        """Load annotations for an image, trying formats with preferred format first."""
        bounding_boxes = []

        # Try preferred format first if specified
        if preferred_format and preferred_format in self.formats:
            annotation_path = self.get_annotation_path(image_path, preferred_format)
            if os.path.exists(annotation_path):
                format_handler = self.get_format(preferred_format)
                bounding_boxes = format_handler.load(annotation_path, image_width, image_height)
                if bounding_boxes:
                    print(f"Loaded {len(bounding_boxes)} annotations from {annotation_path}")
                    return bounding_boxes

        # Try each format in order of preference (excluding already tried preferred format)
        for format_name in ['grc', 'coco', 'yolo']:
            if preferred_format and format_name == preferred_format:
                continue  # Already tried this one
                
            annotation_path = self.get_annotation_path(image_path, format_name)
            if os.path.exists(annotation_path):
                format_handler = self.get_format(format_name)
                bounding_boxes = format_handler.load(annotation_path, image_width, image_height)
                if bounding_boxes:
                    print(f"Loaded {len(bounding_boxes)} annotations from {annotation_path}")
                    break

        return bounding_boxes

    def save_annotations(self, image_path: str, bounding_boxes: List[BoundingBox],
                        image_width: int, image_height: int, format_name: str = None):
        """Save annotations for an image in the specified format."""
        if format_name is None:
            format_name = self.default_format

        annotation_path = self.get_annotation_path(image_path, format_name)
        format_handler = self.get_format(format_name)

        print(f"Saving {len(bounding_boxes)} annotations to {annotation_path}")
        format_handler.save(annotation_path, bounding_boxes, image_width, image_height)
