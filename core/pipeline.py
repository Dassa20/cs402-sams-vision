"""Shared attendance sheet processing pipeline used by both the CLI (sams.py) and the GUI worker.

Having a single implementation means the desktop app and the command line always produce
the same result for the same input, instead of the GUI drifting out of sync with the real
computer vision logic.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

import numpy as np

from core.db.db_manager import DatabaseManager
from core.db.xml_parser import parse_student_info_xml
from core.models.schemas import AttendanceRecord, AttendanceStatus, Student
from core.utils.logger import setup_logger
from core.vision.classifier import detect_signature_presence
from core.vision.grid_extractor import crop_cells
from core.vision.preprocessor import deskew_image, load_image, preprocess_image

logger = setup_logger("core.pipeline")

ProgressCallback = Callable[[int, str], None]
PreviewCallback = Callable[[str, np.ndarray], None]


@dataclass
class SheetProcessingResult:
    """Outcome of running the full ingestion pipeline against one signing sheet image."""

    sheet_id: str
    date: str
    records: List[AttendanceRecord] = field(default_factory=list)
    present_count: int = 0
    absent_count: int = 0
    low_confidence: bool = False


def process_attendance_sheet(
    sheet_path: Path,
    xml_path: Path,
    db: DatabaseManager,
    date: str,
    on_progress: Optional[ProgressCallback] = None,
    on_preview: Optional[PreviewCallback] = None,
) -> SheetProcessingResult:
    """Runs load -> deskew -> binarize -> segment -> classify -> persist for one signing sheet.

    `on_progress(percent, message)` and `on_preview(stage_name, image)` are optional hooks so
    CLI and GUI callers can surface progress/step images without duplicating pipeline logic.
    """

    def progress(pct: int, message: str) -> None:
        logger.info(message)
        if on_progress:
            on_progress(pct, message)

    def preview(stage: str, image: np.ndarray) -> None:
        if on_preview:
            on_preview(stage, image)

    progress(5, "Loading sheet image & student metadata...")
    students: List[Student] = parse_student_info_xml(xml_path)
    if students:
        db.insert_students(students)
    image = load_image(str(sheet_path))
    preview("Original", image)

    progress(20, "Applying perspective correction & deskewing...")
    image = deskew_image(image)
    preview("Deskewed", image)

    progress(40, "Converting to greyscale & binarizing...")
    gray, binary = preprocess_image(image)
    preview("Greyscale", gray)
    preview("Binarized", binary)

    progress(60, "Segmenting grid cells & analyzing signatures...")
    cells, low_confidence = crop_cells(image, rows=max(1, len(students)), cols=1)

    if low_confidence:
        logger.warning(
            "Table geometry could not be confirmed by real grid-line detection on this sheet "
            "(fell back to an estimated layout) — results should be spot-checked against the photo."
        )

    records: List[AttendanceRecord] = []
    present_count = 0
    absent_count = 0
    for idx, cell in enumerate(cells):
        status = detect_signature_presence(cell.image_crop)
        student_id = students[idx].student_id if idx < len(students) else cell.student_id

        record = AttendanceRecord(
            record_id=None,
            sheet_id=sheet_path.stem,
            student_id=student_id,
            date=date,
            status=status,
        )
        db.insert_attendance_record(record)
        records.append(record)

        if status == AttendanceStatus.PRESENT:
            present_count += 1
        else:
            absent_count += 1

        logger.info(f"Recorded student {student_id}: {status.value} on {date}")

    progress(100, "Saving attendance records to database...")

    return SheetProcessingResult(
        sheet_id=sheet_path.stem,
        date=date,
        records=records,
        present_count=present_count,
        absent_count=absent_count,
        low_confidence=low_confidence,
    )
