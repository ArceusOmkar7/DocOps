"""
Base reportlab helpers, styling, canvas classes, and formatting for all document generators.
"""
from typing import Tuple, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Flowable,
)
from reportlab.pdfgen import canvas


def format_inr(amount: float, decimals: int = 2, symbol: str = "Rs. ") -> str:
    """Format a number into Indian numbering format: e.g. 12,34,567.89"""
    is_negative = amount < 0
    amount = abs(amount)
    fmt = f"{{:.{decimals}f}}".format(amount)
    parts = fmt.split(".")
    integer_part = parts[0]
    decimal_part = parts[1] if len(parts) > 1 else ""

    if len(integer_part) <= 3:
        formatted = integer_part
    else:
        last3 = integer_part[-3:]
        remaining = integer_part[:-3]
        groups = []
        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            groups.insert(0, remaining)
        groups.append(last3)
        formatted = ",".join(groups)

    result = f"{formatted}.{decimal_part}" if decimals > 0 else formatted
    prefix = f"-{symbol}" if is_negative else symbol
    return f"{prefix}{result}"


class LogoFlowable(Flowable):
    """Draws a crisp coloured rectangle with bold white initials representing the corporate logo."""
    def __init__(self, width: float = 48, height: float = 48, color: Tuple[float, float, float] = (0.2, 0.4, 0.6), text: str = "CO"):
        super().__init__()
        self.width = width
        self.height = height
        self.color = color
        self.text = text

    def wrap(self, availWidth, availHeight):
        return self.width, self.height

    def draw(self):
        self.canv.saveState()
        self.canv.setFillColorRGB(*self.color)
        self.canv.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)
        self.canv.setFillColorRGB(1, 1, 1)
        font_size = min(self.height * 0.42, (self.width / max(len(self.text), 1)) * 1.1)
        self.canv.setFont("Helvetica-Bold", font_size)
        self.canv.drawCentredString(self.width / 2.0, (self.height - font_size) / 2.0 + font_size * 0.22, self.text)
        self.canv.restoreState()


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to calculate total page count and draw 'Page X of Y' in footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(A4[0] - 36, 20, page_str)
        self.restoreState()


def get_doc_styles():
    """Build a comprehensive set of typography styles for financial documents."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="DocTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1A202C"),
    ))
    styles.add(ParagraphStyle(
        name="DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#4A5568"),
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#1A202C"),
        spaceBefore=8,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="TH",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1A202C"),
        alignment=0,
    ))
    styles.add(ParagraphStyle(
        name="TH_Right",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1A202C"),
        alignment=2,
    ))
    styles.add(ParagraphStyle(
        name="TD",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#2D3748"),
        alignment=0,
    ))
    styles.add(ParagraphStyle(
        name="TD_Right",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#2D3748"),
        alignment=2,
    ))
    styles.add(ParagraphStyle(
        name="TD_Bold_Right",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1A202C"),
        alignment=2,
    ))
    styles.add(ParagraphStyle(
        name="FinePrint",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=colors.HexColor("#718096"),
    ))
    return styles
