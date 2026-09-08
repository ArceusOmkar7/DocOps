"""
Form 16 and Form 26AS PDF Generator for Clean Category.
Produces:
- form16_arjun_fy2526.pdf (Form 16 Part A + Part B, 2 pages, gross ₹14.4L, TDS ₹1.86L)
- form26as_arjun_ay2627.pdf (Form 26AS Annual Tax Statement, 2 pages, exact cross-reference with Form 16)
"""
from pathlib import Path
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from .base import NumberedCanvas, LogoFlowable, format_inr, get_doc_styles
from ..universe import CODEIFY_TECH, ARJUN_KHANNA


def generate_form16_arjun_fy2526(output_path: Path) -> Dict[str, Any]:
    """Generates official-format 2-page Form 16 (Part A and Part B) for Arjun Khanna."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30,
    )
    styles = get_doc_styles()
    story = []

    # TRACES Portal Header
    itd_logo = LogoFlowable(width=44, height=44, color=(0.08, 0.40, 0.28), text="TRACES")
    hdr_text = """<b>INCOME TAX DEPARTMENT</b><br/>
<font size="8">Certificate under Section 203 of the Income-tax Act, 1961 for Tax Deducted at Source on Salary<br/>
<b>FORM NO. 16 — PART A</b> &nbsp;|&nbsp; Certificate No: TRACES-16-2026-881920</font>
"""
    ay_meta = """<b>Assessment Year:</b> 2026-27<br/>
