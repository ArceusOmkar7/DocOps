import React, { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { Search, Upload, X } from 'lucide-react';
import { DocumentUploader } from '../components/documents/DocumentUploader';
import { ErrorState } from '../components/common/ErrorState';
import { PageHeader } from '../components/common/PageHeader';
import { StatusBadge, Tone } from '../components/common/StatusBadge';
import { useDrawer } from '../contexts/DrawerContext';
import { useClients } from '../hooks/useClients';
import { useDocuments } from '../hooks/useDocuments';
import { documentTypeLabel, formatConfidence, formatDate } from '../lib/format';
import { DocBucket, documentBucket } from '../lib/readiness';
import ui from '../styles/ui.module.css';
import styles from './DocumentsPage.module.css';

const BUCKET_BADGE: Record<DocBucket, { label: string; tone: Tone }> = {
  validated: { label: 'Validated', tone: 'ok' },
  review: { label: 'Needs review', tone: 'warn' },
  failed: { label: 'Failed', tone: 'bad' },
  pending: { label: 'Pending', tone: 'idle' },
};

export const DocumentsPage: React.FC = () => {
  const { openDrawer } = useDrawer();
  const [params, setParams] = useSearchParams();
  const [showUploader, setShowUploader] = useState(params.get('upload') === '1');
  const [query, setQuery] = useState('');

  const clientFilter = params.get('client') ?? '';
  const showFilter = params.get('show') ?? 'all';

  const { data: documents = [], isLoading, isError, refetch } = useDocuments();
  const { data: clients = [] } = useClients();

  const clientName = useMemo(() => new Map(clients.map((c) => [c.id, c.name])), [clients]);

  const setParam = (key: string, value: string | null) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next, { replace: true });
  };

  const q = query.trim().toLowerCase();
  const visible = documents.filter((doc) => {
    if (clientFilter && doc.client_id !== clientFilter) return false;
    if (showFilter !== 'all' && documentBucket(doc) !== showFilter) return false;
    if (!q) return true;
    return (
      doc.source_filename.toLowerCase().includes(q) ||
      documentTypeLabel(doc.document_type).toLowerCase().includes(q) ||
      (clientName.get(doc.client_id) ?? '').toLowerCase().includes(q)
    );
  });

  return (
    <div className={ui.page}>
      <PageHeader
        title="Documents"
        actions={
          <button className={ui.btnPrimary} onClick={() => setShowUploader(!showUploader)}>
            {showUploader ? (
              <X size={15} strokeWidth={1.75} aria-hidden="true" />
            ) : (
              <Upload size={15} strokeWidth={1.75} aria-hidden="true" />
            )}
            {showUploader ? 'Close upload' : 'Upload document'}
          </button>
        }
      />

      {showUploader && (
        <DocumentUploader
          clientId={clientFilter || undefined}
          onSuccess={() => {
            setShowUploader(false);
            refetch();
          }}
        />
      )}

      <section className={ui.panel} aria-label="Document register">
        <div className={ui.panelHead}>
          <h2 className={ui.panelTitle}>
            {clientFilter && clientName.get(clientFilter)
              ? clientName.get(clientFilter)
              : 'All documents'}
            <span className={ui.panelCount}>{visible.length}</span>
          </h2>
          <div className={ui.tools}>
            {clientFilter && (
              <button className={ui.btnQuiet} onClick={() => setParam('client', null)}>
                <X size={14} strokeWidth={1.75} aria-hidden="true" />
                Show all clients
              </button>
            )}
            <label className={ui.search}>
              <Search size={14} className={ui.searchIcon} aria-hidden="true" />
              <input
                type="search"
                className={ui.input}
                placeholder="Search file, type or client"
                aria-label="Search documents"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
            </label>
            <select
              className={ui.select}
              aria-label="Filter by status"
              value={showFilter}
              onChange={(e) => setParam('show', e.target.value === 'all' ? null : e.target.value)}
            >
              <option value="all">All statuses</option>
              <option value="review">Needs review</option>
              <option value="failed">Failed</option>
              <option value="pending">Pending</option>
              <option value="validated">Validated</option>
            </select>
          </div>
        </div>

        {isError ? (
          <ErrorState what="documents" />
        ) : isLoading ? (
          <div className={ui.empty} aria-busy="true">
            <div className={ui.skeletonRow} style={{ width: '60%' }} />
          </div>
        ) : visible.length === 0 ? (
          <div className={ui.empty}>
            <span className={ui.emptyTitle}>
              {documents.length === 0 ? 'No documents yet' : 'No documents match'}
            </span>
            <span className={ui.emptyText}>
              {documents.length === 0
                ? 'Upload a PDF or image and Patra will read it, classify it and check the figures.'
                : 'Clear the search or the filters to see more.'}
            </span>
            {documents.length > 0 && clientFilter && (
              <Link to="/documents" className={ui.btn} style={{ marginTop: 8 }}>
                Show all documents
              </Link>
            )}
          </div>
        ) : (
          <div className={ui.tableWrap}>
            <table className={ui.table}>
              <thead>
                <tr>
                  <th scope="col">File</th>
                  <th scope="col">Type</th>
                  <th scope="col">Client</th>
                  <th scope="col" className={`${ui.num} ${ui.hideNarrow}`}>OCR confidence</th>
                  <th scope="col">Status</th>
                  <th scope="col" className={ui.hideNarrow}>Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {visible.map((doc) => {
                  const badge = BUCKET_BADGE[documentBucket(doc)];
                  return (
                    <tr
                      key={doc.id}
                      className={ui.rowLink}
                      onClick={() => openDrawer(doc.id, doc.ocr_result_id || undefined)}
                    >
                      <td>
                        <button
                          className={`${ui.primaryCell} ${styles.fileName}`}
                          onClick={(e) => {
                            e.stopPropagation();
                            openDrawer(doc.id, doc.ocr_result_id || undefined);
                          }}
                        >
                          {doc.source_filename}
                        </button>
                      </td>
                      <td>{documentTypeLabel(doc.document_type)}</td>
                      <td className={ui.clipCell}>{clientName.get(doc.client_id) ?? <span className={ui.muted}>Unknown</span>}</td>
                      <td className={`${ui.num} ${ui.hideNarrow}`}>{formatConfidence(doc.ocr_confidence)}</td>
                      <td>
                        <StatusBadge status={doc.status} label={badge.label} tone={badge.tone} />
                      </td>
                      <td className={`${ui.muted} ${ui.hideNarrow}`} style={{ whiteSpace: 'nowrap' }}>
                        {formatDate(doc.uploaded_at)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};
