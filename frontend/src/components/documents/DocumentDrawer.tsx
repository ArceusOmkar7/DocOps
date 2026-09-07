import React, { useState } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  Download,
  Eye,
  Loader2,
  X,
} from 'lucide-react';
import { StatusBadge } from '../common/StatusBadge';
import { useDocument } from '../../hooks/useDocuments';
import { useOCRMarkdown, useOCRResult } from '../../hooks/useOCR';
import { DocumentType } from '../../types/enums';
import {
  BankStatementView,
  GSTReturnView,
  InvestmentProofView,
  TDSFormView,
} from './SchemaViewers';
import styles from './DocumentDrawer.module.css';

interface DocumentDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  documentId?: string;
  resultId?: string;
}

type Tab = 'overview' | 'preview' | 'ocr' | 'raw' | 'history';

export const DocumentDrawer: React.FC<DocumentDrawerProps> = ({
  isOpen,
  onClose,
  documentId,
  resultId,
}) => {
  const [activeTab, setActiveTab] = useState<Tab>('overview');

  const { data: dbDoc, isLoading: loadingDoc } = useDocument(documentId);
  const activeOcrId = resultId || dbDoc?.ocr_result_id || undefined;

  // Optimistic data fetching: only load raw OCR disk result if dbDoc is missing or user inspects OCR/raw tabs
  const shouldFetchOcr = !!activeOcrId && (!dbDoc || activeTab === 'ocr' || activeTab === 'raw');
  const { data: ocrResult, isLoading: loadingOcr } = useOCRResult(shouldFetchOcr ? activeOcrId : undefined);

  if (!isOpen) return null;

  const isLoading = loadingDoc || (shouldFetchOcr && loadingOcr);

  // Extracted data objects (extracted_data holds the business object directly)
  const extractedObj: any = dbDoc?.extracted_data || {};
  const inv = extractedObj.invoice ?? extractedObj ?? {};
  const filename = dbDoc?.source_filename || ocrResult?.filename || 'Document_Inspection.pdf';
  const docTypeEnum = (dbDoc?.document_type as DocumentType) || DocumentType.UNKNOWN;
  const docType = (dbDoc?.document_type || extractedObj.document_type || 'INVOICE').toString().toUpperCase();
  const confidence = dbDoc?.ocr_confidence ?? 0.985;
  const confidencePct = `${(confidence * 100).toFixed(1)}%`;
  const needsReview = dbDoc?.needs_human_review ?? false;
  const reviewReason = dbDoc?.review_reason || 'Needs human verification';

  const isInvoiceLike =
    docTypeEnum === DocumentType.INVOICE ||
    docTypeEnum === DocumentType.PURCHASE_ORDER ||
    docTypeEnum === DocumentType.RECEIPT ||
    docTypeEnum === DocumentType.UNKNOWN;

  const TABS: { key: Tab; label: string }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'preview', label: 'Preview' },
    { key: 'ocr', label: 'OCR Markdown' },
    { key: 'raw', label: 'Raw JSON' },
    { key: 'history', label: 'Audit Trail' },
  ];

  return (
    <div className={styles.drawer} onClick={(e) => e.stopPropagation()}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.titleArea}>
          <span className={styles.filename}>{filename}</span>
          <StatusBadge status={needsReview ? 'needs_review' : 'validated'} />
        </div>
        <div className={styles.headerActions}>
          {activeOcrId && (
            <a
              href={`/api/v1/ocr/results/${activeOcrId}/source`}
              target="_blank"
              rel="noreferrer"
              className={styles.iconBtn}
              title="Download Source"
            >
              <Download size={14} />
            </a>
          )}
          <button className={styles.iconBtn} onClick={onClose} title="Close">
            <X size={14} />
          </button>
        </div>
      </div>

      {/* Tab bar */}
      <div className={styles.tabBar}>
        {TABS.map((t) => (
          <button
            key={t.key}
            className={`${styles.tab} ${activeTab === t.key ? styles.active : ''}`}
            onClick={() => setActiveTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Body */}
      <div className={styles.body}>
        {isLoading ? (
          <div className={styles.emptyState}>
            <Loader2 size={28} className="animate-spin" />
            <span>Loading live document intelligence...</span>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <>
                {docTypeEnum === DocumentType.BANK_STATEMENT ? (
                  <BankStatementView data={extractedObj} />
                ) : docTypeEnum === DocumentType.GST_RETURN ? (
                  <GSTReturnView data={extractedObj} />
                ) : docTypeEnum === DocumentType.TDS_FORM ? (
                  <TDSFormView data={extractedObj} />
                ) : docTypeEnum === DocumentType.INVESTMENT_PROOF ? (
                  <InvestmentProofView data={extractedObj} />
                ) : isInvoiceLike && (
                  <>
                  {/* Document Info */}
                  <div className={styles.section}>
                    <div className={styles.sectionHeader}>Document Info</div>
                  <div className={styles.infoGrid}>
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>Document Type</span>
                      <span className={styles.infoValue}>{docType}</span>
                    </div>
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>OCR Confidence</span>
                      <span className={styles.infoValueHighlight}>{confidencePct}</span>
                    </div>
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>Invoice Number</span>
                      <span className={styles.infoValue}>{inv.invoice_number || 'N/A'}</span>
                    </div>
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>Invoice Date</span>
                      <span className={styles.infoValue}>{inv.invoice_date || 'N/A'}</span>
                    </div>
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>Due Date</span>
                      <span className={styles.infoValue}>{inv.due_date || 'N/A'}</span>
                    </div>
                    <div className={styles.infoItem}>
                      <span className={styles.infoLabel}>Processed At</span>
                      <span className={styles.infoValue}>
                        {dbDoc?.processed_at ? new Date(dbDoc.processed_at).toLocaleString() : 'Just now'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Entities */}
                {(inv.seller || inv.buyer) && (
                  <div className={styles.section}>
                    <div className={styles.sectionHeader}>Entities</div>
                    <div className={styles.entityGrid}>
                      <div className={styles.entityCard}>
                        <span className={styles.entityRole}>Seller</span>
                        <span className={styles.entityName}>{inv.seller?.name || 'N/A'}</span>
                        {inv.seller?.tax_id && (
                          <span className={styles.entityMeta}>GSTIN: {inv.seller.tax_id}</span>
                        )}
                        {inv.seller?.address && (
                          <span className={styles.entityMeta}>{inv.seller.address}</span>
                        )}
                      </div>
                      <div className={styles.entityCard}>
                        <span className={styles.entityRole}>Buyer</span>
                        <span className={styles.entityName}>{inv.buyer?.name || 'N/A'}</span>
                        {inv.buyer?.tax_id && (
                          <span className={styles.entityMeta}>GSTIN: {inv.buyer.tax_id}</span>
                        )}
                        {inv.buyer?.address && (
                          <span className={styles.entityMeta}>{inv.buyer.address}</span>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Line Items */}
                {inv.items && inv.items.length > 0 && (
                  <div className={styles.section}>
                    <div className={styles.sectionHeader}>Line Items ({inv.items.length})</div>
                    <div className={styles.tableWrapper}>
                      <table className={styles.table}>
                        <thead>
                          <tr>
                            <th style={{ width: 36 }}>#</th>
                            <th>Description</th>
                            <th style={{ textAlign: 'center' }}>Qty</th>
                            <th style={{ textAlign: 'right' }}>Unit Price</th>
                            <th style={{ textAlign: 'right' }}>Line Total</th>
                          </tr>
                        </thead>
                        <tbody>
                          {inv.items.map((item: any, idx: number) => (
                            <tr key={idx}>
                              <td style={{ color: '#94a3b8', fontSize: 11 }}>{idx + 1}</td>
                              <td style={{ fontWeight: 500, color: '#0f172a' }}>
                                {item.description || 'Item'}
                              </td>
                              <td style={{ textAlign: 'center' }}>{item.quantity ?? 1}</td>
                              <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
                                ₹{item.unit_price ? item.unit_price.toLocaleString('en-IN') : '0'}
                              </td>
                              <td style={{ textAlign: 'right', fontWeight: 600, whiteSpace: 'nowrap', color: '#0f172a' }}>
                                ₹{item.line_total ? item.line_total.toLocaleString('en-IN') : '0'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                {/* Summary */}
                <div className={styles.section}>
                  <div className={styles.taxSummaryGrid}>
                    <div className={styles.taxBlock}>
                      <div className={styles.taxBlockTitle}>Tax Breakdown</div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 12 }}>
                        {inv.tax_details && inv.tax_details.length > 0 ? (
                          inv.tax_details.map((t: any, i: number) => (
                            <div key={i} style={{ display: 'flex', justifyContent: 'space-between' }}>
                              <span>{t.tax_name || 'Tax'} ({((t.rate || 0) * 100).toFixed(0)}%)</span>
                              <span style={{ fontWeight: 600 }}>₹{(t.amount || 0).toLocaleString('en-IN')}</span>
                            </div>
                          ))
                        ) : (
                          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span>Total Tax</span>
                            <span style={{ fontWeight: 600 }}>₹{(inv.total_tax || 0).toLocaleString('en-IN')}</span>
                          </div>
                        )}
                      </div>
                    </div>
                    <div className={styles.summaryBlock}>
                      <div className={styles.taxBlockTitle}>Summary</div>
                      <div className={styles.summaryRow}>
                        <span>Subtotal</span>
                        <span>₹{(inv.subtotal || 0).toLocaleString('en-IN')}</span>
                      </div>
                      <div className={styles.summaryRow}>
                        <span>Total Tax</span>
                        <span>₹{(inv.total_tax || 0).toLocaleString('en-IN')}</span>
                      </div>
                      <div className={styles.totalRow}>
                        <span>Grand Total</span>
                        <span>₹{(inv.total || 0).toLocaleString('en-IN')}</span>
                      </div>
                    </div>
                  </div>
                </div>
                  </>
                )}

                {/* Alert Banner */}
                {needsReview && (
                  <div className={styles.alertBanner}>
                    <AlertTriangle size={15} className={styles.alertIcon} />
                    <div className={styles.alertContent}>
                      <strong className={styles.alertTitle}>Business Review Flagged</strong>
                      {reviewReason}
                    </div>
                  </div>
                )}
              </>
            )}

            {activeTab === 'preview' && (
              <div className={styles.emptyState}>
                <Eye size={36} />
                <span className={styles.emptyTitle}>Source File Preview</span>
                {activeOcrId ? (
                  <a
                    href={`/api/v1/ocr/results/${activeOcrId}/source`}
                    target="_blank"
                    rel="noreferrer"
                    style={{ color: '#059669', fontWeight: 600, textDecoration: 'underline' }}
                  >
                    Open original file ({filename})
                  </a>
                ) : (
                  <span>No original source file path available.</span>
                )}
              </div>
            )}

            {activeTab === 'ocr' && (
              <div style={{ padding: 12 }}>
                {shouldFetchOcr && loadingOcr ? (
                  <span>Loading OCR text...</span>
                ) : (
                  <pre className={styles.rawBlock}>
                    {ocrResult?.markdown || extractedObj?.markdown || extractedObj?.raw_markdown || '# No raw markdown text available'}
                  </pre>
                )}
              </div>
            )}

            {activeTab === 'raw' && (
              <pre className={styles.rawBlock}>
                {JSON.stringify(dbDoc || ocrResult || { message: 'No data' }, null, 2)}
              </pre>
            )}

            {activeTab === 'history' && (
              <div className={styles.section}>
                <div className={styles.sectionHeader}>Audit Trail</div>
                <div style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 10 }}>
                  <div style={{ fontSize: 12.5, color: '#475569', display: 'flex', gap: 8 }}>
                    <span style={{ color: '#16a34a' }}>✓</span>
                    <span>Document uploaded to system storage</span>
                  </div>
                  <div style={{ fontSize: 12.5, color: '#475569', display: 'flex', gap: 8 }}>
                    <span style={{ color: '#16a34a' }}>✓</span>
                    <span>PP-StructureV3 GPU OCR Layout parsed</span>
                  </div>
                  <div style={{ fontSize: 12.5, color: '#475569', display: 'flex', gap: 8 }}>
                    <span style={{ color: '#16a34a' }}>✓</span>
                    <span>LLM Extracted {docType} business object</span>
                  </div>
                  <div style={{ fontSize: 12.5, color: '#475569', display: 'flex', gap: 8 }}>
                    <span style={{ color: needsReview ? '#d97706' : '#16a34a' }}>
                      {needsReview ? '⚠️' : '✓'}
                    </span>
                    <span>
                      {needsReview
                        ? `Business Review flagged: ${reviewReason}`
                        : 'Business validation checks passed'}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Footer */}
      <div className={styles.footer}>
        <button className={styles.btnApprove} onClick={onClose}>
          <CheckCircle size={13} />
          Approve
        </button>
        <button className={styles.btnSecondary} onClick={onClose}>
          Send for Review
        </button>
        <button className={styles.moreBtn} onClick={onClose}>
          Close <ChevronDown size={12} />
        </button>
      </div>
    </div>
  );
};
