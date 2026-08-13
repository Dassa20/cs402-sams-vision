"""Unit tests for SQLite database manager and XML info parsing."""

from pathlib import Path
from core.db.db_manager import DatabaseManager
from core.db.xml_parser import parse_student_info_xml
from core.models.schemas import Student, AttendanceRecord, AttendanceStatus


def test_db_manager_lifecycle(tmp_path):
    db_file = tmp_path / "test_sams.db"
    db = DatabaseManager(db_file)
    
    assert db_file.exists()

    # Insert student
    students = [Student(student_id="STU_TEST", name="Test User", course_code="CS402")]
    db.insert_students(students)

    # Insert attendance record
    record = AttendanceRecord(
        record_id=None,
        sheet_id="sheet_001",
        student_id="STU_TEST",
        date="2026-07-24",
        status=AttendanceStatus.PRESENT
    )
    db.insert_attendance_record(record)

    # Fetch history
    history = db.get_student_records("STU_TEST")
    assert len(history) == 1
    assert history[0]["status"] == "PRESENT"


def test_parse_student_info_xml(tmp_path):
    xml_file = tmp_path / "info.xml"
    xml_content = """<?xml version="1.0"?>
    <students>
        <student>
            <id>STU001</id>
            <name>Alice</name>
            <course>CS402</course>
        </student>
    </students>
    """
    xml_file.write_text(xml_content)

    students = parse_student_info_xml(xml_file)
    assert len(students) == 1
    assert students[0].student_id == "STU001"
    assert students[0].name == "Alice"
