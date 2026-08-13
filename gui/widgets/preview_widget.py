"""Image processing step-by-step preview inspector widget."""

import cv2
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget


class PreviewWidget(QWidget):
    """Renders processed image frames (Original, Deskewed, Greyscale, Binarized)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.title_label = QLabel("📷 Image Processing Inspector", self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        self.stage_label = QLabel("", self)
        self.stage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.stage_label.setStyleSheet("font-weight: bold;")
        self.layout.addWidget(self.stage_label)

        self.image_display = QLabel("No image loaded", self)
        self.image_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_display.setStyleSheet("border: 2px dashed #888; background: #222; color: #ccc; font-size: 14px;")
        self.image_display.setMinimumSize(400, 300)
        self.layout.addWidget(self.image_display)

    def set_status_text(self, text: str):
        self.stage_label.setText("")
        self.image_display.setText(text)

    def set_image(self, stage_name: str, image: np.ndarray):
        """Displays an OpenCV BGR or single-channel frame for the given pipeline stage."""
        if image is None or image.size == 0:
            return

        self.stage_label.setText(stage_name)

        if image.ndim == 2:
            frame = np.ascontiguousarray(image)
            h, w = frame.shape
            qimage = QImage(frame.data, w, h, w, QImage.Format.Format_Grayscale8)
        else:
            frame = np.ascontiguousarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            h, w, ch = frame.shape
            qimage = QImage(frame.data, w, h, ch * w, QImage.Format.Format_RGB888)

        pixmap = QPixmap.fromImage(qimage).scaled(
            self.image_display.width() or 400,
            self.image_display.height() or 300,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.image_display.setPixmap(pixmap)
