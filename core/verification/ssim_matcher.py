"""Structural Similarity Index (SSIM) signature comparison module."""

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from core.utils.logger import setup_logger

logger = setup_logger("core.verification.ssim_matcher")


def compute_ssim_similarity(reference_crop: np.ndarray, extracted_crop: np.ndarray) -> float:
    """Computes SSIM score between a reference signature image and an extracted signature cell crop.
    
    Returns:
        float score between 0.0 and 1.0 (higher = more similar).
    """
    if reference_crop is None or extracted_crop is None:
        return 0.0
        
    # Ensure grayscale single channel
    if len(reference_crop.shape) == 3:
        reference_crop = cv2.cvtColor(reference_crop, cv2.COLOR_BGR2GRAY)
    if len(extracted_crop.shape) == 3:
        extracted_crop = cv2.cvtColor(extracted_crop, cv2.COLOR_BGR2GRAY)

    # Resize extracted crop to match reference dimensions
    h, w = reference_crop.shape
    resized_extracted = cv2.resize(extracted_crop, (w, h), interpolation=cv2.INTER_AREA)

    score, _ = ssim(reference_crop, resized_extracted, full=True)
    logger.debug(f"SSIM similarity score: {score:.4f}")
    return float(score)
