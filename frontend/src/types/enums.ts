/**
 * Enums mirroring backend models/enums.py
 */

export enum DocumentType {
  INVOICE = 'invoice',
  RECEIPT = 'receipt',
  BANK_STATEMENT = 'bank_statement',
  PURCHASE_ORDER = 'purchase_order',
  GST_RETURN = 'gst_return',
  TDS_FORM = 'tds_form',
  INVESTMENT_PROOF = 'investment_proof',
  UNKNOWN = 'unknown',
}

export enum DocumentStatus {
  UPLOADED = 'uploaded',
  PROCESSING = 'processing',
  EXTRACTED = 'extracted',
  NEEDS_REVIEW = 'needs_review',
  VALIDATED = 'validated',
  REJECTED = 'rejected',
  FAILED = 'failed',
}

export enum WorkflowType {
  GST_FILING = 'gst_filing',
  BOOKKEEPING = 'bookkeeping',
  TDS_FILING = 'tds_filing',
  AUDIT = 'audit',
  PAYROLL = 'payroll',
  CUSTOM = 'custom',
}

export enum WorkflowStatus {
  COLLECTING_DOCUMENTS = 'collecting_documents',
  READY_FOR_REVIEW = 'ready_for_review',
  IN_REVIEW = 'in_review',
  READY_FOR_FILING = 'ready_for_filing',
  COMPLETED = 'completed',
  BLOCKED = 'blocked',
}

export enum ClientStatus {
  ON_TRACK = 'on_track',
  AWAITING_DOCUMENTS = 'awaiting_documents',
  REVIEW_REQUIRED = 'review_required',
  ACTION_REQUIRED = 'action_required',
  COMPLETED = 'completed',
}
