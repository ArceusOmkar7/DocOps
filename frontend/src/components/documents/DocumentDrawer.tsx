import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Download, X } from 'lucide-react';
import { StatusBadge, Tone } from '../common/StatusBadge';
import { useDocument } from '../../hooks/useDocuments';
import { useOCRResult } from '../../hooks/useOCR';
import { DocumentType } from '../../types/enums';
import { documentBucket, DocBucket } from '../../lib/readiness';
import { documentTypeLabel, formatConfidence, formatDateTime } from '../../lib/format';
import {
  BankStatementView,
  GSTReturnView,
  InvestmentProofView,
  InvoiceView,
  TDSFormView,
} from './SchemaViewers';
import ui from '../../styles/ui.module.css';
import styles from './DocumentDrawer.module.css';

interface DocumentDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  documentId?: string;
  resultId?: string;
}

type Tab = 'overview' | 'source' | 'ocr' | 'raw' | 'history';

const TABS: { key: Tab; label: string }[] = [
  { key: 'overview', label: 'Extracted data' },
  { key: 'source', label: 'Source file' },
  { key: 'ocr', label: 'OCR text' },
  { key: 'raw', label: 'Raw data' },
  { key: 'history', label: 'History' },
];

const BUCKET_BADGE: Record<DocBucket, { label: string; tone: Tone }> = {
  validated: { label: 'Validated', tone: 'ok' },
  review: { label: 'Needs review', tone: 'warn' },
  failed: { label: 'Failed', tone: 'bad' },
  pending: { label: 'Pending', tone: 'idle' },
};

/** Fetches the stored original and shows it inline, or says it is not stored. */
const SourcePreview: React.FC<{ resultId?: string; filename: string }> = ({ resultId, filename }) => {
  const url = resultId ? `/api/v1/ocr/results/${resultId}/source` : undefined;
  const { data, isLoading } = useQuery({
    queryKey: ['source', resultId],
    enabled: !!url,
    retry: false,
    queryFn: async () => {
      const res = await fetch(url!);
      if (!res.ok) return null;
      const blob = await res.blob();
      return { href: URL.createObjectURL(blob), type: blob.type };
    },
  });

  useEffect(() => {
    const href = data?.href;
    return () => {
      if (href) URL.revokeObjectURL(href);
    };
  }, [data?.href]);

  if (isLoading) return <div className={ui.skeletonRow} style={{ height: 240 }} />;
  if (!data) {
    return (
      <p className={styles.none}>
        The original file is not stored for this document, so there is nothing to preview.
      </p>
    );
  }
  return data.type.startsWith('image/') ? (
    <img className={styles.sourceImage} src={data.href} alt={`Original file ${filename}`} />
  ) : (
    <iframe className={styles.sourceFrame} src={data.href} title={`Original file ${filename}`} />
  );
};

