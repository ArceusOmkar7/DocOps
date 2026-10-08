# Patra — Master Phase-Wise Implementation Plan

> **Document Version:** 1.0.0  
> **Status:** Active Engineering Roadmap  
> **System Scope:** Agentic Document Orchestration & Workflow Intelligence Platform for Accounting & CA Firms  

---

## 1. Executive Summary & Target Vision

Today, accounting and Chartered Accountancy (CA) firms lose a substantial percentage of billable hours on pre-accounting manual overhead:
1. Downloading unorganized attachments from Email, WhatsApp, and Google Drive.
2. Manually sorting, classifying, and renaming files into client folders.
3. Cross-checking received files against mental or static checklists (Audit, Income Tax, GST, TDS).
4. Repeatedly writing kickoff emails and chasing clients over phone/email for missing items.
5. Manually validating mathematical totals, GSTINs, PANs, and redacting confidential client PII for compliance with data privacy regulations (e.g., India's DPDP Act 2023).

**Patra** automates this entire pre-accounting operational layer. Instead of accountants managing documents, documents move themselves through automated ingestion, local layout-aware OCR, classification, entity extraction, mathematical/statutory validation, dynamic workflow tracking, and proactive follow-up recommendations. The human accountant acts exclusively as the final reviewer and decision-maker (*Human-in-the-Loop*).

---

## 2. Current State vs. Target State Baseline

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                          CURRENT STATE (v0.2.0)                                         │
│                                                                                                         │
│  [Upload UI / API] ──▶ [PP-StructureV3 GPU OCR] ──▶ [Decoupled LLM] ──▶ [Postgres Multi-Tenant DB]     │
│  • Single Ingest (Web)  • Text & Layout BBoxes       • Classify Doc Type • Organizations / Clients      │
│  • React 19 Frontend    • HTML Tables in Markdown    • Invoice Extractor • Workflows & Requirements     │
│  • Inspection Drawer    • CUDA 12.6 Acceleration     • 3-Try Retry Loop  • Documents & Junction Links   │
│  • Seeded Demo Data     • Disk Persistence (/data)   • Math Cross-Checks • 32 Backend Unit Tests Passed │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                     │
                                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       TARGET VISION (Final Product)                                     │
│                                                                                                         │
│  [Multi-Channel Intake] ──▶ [Privacy / Redaction] ──▶ [OCR & Multi-Doc] ──▶ [Validation & Checks]       │
│  • Email IMAP / Gmail OAuth • Local DPDP Masking     • Invoices & Receipts • GSTIN Luhn / PAN Validation │
│  • WhatsApp Cloud API       • PAN / Aadhaar Masking  • Bank Statements     • Duplicate Hash Detection   │
│  • Google Drive / OneDrive  • Zero Data Retention    • TDS / GST Returns   • Multi-Person Segregation   │
│                                                      • Investment Proofs                                │
│                                                                                                         │
│  [Workflow Engine] ───────▶ [Missing Doc Tracker] ──▶ [Follow-Up Engine] ─▶ [AI Review Copilot]        │
│  • Audit Checklists         • Real-time Requirements • Kickoff Email Gen   • "What is missing for audit"│
│  • ITR Adaptive Rules       • Delta Calculation      • Phone vs Email Rec  • Natural Language Search    │
│  • GST/TDS Cycles           • Auto State Progression • Client Portal Upload• Timeline Audit Log         │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Component Comparison

| Component | Current State (Built) | Target State (To Build) | Gap / Delta |
|---|---|---|---|
| **Intake Channels** | Web UI drag-and-drop & `POST /ocr/extract` API. | Multi-channel: Email (IMAP/Gmail/Outlook OAuth), WhatsApp Cloud API, Drive/OneDrive sync, Web Portal. | Ingestion workers, mailbox polling, webhook handlers, attachment decoders. |
| **OCR & Layout** | GPU `PP-StructureV3` (CUDA 12.6), tables to HTML, markdown reading order, disk caching. | Full multi-page support, complex bank statement layout recognition, challan & scanned form OCR. | Specialized tabular/transaction post-processors, OCR page chunking for large files. |
| **Doc Classification** | LLM `ClassificationService` classifying into 6 types (`invoice`, `receipt`, `bank_statement`, `purchase_order`, `gst_return`, `unknown`). | Classification + Multi-Person Taxpayer Segregation (splitting joint family ITR bundles by PAN). | Multi-taxpayer splitting logic, client/FY identification from OCR content. |
| **Data Extraction** | `Invoice` business schema with seller/buyer GSTINs, items, CGST/SGST/IGST breakdown. | Typed extractors for Bank Statements, GST Returns (GSTR-1, 3B, 2B), TDS Forms (16, 16A, 26AS, AIS/TIS), Investment Proofs (80C, 80D). | Dedicated Pydantic schemas, extractor prompts, JSON validation routines for each document family. |
| **Validation Engine** | Line totals vs subtotal, qty*unit vs line total, subtotal+tax vs total. | Statutory GSTIN Luhn checksum, PAN structure, duplicate upload hash/invoice ID, FY mismatch, date bounds, missing mandatory pages. | Algorithmic statutory validators, SHA-256 deduplication service, rule registry. |
| **Privacy & Security** | Direct forwarding to LLM provider (OpenRouter / Groq / OpenAI). | Built-in DPDP Act PII redaction layer (Aadhaar 8-digit masking, PAN/bank redaction option, local LLM option). | Regex/NER PII scrubber before LLM dispatch, token masking and unmasking engine. |
| **Workflow Engine** | Static models for `Workflow`, `WorkflowDocumentRequirement`, `WorkflowDocument` with CRUD endpoints. | Dynamic workflow templates with adaptive checklists (Audit, ITR, GST, Bookkeeping), auto-requirement matching on upload. | Auto-association logic linking parsed docs to requirements, adaptive rule generator from previous FY filings. |
| **Requirement Tracking** | Static checklist counts. | Dynamic Received vs Missing delta computation, workflow progression trigger (`collecting` -> `ready_for_review`). | Delta engine, missing document dashboard, blocked workflow alerts. |
| **Client Follow-ups** | None. | Kickoff email generator, Reminder engine recommending Email vs WhatsApp vs Phone Call based on urgency & client relationship. | Email template engine, follow-up recommendation heuristics, one-click copy/send action. |
| **Review & Copilot** | Document inspection drawer (Overview, Preview, Markdown, JSON, History). | AI Review Assistant / Copilot ("What's missing for ABC Pvt Ltd?", "Show GST mismatches"), Full-Text search, Timeline Audit log. | RAG / Text-to-SQL copilot service, Elasticsearch / pg_trgm full-text search, event audit store. |
| **Auth & Client Portal** | Single tenant / mock auth context. | Multi-tenant RBAC (Partner, Senior CA, Staff, Client) + Secure Client-facing upload portal link. | JWT authentication middleware, passwordless magic links for client uploads. |

---

## 3. Master Phase-Wise Implementation Roadmap

```
  2026 Q3               2026 Q4               2027 Q1               2027 Q2
┌─────────────────────┬─────────────────────┬─────────────────────┬─────────────────────┐
│      PHASE 1        │      PHASE 2        │      PHASE 3        │      PHASE 4        │
│ Multi-Doc Schemas & │ Validation Engine & │ Multi-Channel Intake│ Workflow Automation │
│ Family Segregation  │ DPDP Privacy Redact │ Email / WhatsApp    │ & Reminder Engine   │
├─────────────────────┴─────────────────────┴─────────────────────┴─────────────────────┤
│                                     PHASE 5                                           │
│                     AI Copilot, Unified Search & Timeline Audit                       │
├───────────────────────────────────────────────────────────────────────────────────────┤
│                                     PHASE 6                                           │
│                    Client Portal & Multi-Tenant RBAC                                  │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

### PHASE 1: Document Intelligence & Multi-Document Family Schemas

#### Goal
Expand data extraction beyond Invoices to cover the full spectrum of Indian CA firm documents (Bank Statements, GST Returns, TDS Forms, Investment Proofs) and introduce multi-taxpayer family bundle segregation.

#### 1.1 New Typed Business Schemas (Pydantic & DB JSONB)
Implement structured schemas in `backend/app/schemas/extraction.py`:
1. **`BankStatement`**:
   - `account_number`, `bank_name`, `ifsc_code`, `account_holder`, `period_start`, `period_end`, `opening_balance`, `closing_balance`.
   - `transactions`: list of `{"date", "description", "cheque_ref_no", "debit", "credit", "balance", "category"}`.
2. **`GSTReturn`** (GSTR-1, GSTR-3B, GSTR-2B):
   - `gstin`, `return_period` (MM-YYYY), `filing_date`, `arn_number`.
   - `taxable_turnover`, `outward_tax_summary` (IGST, CGST, SGST, Cess).
   - `itc_available` (Input Tax Credit breakdown), `itc_reversed`, `net_itc`.
3. **`TDSForm`** (Form 16 / 16A / 26AS / AIS / TIS):
   - `pan`, `tan_of_deductor`, `deductor_name`, `assessment_year`, `financial_year`.
   - `gross_salary` / `total_amount_credited`, `total_tds_deducted`, `total_tds_deposited`, `section_codes` (e.g. 194C, 194J, 192).
4. **`InvestmentProof`** (Chapter VI-A):
   - `pan`, `taxpayer_name`, `policy_account_no`, `institution_name`, `section` (`80C`, `80D`, `80CCD`, `24b`), `amount_paid`, `date_of_payment`.

#### 1.2 Extractor Registry Expansion
Update `ExtractionService.EXTRACTORS` in `backend/app/services/extraction.py`:
- `_extract_bank_statement(markdown, document_id)`
- `_extract_gst_return(markdown, document_id)`
- `_extract_tds_form(markdown, document_id)`
- `_extract_investment_proof(markdown, document_id)`

#### 1.3 Multi-Taxpayer Family Bundle Segregation Engine
- **The Problem**: In ITR season, a client emails a single PDF containing husband's Form 16, wife's LIC receipt, and father's pension statement.
- **Implementation**:
  - Add `services/segregation.py`: Splits multi-page OCR output into logical document segments by detecting changing PANs, employer TANs, and taxpayer names across pages.
  - Generates sub-documents linked to the respective individual client profiles in the family group.

#### Phase 1 Deliverables & Verification
- Unit & integration tests for all 4 new extraction schemas with fake LLM clients and sample test data.
- Frontend Document Drawer updated with custom schema viewers (e.g., Transaction table for Bank Statements, ITC grid for GST Returns).

---

### PHASE 2: Comprehensive Validation Engine & DPDP Act Privacy Layer

#### Goal
Prevent bad, corrupt, or duplicate documents from reaching accountants, and ensure strict compliance with India's Digital Personal Data Protection (DPDP) Act 2023.

```
Incoming Document ──▶ [SHA-256 Hash Check] ──▶ [DPDP PII Redaction] ──▶ [LLM Extraction] ──▶ [Statutory Validation Engine]
                        (Reject Duplicate)      (Mask Aadhaar/PAN)       (Zero Leakage)       • GSTIN Luhn Mod-36
                                                                                              • PAN 4th Char Check
                                                                                              • FY / Date Cross-Check
                                                                                              • Tax Math Reconciliation
```

#### 2.1 Statutory & Technical Validation Engine (`backend/app/services/validation/`)
1. **GSTIN Luhn Mod-36 Checksum Validator**:
   - Verify 15-character GSTIN structure: `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$`.
   - Calculate and verify the modulo-36 check digit algorithm.
2. **PAN Structure & Entity Matcher**:
   - Validate 10-character PAN regex: `^[A-Z]{3}[ABCFGHJLPT]{1}[A-Z]{1}[0-9]{4}[A-Z]{1}$`.
   - Verify 4th character matches client entity type (`P` = Individual, `C` = Company, `F` = Partnership Firm, `H` = HUF, `T` = Trust).
3. **Duplicate Detection Layer**:
   - Compute SHA-256 content hash on raw upload.
   - Cross-check `(seller_tax_id, invoice_number, invoice_date)` against existing database records. Flag immediate duplicates.
4. **Financial Year & Date Bounds Validation**:
   - Detect invoices or challans with dates falling outside the workflow's active financial period (e.g. FY 2024-25 vs invoice date in 2022).
5. **Quality & Completeness Checks**:
   - Detect blank pages, OCR confidence scores $< 70\%$, unreadable scans, and missing mandatory summary pages.

#### 2.2 DPDP Act Privacy & Redaction Engine (`backend/app/services/privacy/`)
1. **Aadhaar Masking**:
   - Comply with UIDAI & DPDP guidelines: Mask the first 8 digits of any 12-digit Aadhaar number (`XXXX-XXXX-1234`).
2. **Confidential Entity Scrubber**:
   - Regex + NER engine that identifies and masks bank account numbers, director personal contact details, and sensitive identifiers before dispatching markdown to external LLMs.
3. **Multi-Provider AI & On-Premise Support**:
   - Allow configuration of `LLM_PROVIDER`:
     - `openai` / `groq` / `openrouter` (External cloud with PII redaction active).
     - `azure_openai` (Enterprise Zero-Data-Retention tier).
     - `ollama` / `vllm` / `local_server` (100% on-premise, zero internet access for ultra-sensitive CA firms).

#### Phase 2 Deliverables & Verification
- Test suite verifying GSTIN/PAN validator edge cases and Aadhaar masking.
- Validation warning banners rendered in the frontend Document Drawer with human-in-the-loop override buttons.

---

### PHASE 3: Multi-Channel Document Intake & Ingestion Pipeline

#### Goal
Automate the intake of documents from Email, WhatsApp, and Cloud Storage, removing the need for manual downloading and file saving.

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Email Inbox   │       │  WhatsApp API   │       │  Google Drive   │
│  (IMAP / OAuth) │       │   (Cloud API)   │       │  (Folder Watch) │
└────────┬────────┘       └────────┬────────┘       └────────┬────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   │
                                   ▼
                   ┌───────────────────────────────┐
                   │  Ingestion Worker & Queue     │
                   │  • Attachment Extraction      │
                   │  • Sender-to-Client Resolver  │
                   │  • SHA-256 Deduplication      │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                   [ Automated Processing Pipeline ]
                   (OCR ──▶ Classify ──▶ Extract ──▶ Assign)
```

#### 3.1 Email Intake Service (`backend/app/services/intake/email_service.py`)
- **Protocols**:
  - IMAP with SSL (generic for custom firm domains, Zoho, cPanel).
  - OAuth2 integrations for Google Workspace (Gmail API) and Microsoft 365 (Graph API).
- **Functionality**:
  - Periodically poll monitored inboxes (or receive webhooks).
  - Extract PDF, PNG, JPG, TIFF, ZIP attachments.
  - Unpack password-protected PDFs (using client PAN or DOB stored securely in client profile).
  - Map email sender address to client profile in database.

#### 3.2 WhatsApp Business Cloud API Integration (`backend/app/services/intake/whatsapp_service.py`)
- Webhook endpoint `POST /api/v1/intake/whatsapp/webhook` to receive incoming media.
- Download media files using Meta Cloud API tokens.
- Map sender phone number to client CRM record.
- Send instant automated reply: *"Received 3 documents. Ingesting into your FY 2025-26 GST Filing workflow."*

#### 3.3 Cloud Drive Sync (`backend/app/services/intake/drive_service.py`)
- Google Drive & OneDrive folder watcher for shared client folders.
- Automatically ingest new files uploaded by clients into their dedicated drive folders.

#### 3.4 Auto-Client & Auto-Workflow Resolution Engine
- Inspects sender metadata (email/phone) and extracted document content (GSTIN/PAN).
- Matches document to the active workflow period (e.g. Inward Tax Invoice dated 2026-08 $\rightarrow$ August 2026 GSTR-3B Workflow).

#### Phase 3 Deliverables & Verification
- Live intake test suite simulating IMAP and WhatsApp webhook payloads.
- Ingestion feed widget on the Dashboard showing real-time multi-channel arrivals.

---

### PHASE 4: Workflow Orchestration, Missing Document Detection & Follow-Up Engine

#### Goal
Implement the core business engine: tracking what has been received vs. what is missing for every active workflow, generating kickoff requirement emails, and calculating smart reminder recommendations.

```
Workflow Template (e.g. Audit)
       │
       ▼
[ Active Workflow Instance ] ◀── Matching Ingested Documents
       │
       ▼
[ Delta Calculation Engine ] ──▶ Received: [ Trial Balance ✓, GST Return ✓ ]
       │                         Missing:  [ TDS Return ❌, Stock Cert ❌ ]
       ▼
[ Follow-Up Engine ] ──────────▶ 1. Kickoff Email Draft Generator
                                 2. Recommendation Engine (Email vs Phone Call)
                                 3. One-Click Client Dispatch
```

#### 4.1 Specialized Accounting Workflow Templates (`backend/app/models/workflow.py`)
1. **Statutory & Tax Audit Workflow**:
   - Mandatory: *Trial Balance, GSTR-9/9C, Form 26AS, Bank Statements (All Accounts), PF/ESI Challans, Fixed Asset Invoices, Cash Verification Certificate, Stock Valuation Certificate, Director Balance Confirmations*.
2. **Income Tax Filing (ITR-1 to ITR-6)**:
   - Adaptive Checklist: Inferred from client entity type + previous year's filing (e.g., if client claimed 80D or home loan in PY, auto-add requirement for current FY).
   - Mandatory: *Form 16 / 16A, AIS / TIS, Capital Gains Statements, Bank Interest Certificates, Chapter VI-A Investment Proofs*.
3. **Monthly GST Compliance (GSTR-1 & 3B)**:
   - Mandatory: *Sales Register, Purchase Register, Export Invoices with Shipping Bills, E-Way Bill Register, GSTR-2B Portal Download*.
4. **Quarterly TDS Compliance (Form 24Q / 26Q / 27Q)**:
   - Mandatory: *Salary Deductions Register, Vendor Payments Subject to TDS (194C/J/I/H), ITNS-281 Tax Deposit Challans*.

#### 4.2 Requirement Tracking & State Machine
- **Live Delta Computation**: Recomputes fulfilled vs missing items whenever a document is attached or validated.
- **Workflow State Machine**:
  - `collecting_documents`: Waiting on client uploads.
  - `ready_for_review`: $100\%$ of mandatory requirements fulfilled, no critical validation errors.
  - `in_review`: Assigned accountant actively verifying calculations.
  - `ready_for_filing`: Approved by Senior CA / Partner.
  - `completed`: Return filed / Audit signed.
  - `blocked`: Critical validation failure (e.g., severe GSTIN mismatch or invalid ledger).

#### 4.3 AI Kickoff Email & Follow-Up Generator (`backend/app/services/followup/`)
1. **Kickoff Email Generator**:
   - Compiles a personalized email listing all required documents formatted with clear checkboxes.
2. **Smart Follow-Up Recommendation Engine**:
   - Heuristic rules:
     - Days to statutory filing deadline $> 15$ days $\rightarrow$ *Send Gentle Email Reminder*.
     - Days to deadline $\le 7$ days $\rightarrow$ *Send WhatsApp Message + High-Priority Email*.
     - Days to deadline $\le 3$ days $\rightarrow$ *Recommend Immediate Phone Call* (with phone script).
   - Considers client responsiveness history and relationship tier.

#### Phase 4 Deliverables & Verification
- End-to-end integration test creating a workflow, attaching documents, and verifying state transitions.
- Frontend Workflow Inspector modal rendering the Received/Missing checklist and the Follow-up Action card.

---

### PHASE 5: CA Review Copilot, Unified Search & Timeline Audit Trail

#### Goal
Empower accountants to query their entire practice database in natural language, search across any extracted entity, and maintain an immutable audit trail for every document action.

```
                  ┌──────────────────────────────────────────────┐
                  │          Natural Language Query              │
                  │ "What documents are missing for ABC Audit?"  │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │               AI Copilot Engine              │
                  │  • Schema-Aware SQL & RAG Query Planner      │
                  │  • Document & Workflow Entity Indexer        │
                  │  • Contextual Response & Action Generator    │
                  └──────────────────────┬───────────────────────┘
                                         │
                                         ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ Response:                                                                        │
│ "ABC Pvt Ltd Audit is at 75% completion. Missing: Stock Certificate & Cash Cert.  │
│  Recommendation: Client prefers phone calls. [Copy Phone Script] [Send Email]"  │
└──────────────────────────────────────────────────────────────────────────────────┘
```

#### 5.1 AI Review Assistant & Copilot (`backend/app/services/copilot/`)
- Natural Language Interface for accountants to query practice intelligence:
  - *"Which clients have not submitted bank statements for August?"*
  - *"Show all purchase invoices exceeding ₹1,00,000 where GST was not claimed."*
  - *"Summarize all tax-deductible expenses extracted for XYZ Industries."*
- Implemented via schema-aware Text-to-SQL + Vector RAG over extracted entity metadata.

#### 5.2 Unified Search & Discovery (`backend/app/services/search/`)
- Multi-faceted full-text search across:
  - Extracted invoice line items and descriptions.
  - Vendor and buyer GSTINs / PANs.
  - Financial years, assessment years, and document types.
  - Workflow status and client names.

#### 5.3 Immutable Timeline & Audit Trail (`backend/app/models/audit_event.py`)
- Log every single event with precise timestamps and user attribution:
  - `DOC_INGESTED` (via Email/WhatsApp/Web).
  - `DOC_CLASSIFIED` & `DOC_EXTRACTED`.
  - `VALIDATION_FLAG_RAISED` & `VALIDATION_OVERRIDDEN`.
  - `REMINDER_DISPATCHED`.
  - `WORKFLOW_STATUS_CHANGED`.

#### Phase 5 Deliverables & Verification
- Copilot drawer in frontend top bar accessible via `⌘K` or dedicated assistant tab.
- Search page with instantaneous faceted filtering.

---

### PHASE 6: Client Portal & Multi-Tenant RBAC

#### Goal
Deliver client-facing self-service upload links and secure role-based access control across all firm roles.

#### 6.1 Role-Based Access Control (RBAC) & Authentication
- **Roles**:
  - `Partner / Admin`: Full practice access, audit sign-offs, system settings.
  - `Senior CA`: Workflow reviews, approvals, client assignments.
  - `Articled Assistant / Staff`: Document uploads, OCR inspection, validation reviews.
  - `Client User`: Access strictly limited to their own organization's upload portal.
- **Security**: JWT authentication, secure refresh tokens, passwordless magic links for client uploads.

#### 6.2 Dedicated Client-Facing Upload Portal
- Lightweight mobile-first web app:
  - Clean view showing: *"Here is what your CA needs for August 2026 GST Filing"*.
  - Upload boxes per checklist item.
  - Instant client-side validation feedback (*"Uploaded file is an Invoice for July, but August is required"*).


---

## 4. Complete Database Architecture & ERD

```
┌───────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       RELATIONAL DATABASE SCHEMA                                      │
├───────────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                       │
│  ┌───────────────────────┐       ┌───────────────────────┐       ┌───────────────────────┐            │
│  │     organizations     │───────│        clients        │───────│     client_members    │ (Family/   │
│  │───────────────────────│  1:N  │───────────────────────│  1:N  │───────────────────────│  Groups)   │
│  │ id (UUID, PK)         │       │ id (UUID, PK)         │       │ id (UUID, PK)         │            │
│  │ name (VARCHAR)        │       │ organization_id (FK)  │       │ client_id (FK)        │            │
│  │ slug (VARCHAR, UQ)    │       │ name (VARCHAR)        │       │ name, pan, relation   │            │
│  │ plan (VARCHAR)        │       │ tax_id / GSTIN        │       │ email, phone          │            │
│  │ created_at (TIMESTAMPT│       │ email, phone          │       └───────────────────────┘            │
│  └───────────────────────┘       │ status (ENUM)         │                   │                        │
│             │                    └───────────┬───────────┘                   │ 1:N                    │
│             │ 1:N                            │ 1:N                           ▼                        │
│             ▼                                ▼                   ┌───────────────────────┐            │
│  ┌───────────────────────┐       ┌───────────────────────┐       │       documents       │            │
│  │         users         │       │       workflows       │       │───────────────────────│            │
│  │───────────────────────│       │───────────────────────│       │ id (UUID, PK)         │            │
│  │ id (UUID, PK)         │       │ id (UUID, PK)         │       │ organization_id (FK)  │            │
│  │ organization_id (FK)  │       │ organization_id (FK)  │       │ client_id (FK)        │            │
│  │ email, name           │       │ client_id (FK)        │       │ client_member_id (FK) │ (Nullable) │
│  │ role (ENUM)           │       │ name (VARCHAR)        │       │ source_filename       │            │
│  │ hashed_password       │       │ workflow_type (ENUM)  │       │ ocr_result_id (UQ)    │            │
│  └───────────────────────┘       │ period_start, end     │       │ document_type (ENUM)  │            │
│                                  │ status (ENUM)         │       │ status (ENUM)         │            │
│                                  │ created_at, closed_at │       │ ocr_confidence (FLOAT)│            │
│                                  └───────────┬───────────┘       │ needs_human_review    │            │
│                                              │ 1:N               │ review_reason (TEXT)  │            │
│                                              ▼                   │ extracted_data (JSONB)│            │
│                                  ┌───────────────────────┐       │ metadata (JSONB)      │            │
│                                  │ workflow_requirements │       │ content_hash (SHA256) │            │
│                                  │───────────────────────│       │ uploaded_at           │            │
│                                  │ id (UUID, PK)         │       └───────────┬───────────┘            │
│                                  │ workflow_id (FK)      │                   │                        │
│                                  │ document_type (ENUM)  │                   │ 1:N                    │
│                                  │ label (VARCHAR)       │                   ▼                        │
│                                  │ required_count (INT)  │       ┌───────────────────────┐            │
│                                  │ notes (TEXT)          │       │  workflow_documents   │ (Junction) │
│                                  └───────────┬───────────┘       │───────────────────────│            │
│                                              │ 1:N               │ id (UUID, PK)         │            │
│                                              │                   │ workflow_id (FK)      │            │
│                                              └──────────────────▶│ document_id (FK)      │            │
│                                                                  │ requirement_id (FK)   │            │
│                                                                  │ added_at              │            │
│                                                                  └───────────────────────┘            │
└───────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Technical Stack & Architecture Standards

- **Backend Language & Runtime**: Python 3.12 (managed via `uv`).
- **Web Framework**: FastAPI 0.141+ with async endpoints and async lifespan management.
- **Database Layer**: PostgreSQL 16+ via SQLAlchemy 2.0 (Async) and `asyncpg` driver; Alembic for migrations.
- **Local OCR & Vision**: PaddlePaddle-GPU 3.3.1 (CUDA 12.6, RTX 4060) with `PP-StructureV3` document layout pipeline, table structure recognition, and reading order reconstruction.
- **LLM Client & Orchestration**: Lightweight `httpx` client targeting OpenAI-compatible endpoints (`/chat/completions`) with strict JSON schema validation and error-feedback self-correction retry loops.
- **Frontend Stack**: React 19 SPA, TypeScript 5.7+, Vite 6, TanStack Query v5 (React Query), React Router v7, Lucide React, Bun package manager.
- **Styling Architecture**: Custom responsive CSS Token Design System (CSS Variables for light/dark theme, emerald/slate palette, glassmorphism cards, zero Tailwind bloat).

---

## 6. Execution Order & Milestone Deliverables

| Milestone | Phase | Target Focus | Key Deliverable | Success Criteria |
|---|---|---|---|---|
| **M1** | Phase 1 | Multi-Document Extraction | Bank Statement, GST, TDS, Investment Schemas + Family Segregation | Parse real bank statements and Form 16s into structured DB records. |
| **M2** | Phase 2 | Validation & Privacy | GSTIN Luhn, PAN 4th Char, Duplicate SHA-256, DPDP Aadhaar Masking | Zero PII leaks to external LLMs; 100% duplicate upload detection. |
| **M3** | Phase 3 | Multi-Channel Intake | Email IMAP/OAuth & WhatsApp Webhook Ingestion Pipeline | Client emails an attachment $\rightarrow$ automatically ingested, OCR'd, and matched. |
| **M4** | Phase 4 | Workflow & Follow-Up Engine | Adaptive Checklists, Received/Missing Tracker, Kickoff Email Generator | Accountant opens workflow and immediately sees exact missing items + 1-click email draft. |
| **M5** | Phase 5 | AI Copilot & Unified Search | Natural Language Copilot + Global Full-Text Search + Audit Log | Accountant asks "What's missing for ABC Audit?" and receives instant grounded answer. |
| **M6** | Phase 6 | Client Portal & RBAC | Dedicated Client Upload UI + JWT Multi-Tenant RBAC | Client uploads missing docs directly; accountants log in with role-scoped access. |

---

## 7. Immediate Next Steps (Starting Phase 1)

1. **Create Pydantic Schemas**: Add `BankStatement`, `GSTReturn`, `TDSForm`, `InvestmentProof` models to `backend/app/schemas/extraction.py`.
2. **Implement Extractor Methods**: Register `_extract_bank_statement`, `_extract_gst_return`, `_extract_tds_form`, `_extract_investment_proof` in `ExtractionService`.
3. **Add Algorithmic Validation**: Create `backend/app/services/validation/statutory.py` implementing GSTIN Luhn Checksum and PAN entity verification.
4. **Update Frontend Inspection Drawer**: Add specialized view tabs for Bank Transactions, GST ITC tables, and TDS deduction registers.
5. **Run Integration Tests**: Ensure test suite passes cleanly with zero regressions.
