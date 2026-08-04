import React, { useState } from 'react';
import {
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  Download,
  Eye,
  X,
} from 'lucide-react';
import { StatusBadge } from '../common/StatusBadge';
import { DocumentExtraction } from '../../types/api';
import { DEMO_INVOICE_EXTRACTION } from '../../data/demoData';
import styles from './DocumentDrawer.module.css';

interface DocumentDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  extraction?: DocumentExtraction | null;
}

type Tab = 'overview' | 'preview' | 'ocr' | 'raw' | 'history';

export const DocumentDrawer: React.FC<DocumentDrawerProps> = ({
  isOpen,
  onClose,
  extraction = DEMO_INVOICE_EXTRACTION,
}) => {
  const [activeTab, setActiveTab] = useState<Tab>('overview');

  if (!isOpen) return null;

  const data = extraction || DEMO_INVOICE_EXTRACTION;
  const doc = data.document;
  const inv = data.invoice;
  const confidencePct = doc.ocr_confidence ? (doc.ocr_confidence * 100).toFixed(1) + '%' : '98.6%';

  const TABS: { key: Tab; label: string }[] = [
    { key: 'overview', label: 'Overview' },
    { key: 'preview', label: 'Preview' },
    { key: 'ocr', label: 'OCR' },
    { key: 'raw', label: 'Raw Data' },
    { key: 'history', label: 'History' },
  ];

  return (
    <div className={styles.drawer} onClick={(e) => e.stopPropagation()}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.titleArea}>
          <span className={styles.filename}>{doc.source_filename}</span>
          <StatusBadge status={doc.needs_human_review ? 'needs_review' : 'validated'} />
        </div>
        <div className={styles.headerActions}>
          <button className={styles.iconBtn} title="Download"><Download size={14} /></button>
          <button className={styles.iconBtn} onClick={onClose} title="Close"><X size={14} /></button>
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
        {activeTab === 'overview' && (
          <>
            {/* Document Info */}
            <div className={styles.section}>
              <div className={styles.sectionHeader}>Document Info</div>
              <div className={styles.infoGrid}>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>Type</span>
                  <span className={styles.infoValue}>{doc.document_type.toUpperCase()}</span>
                </div>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>Confidence Score</span>
                  <span className={styles.infoValueHighlight}>{confidencePct}</span>
                </div>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>Invoice</span>
                  <span className={styles.infoValue}>{inv?.invoice_number || 'INV-1023'}</span>
                </div>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>Extraction Model</span>
                  <span className={styles.infoValue}>gpt-oss-20b</span>
                </div>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>Invoice Date</span>
                  <span className={styles.infoValue}>{inv?.invoice_date || '13 Apr 2025'}</span>
                </div>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>Processed At</span>
                  <span className={styles.infoValue}>13 Apr 2025, 10:42 AM</span>
                </div>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>Due Date</span>
                  <span className={styles.infoValue}>{inv?.due_date || '28 Apr 2025'}</span>
                </div>
                <div className={styles.infoItem}>
                  <span className={styles.infoLabel}>Processed By</span>
                  <span className={styles.infoValue}>AI Extraction + Validation</span>
                </div>
              </div>
            </div>

            {/* Entities */}
            <div className={styles.section}>
              <div className={styles.sectionHeader}>Entities</div>
              <div className={styles.entityGrid}>
                <div className={styles.entityCard}>
                  <span className={styles.entityRole}>Seller</span>
                  <span className={styles.entityName}>{inv?.seller?.name || 'ABC Traders Pvt Ltd'}</span>
                  <span className={styles.entityMeta}>GSTIN: {inv?.seller?.tax_id || '27ABCDE1234F125'}</span>
                  <span className={styles.entityMeta}>{inv?.seller?.address?.city || 'Mumbai'}, {inv?.seller?.address?.state || 'Maharashtra'}, India</span>
                  <span className={styles.entityMeta}>{inv?.seller?.email || 'contact@abctraders.com'}</span>
                  <span className={styles.entityMeta}>{inv?.seller?.phone || '+91 98765 43210'}</span>
                </div>
                <div className={styles.entityCard}>
                  <span className={styles.entityRole}>Buyer</span>
                  <span className={styles.entityName}>{inv?.buyer?.name || 'XYZ Industries'}</span>
                  <span className={styles.entityMeta}>GSTIN: {inv?.buyer?.tax_id || '27X72A85678O722'}</span>
                  <span className={styles.entityMeta}>{inv?.buyer?.address?.city || 'Pune'}, {inv?.buyer?.address?.state || 'Maharashtra'}, India</span>
                  <span className={styles.entityMeta}>{inv?.buyer?.email || 'accounts@sysindustries.com'}</span>
                  <span className={styles.entityMeta}>{inv?.buyer?.phone || '+91 91234 56789'}</span>
                </div>
              </div>
            </div>

            {/* Line Items */}
            <div className={styles.section}>
              <div className={styles.sectionHeader}>Line Items ({inv?.items?.length || 3})</div>
              <div className={styles.tableWrapper}>
                <table className={styles.table}>
                  <thead>
                    <tr>
                      <th style={{ width: 36 }}>#</th>
                      <th>Description</th>
                      <th style={{ textAlign: 'center' }}>Qty</th>
                      <th style={{ textAlign: 'right' }}>Unit Price</th>
                      <th style={{ textAlign: 'right' }}>Amount</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(inv?.items || []).map((item, idx) => (
                      <tr key={idx}>
                        <td style={{ color: '#94a3b8', fontSize: 11 }}>{idx + 1}</td>
                        <td style={{ fontWeight: 500, color: '#0f172a' }}>{item.description}</td>
                        <td style={{ textAlign: 'center' }}>{item.quantity}</td>
                        <td style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>₹{item.unit_price?.toLocaleString('en-IN')}</td>
                        <td style={{ textAlign: 'right', fontWeight: 600, whiteSpace: 'nowrap', color: '#0f172a' }}>₹{item.line_total?.toLocaleString('en-IN')}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Taxes + Summary side by side */}
            <div className={styles.section}>
              <div className={styles.taxSummaryGrid}>
                <div className={styles.taxBlock}>
                  <div className={styles.taxBlockTitle}>Taxes</div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '6px 8px' }}>
                    <span style={{ fontSize: 10.5, fontWeight: 700, color: '#94a3b8' }}>Type</span>
                    <span style={{ fontSize: 10.5, fontWeight: 700, color: '#94a3b8' }}>Rate</span>
                    <span style={{ fontSize: 10.5, fontWeight: 700, color: '#94a3b8', textAlign: 'right' }}>Amount</span>
                    
                    <span style={{ fontSize: 12, color: '#334155' }}>CGST</span>
                    <span style={{ fontSize: 12, color: '#334155' }}>9%</span>
                    <span style={{ fontSize: 12, color: '#0f172a', fontWeight: 500, textAlign: 'right' }}>₹{inv?.tax?.cgst?.toLocaleString('en-IN') || '7,563'}</span>
                    
                    <span style={{ fontSize: 12, color: '#334155' }}>SGST</span>
                    <span style={{ fontSize: 12, color: '#334155' }}>9%</span>
                    <span style={{ fontSize: 12, color: '#0f172a', fontWeight: 500, textAlign: 'right' }}>₹{inv?.tax?.sgst?.toLocaleString('en-IN') || '7,563'}</span>
                  </div>
                </div>
                <div className={styles.summaryBlock}>
                  <div className={styles.taxBlockTitle}>Summary</div>
                  <div className={styles.summaryRow}>
                    <span>Subtotal</span>
                    <span>₹{inv?.subtotal?.toLocaleString('en-IN') || '84,000'}</span>
                  </div>
                  <div className={styles.summaryRow}>
                    <span>Total Tax</span>
                    <span>₹{inv?.total_tax?.toLocaleString('en-IN') || '15,126'}</span>
                  </div>
                  <div className={styles.summaryRow}>
                    <span>Granted Off</span>
                    <span>₹0.00</span>
                  </div>
                  <div className={styles.totalRow}>
                    <span>Grand Total</span>
                    <span>₹{inv?.total?.toLocaleString('en-IN') || '99,126'}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Alert Banner */}
            <div className={styles.alertBanner}>
              <AlertTriangle size={15} className={styles.alertIcon} />
              <div className={styles.alertContent}>
                <strong className={styles.alertTitle}>Business Review: Please verify totals</strong>
                Calculated total (₹{inv?.total?.toLocaleString('en-IN') || '99,126'}) matches extracted total.
              </div>
              <button className={styles.alertViewBtn}>View Details</button>
            </div>
          </>
        )}

        {activeTab === 'preview' && (
          <div className={styles.emptyState}>
            <Eye size={36} />
            <span className={styles.emptyTitle}>Visual Bounding Box Preview</span>
            <span>OCR region overlay rendering for {doc.source_filename}</span>
          </div>
        )}

        {activeTab === 'ocr' && (
          <pre className={styles.rawBlock}>{doc.raw_markdown || '# OCR Raw Markdown\n\nBlock 1: INVOICE\nBlock 2: ABC Traders Pvt Ltd\n...'}</pre>
        )}

        {activeTab === 'raw' && (
          <pre className={styles.rawBlock}>{JSON.stringify(data, null, 2)}</pre>
        )}

        {activeTab === 'history' && (
          <div className={styles.section}>
            <div className={styles.sectionHeader}>Audit Trail</div>
            <div style={{ padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 10 }}>
              {[
                '✓ Uploaded to system — 13 Apr 2025, 10:41 AM',
                '✓ PaddleOCR Layout parsed 14 region blocks — 10:41 AM',
                '✓ LLM Extracted Invoice object — 10:42 AM',
                '✓ Business math checks passed — 10:42 AM',
              ].map((entry, i) => (
                <div key={i} style={{ fontSize: 12.5, color: '#475569', display: 'flex', gap: 8 }}>
                  <span style={{ color: '#16a34a', flexShrink: 0 }}>✓</span>
                  <span>{entry.replace('✓ ', '')}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className={styles.footer}>
        <button className={styles.btnApprove}>
          <CheckCircle size={13} />
          Approve
        </button>
        <button className={styles.btnSecondary}>
          <CheckCircle size={13} />
          Send for Review
        </button>
        <button className={styles.moreBtn}>
          More Actions <ChevronDown size={12} />
        </button>
      </div>
    </div>
  );
};
