"""
GSTR-3B PDF Generator for Clean Category.
Produces:
- gstr3b_rajput_aug2026.pdf (Manufacturing, intra-state dominant, turnover ₹22.4L, ITC ₹1.8L)
- gstr3b_codeify_aug2026.pdf (Tech LLP, export/LUT + inter-state IGST, turnover ₹38.7L)
Strictly satisfies: net_itc = itc_available - itc_reversed
"""
from pathlib import Path
from typing import Dict, Any
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from .base import NumberedCanvas, LogoFlowable, format_inr, get_doc_styles
from ..universe import RAJPUT_STEELWORKS, CODEIFY_TECH


def generate_gstr3b_rajput_aug2026(output_path: Path) -> Dict[str, Any]:
    """Generates official-format GSTR-3B return for Rajput Steelworks Pvt Ltd for August 2026."""
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

    # GST Portal Header
    gov_logo = LogoFlowable(width=44, height=44, color=(0.12, 0.28, 0.45), text="GSTN")
    gov_hdr = """<b>Goods and Services Tax</b><br/>
<font size="8">Government of India & Government of Gujarat<br/>
Form GSTR-3B [See rule 61(5)] — Monthly Return</font>
"""
    ret_meta = """<b>Year:</b> 2026-27<br/>
<b>Period:</b> August 2026<br/>
<b>Status:</b> Filed (ARN: AA240826019284F)
"""
    header_table = Table(
        [[gov_logo, Paragraph(gov_hdr, styles["TD"]), Paragraph(ret_meta, styles["TD_Right"])]],
        colWidths=[50, 315, 170],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#1E3A8A")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    # Basic Details
    basic_info = f"""<b>1. GSTIN:</b> {RAJPUT_STEELWORKS.gstin} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <b>2. Legal Name:</b> {RAJPUT_STEELWORKS.name}<br/>
<b>Trade Name:</b> {RAJPUT_STEELWORKS.trade_name} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <b>Filing Date:</b> 20/09/2026
"""
    info_table = Table([[Paragraph(basic_info, styles["TD"])]], colWidths=[535])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    # Table 3.1 Outward supplies
    story.append(Paragraph("<b>3.1 Details of Outward Supplies and inward supplies liable to reverse charge</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))

    t31_data = [
        [
            Paragraph("<b>Nature of Supplies</b>", styles["TH"]),
            Paragraph("<b>Total Taxable Value (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Integrated Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Central Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>State/UT Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Cess (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("(a) Outward taxable supplies (other than zero rated, nil rated and exempted)", styles["TD"]),
            Paragraph("22,40,000.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("2,01,600.00", styles["TD_Right"]),
            Paragraph("2,01,600.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("(b) Outward taxable supplies (zero rated)", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("(c) Other outward supplies (Nil rated, exempted)", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
        ],
        [
            Paragraph("(d) Inward supplies (liable to reverse charge)", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("(e) Non-GST outward supplies", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
        ],
        [
            Paragraph("<b>Total Outward Supplies</b>", styles["TH"]),
            Paragraph("<b>22,40,000.00</b>", styles["TH_Right"]),
            Paragraph("<b>0.00</b>", styles["TH_Right"]),
            Paragraph("<b>2,01,600.00</b>", styles["TH_Right"]),
            Paragraph("<b>2,01,600.00</b>", styles["TH_Right"]),
            Paragraph("<b>0.00</b>", styles["TH_Right"]),
        ],
    ]

    t31_table = Table(t31_data, colWidths=[185, 80, 70, 70, 70, 60])
    t31_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#1E3A8A")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(t31_table)
    story.append(Spacer(1, 12))

    # Table 4 Eligible ITC
    story.append(Paragraph("<b>4. Eligible ITC (Input Tax Credit)</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))

    t4_data = [
        [
            Paragraph("<b>Details</b>", styles["TH"]),
            Paragraph("<b>Integrated Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Central Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>State/UT Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Cess (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("<b>(A) ITC Available (whether in full or part)</b>", styles["TH"]),
            Paragraph("", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(1) Import of goods", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(2) Import of services", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(3) Inward supplies liable to reverse charge", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(4) Inward supplies from ISD", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(5) All other ITC (Purchases & Expenses)", styles["TD"]),
            Paragraph("18,000.00", styles["TD_Right"]), Paragraph("81,000.00", styles["TD_Right"]), Paragraph("81,000.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("<b>Subtotal (A) ITC Available</b>", styles["TH"]),
            Paragraph("<b>18,000.00</b>", styles["TH_Right"]), Paragraph("<b>81,000.00</b>", styles["TH_Right"]), Paragraph("<b>81,000.00</b>", styles["TH_Right"]), Paragraph("<b>0.00</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("<b>(B) ITC Reversed</b>", styles["TH"]),
            Paragraph("", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(1) As per rules 38, 42 & 43 of CGST Rules", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(2) Others (Credit notes / ineligible reversal)", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]), Paragraph("2,500.00", styles["TD_Right"]), Paragraph("2,500.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("<b>Subtotal (B) ITC Reversed</b>", styles["TH"]),
            Paragraph("<b>0.00</b>", styles["TH_Right"]), Paragraph("<b>2,500.00</b>", styles["TH_Right"]), Paragraph("<b>2,500.00</b>", styles["TH_Right"]), Paragraph("<b>0.00</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("<b>(C) Net ITC Available (A) - (B)</b>", styles["TH"]),
            Paragraph("<b>18,000.00</b>", styles["TH_Right"]), Paragraph("<b>78,500.00</b>", styles["TH_Right"]), Paragraph("<b>78,500.00</b>", styles["TH_Right"]), Paragraph("<b>0.00</b>", styles["TH_Right"]),
        ],
    ]

    t4_table = Table(t4_data, colWidths=[235, 75, 75, 75, 75])
    t4_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 7), (-1, 7), colors.HexColor("#F1F5F9")),
        ("BACKGROUND", (0, 11), (-1, 11), colors.HexColor("#F1F5F9")),
        ("BACKGROUND", (0, 12), (-1, 12), colors.HexColor("#E0E7FF")),
        ("LINEABOVE", (0, 12), (-1, 12), 1, colors.HexColor("#1E3A8A")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(t4_table)
    story.append(Spacer(1, 12))

    # Table 5.1 Verification
    story.append(Paragraph("<b>Verification & Declaration</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))
    decl_text = f"""I hereby solemnly affirm and declare that the information given herein above is true and correct to the best of my knowledge and belief and nothing has been concealed therefrom.<br/><br/>
<b>Authorized Signatory:</b> Rajput Steelworks Private Limited &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Designation:</b> Director<br/>
<b>Date of Filing:</b> 20-09-2026 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Place:</b> Ahmedabad
"""
    decl_table = Table([[Paragraph(decl_text, styles["FinePrint"])]], colWidths=[535])
    decl_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(decl_table)

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "form_type": "GSTR-3B",
        "return_period": "August 2026",
        "gstin": RAJPUT_STEELWORKS.gstin,
        "legal_name": RAJPUT_STEELWORKS.name,
        "taxable_turnover": 2240000.00,
        "outward_igst": 0.00,
        "outward_cgst": 201600.00,
        "outward_sgst": 201600.00,
        "itc_available_igst": 18000.00,
        "itc_available_cgst": 81000.00,
        "itc_available_sgst": 81000.00,
        "itc_available_total": 180000.00,
        "itc_reversed_igst": 0.00,
        "itc_reversed_cgst": 2500.00,
        "itc_reversed_sgst": 2500.00,
        "itc_reversed_total": 5000.00,
        "net_itc_igst": 18000.00,
        "net_itc_cgst": 78500.00,
        "net_itc_sgst": 78500.00,
        "net_itc_total": 175000.00,
        "math_verified": True,
    }


def generate_gstr3b_codeify_aug2026(output_path: Path) -> Dict[str, Any]:
    """Generates official-format GSTR-3B return for Codeify Technologies LLP for August 2026."""
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

    gov_logo = LogoFlowable(width=44, height=44, color=(0.12, 0.28, 0.45), text="GSTN")
    gov_hdr = """<b>Goods and Services Tax</b><br/>
<font size="8">Government of India & Government of Maharashtra<br/>
Form GSTR-3B [See rule 61(5)] — Monthly Return</font>
"""
    ret_meta = """<b>Year:</b> 2026-27<br/>
<b>Period:</b> August 2026<br/>
<b>Status:</b> Filed (ARN: AA270826084920E)
"""
    header_table = Table(
        [[gov_logo, Paragraph(gov_hdr, styles["TD"]), Paragraph(ret_meta, styles["TD_Right"])]],
        colWidths=[50, 315, 170],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1.5, colors.HexColor("#1E3A8A")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))

    basic_info = f"""<b>1. GSTIN:</b> {CODEIFY_TECH.gstin} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <b>2. Legal Name:</b> {CODEIFY_TECH.name}<br/>
<b>Trade Name:</b> {CODEIFY_TECH.trade_name} &nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp; <b>Filing Date:</b> 18/09/2026
"""
    info_table = Table([[Paragraph(basic_info, styles["TD"])]], colWidths=[535])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>3.1 Details of Outward Supplies and inward supplies liable to reverse charge</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))

    t31_data = [
        [
            Paragraph("<b>Nature of Supplies</b>", styles["TH"]),
            Paragraph("<b>Total Taxable Value (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Integrated Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Central Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>State/UT Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Cess (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("(a) Outward taxable supplies (other than zero rated)", styles["TD"]),
            Paragraph("30,70,000.00", styles["TD_Right"]),
            Paragraph("5,52,600.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("(b) Outward taxable supplies (zero rated - Software Export under LUT)", styles["TD"]),
            Paragraph("8,00,000.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("(c) Other outward supplies (Nil rated, exempted)", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
        ],
        [
            Paragraph("(d) Inward supplies (liable to reverse charge)", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("(e) Non-GST outward supplies", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
            Paragraph("-", styles["TD_Right"]),
        ],
        [
            Paragraph("<b>Total Outward Supplies</b>", styles["TH"]),
            Paragraph("<b>38,70,000.00</b>", styles["TH_Right"]),
            Paragraph("<b>5,52,600.00</b>", styles["TH_Right"]),
            Paragraph("<b>0.00</b>", styles["TH_Right"]),
            Paragraph("<b>0.00</b>", styles["TH_Right"]),
            Paragraph("<b>0.00</b>", styles["TH_Right"]),
        ],
    ]

    t31_table = Table(t31_data, colWidths=[185, 80, 70, 70, 70, 60])
    t31_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.HexColor("#1E3A8A")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(t31_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>4. Eligible ITC (Input Tax Credit)</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))

    t4_data = [
        [
            Paragraph("<b>Details</b>", styles["TH"]),
            Paragraph("<b>Integrated Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Central Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>State/UT Tax (Rs.)</b>", styles["TH_Right"]),
            Paragraph("<b>Cess (Rs.)</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("<b>(A) ITC Available (whether in full or part)</b>", styles["TH"]),
            Paragraph("", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(1) Import of goods", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(2) Import of services (Cloud Hosting & SaaS)", styles["TD"]),
            Paragraph("34,200.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(3) Inward supplies liable to reverse charge", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(4) Inward supplies from ISD", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(5) All other ITC (Office lease, hardware, consultants)", styles["TD"]),
            Paragraph("50,000.00", styles["TD_Right"]), Paragraph("26,400.00", styles["TD_Right"]), Paragraph("26,400.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("<b>Subtotal (A) ITC Available</b>", styles["TH"]),
            Paragraph("<b>84,200.00</b>", styles["TH_Right"]), Paragraph("<b>26,400.00</b>", styles["TH_Right"]), Paragraph("<b>26,400.00</b>", styles["TH_Right"]), Paragraph("<b>0.00</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("<b>(B) ITC Reversed</b>", styles["TH"]),
            Paragraph("", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"]), Paragraph("", styles["TD"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(1) As per rules 38, 42 & 43 of CGST Rules", styles["TD"]),
            Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("&nbsp;&nbsp;(2) Others (Credit note adjustments)", styles["TD"]),
            Paragraph("4,200.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]), Paragraph("0.00", styles["TD_Right"]),
        ],
        [
            Paragraph("<b>Subtotal (B) ITC Reversed</b>", styles["TH"]),
            Paragraph("<b>4,200.00</b>", styles["TH_Right"]), Paragraph("<b>0.00</b>", styles["TH_Right"]), Paragraph("<b>0.00</b>", styles["TH_Right"]), Paragraph("<b>0.00</b>", styles["TH_Right"]),
        ],
        [
            Paragraph("<b>(C) Net ITC Available (A) - (B)</b>", styles["TH"]),
            Paragraph("<b>80,000.00</b>", styles["TH_Right"]), Paragraph("<b>26,400.00</b>", styles["TH_Right"]), Paragraph("<b>26,400.00</b>", styles["TH_Right"]), Paragraph("<b>0.00</b>", styles["TH_Right"]),
        ],
    ]

    t4_table = Table(t4_data, colWidths=[235, 75, 75, 75, 75])
    t4_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("BACKGROUND", (0, 7), (-1, 7), colors.HexColor("#F1F5F9")),
        ("BACKGROUND", (0, 11), (-1, 11), colors.HexColor("#F1F5F9")),
        ("BACKGROUND", (0, 12), (-1, 12), colors.HexColor("#E0E7FF")),
        ("LINEABOVE", (0, 12), (-1, 12), 1, colors.HexColor("#1E3A8A")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
    ]))
    story.append(t4_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Verification & Declaration</b>", styles["SectionHeading"]))
    story.append(Spacer(1, 4))
    decl_text = f"""I hereby solemnly affirm and declare that the information given herein above is true and correct to the best of my knowledge and belief and nothing has been concealed therefrom.<br/><br/>
<b>Authorized Signatory:</b> Codeify Technologies LLP &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Designation:</b> Designated Partner<br/>
<b>Date of Filing:</b> 18-09-2026 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Place:</b> Pune
"""
    decl_table = Table([[Paragraph(decl_text, styles["FinePrint"])]], colWidths=[535])
    decl_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(decl_table)

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "form_type": "GSTR-3B",
        "return_period": "August 2026",
        "gstin": CODEIFY_TECH.gstin,
        "legal_name": CODEIFY_TECH.name,
        "taxable_turnover": 3870000.00,
        "outward_igst": 552600.00,
        "outward_cgst": 0.00,
        "outward_sgst": 0.00,
        "itc_available_igst": 84200.00,
        "itc_available_cgst": 26400.00,
        "itc_available_sgst": 26400.00,
        "itc_available_total": 137000.00,
        "itc_reversed_igst": 4200.00,
        "itc_reversed_cgst": 0.00,
        "itc_reversed_sgst": 0.00,
        "itc_reversed_total": 4200.00,
        "net_itc_igst": 80000.00,
        "net_itc_cgst": 26400.00,
        "net_itc_sgst": 26400.00,
        "net_itc_total": 132800.00,
        "math_verified": True,
    }