<b>Period with Employer:</b><br/>
01-Apr-2025 to 31-Mar-2026
"""
    header_table = Table(
        [[itd_logo, Paragraph(hdr_text, styles["TD"]), Paragraph(ay_meta, styles["TD_Right"])]],
        colWidths=[50, 315, 170],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#065F46")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # Deductor and Employee Identification
    entities_table_data = [
        [
            Paragraph(f"<b>Name and Address of the Employer (Deductor):</b><br/><b>{CODEIFY_TECH.name}</b><br/>{CODEIFY_TECH.address}", styles["TD"]),
            Paragraph(f"<b>Name and Address of the Employee:</b><br/><b>{ARJUN_KHANNA.name}</b><br/>{ARJUN_KHANNA.address}", styles["TD"]),
        ],
        [
            Paragraph(f"<b>PAN of Deductor:</b> {CODEIFY_TECH.pan}<br/><b>TAN of Deductor:</b> {ARJUN_KHANNA.employer_tan}", styles["TD"]),
            Paragraph(f"<b>PAN of Employee:</b> {ARJUN_KHANNA.pan}<br/><b>Aadhaar (Masked):</b> {ARJUN_KHANNA.aadhaar_masked}", styles["TD"]),
        ],
    ]
    entities_table = Table(entities_table_data, colWidths=[267, 268])
    entities_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0FDF4")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#BBF7D0")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BBF7D0")),
    ]))
    story.append(entities_table)
    story.append(Spacer(1, 10))

    # Summary of Tax Deducted and Deposited (Quarterly)
    story.append(Paragraph("<b>Summary of Tax Deducted and Deposited in the Central Government Account through Challans</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))

    tds_data = [
        [
            Paragraph("<b>Quarter</b>", styles["TH"]),
            Paragraph("<b>Receipt No. of Original Statement (24Q)</b>", styles["TH"]),
            Paragraph("<b>Amount Paid / Credited (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Amount of Tax Deducted (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Amount of Tax Deposited (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("Q1 (Apr - Jun)", styles["TD"]),
            Paragraph("24Q-2025-01-998231", styles["TD"]),
            Paragraph("3,60,000.00", styles["TD_Right"]),
            Paragraph("46,500.00", styles["TD_Right"]),
            Paragraph("46,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("Q2 (Jul - Sep)", styles["TD"]),
            Paragraph("24Q-2025-02-114920", styles["TD"]),
            Paragraph("3,60,000.00", styles["TD_Right"]),
            Paragraph("46,500.00", styles["TD_Right"]),
            Paragraph("46,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("Q3 (Oct - Dec)", styles["TD"]),
            Paragraph("24Q-2025-03-348921", styles["TD"]),
            Paragraph("3,60,000.00", styles["TD_Right"]),
            Paragraph("46,500.00", styles["TD_Right"]),
            Paragraph("46,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("Q4 (Jan - Mar)", styles["TD"]),
            Paragraph("24Q-2025-04-771204", styles["TD"]),
            Paragraph("3,60,000.00", styles["TD_Right"]),
            Paragraph("46,500.00", styles["TD_Right"]),
            Paragraph("46,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("<b>Total</b>", styles["TH"]),
            Paragraph("-", styles["TD"]),
            Paragraph("<b>14,40,000.00</b>", styles["TH_Right"]),
            Paragraph("<b>1,86,000.00</b>", styles["TH_Right"]),
            Paragraph("<b>1,86,000.00</b>", styles["TH_Right"]),
        ],
    ]
    tds_table = Table(tds_data, colWidths=[85, 170, 95, 90, 95])
    tds_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#065F46")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(tds_table)
    story.append(Spacer(1, 10))

    # Challan Details
    story.append(Paragraph("<b>Challan Identification Details (BSR Code, Challan Date & Serial Number)</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))
    challan_data = [
        [
            Paragraph("<b>Sl. No.</b>", styles["TH"]),
            Paragraph("<b>BSR Code of Bank</b>", styles["TH"]),
            Paragraph("<b>Date on which Tax Deposited</b>", styles["TH"]),
            Paragraph("<b>Challan Serial No.</b>", styles["TH"]),
            Paragraph("<b>Tax Deposited (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("1", styles["TD"]), Paragraph("0210045", styles["TD"]), Paragraph("07/07/2025", styles["TD"]), Paragraph("00012", styles["TD"]), Paragraph("46,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("2", styles["TD"]), Paragraph("0210045", styles["TD"]), Paragraph("06/10/2025", styles["TD"]), Paragraph("00018", styles["TD"]), Paragraph("46,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("3", styles["TD"]), Paragraph("0210045", styles["TD"]), Paragraph("07/01/2026", styles["TD"]), Paragraph("00024", styles["TD"]), Paragraph("46,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("4", styles["TD"]), Paragraph("0210045", styles["TD"]), Paragraph("28/04/2026", styles["TD"]), Paragraph("00031", styles["TD"]), Paragraph("46,500.00", styles["TD_Right"]),
        ],
    ]
    challan_table = Table(challan_data, colWidths=[45, 120, 150, 110, 110])
    challan_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(challan_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<i>(Part B continued on Page 2...)</i>", styles["FinePrint"]))

    # PAGE 2: PART B
    story.append(PageBreak())

    p2_hdr = Table(
        [[
            itd_logo,
            Paragraph(f"<b>FORM NO. 16 — PART B</b> &nbsp;|&nbsp; Assessment Year: 2026-27<br/><font size='8'>Details of Salary Paid and any other income and tax deducted for {ARJUN_KHANNA.name} (PAN: {ARJUN_KHANNA.pan})</font>", styles["TD"]),
            Paragraph("<b>PAGE 2 OF 2</b>", styles["TD_Right"]),
        ]],
        colWidths=[44, 385, 106],
    )
    p2_hdr.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#065F46")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(p2_hdr)
    story.append(Spacer(1, 8))

    part_b_data = [
        [Paragraph("<b>Particulars</b>", styles["TH"]), Paragraph("<b>Amount (Rs.)</b>", styles["TH_Right"]), Paragraph("<b>Amount (Rs.)</b>", styles["TH_Right"])],
        [Paragraph("1. Gross Salary", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"])],
        [Paragraph("&nbsp;&nbsp;(a) Salary as per provisions contained in sec. 17(1)", styles["TD"]), Paragraph("14,40,000.00", styles["TD_Right"]), Paragraph("", styles["TD"])],
        [Paragraph("&nbsp;&nbsp;(b) Value of perquisites u/s 17(2)", styles["TD"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("", styles["TD"])],
        [Paragraph("&nbsp;&nbsp;<b>Total Gross Salary</b>", styles["TH"]), Paragraph("", styles["TD"]), Paragraph("14,40,000.00", styles["TD_Right"])],
        [Paragraph("2. Less: Allowances to the extent exempt u/s 10 (House Rent Allowance u/s 10(13A))", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("1,20,000.00", styles["TD_Right"])],
        [Paragraph("3. Balance (1 - 2)", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("13,20,000.00", styles["TD_Right"])],
        [Paragraph("4. Deductions under Section 16", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"])],
        [Paragraph("&nbsp;&nbsp;(a) Standard Deduction u/s 16(ia)", styles["TD"]), Paragraph("50,000.00", styles["TD_Right"]), Paragraph("", styles["TD"])],
        [Paragraph("&nbsp;&nbsp;(b) Tax on Employment (Professional Tax) u/s 16(iii)", styles["TD"]), Paragraph("2,500.00", styles["TD_Right"]), Paragraph("", styles["TD"])],
        [Paragraph("5. Total Deductions under Section 16", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("52,500.00", styles["TD_Right"])],
        [Paragraph("<b>6. Income chargeable under the head 'Salaries' (3 - 5)</b>", styles["TH"]), Paragraph("", styles["TD"]), Paragraph("<b>12,67,500.00</b>", styles["TD_Right"])],
        [Paragraph("7. Deductions under Chapter VI-A", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"])],
        [Paragraph("&nbsp;&nbsp;(a) Section 80C (PPF: Rs. 1,02,000 + LIC: Rs. 48,000, Total Rs. 1,50,000)", styles["TD"]), Paragraph("1,50,000.00", styles["TD_Right"]), Paragraph("", styles["TD"])],
        [Paragraph("&nbsp;&nbsp;(b) Section 80D (Health Insurance Premium)", styles["TD"]), Paragraph("25,000.00", styles["TD_Right"]), Paragraph("", styles["TD"])],
        [Paragraph("8. Aggregate of Deductible Amount under Chapter VI-A", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("1,75,000.00", styles["TD_Right"])],
        [Paragraph("<b>9. Total Taxable Income (6 - 8)</b>", styles["TH"]), Paragraph("", styles["TD"]), Paragraph("<b>10,92,500.00</b>", styles["TD_Right"])],
        [Paragraph("10. Tax on Total Income", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("1,78,846.00", styles["TD_Right"])],
        [Paragraph("11. Health and Education Cess (4%)", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("7,154.00", styles["TD_Right"])],
        [Paragraph("<b>12. Total Tax Payable</b>", styles["TH"]), Paragraph("", styles["TD"]), Paragraph("<b>1,86,000.00</b>", styles["TD_Right"])],
        [Paragraph("13. Less: Tax Deducted at Source u/s 192(1)", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("1,86,000.00", styles["TD_Right"])],
        [Paragraph("<b>14. Net Tax Payable / Refundable</b>", styles["TH"]), Paragraph("", styles["TD"]), Paragraph("<b>0.00</b>", styles["TD_Right"])],
    ]
    part_b_table = Table(part_b_data, colWidths=[335, 100, 100])
    part_b_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#F8FAFC")),
        ("BACKGROUND", (0, 11), (-1, 11), colors.HexColor("#F1F5F9")),
        ("BACKGROUND", (0, 16), (-1, 16), colors.HexColor("#E0E7FF")),
        ("BACKGROUND", (0, 19), (-1, 19), colors.HexColor("#DCFCE7")),
        ("LINEABOVE", (0, 19), (-1, 19), 1, colors.HexColor("#065F46")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(part_b_table)
    story.append(Spacer(1, 10))

    verification_text = f"""<b>Verification:</b><br/>
