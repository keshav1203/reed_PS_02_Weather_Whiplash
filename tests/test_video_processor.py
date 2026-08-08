import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline.video_processor import process_video, ProcessedVideoResult
from src.pipeline.validation import compute_sha256
from src.pipeline.config import PipelineConfig

def test_process_video_creates_frames(tmp_path, sample_video):
    config = PipelineConfig(base_dir=tmp_path / 'data')
    config.create_directories()
    sha256 = compute_sha256(sample_video)
    result = process_video(sample_video, sha256, config)
    assert len(result.frames) > 0
    for frame in result.frames:
        assert Path(frame.image_path).exists()

def test_process_video_frame_count(tmp_path, sample_video):
    # 2 seconds at sampling_fps=2 should be around 4 frames
    config = PipelineConfig(base_dir=tmp_path / 'data', sampling_fps=2.0)
    config.create_directories()
    sha256 = compute_sha256(sample_video)
    result = process_video(sample_video, sha256, config)
    # Give some slack to precise frame extraction counts
    assert 3 <= len(result.frames) <= 5

def test_process_video_preserves_original(tmp_path, sample_video):
    config = PipelineConfig(base_dir=tmp_path / 'data')
    config.create_directories()
    sha256 = compute_sha256(sample_video)
    result = process_video(sample_video, sha256, config)
    assert result.original_path.exists()
    assert compute_sha256(result.original_path) == sha256

def test_process_video_metadata(tmp_path, sample_video):
    config = PipelineConfig(base_dir=tmp_path / 'data')
    config.create_directories()
    sha256 = compute_sha256(sample_video)
    result = process_video(sample_video, sha256, config)
    assert result.metadata.fps is not None
    assert result.metadata.frame_count is not None
    assert result.metadata.duration_seconds is not None

def test_process_video_frame_metadata(tmp_path, sample_video):
    config = PipelineConfig(base_dir=tmp_path / 'data')
    config.create_directories()
    sha256 = compute_sha256(sample_video)
    result = process_video(sample_video, sha256, config)
    for frame in result.frames:
        assert frame.source_file_id == result.metadata.file_id

def test_process_video_custom_sampling(tmp_path, sample_video):
    config_1fps = PipelineConfig(base_dir=tmp_path / 'data', sampling_fps=1.0)
    config_1fps.create_directories()
    sha256 = compute_sha256(sample_video)
    result_1fps = process_video(sample_video, sha256, config_1fps)
    
    config_4fps = PipelineConfig(base_dir=tmp_path / 'data_high', sampling_fps=4.0)
    config_4fps.create_directories()
    result_4fps = process_video(sample_video, sha256, config_4fps)
    
    assert len(result_1fps.frames) < len(result_4fps.frames)

def test_frame_naming(tmp_path, sample_video):
    config = PipelineConfig(base_dir=tmp_path / 'data')
    config.create_directories()
    sha256 = compute_sha256(sample_video)
    result = process_video(sample_video, sha256, config)
    
    frame_names = [Path(frame.image_path).name for frame in result.frames]
    assert "frame_000001.jpg" in frame_names
