"""
Investment Proof PDF Generator for Clean Category.
Produces:
- lic_receipt_arjun_80c.pdf (LIC Life Insurance Premium Receipt, ₹48,000.00, Section 80C)
- ppf_statement_arjun_80c.pdf (SBI PPF Account Annual Statement, ₹1,02,000.00 deposit, Section 80C)
Matches Form 16 Chapter VI-A 80C breakdown: LIC (₹48,000) + PPF (₹1,02,000) = ₹1,50,000.
"""
from pathlib import Path
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .base import NumberedCanvas, LogoFlowable, format_inr, get_doc_styles
from ..universe import ARJUN_KHANNA


def generate_lic_receipt_arjun_80c(output_path: Path) -> Dict[str, Any]:
    """Generates official-format LIC Premium Paid Certificate / Receipt."""
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

    lic_logo = LogoFlowable(width=48, height=48, color=(0.85, 0.65, 0.12), text="LIC")
    org_info = """<b>LIFE INSURANCE CORPORATION OF INDIA</b><br/>
<font size="8">Branch Office 882 (Pune City Branch), Laxmi Road, Pune - 411030<br/>
<b>PREMIUM PAYMENT CERTIFICATE FOR INCOME TAX REBATE (U/S 80C)</b></font>
"""
    doc_meta = """<b>Receipt No:</b> LIC/PN/2025/99812<br/>
<b>Date:</b> 15-Sep-2025<br/>
<b>Financial Year:</b> 2025-26
"""
    header_table = Table(
        [[lic_logo, Paragraph(org_info, styles["TD"]), Paragraph(doc_meta, styles["TD_Right"])]],
        colWidths=[55, 310, 160],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#D97706")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))

    cert_banner = """<b>TO WHOMSOEVER IT MAY CONCERN</b><br/>
This is to certify that the policyholder mentioned below has paid the life insurance premium under the said policy during the financial year 2025-2026 as detailed below:
"""
    story.append(Paragraph(cert_banner, styles["TD"]))
    story.append(Spacer(1, 10))

    holder_info = f"""<b>Name of Policyholder:</b> {ARJUN_KHANNA.name}<br/>
<b>Address:</b> {ARJUN_KHANNA.address}<br/>
<b>PAN:</b> {ARJUN_KHANNA.pan}<br/>
<b>Life Assured:</b> {ARJUN_KHANNA.name} (Self)
"""
    policy_meta = f"""<b>Policy Number:</b> {ARJUN_KHANNA.lic_policy_no}<br/>
<b>Plan & Term:</b> Jeevan Labh (Plan 936 / Term 25 yrs)<br/>
<b>Sum Assured:</b> Rs. 15,00,000.00<br/>
<b>Premium Frequency:</b> Annual
"""
    info_table = Table(
        [[Paragraph(holder_info, styles["TD"]), Paragraph(policy_meta, styles["TD"])]],
        colWidths=[265, 260],
    )
    info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#F59E0B")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 14))

    table_data = [
        [
            Paragraph("<b>Receipt Date</b>", styles["TH"]),
            Paragraph("<b>Due Date</b>", styles["TH"]),
            Paragraph("<b>Mode of Payment</b>", styles["TH"]),
            Paragraph("<b>Basic Premium (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>GST (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Total Amount Paid (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("15/09/2025", styles["TD"]),
            Paragraph("15/09/2025", styles["TD"]),
            Paragraph("Net Banking (HDFC)", styles["TD"]),
            Paragraph("46,028.71", styles["TD_Right"]),
            Paragraph("1,971.29", styles["TD_Right"]),
            Paragraph("48,000.00", styles["TD_Right"]),
        ],
    ]
    receipt_table = Table(table_data, colWidths=[80, 80, 110, 85, 75, 95])
    receipt_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#9CA3AF")),
    ]))
    story.append(receipt_table)
    story.append(Spacer(1, 15))

    rebate_notice = """<b>Income Tax Rebate Notice:</b><br/>
1. Premium paid is eligible for deduction under <b>Section 80C</b> of the Income-tax Act, 1961 up to the statutory limit.<br/>
2. In terms of Section 10(10D), the premium payable for any year does not exceed 10% of the actual capital sum assured.<br/>
3. Eligible 80C Deduction Amount: <b>Rs. 48,000.00 (Forty-Eight Thousand Rupees Only)</b>
"""
    rebate_table = Table([[Paragraph(rebate_notice, styles["FinePrint"])]], colWidths=[525])
    rebate_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F9FAFB")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
    ]))
    story.append(rebate_table)
    story.append(Spacer(1, 20))

    sign_text = """<br/><br/>
For <b>LIFE INSURANCE CORPORATION OF INDIA</b><br/><br/><br/>
<b>Branch Manager / Authorized Signatory</b><br/>
Branch Code: 882 (Pune City)
"""
    story.append(Table([["", Paragraph(sign_text, styles["TD_Right"])]], colWidths=[300, 225]))

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "institution": "Life Insurance Corporation of India",
        "policy_number": ARJUN_KHANNA.lic_policy_no,
        "policyholder": ARJUN_KHANNA.name,
        "pan": ARJUN_KHANNA.pan,
        "financial_year": "2025-26",
        "total_premium_paid": 48000.00,
        "eligible_80c_amount": 48000.00,
    }


