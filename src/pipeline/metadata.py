from __future__ import annotations
import logging
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
from pathlib import Path
import uuid
from datetime import datetime, timezone

from PIL import Image
import cv2

from .config import PipelineConfig

logger = logging.getLogger(__name__)

@dataclass
class FileMetadata:
    """Metadata for a processed file."""
    file_id: str
    filename: str
    file_type: str  # 'image' or 'video'
    extension: str
    sha256: str
    original_path: str
    processed_path: str
    width: int
    height: int
    fps: Optional[float] = None
    frame_count: Optional[int] = None
    duration_seconds: Optional[float] = None
    sampling_fps: Optional[float] = None
    frames_extracted: Optional[int] = None
    created_at: str = ""
    pipeline_version: str = ""
    status: str = "processed"
    quality: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class FrameMetadata:
    """Metadata for an extracted video frame."""
    frame_id: str
    source_file_id: str
    frame_number: int
    timestamp_seconds: float
    image_path: str
    source_video: str
    quality: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def extract_image_metadata(
    path: Path,
    sha256: str,
    processed_path: Path,
    config: PipelineConfig,
) -> FileMetadata:
    """
    Extract metadata from an image file.
    Opens the image with Pillow to get width/height.
    Generates a UUID for file_id.
    Sets created_at to current UTC ISO-8601.
    """
    try:
        with Image.open(path) as img:
            width, height = img.size
    except Exception as e:
        logger.error(f"Error extracting metadata from image {path}: {e}")
        width, height = 0, 0
        
    return FileMetadata(
        file_id=str(uuid.uuid4()),
        filename=path.name,
        file_type="image",
        extension=path.suffix.lower(),
        sha256=sha256,
        original_path=str(path),
        processed_path=str(processed_path),
        width=width,
        height=height,
        created_at=datetime.now(timezone.utc).isoformat(),
        pipeline_version=config.pipeline_version
    )

def extract_video_metadata(
    path: Path,
    sha256: str,
    processed_path: Path,
    config: PipelineConfig,
) -> FileMetadata:
    """
    Extract metadata from a video file.
    Opens with cv2.VideoCapture to get width, height, fps, frame_count.
    Calculates duration_seconds = frame_count / fps.
    Sets sampling_fps from config.
    """
    try:
        cap = cv2.VideoCapture(str(path))
        if cap.isOpened():
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration_seconds = frame_count / fps if fps > 0 else 0.0
            cap.release()
        else:
            raise ValueError("Could not open video.")
    except Exception as e:
        logger.error(f"Error extracting metadata from video {path}: {e}")
        width, height, fps, frame_count, duration_seconds = 0, 0, 0.0, 0, 0.0
        
    return FileMetadata(
        file_id=str(uuid.uuid4()),
        filename=path.name,
        file_type="video",
        extension=path.suffix.lower(),
        sha256=sha256,
        original_path=str(path),
        processed_path=str(processed_path),
        width=width,
        height=height,
        fps=fps,
        frame_count=frame_count,
        duration_seconds=duration_seconds,
        sampling_fps=config.sampling_fps,
        created_at=datetime.now(timezone.utc).isoformat(),
        pipeline_version=config.pipeline_version
    )

def create_frame_metadata(
    source_meta: FileMetadata,
    frame_number: int,
    timestamp: float,
    image_path: Path,
) -> FrameMetadata:
    """
    Create metadata for a single extracted frame.
    Generates a UUID for frame_id.
    """
    return FrameMetadata(
        frame_id=str(uuid.uuid4()),
        source_file_id=source_meta.file_id,
        frame_number=frame_number,
        timestamp_seconds=timestamp,
        image_path=str(image_path),
        source_video=source_meta.filename
    )
