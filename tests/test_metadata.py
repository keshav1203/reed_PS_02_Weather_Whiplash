import sys
from pathlib import Path
import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline.metadata import extract_image_metadata, extract_video_metadata, create_frame_metadata, FileMetadata, FrameMetadata
from src.pipeline.config import PipelineConfig

def test_image_metadata_fields(config, sample_image):
    meta = extract_image_metadata(sample_image, "fakehash", "processed/path.jpg", config)
    assert meta.file_type == "image"
    assert meta.extension == ".jpg"
    assert meta.sha256 == "fakehash"
    assert meta.width > 0
    assert meta.height > 0
    assert meta.file_id != ""
    assert meta.created_at != ""
    assert meta.pipeline_version == config.pipeline_version
    assert meta.fps is None

def test_video_metadata_fields(config, sample_video):
    meta = extract_video_metadata(sample_video, "videohash", "processed/video.mp4", config)
    assert meta.file_type == "video"
    assert meta.fps is not None and meta.fps > 0
    assert meta.frame_count is not None and meta.frame_count > 0
    assert meta.duration_seconds is not None and meta.duration_seconds > 0
    assert meta.sampling_fps == config.sampling_fps

def test_frame_metadata():
    source_meta = FileMetadata(
        file_id="source123",
        filename="video.mp4",
        file_type="video",
        extension=".mp4",
        sha256="hash",
        original_path="old",
        processed_path="new",
        width=100,
        height=100
    )
    frame_meta = create_frame_metadata(source_meta, 5, 2.5, "frames/f.jpg")
    assert frame_meta.source_file_id == "source123"
    assert frame_meta.frame_number == 5
    assert frame_meta.timestamp_seconds == 2.5
    assert frame_meta.source_video == "video.mp4"

def test_metadata_to_dict(config, sample_image):
    meta = extract_image_metadata(sample_image, "hash", "path", config)
    d = meta.to_dict()
    assert isinstance(d, dict)
    assert d["file_id"] == meta.file_id
    assert d["sha256"] == "hash"

def test_frame_metadata_to_dict():
    source_meta = FileMetadata(
        file_id="source123",
        filename="video.mp4",
        file_type="video",
        extension=".mp4",
        sha256="hash",
        original_path="old",
        processed_path="new",
        width=100,
        height=100
    )
    frame_meta = create_frame_metadata(source_meta, 5, 2.5, "frames/f.jpg")
    d = frame_meta.to_dict()
    assert isinstance(d, dict)
    assert d["frame_id"] == frame_meta.frame_id

def test_file_id_is_unique(config, sample_image):
    meta1 = extract_image_metadata(sample_image, "hash", "path1", config)
    meta2 = extract_image_metadata(sample_image, "hash", "path2", config)
    assert meta1.file_id != meta2.file_id

def test_created_at_is_iso_format(config, sample_image):
    meta = extract_image_metadata(sample_image, "hash", "path", config)
    # Should parse successfully
    dt = datetime.datetime.fromisoformat(meta.created_at)
    assert isinstance(dt, datetime.datetime)
