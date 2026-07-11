from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from dataclasses import dataclass, field
from pathlib import Path

from cashd_core.data import CASHD_FILES_PATH

DOCUMENTS_DIR = CASHD_FILES_PATH.joinpath("documents")
DOCUMENTS_DIR.mkdir(exist_ok=True)


class StyleSheet:
    styles = getSampleStyleSheet()
    L_HEADING = ParagraphStyle(
        "l_heading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=11,
    )
    L_PARA = ParagraphStyle(
        "l_para",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=9,
    )
    L_BOLD = ParagraphStyle(
        "l_bold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=9,
    )
    R_PARA = ParagraphStyle("r_para", parent=L_PARA, alignment=2)
    R_BOLD = ParagraphStyle("r_bold", parent=L_BOLD, alignment=2)
    C_PARA = ParagraphStyle("c_para", parent=L_PARA, alignment=1)
    C_BOLD = ParagraphStyle("c_bold", parent=L_BOLD, alignment=1)


@dataclass(frozen=True)
class DocumentMeta:
    """Provide standard metadata for specific document types."""

    size: tuple[int]
    """Width and height of the document."""

    margin: tuple[float]
    """Margins of the document in order top-right-bottom-left."""

    name: str
    """Name of the generated file."""

    document_path: Path = field(init=False)
    """`Path` object indicating the location where the file should be stored."""

    def __post_init__(self):
        object.__setattr__(
            self,
            "document_path",
            DOCUMENTS_DIR.joinpath(f"{self.name}.pdf")
        )
