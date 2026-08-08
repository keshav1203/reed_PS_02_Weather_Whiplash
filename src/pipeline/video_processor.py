from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import cv2

from .config import PipelineConfig
from .metadata import (
    FileMetadata,
    FrameMetadata,
    extract_video_metadata,
    create_frame_metadata,
)
from .quality import QualityResult, check_quality

logger = logging.getLogger(__name__)

@dataclass
class ProcessedVideoResult:
    """Result of processing a single video."""
    original_path: Path
    processed_path: Path
    metadata: FileMetadata
    frames: List[FrameMetadata] = field(default_factory=list)
    quality_results: List[QualityResult] = field(default_factory=list)

def process_video(
    path: Path,
    sha256: str,
    config: PipelineConfig,
) -> ProcessedVideoResult:
    """
    Process a single video file.
    
    Steps:
    1. Copy original to config.raw_videos_dir / filename
    2. Open with cv2.VideoCapture
    3. Get video_fps from CAP_PROP_FPS
    4. Calculate frame_interval = video_fps / config.sampling_fps
       (extract every Nth frame where N = frame_interval)
    5. Create output directory: config.processed_frames_dir / video_stem
    6. Loop through video:
       - Read each frame
       - If frame_index matches sampling interval, save as frame_NNNNNN.jpg
       - Run quality check on saved frame
       - Create FrameMetadata for frame
    7. Extract video metadata
    8. Set frames_extracted on metadata
    9. Release VideoCapture
    10. Return ProcessedVideoResult
    
    Frame naming: frame_000001.jpg (6-digit zero-padded, 1-indexed)
    Timestamp calculation: frame_index / video_fps
    
    Logging:
    - Log video resolution, FPS, duration
    - Log sampling rate
    - Log number of frames extracted
    """
    logger.info(f"Processing video: {path.name}")
    
    raw_path = config.raw_videos_dir / path.name
    shutil.copy2(path, raw_path)
    
    frames_dir = config.processed_frames_dir / path.stem
    frames_dir.mkdir(parents=True, exist_ok=True)
    
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video {path}")
        
    try:
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        duration = total_frames / video_fps if video_fps > 0 else 0
        logger.info(f"Video resolution: {width}x{height}, FPS: {video_fps:.2f}, Duration: {duration:.2f}s")
        
        if video_fps > 0:
            frame_interval = max(1, round(video_fps / config.sampling_fps))
        else:
            frame_interval = 1
            
        logger.info(f"Sampling rate: {config.sampling_fps} FPS, Frame interval: {frame_interval}")
        
        metadata = extract_video_metadata(path, sha256, str(frames_dir), config)
        
        frames_list = []
        quality_results = []
        
        frame_idx = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_idx % frame_interval == 0:
                saved_count += 1
                frame_filename = f"frame_{saved_count:06d}.jpg"
                frame_path = frames_dir / frame_filename
                
                cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                
                quality_res = check_quality(frame_path, config)
                quality_results.append(quality_res)
                
                timestamp = frame_idx / video_fps if video_fps > 0 else 0
                
                frame_meta = create_frame_metadata(
                    source_meta=metadata,
                    frame_number=saved_count,
                    timestamp=timestamp,
                    image_path=str(frame_path)
                )
                frame_meta.quality = quality_res.to_dict()
                frames_list.append(frame_meta)
                
            frame_idx += 1
            
        metadata.frames_extracted = saved_count
        logger.info(f"Extracted {saved_count} frames")
        
    finally:
        cap.release()
        
    return ProcessedVideoResult(
        original_path=raw_path,
        processed_path=frames_dir,
        metadata=metadata,
        frames=frames_list,
        quality_results=quality_results
    )
