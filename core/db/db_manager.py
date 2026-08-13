"""SQLite database manager for student attendance persistence."""

import sqlite3
from typing import List, Optional
from pathlib import Path
from core.models.schemas import Student, AttendanceRecord, AttendanceStatus
from core.utils.logger import setup_logger

logger = setup_logger("core.db.db_manager")


class DatabaseManager:
    """Manages SQLite connection lifecycle and relational schema queries."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Initializes database relational tables if they do not exist."""
        logger.info(f"Initializing database tables at: {self.db_path}")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Students table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    student_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    course_code TEXT NOT NULL,
                    baseline_signature_path TEXT
                )
            """)
            # Attendance Records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance_records (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sheet_id TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    ssim_score REAL,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )
            """)
            conn.commit()

    def insert_students(self, students: List[Student]):
        """Inserts or replaces student records in bulk."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT OR REPLACE INTO students (student_id, name, course_code, baseline_signature_path)
                VALUES (?, ?, ?, ?)
            """, [(s.student_id, s.name, s.course_code, s.baseline_signature_path) for s in students])
            conn.commit()

    def insert_attendance_record(self, record: AttendanceRecord):
        """Inserts a single student attendance record."""
        ssim = record.verification.ssim_score if record.verification else None
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO attendance_records (sheet_id, student_id, date, status, ssim_score)
                VALUES (?, ?, ?, ?, ?)
            """, (record.sheet_id, record.student_id, record.date, record.status.value, ssim))
            conn.commit()

    def clear_all_data(self):
        """Clears all records from attendance_records and students tables."""
        logger.info("Clearing all data from database tables.")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM attendance_records")
            cursor.execute("DELETE FROM students")
            conn.commit()

    def get_student_records(self, student_id: str) -> List[dict]:
        """Fetches all attendance history for a given student ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sheet_id, date, status, ssim_score
                FROM attendance_records
                WHERE student_id = ?
                ORDER BY date DESC
            """, (student_id,))
            rows = cursor.fetchall()
            return [{"sheet_id": r[0], "date": r[1], "status": r[2], "ssim_score": r[3]} for r in rows]
