from __future__ import annotations
import logging
import json
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict, Any

from .config import PipelineConfig
from .metadata import FileMetadata, FrameMetadata

logger = logging.getLogger(__name__)

class StorageManager:
    """Manages file storage and metadata persistence."""
    
    def __init__(self, config: PipelineConfig):
        self._config = config
        config.create_directories()
    
    def save_file_metadata(self, metadata: FileMetadata) -> Path:
        """
        Save file metadata as JSON to data/metadata/<file_id>.json
        Returns the path to the saved file.
        """
        out_path = self._config.metadata_dir / f"{metadata.file_id}.json"
        with open(out_path, 'w') as f:
            json.dump(metadata.to_dict(), f, indent=2)
        return out_path
    
    def save_frame_metadata(self, frames: List[FrameMetadata], video_id: str) -> Path:
        """
        Save frame metadata as JSON to data/metadata/<video_id>_frames.json
        Saves as a JSON array of frame metadata dicts.
        Returns the path to the saved file.
        """
        out_path = self._config.metadata_dir / f"{video_id}_frames.json"
        with open(out_path, 'w') as f:
            json.dump([frame.to_dict() for frame in frames], f, indent=2)
        return out_path
    
    def move_to_rejected(self, filepath: Path, reason: str) -> None:
        """
        Copy file to data/rejected/ and append entry to rejection_log.json.
        The rejection_log.json is a JSON array of objects with:
        {filename, original_path, reason, rejected_at}
        """
        dest_path = self._config.rejected_dir / filepath.name
        try:
            shutil.copy2(filepath, dest_path)
        except Exception as e:
            logger.error(f"Failed to copy {filepath} to rejected: {e}")
            
        log_path = self._config.rejected_dir / "rejection_log.json"
        
        entries = []
        if log_path.exists():
            try:
                with open(log_path, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        entries = data
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Failed to load rejection log: {e}")
                
        entry = {
            "filename": filepath.name,
            "original_path": str(filepath),
            "reason": reason,
            "rejected_at": datetime.now(timezone.utc).isoformat()
        }
        entries.append(entry)
        
        try:
            with open(log_path, 'w') as f:
                json.dump(entries, f, indent=2)
        except IOError as e:
            logger.error(f"Failed to save rejection log: {e}")
            
    def save_batch_summary(self, summary: Dict[str, Any]) -> Path:
        """
        Save pipeline run summary to data/metadata/batch_summary_<timestamp>.json
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        out_path = self._config.metadata_dir / f"batch_summary_{timestamp}.json"
        with open(out_path, 'w') as f:
            json.dump(summary, f, indent=2)
        return out_path
