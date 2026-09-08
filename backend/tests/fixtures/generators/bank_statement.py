"""
Bank Statement PDF Generator for Clean Category.
Produces:
- bank_stmt_rajput_aug2026.pdf (SBI Current Account, 2 pages, 35 transactions, exact reconciliation)
- bank_stmt_codeify_aug2026.pdf (Axis Bank Current Account, 2 pages, 28 transactions, exact reconciliation)
"""
from pathlib import Path
from typing import List, Dict, Any, Tuple
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from .base import NumberedCanvas, LogoFlowable, format_inr, get_doc_styles
from ..universe import RAJPUT_STEELWORKS, CODEIFY_TECH


def _build_reconciled_txns(opening_balance: float, raw_txns: List[Tuple[str, str, str, float, float]]):
    """
    Given raw transactions (date, desc, ref, debit, credit), computes exact running balance.
    Returns: list of dicts with calculated balance, plus summary dict.
    """
    current_bal = opening_balance
    processed = []
    total_debits = 0.0
    total_credits = 0.0

    for dt, desc, ref, dr, cr in raw_txns:
        current_bal = round(current_bal - dr + cr, 2)
        total_debits = round(total_debits + dr, 2)
        total_credits = round(total_credits + cr, 2)
        processed.append({
            "date": dt,
            "description": desc,
            "ref_no": ref,
            "debit": dr,
            "credit": cr,
            "balance": current_bal,
        })

    closing_balance = current_bal
    # Verify exact math
    assert round(opening_balance + total_credits - total_debits, 2) == round(closing_balance, 2)

    return processed, {
        "opening_balance": opening_balance,
        "total_debits": total_debits,
        "total_credits": total_credits,
        "closing_balance": closing_balance,
        "count": len(processed),
    }


