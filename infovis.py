#!/usr/bin/env python3
"""Student Visualization & Statistics CLI Interface (Information Visualization).

Usage:
    python infovis.py 10000409
    python infovis.py --student-id 10000409
"""

import argparse
from pathlib import Path
from core.utils.config import Config
from core.utils.logger import setup_logger
from core.db.db_manager import DatabaseManager

logger = setup_logger("infovis_cli")


def main():
    parser = argparse.ArgumentParser(description="Student Attendance Data Visualization Engine")
    parser.add_argument("student_id_pos", type=str, nargs="?", default=None, help="Student ID to plot history for (positional form)")
    parser.add_argument("--student-id", type=str, help="Student ID to plot history for", default=None)
    parser.add_argument("--db", type=str, help="Path to SQLite database", default=str(Config.DB_PATH))
    parser.add_argument("--save-chart", type=str, help="Output path for chart image", default=None)
    parser.add_argument("--no-gui", action="store_true", help="Disable GUI pop-up window")

    args = parser.parse_args()
    student_id = args.student_id or args.student_id_pos

    db = DatabaseManager(Path(args.db))
    logger.info("Generating attendance visualization summary.")

    present_count = 0
    absent_count = 0
    proxy_count = 0

    if student_id:
        records = db.get_student_records(student_id)
        logger.info(f"Student '{student_id}' attendance record count: {len(records)}")
        for r in records:
            st = r.get("status", "").upper()
            if st == "PRESENT":
                present_count += 1
            elif st == "ABSENT":
                absent_count += 1
            elif st == "SUSPECTED_PROXY":
                proxy_count += 1
        chart_title = f"Attendance Distribution — Student {student_id}"
    else:
        # Query overall database totals
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM attendance_records GROUP BY status")
            rows = cursor.fetchall()
            for status, count in rows:
                st = status.upper()
                if st == "PRESENT":
                    present_count += count
                elif st == "ABSENT":
                    absent_count += count
                elif st == "SUSPECTED_PROXY":
                    proxy_count += count
        chart_title = "Overall Course Attendance Distribution"

    # Lazy import matplotlib when rendering charts
    import matplotlib.pyplot as plt
    
    statuses = ["PRESENT", "ABSENT", "SUSPECTED_PROXY"]
    counts = [present_count, absent_count, proxy_count]
    colors = ["#2ecc71", "#e74c3c", "#f39c12"]
    
    plt.figure(figsize=(8, 5))
    bars = plt.bar(statuses, counts, color=colors, width=0.5)
    plt.title(chart_title, fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Attendance Status", fontsize=11)
    plt.ylabel("Session Count", fontsize=11)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Value annotations on top of bars
    for bar in bars:
        height = bar.get_height()
        plt.annotate(f"{height}",
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),  # 3 points vertical offset
                     textcoords="offset points",
                     ha='center', va='bottom', fontweight="bold")

    plt.tight_layout()

    if args.save_chart:
        plt.savefig(args.save_chart)
        logger.info(f"Chart saved to: {args.save_chart}")

    if not args.no_gui:
        logger.info("Opening GUI visualization window...")
        plt.show()


if __name__ == "__main__":
    main()