I, <b>Suresh Nair</b>, Head of Human Resources and Designated Signatory of <b>{CODEIFY_TECH.name}</b>, do hereby certify that a sum of <b>Rs. 1,86,000.00 (One Lakh Eighty-Six Thousand Rupees Only)</b> has been deducted at source and paid to the credit of the Central Government. I further certify that the information given above is true, complete and correct based on the books of account and other available records.<br/><br/>
<b>Place:</b> Pune &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Date:</b> 30-May-2026 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Signature:</b> [Digitally Signed by Suresh Nair]
"""
    ver_table = Table([[Paragraph(verification_text, styles["FinePrint"])]], colWidths=[535])
    ver_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(ver_table)

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "form_type": "Form 16",
        "employee_name": ARJUN_KHANNA.name,
        "employee_pan": ARJUN_KHANNA.pan,
        "employer_name": CODEIFY_TECH.name,
        "employer_tan": ARJUN_KHANNA.employer_tan,
        "employer_pan": CODEIFY_TECH.pan,
        "assessment_year": "2026-27",
        "financial_year": "2025-26",
        "gross_salary": 1440000.00,
        "total_deductions_chapter_via": 175000.00,
        "taxable_income": 1092500.00,
        "total_tax_deducted": 186000.00,
        "total_tax_deposited": 186000.00,
        "reconciled": True,
    }


def generate_form26as_arjun_ay2627(output_path: Path) -> Dict[str, Any]:
    """Generates official-format 2-page Form 26AS Annual Tax Statement for Arjun Khanna."""
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=30,
        rightMargin=30,
        topMargin=30,
        bottomMargin=30,
    )
    styles = get_doc_styles()
    story = []

    itd_logo = LogoFlowable(width=44, height=44, color=(0.10, 0.25, 0.45), text="TRACES")
    hdr_text = """<b>INCOME TAX DEPARTMENT</b><br/>
