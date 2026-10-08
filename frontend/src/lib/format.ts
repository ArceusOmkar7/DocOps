import { ClientStatus, DocumentType, WorkflowStatus } from '../types/enums';

const DOC_TYPE_LABELS: Record<string, string> = {
  [DocumentType.INVOICE]: 'Invoice',
  [DocumentType.RECEIPT]: 'Receipt',
  [DocumentType.BANK_STATEMENT]: 'Bank statement',
  [DocumentType.PURCHASE_ORDER]: 'Purchase order',
  [DocumentType.GST_RETURN]: 'GST return',
  [DocumentType.TDS_FORM]: 'TDS form',
  [DocumentType.INVESTMENT_PROOF]: 'Investment proof',
  [DocumentType.UNKNOWN]: 'Unclassified',
};

export const documentTypeLabel = (type?: string | null): string =>
  DOC_TYPE_LABELS[type ?? ''] ?? 'Unclassified';

const CLIENT_STATUS_LABELS: Record<string, string> = {
  [ClientStatus.ON_TRACK]: 'On track',
  [ClientStatus.AWAITING_DOCUMENTS]: 'Awaiting documents',
  [ClientStatus.REVIEW_REQUIRED]: 'Review required',
  [ClientStatus.ACTION_REQUIRED]: 'Action required',
  [ClientStatus.COMPLETED]: 'Completed',
};

export const clientStatusLabel = (status?: string | null): string =>
  CLIENT_STATUS_LABELS[status ?? ''] ?? 'On track';

const WORKFLOW_STATUS_LABELS: Record<string, string> = {
  [WorkflowStatus.COLLECTING_DOCUMENTS]: 'Collecting documents',
  [WorkflowStatus.READY_FOR_REVIEW]: 'Ready for review',
  [WorkflowStatus.IN_REVIEW]: 'In review',
  [WorkflowStatus.READY_FOR_FILING]: 'Ready for filing',
  [WorkflowStatus.COMPLETED]: 'Completed',
  [WorkflowStatus.BLOCKED]: 'Blocked',
};

export const workflowStatusLabel = (status?: string | null): string =>
  WORKFLOW_STATUS_LABELS[status ?? ''] ?? 'Collecting documents';

export const formatInr = (value?: number | null): string =>
  value != null ? value.toLocaleString('en-IN') : '0';

export const formatRupees = (value?: number | null): string =>
  value != null ? `₹${value.toLocaleString('en-IN')}` : '₹0';

const parseDate = (value?: string | null): Date | null => {
  if (!value) return null;
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
};

export const formatDate = (value?: string | null): string => {
  const d = parseDate(value);
  return d
    ? d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    : '';
};

export const formatDateTime = (value?: string | null): string => {
  const d = parseDate(value);
  return d
    ? d.toLocaleString('en-GB', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : '';
};

/** "25 Sep to 25 Oct 2026". The end date carries the year unless the years differ. */
export const formatPeriod = (start?: string | null, end?: string | null): string => {
  const s = parseDate(start);
  const e = parseDate(end);
  if (!s || !e) return '';
  const short = (d: Date) => d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
  const full = (d: Date) => formatDate(d.toISOString());
  return s.getFullYear() === e.getFullYear()
    ? `${short(s)} to ${full(e)}`
    : `${full(s)} to ${full(e)}`;
};

export const formatConfidence = (value?: number | null): string =>
  value == null ? 'Not recorded' : `${(value * 100).toFixed(1)}%`;
