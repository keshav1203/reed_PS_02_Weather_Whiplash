import pytest
import numpy as np
from PIL import Image
from pathlib import Path
import cv2
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.pipeline.config import PipelineConfig

@pytest.fixture
def config(tmp_path):
    """Create a PipelineConfig with tmp_path as base_dir."""
    return PipelineConfig(base_dir=tmp_path / 'data')

@pytest.fixture
def sample_image(tmp_path):
    """Create a valid 200x200 RGB test image."""
    img_path = tmp_path / 'test_image.jpg'
    img = Image.new('RGB', (200, 200), color=(128, 128, 128))
    # Add some variation so it's not perfectly uniform
    pixels = img.load()
    for x in range(0, 200, 10):
        for y in range(0, 200, 10):
            pixels[x, y] = (100 + x % 50, 100 + y % 50, 128)
    img.save(str(img_path), quality=95)
    return img_path

@pytest.fixture
def sample_png(tmp_path):
    """Create a valid PNG test image."""
    img_path = tmp_path / 'test_image.png'
    img = Image.new('RGB', (300, 300), color=(100, 150, 200))
    img.save(str(img_path))
    return img_path

@pytest.fixture
def tiny_image(tmp_path):
    """Create a very small image below minimum resolution."""
    img_path = tmp_path / 'tiny.jpg'
    img = Image.new('RGB', (32, 32), color=(128, 128, 128))
    img.save(str(img_path))
    return img_path

@pytest.fixture
def dark_image(tmp_path):
    """Create an extremely dark image."""
    img_path = tmp_path / 'dark.jpg'
    img = Image.new('RGB', (200, 200), color=(2, 2, 2))
    img.save(str(img_path))
    return img_path

@pytest.fixture
def bright_image(tmp_path):
    """Create an extremely bright image."""
    img_path = tmp_path / 'bright.jpg'
    img = Image.new('RGB', (200, 200), color=(252, 252, 252))
    img.save(str(img_path))
    return img_path

@pytest.fixture
def zero_byte_file(tmp_path):
    """Create a zero-byte file."""
    f = tmp_path / 'empty.jpg'
    f.touch()
    return f

@pytest.fixture
def corrupted_image(tmp_path):
    """Create a file with image extension but random bytes."""
    f = tmp_path / 'corrupted.jpg'
    f.write_bytes(b'this is not an image file at all' * 10)
    return f

@pytest.fixture
def sample_video(tmp_path):
    """Create a small valid video file using OpenCV."""
    video_path = tmp_path / 'test_video.mp4'
    # Create a 2-second video at 30fps, 160x120 resolution
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(video_path), fourcc, 30.0, (160, 120))
    for i in range(60):  # 60 frames = 2 seconds at 30fps
        # Create frames with varying brightness for realistic testing
        frame = np.full((120, 160, 3), fill_value=((i * 4) % 200 + 28), dtype=np.uint8)
        writer.write(frame)
    writer.release()
    return video_path

@pytest.fixture
def corrupted_video(tmp_path):
    """Create a file with video extension but invalid content."""
    f = tmp_path / 'corrupted.mp4'
    f.write_bytes(b'not a video' * 100)
    return f

@pytest.fixture
def unsupported_file(tmp_path):
    """Create a file with unsupported extension."""
    f = tmp_path / 'document.pdf'
    f.write_text('fake pdf content')
    return f

@pytest.fixture
def input_directory(tmp_path, sample_image, sample_png, sample_video):
    """Create a directory with mixed valid files."""
    input_dir = tmp_path / 'input'
    input_dir.mkdir()
    import shutil
    shutil.copy(sample_image, input_dir / 'photo.jpg')
    shutil.copy(sample_png, input_dir / 'screenshot.png')
    shutil.copy(sample_video, input_dir / 'race.mp4')
    # Add an unsupported file too
    (input_dir / 'notes.txt').write_text('some notes')
    return input_dir
