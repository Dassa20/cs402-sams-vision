# 🏗 Architecture & System Design — SAMS Vision

**Project:** CS402.3 Computer Graphics and Visualization Coursework  
**System Name:** Student Attendance Management System (SAMS Vision)  
**Target Platform:** Cross-Platform Desktop (macOS / Windows)  

---

## 📌 Executive Summary

SAMS Vision is an automated student attendance processing and signature verification platform built with Python. The system ingests smartphone snapshot images of physical signing sheets along with XML student metadata (`info.xml`), processes the images using computer vision pipelines to determine attendance status, stores structured records in a local SQLite database (`sams.db`), renders statistical data visualizations, and performs baseline signature comparison to detect anomalies.

---

## 🏛 System Architecture & Design Principles

The architecture follows a **decoupled, layer-separated, and thread-safe** structure designed for scalable concurrent development across a **10-member team**.

### Key Architectural Guidelines
1. **Separation of Concerns**: Core processing logic (`core/`) is completely decoupled from presentation logic (`gui/`) and CLI interfaces (`sams.py`, `infovis.py`, `investigate.py`).
2. **Non-Blocking UI Threading**: All CPU-intensive computer vision operations (perspective transformation, binarization, SSIM matching) execute on background worker threads (`QThread` / thread pools) to maintain a smooth desktop user experience.
3. **Structured Data Contracts**: Shared strongly-typed data structures (`dataclasses`) are passed between modules instead of untyped raw dictionaries or tuples to reduce integration bugs.
4. **Modular Sub-packages**: `core/` is divided into functional domains (`vision/`, `verification/`, `db/`, `models/`, `utils/`) to prevent Git merge conflicts during team collaboration.

---

## 🛠 Technology Stack

| Layer | Technology / Library | Description |
| :--- | :--- | :--- |
| **Core Engine** | Python 3.10+ | Primary runtime environment across all modules. |
| **Computer Vision** | OpenCV (`opencv-python`), NumPy | Image loading, deskewing, binarization, contour analysis, cell extraction. |
| **GUI Framework** | `PyQt6` (or `PySide6`) | Cross-platform desktop interface with native event loops and `QThread` workers. |
| **Visualization** | `Matplotlib`, `Seaborn` | Attendance trends, bar graphs, and heatmaps embedded in GUI and CLI output. |
| **Verification Engine**| `scikit-image` (SSIM), OpenCV ORB | Structural Similarity Index (SSIM) and feature-matching signature comparison. |
| **Data & Persistence** | `xml.etree.ElementTree`, `sqlite3` | XML ingestion (`info.xml`) and relational storage (`sams.db`). |
| **Testing & Quality** | `pytest` | Unit, integration, and image processing pipeline validation. |

---

## 📸 Computer Vision Processing Pipeline

The image processing engine handles smartphone snapshots under varying lighting, rotation, and perspective conditions:

```
[ Input Image ] ──► [ 1. Preprocessing & Homography ] ──► [ 2. Grid & Cell Segmentation ]
                                                                        │
                                                                        ▼
[ Attendance DB ] ◄── [ 4. DB Storage & Result Export ] ◄── [ 3. Cell Ink Analysis ]
```

1. **Preprocessing & Perspective Correction**:
   - Quadrilateral contour detection, perspective transform (homography), Adaptive Binarization to handle real-world shadows.
   - Session date is supplied via `--date` (defaults to today) — the sheet photo's header/lecturer text is not OCR'd.
2. **Grid & Cell Segmentation**:
   - Contour-based table boundary detection, then horizontal/vertical line detection to isolate individual student signature cells. Falls back to an estimated layout (flagged as `low_confidence`) if real grid lines can't be traced on a given photo.
