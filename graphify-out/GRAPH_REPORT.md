# Graph Report - AI_Docs_orch  (2026-09-07)

## Corpus Check
- Corpus is ~32,877 words - fits in a single context window. You may not need a graph.

## Summary
- 763 nodes · 1713 edges · 49 communities (31 shown, 10 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 140 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Extraction Schemas & Config
- React Frontend Components
- OCR Layout & Engine
- Document Segregation Engine
- Frontend Dependencies & Package
- Database Base Models
- Workflow UI & API
- Project Guidelines & Assets
- Workflow REST Endpoints
- Document API & Hooks
- OCR REST Endpoint
- Document & Enum Models
- Organizations API & Hooks
- Alembic Migrations
- TypeScript Config (App)
- Clients API & Demo Data
- API Deps & Health
- Clients REST Endpoints
- TypeScript Config (Node)
- Extraction REST Endpoint
- Document Type Enums & Domain Schemas
- Document Extraction Schema
- Schema Viewer Components
- DB Deps & Organizations Endpoints
- Core App Settings
- API Dependencies & Core Config
- OCR Frontend & Document Drawer
- Alembic Async Migration Runner
- Oxlint Frontend Config
- Extraction Endpoint Tests
- HTTP API Client
- Health Check Tests
- TypeScript Root Config
- DB Initialization
- Framework Logos
- Simplicity First Principle
- Surgical Changes Principle
- Think Before Coding
- Icons SVG Asset
- Hero Image Asset
- Backend Package Root

## God Nodes (most connected - your core abstractions)
1. `ExtractionService` - 38 edges
2. `Settings` - 34 edges
3. `get_settings()` - 30 edges
4. `react` - 22 edges
5. `Client` - 21 edges
6. `OCRService` - 21 edges
7. `DocumentType` - 20 edges
8. `DocumentType` - 19 edges
9. `Organization` - 19 edges
10. `FakeLLMClient` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Goal-Driven Execution` --semantically_similar_to--> `Human-in-the-Loop Review Pattern`  [INFERRED] [semantically similar]
  CLAUDE.md → PROJECT_PLAN.md
- `Graphify Skill` --references--> `AI Docs Orch - Agentic Document Orchestration Platform`  [EXTRACTED]
  AGENTS.md → PROJECT_PLAN.md
- `Technical Stack: FastAPI, React 19, PostgreSQL, PaddlePaddle` --references--> `React + TypeScript + Vite Frontend Setup`  [INFERRED]
  PROJECT_PLAN.md → frontend/README.md
- `create_client()` --uses--> `Organization`  [INFERRED]
  backend/app/api/v1/endpoints/clients.py → backend/app/models/organization.py
- `list_documents()` --uses--> `Document`  [INFERRED]
  backend/app/api/v1/endpoints/documents.py → backend/app/models/document.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Indian CA Document Extraction Schemas** — project_plan_bank_statement_schema, project_plan_gst_return_schema, project_plan_tds_form_schema, project_plan_investment_proof_schema [EXTRACTED 1.00]
- **Statutory Validation Engine Components** — project_plan_gstin_validator, project_plan_pan_validator, project_plan_dpdp_privacy [EXTRACTED 1.00]
- **LLM Coding Behavior Guidelines** — claude_think_before_coding, claude_simplicity_first, claude_surgical_changes, claude_goal_driven_execution [EXTRACTED 1.00]

## Communities (49 total, 10 thin omitted)

### Community 0 - "Extraction Schemas & Config"
Cohesion: 0.05
Nodes (86): get_settings(), Address, BankStatement, BankTransaction, Company, DocumentType, GSTReturn, InvestmentProof (+78 more)

### Community 1 - "React Frontend Components"
Cohesion: 0.07
Nodes (47): App(), queryClient, ProgressBar(), ProgressBarProps, buildSparklinePath(), SPARKLINE_COLORS, StatCard(), StatCardProps (+39 more)

### Community 2 - "OCR Layout & Engine"
Cohesion: 0.07
Nodes (50): OCRBlock, OCREngineInfo, OCRLayoutBlock, OCRPage, OCRResult, BaseModel, Pydantic schemas for OCR API responses., A semantic layout region (text/title/table/...) in reading order. (+42 more)

### Community 3 - "Document Segregation Engine"
Cohesion: 0.12
Nodes (34): assign_segments_to_members(), detect_identity_signals(), DocumentSegment, IdentitySignals, MemberAssignment, MemberProfile, _name_similarity(), _normalize_name() (+26 more)

### Community 4 - "Frontend Dependencies & Package"
Cohesion: 0.06
Nodes (33): dependencies, clsx, lucide-react, react, react-dom, react-router-dom, @tanstack/react-query, devDependencies (+25 more)

### Community 5 - "Database Base Models"
Cohesion: 0.14
Nodes (20): Base, Declarative base and common mixins for all SQLAlchemy models., Shared declarative base for all models., Mixin that adds a UUID primary key generated server-side., Mixin that adds created_at (auto-set) and updated_at (auto-updated)., TimestampMixin, UUIDPrimaryKeyMixin, clean_db() (+12 more)

### Community 6 - "Workflow UI & API"
Cohesion: 0.10
Nodes (21): workflowsApi, STEPS, WorkflowTimeline(), WorkflowTimelineProps, Workflow, WorkflowCreate, WorkflowUpdate, WorkflowStatus (+13 more)

### Community 7 - "Project Guidelines & Assets"
Cohesion: 0.08
Nodes (26): Graphify Skill, Goal-Driven Execution, Frontend HTML Entry Point, App Favicon - Purple Lightning Bolt Logo, React + TypeScript + Vite Frontend Setup, AI Docs Orch - Agentic Document Orchestration Platform, BankStatement Schema, AI Review Copilot Engine (+18 more)

### Community 8 - "Workflow REST Endpoints"
Cohesion: 0.17
Nodes (22): create_workflow(), get_workflow(), list_workflows(), AsyncSession, get, patch, post, UUID (+14 more)

### Community 9 - "Document API & Hooks"
Cohesion: 0.10
Nodes (21): documentsApi, DbDocument, Document, WorkflowRequirement, DocumentStatus, EXTRACTED, FAILED, NEEDS_REVIEW (+13 more)

### Community 10 - "OCR REST Endpoint"
Cohesion: 0.17
Nodes (19): extract(), post, OCR extraction endpoints., _safe_filename(), _validate_extension(), new_result_id(), Exception, Path (+11 more)

### Community 11 - "Document & Enum Models"
Cohesion: 0.16
Nodes (18): Document, Document model — one uploaded file, its OCR result, and extracted data., DocumentStatus, Database-level enum definitions shared across SQLAlchemy models. These are…, Lifecycle of one uploaded document through the processing pipeline., get_or_create_default_client(), get_or_create_default_organization(), Any (+10 more)

### Community 12 - "Organizations API & Hooks"
Cohesion: 0.12
Nodes (17): organizationsApi, Address, BankTransaction, Company, GSTReturnType, InvestmentSection, Invoice, InvoiceItem (+9 more)

### Community 13 - "Alembic Migrations"
Cohesion: 0.16
Nodes (15): Alembic env.py — configured for async SQLAlchemy + our model metadata. Reads…, Run migrations in 'offline' mode (emit SQL without connecting)., run_migrations_offline(), attach_document_to_workflow(), get_document(), list_documents(), AsyncSession, get (+7 more)

### Community 14 - "TypeScript Config (App)"
Cohesion: 0.11
Nodes (18): compilerOptions, allowArbitraryExtensions, allowImportingTsExtensions, jsx, lib, module, moduleDetection, moduleResolution (+10 more)

### Community 15 - "Clients API & Demo Data"
Cohesion: 0.14
Nodes (16): clientsApi, AvatarColor, DEMO_CLIENTS, DEMO_INVOICE_EXTRACTION, DEMO_RECENT_ACTIVITIES, DEMO_STATS, Client, ClientCreate (+8 more)

### Community 16 - "API Deps & Health"
Cohesion: 0.18
Nodes (12): get_ocr_service(), health(), AsyncSession, get, System health & configuration endpoint., Aggregates all v1 API routers., Logging setup for the application., setup_logging() (+4 more)

### Community 17 - "Clients REST Endpoints"
Cohesion: 0.24
Nodes (16): create_client(), get_client(), list_clients(), AsyncSession, Client, get, patch, post (+8 more)

### Community 18 - "TypeScript Config (Node)"
Cohesion: 0.12
Nodes (16): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, noEmit, noFallthroughCasesInSwitch (+8 more)

### Community 19 - "Extraction REST Endpoint"
Cohesion: 0.20
Nodes (15): _average_confidence(), parse(), AsyncSession, post, UUID, Business extraction endpoints (markdown -> Document + Invoice)., get_markdown(), get_result() (+7 more)

### Community 20 - "Document Type Enums & Domain Schemas"
Cohesion: 0.26
Nodes (14): DocumentType, The kind of business document (used for classification + extraction)., ClientRead, DocumentAttachToWorkflow, DocumentCreate, DocumentRead, OrganizationCreate, OrganizationRead (+6 more)

### Community 21 - "Document Extraction Schema"
Cohesion: 0.23
Nodes (9): Document, DocumentExtraction, What the LLM parse step returns for one uploaded document. At most one business…, Map of field name -> populated business object (usually 0 or 1 entries)., FakeExtractionService, FakeExtractionService, Tests for the parse endpoint (LLM extraction is mocked)., _stored_result() (+1 more)

### Community 22 - "Schema Viewer Components"
Cohesion: 0.24
Nodes (12): BankStatementView(), fmtINR(), GSTReturnView(), InfoEntry, InvestmentProofView(), ITCGrid(), orNA(), TDSFormView() (+4 more)

### Community 23 - "DB Deps & Organizations Endpoints"
Cohesion: 0.21
Nodes (12): get_db(), AsyncSession, Yield an async DB session per request, auto-closing on completion., create_organization(), get_organization(), list_organizations(), AsyncSession, get (+4 more)

### Community 24 - "Core App Settings"
Cohesion: 0.23
Nodes (7): Path, Settings, ClassificationService, LLMClient, Minimal OpenAI-compatible chat client built on httpx (no SDK dependency)., Picks the document type with a cheap, separate LLM call., BaseSettings

### Community 25 - "API Dependencies & Core Config"
Cohesion: 0.21
Nodes (6): get_extraction_service(), Shared FastAPI dependencies., Application configuration loaded from environment / .env., Integration tests for DB-backed Organization, Client, Workflow, and Document…, _sample_ocr_result(), test_parse_endpoint_persists_to_db()

### Community 26 - "OCR Frontend & Document Drawer"
Cohesion: 0.24
Nodes (8): ocrApi, DocumentDrawer(), DocumentDrawerProps, Tab, useDocument(), useOCRMarkdown(), useOCRResult(), OCRResult

### Community 27 - "Alembic Async Migration Runner"
Cohesion: 0.33
Nodes (6): do_run_migrations(), Shared migration runner used by the async online path., Create an async engine and run migrations inside a connection., Run migrations in 'online' mode (async)., run_async_migrations(), run_migrations_online()

### Community 28 - "Oxlint Frontend Config"
Cohesion: 0.33
Nodes (5): plugins, rules, react/only-export-components, react/rules-of-hooks, $schema

### Community 29 - "Extraction Endpoint Tests"
Cohesion: 0.50
Nodes (3): _make_png_bytes(), End-to-end test exercising the real OCR pipeline (models are cached)., test_extract_image_end_to_end()

### Community 30 - "HTTP API Client"
Cohesion: 0.50
Nodes (3): apiClient, ApiError, request()

## Knowledge Gaps
- **152 isolated node(s):** `backend`, `$schema`, `plugins`, `react/rules-of-hooks`, `react/only-export-components` (+147 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 333 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Settings` connect `Core App Settings` to `Extraction Schemas & Config`, `OCR Layout & Engine`, `OCR REST Endpoint`, `API Deps & Health`, `Extraction REST Endpoint`, `API Dependencies & Core Config`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `Extraction Schemas & Config` to `Database Base Models`, `OCR REST Endpoint`, `Alembic Migrations`, `API Deps & Health`, `Extraction REST Endpoint`, `Document Extraction Schema`, `Core App Settings`, `API Dependencies & Core Config`?**
  _High betweenness centrality (0.026) - this node is a cross-community bridge._
- **Why does `OCRService` connect `OCR Layout & Engine` to `API Deps & Health`, `API Dependencies & Core Config`, `OCR REST Endpoint`, `Core App Settings`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `ExtractionService` (e.g. with `parse()` and `Settings`) actually correct?**
  _`ExtractionService` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `Settings` (e.g. with `parse()` and `health()`) actually correct?**
  _`Settings` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Client` (e.g. with `create_client()` and `get_client()`) actually correct?**
  _`Client` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `backend`, `$schema`, `plugins` to the rest of the system?**
  _152 weakly-connected nodes found - possible documentation gaps or missing edges._