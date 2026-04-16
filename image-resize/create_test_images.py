#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create test images for image-resize skill
"""

from PIL import Image
from pathlib import Path
import sys

def create_test_images():
    """Create test images in different formats"""
    test_dir = Path("test_input")
    test_dir.mkdir(exist_ok=True)
    
    # Create a colorful test image
    colors = [
        ("red", (255, 0, 0)),
        ("green", (0, 255, 0)),
        ("blue", (0, 0, 255)),
        ("yellow", (255, 255, 0)),
        ("purple", (255, 0, 255))
    ]
    
    for i, (name, color) in enumerate(colors):
        # Create image with text
        img = Image.new("RGB", (800, 600), color=color)
        
        # Save in different formats
        img.save(test_dir / f"test_{name}.jpg", "JPEG", quality=95)
        img.save(test_dir / f"test_{name}.png", "PNG")
        
        print(f"Created: test_{name}.jpg and test_{name}.png")
    
    # Create a large image for testing compression
    large_img = Image.new("RGB", (2000, 1500), (128, 128, 128))
    large_img.save(test_dir / "large_test.jpg", "JPEG", quality=95)
    print(f"Created: large_test.jpg (2000x1500)")
    
    print(f"\nTest images created in {test_dir.absolute()}")
    print(f"Total files: {len(list(test_dir.glob('*')))}")

if __name__ == "__main__":
    create_test_images()
