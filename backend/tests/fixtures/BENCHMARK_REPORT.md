# Live Pipeline Benchmark & Accuracy Report

**Run Date:** 2026-09-09 16:33 UTC  
**Model:** `openai/gpt-oss-120b` via Groq  
**OCR Engine:** PaddleOCR `PP-StructureV3` (CUDA GPU)  
**Total Documents Evaluated:** 22

---

## 1. Executive Summary & Quantifiable Metrics

| Metric | Result | Benchmark Target | Status |
|---|:---:|:---:|:---:|
| **Document Classification Accuracy** | **95.5%** | >= 95% | ✅ PASS |
| **Key Field Extraction Accuracy** | **82.7%** | >= 85% | ⚠️ REVIEW |
| **Human Review Trigger Rate** | **31.8%** | Auto-flagged | ℹ️ INFO |
| **Avg OCR Latency** | **3.68s** | < 5.0s | ✅ FAST |
| **Avg LLM Extraction Latency** | **18.21s** | < 4.0s | ✅ FAST |

---

## 2. Robustness by Document Condition (Ablation Analysis)

| Category | Count | Classification Acc | Field Acc | Avg OCR Conf | Review Flagged |
|---|:---:|:---:|:---:|:---:|:---:|
| **`clean`** | 11 | 100.0% | 93.9% | 0.972 | 2/11 |
| **`scanned_good`** | 5 | 100.0% | 87.4% | 0.978 | 1/5 |
| **`scanned_poor`** | 4 | 75.0% | 45.9% | 0.84 | 2/4 |
| **`edge_cases`** | 2 | 100.0% | 0.0% | 0.492 | 2/2 |

---

## 3. Detailed Per-Document Results

| Filename | Category | Expected | Classified | Field Acc | OCR Conf | Total Time | Review Needed |
|---|---|---|---|:---:|:---:|:---:|:---:|
| `clean/invoice_rajput_rs0234.pdf` | `clean` | `invoice` | `invoice` | 83.3% | 0.9769 | 64.71s | No ✅ |
| `clean/invoice_rajput_rs0235.pdf` | `clean` | `invoice` | `invoice` | 66.7% | 0.9794 | 9.12s | Yes ⚠️ |
| `clean/invoice_codeify_ct0189.pdf` | `clean` | `invoice` | `invoice` | 83.3% | 0.9711 | 10.0s | No ✅ |
| `clean/bank_stmt_rajput_aug2026.pdf` | `clean` | `bank_statement` | `bank_statement` | 100.0% | 0.9629 | 24.71s | No ✅ |
| `clean/bank_stmt_codeify_aug2026.pdf` | `clean` | `bank_statement` | `bank_statement` | 99.3% | 0.9621 | 13.9s | Yes ✅ |
| `clean/gstr3b_rajput_aug2026.pdf` | `clean` | `gst_return` | `gst_return` | 100.0% | 0.9746 | 8.06s | No ✅ |
| `clean/gstr3b_codeify_aug2026.pdf` | `clean` | `gst_return` | `gst_return` | 100.0% | 0.967 | 7.44s | No ✅ |
| `clean/form16_arjun_fy2526.pdf` | `clean` | `tds_form` | `tds_form` | 100.0% | 0.9801 | 43.66s | No ✅ |
| `clean/form26as_arjun_ay2627.pdf` | `clean` | `tds_form` | `tds_form` | 100.0% | 0.9653 | 6.74s | No ✅ |
| `clean/lic_receipt_arjun_80c.pdf` | `clean` | `investment_proof` | `investment_proof` | 100.0% | 0.972 | 6.98s | No ✅ |
| `clean/ppf_statement_arjun_80c.pdf` | `clean` | `investment_proof` | `investment_proof` | 100.0% | 0.9807 | 5.49s | No ✅ |
| `scanned_good/invoice_rajput_rs0234_scan.pdf` | `scanned_good` | `invoice` | `invoice` | 66.7% | 0.9746 | 7.42s | No ⚠️ |
| `scanned_good/bank_stmt_rajput_scan.pdf` | `scanned_good` | `bank_statement` | `bank_statement` | 70.3% | 0.9891 | 161.77s | Yes ⚠️ |
| `scanned_good/gstr3b_rajput_scan.pdf` | `scanned_good` | `gst_return` | `gst_return` | 100.0% | 0.9743 | 52.37s | No ✅ |
| `scanned_good/form16_arjun_scan.pdf` | `scanned_good` | `tds_form` | `tds_form` | 100.0% | 0.9812 | 8.3s | No ✅ |
| `scanned_good/lic_receipt_arjun_scan.pdf` | `scanned_good` | `investment_proof` | `investment_proof` | 100.0% | 0.9684 | 51.48s | No ✅ |
| `scanned_poor/invoice_codeify_ct0189_mobile.pdf` | `scanned_poor` | `invoice` | `unknown` | 0.0% | 0.5454 | 5.66s | Yes ⚠️ |
| `scanned_poor/bank_stmt_codeify_mobile.pdf` | `scanned_poor` | `bank_statement` | `bank_statement` | 50.0% | 0.9818 | 9.17s | Yes ⚠️ |
| `scanned_poor/form26as_arjun_mobile.pdf` | `scanned_poor` | `tds_form` | `tds_form` | 66.7% | 0.9489 | 6.46s | No ⚠️ |
| `scanned_poor/ppf_statement_arjun_mobile.pdf` | `scanned_poor` | `investment_proof` | `investment_proof` | 66.7% | 0.8834 | 15.09s | No ⚠️ |
| `edge_cases/payslip_arjun_aug2026.pdf` | `edge_cases` | `unknown` | `unknown` | 100.0% | 0.9833 | 3.91s | Yes ✅ |
| `edge_cases/blank_page.pdf` | `edge_cases` | `unknown` | `unknown` | 100.0% | N/A | 3.28s | Yes ✅ |

