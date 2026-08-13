"""Configuration settings for SAMS Vision."""

from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).resolve().parent.parent.parent

@dataclass
class Config:
    # Directory paths
    DATA_DIR: Path = BASE_DIR / "data"
    TEST_IMAGES_DIR: Path = BASE_DIR / "test_images"
    DOCS_DIR: Path = BASE_DIR / "docs"
    DB_PATH: Path = DATA_DIR / "sams.db"
    XML_PATH: Path = DATA_DIR / "info.xml"

    # Computer Vision parameters
    CANNY_THRESH_LOW: int = 50
    CANNY_THRESH_HIGH: int = 150
    ADAPTIVE_BLOCK_SIZE: int = 11
    ADAPTIVE_C: int = 2
    MIN_CELL_AREA: int = 500

    # Signature Verification thresholds
    DEFAULT_SSIM_THRESHOLD: float = 0.65
    MIN_INK_PIXEL_COUNT: int = 100
    ORB_MIN_MATCHES: int = 10