def generate_ppf_statement_arjun_80c(output_path: Path) -> Dict[str, Any]:
    """Generates official-format SBI PPF Account Passbook / Statement."""
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

    sbi_logo = LogoFlowable(width=48, height=48, color=(0.10, 0.35, 0.65), text="SBI")
    org_info = """<b>STATE BANK OF INDIA</b><br/>
<font size="8">Baner Branch (04482), Pancard Club Road, Baner, Pune - 411045 | IFSC: SBIN0004482<br/>
<b>PUBLIC PROVIDENT FUND (PPF) SCHEME, 1968 / 2019 — ANNUAL ACCOUNT STATEMENT</b></font>
"""
    doc_meta = """<b>Statement Date:</b> 05-Apr-2026<br/>
<b>Financial Year:</b> 2025-26<br/>
<b>Assessment Year:</b> 2026-27
"""
    header_table = Table(
        [[sbi_logo, Paragraph(org_info, styles["TD"]), Paragraph(doc_meta, styles["TD_Right"])]],
        colWidths=[55, 310, 160],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#105990")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 12))

    acct_info = f"""<b>Subscriber Name:</b> {ARJUN_KHANNA.name}<br/>
<b>Address:</b> {ARJUN_KHANNA.address}<br/>
<b>PAN:</b> {ARJUN_KHANNA.pan} &nbsp;|&nbsp; <b>CIF No:</b> 81920391823<br/>
<b>Nominee:</b> Sangeeta Khanna (Spouse)
"""
    ppf_meta = f"""<b>PPF Account No:</b> {ARJUN_KHANNA.ppf_account_no}<br/>
<b>Account Status:</b> Active / KYC Complied<br/>
<b>Date of Account Opening:</b> 12-Jun-2020<br/>
<b>Date of Maturity:</b> 31-Mar-2036
"""
    info_table = Table(
        [[Paragraph(acct_info, styles["TD"]), Paragraph(ppf_meta, styles["TD"])]],
        colWidths=[265, 260],
    )
    info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#93C5FD")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>Deposit Transactions for FY 2025-26 (Eligible u/s 80C)</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))

    # PPF Ledger for FY 2025-26
    # Opening balance: 4,15,400.00
    # Deposit 1: 05-Apr-2025: 50,000.00 -> 4,65,400.00
    # Deposit 2: 04-Oct-2025: 52,000.00 -> 5,17,400.00
    # Total deposits in FY 25-26: 1,02,000.00
    # Annual Interest credited on 31-Mar-2026 @ 7.1%: 35,445.00
    # Closing balance: 5,52,845.00
    table_data = [
        [
            Paragraph("<b>Date</b>", styles["TH"]),
            Paragraph("<b>Particulars / Narration</b>", styles["TH"]),
            Paragraph("<b>Chq / Ref No</b>", styles["TH"]),
            Paragraph("<b>Deposit (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Withdrawal (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Balance (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("01/04/2025", styles["TD"]),
            Paragraph("OPENING BALANCE B/F", styles["TD"]),
            Paragraph("-", styles["TD"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("4,15,400.00", styles["TD_Right"]),
        ],
        [
            Paragraph("05/04/2025", styles["TD"]),
            Paragraph("TRANSFER BY AUTO-DEBIT SB A/C", styles["TD"]),
            Paragraph("TRF-0425-9981", styles["TD"]),
            Paragraph("50,000.00", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("4,65,400.00", styles["TD_Right"]),
        ],
        [
            Paragraph("04/10/2025", styles["TD"]),
            Paragraph("TRANSFER BY ONLINE INB PORTAL", styles["TD"]),
            Paragraph("TRF-1025-4412", styles["TD"]),
            Paragraph("52,000.00", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("5,17,400.00", styles["TD_Right"]),
        ],
        [
            Paragraph("31/03/2026", styles["TD"]),
            Paragraph("ANNUAL INTEREST APPLIED @ 7.1% P.A.", styles["TD"]),
            Paragraph("INT-CREDIT-FY2526", styles["TD"]),
            Paragraph("35,445.00", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("5,52,845.00", styles["TD_Right"]),
        ],
        [
            Paragraph("<b>CLOSING</b>", styles["TH"]),
            Paragraph("<b>TOTAL DEPOSITS IN FY 2025-26</b>", styles["TH"]),
            Paragraph("-", styles["TD"]),
            Paragraph("<b>1,02,000.00</b>", styles["TH_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("<b>5,52,845.00</b>", styles["TH_Right"]),
        ],
    ]
    ppf_table = Table(table_data, colWidths=[65, 175, 95, 75, 55, 60])
    ppf_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EFF6FF")),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#105990")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(ppf_table)
    story.append(Spacer(1, 15))

    cert_note = """<b>Tax Exemption Certificate:</b><br/>
Certified that the subscriber has deposited a sum of <b>Rs. 1,02,000.00 (One Lakh Two Thousand Rupees Only)</b> in the above PPF Account during the financial year 2025-26. This deposit is eligible for deduction under <b>Section 80C</b> of the Income-tax Act, 1961. The interest credited is exempt from tax under Section 10(11).
"""
    cert_table = Table([[Paragraph(cert_note, styles["FinePrint"])]], colWidths=[525])
    cert_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(cert_table)
    story.append(Spacer(1, 20))

    bank_sign = """<br/><br/>
For <b>STATE BANK OF INDIA</b><br/><br/><br/>
<b>Branch Manager / Assistant General Manager</b><br/>
Baner Branch, Pune (04482)
"""
    story.append(Table([["", Paragraph(bank_sign, styles["TD_Right"])]], colWidths=[300, 225]))

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "bank_name": "State Bank of India",
        "ppf_account_number": ARJUN_KHANNA.ppf_account_no,
        "subscriber_name": ARJUN_KHANNA.name,
        "pan": ARJUN_KHANNA.pan,
        "financial_year": "2025-26",
        "deposits_in_fy": 102000.00,
        "interest_credited": 35445.00,
        "closing_balance": 552845.00,
        "eligible_80c_amount": 102000.00,
    }
