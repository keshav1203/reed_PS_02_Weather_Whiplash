from __future__ import annotations
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List

from .config import PipelineConfig

logger = logging.getLogger(__name__)

@dataclass
class DiscoveredFile:
    """Represents a discovered input file."""
    path: Path
    file_type: str  # 'image', 'video', or 'unsupported'
    extension: str

def discover_files(input_path: Path, config: PipelineConfig) -> List[DiscoveredFile]:
    """
    Discover all files from an input path.
    Accepts a single file or a directory (non-recursive for top level,
    but should handle nested dirs too).
    Classifies each file as 'image', 'video', or 'unsupported'.
    Uses logging to report what was found.
    """
    discovered: List[DiscoveredFile] = []
    
    if not input_path.exists():
        logger.warning(f"Input path does not exist: {input_path}")
        return discovered
    
    files_to_process = [input_path] if input_path.is_file() else list(input_path.rglob('*'))
    
    image_count = 0
    video_count = 0
    unsupported_count = 0
    
    for file_path in files_to_process:
        if file_path.is_dir():
            continue
            
        ext = file_path.suffix.lower()
        if ext in config.supported_image_extensions:
            file_type = 'image'
            image_count += 1
        elif ext in config.supported_video_extensions:
            file_type = 'video'
            video_count += 1
        else:
            file_type = 'unsupported'
            unsupported_count += 1
            
        discovered.append(DiscoveredFile(path=file_path, file_type=file_type, extension=ext))
    
    logger.info(f"Discovered {len(discovered)} files: {image_count} images, {video_count} videos, {unsupported_count} unsupported.")
    return discovered
