"""Unit tests for computer vision preprocessing and cell extraction."""

import cv2
import numpy as np
from core.vision.preprocessor import preprocess_image, deskew_image
from core.vision.classifier import detect_signature_presence
from core.models.schemas import AttendanceStatus


def test_preprocess_image_grayscale():
    # Synthetic RGB image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    gray, binary = preprocess_image(img)

    assert gray.shape == (100, 100)
    assert binary.shape == (100, 100)


def test_deskew_image_warps_clean_quad():
    # White sheet on a black background, tilted, so a 4-point boundary is easy to find
    canvas = np.zeros((400, 400, 3), dtype=np.uint8)
    sheet = np.array([[100, 60], [320, 100], [280, 340], [60, 300]], dtype=np.int32)
    cv2.fillConvexPoly(canvas, sheet, (255, 255, 255))

    result = deskew_image(canvas)

    assert result.shape != canvas.shape


def test_deskew_image_falls_back_on_no_boundary():
    # Flat, featureless image, no sheet boundary to detect
    canvas = np.full((100, 100, 3), 128, dtype=np.uint8)

    result = deskew_image(canvas)

    assert result.shape == canvas.shape
    assert np.array_equal(result, canvas)


def test_detect_signature_presence():
    # Empty crop (all zeros) -> ABSENT
    empty_crop = np.zeros((50, 50), dtype=np.uint8)
    status_absent = detect_signature_presence(empty_crop, ink_threshold=50)
    assert status_absent == AttendanceStatus.ABSENT

    # Ink crop (ink pixels = 255) -> PRESENT
    ink_crop = np.zeros((50, 50), dtype=np.uint8)
    ink_crop[10:30, 10:30] = 255
    status_present = detect_signature_presence(ink_crop, ink_threshold=50)
    assert status_present == AttendanceStatus.PRESENT