<font size="8">Annual Tax Statement Under Section 203AA of the Income-tax Act, 1961<br/>
<b>FORM 26AS</b> &nbsp;|&nbsp; Financial Year: 2025-26 &nbsp;|&nbsp; <b>Assessment Year: 2026-27</b></font>
"""
    status_meta = """<b>Status:</b> Active<br/>
<b>Extraction Date:</b> 12-Jul-2026<br/>
<b>Financial Year:</b> 2025-26
"""
    header_table = Table(
        [[itd_logo, Paragraph(hdr_text, styles["TD"]), Paragraph(status_meta, styles["TD_Right"])]],
        colWidths=[50, 315, 170],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#1E3A8A")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    assesse_info = f"""<b>Permanent Account Number (PAN):</b> {ARJUN_KHANNA.pan} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <b>Name of Assessee:</b> {ARJUN_KHANNA.name}<br/>
<b>Current Address:</b> {ARJUN_KHANNA.address}
"""
    info_table = Table([[Paragraph(assesse_info, styles["TD"])]], colWidths=[535])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # Part A: Details of Tax Deducted at Source (Salary)
    story.append(Paragraph("<b>PART A — Details of Tax Deducted at Source (As per Form 24Q filed by Deductor)</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))

    deductor_info = f"<b>Deductor:</b> {CODEIFY_TECH.name} &nbsp;&nbsp;|&nbsp;&nbsp; <b>TAN:</b> {ARJUN_KHANNA.employer_tan}"
    story.append(Paragraph(deductor_info, styles["FinePrint"]))
    story.append(Spacer(1, 4))

    part_a_data = [
        [
            Paragraph("<b>Sl.</b>", styles["TH"]),
            Paragraph("<b>Section</b>", styles["TH"]),
            Paragraph("<b>Transaction Date</b>", styles["TH"]),
            Paragraph("<b>Status of Booking</b>", styles["TH"]),
            Paragraph("<b>Date of Booking</b>", styles["TH"]),
            Paragraph("<b>Amount Paid (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Tax Deducted (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Total TDS Deposited (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("1", styles["TD"]), Paragraph("192", styles["TD"]), Paragraph("30/06/2025", styles["TD"]), Paragraph("Matched (F)", styles["TD"]), Paragraph("12/07/2025", styles["TD"]), Paragraph("3,60,000.00", styles["TD_Right"]), Paragraph("46,500.00", styles["TD_Right"]), Paragraph("46,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("2", styles["TD"]), Paragraph("192", styles["TD"]), Paragraph("30/09/2025", styles["TD"]), Paragraph("Matched (F)", styles["TD"]), Paragraph("14/10/2025", styles["TD"]), Paragraph("3,60,000.00", styles["TD_Right"]), Paragraph("46,500.00", styles["TD_Right"]), Paragraph("46,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("3", styles["TD"]), Paragraph("192", styles["TD"]), Paragraph("31/12/2025", styles["TD"]), Paragraph("Matched (F)", styles["TD"]), Paragraph("15/01/2026", styles["TD"]), Paragraph("3,60,000.00", styles["TD_Right"]), Paragraph("46,500.00", styles["TD_Right"]), Paragraph("46,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("4", styles["TD"]), Paragraph("192", styles["TD"]), Paragraph("31/03/2026", styles["TD"]), Paragraph("Matched (F)", styles["TD"]), Paragraph("05/05/2026", styles["TD"]), Paragraph("3,60,000.00", styles["TD_Right"]), Paragraph("46,500.00", styles["TD_Right"]), Paragraph("46,500.00", styles["TD_Right"]),
        ],
        [
            Paragraph("<b>Total</b>", styles["TH"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("<b>14,40,000.00</b>", styles["TH_Right"]), Paragraph("<b>1,86,000.00</b>", styles["TH_Right"]), Paragraph("<b>1,86,000.00</b>", styles["TH_Right"]),
        ],
    ]
    part_a_table = Table(part_a_data, colWidths=[20, 35, 65, 65, 65, 95, 95, 95])
    part_a_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#1E3A8A")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(part_a_table)
    story.append(Spacer(1, 10))

    # Part A1: Details of Tax Deducted at Source for 15G / 15H
    story.append(Paragraph("<b>PART A1 — Details of Tax Deducted at Source for 15G / 15H</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))
    nil_row1 = [
        [Paragraph("<b>No transactions present for this assessment year under Part A1</b>", styles["TD"])]
    ]
    nil_t1 = Table(nil_row1, colWidths=[535])
    nil_t1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(nil_t1)
    story.append(Spacer(1, 10))

    # Part A2: Details of Tax Deducted at Source on sale of Immovable Property
    story.append(Paragraph("<b>PART A2 — Details of Tax Deducted at Source on sale of Immovable Property u/s 194-IA</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))
    nil_row2 = [
        [Paragraph("<b>No transactions present for this assessment year under Part A2</b>", styles["TD"])]
    ]
    nil_t2 = Table(nil_row2, colWidths=[535])
    nil_t2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(nil_t2)
    story.append(Spacer(1, 8))
    story.append(Paragraph("<i>(Form 26AS continued on Page 2...)</i>", styles["FinePrint"]))

    # PAGE 2
    story.append(PageBreak())

    p2_hdr = Table(
        [[
            itd_logo,
            Paragraph(f"<b>FORM 26AS — ANNUAL TAX STATEMENT</b> &nbsp;|&nbsp; AY 2026-27<br/><font size='8'>Assessee: {ARJUN_KHANNA.name} (PAN: {ARJUN_KHANNA.pan})</font>", styles["TD"]),
            Paragraph("<b>PAGE 2 OF 2</b>", styles["TD_Right"]),
        ]],
        colWidths=[44, 385, 106],
    )
    p2_hdr.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#1E3A8A")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(p2_hdr)
    story.append(Spacer(1, 8))

    # Part B: Details of Tax Collected at Source
    story.append(Paragraph("<b>PART B — Details of Tax Collected at Source (TCS)</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))
    nil_t3 = Table([[Paragraph("No transactions recorded under Part B", styles["TD"])]], colWidths=[535])
    nil_t3.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(nil_t3)
    story.append(Spacer(1, 10))

    # Part C: Details of Tax Paid (other than TDS or TCS)
    story.append(Paragraph("<b>PART C — Details of Tax Paid (Advance Tax / Self-Assessment Tax)</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))
    nil_t4 = Table([[Paragraph("No advance tax / self-assessment payments recorded under Part C", styles["TD"])]], colWidths=[535])
    nil_t4.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(nil_t4)
    story.append(Spacer(1, 10))

    # Part D: Details of Paid Refund
    story.append(Paragraph("<b>PART D — Details of Paid Refund</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))
    nil_t5 = Table([[Paragraph("No income tax refunds issued during this financial year", styles["TD"])]], colWidths=[535])
    nil_t5.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(nil_t5)
    story.append(Spacer(1, 10))

    # Part E: Details of SFT (Specified Financial Transactions)
    story.append(Paragraph("<b>PART E — Details of Specified Financial Transactions (SFT)</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))
    sft_data = [
        [Paragraph("<b>Sl.</b>", styles["TH"]), Paragraph("<b>Type of Transaction</b>", styles["TH"]), Paragraph("<b>Reporting Entity</b>", styles["TH"]), Paragraph("<b>Amount (Rs.)</b>", styles["TH_Right"])],
        [Paragraph("1", styles["TD"]), Paragraph("SFT-005: Time Deposit / Flexi Sweep", styles["TD"]), Paragraph("Axis Bank Limited (UTIB0001234)", styles["TD"]), Paragraph("4,00,000.00", styles["TD_Right"])],
    ]
    sft_table = Table(sft_data, colWidths=[25, 200, 200, 110])
    sft_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(sft_table)
    story.append(Spacer(1, 15))

    footer_disclaimer = """<font size="7" color="#64748B">
<b>Notes:</b><br/>
1. If tax deducted has not been deposited or reflected in 26AS, please contact the deductor.<br/>
2. This is a computer generated statement downloaded from TRACES portal (https://www.tdscpc.gov.in) and requires no signature.
</font>"""
    story.append(Paragraph(footer_disclaimer, styles["FinePrint"]))

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "form_type": "Form 26AS",
        "assessee_name": ARJUN_KHANNA.name,
        "assessee_pan": ARJUN_KHANNA.pan,
        "assessment_year": "2026-27",
        "financial_year": "2025-26",
        "deductor_name": CODEIFY_TECH.name,
        "deductor_tan": ARJUN_KHANNA.employer_tan,
        "total_amount_paid": 1440000.00,
        "total_tds_deducted": 186000.00,
        "total_tds_deposited": 186000.00,
        "cross_referenced_with_form16": True,
    }
