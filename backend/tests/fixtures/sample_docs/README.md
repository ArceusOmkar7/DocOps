# Sample Document Fixtures

Real-format Indian accounting document samples for testing the AI_Docs_orch extraction pipeline.
Each file is an OCR markdown representation — the format PaddlePaddle PP-StructureV3 produces
after processing a scanned PDF.

## Files

| File | Document Type | Entity | Period | Key Fields |
|---|---|---|---|---|
| [`gstr3b_unifab_jul2026.md`](gstr3b_unifab_jul2026.md) | `gst_return` | United Fabricators Pvt Ltd | Jul 2026 | GSTIN: 27AAPFU0939F1ZV, ARN: AA270726012345678 |
| [`form16_priya_anand_fy2526.md`](form16_priya_anand_fy2526.md) | `tds_form` | Priya Anand / Nexgen Software | FY 2025-26 | PAN: ABYPA3456H, TAN: BLRN12345F, Gross Salary ₹12L |
| [`bank_statement_hdfc_jul2026.md`](bank_statement_hdfc_jul2026.md) | `bank_statement` | Mehta & Associates CA Firm | Jul 2026 | A/c: 50200087654321, IFSC: HDFC0001234, 21 txns |
| [`invoice_varma_industries_jul2026.md`](invoice_varma_industries_jul2026.md) | `invoice` | Varma Industries Pvt Ltd | 08-Jul-2026 | GSTIN: 29AACCV4321M1Z8, Total ₹5,22,327 (IGST) |
| [`form26as_priya_anand_ay2627.md`](form26as_priya_anand_ay2627.md) | `tds_form` | Priya Anand | AY 2026-27 | PAN: ABYPA3456H, TDS ₹1,55,000 + ₹1,845 |

## Data Integrity Notes

- **Bank statement**: Running balances reconcile correctly (use `_review_bank_statement` to verify)
- **Invoice**: IGST-only (inter-state: Karnataka → Maharashtra), totals add up
- **GSTR-3B**: Net ITC = ITC Available − ITC Reversed (reconcilable)
- **Form 16 + Form 26AS**: Cross-referenced — Priya Anand's TDS from Nexgen appears in both;
  same BSR codes, challan numbers, and deposit dates

## Usage in Tests

```python
from pathlib import Path

FIXTURES = Path(__file__).parent / "sample_docs"

def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")

# Example
gstr3b_md = load_fixture("gstr3b_unifab_jul2026.md")
form16_md  = load_fixture("form16_priya_anand_fy2526.md")
bank_md    = load_fixture("bank_statement_hdfc_jul2026.md")
invoice_md = load_fixture("invoice_varma_industries_jul2026.md")
form26as_md = load_fixture("form26as_priya_anand_ay2627.md")
```

## Sources

Data formats grounded in:
- [GST Portal](https://www.gst.gov.in) — GSTR-3B table structure (6 tables)
- [TRACES Portal](https://www.tdscpc.gov.in) — Form 16 Part A/B column definitions
- [Income Tax Portal](https://incometaxindia.gov.in) — Form 26AS Part A–G structure
- [HDFC Bank NetBanking](https://netbanking.hdfcbank.com) — statement column format
- [Groww Tax Guides](https://groww.in/p/tax) — field-level reference
- [BankBazaar](https://www.bankbazaar.com/tax/) — Form 16 Part B breakdown
