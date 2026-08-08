from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .config import PipelineConfig
from .metadata import FileMetadata, extract_image_metadata
from .quality import QualityResult, check_quality

logger = logging.getLogger(__name__)

@dataclass
class ProcessedImageResult:
    """Result of processing a single image."""
    original_path: Path
    processed_path: Path
    metadata: FileMetadata
    quality: QualityResult

def process_image(
    path: Path,
    sha256: str,
    config: PipelineConfig,
) -> ProcessedImageResult:
    """
    Process a single image file.
    
    Steps:
    1. Copy the original to config.raw_images_dir / filename
    2. Open with Pillow
    3. Resize to (config.model_width, config.model_height) using Image.LANCZOS
    4. Save processed copy to config.processed_images_dir / filename (always as the original format)
    5. Run quality check on the PROCESSED image
    6. Extract metadata
    7. Attach quality result to metadata
    8. Return ProcessedImageResult
    
    Logging:
    - Log the original resolution
    - Log the target resolution
    - Log quality results
    """
    logger.info(f"Processing image: {path.name}")
    
    raw_path = config.raw_images_dir / path.name
    shutil.copy2(path, raw_path)
    
    processed_path = config.processed_images_dir / path.name
    
    with Image.open(path) as img:
        original_width, original_height = img.size
        logger.info(f"Original resolution: {original_width}x{original_height}")
        
        target_size = (config.model_width, config.model_height)
        logger.info(f"Target resolution: {target_size[0]}x{target_size[1]}")
        
        resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
        
        save_kwargs = {}
        if path.suffix.lower() in ('.jpg', '.jpeg'):
            save_kwargs['quality'] = 95
            
        resized_img.save(processed_path, **save_kwargs)
        
    quality_result = check_quality(processed_path, config)
    logger.info(f"Quality result: {quality_result}")
    
    metadata = extract_image_metadata(path, sha256, str(processed_path), config)
    metadata.quality = quality_result.to_dict()
    
    return ProcessedImageResult(
        original_path=raw_path,
        processed_path=processed_path,
        metadata=metadata,
        quality=quality_result
    )
