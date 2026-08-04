import React from 'react';
import { Plus } from 'lucide-react';
import { StatusBadge } from '../components/common/StatusBadge';
import { ProgressBar } from '../components/common/ProgressBar';
import { DEMO_CLIENTS } from '../data/demoData';
import styles from './DashboardPage.module.css';

export const ClientsPage: React.FC = () => {
  return (
    <div className={styles.container}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>
            Client Management
          </h2>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            View and manage organizational clients and their compliance state.
          </p>
        </div>
        <button className={styles.btnPrimary}>
          <Plus size={16} />
          Add Client
        </button>
      </div>

      <div className={styles.cardSection}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Client</th>
              <th>Status</th>
              <th style={{ width: 140 }}>Documents</th>
              <th>Contact Person</th>
              <th>Phone</th>
              <th>Email</th>
            </tr>
          </thead>
          <tbody>
            {DEMO_CLIENTS.map((client) => (
              <tr key={client.id}>
                <td>
                  <div className={styles.clientCell}>
                    <div className={styles.avatar}>{client.initials}</div>
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
                <td>{client.contact_person}</td>
                <td style={{ color: 'var(--text-muted)' }}>{client.phone}</td>
                <td style={{ color: 'var(--text-muted)' }}>{client.email}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
