# Project Map - AI_Docs_orch

Status: maintained by AI sessions.

## Project purpose
DocOps (AI Docs Orchestrator) is an audit-grade statutory document orchestration platform for accounting and CA firms that automates ingestion, layout-aware GPU OCR, typed multi-document extraction, PAN/TAN segregation, and compliance checklist tracking with human-in-the-loop verification.

## Structure
- `backend/` — FastAPI backend service (Python 3.12, CUDA 12.6, PostgreSQL asyncpg)
  - `backend/app/main.py` — FastAPI application factory, lifespan management, directory creation, DB engine disposal
  - `backend/app/core/config.py` — Application configuration, dual LLM provider credentials (Gemini/Groq), OCR parameters
  - `backend/app/core/logging.py` — Unified structured stdout logging setup
  - `backend/app/core/storage.py` — File persistence for uploaded raw documents, OCR results, and JSON artifacts in `backend/data/`
  - `backend/app/db/` — Database engine and session management
    - `backend/app/db/session.py` — Async SQLAlchemy engine and async sessionmaker bound to PostgreSQL
    - `backend/app/db/base.py` — Declarative Base importing all domain models for Alembic autogeneration
  - `backend/app/models/` — SQLAlchemy 2.x async ORM models
    - `backend/app/models/domain.py` — Core entities: Organization, Client, ClientMember, Document, Workflow, WorkflowDocumentRequirement
  - `backend/app/schemas/` — Pydantic data contract definitions
    - `backend/app/schemas/ocr.py` — OCRBlock, OCRLayoutBlock, OCRPage, OCRResult models
    - `backend/app/schemas/extraction.py` — Business schemas: Invoice, BankStatement, GSTReturn, TDSForm, InvestmentProof
    - `backend/app/schemas/domain.py` — Domain API schemas for Organizations, Clients, Workflows, Requirements
  - `backend/app/services/` — Business logic and service orchestration
    - `backend/app/services/ocr.py` — PPStructureV3 GPU OCR wrapper with layout detection, HTML table recognition, and header preservation
    - `backend/app/services/extraction.py` — Dual-provider LLM client (Gemini primary, Groq fallback) with classification & typed extraction registry
    - `backend/app/services/segregation.py` — Deterministic PAN/TAN/Name document segregation and client member assignment
    - `backend/app/services/db_helpers.py` — Extraction persistence helpers updating PostgreSQL Document records
  - `backend/app/api/` — HTTP REST API routers
    - `backend/app/api/deps.py` — Dependency injection for DB session, OCRService, and ExtractionService
    - `backend/app/api/v1/router.py` — Aggregates all v1 API route endpoints
    - `backend/app/api/v1/endpoints/ocr.py` — Endpoints for OCR extraction, result retrieval, markdown/source download, and parse-to-DB
    - `backend/app/api/v1/endpoints/health.py` — Liveness and engine readiness health checks
    - `backend/app/api/v1/endpoints/organizations.py` — CRUD operations for Organizations
    - `backend/app/api/v1/endpoints/clients.py` — CRUD operations for Clients and ClientMembers
    - `backend/app/api/v1/endpoints/workflows.py` — Workflow progression and requirement management
    - `backend/app/api/v1/endpoints/documents.py` — Document queries and metadata management
  - `backend/alembic/` — Database schema migration version scripts
  - `backend/tests/` — Test suites and synthetic CA benchmarking fixtures
    - `backend/tests/conftest.py` — Pytest configuration, async test client fixtures, isolated test-org teardown
    - `backend/tests/test_ocr_service.py` — Unit tests for PP-StructureV3 output parsing and layout preservation
    - `backend/tests/test_extraction.py` — Unit tests for LLM extraction retry loops and business review validators
    - `backend/tests/test_domain_api.py` — Integration tests for organization, client, and workflow endpoints
    - `backend/tests/fixtures/generators/` — Synthetic Indian document generators (ReportLab) for Invoices, Bank Statements, GST, TDS, Investment
    - `backend/tests/fixtures/degradation.py` — Scan degradation pipelines (clean, 300 DPI flatbed, 150 DPI mobile camera warp/vignette)
    - `backend/tests/fixtures/seed_db.py` — Kapoor & Shah Associates CA universe database seed script
    - `backend/tests/fixtures/benchmark_dataset.py` — Live 22-document evaluation benchmark runner with field accuracy & latency profiling