---

## 4. Field-Level Failure Analysis

### `clean/invoice_rajput_rs0234.pdf`
- **seller_gstin**: Expected `24AABCR5678Q1ZP`, got `None` (mismatch)

### `clean/invoice_rajput_rs0235.pdf`
- **seller_gstin**: Expected `24AABCR5678Q1ZP`, got `None` (mismatch)
- **igst**: Expected `36108.0`, got `None` (mismatch)

### `clean/invoice_codeify_ct0189.pdf`
- **seller_gstin**: Expected `27AAGFC4321N1ZT`, got `None` (mismatch)

### `scanned_good/invoice_rajput_rs0234_scan.pdf`
- **invoice_number**: Expected `RS/2026-27/0234`, got `` (mismatch)
- **seller_gstin**: Expected `24AABCR5678Q1ZP`, got `None` (mismatch)

### `scanned_good/bank_stmt_rajput_scan.pdf`
- **bank_name**: Expected `State Bank of India`, got `` (mismatch)
- **transaction_count**: Expected `35`, got `18` (18/35 txns)

### `scanned_poor/invoice_codeify_ct0189_mobile.pdf`
- **invoice_payload**: Expected `{'invoice_number': 'CT/2026-27/0189', 'date': '2026-08-22', 'seller_name': 'Codeify Technologies LLP', 'seller_gstin': '27AAGFC4321N1ZT', 'buyer_name': 'Apex Global Logistics Solutions Private Limited', 'buyer_gstin': '29AAACA1234F1ZU', 'subtotal': 750000.0, 'cgst': 0.0, 'sgst': 0.0, 'igst': 135000.0, 'total': 885000.0, 'tax_type': 'inter_state'}`, got `None` (Missing invoice payload)

### `scanned_poor/bank_stmt_codeify_mobile.pdf`
- **account_number**: Expected `9876501234`, got `` (mismatch)
- **opening_balance**: Expected `2840650.0`, got `3215692.0` (mismatch)
- **transaction_count**: Expected `28`, got `14` (14/28 txns)

### `scanned_poor/form26as_arjun_mobile.pdf`
- **pan**: Expected `AKQPK7890G`, got `` (mismatch)

### `scanned_poor/ppf_statement_arjun_mobile.pdf`
- **pan**: Expected `AKQPK7890G`, got `` (mismatch)
