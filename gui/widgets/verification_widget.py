"""Dialog for verifying a student's signature on a specific dated sheet against their baseline."""

from pathlib import Path

import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from core.db.db_manager import DatabaseManager
from core.db.xml_parser import parse_student_info_xml
from core.investigation import verify_student_signature
from core.utils.config import Config
from core.utils.logger import setup_logger

logger = setup_logger("gui.widgets.verification_widget")


def _to_pixmap(image: np.ndarray, target_w: int = 320, target_h: int = 140) -> QPixmap:
    if image.ndim == 2:
        frame = np.ascontiguousarray(image)
        h, w = frame.shape
        qimage = QImage(frame.data, w, h, w, QImage.Format.Format_Grayscale8)
    else:
        frame = np.ascontiguousarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        h, w, ch = frame.shape
        qimage = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)
    return QPixmap.fromImage(qimage).scaled(
        target_w, target_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
    )


class SignatureVerificationDialog(QDialog):
    """Lets a user pick a student + a specific dated sheet and check the signature against baseline."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Verify Signature")
        self.resize(680, 480)
        self.db = DatabaseManager(Path(Config.DB_PATH))
        self.custom_sheet_path: str = None

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.student_combo = QComboBox(self)
        self.students = parse_student_info_xml(Path(Config.XML_PATH))
        for student in self.students:
            self.student_combo.addItem(f"{student.student_id} — {student.name}", student.student_id)
        self.student_combo.currentIndexChanged.connect(self.refresh_sheet_options)
        form.addRow("Student:", self.student_combo)

        self.sheet_combo = QComboBox(self)
        form.addRow("Attendance date / sheet:", self.sheet_combo)

        browse_row = QHBoxLayout()
        self.btn_browse_sheet = QPushButton("📂 Use a different sheet image...", self)
        self.btn_browse_sheet.clicked.connect(self.browse_sheet)
        browse_row.addWidget(self.btn_browse_sheet)
        self.custom_sheet_label = QLabel("", self)
        browse_row.addWidget(self.custom_sheet_label, stretch=1)
        form.addRow("", browse_row)

        layout.addLayout(form)

        self.btn_verify = QPushButton("✅ Run Verification", self)
        self.btn_verify.clicked.connect(self.run_verification)
        layout.addWidget(self.btn_verify)

        images_row = QHBoxLayout()
        baseline_col = QVBoxLayout()
        baseline_col.addWidget(QLabel("Baseline (on file)", self))
        self.baseline_image_label = QLabel("—", self)
        self.baseline_image_label.setMinimumSize(320, 140)
        self.baseline_image_label.setStyleSheet("border: 1px solid #555; background: #1e1e1e;")
        self.baseline_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        baseline_col.addWidget(self.baseline_image_label)
        images_row.addLayout(baseline_col)

        extracted_col = QVBoxLayout()
        extracted_col.addWidget(QLabel("Extracted from sheet", self))
        self.extracted_image_label = QLabel("—", self)
        self.extracted_image_label.setMinimumSize(320, 140)
        self.extracted_image_label.setStyleSheet("border: 1px solid #555; background: #1e1e1e;")
        self.extracted_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        extracted_col.addWidget(self.extracted_image_label)
        images_row.addLayout(extracted_col)

        layout.addLayout(images_row)

        self.result_label = QLabel("Pick a student and a sheet, then run verification.", self)
        self.result_label.setWordWrap(True)
        self.result_label.setObjectName("verdictLabel")
        layout.addWidget(self.result_label)

        self.btn_close = QPushButton("Close", self)
        self.btn_close.clicked.connect(self.close)
        layout.addWidget(self.btn_close)

        self.refresh_sheet_options()

    def current_student_id(self) -> str:
        return self.student_combo.currentData()

    def refresh_sheet_options(self):
        self.sheet_combo.clear()
        student_id = self.current_student_id()
        if not student_id:
            return
        records = self.db.get_student_records(student_id)
        if not records:
            self.sheet_combo.addItem("(no stored attendance records for this student)", None)
            return
        for record in records:
            label = f"{record['date']} — sheet '{record['sheet_id']}' ({record['status']})"
            self.sheet_combo.addItem(label, record["sheet_id"])

    def browse_sheet(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Signing Sheet Image", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.custom_sheet_path = file_path
            self.custom_sheet_label.setText(Path(file_path).name)

    def resolve_sheet_path(self) -> Path:
        if self.custom_sheet_path:
            return Path(self.custom_sheet_path)
        sheet_id = self.sheet_combo.currentData()
        if not sheet_id:
            raise FileNotFoundError("No sheet selected. Process a sheet first, or browse to an image file.")
        for ext in (".jpeg", ".jpg", ".png"):
            candidate = Config.TEST_IMAGES_DIR / f"{sheet_id}{ext}"
            if candidate.exists():
                return candidate
        raise FileNotFoundError(f"Could not locate image file for sheet '{sheet_id}'. Use 'Browse' instead.")

    def run_verification(self):
        student_id = self.current_student_id()
        if not student_id:
            return
        try:
            sheet_path = self.resolve_sheet_path()
            result = verify_student_signature(
                student_id=student_id,
                sheet_path=sheet_path,
                xml_path=Path(Config.XML_PATH),
            )
        except (FileNotFoundError, ValueError, IndexError) as e:
            QMessageBox.warning(self, "Verification failed", str(e))
            return

        self.baseline_image_label.setPixmap(_to_pixmap(result.baseline_crop))
        self.extracted_image_label.setPixmap(_to_pixmap(result.extracted_crop))

        color = "#e74c3c" if result.is_anomaly else "#2ecc71"
        warning_html = ""
        if result.low_confidence:
            warning_html = (
                "<br><span style='color:#f39c12;'>⚠️ Table geometry was estimated, not detected — "
                "spot-check this result against the photo.</span>"
            )
        self.result_label.setText(
            f"<b>{result.student_name} ({result.student_id})</b> — sheet: {result.sheet_path.name}<br>"
            f"SSIM similarity: {result.ssim_score:.3f} &nbsp;|&nbsp; ORB matches: {result.orb_matches}<br>"
            f"<span style='color:{color}; font-weight:bold;'>{result.verdict}</span>"
            f"{warning_html}"
        )
