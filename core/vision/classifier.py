"""Cell content classifier to determine signature/mark presence."""

import re
import shutil
from pathlib import Path

import cv2
import numpy as np
from core.models.schemas import AttendanceStatus
from core.utils.logger import setup_logger

logger = setup_logger("core.vision.classifier")

# Common ways a student marks themselves absent by hand instead of leaving the cell blank.
_ABSENCE_NOTATION_WORDS = {"ab", "abs", "absent"}

_KNOWN_TESSERACT_PATHS = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
)

_ocr_checked = False
_ocr_available = False


def _ensure_ocr_configured() -> bool:
    """Locates pytesseract + the Tesseract binary once and caches the result.

    Returns False (without raising) if either isn't installed, so callers can fall back to
    ink-only classification instead of crashing on a machine that doesn't have OCR set up.
    """
    global _ocr_checked, _ocr_available
    if _ocr_checked:
        return _ocr_available
    _ocr_checked = True

    try:
        import pytesseract
    except ImportError:
        logger.debug("pytesseract not installed; skipping OCR absence-notation check.")
        return False

    if shutil.which("tesseract") is None:
        for candidate in _KNOWN_TESSERACT_PATHS:
            if Path(candidate).exists():
                pytesseract.pytesseract.tesseract_cmd = candidate
                break
        else:
            logger.debug("Tesseract binary not found on PATH or in known install locations.")
            return False

    _ocr_available = True
    return True


def _matches_absence_notation(cell_crop: np.ndarray) -> bool:
    """Uses OCR (if available) to check whether ink in the cell is handwritten absence
    notation (e.g. "ab", "absent") rather than a signature.

    Pure ink/edge pixel density can't reliably tell these apart -- a quickly-written "ab" with
    a connecting stroke can have ink coverage statistically indistinguishable from a real
    signature. Returns False (deferring to the ink-based verdict) if OCR isn't installed, so
    this stays a fully optional enhancement rather than a hard dependency.
    """
    if not _ensure_ocr_configured():
        return False

    try:
        import pytesseract

        gray = cv2.cvtColor(cell_crop, cv2.COLOR_BGR2GRAY) if cell_crop.ndim == 3 else cell_crop
        # Upscale small handwriting crops -- Tesseract is tuned for print-sized text.
        scaled = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
        text = pytesseract.image_to_string(scaled, config="--psm 7").strip().lower()
    except Exception as e:
        logger.debug(f"OCR absence-notation check failed, ignoring: {e}")
        return False

    cleaned = re.sub(r"[^a-z]", "", text)
    matched = cleaned in _ABSENCE_NOTATION_WORDS
    if matched:
        logger.info(f"OCR read '{text}' in signature cell -> treating as absence notation, not a signature.")
    return matched


def detect_signature_presence(cell_crop: np.ndarray, ink_threshold: int = 1000) -> AttendanceStatus:
    """Determines signature presence using Pen Ink Color Differential and Laplacian Edge Analysis.

    Args:
        cell_crop: BGR or Grayscale image crop of the student's signature box.
        ink_threshold: Minimum combined ink & stroke edge pixel count to qualify as PRESENT (default 1000).

    Returns:
        AttendanceStatus (PRESENT or ABSENT).
    """
    if cell_crop is None or cell_crop.size == 0:
        return AttendanceStatus.ABSENT

    if len(cell_crop.shape) == 2:
        gray = cell_crop
        bgr = cv2.cvtColor(cell_crop, cv2.COLOR_GRAY2BGR)
    else:
        bgr = cell_crop
        gray = cv2.cvtColor(cell_crop, cv2.COLOR_BGR2GRAY)

    b, g, r = cv2.split(bgr)

    # 1. Blue Pen Ink Detector (B - R > 15)
    blue_diff = b.astype(int) - r.astype(int)
    blue_pixels = int(np.count_nonzero(blue_diff > 15))

    # 2. Black/Dark Pen Stroke Sharp Edge Detector (|Laplacian(Gray)| > 30)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    edge_pixels = int(np.count_nonzero(np.abs(laplacian) > 30))

    combined_score = blue_pixels + edge_pixels

    status = AttendanceStatus.PRESENT if combined_score >= ink_threshold else AttendanceStatus.ABSENT

    if status == AttendanceStatus.PRESENT and _matches_absence_notation(bgr):
        status = AttendanceStatus.ABSENT

    logger.info(
        f"Cell signature score: {combined_score} (Blue: {blue_pixels}, Edges: {edge_pixels}, Threshold: {ink_threshold}) -> {status.value}"
    )

    return status
