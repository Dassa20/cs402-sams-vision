#!/usr/bin/env python3
"""Signature Anomaly Verification & Forensic Investigation CLI Interface.

Compares the signature a student put on a given signing sheet against their baseline
reference signature (info.xml -> signature_path) using SSIM and ORB feature matching,
and reports whether it looks like a match or a possible mismatch.

Usage:
    python investigate.py 10000409
    python investigate.py 10000409 --sheet test_images/3.jpeg
"""

import argparse
import sys
from pathlib import Path

from core.db.db_manager import DatabaseManager
from core.investigation import resolve_sheet_path, verify_student_signature
from core.utils.config import Config
from core.utils.logger import setup_logger

logger = setup_logger("investigate_cli")


def main():
    parser = argparse.ArgumentParser(description="Signature Anomaly Verification Engine")
    parser.add_argument("student_id", type=str, nargs="?", default=None, help="Student index to investigate")
    parser.add_argument("--sheet", type=str, default=None, help="Signing sheet image (defaults to the student's most recent stored sheet)")
    parser.add_argument("--xml", type=str, default=str(Config.XML_PATH), help="Path to student info XML metadata")
    parser.add_argument("--db", type=str, default=str(Config.DB_PATH), help="Path to SQLite database")
    parser.add_argument("--threshold", type=float, default=Config.DEFAULT_SSIM_THRESHOLD, help="SSIM threshold for flagging anomalies")

    args = parser.parse_args()

    if not args.student_id:
        logger.info("No student ID provided. Usage: python investigate.py <student_id> [--sheet PATH]")
        return

    db = DatabaseManager(Path(args.db))
    try:
        sheet_path = resolve_sheet_path(args.sheet, args.student_id, db)
        result = verify_student_signature(
            student_id=args.student_id,
            sheet_path=sheet_path,
            xml_path=Path(args.xml),
            threshold=args.threshold,
        )
    except (FileNotFoundError, ValueError, IndexError) as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info(
        f"SSIM: {result.ssim_score:.3f} (threshold {args.threshold:.2f}) | "
        f"ORB good matches: {result.orb_matches} (min {Config.ORB_MIN_MATCHES}) -> {result.verdict}"
    )
    print(f"\nStudent: {result.student_name} ({result.student_id})")
    print(f"Sheet: {result.sheet_path}")
    print(f"SSIM similarity: {result.ssim_score:.3f}  |  ORB matches: {result.orb_matches}")
    print(f"Verdict: {result.verdict}")
    if result.low_confidence:
        print("⚠️  Table geometry was estimated, not detected — spot-check this result against the photo.")
    print()


if __name__ == "__main__":
    main()
