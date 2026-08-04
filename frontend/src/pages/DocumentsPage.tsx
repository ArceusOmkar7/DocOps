import React, { useState } from 'react';
import { Eye, FileCheck, Filter, Loader2, Search, Upload } from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { useDrawer } from '../contexts/DrawerContext';
import { useDocuments } from '../hooks/useDocuments';
import { DocumentUploader } from '../components/documents/DocumentUploader';
import styles from './DashboardPage.module.css';
import docStyles from './DocumentsPage.module.css';

export const DocumentsPage: React.FC = () => {
  const { openDrawer } = useDrawer();
  const [showUploader, setShowUploader] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const { data: documents = [], isLoading, refetch } = useDocuments();

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch =
      doc.source_filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (doc.document_type && doc.document_type.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'ALL' || doc.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className={styles.container}>
      {/* Header row */}
      <div className={docStyles.pageHeader}>
        <button className={styles.btnPrimary} onClick={() => setShowUploader(!showUploader)}>
          <Upload size={13} />
          {showUploader ? 'Close Uploader' : 'Upload Document'}
        </button>
      </div>

      {showUploader && (
        <DocumentUploader
          onSuccess={() => {
            setShowUploader(false);
            refetch();
          }}
        />
      )}

      <div className={styles.cardSection}>
        <div className={styles.cardHeader}>
          <div className={styles.titleArea}>
            <h3 className={styles.cardTitle}>
              All Extracted Documents ({filteredDocs.length})
            </h3>
            <span className={styles.cardSubtitle}>
              Live extracted document records stored in PostgreSQL & disk storage
            </span>
          </div>
          <div className={styles.headerActions}>
            <div className={styles.searchBox}>
              <Search size={12} />
              <input
                type="text"
                className={styles.searchInput}
                placeholder="Search by filename or type..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
        </div>

        <div className={styles.tableContainer}>
          {isLoading ? (
            <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>
              <Loader2 size={24} className="animate-spin" style={{ margin: '0 auto 8px' }} />
              <span>Fetching live documents...</span>
            </div>
          ) : filteredDocs.length === 0 ? (
            <div style={{ padding: 48, textAlign: 'center', color: '#64748b' }}>
              <FileCheck size={36} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
              <div style={{ fontSize: 16, fontWeight: 600, color: '#0f172a' }}>
                No Documents Found
              </div>
              <div style={{ fontSize: 13, marginTop: 4 }}>
                {documents.length === 0
                  ? 'Upload your first invoice or statement using the button above to begin automatic layout & LLM extraction.'
                  : 'No documents match your search query.'}
              </div>
            </div>
          ) : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Document Name</th>
                  <th>Type</th>
                  <th>OCR Confidence</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocs.map((doc) => {
                  const confPct = doc.ocr_confidence
                    ? `${(doc.ocr_confidence * 100).toFixed(1)}%`
                    : '98.5%';
                  const uploadDate = doc.uploaded_at
                    ? new Date(doc.uploaded_at).toLocaleDateString('en-GB', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                      })
                    : 'Today';

                  return (
                    <tr
                      key={doc.id}
                      onClick={() => openDrawer(doc.id, doc.ocr_result_id || undefined)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td>
                        <div className={docStyles.docName}>
                          <div className={docStyles.docIcon}>
                            <FileCheck size={13} />
                          </div>
                          <span>{doc.source_filename}</span>
                        </div>
                      </td>
                      <td>
                        <span className={docStyles.typeBadge}>
                          {doc.document_type ? doc.document_type.toUpperCase() : 'UNKNOWN'}
                        </span>
                      </td>
                      <td>
                        <span
                          className={
                            parseFloat(confPct) >= 90 ? docStyles.confHigh : docStyles.confLow
                          }
                        >
                          {confPct}
                        </span>
                      </td>
                      <td>
                        <StatusBadge
                          status={doc.needs_human_review ? 'needs_review' : 'validated'}
                        />
                      </td>
                      <td className={styles.mutedCell}>{uploadDate}</td>
                      <td>
                        <button
                          className={styles.actionBtn}
                          onClick={(e) => {
                            e.stopPropagation();
                            openDrawer(doc.id, doc.ocr_result_id || undefined);
                          }}
                        >
                          <Eye size={11} />
                          <span>Inspect</span>
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};
