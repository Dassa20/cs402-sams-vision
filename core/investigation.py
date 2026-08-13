"""Shared signature verification logic used by both investigate.py (CLI) and the GUI.

Compares a student's signature on a specific dated sheet against their baseline reference
signature from info.xml, so both entry points stay in sync instead of drifting apart.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from core.db.db_manager import DatabaseManager
from core.db.xml_parser import parse_student_info_xml
from core.utils.config import Config
from core.utils.logger import setup_logger
from core.verification.feature_matcher import compute_orb_matches
from core.verification.ssim_matcher import compute_ssim_similarity
from core.vision.grid_extractor import crop_cells
from core.vision.preprocessor import deskew_image, load_image

logger = setup_logger("core.investigation")


@dataclass
class SignatureVerificationResult:
    student_id: str
    student_name: str
    sheet_path: Path
    ssim_score: float
    orb_matches: int
    is_anomaly: bool
    baseline_crop: np.ndarray
    extracted_crop: np.ndarray
    low_confidence: bool = False

    @property
    def verdict(self) -> str:
        return "SUSPECTED MISMATCH — signature does not resemble baseline" if self.is_anomaly \
            else "MATCH — signature consistent with baseline"


def resolve_sheet_path(sheet_arg: Optional[str], student_id: str, db: DatabaseManager) -> Path:
    """Finds the sheet image to investigate: an explicit path, or the student's most recent stored record."""
    if sheet_arg:
        return Path(sheet_arg)

    records = db.get_student_records(student_id)
    if not records:
        raise FileNotFoundError(
            f"No stored attendance sheets found for student {student_id}; pass a sheet path explicitly."
        )
    sheet_id = records[0]["sheet_id"]
    for ext in (".jpeg", ".jpg", ".png"):
        candidate = Config.TEST_IMAGES_DIR / f"{sheet_id}{ext}"
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Could not locate image file for sheet '{sheet_id}' in {Config.TEST_IMAGES_DIR}; pass a sheet path explicitly."
    )


def verify_student_signature(
    student_id: str,
    sheet_path: Path,
    xml_path: Path,
    threshold: float = Config.DEFAULT_SSIM_THRESHOLD,
) -> SignatureVerificationResult:
    """Compares a student's signature crop on `sheet_path` against their baseline reference."""
    students = {s.student_id: s for s in parse_student_info_xml(xml_path)}
    student = students.get(student_id)
    if not student:
        raise ValueError(f"Student '{student_id}' not found in {xml_path}")
    if not student.baseline_signature_path or not Path(student.baseline_signature_path).exists():
        raise FileNotFoundError(
            f"No baseline signature on file for student '{student_id}' ({student.baseline_signature_path})."
        )
    if not sheet_path.exists():
        raise FileNotFoundError(f"Sheet image file not found: {sheet_path}")

    # NOTE: row position is matched by the student's order in info.xml, mirroring the same
    # positional assumption core/pipeline.py's ingestion pipeline makes.
    ordered_ids = list(students.keys())
    row_idx = ordered_ids.index(student_id)

    image = deskew_image(load_image(str(sheet_path)))
    cells, low_confidence = crop_cells(image, rows=len(students), cols=1)
    if low_confidence:
        logger.warning(
            f"Table geometry could not be confirmed by real grid-line detection on '{sheet_path}' — "
            "this verification result should be spot-checked against the photo."
        )
    if row_idx >= len(cells):
        raise IndexError(f"Signature row for student '{student_id}' could not be located on sheet '{sheet_path}'.")
    extracted_crop = cells[row_idx].image_crop

    baseline = load_image(student.baseline_signature_path)
    baseline_gray = cv2.cvtColor(baseline, cv2.COLOR_BGR2GRAY)
    extracted_gray = cv2.cvtColor(extracted_crop, cv2.COLOR_BGR2GRAY) if extracted_crop.ndim == 3 else extracted_crop

    ssim_score = compute_ssim_similarity(baseline, extracted_crop)
    orb_matches = compute_orb_matches(baseline_gray, extracted_gray)
    is_anomaly = ssim_score < threshold and orb_matches < Config.ORB_MIN_MATCHES

    logger.info(
        f"Verified {student_id} against {sheet_path}: SSIM={ssim_score:.3f}, "
        f"ORB={orb_matches}, anomaly={is_anomaly}"
    )

    return SignatureVerificationResult(
        student_id=student_id,
        student_name=student.name,
        sheet_path=sheet_path,
        ssim_score=ssim_score,
        orb_matches=orb_matches,
        is_anomaly=is_anomaly,
        baseline_crop=baseline,
        extracted_crop=extracted_crop,
        low_confidence=low_confidence,
    )
