import React, { useState } from 'react';
import {
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  Clock,
  Eye,
  FileCheck,
  FileText,
  FileWarning,
  Loader2,
  Search,
  ShieldAlert,
  Users,
} from 'lucide-react';
import { StatCard } from '../components/common/StatCard';
import { StatusBadge } from '../components/common/StatusBadge';
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
          label="Client Accounts"
          value={totalClients}
          trend={`${totalClients} active`}
          icon={Users}
        />
        <StatCard
          label="Documents Ingested"
          value={documentsProcessed}
          trend={`${documentsProcessed} total`}
          icon={FileText}
        />
        <StatCard
          label="Filing Ready"
          value={readyForFiling}
          trend={documentsProcessed > 0 ? `${((readyForFiling / documentsProcessed) * 100).toFixed(0)}% validated` : '0%'}
          icon={FileCheck}
        />
        <StatCard
          label="Action Required"
          value={missingDocuments}
          trend={missingDocuments > 0 ? `${missingDocuments} exceptions` : '0 backlog'}
          trendType={missingDocuments > 0 ? 'warning' : 'positive'}
          icon={FileWarning}
        />
        <StatCard
          label="Verification Needed"
          value={needReview}
          trend={needReview > 0 ? `${needReview} flagged for review` : 'All verified'}
          trendType={needReview > 0 ? 'warning' : 'positive'}
          icon={AlertTriangle}
        />
      </div>

      {/* Clients Table Section */}
      <div className={styles.cardSection}>
        <div className={styles.cardHeader}>
          <div className={styles.titleArea}>
            <h3 className={styles.cardTitle}>Client Filing Status</h3>
            <span className={styles.cardSubtitle}>
              Active client records and statutory compliance posture
            </span>
          </div>

          <div className={styles.headerActions}>
            <div className={styles.searchBox}>
              <Search size={13} className={styles.searchIcon} />
              <input
                type="text"
                className={styles.searchInput}
                placeholder="Filter clients or GSTIN..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>

            <select
              className={styles.filterSelect}
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Statuses</option>
              <option value="on_track">On Track</option>
              <option value="awaiting_documents">Awaiting Documents</option>
              <option value="needs_review">Needs Review</option>
              <option value="action_required">Action Required</option>
            </select>
          </div>
        </div>

        <div className={styles.tableContainer}>
          {loadingClients ? (
            <div className={styles.emptyState}>
              <Loader2 size={20} className="animate-spin" />
              <span>Fetching client records...</span>
            </div>
          ) : filteredClients.length === 0 ? (
            <div className={styles.emptyState}>
              <Users size={28} />
              <span>No client accounts match your criteria.</span>
            </div>
          ) : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Client Account</th>
                  <th>Compliance Status</th>
                  <th>Primary Contact</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
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
                    <tr
                      key={client.id}
                      onClick={() => openDrawer()}
                      className={styles.tableRow}
                    >
                      <td>
                        <div className={styles.clientCell}>
                          <div className={styles.avatar}>{initials}</div>
                          <div className={styles.clientInfo}>
                            <span className={styles.clientName}>{client.name}</span>
                            <span className={styles.clientGstin}>
                              GSTIN: {client.tax_id || 'NOT_REGISTERED'}
                            </span>
                          </div>
                        </div>
                      </td>
                      <td>
                        <StatusBadge status={client.status || 'on_track'} />
                      </td>
                      <td className={styles.secondaryText}>{client.contact_person || '—'}</td>
                      <td className={styles.mutedCell}>{client.email || '—'}</td>
                      <td className={styles.mutedCell}>{client.phone || '—'}</td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          className={styles.actionBtn}
                          onClick={(e) => {
                            e.stopPropagation();
                            openDrawer();
                          }}
                        >
                          <Eye size={12} />
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
            Displaying {filteredClients.length} of {totalClients} client accounts
          </span>
        </div>
      </div>

      {/* Operational Activity Stream */}
      <div className={styles.cardSection}>
        <div className={styles.cardHeader}>
          <div className={styles.titleArea}>
            <h3 className={styles.cardTitle}>Operational Activity & Ingestion Stream</h3>
            <span className={styles.cardSubtitle}>
              Audit trail of document extraction, classification, and statutory checks
            </span>
          </div>
        </div>

        <div className={styles.activityFeed}>
          {documents.length === 0 ? (
            <div className={styles.emptyState}>
              <Clock size={24} />
              <span>No document activity recorded in current session.</span>
            </div>
          ) : (
            documents.slice(0, 5).map((doc) => (
              <div
                key={doc.id}
                className={styles.activityItem}
                onClick={() => openDrawer(doc.id, doc.ocr_result_id || undefined)}
              >
                <div
                  className={`${styles.actIcon} ${
                    doc.needs_human_review ? styles.actIconWarning : styles.actIconSuccess
                  }`}
                >
                  {doc.needs_human_review ? (
                    <ShieldAlert size={14} />
                  ) : (
                    <CheckCircle2 size={14} />
                  )}
                </div>
                <div className={styles.actContent}>
                  <div className={styles.actMessage}>
                    {doc.needs_human_review ? (
                      <span>
                        Flagged for human signoff:{' '}
                        <strong>{doc.source_filename}</strong>
                      </span>
                    ) : (
                      <span>
                        Verified and parsed:{' '}
                        <strong>{doc.source_filename}</strong>
                      </span>
                    )}
                  </div>
                  <div className={styles.actMeta}>
                    <span className={styles.docTypeTag}>
                      {doc.document_type ? doc.document_type.toUpperCase() : 'DOCUMENT'}
                    </span>
                    <span>•</span>
                    <span>
                      {doc.uploaded_at
                        ? new Date(doc.uploaded_at).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                          })
                        : 'Recently'}
                    </span>
                  </div>
                </div>
                <StatusBadge
                  status={doc.needs_human_review ? 'needs_review' : 'validated'}
                />
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
