"""Data schemas and transfer objects for SAMS Vision."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Any, TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np


class AttendanceStatus(str, Enum):

    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    SUSPECTED_PROXY = "SUSPECTED_PROXY"
    UNCLEAR = "UNCLEAR"


@dataclass
class Student:
    """Represents student metadata loaded from XML or DB."""
    student_id: str
    name: str
    course_code: str
    baseline_signature_path: Optional[str] = None
    title: Optional[str] = None


@dataclass
class SheetMetadata:
    """Metadata regarding a processed attendance sheet."""
    sheet_id: str
    date: str
    course_code: str
    total_students: int
    image_path: str


@dataclass
class CellCrop:
    """A cropped cell region from the attendance grid image."""
    row_idx: int
    col_idx: int
    student_id: str
    image_crop: Any
    bounding_box: tuple[int, int, int, int]  # (x, y, w, h)


@dataclass
class VerificationResult:
    """Result of signature comparison between baseline and extracted crop."""
    student_id: str
    ssim_score: float
    orb_matches: int
    is_anomaly: bool
    status: AttendanceStatus
    confidence: float


@dataclass
class AttendanceRecord:
    """A final attendance record ready for persistence."""
    record_id: Optional[int]
    sheet_id: str
    student_id: str
    date: str
    status: AttendanceStatus
    verification: Optional[VerificationResult] = None
