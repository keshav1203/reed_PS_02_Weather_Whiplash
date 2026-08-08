from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Tuple

@dataclass
class PipelineConfig:
    """Central configuration for the Weather Whiplash data pipeline."""
    
    # Supported extensions
    supported_image_extensions: Tuple[str, ...] = ('.jpg', '.jpeg', '.png', '.webp')
    supported_video_extensions: Tuple[str, ...] = ('.mp4', '.mov', '.avi', '.mkv', '.webm')
    
    # Model input dimensions
    model_width: int = 640
    model_height: int = 640
    
    # Video sampling
    sampling_fps: float = 2.0
    
    # Quality thresholds
    min_image_width: int = 64
    min_image_height: int = 64
    blur_threshold: float = 100.0
    brightness_min: float = 10.0
    brightness_max: float = 245.0
    
    # Directories
    base_dir: Path = field(default_factory=lambda: Path('data'))
    
    # Pipeline version
    pipeline_version: str = '0.1.0'
    
    @property
    def raw_images_dir(self) -> Path:
        return self.base_dir / 'raw' / 'images'
    
    @property
    def raw_videos_dir(self) -> Path:
        return self.base_dir / 'raw' / 'videos'
    
    @property
    def processed_images_dir(self) -> Path:
        return self.base_dir / 'processed' / 'images'
    
    @property
    def processed_frames_dir(self) -> Path:
        return self.base_dir / 'processed' / 'frames'
    
    @property
    def rejected_dir(self) -> Path:
        return self.base_dir / 'rejected'
    
    @property
    def metadata_dir(self) -> Path:
        return self.base_dir / 'metadata'
    
    @property
    def all_supported_extensions(self) -> Tuple[str, ...]:
        return self.supported_image_extensions + self.supported_video_extensions
    
    def create_directories(self) -> None:
        """Create all required output directories."""
        for dir_path in [
            self.raw_images_dir, self.raw_videos_dir,
            self.processed_images_dir, self.processed_frames_dir,
            self.rejected_dir, self.metadata_dir,
        ]:
            dir_path.mkdir(parents=True, exist_ok=True)
