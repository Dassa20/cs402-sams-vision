"""Utility script to generate synthetic sample attendance sheet images and reference signatures for testing."""

import cv2
import numpy as np
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
TEST_IMAGES_DIR = Path(__file__).parent
SIG_DIR = DATA_DIR / "signatures"

SIG_DIR.mkdir(parents=True, exist_ok=True)


def generate_sample_sheet():
    """Generates a synthetic paper sheet image with a student grid table."""
    # Create white paper canvas (800x600)
    canvas = np.full((600, 800, 3), 255, dtype=np.uint8)

    # Title header
    cv2.putText(canvas, "CS402.3 Attendance Sheet - Session 01", (150, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(canvas, "Date: 2026-07-24", (600, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 50, 50), 1)

    # Draw table border
    cv2.rectangle(canvas, (50, 70), (750, 550), (0, 0, 0), 2)
    
    # Table Header Row
    cv2.line(canvas, (50, 110), (750, 110), (0, 0, 0), 2)
    cv2.line(canvas, (200, 70), (200, 550), (0, 0, 0), 2)
    cv2.line(canvas, (500, 70), (500, 550), (0, 0, 0), 2)

    cv2.putText(canvas, "Student ID", (70, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(canvas, "Name", (220, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    cv2.putText(canvas, "Signature / Mark", (520, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

    # Student Rows
    students = [
        ("STU001", "Alice Smith", True),
        ("STU002", "Bob Jones", True),
        ("STU003", "Charlie Brown", False),
    ]

    row_height = 130
    for idx, (stu_id, name, signed) in enumerate(students):
        y = 110 + idx * row_height
        # Horizontal divider
        cv2.line(canvas, (50, y + row_height), (750, y + row_height), (0, 0, 0), 1)

        cv2.putText(canvas, stu_id, (70, y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
        cv2.putText(canvas, name, (220, y + 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

        if signed:
            # Draw synthetic signature curve
            points = np.array([
                [530 + idx * 5, y + 60],
                [560, y + 30],
                [590, y + 80],
                [630 + idx * 10, y + 40],
                [680, y + 70]
            ], np.int32)
            cv2.polylines(canvas, [points], False, (20, 20, 180), 2, cv2.LINE_AA)

            # Save reference baseline signature
            sig_crop = canvas[y + 10 : y + row_height - 10, 510 : 740]
            cv2.imwrite(str(SIG_DIR / f"{stu_id}.png"), sig_crop)

    sheet_path = TEST_IMAGES_DIR / "sample_sheet.jpg"
    cv2.imwrite(str(sheet_path), canvas)
    print(f"✅ Generated sample sheet: {sheet_path}")
    print(f"✅ Generated reference signatures in: {SIG_DIR}")


if __name__ == "__main__":
    generate_sample_sheet()
