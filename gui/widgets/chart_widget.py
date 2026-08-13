"""Embedded Matplotlib canvas widget for rendering attendance statistical charts."""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartWidget(QWidget):
    """Embeds Matplotlib FigureCanvas for PyQt user interfaces."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)
        
        self.render_sample_chart()

    def render_sample_chart(self):
        """Draws a placeholder chart before any sheet has been processed."""
        self.update_chart(present=0, absent=0, suspected=0, title="Attendance Summary (no sheet processed yet)")

    def update_chart(self, present: int, absent: int, suspected: int = 0, title: str = "Attendance Summary"):
        """Redraws the bar chart with real counts from a processed attendance sheet."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        categories = ["Present", "Absent", "Suspected Proxy"]
        counts = [present, absent, suspected]
        colors = ["#2ecc71", "#e74c3c", "#f39c12"]

        ax.bar(categories, counts, color=colors)
        ax.set_title(title)
        ax.set_ylabel("Student Count")
        self.canvas.draw()
