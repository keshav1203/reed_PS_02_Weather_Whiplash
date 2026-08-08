# Weather Whiplash Data Pipeline

A robust, modular data processing pipeline for images and videos, built to handle erratic and extreme weather media ingestion, validation, metadata extraction, and quality control.

## Features

- **Multi-modal Support:** Handles both images (.jpg, .png, .webp) and videos (.mp4, .mov, .avi, etc.).
- **Automatic Validation:** Detects zero-byte files, corrupted media, and unsupported formats.
- **Deduplication:** Robust SHA-256 hash-based duplicate tracking.
- **Video Frame Extraction:** Configurable FPS sampling for extracting frames from videos.
- **Quality Control:** Filters media based on brightness, blur scores, and minimum resolution requirements.
- **Rich Metadata Extraction:** Produces comprehensive metadata for files and video frames.

## Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   cd weather-whiplash
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Basic usage examples for the CLI:

```bash
# Process a directory of images and videos
python -m src.pipeline.main --input-dir /path/to/raw/data
```

Advanced usage:

```bash
# Process with custom configuration
python -m src.pipeline.main --input-dir /path/to/raw/data \
    --sampling-fps 5.0 \
    --model-width 1024 \
    --model-height 1024 \
    --blur-threshold 150
```

## Pipeline Architecture

```text
[Raw Data] -> [Ingestion/Discovery] -> [Validation & Deduplication] 
                                                 |
                                     [Valid Files] -> [Image/Video Processing]
                                                             |
                                      +----------------------+----------------------+
                                      |                                             |
                              [Resized Images]                               [Video Frames]
                                      |                                             |
                              [Quality Control]                              [Quality Control]
                                      |                                             |
                              [Metadata Output]                              [Metadata Output]
```

## Configuration Options

| Option | Default | Description |
|---|---|---|
| `model_width` | 640 | Target width for resizing images and frames |
| `model_height` | 640 | Target height for resizing images and frames |
| `sampling_fps` | 2.0 | Frames per second to extract from videos |
| `blur_threshold` | 100.0 | Minimum variance of Laplacian for blur detection |
| `brightness_min` | 10.0 | Minimum average brightness |
| `brightness_max` | 245.0 | Maximum average brightness |

## Project Structure

```
weather-whiplash/
├── src/
│   └── pipeline/
│       ├── config.py
│       ├── ingestion.py
│       ├── validation.py
│       ├── metadata.py
│       ├── quality.py
│       ├── image_processor.py
│       └── video_processor.py
├── tests/
│   ├── conftest.py
│   ├── test_validation.py
│   ├── test_metadata.py
│   ├── test_image_processor.py
│   └── test_video_processor.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Running Tests

Run the test suite using `pytest`:

```bash
pytest tests/ -v
```

## Future Roadmap

- Cloud storage integration (S3/GCS)
- Advanced AI-based content filtering
- Asynchronous processing pipeline
- Web-based monitoring dashboard
