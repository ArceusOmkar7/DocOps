# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Chartered Accountants (CAs), CPAs, tax professionals, and accounting firm audit/operations teams managing high volumes of client compliance filings (GST, TDS, ITR, statutory audits).

## Product Purpose

Patra eliminates pre-accounting manual overhead by automating document ingestion, layout-aware OCR extraction, classification, statutory cross-checks, and client checklist progression. It keeps the human accountant strictly as the final reviewer and authority (Human-in-the-Loop).

## Positioning

Unlike generic document intake or generic AI chatbots, Patra is an audit-grade statutory orchestration platform designed specifically for accounting workflows. It performs exact mathematical cross-validation, GSTIN and PAN statutory validation, compliance checklist tracking, and audit-ready inspection trails.

## Operating Context

Accounting professionals operate in high-density, multi-client compliance environments under strict regulatory deadlines. They deal with financial records, invoices, bank statements, tax returns (GSTR-3B, GSTR-1, Form 16, Form 26AS), and investment proofs across clients. Speed, information density, precision, and compliance integrity are paramount.

## Capabilities and Constraints

- **Capabilities**: Multi-tenant client management, file ingestion & disk storage, PaddleOCR/PP-StructureV3 GPU OCR, document type classification, invoice/statement entity extraction, statutory math checks, live compliance workflows with status progression, inspection drawer with raw OCR & JSON viewer.
- **Constraints**: Data privacy (DPDP compliance, client data isolation), strict zero-hallucination requirement for numbers/amounts, desktop web priority with high information density.

## Brand Commitments

- **Name**: Patra (Statutory Document & Compliance Orchestration)
- **Tone**: Authoritative, precise, enterprise-grade, institutional, calm, and distraction-free. Not a toy, playful SaaS, or consumer chatbot.
- **Interface style**: Familiar and intuitive over distinctive. The UI should look like accounting software a CA already knows how to use: standard controls, a clear register, no portfolio-style flourishes. Colour is reserved for state.

## Evidence on Hand

- Real database schemas and seed records for clients (Rajput Steelworks, Codeify Technologies, Arjun Khanna).
- Extracted documents covering Invoices, GSTR-3B, Bank Statements, LIC receipts, PPF statements, Form 16/26AS.
- Live backend running FastAPI on port 8000; Vite frontend on port 3000.

## Product Principles

1. **Precision & Trust First**: Every number, date, and status must look audited and verifiable; no speculative styling or vague decorative indicators.
2. **Tools Over Toys**: Built for speed, high data density, and clear visual hierarchy rather than pastel bubble-gum aesthetics or AI buzzwords.
3. **Restrained Color Function**: Color exists strictly to communicate state (e.g. attention needed vs. validated) rather than decoration.
4. **Human-in-the-Loop Integrity**: The system presents facts, confidence, and audit trails transparently for professional verification.
