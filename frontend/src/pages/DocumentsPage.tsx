import React, { useState } from 'react';
import { Eye, FileCheck, Filter, Search, Upload } from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { useDrawer } from '../contexts/DrawerContext';
import { DocumentUploader } from '../components/documents/DocumentUploader';
import styles from './DashboardPage.module.css';
import docStyles from './DocumentsPage.module.css';

export const DocumentsPage: React.FC = () => {
  const { openDrawer } = useDrawer();
  const [showUploader, setShowUploader] = useState(false);

  const mockDocs = [
    { id: '1', name: 'Invoice_INV-1023.pdf', type: 'Invoice', client: 'ABC Traders', confidence: '98.6%', status: 'validated', date: '13 Apr 2025' },
    { id: '2', name: 'Rent_Bill_XYZ.pdf', type: 'Invoice', client: 'XYZ Industries', confidence: '94.2%', status: 'needs_review', date: '12 Apr 2025' },
    { id: '3', name: 'HDFC_Bank_Statement.pdf', type: 'Bank Statement', client: 'ABC Traders', confidence: '99.1%', status: 'validated', date: '10 Apr 2025' },
    { id: '4', name: 'Purchase_Bill_5678.pdf', type: 'Invoice', client: 'PQR Pvt Ltd', confidence: '72.0%', status: 'needs_review', date: '09 Apr 2025' },
    { id: '5', name: 'GSTR_2B_April.json', type: 'GST Return', client: 'ABC Traders', confidence: '100%', status: 'validated', date: '05 Apr 2025' },
  ];

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
        <DocumentUploader onSuccess={() => { setShowUploader(false); openDrawer(); }} />
      )}

      <div className={styles.cardSection}>
        <div className={styles.cardHeader}>
          <div className={styles.titleArea}>
            <h3 className={styles.cardTitle}>All Extracted Documents ({mockDocs.length})</h3>
            <span className={styles.cardSubtitle}>OCR layout blocks, JSON metadata, and extracted business objects</span>
          </div>
          <div className={styles.headerActions}>
            <button className={styles.actionBtn}>
              <Filter size={12} />
              Filter
            </button>
            <div className={styles.searchBox}>
              <Search size={12} />
              <input type="text" className={styles.searchInput} placeholder="Search documents..." />
            </div>
          </div>
        </div>

        <div className={styles.tableContainer}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Document Name</th>
                <th>Type</th>
                <th>Client</th>
                <th>OCR Confidence</th>
                <th>Status</th>
                <th>Uploaded</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {mockDocs.map((doc) => (
                <tr key={doc.id} onClick={openDrawer}>
                  <td>
                    <div className={docStyles.docName}>
                      <div className={docStyles.docIcon}>
                        <FileCheck size={13} />
                      </div>
                      <span>{doc.name}</span>
                    </div>
                  </td>
                  <td>
                    <span className={docStyles.typeBadge}>{doc.type}</span>
                  </td>
                  <td style={{ color: '#475569' }}>{doc.client}</td>
                  <td>
                    <span className={parseFloat(doc.confidence) >= 90 ? docStyles.confHigh : docStyles.confLow}>
                      {doc.confidence}
                    </span>
                  </td>
                  <td><StatusBadge status={doc.status} /></td>
                  <td className={styles.mutedCell}>{doc.date}</td>
                  <td>
                    <button className={styles.actionBtn} onClick={(e) => { e.stopPropagation(); openDrawer(); }}>
                      <Eye size={11} />
                      <span>Inspect</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
