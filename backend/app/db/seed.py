"""Database seed script to populate PostgreSQL with initial organizations, clients, workflows, and documents."""

import asyncio
import uuid
from datetime import date, datetime, timezone
from sqlalchemy import select

from app.db.engine import async_session_factory
from app.models.organization import Organization
from app.models.client import Client
from app.models.workflow import Workflow
from app.models.workflow_document_requirement import WorkflowDocumentRequirement
from app.models.document import Document
from app.models.workflow_document import WorkflowDocument
from app.models.enums import ClientStatus, WorkflowStatus, WorkflowType, DocumentType, DocumentStatus


async def seed() -> None:
    async with async_session_factory() as db:
        print("[SEED] Starting database seeding...")

        # 1. Seed Organization
        stmt = select(Organization).where(Organization.slug == "default-org")
        res = await db.execute(stmt)
        org = res.scalar_one_or_none()

        if not org:
            org = Organization(
                name="Acme Accounting & Tax Advisory",
                slug="default-org",
                plan="pro",
            )
            db.add(org)
            await db.commit()
            await db.refresh(org)
            print(f"[SEED] Created Organization: {org.name} ({org.id})")
        else:
            print(f"[SEED] Organization already exists: {org.name}")

        # 2. Seed Clients
        clients_data = [
            {
                "name": "ABC Traders",
                "tax_id": "27ABCDE1234F1Z5",
                "email": "contact@abctraders.com",
                "phone": "+91 98765 43210",
                "contact_person": "Rajesh Kumar",
                "status": ClientStatus.on_track,
            },
            {
                "name": "XYZ Industries",
                "tax_id": "27XYZAB5678G2Z9",
                "email": "finance@xyzindustries.io",
                "phone": "+91 98123 45678",
                "contact_person": "Priya Sharma",
                "status": ClientStatus.review_required,
            },
            {
                "name": "PQR Pvt Ltd",
                "tax_id": "27PQRST9012H3Z1",
                "email": "accounts@pqr.co.in",
                "phone": "+91 97654 32109",
                "contact_person": "Amit Patel",
                "status": ClientStatus.action_required,
            },
        ]

        created_clients = []
        for cdata in clients_data:
            stmt = select(Client).where(
                Client.organization_id == org.id,
                Client.name == cdata["name"],
            )
            res = await db.execute(stmt)
            client = res.scalar_one_or_none()
            if not client:
                client = Client(organization_id=org.id, **cdata)
                db.add(client)
                await db.commit()
                await db.refresh(client)
                print(f"[SEED] Created Client: {client.name}")
            else:
                print(f"[SEED] Client already exists: {client.name}")
            created_clients.append(client)

        # 3. Seed Documents
        docs_seed_data = [
            {
                "client": created_clients[0],  # ABC Traders
                "source_filename": "Invoice_INV-1023.pdf",
                "document_type": DocumentType.invoice,
                "status": DocumentStatus.validated,
                "ocr_confidence": 0.986,
                "extraction_confidence": 0.99,
                "needs_human_review": False,
                "review_reason": None,
                "ocr_result_id": "739dcb898dab4bacbcb8d90a05abc72c",
                "extracted_data": {
                    "document_type": "invoice",
                    "invoice": {
                        "invoice_number": "INV-1023",
                        "invoice_date": "2025-04-13",
                        "due_date": "2025-04-30",
                        "currency": "INR",
                        "seller": {
                            "name": "Dell India Pvt Ltd",
                            "tax_id": "29AAACD0123P1Z2",
                            "address": "12/A Electronic City, Bengaluru",
                        },
                        "buyer": {
                            "name": "ABC Traders",
                            "tax_id": "27ABCDE1234F1Z5",
                            "address": "45 Commercial Street, Mumbai",
                        },
                        "items": [
                            {
                                "description": "CLEARANCE! Fast Dell Desktop",
                                "quantity": 3.0,
                                "unit_price": 209.0,
                                "line_total": 627.0,
                                "tax_rate": 0.10,
                            }
                        ],
                        "subtotal": 627.0,
                        "tax_details": [{"tax_name": "GST", "rate": 0.10, "amount": 62.7}],
                        "total_tax": 62.7,
                        "total": 689.7,
                    },
                },
            },
            {
                "client": created_clients[1],  # XYZ Industries
                "source_filename": "Rent_Bill_XYZ_April.pdf",
                "document_type": DocumentType.invoice,
                "status": DocumentStatus.needs_review,
                "ocr_confidence": 0.942,
                "extraction_confidence": 0.88,
                "needs_human_review": True,
                "review_reason": "Tax-inclusive line items: sum of line totals (627.0) != pre-tax subtotal (570.0)",
                "ocr_result_id": "rent_bill_xyz_april_2025",
                "extracted_data": {
                    "document_type": "invoice",
                    "invoice": {
                        "invoice_number": "RENT-8841",
                        "invoice_date": "2025-04-12",
                        "currency": "INR",
                        "seller": {"name": "Metro Properties Corp", "tax_id": "27METRO9988A1Z1"},
                        "buyer": {"name": "XYZ Industries", "tax_id": "27XYZAB5678G2Z9"},
                        "items": [
                            {
                                "description": "April Office Space Lease",
                                "quantity": 1.0,
                                "unit_price": 45000.0,
                                "line_total": 45000.0,
                            }
                        ],
                        "subtotal": 45000.0,
                        "total_tax": 8100.0,
                        "total": 53100.0,
                    },
                },
            },
            {
                "client": created_clients[0],  # ABC Traders
                "source_filename": "HDFC_Bank_Statement_April.pdf",
                "document_type": DocumentType.bank_statement,
                "status": DocumentStatus.validated,
                "ocr_confidence": 0.991,
                "extraction_confidence": 0.98,
                "needs_human_review": False,
                "review_reason": None,
                "ocr_result_id": "hdfc_bank_statement_april",
                "extracted_data": {
                    "document_type": "bank_statement",
                    "statement": {
                        "bank_name": "HDFC Bank",
                        "account_number": "XXXX-XXXX-4102",
                        "period_start": "2025-04-01",
                        "period_end": "2025-04-30",
                        "opening_balance": 142050.0,
                        "closing_balance": 284100.0,
                    },
                },
            },
            {
                "client": created_clients[2],  # PQR Pvt Ltd
                "source_filename": "Purchase_Bill_5678.pdf",
                "document_type": DocumentType.invoice,
                "status": DocumentStatus.needs_review,
                "ocr_confidence": 0.720,
                "extraction_confidence": 0.65,
                "needs_human_review": True,
                "review_reason": "Low OCR block confidence score (72.0%)",
                "ocr_result_id": "purchase_bill_5678_pqr",
                "extracted_data": {
                    "document_type": "invoice",
                    "invoice": {
                        "invoice_number": "PB-5678",
                        "invoice_date": "2025-04-09",
                        "currency": "INR",
                        "seller": {"name": "Global Office Supplies"},
                        "buyer": {"name": "PQR Pvt Ltd", "tax_id": "27PQRST9012H3Z1"},
                        "subtotal": 12500.0,
                        "total": 14750.0,
                    },
                },
            },
        ]

        created_docs = []
        now = datetime.now(timezone.utc)
        for dseed in docs_seed_data:
            stmt = select(Document).where(
                Document.organization_id == org.id,
                Document.source_filename == dseed["source_filename"],
            )
            res = await db.execute(stmt)
            doc = res.scalar_one_or_none()
            if not doc:
                doc = Document(
                    organization_id=org.id,
                    client_id=dseed["client"].id,
                    source_filename=dseed["source_filename"],
                    document_type=dseed["document_type"],
                    status=dseed["status"],
                    ocr_confidence=dseed["ocr_confidence"],
                    extraction_confidence=dseed["extraction_confidence"],
                    needs_human_review=dseed["needs_human_review"],
                    review_reason=dseed["review_reason"],
                    ocr_result_id=dseed["ocr_result_id"],
                    extracted_data=dseed["extracted_data"],
                    metadata_={
                        "engine": "PP-StructureV3",
                        "device": "gpu",
                        "pages": 1,
                    },
                    uploaded_at=now,
                    processed_at=now,
                )
                db.add(doc)
                await db.commit()
                await db.refresh(doc)
                print(f"[SEED] Created Document: {doc.source_filename}")
            else:
                print(f"[SEED] Document already exists: {doc.source_filename}")
            created_docs.append(doc)

        # 4. Seed Workflows & attach document links
        if created_clients:
            workflows_data = [
                {
                    "client": created_clients[0],  # ABC Traders
                    "name": "GST Monthly Filing — April 2025",
                    "workflow_type": WorkflowType.gst_filing,
                    "status": WorkflowStatus.ready_for_filing,
                    "period_start": date(2025, 4, 1),
                    "period_end": date(2025, 4, 30),
                    "reqs": [
                        {"name": "Sales Invoices GSTR-1", "doc_type": DocumentType.invoice, "req": True},
                        {"name": "Purchase Bills GSTR-2B", "doc_type": DocumentType.invoice, "req": True},
                        {"name": "Bank Statement", "doc_type": DocumentType.bank_statement, "req": True},
                    ],
                },
                {
                    "client": created_clients[1],  # XYZ Industries
                    "name": "AP 3-Way Match — Hardware Purchase",
                    "workflow_type": WorkflowType.bookkeeping,
                    "status": WorkflowStatus.collecting_documents,
                    "period_start": date(2025, 4, 1),
                    "period_end": date(2025, 4, 30),
                    "reqs": [
                        {"name": "Purchase Order", "doc_type": DocumentType.invoice, "req": True},
                        {"name": "Delivery Challan", "doc_type": DocumentType.receipt, "req": True},
                        {"name": "Vendor Invoice", "doc_type": DocumentType.invoice, "req": True},
                    ],
                },
                {
                    "client": created_clients[2],  # PQR Pvt Ltd
                    "name": "TDS Quarterly Return Q4",
                    "workflow_type": WorkflowType.tds_filing,
                    "status": WorkflowStatus.in_review,
                    "period_start": date(2025, 1, 1),
                    "period_end": date(2025, 3, 31),
                    "reqs": [
                        {"name": "TDS Payment Challans", "doc_type": DocumentType.receipt, "req": True},
                        {"name": "Deduction Register", "doc_type": DocumentType.invoice, "req": True},
                    ],
                },
            ]

            for wdata in workflows_data:
                stmt = select(Workflow).where(
                    Workflow.client_id == wdata["client"].id,
                    Workflow.name == wdata["name"],
                )
                res = await db.execute(stmt)
                wf = res.scalar_one_or_none()
                if not wf:
                    wf = Workflow(
                        organization_id=org.id,
                        client_id=wdata["client"].id,
                        name=wdata["name"],
                        workflow_type=wdata["workflow_type"],
                        status=wdata["status"],
                        period_start=wdata["period_start"],
                        period_end=wdata["period_end"],
                    )
                    db.add(wf)
                    await db.commit()
                    await db.refresh(wf)

                    created_reqs = []
                    for req_info in wdata["reqs"]:
                        req = WorkflowDocumentRequirement(
                            workflow_id=wf.id,
                            label=req_info["name"],
                            document_type=req_info["doc_type"],
                            required_count=1 if req_info["req"] else None,
                        )
                        db.add(req)
                        created_reqs.append(req)
                    await db.commit()

                    # Attach matching created docs to workflow requirement
                    if created_docs and created_reqs:
                        for d in created_docs:
                            if d.client_id == wf.client_id:
                                link = WorkflowDocument(
                                    workflow_id=wf.id,
                                    document_id=d.id,
                                    requirement_id=created_reqs[0].id,
                                )
                                db.add(link)
                        await db.commit()
                    print(f"[SEED] Created Workflow: {wf.name}")
                else:
                    print(f"[SEED] Workflow already exists: {wf.name}")

        print("[SEED] Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
