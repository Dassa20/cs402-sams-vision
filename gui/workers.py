"""PyQt QThread background worker for non-blocking computer vision execution."""

from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QThread, pyqtSignal

from core.db.db_manager import DatabaseManager
from core.pipeline import process_attendance_sheet
from core.utils.config import Config
from core.utils.logger import setup_logger

logger = setup_logger("gui.workers")


class AttendanceProcessorWorker(QThread):
    """Executes heavy OpenCV pre-processing and SSIM signature matching off the UI main thread."""

    progress = pyqtSignal(int)          # Percentage complete (0-100)
    step_message = pyqtSignal(str)      # Description of current step
    preview_image = pyqtSignal(str, object)  # (stage name, OpenCV numpy frame)
    finished = pyqtSignal(dict)         # Final results dictionary
    failed = pyqtSignal(str)            # Error message on failure

    def __init__(self, image_path: str, xml_path: str, date: str = None):
        super().__init__()
        self.image_path = image_path
        self.xml_path = xml_path
        self.date = date or datetime.now().strftime("%Y-%m-%d")

    def run(self):
        try:
            logger.info("Starting background CV processing thread.")
            db = DatabaseManager(Path(Config.DB_PATH))

            result = process_attendance_sheet(
                sheet_path=Path(self.image_path),
                xml_path=Path(self.xml_path),
                db=db,
                date=self.date,
                on_progress=lambda pct, msg: (self.progress.emit(pct), self.step_message.emit(msg)),
                on_preview=lambda stage, img: self.preview_image.emit(stage, img),
            )

            self.finished.emit({
                "status": "success",
                "processed_count": len(result.records),
                "present_count": result.present_count,
                "absent_count": result.absent_count,
                "low_confidence": result.low_confidence,
            })
        except Exception as e:
            logger.error(f"Worker thread error: {e}")
            self.failed.emit(str(e))
