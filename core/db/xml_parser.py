"""XML parser for student metadata ingestion from info.xml."""

import xml.etree.ElementTree as ET
from typing import List
from pathlib import Path
from core.models.schemas import Student
from core.utils.logger import setup_logger

logger = setup_logger("core.db.xml_parser")


def parse_student_info_xml(xml_path: Path) -> List[Student]:
    """Parses student metadata from an info.xml metadata file.

    Returns:
        List of Student dataclass objects.
    """
    logger.info(f"Parsing XML metadata from: {xml_path}")
    path = Path(xml_path)
    if not path.exists():
        logger.warning(f"XML file not found at {xml_path}. Returning empty list.")
        return []

    tree = ET.parse(path)
    root = tree.getroot()

    students: List[Student] = []
    for elem in root.findall("student"):
        s_id = elem.findtext("id", "")
        name = elem.findtext("name", "")
        title = elem.findtext("title", None)
        course = elem.findtext("course", "CS402")
        sig_path = elem.findtext("signature_path", None)

        students.append(
            Student(
                student_id=s_id,
                name=name,
                course_code=course,
                baseline_signature_path=sig_path,
                title=title,
            )
        )
    logger.info(f"Successfully parsed {len(students)} student records from XML.")
    return students


def write_student_info_xml(xml_path: Path, students: List[Student], subject_code: str = "CGV") -> None:
    """Writes student metadata back out to an info.xml metadata file.

    Preserves the root `<students course="...">` attribute from the existing file if one is
    present, since that attribute (subject code) is separate from each student's `course_code`
    (degree programme) and isn't modeled on the Student dataclass.
    """
    path = Path(xml_path)
    if path.exists():
        try:
            existing_root = ET.parse(path).getroot()
            subject_code = existing_root.get("course", subject_code)
        except ET.ParseError:
            pass

    root = ET.Element("students", {"course": subject_code})
    for student in students:
        elem = ET.SubElement(root, "student")
        ET.SubElement(elem, "id").text = student.student_id
        if student.title:
            ET.SubElement(elem, "title").text = student.title
        ET.SubElement(elem, "name").text = student.name
        ET.SubElement(elem, "course").text = student.course_code
        if student.baseline_signature_path:
            ET.SubElement(elem, "signature_path").text = student.baseline_signature_path

    ET.indent(root, space="    ")
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="UTF-8", xml_declaration=True)
    logger.info(f"Wrote {len(students)} student record(s) to XML: {xml_path}")
