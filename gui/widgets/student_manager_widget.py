"""Dialog for visually adding, editing, and removing students in info.xml."""

from pathlib import Path

from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from core.db.xml_parser import parse_student_info_xml, write_student_info_xml
from core.utils.config import Config
from core.utils.logger import setup_logger

logger = setup_logger("gui.widgets.student_manager_widget")

COLUMNS = ["Student ID", "Name", "Title", "Course", "Baseline Signature Path"]


class StudentManagerDialog(QDialog):
    """Lets a user add/edit/remove student roster entries and save them back to info.xml."""

    def __init__(self, xml_path: Path = None, parent=None):
        super().__init__(parent)
        self.xml_path = xml_path or Config.XML_PATH
        self.setWindowTitle("👥 Manage Students — info.xml")
        self.resize(760, 420)

        layout = QVBoxLayout(self)

        self.table = QTableWidget(0, len(COLUMNS), self)
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.status_label = QLabel("", self)
        layout.addWidget(self.status_label)

        button_row = QHBoxLayout()
        self.btn_add = QPushButton("➕ Add Student", self)
        self.btn_add.clicked.connect(self.add_row)
        button_row.addWidget(self.btn_add)

        self.btn_delete = QPushButton("🗑 Delete Selected", self)
        self.btn_delete.clicked.connect(self.delete_selected_rows)
        button_row.addWidget(self.btn_delete)

        self.btn_browse = QPushButton("📂 Browse Signature...", self)
        self.btn_browse.clicked.connect(self.browse_signature_for_selected_row)
        button_row.addWidget(self.btn_browse)

        button_row.addStretch(1)

        self.btn_save = QPushButton("💾 Save to info.xml", self)
        self.btn_save.clicked.connect(self.save_to_xml)
        button_row.addWidget(self.btn_save)

        self.btn_close = QPushButton("Close", self)
        self.btn_close.clicked.connect(self.close)
        button_row.addWidget(self.btn_close)

        layout.addLayout(button_row)

        self.load_from_xml()

    def load_from_xml(self):
        students = parse_student_info_xml(self.xml_path)
        self.table.setRowCount(0)
        for student in students:
            self._append_row(
                student.student_id,
                student.name,
                student.title or "",
                student.course_code,
                student.baseline_signature_path or "",
            )
        self.status_label.setText(f"Loaded {len(students)} student(s) from {self.xml_path}")

    def _append_row(self, student_id: str, name: str, title: str, course: str, signature_path: str):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for col, value in enumerate([student_id, name, title, course, signature_path]):
            self.table.setItem(row, col, QTableWidgetItem(value))

    def add_row(self):
        self._append_row("", "", "", "CS402", "")
        self.table.setCurrentCell(self.table.rowCount() - 1, 0)

    def delete_selected_rows(self):
        rows = sorted({idx.row() for idx in self.table.selectedIndexes()}, reverse=True)
        if not rows:
            self.status_label.setText("Select a row first to delete it.")
            return
        for row in rows:
            self.table.removeRow(row)
        self.status_label.setText(f"Removed {len(rows)} row(s). Click Save to persist.")

    def browse_signature_for_selected_row(self):
        row = self.table.currentRow()
        if row < 0:
            self.status_label.setText("Select a row first to attach a signature file.")
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Baseline Signature Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.table.setItem(row, COLUMNS.index("Baseline Signature Path"), QTableWidgetItem(file_path))

    def save_to_xml(self):
        from core.models.schemas import Student

        students = []
        seen_ids = set()
        for row in range(self.table.rowCount()):
            student_id = self._cell_text(row, "Student ID")
            name = self._cell_text(row, "Name")
            if not student_id or not name:
                QMessageBox.warning(
                    self, "Missing required field",
                    f"Row {row + 1}: Student ID and Name are required. Fix or delete this row before saving."
                )
                return
            if student_id in seen_ids:
                QMessageBox.warning(
                    self, "Duplicate Student ID",
                    f"Student ID '{student_id}' appears more than once. Each student needs a unique ID."
                )
                return
            seen_ids.add(student_id)

            students.append(
                Student(
                    student_id=student_id,
                    name=name,
                    course_code=self._cell_text(row, "Course") or "CS402",
                    baseline_signature_path=self._cell_text(row, "Baseline Signature Path") or None,
                    title=self._cell_text(row, "Title") or None,
                )
            )

        write_student_info_xml(self.xml_path, students)
        self.status_label.setText(f"Saved {len(students)} student(s) to {self.xml_path}")

    def _cell_text(self, row: int, column_name: str) -> str:
        item = self.table.item(row, COLUMNS.index(column_name))
        return item.text().strip() if item else ""
