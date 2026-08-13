"""ORB feature point matching signature comparison module."""

import cv2
import numpy as np
from core.utils.logger import setup_logger

logger = setup_logger("core.verification.feature_matcher")


def compute_orb_matches(reference_crop: np.ndarray, extracted_crop: np.ndarray) -> int:
    """Detects ORB feature points and counts good descriptor matches using BFMatcher.
    
    Returns:
        int: Number of good feature matches.
    """
    if reference_crop is None or extracted_crop is None:
        return 0

    orb = cv2.ORB_create(nfeatures=500)

    # Find keypoints and descriptors
    kp1, des1 = orb.detectAndCompute(reference_crop, None)
    kp2, des2 = orb.detectAndCompute(extracted_crop, None)

    if des1 is None or des2 is None or len(des1) < 2 or len(des2) < 2:
        return 0

    # Brute Force Matcher with Hamming distance
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)

    # Filter good matches by distance threshold
    good_matches = [m for m in matches if m.distance < 50]
    logger.debug(f"ORB feature matches: {len(good_matches)}")
    return len(good_matches)
