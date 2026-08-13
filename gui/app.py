"""Main Desktop PyQt Application Shell for SAMS Vision."""

import sys
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
    QPushButton,
    QProgressBar,
    QLabel,
    QFileDialog,
)
from gui.theme import STYLESHEET
from gui.widgets.preview_widget import PreviewWidget
from gui.widgets.chart_widget import ChartWidget
from gui.widgets.student_manager_widget import StudentManagerDialog
from gui.widgets.verification_widget import SignatureVerificationDialog
from gui.workers import AttendanceProcessorWorker
from core.utils.logger import setup_logger

logger = setup_logger("gui.app")


def _card(title: str) -> tuple[QFrame, QVBoxLayout]:
    """Builds a titled panel frame so sections read as distinct cards, not bare widgets."""
    frame = QFrame()
    frame.setObjectName("card")
    layout = QVBoxLayout(frame)
    layout.setContentsMargins(14, 12, 14, 14)
    heading = QLabel(title)
    heading.setObjectName("sectionHeading")
    layout.addWidget(heading)
    return frame, layout


class MainWindow(QMainWindow):
    """Main Application Window layout."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SAMS Vision — Student Attendance & Signature Verification")
        self.resize(1080, 700)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(12)

        title_label = QLabel("👁 SAMS Vision")
        title_label.setObjectName("appTitle")
        main_layout.addWidget(title_label)
        subtitle_label = QLabel("Image-processing attendance ingestion & signature verification")
        subtitle_label.setObjectName("appSubtitle")
        main_layout.addWidget(subtitle_label)

        # Actions card
        actions_card, actions_layout = _card("Actions")
        control_layout = QHBoxLayout()
        self.btn_open_sheet = QPushButton("📂 Load Sheet Image", self)
        self.btn_open_sheet.setObjectName("secondaryButton")
        self.btn_open_sheet.clicked.connect(self.select_sheet_image)
        control_layout.addWidget(self.btn_open_sheet)

        self.btn_process = QPushButton("⚡ Process Attendance", self)
        self.btn_process.clicked.connect(self.run_processing)
        control_layout.addWidget(self.btn_process)

        self.btn_manage_students = QPushButton("👥 Manage Students", self)
        self.btn_manage_students.setObjectName("secondaryButton")
        self.btn_manage_students.clicked.connect(self.open_student_manager)
        control_layout.addWidget(self.btn_manage_students)

        self.btn_verify_signature = QPushButton("🔍 Verify Signature", self)
        self.btn_verify_signature.setObjectName("secondaryButton")
        self.btn_verify_signature.clicked.connect(self.open_verification_dialog)
        control_layout.addWidget(self.btn_verify_signature)

        actions_layout.addLayout(control_layout)
        main_layout.addWidget(actions_card)

        # Status card
        status_card, status_layout = _card("Status")
        self.status_label = QLabel("Ready", self)
        status_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setValue(0)
        status_layout.addWidget(self.progress_bar)
        main_layout.addWidget(status_card)

        # Content split: vision pipeline preview + attendance chart
        content_layout = QHBoxLayout()
        content_layout.setSpacing(12)

        preview_card, preview_layout = _card("🖼 Vision Pipeline Inspector")
        self.preview_widget = PreviewWidget(self)
        preview_layout.addWidget(self.preview_widget)
        content_layout.addWidget(preview_card, stretch=1)

        chart_card, chart_layout = _card("📊 Attendance Summary")
        self.chart_widget = ChartWidget(self)
        chart_layout.addWidget(self.chart_widget)
        content_layout.addWidget(chart_card, stretch=1)

        main_layout.addLayout(content_layout, stretch=1)

        self.selected_image_path = None
        self.worker = None

    def select_sheet_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Attendance Sheet", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.selected_image_path = file_path
            self.preview_widget.set_status_text(f"Selected:\n{file_path}")
            self.status_label.setText(f"Loaded: {file_path}")

    def run_processing(self):
        if not self.selected_image_path:
            self.status_label.setText("⚠️ Please select an attendance sheet image first.")
            return

        self.btn_process.setEnabled(False)
        self.worker = AttendanceProcessorWorker(self.selected_image_path, "data/info.xml")
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.step_message.connect(self.status_label.setText)
        self.worker.preview_image.connect(self.preview_widget.set_image)
        self.worker.finished.connect(self.on_processing_complete)
        self.worker.failed.connect(self.on_processing_failed)
        self.worker.start()

    def on_processing_complete(self, results: dict):
        present = results.get("present_count", 0)
        absent = results.get("absent_count", 0)
        summary = f"✅ Processing Complete! {present} present, {absent} absent."
        if results.get("low_confidence"):
            summary += " ⚠️ Table geometry was estimated, not detected — verify results against the photo."
        self.status_label.setText(summary)
        self.chart_widget.update_chart(present, absent, title=f"Attendance Summary — {Path(self.selected_image_path).name}")
        self.btn_process.setEnabled(True)

    def on_processing_failed(self, error_msg: str):
        self.status_label.setText(f"❌ Error: {error_msg}")
        self.btn_process.setEnabled(True)

    def open_student_manager(self):
        dialog = StudentManagerDialog(parent=self)
        dialog.exec()

    def open_verification_dialog(self):
        dialog = SignatureVerificationDialog(parent=self)
        dialog.exec()


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
