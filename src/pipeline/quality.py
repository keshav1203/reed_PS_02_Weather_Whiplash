from __future__ import annotations
import logging
from dataclasses import dataclass
from pathlib import Path
import cv2
import numpy as np

from .config import PipelineConfig

logger = logging.getLogger(__name__)

@dataclass
class QualityResult:
    """Result of image quality checks."""
    valid: bool
    blur_score: float
    brightness: float
    resolution_valid: bool
    
    def to_dict(self) -> dict:
        return {
            'valid': self.valid,
            'blur_score': round(self.blur_score, 2),
            'brightness': round(self.brightness, 2),
            'resolution_valid': self.resolution_valid,
        }

def check_quality(image_path: Path, config: PipelineConfig) -> QualityResult:
    """
    Perform quality checks on an image.
    
    1. Read image with cv2.imread
    2. Convert to grayscale
    3. Blur score: variance of cv2.Laplacian(gray, cv2.CV_64F)
    4. Brightness: mean of grayscale pixels
    5. Resolution: check width >= min_image_width and height >= min_image_height
    6. valid = blur_score >= blur_threshold AND brightness in [min, max] AND resolution_valid
    """
    img = cv2.imread(str(image_path))
    if img is None:
        logger.error(f"Cannot read image for quality check: {image_path}")
        return QualityResult(valid=False, blur_score=0.0, brightness=0.0, resolution_valid=False)
        
    height, width = img.shape[:2]
    resolution_valid = width >= config.min_image_width and height >= config.min_image_height
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(gray.mean())
    
    valid = bool(
        blur_score >= config.blur_threshold and
        config.brightness_min <= brightness <= config.brightness_max and
        resolution_valid
    )
    
    return QualityResult(
        valid=valid,
        blur_score=blur_score,
        brightness=brightness,
        resolution_valid=bool(resolution_valid)
    )
