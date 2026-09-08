"""
Invoice PDF Generator for Clean Category.
Produces:
- invoice_rajput_rs0234.pdf (Intra-state CGST/SGST, ₹1,18,000.00)
- invoice_rajput_rs0235.pdf (Inter-state IGST, ₹2,36,708.00)
- invoice_codeify_ct0189.pdf (Multi-page IT services invoice with 5 detailed milestones, ₹8,85,000.00)
"""
from pathlib import Path
from typing import List, Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from .base import NumberedCanvas, LogoFlowable, format_inr, get_doc_styles
from ..universe import RAJPUT_STEELWORKS, KAPOOR_SHAH, CODEIFY_TECH


def generate_invoice_rajput_rs0234(output_path: Path) -> Dict[str, Any]:
    """Generates clean intra-state GST invoice from Rajput Steelworks to Kapoor & Shah (Ahmedabad)."""
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

    # Header with Logo and Seller Details
    logo = LogoFlowable(width=48, height=48, color=RAJPUT_STEELWORKS.logo_color, text=RAJPUT_STEELWORKS.logo_initials)
    seller_text = f"""<b>{RAJPUT_STEELWORKS.name}</b><br/>
{RAJPUT_STEELWORKS.address}<br/>
<b>GSTIN:</b> {RAJPUT_STEELWORKS.gstin} | <b>PAN:</b> {RAJPUT_STEELWORKS.pan}<br/>
<b>Email:</b> {RAJPUT_STEELWORKS.email} | <b>Phone:</b> {RAJPUT_STEELWORKS.phone}
"""
    inv_title_text = """<font size="14"><b>TAX INVOICE</b></font><br/>
<font size="8" color="#666666">ORIGINAL FOR RECIPIENT</font>
"""

    header_table = Table(
        [
            [logo, Paragraph(seller_text, styles["TD"]), Paragraph(inv_title_text, styles["TD_Right"])],
        ],
        colWidths=[55, 310, 160],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # Meta and Billing Info
    buyer_gstin = "24AABFK9234P1ZS"  # Gujarat branch of Kapoor & Shah
    buyer_info = f"""<b>Billed To (Recipient):</b><br/>
<b>{KAPOOR_SHAH.name} (Ahmedabad Branch)</b><br/>
3rd Floor, Navratna Corporate Park, Ambli Road, Ahmedabad, Gujarat 380058<br/>
<b>GSTIN:</b> {buyer_gstin} | <b>State:</b> Gujarat (Code: 24)<br/>
<b>Place of Supply:</b> 24-Gujarat
"""

    meta_info = """<b>Invoice No:</b> RS/2026-27/0234<br/>
<b>Invoice Date:</b> 14-Aug-2026<br/>
<b>Due Date:</b> 13-Sep-2026<br/>
<b>Reverse Charge:</b> No<br/>
<b>Transport Mode:</b> Road (GJ-01-BX-4412)
"""

    info_table = Table(
        [
            [Paragraph(buyer_info, styles["TD"]), Paragraph(meta_info, styles["TD"])],
        ],
        colWidths=[310, 215],
    )
    info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # Line Items
    items_data = [
        [
            Paragraph("<b>#</b>", styles["TH"]),
            Paragraph("<b>Description of Goods</b>", styles["TH"]),
            Paragraph("<b>HSN/SAC</b>", styles["TH"]),
            Paragraph("<b>Qty</b>", styles["TH_Right"]),
            Paragraph("<b>Rate (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Amount (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("1", styles["TD"]),
            Paragraph("Structural Steel Beams (IS 2062 / Grade E250)", styles["TD"]),
            Paragraph("7216", styles["TD"]),
            Paragraph("20.00 MT", styles["TD_Right"]),
            Paragraph("5,000.00", styles["TD_Right"]),
            Paragraph("1,00,000.00", styles["TD_Right"]),
        ],
    ]

    items_table = Table(items_data, colWidths=[25, 230, 65, 60, 70, 75])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#CBD5E0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # Summary & Taxes
    summary_data = [
        ["", "", "Subtotal:", "1,00,000.00"],
        ["", "", "CGST @ 9.0%:", "9,000.00"],
        ["", "", "SGST @ 9.0%:", "9,000.00"],
        ["", "", "Total Invoice Value (INR):", "1,18,000.00"],
    ]
    summary_table = Table(
        [
            [
                "",
                "",
                Paragraph(f"<b>{row[2]}</b>", styles["TD_Right"] if "Total" not in row[2] else styles["TH_Right"]),
                Paragraph(f"<b>Rs. {row[3]}</b>" if "Total" in row[2] else f"{row[3]}", styles["TD_Right"] if "Total" not in row[2] else styles["TH_Right"]),
            ]
            for row in summary_data
        ],
        colWidths=[150, 140, 140, 95],
    )
    summary_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEABOVE", (2, 3), (3, 3), 1, colors.HexColor("#2D3748")),
        ("BACKGROUND", (2, 3), (3, 3), colors.HexColor("#EDF2F7")),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    # Bank Details & Sign-off
    bank_notes = f"""<b>Bank Details for Payment:</b><br/>
Bank Name: {RAJPUT_STEELWORKS.bank_name}<br/>
A/C No: {RAJPUT_STEELWORKS.account_number} | IFSC: {RAJPUT_STEELWORKS.ifsc}<br/>
Branch: {RAJPUT_STEELWORKS.branch}<br/>
Amount in Words: <i>One Lakh Eighteen Thousand Rupees Only</i>
"""
    signoff = f"""<br/><br/>
For <b>{RAJPUT_STEELWORKS.name}</b><br/><br/><br/>
<b>Authorized Signatory</b>
"""
    footer_table = Table(
        [
            [Paragraph(bank_notes, styles["TD"]), Paragraph(signoff, styles["TD_Right"])],
        ],
        colWidths=[330, 195],
    )
    footer_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(footer_table)

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "invoice_number": "RS/2026-27/0234",
        "date": "2026-08-14",
        "seller_name": RAJPUT_STEELWORKS.name,
        "seller_gstin": RAJPUT_STEELWORKS.gstin,
        "buyer_name": "Kapoor & Shah Associates (Ahmedabad Branch)",
        "buyer_gstin": buyer_gstin,
        "subtotal": 100000.00,
        "cgst": 9000.00,
        "sgst": 9000.00,
        "igst": 0.00,
        "total": 118000.00,
        "tax_type": "intra_state",
    }


def generate_invoice_rajput_rs0235(output_path: Path) -> Dict[str, Any]:
    """Generates clean inter-state GST invoice from Rajput Steelworks to Codeify Technologies."""
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

    logo = LogoFlowable(width=48, height=48, color=RAJPUT_STEELWORKS.logo_color, text=RAJPUT_STEELWORKS.logo_initials)
    seller_text = f"""<b>{RAJPUT_STEELWORKS.name}</b><br/>
{RAJPUT_STEELWORKS.address}<br/>
<b>GSTIN:</b> {RAJPUT_STEELWORKS.gstin} | <b>PAN:</b> {RAJPUT_STEELWORKS.pan}<br/>
<b>Email:</b> {RAJPUT_STEELWORKS.email} | <b>Phone:</b> {RAJPUT_STEELWORKS.phone}
"""
    inv_title_text = """<font size="14"><b>TAX INVOICE</b></font><br/>
<font size="8" color="#666666">ORIGINAL FOR RECIPIENT</font>
"""
    header_table = Table(
        [[logo, Paragraph(seller_text, styles["TD"]), Paragraph(inv_title_text, styles["TD_Right"])]],
        colWidths=[55, 310, 160],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    buyer_info = f"""<b>Billed To (Recipient):</b><br/>
<b>{CODEIFY_TECH.name}</b><br/>
{CODEIFY_TECH.address}<br/>
<b>GSTIN:</b> {CODEIFY_TECH.gstin} | <b>State:</b> {CODEIFY_TECH.state} (Code: {CODEIFY_TECH.state_code})<br/>
<b>Place of Supply:</b> {CODEIFY_TECH.state_code}-{CODEIFY_TECH.state}
"""

    meta_info = """<b>Invoice No:</b> RS/2026-27/0235<br/>
<b>Invoice Date:</b> 18-Aug-2026<br/>
<b>Due Date:</b> 17-Sep-2026<br/>
<b>Reverse Charge:</b> No<br/>
<b>PO Reference:</b> CT-PO-2026-089
"""

    info_table = Table(
        [[Paragraph(buyer_info, styles["TD"]), Paragraph(meta_info, styles["TD"])]],
        colWidths=[310, 215],
    )
    info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    items_data = [
        [
            Paragraph("<b>#</b>", styles["TH"]),
            Paragraph("<b>Description of Goods</b>", styles["TH"]),
            Paragraph("<b>HSN/SAC</b>", styles["TH"]),
            Paragraph("<b>Qty</b>", styles["TH_Right"]),
            Paragraph("<b>Rate (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Amount (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("1", styles["TD"]),
            Paragraph("Cold Rolled Steel Coils (0.8mm CRCA)", styles["TD"]),
            Paragraph("7209", styles["TD"]),
            Paragraph("2.00 MT", styles["TD_Right"]),
            Paragraph("70,000.00", styles["TD_Right"]),
            Paragraph("1,40,000.00", styles["TD_Right"]),
        ],
        [
            Paragraph("2", styles["TD"]),
            Paragraph("Heavy Duty Server Rack Structural Frames", styles["TD"]),
            Paragraph("7308", styles["TD"]),
            Paragraph("12.00 Nos", styles["TD_Right"]),
            Paragraph("5,050.00", styles["TD_Right"]),
            Paragraph("60,600.00", styles["TD_Right"]),
        ],
    ]

    items_table = Table(items_data, colWidths=[25, 230, 65, 60, 70, 75])
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#CBD5E0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    summary_data = [
        ["", "", "Subtotal:", "2,00,600.00"],
        ["", "", "IGST @ 18.0%:", "36,108.00"],
        ["", "", "Total Invoice Value (INR):", "2,36,708.00"],
    ]
    summary_table = Table(
        [
            [
                "",
                "",
                Paragraph(f"<b>{row[2]}</b>", styles["TD_Right"] if "Total" not in row[2] else styles["TH_Right"]),
                Paragraph(f"<b>Rs. {row[3]}</b>" if "Total" in row[2] else f"{row[3]}", styles["TD_Right"] if "Total" not in row[2] else styles["TH_Right"]),
            ]
            for row in summary_data
        ],
        colWidths=[150, 140, 140, 95],
    )
    summary_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEABOVE", (2, 2), (3, 2), 1, colors.HexColor("#2D3748")),
        ("BACKGROUND", (2, 2), (3, 2), colors.HexColor("#EDF2F7")),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 15))

    bank_notes = f"""<b>Bank Details for Payment:</b><br/>
Bank Name: {RAJPUT_STEELWORKS.bank_name}<br/>
A/C No: {RAJPUT_STEELWORKS.account_number} | IFSC: {RAJPUT_STEELWORKS.ifsc}<br/>
Branch: {RAJPUT_STEELWORKS.branch}<br/>
Amount in Words: <i>Two Lakh Thirty-Six Thousand Seven Hundred Eight Rupees Only</i>
"""
    signoff = f"""<br/><br/>
For <b>{RAJPUT_STEELWORKS.name}</b><br/><br/><br/>
<b>Authorized Signatory</b>
"""
    footer_table = Table(
        [[Paragraph(bank_notes, styles["TD"]), Paragraph(signoff, styles["TD_Right"])]],
        colWidths=[330, 195],
    )
    footer_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(footer_table)

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "invoice_number": "RS/2026-27/0235",
        "date": "2026-08-18",
        "seller_name": RAJPUT_STEELWORKS.name,
        "seller_gstin": RAJPUT_STEELWORKS.gstin,
        "buyer_name": CODEIFY_TECH.name,
        "buyer_gstin": CODEIFY_TECH.gstin,
        "subtotal": 200600.00,
        "cgst": 0.00,
        "sgst": 0.00,
        "igst": 36108.00,
        "total": 236708.00,
        "tax_type": "inter_state",
    }


