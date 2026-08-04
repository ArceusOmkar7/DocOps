import {
  ClientStatus,
  DocumentStatus,
  DocumentType,
  WorkflowStatus,
  WorkflowType,
} from './enums';

export {
  ClientStatus,
  DocumentStatus,
  DocumentType,
  WorkflowStatus,
  WorkflowType,
};

export interface Address {
  line1?: string | null;
  line2?: string | null;
  city?: string | null;
  state?: string | null;
  postal_code?: string | null;
  country?: string | null;
}

export interface Company {
  name?: string | null;
  address?: Address | null;
  tax_id?: string | null; // GSTIN, VAT, etc.
  email?: string | null;
  phone?: string | null;
}

export interface InvoiceItem {
  description?: string | null;
  quantity?: number | null;
  unit_price?: number | null;
  tax_rate?: number | null;
  line_total?: number | null;
}

export interface TaxBreakdown {
  cgst?: number | null;
  sgst?: number | null;
  igst?: number | null;
  vat?: number | null;
  other_tax_label?: string | null;
  other_tax_amount?: number | null;
}

export interface Document {
  id: string;
  source_filename: string;
  document_type: DocumentType;
  ocr_confidence?: number | null;
  raw_markdown?: string;
  created_at: string;
  extraction_status: 'pending' | 'success' | 'failed' | 'needs_review' | 'unsupported';
  needs_human_review: boolean;
  review_reason?: string | null;
}

export interface Invoice {
  document_id: string;
  invoice_number?: string | null;
  invoice_date?: string | null;
  due_date?: string | null;
  purchase_order_ref?: string | null;
  seller?: Company;
  buyer?: Company;
  currency?: string | null;
  items?: InvoiceItem[];
  subtotal?: number | null;
  tax?: TaxBreakdown;
  total_tax?: number | null;
  total?: number | null;
  amount_paid?: number | null;
  balance_due?: number | null;
  payment_terms?: string | null;
  notes?: string | null;
  extraction_confidence?: number | null;
}

export interface DocumentExtraction {
  document: Document;
  invoice?: Invoice | null;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  plan: string;
  created_at: string;
  updated_at?: string | null;
}

export interface OrganizationCreate {
  name: string;
  slug: string;
  plan?: string;
}

export interface Client {
  id: string;
  organization_id: string;
  name: string;
  tax_id?: string | null;
  email?: string | null;
  phone?: string | null;
  contact_person?: string | null;
  status: ClientStatus;
  created_at: string;
  updated_at?: string | null;
}

export interface ClientCreate {
  organization_id: string;
  name: string;
  tax_id?: string | null;
  email?: string | null;
  phone?: string | null;
  contact_person?: string | null;
  status?: ClientStatus;
}

export interface ClientUpdate {
  name?: string;
  tax_id?: string | null;
  email?: string | null;
  phone?: string | null;
  contact_person?: string | null;
  status?: ClientStatus;
}

export interface WorkflowRequirement {
  id: string;
  workflow_id: string;
  document_type: DocumentType;
  label: string;
  required_count?: number | null;
  notes?: string | null;
}

export interface WorkflowRequirementCreate {
  document_type: DocumentType;
  label: string;
  required_count?: number | null;
  notes?: string | null;
}

export interface Workflow {
  id: string;
  organization_id: string;
  client_id: string;
  name: string;
  workflow_type: WorkflowType;
  period_start: string;
  period_end: string;
  status: WorkflowStatus;
  created_at: string;
  closed_at?: string | null;
  requirements: WorkflowRequirement[];
}

export interface WorkflowCreate {
  organization_id: string;
  client_id: string;
  name: string;
  workflow_type: WorkflowType;
  period_start: string;
  period_end: string;
  requirements?: WorkflowRequirementCreate[];
}

export interface WorkflowUpdate {
  name?: string;
  status?: WorkflowStatus;
  closed_at?: string | null;
}

export interface DbDocument {
  id: string;
  organization_id: string;
  client_id: string;
  source_filename: string;
  file_path?: string | null;
  ocr_result_id?: string | null;
  document_type: DocumentType;
  status: DocumentStatus;
  ocr_confidence?: number | null;
  extraction_confidence?: number | null;
  needs_human_review: boolean;
  review_reason?: string | null;
  extracted_data?: Record<string, any> | null;
  metadata_?: Record<string, any> | null;
  uploaded_at: string;
  processed_at?: string | null;
}

export interface OCRBlock {
  block_id: number;
  label?: string | null;
  text: string;
  confidence: number;
  bbox?: [number, number, number, number] | null;
}

export interface OCRPage {
  page_index: number;
  width?: number | null;
  height?: number | null;
  blocks: OCRBlock[];
}

export interface OCRResult {
  id?: string;
  result_id: string;
  filename: string;
  file_type: string;
  page_count: number;
  pages: OCRPage[];
  full_text: string;
  markdown: string;
  processing_time_ms: number;
  engine: Record<string, any>;
  created_at: string;
  source_url?: string;
  markdown_url?: string;
}

