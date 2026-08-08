from __future__ import annotations

"""Weather Whiplash Data Pipeline.

A modular pipeline for ingesting, validating, and processing
motorsport/F1 track condition images and videos.
"""

from .config import PipelineConfig
from .pipeline import WeatherWhiplashPipeline

__version__ = "0.1.0"
__all__ = ["PipelineConfig", "WeatherWhiplashPipeline"]