def generate_bank_stmt_rajput_aug2026(output_path: Path) -> Dict[str, Any]:
    """Generates 2-page SBI Bank Statement for Rajput Steelworks Pvt Ltd."""
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

    # 35 transactions
    raw_txns = [
        ("01/08/2026", "NEFT-INW: GODREJ INDS-PAYMENT 4412", "SBIN92621001", 0.0, 350000.0),
        ("02/08/2026", "CHQ CLG: TATA STEEL LTD INV 9901", "CHQ-001241", 420000.0, 0.0),
        ("03/08/2026", "RTGS-OUT: SAIL RAW MATERIAL PO 881", "SBINR0261102", 510000.0, 0.0),
        ("04/08/2026", "UPI/DR/6211098/HPCL FUEL DISPENSING", "UPI-62110982", 14500.0, 0.0),
        ("05/08/2026", "ACH/DR: TRENT AUTOMATION EMI", "ACH-4019283", 38500.0, 0.0),
        ("06/08/2026", "NEFT-INW: KAPOOR & SHAH ADV 110", "HDFCN2621800", 0.0, 118000.0),
        ("07/08/2026", "SALARY DISBURSEMENT JULY 2026", "CMS-SAL-0726", 485000.0, 0.0),
        ("08/08/2026", "EPFO ELECTRONIC CHALLAN RETURN", "TRRN-1082601", 58400.0, 0.0),
        ("10/08/2026", "ESIC MONTHLY STATUTORY DEDUCTION", "ESIC-2026081", 12300.0, 0.0),
        ("11/08/2026", "NEFT-INW: L&T HEAVY ENGR PART-PAY", "AXISN2622301", 0.0, 620000.0),
        ("12/08/2026", "BILL PAYMENT: UGVCL ELECTRICITY", "UGVCL-882194", 94250.0, 0.0),
        ("13/08/2026", "CHQ CLG: JINDAL TUBES & PIPES", "CHQ-001242", 185000.0, 0.0),
        ("14/08/2026", "NEFT-INW: SHREE RAM FOUNDRY CR", "ICICN2622605", 0.0, 240000.0),
        ("16/08/2026", "RTGS-OUT: ADANI SOLAR ROOFTOP AMC", "SBINR0261601", 45000.0, 0.0),
        ("17/08/2026", "UPI/DR/6229910/AMAZON BUSINESS", "UPI-62299101", 8200.0, 0.0),
        ("18/08/2026", "CHQ CLG: RELIANCE INDUSTRIAL OILS", "CHQ-001243", 64000.0, 0.0),
        ("19/08/2026", "GST PAYMENT PMT-06 CASH LEDGER", "CPIN-2408261", 125000.0, 0.0),
        # Page break target ~ txn 18
        ("20/08/2026", "NEFT-INW: THERMAX BOILERS CR", "PUNBN2623201", 0.0, 480000.0),
        ("21/08/2026", "TDS CHALLAN 281 PAYMENT JUL 26", "BSR-00034561", 42500.0, 0.0),
        ("22/08/2026", "RTGS-OUT: MAHARASHTRA SEAMLESS", "SBINR0262201", 310000.0, 0.0),
        ("23/08/2026", "POS/DR: IOCL FLEET DIESEL FUEL", "POS-88910291", 24000.0, 0.0),
        ("24/08/2026", "NEFT-INW: BHARAT FORGE PO 9122", "KKBKN2623601", 0.0, 520000.0),
        ("25/08/2026", "CHQ CLG: GUJARAT GAS INDUSTRIAL", "CHQ-001244", 76400.0, 0.0),
        ("26/08/2026", "BANK CHARGES: RTGS/NEFT BULK", "SBICHG-08260", 1180.0, 0.0),
        ("27/08/2026", "NEFT-INW: MAHINDRA CIE AUTO CR", "BARBN2623901", 0.0, 390000.0),
        ("27/08/2026", "CHQ CLG: SHREE CEMENT CRUSHERS", "CHQ-001245", 112000.0, 0.0),
        ("28/08/2026", "RTGS-OUT: STEEL AUTHORITY BOKARO", "SBINR0262801", 450000.0, 0.0),
        ("28/08/2026", "INTEREST CREDIT: AUTO-SWEEP MOD", "SBI-INT-0826", 0.0, 14220.0),
        ("29/08/2026", "NEFT-INW: CODEIFY TECH CT0189", "UTIBN2624101", 0.0, 236708.0),
        ("29/08/2026", "ACH/DR: BAJAJ ALLIANZ ASSET INS", "ACH-8891002", 48200.0, 0.0),
        ("30/08/2026", "CHQ CLG: KALYANI FORGING METALS", "CHQ-001246", 195000.0, 0.0),
        ("30/08/2026", "UPI/DR/6241901/INDIGO AIR CARGO", "UPI-62419012", 18500.0, 0.0),
        ("31/08/2026", "MONTHLY CURRENT A/C MAINT CHG", "SBIMNT-08260", 590.0, 0.0),
        ("31/08/2026", "SWEEP TRANSFER TO MULTI-OPTION", "SBIMOD-31082", 200000.0, 0.0),
        ("31/08/2026", "NEFT-INW: SUZLON ENERGY CR", "SBIN92624301", 0.0, 185000.0),
    ]

    opening_balance = 1450230.50
    txns, summary = _build_reconciled_txns(opening_balance, raw_txns)

    # PAGE 1 HEADER
    sbi_logo = LogoFlowable(width=44, height=44, color=(0.10, 0.35, 0.65), text="SBI")
    bank_hdr = """<b>STATE BANK OF INDIA</b><br/>
<font size="8">Vatva Industrial Estate Branch (03456)<br/>
GIDC Phase 2, Vatva, Ahmedabad - 382445 | IFSC: SBIN0003456</font>
"""
    stmt_meta = """<font size="12"><b>ACCOUNT STATEMENT</b></font><br/>
<font size="8">Statement Period: 01/08/2026 to 31/08/2026<br/>
Account Type: Current Account (Corporate)</font>
"""
    header_table = Table(
        [[sbi_logo, Paragraph(bank_hdr, styles["TD"]), Paragraph(stmt_meta, styles["TD_Right"])]],
        colWidths=[50, 275, 210],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#105990")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))

    acct_details = f"""<b>Account Holder:</b> {RAJPUT_STEELWORKS.name}<br/>
<b>Address:</b> {RAJPUT_STEELWORKS.address}<br/>
<b>Account Number:</b> {RAJPUT_STEELWORKS.account_number} | <b>CIF No:</b> 88491029381<br/>
<b>PAN:</b> {RAJPUT_STEELWORKS.pan} | <b>GSTIN:</b> {RAJPUT_STEELWORKS.gstin}
"""
    summary_box = f"""<b>Opening Balance:</b> Rs. {format_inr(summary['opening_balance'], symbol='')}<br/>
<b>Total Credits (Deposits):</b> Rs. {format_inr(summary['total_credits'], symbol='')}<br/>
<b>Total Debits (Withdrawals):</b> Rs. {format_inr(summary['total_debits'], symbol='')}<br/>
<b>Closing Balance:</b> <b>Rs. {format_inr(summary['closing_balance'], symbol='')}</b>
"""
    cust_table = Table(
        [[Paragraph(acct_details, styles["TD"]), Paragraph(summary_box, styles["TD"])]],
        colWidths=[315, 220],
    )
    cust_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(cust_table)
    story.append(Spacer(1, 8))

    th_row = [
        Paragraph("<b>Date</b>", styles["TH"]),
        Paragraph("<b>Transaction Description</b>", styles["TH"]),
        Paragraph("<b>Ref / Chq No</b>", styles["TH"]),
        Paragraph("<b>Debit (Rs.)</b>", styles["TH_Right"]),
        Paragraph("<b>Credit (Rs.)</b>", styles["TH_Right"]),
        Paragraph("<b>Balance (Rs.)</b>", styles["TH_Right"]),
    ]

    # Split into 18 txns on Page 1, 17 txns on Page 2
    p1_rows = [th_row]
    for t in txns[:18]:
        dr_str = format_inr(t["debit"], symbol="") if t["debit"] > 0 else "-"
        cr_str = format_inr(t["credit"], symbol="") if t["credit"] > 0 else "-"
        bal_str = format_inr(t["balance"], symbol="")
        p1_rows.append([
            Paragraph(t["date"], styles["TD"]),
            Paragraph(t["description"], styles["TD"]),
            Paragraph(t["ref_no"], styles["TD"]),
            Paragraph(dr_str, styles["TD_Right"]),
            Paragraph(cr_str, styles["TD_Right"]),
            Paragraph(bal_str, styles["TD_Right"]),
        ])

    table_p1 = Table(p1_rows, colWidths=[55, 185, 80, 70, 70, 75])
    table_p1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#94A3B8")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(table_p1)
    story.append(Spacer(1, 8))
    story.append(Paragraph("<i>(Statement continued on next page...)</i>", styles["FinePrint"]))

    # PAGE 2
    story.append(PageBreak())

    p2_hdr = Table(
        [[
            sbi_logo,
            Paragraph(f"<b>STATE BANK OF INDIA</b> — Current A/C {RAJPUT_STEELWORKS.account_number} ({RAJPUT_STEELWORKS.name})", styles["TD"]),
            Paragraph("<b>PAGE 2 OF 2</b>", styles["TD_Right"]),
        ]],
        colWidths=[44, 385, 106],
    )
    p2_hdr.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#105990")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(p2_hdr)
    story.append(Spacer(1, 8))

    p2_rows = [th_row]
    for t in txns[18:]:
        dr_str = format_inr(t["debit"], symbol="") if t["debit"] > 0 else "-"
        cr_str = format_inr(t["credit"], symbol="") if t["credit"] > 0 else "-"
        bal_str = format_inr(t["balance"], symbol="")
        p2_rows.append([
            Paragraph(t["date"], styles["TD"]),
            Paragraph(t["description"], styles["TD"]),
            Paragraph(t["ref_no"], styles["TD"]),
            Paragraph(dr_str, styles["TD_Right"]),
            Paragraph(cr_str, styles["TD_Right"]),
            Paragraph(bal_str, styles["TD_Right"]),
        ])

    table_p2 = Table(p2_rows, colWidths=[55, 185, 80, 70, 70, 75])
    table_p2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E2E8F0")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#94A3B8")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))
    story.append(table_p2)
    story.append(Spacer(1, 10))

    # Statement Reconciliation Footer
    reconciled_footer = [
        ["", "TOTALS FOR PERIOD:", f"Rs. {format_inr(summary['total_debits'], symbol='')}", f"Rs. {format_inr(summary['total_credits'], symbol='')}", f"Rs. {format_inr(summary['closing_balance'], symbol='')}"],
    ]
    reconciled_table = Table(
        [
            [
                "",
                Paragraph("<b>ACCOUNT SUMMARY TOTALS</b>", styles["TH_Right"]),
                Paragraph(f"<b>{reconciled_footer[0][2]}</b>", styles["TH_Right"]),
                Paragraph(f"<b>{reconciled_footer[0][3]}</b>", styles["TH_Right"]),
                Paragraph(f"<b>{reconciled_footer[0][4]}</b>", styles["TH_Right"]),
            ]
        ],
        colWidths=[120, 200, 70, 70, 75],
    )
    reconciled_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E2E8F0")),
        ("LINEABOVE", (0, 0), (-1, -1), 1, colors.HexColor("#105990")),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#105990")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(reconciled_table)
    story.append(Spacer(1, 15))

    footer_disclaimer = """<font size="7" color="#64748B">
Unless a constituent notifies the Bank immediately of any discrepancy found in this statement of account, it will be taken that the account has been verified and found correct.<br/>
This is a computer generated statement and does not require a physical signature. State Bank of India | CIN: L65110MH1955GOI009772
</font>"""
    story.append(Paragraph(footer_disclaimer, styles["FinePrint"]))

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "bank_name": RAJPUT_STEELWORKS.bank_name,
        "account_number": RAJPUT_STEELWORKS.account_number,
        "account_holder": RAJPUT_STEELWORKS.name,
        "statement_period": "01/08/2026 to 31/08/2026",
        "opening_balance": summary["opening_balance"],
        "total_debits": summary["total_debits"],
        "total_credits": summary["total_credits"],
        "closing_balance": summary["closing_balance"],
        "transaction_count": summary["count"],
        "reconciled": True,
    }


