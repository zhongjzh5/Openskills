---
name: image-resize
version: 1.0.0
author: zjz
license: MIT
description: Batch image resize, compress and format optimization tool
---

# Skill Overview

`image-resize` is a powerful image processing skill that provides:

1. **Batch Resize**: Resize multiple images to specified dimensions
2. **Smart Compression**: Optimize file size while maintaining quality
3. **Format Conversion**: Convert between image formats (PNG, JPEG, WebP, etc.)
4. **Aspect Ratio Control**: Maintain aspect ratios or use custom dimensions
5. **Quality Settings**: Adjustable compression levels for different use cases

## Use Cases
- Preparing images for web upload
- Reducing storage space for large image collections
- Creating thumbnails for galleries
- Optimizing images for mobile devices
- Batch processing product images

---

# Trigger Conditions

## Keywords
- Primary: `resize`, `compress`, `optimize`, `batch resize`, `image resize`
- Secondary: `thumbnail`, `webp`, `jpeg`, `png`, `image optimization`
- English: `resize images`, `compress photos`, `batch image processing`

## Context Patterns
- When discussing image preparation: "prepare images for upload", "optimize images"
- When mentioning file size: "reduce image size", "make images smaller"
- When talking about formats: "convert to webp", "change image format"

---

# Safety Boundaries

## Prohibited Operations
- Processing system files or protected directories
- Overwriting original files without explicit permission
- Processing copyrighted images without authorization
- Exceeding reasonable memory limits

## Required Permissions
- File read access for input images
- File write access for output directory
- Temporary file creation for processing
- Memory allocation for image processing

## Confirmation Required
- When processing more than 100 images
- When input directory contains system files
- When output directory would overwrite existing files

---

# Interface Definition

## Input Format (JSON)
```json
{
  "input_dir": "path/to/input/directory",
  "output_dir": "path/to/output/directory",
  "options": {
    "width": 800,
    "height": 600,
    "maintain_aspect_ratio": true,
    "quality": 85,
    "format": "jpeg",
    "create_thumbnails": false,
    "thumbnail_size": 150
  },
  "file_patterns": ["*.jpg", "*.png", "*.bmp"]
}
```

## Output Format (JSON)
```json
{
  "status": "success|partial|error",
  "processed": 25,
  "failed": 2,
  "total_size_reduction": "45.2MB",
  "results": [
    {
      "input_file": "image1.jpg",
      "output_file": "image1_resized.jpg",
      "original_size": "2.5MB",
      "new_size": "450KB",
      "status": "success"
    }
  ],
  "errors": [
    {
      "file": "corrupted.jpg",
      "error": "File format not supported"
    }
  ]
}
```

---

# Usage Examples

## Example 1: Basic Resize
```json
Input:
{
  "input_dir": "./photos",
  "output_dir": "./resized",
  "options": {
    "width": 1200,
    "height": 800,
    "maintain_aspect_ratio": true,
    "quality": 90
  }
}

Output:
{
  "status": "success",
  "processed": 15,
  "failed": 0,
  "total_size_reduction": "12.8MB"
}
```

## Example 2: Web Optimization
```json
Input:
{
  "input_dir": "./originals",
  "output_dir": "./web_ready",
  "options": {
    "width": 1920,
    "height": 1080,
    "quality": 75,
    "format": "webp",
    "create_thumbnails": true
  }
}
```

## CLI Usage
```bash
# Basic resize
python scripts/main.py --input ./photos --output ./resized --width 800 --height 600

# Web optimization
python scripts/main.py --input ./originals --output ./web --format webp --quality 75

# Create thumbnails
python scripts/main.py --input ./gallery --output ./thumbs --thumbnail-size 150
```

---

# Installation

```bash
pip install -r requirements.txt
```

Dependencies:
- Pillow >= 9.0.0
- pathlib (built-in)
- json (built-in)

---

# Configuration

## Default Settings
```json
{
  "default_width": 800,
  "default_height": 600,
  "default_quality": 85,
  "default_format": "jpeg",
  "max_file_size_mb": 50,
  "batch_size": 50
}
```

## Supported Formats
- Input: JPEG, PNG, BMP, TIFF, WebP
- Output: JPEG, PNG, WebP

---

# Testing

```bash
python -m pytest tests/
```

## Test Coverage
- Basic resize functionality
- Aspect ratio preservation
- Format conversion
- Error handling
- Batch processing

---

# Performance

## Benchmarks
- Single image (2MB JPEG to 800x600): ~0.2s
- Batch of 100 images: ~15s
- Memory usage: ~50MB for typical batch

## Optimization Tips
- Use appropriate quality settings (75-85 for web)
- Consider WebP format for better compression
- Process in batches for large collections
