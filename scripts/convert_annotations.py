#!/usr/bin/env python3
"""
Convert annotations between different formats.
"""

import json
import os
import argparse
from pathlib import Path


def yolo_to_coco(yolo_dir, output_file, class_names):
    """Convert YOLO format annotations to COCO format."""
    
    coco_data = {
        "info": {
            "description": "Converted from YOLO format",
            "version": "1.0",
            "year": 2024,
            "contributor": "GRC Converter",
            "date_created": "2024-10-04"
        },
        "licenses": [{"id": 1, "name": "MIT", "url": "https://opensource.org/licenses/MIT"}],
        "images": [],
        "annotations": [],
        "categories": []
    }
    
    # Add categories
    for i, class_name in enumerate(class_names):
        coco_data["categories"].append({
            "id": i,
            "name": class_name,
            "supercategory": "object"
        })
    
    image_id = 1
    annotation_id = 1
    
    # Process each image
    for img_file in Path(yolo_dir).glob("*.jpg"):
        # Get image dimensions (simplified - you'd normally read the actual image)
        width, height = 800, 600  # Default dimensions
        
        # Add image info
        coco_data["images"].append({
            "id": image_id,
            "width": width,
            "height": height,
            "file_name": img_file.name,
            "license": 1,
            "date_captured": "2024-10-04T00:00:00+00:00"
        })
        
        # Read YOLO annotations
        yolo_file = img_file.with_suffix('.txt')
        if yolo_file.exists():
            with open(yolo_file, 'r') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        class_id = int(parts[0])
                        center_x = float(parts[1])
                        center_y = float(parts[2])
                        bbox_width = float(parts[3])
                        bbox_height = float(parts[4])
                        
                        # Convert to COCO format (top-left corner, width, height)
                        x = (center_x - bbox_width / 2) * width
                        y = (center_y - bbox_height / 2) * height
                        w = bbox_width * width
                        h = bbox_height * height
                        
                        coco_data["annotations"].append({
                            "id": annotation_id,
                            "image_id": image_id,
                            "category_id": class_id,
                            "bbox": [x, y, w, h],
                            "area": w * h,
                            "iscrowd": 0
                        })
                        annotation_id += 1
        
        image_id += 1
    
    # Save COCO format
    with open(output_file, 'w') as f:
        json.dump(coco_data, f, indent=2)
    
    print(f"Converted {image_id - 1} images to COCO format: {output_file}")


def coco_to_yolo(coco_file, output_dir, class_names):
    """Convert COCO format annotations to YOLO format."""
    
    with open(coco_file, 'r') as f:
        coco_data = json.load(f)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Create class mapping
    class_id_map = {cat['id']: cat['name'] for cat in coco_data['categories']}
    
    # Group annotations by image
    image_annotations = {}
    for ann in coco_data['annotations']:
        image_id = ann['image_id']
        if image_id not in image_annotations:
            image_annotations[image_id] = []
        image_annotations[image_id].append(ann)
    
    # Process each image
    for img in coco_data['images']:
        image_id = img['id']
        filename = img['file_name']
        width = img['width']
        height = img['height']
        
        # Create YOLO annotation file
        yolo_file = os.path.join(output_dir, os.path.splitext(filename)[0] + '.txt')
        
        with open(yolo_file, 'w') as f:
            if image_id in image_annotations:
                for ann in image_annotations[image_id]:
                    # Convert COCO bbox to YOLO format
                    x, y, w, h = ann['bbox']
                    
                    # Convert to normalized center coordinates
                    center_x = (x + w / 2) / width
                    center_y = (y + h / 2) / height
                    norm_width = w / width
                    norm_height = h / height
                    
                    f.write(f"{ann['category_id']} {center_x:.6f} {center_y:.6f} {norm_width:.6f} {norm_height:.6f}\n")
    
    print(f"Converted COCO annotations to YOLO format in: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Convert annotation formats')
    parser.add_argument('--input', required=True, help='Input file or directory')
    parser.add_argument('--output', required=True, help='Output file or directory')
    parser.add_argument('--format', choices=['yolo-to-coco', 'coco-to-yolo'], required=True)
    parser.add_argument('--classes', help='Class names file (one per line)')
    
    args = parser.parse_args()
    
    # Load class names
    if args.classes:
        with open(args.classes, 'r') as f:
            class_names = [line.strip() for line in f if line.strip()]
    else:
        # Default class names
        class_names = [
            'person', 'car', 'bicycle', 'dog', 'cat', 'tree', 'building',
            'sign', 'traffic_light', 'stop_sign', 'table', 'bookshelf',
            'book', 'chair', 'window', 'bird'
        ]
    
    if args.format == 'yolo-to-coco':
        yolo_to_coco(args.input, args.output, class_names)
    elif args.format == 'coco-to-yolo':
        coco_to_yolo(args.input, args.output, class_names)


if __name__ == "__main__":
    main()