def generate_bank_stmt_codeify_aug2026(output_path: Path) -> Dict[str, Any]:
    """Generates 2-page Axis Bank Statement for Codeify Technologies LLP."""
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

    # 28 transactions
    raw_txns = [
        ("01/08/2026", "INW NEFT: FINCORP SYSTEMS INC", "AXISN2621401", 0.0, 680000.0),
        ("02/08/2026", "DR: AWS CLOUD INFRA SERVICES", "POS-AWS-08261", 142350.0, 0.0),
        ("03/08/2026", "DR: GOOGLE WORKSPACE SUBSCRIPTION", "POS-GOOG-882", 28400.0, 0.0),
        ("04/08/2026", "DR: GITHUB ENTERPRISE ANNUAL", "POS-GHUB-109", 54000.0, 0.0),
        ("05/08/2026", "ACH: MAGARPATTA CYBER CITY RENT", "ACH-CYBER-89", 175000.0, 0.0),
        ("07/08/2026", "SALARY PAYMENT MONTH JULY 2026", "SAL-NEFT-0726", 1120000.0, 0.0),
        ("08/08/2026", "EPFO ONLINE MONTHLY DEPOSIT", "EPFO-082026-1", 118400.0, 0.0),
        ("09/08/2026", "PROFESSIONAL TAX GOVT OF MAHA", "PTEC-2708261", 4600.0, 0.0),
        ("11/08/2026", "INW RTGS: MEDTECH GLOBAL ASIA", "HDFCR2622301", 0.0, 850000.0),
        ("12/08/2026", "DR: TATA TELE LEASED LINE INTERNET", "ACH-TTEL-441", 32500.0, 0.0),
        ("14/08/2026", "INW NEFT: VIBRANT APPS CORP", "SBIN92622601", 0.0, 320000.0),
        ("15/08/2026", "OUT RTGS: DELL SERVER PROCUREMENT", "AXISR0261501", 380000.0, 0.0),
        ("17/08/2026", "DR: SLACK TECHNOLOGIES ANNUAL", "POS-SLACK-99", 68000.0, 0.0),
        ("18/08/2026", "OUT NEFT: RAJPUT STEELWORKS RS0235", "AXISN2623001", 236708.0, 0.0),
        # Page 2 target ~ txn 15
        ("20/08/2026", "INW RTGS: APEX GLOBAL LOGISTICS", "KKBKR2623201", 0.0, 885000.0),
        ("21/08/2026", "DR: SUTTER LABS AI API COMPUTE", "POS-SUTTER-2", 46800.0, 0.0),
        ("22/08/2026", "TDS SEC 194J & 192 CHALLAN 281", "BSR-00012341", 168000.0, 0.0),
        ("24/08/2026", "GST TAX PAYMENT OLTAS PMT-06", "GST-PMT06-27", 135000.0, 0.0),
        ("25/08/2026", "INW NEFT: CITRIX SYSTEMS CONSULT", "CITIN2623701", 0.0, 450000.0),
        ("26/08/2026", "DR: JETBRAINS ALL PRODUCTS PACK", "POS-JETB-082", 24200.0, 0.0),
        ("27/08/2026", "DR: CLEANING & FACILITY SERVICES", "CHQ-004412", 28000.0, 0.0),
        ("28/08/2026", "INW NEFT: HYPERLINK INFRA LTD", "ICICN2624001", 0.0, 520000.0),
        ("28/08/2026", "INTEREST CREDIT: AUTO FLEXI SWEEP", "AXIS-INT-082", 0.0, 22480.0),
        ("29/08/2026", "DR: DATADOG MONITORING SAAS", "POS-DDOG-819", 38400.0, 0.0),
        ("30/08/2026", "OUT NEFT: CA KAPOOR & SHAH AUDIT", "AXISN2624201", 75000.0, 0.0),
        ("31/08/2026", "DR: CURRENT A/C MONTHLY CHARGES", "AXISMNT-082", 885.0, 0.0),
        ("31/08/2026", "DR: TERM DEPOSIT AUTO-SWEEP", "AXISTD-31082", 400000.0, 0.0),
        ("31/08/2026", "INW UPI: REIMBURSEMENT ADVANCE", "UPI-62439102", 0.0, 15000.0),
    ]

    opening_balance = 2840650.00
    txns, summary = _build_reconciled_txns(opening_balance, raw_txns)

    axis_logo = LogoFlowable(width=44, height=44, color=(0.58, 0.07, 0.28), text="AXIS")
    bank_hdr = """<b>AXIS BANK LIMITED</b><br/>
<font size="8">Magarpatta City Branch (01234)<br/>
Mega Center, Hadapsar, Pune - 411028 | IFSC: UTIB0001234</font>
"""
    stmt_meta = """<font size="12"><b>STATEMENT OF ACCOUNT</b></font><br/>
<font size="8">Statement Period: 01/08/2026 to 31/08/2026<br/>
Product: Corporate Current Account</font>
"""
    header_table = Table(
        [[axis_logo, Paragraph(bank_hdr, styles["TD"]), Paragraph(stmt_meta, styles["TD_Right"])]],
        colWidths=[50, 275, 210],
    )
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#97144D")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 6))

    acct_details = f"""<b>Customer Name:</b> {CODEIFY_TECH.name}<br/>
<b>Registered Address:</b> {CODEIFY_TECH.address}<br/>
<b>Account Number:</b> {CODEIFY_TECH.account_number} | <b>Customer ID:</b> 918237461<br/>
<b>PAN:</b> {CODEIFY_TECH.pan} | <b>GSTIN:</b> {CODEIFY_TECH.gstin}
"""
    summary_box = f"""<b>Opening Balance:</b> Rs. {format_inr(summary['opening_balance'], symbol='')}<br/>
<b>Total Deposits:</b> Rs. {format_inr(summary['total_credits'], symbol='')}<br/>
<b>Total Withdrawals:</b> Rs. {format_inr(summary['total_debits'], symbol='')}<br/>
<b>Closing Balance:</b> <b>Rs. {format_inr(summary['closing_balance'], symbol='')}</b>
"""
    cust_table = Table(
        [[Paragraph(acct_details, styles["TD"]), Paragraph(summary_box, styles["TD"])]],
        colWidths=[315, 220],
    )
    cust_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FDF2F4")),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#FBCFE8")),
    ]))
    story.append(cust_table)
    story.append(Spacer(1, 8))

    th_row = [
        Paragraph("<b>Tran Date</b>", styles["TH"]),
        Paragraph("<b>Particulars / Narration</b>", styles["TH"]),
        Paragraph("<b>Chq / Ref No</b>", styles["TH"]),
        Paragraph("<b>Debit (Rs.)</b>", styles["TH_Right"]),
        Paragraph("<b>Credit (Rs.)</b>", styles["TH_Right"]),
        Paragraph("<b>Balance (Rs.)</b>", styles["TH_Right"]),
    ]

    # Split into 14 txns on Page 1, 14 txns on Page 2
    p1_rows = [th_row]
    for t in txns[:14]:
        dr_str = format_inr(t["debit"], symbol="") if t["debit"] > 0 else "-"
        cr_str = format_inr(t["credit"], symbol="") if t["credit"] > 0 else "-"
        bal_str = format_inr(t["balance"], symbol="")
        p1_rows.append([
            Paragraph(t["date"], styles["TD"]),
            Paragraph(t["description"], styles["TD"]),
            Paragraph(t["ref_no"], styles["TD"]),
            Paragraph(dr_str, styles["TD_Right"]),
            Paragraph(cr_str, styles["TD_Right"]),
            Paragraph(bal_str, styles["TD_Right"]),
        ])

    table_p1 = Table(p1_rows, colWidths=[55, 185, 80, 70, 70, 75])
    table_p1.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F8E7EC")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#97144D")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#FCE7F3")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#F472B6")),
    ]))
    story.append(table_p1)
    story.append(Spacer(1, 8))
    story.append(Paragraph("<i>(Statement continues on page 2...)</i>", styles["FinePrint"]))

    # PAGE 2
    story.append(PageBreak())

    p2_hdr = Table(
        [[
            axis_logo,
            Paragraph(f"<b>AXIS BANK LIMITED</b> — Current A/C {CODEIFY_TECH.account_number} ({CODEIFY_TECH.name})", styles["TD"]),
            Paragraph("<b>PAGE 2 OF 2</b>", styles["TD_Right"]),
        ]],
        colWidths=[44, 385, 106],
    )
    p2_hdr.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#97144D")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(p2_hdr)
    story.append(Spacer(1, 8))

    p2_rows = [th_row]
    for t in txns[14:]:
        dr_str = format_inr(t["debit"], symbol="") if t["debit"] > 0 else "-"
        cr_str = format_inr(t["credit"], symbol="") if t["credit"] > 0 else "-"
        bal_str = format_inr(t["balance"], symbol="")
        p2_rows.append([
            Paragraph(t["date"], styles["TD"]),
            Paragraph(t["description"], styles["TD"]),
            Paragraph(t["ref_no"], styles["TD"]),
            Paragraph(dr_str, styles["TD_Right"]),
            Paragraph(cr_str, styles["TD_Right"]),
            Paragraph(bal_str, styles["TD_Right"]),
        ])

    table_p2 = Table(p2_rows, colWidths=[55, 185, 80, 70, 70, 75])
    table_p2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F8E7EC")),
        ("LINEBELOW", (0, 0), (-1, 0), 1, colors.HexColor("#97144D")),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#FCE7F3")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#F472B6")),
    ]))
    story.append(table_p2)
    story.append(Spacer(1, 10))

    reconciled_table = Table(
        [
            [
                "",
                Paragraph("<b>ACCOUNT SUMMARY TOTALS</b>", styles["TH_Right"]),
                Paragraph(f"<b>Rs. {format_inr(summary['total_debits'], symbol='')}</b>", styles["TH_Right"]),
                Paragraph(f"<b>Rs. {format_inr(summary['total_credits'], symbol='')}</b>", styles["TH_Right"]),
                Paragraph(f"<b>Rs. {format_inr(summary['closing_balance'], symbol='')}</b>", styles["TH_Right"]),
            ]
        ],
        colWidths=[120, 200, 70, 70, 75],
    )
    reconciled_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FCE7F3")),
        ("LINEABOVE", (0, 0), (-1, -1), 1, colors.HexColor("#97144D")),
        ("LINEBELOW", (0, 0), (-1, -1), 1, colors.HexColor("#97144D")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(reconciled_table)
    story.append(Spacer(1, 15))

    footer_disclaimer = """<font size="7" color="#64748B">
Registered Office: Axis Bank Limited, 'Trishul', 3rd Floor, Opposite Samartheshwar Temple, Law Garden, Ellisbridge, Ahmedabad - 380006.<br/>
This is a computer-generated bank statement and does not bear physical signature or stamp.
</font>"""
    story.append(Paragraph(footer_disclaimer, styles["FinePrint"]))

    doc.build(story, canvasmaker=NumberedCanvas)

    return {
        "bank_name": CODEIFY_TECH.bank_name,
        "account_number": CODEIFY_TECH.account_number,
        "account_holder": CODEIFY_TECH.name,
        "statement_period": "01/08/2026 to 31/08/2026",
        "opening_balance": summary["opening_balance"],
        "total_debits": summary["total_debits"],
        "total_credits": summary["total_credits"],
        "closing_balance": summary["closing_balance"],
        "transaction_count": summary["count"],
        "reconciled": True,
    }
