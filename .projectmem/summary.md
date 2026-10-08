# projectmem - AI_Docs_orch

_Last updated: 2026-10-08_

## Project purpose
DocOps (AI Docs Orchestrator) is an audit-grade statutory document orchestration platform for accounting and CA firms that automates ingestion, layout-aware GPU OCR, typed multi-document extraction, PAN/TAN segregation, and compliance checklist tracking with human-in-the-loop verification.

## Recent issues
- [DONE] #legacy_ff92 Legacy issue: feat(fixtures): add realistic database seed script and fixture inspection tool -> feat(fixtures): add realistic database seed script and fixture inspection tool (fixed)
- [DONE] #legacy_b772 Legacy issue: feat: synthetic Indian accounting document dataset generation and fixtures -> feat: synthetic Indian accounting document dataset generation and fixtures (fixed)
- [DONE] #legacy_551a Legacy issue: fix(test): prevent pytest teardown from wiping realistic seed database and align default-org slug -> fix(test): prevent pytest teardown from wiping realistic seed database and align default-org slug (fixed)
  - Failed attempt: tried teardown deleting all organizations where slug != 'default-org', which wiped out seeded CA firm records on every test run [backend/tests/conftest.py]

## Decisions
- Use PaddleOCR PP-StructureV3 on NVIDIA CUDA 12.6 GPU for layout-aware document OCR, reading order reconstruction, and HTML table recognition instead of plain text OCR [backend/app/services/ocr.py]
- Dual-provider LLM pipeline: Primary Google Gemini (1M token context, high TPM) with automatic fallback to Groq (openai/gpt-oss-120b) with exponential backoff on HTTP 429/400 errors [backend/app/services/extraction.py]
- Decouple document classification from extraction via an explicit ClassificationService and typed EXTRACTORS registry to prevent schema misclassification and hallucinated fields [backend/app/services/extraction.py]
- Implement deterministic PAN/TAN/Name document segregation engine to split joint family/group filings and map pages to specific client members before persistence [backend/app/services/segregation.py]
- Multi-tenant PostgreSQL database layer using SQLAlchemy 2.x async (asyncpg) and Alembic migrations across Organizations, Clients, ClientMembers, Documents, and Workflows [backend/app/db/]
- Human-in-the-Loop review model: Mathematical and statutory inconsistencies flag needs_human_review=True with audit notes rather than failing pipeline execution [backend/app/schemas/extraction.py]
- React 19 + TypeScript SPA with custom emerald design tokens, TanStack Query, and slide-over DocumentDrawer for side-by-side OCR, JSON, and statutory review [frontend/src/]
- Design System for Documentation: Professional & Elegant Light Theme using porcelain canvas (#f8fafc/#ffffff), deep slate ink typography (#0f172a), hairline borders (#e2e8f0), audit emerald (#047857), statutory amber (#b45309), high-contrast code terminals (#090e17), and Plus Jakarta Sans + JetBrains Mono [docs/]
- Removed Tally ERP integration from roadmap — Phase 6 is now Client Portal & Multi-Tenant RBAC only. Tally is proprietary, requires local client installation, and is orthogonal to the core value proposition. Accountants can export to Tally manually from validated structured data if ever needed.
- Rebrand product to Patra: Statutory Document & Compliance Orchestrator with modern geometric mark (origami document P, slate/emerald palette). Updated all docs, frontend AppShell/Sidebar, and configuration.
- Frontend redesign direction (Operate mode): "Client Register" — books-of-account style light UI, navy (#14213a) shell, white work surface, green only for validated state, amber for review, red for failed; Desk leads with per-client readiness bars. Chosen by user over due-date calendar, emission-line rail, lexicon page etc. because it must feel intuitive, not portfolio-flavoured. Placeholder nav items (Reminders, Reports, Rules, Document Types, Team, Integrations), fake notification badge, and hardcoded user are removed until real pages exist. [frontend/src/]

## Notes
- Environment spec — OS: Windows 11, pwsh. Python 3.12 (uv, venv at backend/.venv), pinned >=3.12,<3.13 for paddlepaddle-gpu cp312 wheel. GPU: NVIDIA RTX 4060 Laptop 8GB (SM 8.9, driver 592.82, CUDA 12.6). PaddleOCR 3.7.0 + PaddlePaddle-GPU 3.3.1 pinned via direct wheel URL in [tool.uv.sources]. OCR models cached at C:/Users/hp/.paddlex/official_models. DB: PostgreSQL 16 localhost:5432, db=ai_docs_orch, user=project_agent. Frontend: Bun 1.x / Vite 6. Primary LLM: Gemini API (https://generativelanguage.googleapis.com/v1beta/openai/, gemini-2.5-flash, 1M ctx). Fallback: Groq (https://api.groq.com/openai/v1, openai/gpt-oss-120b, 8192 token limit).
- API surface reference — POST /api/v1/ocr/extract (upload PDF/image -> OCRResult), GET /api/v1/ocr/results/{id} (fetch JSON), GET /api/v1/ocr/results/{id}/markdown (download markdown), GET /api/v1/ocr/results/{id}/source (original file), POST /api/v1/ocr/results/{id}/parse (markdown -> DB Document + Business Object via LLM), G/POST /api/v1/organizations|clients|workflows|documents (domain CRUD), GET /api/v1/health (engine status), GET /healthz (liveness). Interactive docs: http://127.0.0.1:8000/docs
- Benchmark results (Session 13, 22 synthetic PDFs) — Classification accuracy: 95.5% (21/22). Mean key field accuracy: 82.7% overall. By condition: clean 93.9%, scanned_good 87.4%, scanned_poor 45.9% (mobile cam warp), edge_cases 100%. Human review trigger rate: 31.8% (7/22). Avg OCR latency: 3.68s (RTX 4060 GPU). Avg LLM extraction: 18.21s. Results persisted in backend/tests/fixtures/benchmark_results.json and BENCHMARK_REPORT.md. DB updated in-place with live extraction data.
- Key error solutions — (1) PaddlePaddle 3.3.1 oneDNN CPU crash: pass enable_mkldnn=False. (2) PP-StructureV3 needs paddlex[ocr] extra not just ocr-core. (3) paddlepaddle-gpu pinned via direct wheel URL in [tool.uv.sources] NOT as index (causes PyPI shadowing). (4) Pydantic field named `date` annotated `date|None` shadows built-in under __future__ annotations; use `import datetime as dt; field: dt.date|None`. (5) `rec_polys` entries are numpy arrays; guard with `poly is None or len(poly)==0` not `if not poly`. (6) `model_dump(mode='json')` required for datetime serialization to disk.
- Kapoor & Shah seed universe — 1 org (Kapoor & Shah Associates, Connaught Place, New Delhi). 3 clients: Rajput Heavy Engineering Works Pvt Ltd (GSTIN 07AABCR1234F1Z5, PAN AABCR1234F, HDFC Bank), Codeify Cloud Solutions LLP (GSTIN 27AAAFC9876Q1ZB, PAN AAAFC9876Q, ICICI Bank), Arjun Kapoor HUF (PAN ABCPK1234F). 3 active workflows: August GST, Q2 TDS, FY25-26 Tax Planning. 11 workflow requirements. 22 seeded documents. Seed script: backend/tests/fixtures/seed_db.py (use --wipe-only to reset).
- Patra brand identity: Minimalist institutional logo assets stored in docs/patra_logo.jpg, docs/patra_icon.jpg, frontend/public/favicon.svg, and frontend/public/patra-logo.svg. Color tokens: Slate ink (#0f172a), porcelain background (#f8fafc), audit emerald (#047857).
- Frontend redesign shipped (Client Register direction). Removed StatCard, ProgressBar, TopBar, animations.css (replaced by ReadinessBar, PageHeader, ui.module.css). Kept as pre-existing dead code: src/App.css, src/data/demoData.ts, public/icons.svg. Drawer no longer has Approve/Send for review buttons because there is no backend endpoint to update document status; add PATCH /documents/{id} before reintroducing them. Source preview fetches GET /ocr/results/{id}/source (HEAD returns 405). [frontend/src/]
- gotcha: when starting `impeccable serve-question --start` from Bash, do not pipe into head; the daemon inherits the pipe and the call hangs. Redirect to a file instead.
- New feature: feat(brand): rebrand product to Patra [backend/app/core/config.py]
- New feature: feat(frontend): redesign UI as a client register [.impeccable/design.json]

## Key files
- `backend/.env.example`
- `backend/.gitignore`
- `backend/app/__init__.py`
- `backend/app/api/__init__.py`
- `backend/app/api/deps.py`
- `backend/app/api/v1/__init__.py`
- `backend/app/api/v1/endpoints/__init__.py`
- `backend/app/api/v1/endpoints/health.py`
- `backend/app/api/v1/endpoints/ocr.py`
- `backend/app/api/v1/router.py`
- `backend/app/core/__init__.py`
- `backend/app/core/config.py`
- `backend/app/core/logging.py`
- `backend/app/core/storage.py`
- `backend/app/main.py`
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/ocr.py`
- `backend/app/services/__init__.py`
- `backend/app/services/ocr.py`
- `backend/pyproject.toml`

## Open questions
- None logged yet.