3. **Cell Analysis & Signature Matching**:
   - Signature presence detection combining Blue Pen Color Differential ($B - R > 15$) and Laplacian High-Pass Edge Frequency ($|\nabla^2 I_{gray}| > 30$).
   - Structural Similarity Index (SSIM) and ORB feature point matching against baseline reference signatures (`core/investigation.py`, used by `investigate.py` and the GUI's Verify Signature dialog).
4. **Data Persistence & Visualization**:
   - Records dated results into `sams.db` and renders summary reports via Matplotlib canvases.

> **Known limitation**: signature detection is pure ink/edge pixel density — it has no text understanding, so a handwritten annotation like "ab"/"absent" written inside the signature box can be misread as a signature if it has enough ink coverage. Robustly fixing this would require OCR (e.g. Tesseract), which is not currently a project dependency.

---

## 📁 Repository & Directory Layout

```text
cs402-sams-vision/
├── core/
│   ├── __init__.py
│   ├── pipeline.py              # Shared ingestion pipeline used by sams.py and the GUI worker
│   ├── investigation.py         # Shared signature-verification logic used by investigate.py and the GUI
│   ├── models/                  # Shared strongly-typed data contracts
│   │   ├── __init__.py
│   │   └── schemas.py           # Student, AttendanceRecord, CellCrop, VerificationResult
│   ├── vision/                  # Image processing pipeline
│   │   ├── __init__.py
│   │   ├── preprocessor.py      # Deskewing, shadow removal, thresholding
│   │   ├── grid_extractor.py    # Table/cell detection and grid cropping
│   │   └── classifier.py        # Signature presence detection (ink/edge density)
│   ├── verification/            # Signature verification logic
│   │   ├── __init__.py
│   │   ├── ssim_matcher.py      # SSIM algorithm implementation
│   │   └── feature_matcher.py   # ORB feature-matching comparison
│   ├── db/                      # Persistence & metadata parsing
│   │   ├── __init__.py
│   │   ├── db_manager.py        # SQLite connection manager & SQL queries
│   │   └── xml_parser.py        # Student XML info mapping (`info.xml`), read + write
│   └── utils/                   # Shared utilities & configuration
│       ├── __init__.py
│       ├── config.py            # SSIM thresholds, image parameters, paths
│       └── logger.py            # Centralized logging setup
├── gui/
│   ├── __init__.py
│   ├── app.py                   # Main PyQt desktop application layout
│   ├── theme.py                 # App-wide QSS stylesheet
│   ├── workers.py               # Background thread handlers for async CV execution
│   └── widgets/                 # Reusable UI component widgets
│       ├── __init__.py
│       ├── preview_widget.py         # Frame preview & step-by-step processing inspector
│       ├── chart_widget.py           # Embedded Matplotlib canvas component
│       ├── student_manager_widget.py # Add/edit/remove students in info.xml
│       └── verification_widget.py    # Pick student + dated sheet, compare vs. baseline signature
├── tests/                       # Automated test suite
│   ├── test_vision.py           # Preprocessing & segmentation tests
│   ├── test_verification.py     # Signature SSIM matching unit tests
│   └── test_db.py               # SQLite schema & XML ingestion tests
├── data/
│   ├── info.xml                 # Student metadata file
│   ├── signatures/               # Baseline reference signature crops, one per student
│   └── sams.db                  # Relational SQLite database instance (git-ignored, created at runtime)
├── test_images/                 # Input signing sheet snapshots (.png / .jpg)
├── sams.py                      # CLI entry point for main attendance processing
├── infovis.py                   # CLI entry point for student visualization
├── investigate.py              # CLI entry point for signature verification
├── requirements.txt             # Python project dependencies
├── ARCHITECTURE.md              # Project architectural guide
└── README.md                    # Setup and usage instructions
```

---

## ⚡ Concurrency & Threading Strategy

To keep the GUI responsive during heavy computer vision execution:

- **GUI Main Thread**: Handles user interactions, window rendering, and event dispatching.
- **Worker Threads (`gui/workers.py`)**: Executes `core.vision` and `core.verification` pipelines off the main thread.
- **Signal/Slot Mechanism**: Worker threads communicate progress (`0-100%`) and intermediate preview images to `preview_widget.py` via PyQt signals.

---

## 🧪 Testing & Quality Assurance Plan

- **Unit Tests**: Test `xml_parser.py`, database queries in `db_manager.py`, and `ssim_matcher.py` independently using `pytest`.
- **CV Pipeline Integration Tests**: Run sample image sheets from `test_images/` through `preprocessor.py` and `grid_extractor.py` to verify bounding box accuracy.
- **Regression Suite**: Ensure changes made by one team member do not break signature thresholding or database constraints.