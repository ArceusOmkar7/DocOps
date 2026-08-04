import React, { useState } from 'react';
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Eye,
  FileCheck,
  FileText,
  FileWarning,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  Send,
  Users,
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { StatusBadge } from '../components/common/StatusBadge';
import { ProgressBar } from '../components/common/ProgressBar';
import { useDrawer } from '../contexts/DrawerContext';
import { useClients } from '../hooks/useClients';
import { useDocuments } from '../hooks/useDocuments';
import styles from './DashboardPage.module.css';

export const DashboardPage: React.FC = () => {
  const { openDrawer } = useDrawer();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const { data: clients = [], isLoading: loadingClients } = useClients();
  const { data: documents = [], isLoading: loadingDocs } = useDocuments();

  // Dynamic stat metrics calculated from real database state
  const totalClients = clients.length;
  const documentsProcessed = documents.length;
  const readyForFiling = documents.filter(
    (d) => d.status === 'validated' || d.status === 'extracted'
  ).length;
  const missingDocuments = documents.filter((d) => d.status === 'failed').length;
  const needReview = documents.filter((d) => d.needs_human_review).length;

  const filteredClients = clients.filter((c) => {
    const matchesSearch =
      c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.tax_id && c.tax_id.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className={styles.container}>
      {/* Stat Cards Grid */}
      <div className={styles.statsGrid}>
        <StatCard
          label="Total Clients"
          value={totalClients}
          trend={`${totalClients} active`}
          icon={Users}
          colorTheme="indigo"
          sparkline={[1, 2, 2, 3, 3, 3, 3, totalClients]}
        />
        <StatCard
          label="Documents Processed"
          value={documentsProcessed}
          trend={`${documentsProcessed} total`}
          icon={FileText}
          colorTheme="blue"
          sparkline={[0, 1, 2, 3, 4, documentsProcessed]}
        />
        <StatCard
          label="Ready for Filing"
          value={readyForFiling}
          trend={documentsProcessed > 0 ? `${((readyForFiling / documentsProcessed) * 100).toFixed(0)}% valid` : '0%'}
          icon={FileCheck}
          colorTheme="green"
          sparkline={[0, 1, 1, 2, readyForFiling]}
        />
        <StatCard
          label="Missing Documents"
          value={missingDocuments}
          trend={missingDocuments > 0 ? `${missingDocuments} action req` : '0 pending'}
          trendType="warning"
          icon={FileWarning}
          colorTheme="red"
          sparkline={[0, 0, missingDocuments]}
        />
        <StatCard
          label="Need Review"
          value={needReview}
          trend={needReview > 0 ? `${needReview} flagged` : 'All clear'}
          trendType="warning"
          icon={AlertTriangle}
          colorTheme="amber"
          sparkline={[0, 1, needReview]}
        />
      </div>

      {/* Clients Table Section */}
      <div className={styles.cardSection}>
        <div className={styles.cardHeader}>
          <div className={styles.titleArea}>
            <h3 className={styles.cardTitle}>Clients</h3>
            <span className={styles.cardSubtitle}>
              Live client records and filing compliance state
            </span>
          </div>

          <div className={styles.headerActions}>
            <div className={styles.searchBox}>
              <Search size={13} />
              <input
                type="text"
                className={styles.searchInput}
                placeholder="Search clients..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <select
              className={styles.filterSelect}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Status</option>
              <option value="on_track">On Track</option>
              <option value="awaiting_documents">Awaiting Documents</option>
              <option value="needs_review">Need Review</option>
              <option value="action_required">Action Required</option>
            </select>
          </div>
        </div>

        <div className={styles.tableContainer}>
          {loadingClients ? (
            <div style={{ padding: 36, textAlign: 'center', color: '#64748b' }}>
              <Loader2 size={24} className="animate-spin" style={{ margin: '0 auto 8px' }} />
              <span>Loading client state...</span>
            </div>
          ) : filteredClients.length === 0 ? (
            <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>
              <Users size={32} style={{ margin: '0 auto 8px', opacity: 0.5 }} />
              <div>No client records found.</div>
            </div>
          ) : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Client</th>
                  <th>Status</th>
                  <th>Contact Person</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredClients.map((client) => {
                  const initials = client.name
                    .split(' ')
                    .map((n) => n[0])
                    .join('')
                    .substring(0, 2)
                    .toUpperCase();

                  return (
                    <tr key={client.id} style={{ cursor: 'pointer' }}>
                      <td>
                        <div className={styles.clientCell}>
                          <div className={`${styles.avatar} ${styles.avatarIndigo}`}>
                            {initials}
                          </div>
                          <div className={styles.clientInfo}>
                            <span className={styles.clientName}>{client.name}</span>
                            <span className={styles.clientGstin}>
                              GSTN: {client.tax_id || 'N/A'}
                            </span>
                          </div>
                        </div>
                      </td>
                      <td>
                        <StatusBadge status={client.status || 'on_track'} />
                      </td>
                      <td style={{ color: '#475569' }}>{client.contact_person || 'N/A'}</td>
                      <td className={styles.mutedCell}>{client.email || 'N/A'}</td>
                      <td className={styles.mutedCell}>{client.phone || 'N/A'}</td>
                      <td>
                        <button
                          className={styles.actionBtn}
                          onClick={(e) => {
                            e.stopPropagation();
                            openDrawer();
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

        <div className={styles.tableFooter}>
          <span>
            Showing {filteredClients.length} of {totalClients} clients
          </span>
        </div>
      </div>

      {/* Recent Activity Stream */}
      <div className={styles.cardSection}>
        <div className={styles.cardHeader}>
          <div className={styles.titleArea}>
            <h3 className={styles.cardTitle}>Recent Activity</h3>
            <span className={styles.cardSubtitle}>
              Real-time OCR extraction & LLM reasoning event stream
            </span>
          </div>
        </div>

        <div className={styles.activityFeed}>
          {documents.length === 0 ? (
            <div style={{ padding: 24, color: '#64748b', fontSize: 13 }}>
              No recent activity events yet. Upload a document to start stream.
            </div>
          ) : (
            documents.slice(0, 5).map((doc) => (
              <div
                key={doc.id}
                className={styles.activityItem}
                onClick={() => openDrawer(doc.id, doc.ocr_result_id || undefined)}
              >
                <div className={`${styles.actIcon} ${doc.needs_human_review ? styles.warning : styles.success}`}>
                  {doc.needs_human_review ? <AlertTriangle size={14} /> : <CheckCircle2 size={14} />}
                </div>
                <div className={styles.actContent}>
                  <span className={styles.actMessage}>
                    {doc.needs_human_review
                      ? `Extraction flagged for review: ${doc.source_filename}`
                      : `Successfully processed ${doc.source_filename}`}
                  </span>
                  <span className={styles.actMeta}>
                    {doc.document_type ? doc.document_type.toUpperCase() : 'DOCUMENT'} •{' '}
                    {doc.uploaded_at ? new Date(doc.uploaded_at).toLocaleTimeString() : 'Recently'}
                  </span>
                </div>
                <span
                  className={`${styles.actBadge} ${
                    doc.needs_human_review ? styles.badgeWarning : styles.badgeSuccess
                  }`}
                >
                  {doc.needs_human_review ? 'Needs Review' : 'Validated'}
                </span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
