#!/usr/bin/env python3
"""SAMS Vision Main Attendance Processing CLI Interface.

Usage:
    python sams.py --sheet test_images/sample_sheet.jpg --xml data/info.xml
    python sams.py test_images/sample_sheet.jpg data/info.xml
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from core.utils.config import Config
from core.utils.logger import setup_logger
from core.db.db_manager import DatabaseManager
from core.db.xml_parser import parse_student_info_xml
from core.pipeline import process_attendance_sheet

logger = setup_logger("sams_cli")


def main():
    parser = argparse.ArgumentParser(description="SAMS Vision Attendance Processing CLI")
    parser.add_argument("sheet_pos", type=str, nargs="?", default=None, help="Path to physical signing sheet image (positional form)")
    parser.add_argument("xml_pos", type=str, nargs="?", default=None, help="Path to student info XML metadata (positional form)")
    parser.add_argument("--sheet", type=str, help="Path to physical signing sheet image", default=None)
    parser.add_argument("--xml", type=str, help="Path to student info XML metadata", default=None)
    parser.add_argument("--db", type=str, help="Path to SQLite database", default=str(Config.DB_PATH))
    parser.add_argument("--date", type=str, help="Date of attendance (YYYY-MM-DD)", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--reset", action="store_true", help="Clear all database data")

    args = parser.parse_args()
    sheet_arg = args.sheet or args.sheet_pos
    xml_arg = args.xml or args.xml_pos or str(Config.XML_PATH)

    logger.info("Initializing SAMS Vision Attendance Ingestion Engine.")
    db = DatabaseManager(Path(args.db))

    if args.reset:
        db.clear_all_data()
        logger.info("Database reset complete. All records cleared.")
        if not sheet_arg:
            return

    xml_path = Path(xml_arg)

    if not sheet_arg:
        # Parse XML student metadata even without a sheet, so --xml alone can seed the DB.
        students = parse_student_info_xml(xml_path)
        if students:
            db.insert_students(students)
            logger.info(f"Loaded {len(students)} student records into database.")
        logger.info("No sheet argument provided. Initialization completed.")
        return

    sheet_path = Path(sheet_arg)
    if not sheet_path.exists():
        logger.error(f"Sheet image file not found: {sheet_path}")
        sys.exit(1)

    logger.info(f"Processing sheet: {sheet_path} for Date: {args.date}")
    result = process_attendance_sheet(
        sheet_path=sheet_path,
        xml_path=xml_path,
        db=db,
        date=args.date,
    )

    if result.low_confidence:
        logger.warning(
            "Table geometry could not be confirmed by real grid-line detection on this sheet — "
            "verify attendance results against the photo before trusting them."
        )

    logger.info(
        f"Attendance ingestion finished successfully. "
        f"{result.present_count} present, {result.absent_count} absent."
    )


if __name__ == "__main__":
    main()
