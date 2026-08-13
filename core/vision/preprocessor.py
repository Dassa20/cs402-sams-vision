"""Image preprocessing, binarization, and homography/deskewing operations."""

import cv2
import numpy as np
from typing import Tuple
from core.utils.config import Config
from core.utils.logger import setup_logger

logger = setup_logger("core.vision.preprocessor")


def load_image(image_path: str) -> np.ndarray:
    """Loads an image file into a NumPy array."""
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Failed to load image from path: {image_path}")
    return image


def preprocess_image(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Converts image to grayscale and applies adaptive binarization for shadow handling.

    Returns:
        Tuple of (grayscale_image, binary_image)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Median blur to clean up remaining salt-and-pepper speckle before thresholding
    denoised = cv2.medianBlur(blurred, 5)
    # Adaptive thresholding to handle lighting variations across physical paper sheets
    binary = cv2.adaptiveThreshold(
        denoised,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )
    return gray, binary


def order_points(pts: np.ndarray) -> np.ndarray:
    """Orders 4 boundary points as top-left, top-right, bottom-right, bottom-left."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def deskew_image(image: np.ndarray) -> np.ndarray:
    """Detects sheet boundary contours and applies perspective transformation homography."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, Config.CANNY_THRESH_LOW, Config.CANNY_THRESH_HIGH)
    edges = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    h, w = image.shape[:2]
    sheet_contour = None
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        if len(approx) == 4 and cv2.contourArea(approx) > 0.3 * w * h:
            sheet_contour = approx
            break

    if sheet_contour is None:
        logger.info("No quadrilateral sheet boundary found, skipping deskew.")
        return image

    rect = order_points(sheet_contour.reshape(4, 2))
    (tl, tr, br, bl) = rect

    max_width = max(int(np.linalg.norm(br - bl)), int(np.linalg.norm(tr - tl)))
    max_height = max(int(np.linalg.norm(tr - br)), int(np.linalg.norm(tl - bl)))

    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")

    matrix = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
    logger.info(f"Deskewed sheet to {max_width}x{max_height} via perspective homography.")
    return warped
