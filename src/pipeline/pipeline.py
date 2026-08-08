from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from .config import PipelineConfig
from .ingestion import DiscoveredFile, discover_files
from .validation import ValidationResult, validate_file, compute_sha256, DuplicateTracker
from .image_processor import ProcessedImageResult, process_image
from .video_processor import ProcessedVideoResult, process_video
from .storage import StorageManager

logger = logging.getLogger(__name__)

@dataclass
class PipelineResult:
    """Summary of a pipeline run."""
    files_discovered: int = 0
    images_found: int = 0
    videos_found: int = 0
    unsupported_found: int = 0
    processed: int = 0
    rejected: int = 0
    duplicates: int = 0
    images_generated: int = 0
    frames_generated: int = 0
    errors: List[str] = field(default_factory=list)

class WeatherWhiplashPipeline:
    """Main pipeline orchestrator."""
    
    def __init__(self, config: PipelineConfig | None = None):
        self.config = config or PipelineConfig()
        if hasattr(self.config, 'create_directories'):
            self.config.create_directories()
        self.storage = StorageManager(self.config)
        self.duplicate_tracker = DuplicateTracker(
            self.config.metadata_dir / 'hash_registry.json'
        )
    
    def run(self, input_path: Path) -> PipelineResult:
        """
        Run the full pipeline on the given input path.
        
        Flow:
        1. Discover files
        2. For each file:
           a. If unsupported → reject
           b. Validate → if invalid, reject + move to rejected
           c. Compute SHA-256 → if duplicate, skip
           d. If image → process_image
           e. If video → process_video
           f. Save metadata via StorageManager
        3. Save duplicate tracker
        4. Save batch summary
        5. Return PipelineResult
        """
        result = PipelineResult()
        
        try:
            discovered_files = discover_files(input_path, self.config)
            result.files_discovered = len(discovered_files)
            
            for df in discovered_files:
                try:
                    if df.file_type == 'unsupported':
                        result.unsupported_found += 1
                        result.rejected += 1
                        reason = f"Unsupported file extension: {df.extension}"
                        self.storage.move_to_rejected(df.path, reason)
                        continue
                        
                    if df.file_type == 'image':
                        result.images_found += 1
                    elif df.file_type == 'video':
                        result.videos_found += 1
                        
                    val_result = validate_file(df, self.config)
                    if not val_result.valid:
                        result.rejected += 1
                        self.storage.move_to_rejected(df.path, val_result.reason or "Validation failed")
                        continue
                        
                    file_hash = compute_sha256(df.path)
                    if self.duplicate_tracker.is_duplicate(file_hash):
                        result.duplicates += 1
                        logger.info(f"Duplicate file skipped: {df.path.name}")
                        continue
                        
                    if df.file_type == 'image':
                        proc_res = process_image(df.path, file_hash, self.config)
                        self.storage.save_file_metadata(proc_res.metadata)
                        result.images_generated += 1
                        result.processed += 1
                        
                    elif df.file_type == 'video':
                        proc_res = process_video(df.path, file_hash, self.config)
                        self.storage.save_file_metadata(proc_res.metadata)
                        if proc_res.frames:
                            self.storage.save_frame_metadata(proc_res.frames, proc_res.metadata.file_id)
                        result.frames_generated += len(proc_res.frames)
                        result.processed += 1
                        
                    self.duplicate_tracker.register(file_hash)
                    
                except Exception as e:
                    error_msg = f"Error processing {df.path.name}: {str(e)}"
                    logger.error(error_msg)
                    result.errors.append(error_msg)
                    
        finally:
            self.duplicate_tracker.save()
            summary = {
                "files_discovered": result.files_discovered,
                "images_found": result.images_found,
                "videos_found": result.videos_found,
                "unsupported_found": result.unsupported_found,
                "processed": result.processed,
                "rejected": result.rejected,
                "duplicates": result.duplicates,
                "images_generated": result.images_generated,
                "frames_generated": result.frames_generated,
                "errors": result.errors,
            }
            self.storage.save_batch_summary(summary)
            
        return result
