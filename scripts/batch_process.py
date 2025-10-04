#!/usr/bin/env python3
"""
Batch process images for annotation.
"""

import os
import argparse
from pathlib import Path
from PIL import Image
import json


def resize_images(input_dir, output_dir, target_size=(800, 600), maintain_aspect=True):
    """Resize all images in a directory."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    supported_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    processed_count = 0
    
    for img_file in Path(input_dir).iterdir():
        if img_file.suffix.lower() in supported_formats:
            try:
                with Image.open(img_file) as img:
                    if maintain_aspect:
                        img.thumbnail(target_size, Image.Resampling.LANCZOS)
                    else:
                        img = img.resize(target_size, Image.Resampling.LANCZOS)
                    
                    output_file = Path(output_dir) / img_file.name
                    img.save(output_file)
                    processed_count += 1
                    print(f"Processed: {img_file.name}")
                    
            except Exception as e:
                print(f"Error processing {img_file.name}: {e}")
    
    print(f"Processed {processed_count} images")


def validate_annotations(annotation_dir, image_dir):
    """Validate annotation files against images."""
    
    issues = []
    
    # Check for missing annotation files
    for img_file in Path(image_dir).glob("*.jpg"):
        ann_file = Path(annotation_dir) / f"{img_file.stem}.txt"
        if not ann_file.exists():
            issues.append(f"Missing annotation file: {ann_file.name}")
    
    # Check for orphaned annotation files
    for ann_file in Path(annotation_dir).glob("*.txt"):
        img_file = Path(image_dir) / f"{ann_file.stem}.jpg"
        if not img_file.exists():
            issues.append(f"Orphaned annotation file: {ann_file.name}")
    
    # Validate annotation format
    for ann_file in Path(annotation_dir).glob("*.txt"):
        try:
            with open(ann_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if len(parts) != 5:
                        issues.append(f"{ann_file.name}:{line_num} - Invalid format (expected 5 values)")
                        continue
                    
                    try:
                        class_id = int(parts[0])
                        center_x = float(parts[1])
                        center_y = float(parts[2])
                        width = float(parts[3])
                        height = float(parts[4])
                        
                        if not (0 <= center_x <= 1 and 0 <= center_y <= 1 and 
                               0 <= width <= 1 and 0 <= height <= 1):
                            issues.append(f"{ann_file.name}:{line_num} - Coordinates out of range [0,1]")
                            
                    except ValueError as e:
                        issues.append(f"{ann_file.name}:{line_num} - Invalid number format: {e}")
                        
        except Exception as e:
            issues.append(f"Error reading {ann_file.name}: {e}")
    
    if issues:
        print("Validation Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("All annotations are valid!")


def generate_dataset_report(image_dir, annotation_dir):
    """Generate a dataset statistics report."""
    
    image_count = len(list(Path(image_dir).glob("*.jpg")))
    annotation_count = len(list(Path(annotation_dir).glob("*.txt")))
    
    class_counts = {}
    total_annotations = 0
    
    for ann_file in Path(annotation_dir).glob("*.txt"):
        try:
            with open(ann_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split()
                    if len(parts) >= 5:
                        class_id = int(parts[0])
                        class_counts[class_id] = class_counts.get(class_id, 0) + 1
                        total_annotations += 1
        except Exception as e:
            print(f"Error reading {ann_file.name}: {e}")
    
    print("Dataset Report")
    print("=" * 50)
    print(f"Images: {image_count}")
    print(f"Annotation files: {annotation_count}")
    print(f"Total annotations: {total_annotations}")
    print(f"Average annotations per image: {total_annotations / max(image_count, 1):.2f}")
    print("\nClass distribution:")
    for class_id in sorted(class_counts.keys()):
        count = class_counts[class_id]
        percentage = (count / total_annotations) * 100 if total_annotations > 0 else 0
        print(f"  Class {class_id}: {count} ({percentage:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description='Batch process images and annotations')
    parser.add_argument('--resize', action='store_true', help='Resize images')
    parser.add_argument('--validate', action='store_true', help='Validate annotations')
    parser.add_argument('--report', action='store_true', help='Generate dataset report')
    parser.add_argument('--input-dir', help='Input directory')
    parser.add_argument('--output-dir', help='Output directory')
    parser.add_argument('--annotation-dir', help='Annotation directory')
    parser.add_argument('--target-size', nargs=2, type=int, default=[800, 600], 
                       help='Target size for resizing (width height)')
    
    args = parser.parse_args()
    
    if args.resize:
        if not args.input_dir or not args.output_dir:
            print("Error: --input-dir and --output-dir required for resize operation")
            return
        resize_images(args.input_dir, args.output_dir, tuple(args.target_size))
    
    if args.validate:
        if not args.annotation_dir or not args.input_dir:
            print("Error: --annotation-dir and --input-dir required for validation")
            return
        validate_annotations(args.annotation_dir, args.input_dir)
    
    if args.report:
        if not args.input_dir or not args.annotation_dir:
            print("Error: --input-dir and --annotation-dir required for report")
            return
        generate_dataset_report(args.input_dir, args.annotation_dir)


if __name__ == "__main__":
    main()
