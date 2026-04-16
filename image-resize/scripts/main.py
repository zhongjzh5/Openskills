#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script for image-resize skill
"""

import argparse
import json
import sys
from pathlib import Path
from PIL import Image
import os

def format_size(size_bytes):
    """Format bytes to human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f}KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f}MB"

def get_file_size(file_path):
    """Get file size in bytes"""
    return file_path.stat().st_size

def resize_image(input_path, output_path, options):
    """Resize a single image"""
    try:
        with Image.open(input_path) as img:
            original_size = get_file_size(input_path)
            
            # Get original dimensions
            original_width, original_height = img.size
            
            # Calculate new dimensions
            width = options.get("width", original_width)
            height = options.get("height", original_height)
            maintain_aspect = options.get("maintain_aspect_ratio", True)
            
            if maintain_aspect:
                # Calculate aspect ratio preserving dimensions
                ratio = min(width / original_width, height / original_height)
                new_width = int(original_width * ratio)
                new_height = int(original_height * ratio)
            else:
                new_width = width
                new_height = height
            
            # Resize image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert format if needed
            output_format = options.get("format", "jpeg")
            if output_format.lower() == "jpeg" and img.mode in ("RGBA", "LA", "P"):
                # Convert to RGB for JPEG
                background = Image.new("RGB", resized_img.size, (255, 255, 255))
                if img.mode == "P":
                    resized_img = resized_img.convert("RGBA")
                background.paste(resized_img, mask=resized_img.split()[-1] if resized_img.mode == "RGBA" else None)
                resized_img = background
            
            # Save with quality settings
            quality = options.get("quality", 85)
            save_kwargs = {"quality": quality, "optimize": True}
            
            if output_format.lower() == "png":
                save_kwargs = {"optimize": True}
            
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save image
            resized_img.save(output_path, format=output_format.upper(), **save_kwargs)
            
            new_size = get_file_size(output_path)
            size_reduction = original_size - new_size
            
            return {
                "input_file": str(input_path),
                "output_file": str(output_path),
                "original_size": format_size(original_size),
                "new_size": format_size(new_size),
                "size_reduction": format_size(size_reduction),
                "original_dimensions": f"{original_width}x{original_height}",
                "new_dimensions": f"{new_width}x{new_height}",
                "status": "success"
            }
            
    except Exception as e:
        return {
            "input_file": str(input_path),
            "error": str(e),
            "status": "error"
        }

def create_thumbnail(input_path, output_path, thumbnail_size):
    """Create a thumbnail"""
    try:
        with Image.open(input_path) as img:
            img.thumbnail((thumbnail_size, thumbnail_size), Image.Resampling.LANCZOS)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, "JPEG", quality=85, optimize=True)
            return True
    except Exception:
        return False

def process_images(input_data):
    """Process batch of images"""
    input_dir = Path(input_data["input_dir"])
    output_dir = Path(input_data["output_dir"])
    options = input_data.get("options", {})
    file_patterns = input_data.get("file_patterns", ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"])
    
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    image_files = []
    for pattern in file_patterns:
        image_files.extend(input_dir.glob(pattern))
        image_files.extend(input_dir.glob(pattern.upper()))
    
    results = []
    errors = []
    total_size_reduction = 0
    
    # Process each image
    for img_path in image_files:
        # Generate output filename
        output_filename = f"{img_path.stem}_resized.{options.get('format', 'jpg')}"
        output_path = output_dir / output_filename
        
        # Resize image
        result = resize_image(img_path, output_path, options)
        
        if result["status"] == "success":
            results.append(result)
            # Calculate size reduction
            original_size = img_path.stat().st_size
            new_size = output_path.stat().st_size
            total_size_reduction += (original_size - new_size)
            
            # Create thumbnail if requested
            if options.get("create_thumbnails", False):
                thumb_dir = output_dir / "thumbnails"
                thumb_filename = f"{img_path.stem}_thumb.jpg"
                thumb_path = thumb_dir / thumb_filename
                create_thumbnail(img_path, thumb_path, options.get("thumbnail_size", 150))
        else:
            errors.append(result)
    
    # Determine overall status
    if errors:
        status = "partial" if results else "error"
    else:
        status = "success"
    
    return {
        "status": status,
        "processed": len(results),
        "failed": len(errors),
        "total_size_reduction": format_size(total_size_reduction),
        "results": results,
        "errors": errors
    }

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Image Resize Skill")
    parser.add_argument("--input", help="Input directory")
    parser.add_argument("--output", help="Output directory")
    parser.add_argument("--width", type=int, help="Target width")
    parser.add_argument("--height", type=int, help="Target height")
    parser.add_argument("--quality", type=int, default=85, help="JPEG quality (1-100)")
    parser.add_argument("--format", default="jpeg", help="Output format")
    parser.add_argument("--maintain-aspect", action="store_true", help="Maintain aspect ratio")
    parser.add_argument("--json", help="JSON input file")
    
    args = parser.parse_args()
    
    # Handle JSON input
    if args.json:
        json_path = Path(args.json)
        if not json_path.exists():
            print(f"Error: JSON file {json_path} not found")
            sys.exit(1)
        
        with open(json_path, "r", encoding="utf-8") as f:
            input_data = json.load(f)
    else:
        # Handle CLI arguments
        if not args.input or not args.output:
            print("Error: --input and --output are required when not using --json")
            sys.exit(1)
        
        input_data = {
            "input_dir": args.input,
            "output_dir": args.output,
            "options": {
                "width": args.width or 800,
                "height": args.height or 600,
                "quality": args.quality,
                "format": args.format,
                "maintain_aspect_ratio": args.maintain_aspect or True
            },
            "file_patterns": ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"]
        }
    
    # Validate input directory
    input_dir = Path(input_data["input_dir"])
    if not input_dir.exists():
        print(f"Error: Input directory {input_dir} does not exist")
        sys.exit(1)
    
    # Process images
    result = process_images(input_data)
    
    # Output result
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
