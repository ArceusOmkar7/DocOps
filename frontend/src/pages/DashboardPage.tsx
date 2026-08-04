import React, { useState } from 'react';
import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  Eye,
  FileCheck,
  FileText,
  FileWarning,
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
import { DEMO_CLIENTS, DEMO_RECENT_ACTIVITIES, DEMO_STATS } from '../data/demoData';
import styles from './DashboardPage.module.css';

export const DashboardPage: React.FC = () => {
  const { openDrawer } = useDrawer();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const filteredClients = DEMO_CLIENTS.filter((c) => {
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
          value={DEMO_STATS.totalClients}
          trend={DEMO_STATS.totalClientsTrend}
          icon={Users}
          colorTheme="indigo"
          sparkline={[120, 132, 145, 139, 155, 162, 170, 175, 182]}
        />
        <StatCard
          label="Documents Processed"
          value={DEMO_STATS.documentsProcessed}
          trend={DEMO_STATS.documentsProcessedTrend}
          icon={FileText}
          colorTheme="blue"
          sparkline={[800, 860, 920, 980, 1050, 1100, 1180, 1220, 1247]}
        />
        <StatCard
          label="Ready for Filing"
          value={DEMO_STATS.readyForFiling}
          trend={DEMO_STATS.readyForFilingPercentage}
          icon={FileCheck}
          colorTheme="green"
          sparkline={[90, 105, 118, 125, 132, 140, 148, 153, 156]}
        />
        <StatCard
          label="Missing Documents"
          value={DEMO_STATS.missingDocuments}
          trend={DEMO_STATS.missingDocumentsNote}
          trendType="warning"
          icon={FileWarning}
          colorTheme="red"
          sparkline={[28, 25, 22, 24, 20, 19, 21, 18, 18]}
        />
        <StatCard
          label="Need Review"
          value={DEMO_STATS.needReview}
          trend={DEMO_STATS.needReviewNote}
          trendType="warning"
          icon={AlertTriangle}
          colorTheme="amber"
          sparkline={[12, 10, 9, 11, 8, 7, 8, 6, 6]}
        />
      </div>

      {/* Clients Table Section */}
      <div className={styles.cardSection}>
        <div className={styles.cardHeader}>
          <div className={styles.titleArea}>
            <h3 className={styles.cardTitle}>Clients</h3>
            <span className={styles.cardSubtitle}>All clients and their document status</span>
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
              <option value="review_required">Need Review</option>
              <option value="action_required">Action Required</option>
            </select>

            <button className={styles.btnPrimary}>
              <Plus size={13} />
              Add Client
            </button>
          </div>
        </div>

        <div className={styles.tableContainer}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Client</th>
                <th>Status</th>
                <th>Documents</th>
                <th>Missing</th>
                <th>Next Action</th>
                <th>Updated</th>
              </tr>
            </thead>
            <tbody>
              {filteredClients.map((client) => (
                <tr key={client.id} onClick={openDrawer}>
                  <td>
                    <div className={styles.clientCell}>
                      <div className={`${styles.avatar} ${styles[`avatar${client.avatarColor.charAt(0).toUpperCase() + client.avatarColor.slice(1)}`]}`}>{client.initials}</div>
                      <div className={styles.clientInfo}>
                        <span className={styles.clientName}>{client.name}</span>
                        <span className={styles.clientGstin}>GSTN: {client.tax_id}</span>
                      </div>
                    </div>
                  </td>
                  <td>
                    <StatusBadge status={client.status} />
                  </td>
                  <td>
                    <ProgressBar current={client.docProgress.current} total={client.docProgress.total} />
                  </td>
                  <td>
                    <span className={
                      client.missingCount >= 6 ? styles.missingBad :
                      client.missingCount >= 1 ? styles.missingWarn :
                      styles.missingOk
                    }>
                      {client.missingCount}
                    </span>
                  </td>
                  <td>
                    <button
                      className={styles.actionBtn}
                      onClick={(e) => { e.stopPropagation(); openDrawer(); }}
                    >
                      {client.nextAction === 'Send Reminder' && <Send size={11} />}
                      {client.nextAction === 'Review Documents' && <Eye size={11} />}
                      {client.nextAction === 'Generate Report' && <FileCheck size={11} />}
                      {client.nextAction === 'View Progress' && <BarChart3 size={11} />}
                      {client.nextAction === 'Follow Up' && <RefreshCw size={11} />}
                      <span>{client.nextAction}</span>
                    </button>
                  </td>
                  <td className={styles.mutedCell}>{client.updatedAgo}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className={styles.tableFooter}>
          <span>Showing 1 to {filteredClients.length} of {DEMO_STATS.totalClients} clients</span>
          <div className={styles.pagination}>
            <button className={`${styles.pageBtn} ${styles.active}`}>1</button>
            <button className={styles.pageBtn}>2</button>
            <button className={styles.pageBtn}>3</button>
            <span className={styles.pageEllipsis}>...</span>
            <button className={styles.pageBtn}>37</button>
          </div>
        </div>
      </div>

      {/* Recent Activity Stream */}
      <div className={styles.cardSection}>
        <div className={styles.cardHeader}>
          <div className={styles.titleArea}>
            <h3 className={styles.cardTitle}>Recent Activity</h3>
            <span className={styles.cardSubtitle}>Real-time agentic AI reasoning and OCR events</span>
          </div>
          <button className={styles.viewAllBtn}>View All</button>
        </div>

        <div className={styles.activityFeed}>
          {DEMO_RECENT_ACTIVITIES.map((act) => (
            <div key={act.id} className={styles.activityItem} onClick={openDrawer}>
              <div className={`${styles.actIcon} ${styles[act.type]}`}>
                {act.type === 'success' && <CheckCircle2 size={14} />}
                {act.type === 'warning' && <AlertTriangle size={14} />}
                {act.type === 'info' && <FileText size={14} />}
                {act.type === 'review' && <Eye size={14} />}
              </div>
              <div className={styles.actContent}>
                <span className={styles.actMessage}>{act.message}</span>
                <span className={styles.actMeta}>{act.meta} • {act.timeAgo}</span>
              </div>
              <span className={`${styles.actBadge} ${styles[`badge${act.type.charAt(0).toUpperCase() + act.type.slice(1)}`]}`}>{act.badge}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
