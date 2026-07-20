from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from dataclasses import dataclass, field
from pathlib import Path
from sys import platform
import subprocess
import os

from cashd_core.const import CASHD_FILES_DIR, DOCUMENTS_DIR


# readonly resources directory
RESOURCES_DIR = Path(__file__).resolve().parent / "resources"


# Resources references
IMG_LOGO = RESOURCES_DIR / "logo.png"
IMG_LOGO_SPACED = RESOURCES_DIR / "logo-spaced.png"
IMG_LOGO_SPACED_TRB = RESOURCES_DIR / "logo-spaced-trb.png"


pdfmetrics.registerFont(TTFont("Saira-SemiBold", RESOURCES_DIR / "Saira-SemiBold.ttf"))


class StyleSheet:
    styles = getSampleStyleSheet()
    L_BRAND = ParagraphStyle(
        "l_brand",
        fontName="Saira-SemiBold",
        fontSize=13,
    )
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
    R_HEADING = ParagraphStyle("c_para", parent=L_HEADING, alignment=2)
    R_PARA = ParagraphStyle("r_para", parent=L_PARA, alignment=2)
    R_BOLD = ParagraphStyle("r_bold", parent=L_BOLD, alignment=2)
    C_HEADING = ParagraphStyle("c_para", parent=L_HEADING, alignment=1)
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
            self, "document_path", DOCUMENTS_DIR.joinpath(f"{self.name}.pdf")
        )

    def open_file(self):
        match platform:
            case "win32":
                os.startfile(self.document_path)
            case "linux":
                subprocess.run(["xdg-open", self.document_path])
            case "darwin":
                subprocess.run(["open", self.document_path])