def generate_invoice_codeify_ct0189(output_path: Path) -> Dict[str, Any]:
    """Generates 2-page IT services invoice from Codeify Technologies to an enterprise client."""
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
    seller_text = f"""<b>{CODEIFY_TECH.name}</b><br/>
{CODEIFY_TECH.address}<br/>
<b>GSTIN:</b> {CODEIFY_TECH.gstin} | <b>PAN:</b> {CODEIFY_TECH.pan}<br/>
<b>Email:</b> {CODEIFY_TECH.email} | <b>Phone:</b> {CODEIFY_TECH.phone}
"""
    inv_title_text = """<font size="14"><b>TAX INVOICE</b></font><br/>
<font size="8" color="#666666">PAGE 1 OF 2 | ORIGINAL FOR RECIPIENT</font>
"""
    header_table = Table(
        [[logo, Paragraph(seller_text, styles["TD"]), Paragraph(inv_title_text, styles["TD_Right"])]],
        colWidths=[55, 310, 160],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    buyer_info = """<b>Billed To (Client):</b><br/>
<b>Apex Global Logistics Solutions Private Limited</b><br/>
Level 4, Pretech Tech Park, Bellandur, Bengaluru, Karnataka 560103<br/>
<b>GSTIN:</b> 29AAACA1234F1ZU | <b>State:</b> Karnataka (Code: 29)<br/>
<b>Place of Supply:</b> 29-Karnataka
"""
    meta_info = """<b>Invoice No:</b> CT/2026-27/0189<br/>
<b>Invoice Date:</b> 22-Aug-2026<br/>
<b>Master Agreement:</b> MSA-AGL-2024-001<br/>
<b>SOW Reference:</b> SOW-04-CLOUD-MIGRATION<br/>
<b>Currency:</b> INR (Indian Rupees)
"""

    info_table = Table(
        [[Paragraph(buyer_info, styles["TD"]), Paragraph(meta_info, styles["TD"])]],
        colWidths=[310, 215],
    )
    info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Professional Services & Deliverables Schedule</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))

    # 5 line items across pages
    items_data_p1 = [
        [
            Paragraph("<b>#</b>", styles["TH"]),
            Paragraph("<b>Service Description & Deliverables</b>", styles["TH"]),
            Paragraph("<b>SAC</b>", styles["TH"]),
            Paragraph("<b>Units / Hours</b>", styles["TH_Right"]),
            Paragraph("<b>Rate (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Amount (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("1", styles["TD"]),
            Paragraph("Enterprise Multi-Cloud Infrastructure Architecture Design & Review<br/><font size='7' color='#666666'>Milestone 1: Architectural Blueprints & Threat Model sign-off</font>", styles["TD"]),
            Paragraph("998313", styles["TD"]),
            Paragraph("1 Milestone", styles["TD_Right"]),
            Paragraph("2,50,000.00", styles["TD_Right"]),
            Paragraph("2,50,000.00", styles["TD_Right"]),
        ],
        [
            Paragraph("2", styles["TD"]),
            Paragraph("Kubernetes Cluster Hardening & CI/CD Pipeline Automation<br/><font size='7' color='#666666'>Milestone 2: Automated deployment pipeline into AWS EKS staging</font>", styles["TD"]),
            Paragraph("998314", styles["TD"]),
            Paragraph("1 Milestone", styles["TD_Right"]),
            Paragraph("2,00,000.00", styles["TD_Right"]),
            Paragraph("2,00,000.00", styles["TD_Right"]),
        ],
        [
            Paragraph("3", styles["TD"]),
            Paragraph("PostgreSQL Performance Tuning & Distributed Sharding Consulting<br/><font size='7' color='#666666'>Senior Database Specialist Engagement (50 billing hours @ Rs. 3,000/hr)</font>", styles["TD"]),
            Paragraph("998315", styles["TD"]),
            Paragraph("50 Hours", styles["TD_Right"]),
            Paragraph("3,000.00", styles["TD_Right"]),
            Paragraph("1,50,000.00", styles["TD_Right"]),
        ],
    ]

    items_table_p1 = Table(items_data_p1, colWidths=[25, 230, 65, 60, 70, 75])
    items_table_p1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#CBD5E0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
    ]))
    story.append(items_table_p1)
    story.append(Spacer(1, 15))
    story.append(Paragraph("<i>(Deliverables schedule continued on page 2...)</i>", styles["FinePrint"]))

    # PAGE 2
    story.append(PageBreak())

    header_table_p2 = Table(
        [[logo, Paragraph(f"<b>{CODEIFY_TECH.name}</b> — Invoice CT/2026-27/0189", styles["TD"]), Paragraph("<b>PAGE 2 OF 2</b>", styles["TD_Right"])]],
        colWidths=[55, 365, 105],
    )
    header_table_p2.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E0")),
    ]))
    story.append(header_table_p2)
    story.append(Spacer(1, 10))

    items_data_p2 = [
        [
            Paragraph("<b>#</b>", styles["TH"]),
            Paragraph("<b>Service Description & Deliverables</b>", styles["TH"]),
            Paragraph("<b>SAC</b>", styles["TH"]),
            Paragraph("<b>Units / Hours</b>", styles["TH_Right"]),
            Paragraph("<b>Rate (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Amount (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("4", styles["TD"]),
            Paragraph("Zero-Trust IAM Policy Implementation & Compliance Audit<br/><font size='7' color='#666666'>Milestone 3: SOC2 & ISO 27001 evidence generation automated</font>", styles["TD"]),
            Paragraph("998313", styles["TD"]),
            Paragraph("1 Milestone", styles["TD_Right"]),
            Paragraph("1,00,000.00", styles["TD_Right"]),
            Paragraph("1,00,000.00", styles["TD_Right"]),
        ],
        [
            Paragraph("5", styles["TD"]),
            Paragraph("Production Go-Live 24x7 War-Room Support Coverage<br/><font size='7' color='#666666'>Level 3 Engineering on-call stand-by (10 staff days)</font>", styles["TD"]),
            Paragraph("998319", styles["TD"]),
            Paragraph("10 Days", styles["TD_Right"]),
            Paragraph("5,000.00", styles["TD_Right"]),
            Paragraph("50,000.00", styles["TD_Right"]),
        ],
    ]

    items_table_p2 = Table(items_data_p2, colWidths=[25, 230, 65, 60, 70, 75])
    items_table_p2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EDF2F7")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#CBD5E0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
    ]))
    story.append(items_table_p2)
    story.append(Spacer(1, 10))

    summary_data_p2 = [
        ["", "", "Subtotal (Items 1-5):", "7,50,000.00"],
        ["", "", "IGST @ 18.0% (Inter-State):", "1,35,000.00"],
        ["", "", "Total Invoice Amount (INR):", "8,85,000.00"],
    ]
    summary_table_p2 = Table(
        [
            [
                "",
                "",
                Paragraph(f"<b>{row[2]}</b>", styles["TD_Right"] if "Total" not in row[2] else styles["TH_Right"]),
                Paragraph(f"<b>Rs. {row[3]}</b>" if "Total" in row[2] else f"{row[3]}", styles["TD_Right"] if "Total" not in row[2] else styles["TH_Right"]),
            ]
            for row in summary_data_p2
        ],
        colWidths=[150, 140, 140, 95],
    )
    summary_table_p2.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("LINEABOVE", (2, 2), (3, 2), 1, colors.HexColor("#2D3748")),
        ("BACKGROUND", (2, 2), (3, 2), colors.HexColor("#EDF2F7")),
    ]))
    story.append(summary_table_p2)
    story.append(Spacer(1, 20))

    bank_notes_p2 = f"""<b>Bank Wire Transfer Instructions:</b><br/>
Beneficiary: <b>{CODEIFY_TECH.name}</b><br/>
Bank Name: {CODEIFY_TECH.bank_name}<br/>
A/C Number: {CODEIFY_TECH.account_number} (Current Account)<br/>
IFSC Code: {CODEIFY_TECH.ifsc} | Branch: {CODEIFY_TECH.branch}<br/>
Amount in Words: <i>Eight Lakh Eighty-Five Thousand Rupees Only</i>
"""
    signoff_p2 = f"""<br/>
For <b>{CODEIFY_TECH.name}</b><br/><br/><br/>
<b>Designated Partner / Authorized Signatory</b>
"""
    footer_table_p2 = Table(
        [[Paragraph(bank_notes_p2, styles["TD"]), Paragraph(signoff_p2, styles["TD_Right"])]],
        colWidths=[330, 195],
    )
    footer_table_p2.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEABOVE", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(footer_table_p2)

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "invoice_number": "CT/2026-27/0189",
        "date": "2026-08-22",
        "seller_name": CODEIFY_TECH.name,
        "seller_gstin": CODEIFY_TECH.gstin,
        "buyer_name": "Apex Global Logistics Solutions Private Limited",
        "buyer_gstin": "29AAACA1234F1ZU",
        "subtotal": 750000.00,
        "cgst": 0.00,
        "sgst": 0.00,
        "igst": 135000.00,
        "total": 885000.00,
        "tax_type": "inter_state",
    }
