from __future__ import annotations
import logging
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Set

from PIL import Image, UnidentifiedImageError
import cv2

from .config import PipelineConfig
from .ingestion import DiscoveredFile

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of file validation."""
    valid: bool
    reason: Optional[str] = None

def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 hash of a file, reading in 8KB chunks."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

class DuplicateTracker:
    """Tracks file hashes to detect duplicates across pipeline runs."""
    
    def __init__(self, registry_path: Path):
        self._registry_path = registry_path
        self._hashes: Set[str] = set()
        self._load()
    
    def is_duplicate(self, file_hash: str) -> bool:
        return file_hash in self._hashes
        
    def register(self, file_hash: str) -> None:
        self._hashes.add(file_hash)
        
    def save(self) -> None:
        """Persist hash registry to disk as JSON."""
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._registry_path, 'w') as f:
            json.dump(list(self._hashes), f)
            
    def _load(self) -> None:
        """Load hash registry from disk if it exists."""
        if self._registry_path.exists():
            try:
                with open(self._registry_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self._hashes = set(data)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load duplicate registry: {e}")

def validate_file(discovered_file: DiscoveredFile, config: PipelineConfig) -> ValidationResult:
    """
    Validate a discovered file.
    Checks:
    - File exists
    - File is not zero bytes
    - Extension is supported
    - For images: can be opened by Pillow, has valid dimensions
    - For videos: can be opened by OpenCV, FPS/frame_count/resolution detectable
    Returns ValidationResult(valid=True) or ValidationResult(valid=False, reason='...')
    """
    if not discovered_file.path.exists():
        return ValidationResult(valid=False, reason="File does not exist")
        
    if discovered_file.path.stat().st_size == 0:
        return ValidationResult(valid=False, reason="File is zero bytes")
        
    if discovered_file.file_type == 'unsupported':
        return ValidationResult(valid=False, reason=f"Unsupported extension: {discovered_file.extension}")
        
    if discovered_file.file_type == 'image':
        try:
            with Image.open(discovered_file.path) as img:
                img.load()
                width, height = img.size
                if width <= 0 or height <= 0:
                    return ValidationResult(valid=False, reason="Invalid image dimensions")
        except (UnidentifiedImageError, IOError, Exception) as e:
            return ValidationResult(valid=False, reason=f"Cannot open image: {str(e)}")
            
    elif discovered_file.file_type == 'video':
        try:
            cap = cv2.VideoCapture(str(discovered_file.path))
            if not cap.isOpened():
                return ValidationResult(valid=False, reason="OpenCV cannot open video")
                
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            cap.release()
            
            if fps <= 0:
                return ValidationResult(valid=False, reason="Invalid FPS")
            if frame_count <= 0:
                return ValidationResult(valid=False, reason="Invalid frame count")
            if width <= 0 or height <= 0:
                return ValidationResult(valid=False, reason="Invalid video resolution")
                
        except Exception as e:
            return ValidationResult(valid=False, reason=f"Error validating video: {str(e)}")
            
    return ValidationResult(valid=True)
