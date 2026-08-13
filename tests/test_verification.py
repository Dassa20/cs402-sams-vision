"""Unit tests for SSIM and ORB signature matching verification."""

import numpy as np
from core.verification.ssim_matcher import compute_ssim_similarity
from core.verification.feature_matcher import compute_orb_matches


def test_ssim_identical_images():
    img = np.ones((50, 50), dtype=np.uint8) * 128
    score = compute_ssim_similarity(img, img)
    assert score >= 0.99


def test_orb_matches_handles_none():
    matches = compute_orb_matches(None, None)
    assert matches == 0
