# AI_Docs_orch — plan

> Editable **intent** file: ideas + plans — what we *mean to do*.
> This is NOT the event log. `events.jsonl` -> `summary.md` records what
> *happened*; this file records what we *intend*. The AI reads it at
> session start and edits it directly (like `PROJECT_MAP.md`): add ideas
> and plans, check items off, move done work down to Shipped. Plans are
> never logged as events.

## Ideas
_Loose thoughts, not yet committed to._
- Multi-channel intake pipelines: Email (IMAP/Gmail OAuth), WhatsApp Cloud API, and Google Drive/OneDrive sync
- Local DPDP Act 2023 compliance redaction engine (Aadhaar/PAN masking before external LLM inference)
- Client portal upload links with expiring token authentication for direct client document submission
- AI Review Copilot with natural language querying ("What documents are missing for Kapoor & Shah audit?")

## Active plans
_What we're working toward now. Use `- [ ]` / `- [x]` checklists._
- Phase 2: Advanced statutory validation algorithms
  - [ ] Implement GSTIN Luhn checksum calculation and statutory verification
  - [ ] Implement PAN structural format & taxpayer entity validation
  - [ ] Implement SHA-256 duplicate document hash and invoice number uniqueness detector
  - [ ] Add OCR page chunking and transaction ledger post-processor for 50+ page bank statements

## Next
_Queued, but not started._
- Automated client reminder & follow-up engine
  - [ ] Dynamic kickoff email generation for missing checklist items
  - [ ] Real-time delta tracker comparing received documents against workflow requirements
  - [ ] Follow-up frequency and channel recommendation (Phone vs Email)

## Someday / maybe
- Cross-taxpayer reconciliation (GSTR-2B vs Vendor Purchase Register automatic matching)
- On-device local SLM (e.g. Qwen2.5-VL / Llama-3.2-Vision) for zero-cloud data isolation

## Shipped
_Move completed plans here so the top stays about the future._
- [x] Phase 1: Local GPU PP-StructureV3 OCR pipeline with CUDA 12.6 acceleration and HTML table recognition
- [x] Phase 1: Dual-provider LLM extraction architecture (Google Gemini primary, Groq fallback)
- [x] Phase 1: Business extraction schemas and validation for Invoice, BankStatement, GSTReturn, TDSForm, InvestmentProof
- [x] Phase 1: Deterministic PAN/TAN multi-member document segregation engine
- [x] Phase 1: PostgreSQL asyncpg multi-tenant database layer and domain CRUD endpoints
- [x] Phase 1: Synthetic Indian CA dataset (22 PDFs) with clean, flatbed, mobile camera warp degradation
- [x] Phase 1: Automated 22-PDF benchmark test harness with quantifiable accuracy and latency profiling
- [x] Phase 1: React 19 SPA with emerald design tokens and slide-over DocumentDrawer inspection
