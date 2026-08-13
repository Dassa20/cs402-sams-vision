"""App-wide QSS stylesheet for SAMS Vision's dark, indigo-accented look."""

STYLESHEET = """
QWidget {
    background-color: #12141c;
    color: #e6e6f0;
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #12141c;
}

QLabel#appTitle {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    padding: 4px 0px;
}

QLabel#appSubtitle {
    color: #8a8fa3;
    font-size: 12px;
    padding-bottom: 6px;
}

QFrame#card {
    background-color: #1a1d29;
    border: 1px solid #2a2e40;
    border-radius: 10px;
}

QLabel#sectionHeading {
    color: #a99bff;
    font-weight: 600;
    font-size: 13px;
    padding: 2px 0px;
}

QLabel#verdictLabel {
    background-color: #1a1d29;
    border: 1px solid #2a2e40;
    border-radius: 8px;
    padding: 10px;
}

QPushButton {
    background-color: #6c5ce7;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    padding: 9px 16px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #7d6df0;
}

QPushButton:pressed {
    background-color: #5a4bd1;
}

QPushButton:disabled {
    background-color: #33364a;
    color: #6f7285;
}

QPushButton#secondaryButton {
    background-color: #232637;
    color: #cfd2e6;
    border: 1px solid #34384d;
}

QPushButton#secondaryButton:hover {
    background-color: #2b2f45;
}

QProgressBar {
    background-color: #1e2130;
    border: 1px solid #2a2e40;
    border-radius: 8px;
    text-align: center;
    color: #e6e6f0;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #00d1b2;
    border-radius: 7px;
}

QTableWidget {
    background-color: #1a1d29;
    gridline-color: #2a2e40;
    border: 1px solid #2a2e40;
    border-radius: 8px;
    selection-background-color: #3a3470;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #232637;
    color: #a99bff;
    padding: 6px;
    border: none;
    font-weight: 600;
}

QComboBox, QLineEdit {
    background-color: #1e2130;
    border: 1px solid #2a2e40;
    border-radius: 6px;
    padding: 6px 8px;
    color: #e6e6f0;
}

QComboBox QAbstractItemView {
    background-color: #1e2130;
    color: #e6e6f0;
    selection-background-color: #6c5ce7;
}

QScrollBar:vertical {
    background: #12141c;
    width: 10px;
}

QScrollBar::handle:vertical {
    background: #34384d;
    border-radius: 5px;
    min-height: 24px;
}
"""
