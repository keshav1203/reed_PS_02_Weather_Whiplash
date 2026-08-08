import sys
from pathlib import Path
from PIL import Image

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline.image_processor import process_image, ProcessedImageResult
from src.pipeline.validation import compute_sha256
from src.pipeline.config import PipelineConfig

def test_process_image_creates_output(tmp_path, sample_image):
    config = PipelineConfig(base_dir=tmp_path / 'data')
    config.create_directories()
    sha256 = compute_sha256(sample_image)
    result = process_image(sample_image, sha256, config)
    assert result.processed_path.exists()

def test_process_image_preserves_original(tmp_path, sample_image):
    config = PipelineConfig(base_dir=tmp_path / 'data')
    config.create_directories()
    sha256 = compute_sha256(sample_image)
    result = process_image(sample_image, sha256, config)
    assert result.original_path.exists()
    assert compute_sha256(result.original_path) == sha256

def test_process_image_resizes(tmp_path, sample_image):
    config = PipelineConfig(base_dir=tmp_path / 'data')
    config.create_directories()
    sha256 = compute_sha256(sample_image)
    result = process_image(sample_image, sha256, config)
    with Image.open(result.processed_path) as img:
        assert img.width == config.model_width
        assert img.height == config.model_height

def test_process_image_custom_size(tmp_path, sample_image):
    config = PipelineConfig(base_dir=tmp_path / 'data', model_width=320, model_height=320)
    config.create_directories()
    sha256 = compute_sha256(sample_image)
    result = process_image(sample_image, sha256, config)
    with Image.open(result.processed_path) as img:
        assert img.width == 320
        assert img.height == 320

def test_process_image_metadata(tmp_path, sample_image):
    config = PipelineConfig(base_dir=tmp_path / 'data')
    config.create_directories()
    sha256 = compute_sha256(sample_image)
    result = process_image(sample_image, sha256, config)
    assert result.metadata.file_type == "image"
    assert result.metadata.sha256 == sha256

def test_process_image_quality_result(tmp_path, sample_image):
    config = PipelineConfig(base_dir=tmp_path / 'data')
    config.create_directories()
    sha256 = compute_sha256(sample_image)
    result = process_image(sample_image, sha256, config)
    assert hasattr(result.quality, "blur_score")
    assert hasattr(result.quality, "brightness")
    assert hasattr(result.quality, "resolution_valid")

def test_process_png(tmp_path, sample_png):
    config = PipelineConfig(base_dir=tmp_path / 'data')
    config.create_directories()
    sha256 = compute_sha256(sample_png)
    result = process_image(sample_png, sha256, config)
    assert result.processed_path.exists()
    assert result.metadata.extension == ".png"
