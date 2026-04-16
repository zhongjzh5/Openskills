#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for image-resize skill
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from PIL import Image
import sys

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
import main

def create_test_image(path, size=(1000, 800), format="JPEG"):
    """Create a test image for testing"""
    img = Image.new("RGB", size, color="red")
    img.save(path, format=format)
    return path

def test_format_size():
    """Test size formatting function"""
    assert main.format_size(500) == "500B"
    assert main.format_size(1500) == "1.5KB"
    assert main.format_size(2000000) == "1.9MB"

def test_resize_image_basic():
    """Test basic image resizing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test image
        input_img = temp_path / "test.jpg"
        create_test_image(input_img, (1000, 800))
        
        # Resize image
        output_img = temp_path / "resized.jpg"
        options = {
            "width": 500,
            "height": 400,
            "maintain_aspect_ratio": True,
            "quality": 85,
            "format": "jpeg"
        }
        
        result = main.resize_image(input_img, output_img, options)
        
        assert result["status"] == "success"
        assert output_img.exists()
        
        # Check dimensions
        with Image.open(output_img) as img:
            assert img.size[0] <= 500
            assert img.size[1] <= 400

def test_resize_image_format_conversion():
    """Test image format conversion"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create PNG test image
        input_img = temp_path / "test.png"
        create_test_image(input_img, (800, 600), format="PNG")
        
        # Convert to JPEG
        output_img = temp_path / "converted.jpg"
        options = {
            "width": 600,
            "height": 450,
            "format": "jpeg",
            "quality": 90
        }
        
        result = main.resize_image(input_img, output_img, options)
        
        assert result["status"] == "success"
        assert output_img.exists()
        
        # Verify it's JPEG
        with Image.open(output_img) as img:
            assert img.format == "JPEG"

def test_process_images_batch():
    """Test batch image processing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test images
        input_dir = temp_path / "input"
        input_dir.mkdir()
        
        output_dir = temp_path / "output"
        
        # Create multiple test images
        for i in range(3):
            create_test_image(input_dir / f"test{i}.jpg", (1200, 900))
        
        # Process images
        input_data = {
            "input_dir": str(input_dir),
            "output_dir": str(output_dir),
            "options": {
                "width": 800,
                "height": 600,
                "quality": 85,
                "maintain_aspect_ratio": True
            },
            "file_patterns": ["*.jpg"]
        }
        
        result = main.process_images(input_data)
        
        assert result["status"] == "success"
        assert result["processed"] == 3
        assert result["failed"] == 0
        assert len(list(output_dir.glob("*.jpg"))) == 3

def test_thumbnail_creation():
    """Test thumbnail creation"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test image
        input_img = temp_path / "test.jpg"
        create_test_image(input_img, (1000, 800))
        
        # Create thumbnail
        thumb_path = temp_path / "thumb.jpg"
        success = main.create_thumbnail(input_img, thumb_path, 150)
        
        assert success
        assert thumb_path.exists()
        
        # Check thumbnail size
        with Image.open(thumb_path) as img:
            assert img.size[0] <= 150
            assert img.size[1] <= 150

def test_error_handling():
    """Test error handling for invalid files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create invalid image file
        invalid_img = temp_path / "invalid.jpg"
        invalid_img.write_text("not an image")
        
        output_img = temp_path / "output.jpg"
        options = {"width": 500, "height": 400}
        
        result = main.resize_image(invalid_img, output_img, options)
        
        assert result["status"] == "error"
        assert "error" in result

def test_aspect_ratio_preservation():
    """Test aspect ratio preservation"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test image with 4:3 aspect ratio
        input_img = temp_path / "test.jpg"
        create_test_image(input_img, (1200, 900))  # 4:3 ratio
        
        # Resize with aspect ratio preservation
        output_img = temp_path / "resized.jpg"
        options = {
            "width": 800,
            "height": 800,  # Square target, but should preserve 4:3
            "maintain_aspect_ratio": True,
            "format": "jpeg"
        }
        
        result = main.resize_image(input_img, output_img, options)
        
        assert result["status"] == "success"
        
        # Check that aspect ratio is preserved
        with Image.open(output_img) as img:
            width, height = img.size
            # Should be 800x600 (preserving 4:3 ratio)
            assert width == 800
            assert height == 600

def test_quality_settings():
    """Test quality settings affect file size"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test image
        input_img = temp_path / "test.jpg"
        create_test_image(input_img, (1000, 800))
        
        # Resize with different quality settings
        high_quality = temp_path / "high_quality.jpg"
        low_quality = temp_path / "low_quality.jpg"
        
        options_high = {"width": 800, "height": 600, "quality": 95, "format": "jpeg"}
        options_low = {"width": 800, "height": 600, "quality": 30, "format": "jpeg"}
        
        result_high = main.resize_image(input_img, high_quality, options_high)
        result_low = main.resize_image(input_img, low_quality, options_low)
        
        assert result_high["status"] == "success"
        assert result_low["status"] == "success"
        
        # Higher quality should result in larger file
        assert high_quality.stat().st_size > low_quality.stat().st_size