export const DocumentDrawer: React.FC<DocumentDrawerProps> = ({
  isOpen,
  onClose,
  documentId,
  resultId,
}) => {
  const [activeTab, setActiveTab] = useState<Tab>('overview');

  const { data: dbDoc, isLoading: loadingDoc } = useDocument(documentId);
  const activeOcrId = resultId || dbDoc?.ocr_result_id || undefined;

  // Only load the raw OCR result from disk when the document row is missing or the tab needs it
  const shouldFetchOcr = !!activeOcrId && (!dbDoc || activeTab === 'ocr' || activeTab === 'raw');
  const { data: ocrResult, isLoading: loadingOcr } = useOCRResult(
    shouldFetchOcr ? activeOcrId : undefined
  );

  useEffect(() => setActiveTab('overview'), [documentId, resultId]);

  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const isLoading = loadingDoc || (shouldFetchOcr && loadingOcr);

  const extracted: any = dbDoc?.extracted_data || {};
  const filename = dbDoc?.source_filename || ocrResult?.filename || 'Document';
  const docType = (dbDoc?.document_type as DocumentType) || DocumentType.UNKNOWN;
  const bucket = dbDoc ? documentBucket(dbDoc) : 'pending';
  const badge = BUCKET_BADGE[bucket];
  const flagged = bucket === 'review' || bucket === 'failed';
  const reviewReason = dbDoc?.review_reason || (bucket === 'failed' ? 'Extraction failed.' : 'Flagged for human review.');

  const ocrText =
    ocrResult?.markdown || dbDoc?.raw_markdown || extracted.markdown || extracted.raw_markdown || '';

  const renderOverview = () => {
    switch (docType) {
      case DocumentType.BANK_STATEMENT:
        return <BankStatementView data={extracted} />;
      case DocumentType.GST_RETURN:
        return <GSTReturnView data={extracted} />;
      case DocumentType.TDS_FORM:
        return <TDSFormView data={extracted} />;
      case DocumentType.INVESTMENT_PROOF:
        return <InvestmentProofView data={extracted} />;
      case DocumentType.UNKNOWN:
        return (
          <p className={styles.none}>
            Patra could not tell what kind of document this is, so no fields were extracted. Open
            the source file to read it.
          </p>
        );
      default:
        return <InvoiceView data={extracted.invoice ?? extracted} />;
    }
  };

  const history = [
    dbDoc?.uploaded_at && { when: dbDoc.uploaded_at, text: 'Uploaded' },
    dbDoc?.processed_at && {
      when: dbDoc.processed_at,
      text: `Read and extracted as ${documentTypeLabel(dbDoc.document_type).toLowerCase()}`,
    },
    dbDoc && flagged && {
      when: dbDoc.processed_at || dbDoc.uploaded_at,
      text: `${bucket === 'failed' ? 'Failed' : 'Flagged for review'}: ${reviewReason}`,
    },
    dbDoc && bucket === 'validated' && {
      when: dbDoc.processed_at || dbDoc.uploaded_at,
      text: 'Passed the validation checks',
    },
  ].filter(Boolean) as { when: string; text: string }[];

  return (
    <div className={styles.drawer} role="complementary" aria-label={`Document ${filename}`}>
      <header className={styles.header}>
        <div className={styles.titleBlock}>
          <h2 className={styles.filename} title={filename}>
            {filename}
          </h2>
          <p className={styles.meta}>
            {documentTypeLabel(dbDoc?.document_type)}
            {dbDoc && ` · OCR confidence ${formatConfidence(dbDoc.ocr_confidence)}`}
            {dbDoc?.processed_at && ` · Processed ${formatDateTime(dbDoc.processed_at)}`}
          </p>
        </div>
        <div className={styles.headerActions}>
          {dbDoc && <StatusBadge status={dbDoc.status} label={badge.label} tone={badge.tone} />}
          {activeOcrId && (
            <a
              href={`/api/v1/ocr/results/${activeOcrId}/source`}
              target="_blank"
              rel="noreferrer"
              className={styles.iconBtn}
              title="Download original file"
              aria-label="Download original file"
            >
              <Download size={16} strokeWidth={1.75} aria-hidden="true" />
            </a>
          )}
          <button className={styles.iconBtn} onClick={onClose} title="Close (Esc)" aria-label="Close document">
            <X size={16} strokeWidth={1.75} aria-hidden="true" />
          </button>
        </div>
      </header>

      <div className={styles.tabBar} role="tablist" aria-label="Document views">
        {TABS.map((t) => (
          <button
            key={t.key}
            role="tab"
            aria-selected={activeTab === t.key}
            className={`${styles.tab} ${activeTab === t.key ? styles.active : ''}`}
            onClick={() => setActiveTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      <div className={styles.body} role="tabpanel">
        {isLoading ? (
          <div className={styles.loading} aria-busy="true" aria-label="Loading document">
            {[70, 90, 55, 80].map((w, i) => (
              <div key={i} className={ui.skeletonRow} style={{ width: `${w}%` }} />
            ))}
          </div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <>
                {flagged && (
                  <div className={bucket === 'failed' ? styles.flagBad : styles.flag} role="note">
                    <strong>{bucket === 'failed' ? 'Extraction failed' : 'Flagged for review'}</strong>
                    <span>{reviewReason}</span>
                  </div>
                )}
                {renderOverview()}
              </>
            )}

            {activeTab === 'source' && (
              <SourcePreview resultId={activeOcrId} filename={filename} />
            )}

            {activeTab === 'ocr' &&
              (ocrText ? (
                <pre className={styles.rawBlock}>{ocrText}</pre>
              ) : (
                <p className={styles.none}>No OCR text is stored for this document.</p>
              ))}

            {activeTab === 'raw' && (
              <pre className={styles.rawBlock}>
                {JSON.stringify(dbDoc || ocrResult || { message: 'No data' }, null, 2)}
              </pre>
            )}

            {activeTab === 'history' &&
              (history.length > 0 ? (
                <ol className={styles.history}>
                  {history.map((h, i) => (
                    <li key={i}>
                      <time className={styles.historyTime}>{formatDateTime(h.when)}</time>
                      <span>{h.text}</span>
                    </li>
                  ))}
                </ol>
              ) : (
                <p className={styles.none}>No history is recorded for this document.</p>
              ))}
          </>
        )}
      </div>
    </div>
  );
};