- `frontend/` — React 19 Single Page Application (TypeScript, Vite, TanStack Query v5, Bun)
  - `frontend/src/main.tsx` — React entry point mounting App and TanStack QueryClientProvider
  - `frontend/src/App.tsx` — Top-level application routing and layout wrapping
  - `frontend/src/styles/` — Design system CSS variables (emerald `#059669` theme, card elevation, typography)
  - `frontend/src/components/layout/` — Shell layout components (AppShell, Sidebar, TopBar)
  - `frontend/src/components/common/` — Shared UI primitives (StatCard, StatusBadge, Button, Modal)
  - `frontend/src/components/documents/` — Document inspection and upload components
    - `frontend/src/components/documents/DocumentDrawer.tsx` — Slide-over inspection drawer with Overview, Preview, OCR, and Raw Data tabs
    - `frontend/src/components/documents/DocumentUploader.tsx` — Drag-and-drop document upload zone
    - `frontend/src/components/documents/InvoiceView.tsx` — Typed viewer for B2B GST tax invoices
    - `frontend/src/components/documents/BankStatementView.tsx` — Typed viewer for bank accounts & transaction ledger
    - `frontend/src/components/documents/GSTReturnView.tsx` — Typed viewer for GSTR-3B table summaries and outward tax
    - `frontend/src/components/documents/TDSFormView.tsx` — Typed viewer for Form 16 / 26AS tax deductions
    - `frontend/src/components/documents/InvestmentProofView.tsx` — Typed viewer for Chapter VI-A / 80C investments
  - `frontend/src/components/workflows/` — Workflow tracking and template selection components
  - `frontend/src/pages/` — Page-level views (DashboardPage, ClientsPage, DocumentsPage, WorkflowsPage, SettingsPage)
  - `frontend/src/api/apiClient.ts` — Typed fetch wrapper for backend v1 API endpoints
  - `frontend/src/hooks/` — TanStack Query hooks (useClients, useDocuments, useWorkflows, useOCR)

## Relationships
- `frontend/src/api/apiClient.ts` calls `backend/app/api/v1/router.py` over HTTP REST
- `frontend/src/components/documents/DocumentDrawer.tsx` reads parsed JSON payloads from `backend/app/models/domain.py:Document.extracted_data`
- `backend/app/api/v1/endpoints/ocr.py` calls `backend/app/services/ocr.py` for GPU document parsing
- `backend/app/api/v1/endpoints/ocr.py` calls `backend/app/services/extraction.py` to parse OCR markdown into typed business schemas
- `backend/app/services/ocr.py` invokes PaddleOCR `PPStructureV3` running on NVIDIA CUDA 12.6
- `backend/app/services/extraction.py` calls Google Gemini API (primary) with automatic failover to Groq API (fallback)
- `backend/app/services/extraction.py` calls `backend/app/services/segregation.py` to detect PAN/TAN and associate taxpayer members
- `backend/app/services/db_helpers.py` writes parsed entities and inspection flags to PostgreSQL `documents` table via `backend/app/db/session.py`
- `backend/tests/fixtures/benchmark_dataset.py` benchmarks `backend/app/services/ocr.py` and `backend/app/services/extraction.py` against 22 synthetic ground-truth PDFs

## Stack
- Python 3.12 (pinned `>=3.12, <3.13` for `paddlepaddle-gpu==3.3.1` cu126 wheels)
- NVIDIA CUDA 12.6, PaddleOCR 3.7.0 / PP-StructureV3 layout analysis
- FastAPI 0.141.1, Pydantic v2, pydantic-settings
- Primary LLM: Google Gemini 2.5/3.5 Flash (1M token context, OpenAI-compatible endpoint)
- Fallback LLM: Groq `openai/gpt-oss-120b` (OpenAI-compatible endpoint)
- PostgreSQL 16 on `localhost:5432` (`ai_docs_orch`), SQLAlchemy 2.x async, asyncpg, Alembic
- Frontend: Bun 1.x, Vite, React 19, TypeScript, TanStack Query v5, React Router v7, Lucide React

## Suggested first reads
- `PRODUCT.md` — Product vision, CA user personas, brand principles, and statutory context
- `PROJECT_PLAN.md` — Master phase-wise implementation roadmap and component comparison
- `backend/app/main.py` — Backend application entry point and lifespan hooks
- `backend/app/services/ocr.py` — PP-StructureV3 GPU OCR and header preservation implementation
- `backend/app/services/extraction.py` — Dual-provider LLM classification and typed extraction engine
- `frontend/src/components/documents/DocumentDrawer.tsx` — Human-in-the-loop document inspection drawer
