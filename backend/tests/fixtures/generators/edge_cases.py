"""
Edge Case PDF Generator for Category D.
Produces:
- payslip_arjun_aug2026.pdf (Salary Payslip -> classified as 'unknown')
- blank_page.pdf (Single empty white page -> near-empty OCR, classified as 'unknown')
"""
from pathlib import Path
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .base import NumberedCanvas, LogoFlowable, format_inr, get_doc_styles
from ..universe import CODEIFY_TECH, ARJUN_KHANNA


def generate_payslip_arjun_aug2026(output_path: Path) -> Dict[str, Any]:
    """Generates monthly payslip for Arjun Khanna (August 2026). Expected classification: unknown."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = get_doc_styles()
    story = []

    logo = LogoFlowable(width=48, height=48, color=CODEIFY_TECH.logo_color, text=CODEIFY_TECH.logo_initials)
    org_info = f"""<b>{CODEIFY_TECH.name}</b><br/>
{CODEIFY_TECH.address}<br/>
<b>PAYSLIP FOR THE MONTH OF AUGUST 2026</b>
"""
    header_table = Table([[logo, Paragraph(org_info, styles["TD"])]], colWidths=[55, 470])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#4A154B")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    emp_data = [
        [
            Paragraph(f"<b>Employee Name:</b> {ARJUN_KHANNA.name}", styles["TD"]),
            Paragraph("<b>Employee ID:</b> CT-1048", styles["TD"]),
        ],
        [
            Paragraph(f"<b>Designation:</b> {ARJUN_KHANNA.designation}", styles["TD"]),
            Paragraph("<b>Department:</b> Cloud Platform Engineering", styles["TD"]),
        ],
        [
            Paragraph(f"<b>PAN:</b> {ARJUN_KHANNA.pan}", styles["TD"]),
            Paragraph("<b>Bank A/C:</b> Axis Bank - 912010044921", styles["TD"]),
        ],
        [
            Paragraph("<b>Days Payable:</b> 31", styles["TD"]),
            Paragraph("<b>UAN:</b> 100912489102", styles["TD"]),
        ],
    ]
    emp_table = Table(emp_data, colWidths=[260, 265])
    emp_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FDF2F8")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#F472B6")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#FCE7F3")),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 12))

    breakdown_data = [
        [
            Paragraph("<b>Earnings</b>", styles["TH"]),
            Paragraph("<b>Amount (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Deductions</b>", styles["TH"]),
            Paragraph("<b>Amount (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("Basic Salary", styles["TD"]), Paragraph("60,000.00", styles["TD_Right"]),
            Paragraph("Provident Fund (EPF)", styles["TD"]), Paragraph("1,800.00", styles["TD_Right"]),
        ],
        [
            Paragraph("House Rent Allowance (HRA)", styles["TD"]), Paragraph("30,000.00", styles["TD_Right"]),
            Paragraph("Professional Tax", styles["TD"]), Paragraph("200.00", styles["TD_Right"]),
        ],
        [
            Paragraph("Special Allowance", styles["TD"]), Paragraph("25,000.00", styles["TD_Right"]),
            Paragraph("Income Tax (TDS u/s 192)", styles["TD"]), Paragraph("15,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("Leave Travel Allowance (LTA)", styles["TD"]), Paragraph("5,000.00", styles["TD_Right"]),
            Paragraph("", styles["TD"]), Paragraph("", styles["TD_Right"]),
        ],
        [
            Paragraph("<b>Total Gross Earnings</b>", styles["TH"]),
            Paragraph("<b>1,20,000.00</b>", styles["TH_Right"]),
            Paragraph("<b>Total Deductions</b>", styles["TH"]),
            Paragraph("<b>17,500.00</b>", styles["TH_Right"]),
        ],
    ]
    breakdown_table = Table(breakdown_data, colWidths=[165, 95, 165, 100])
    breakdown_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#4A154B")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(breakdown_table)
    story.append(Spacer(1, 14))

    net_pay_data = [
        [
            Paragraph("<b>Net Pay:</b> Rs. 1,02,500.00", styles["TH"]),
            Paragraph("<i>(One Lakh Two Thousand Five Hundred Rupees Only)</i>", styles["TD"]),
        ]
    ]
    net_table = Table(net_pay_data, colWidths=[180, 345])
    net_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#DCFCE7")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#16A34A")),
    ]))
    story.append(net_table)
    story.append(Spacer(1, 20))

    footer_note = """<font size="7" color="#64748B">
This document is an electronic payslip generated automatically by Codeify Technologies People Ops Portal. Confidential — for internal employee record only.
</font>"""
    story.append(Paragraph(footer_note, styles["FinePrint"]))

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "document_type": "payslip",
        "expected_classification": "unknown",
        "employee_name": ARJUN_KHANNA.name,
        "period": "August 2026",
        "gross_salary": 120000.00,
        "total_deductions": 175000.00,
        "net_pay": 102500.00,
    }


def generate_blank_page(output_path: Path) -> Dict[str, Any]:
    """Generates a blank PDF page. Expected classification: unknown."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    styles = get_doc_styles()
    # A single virtually empty flowable to let ReportLab emit 1 clean white page
    story = [Spacer(1, 10)]
    doc.build(story)

    return {
        "document_type": "blank_page",
        "expected_classification": "unknown",
        "page_count": 1,
    }
