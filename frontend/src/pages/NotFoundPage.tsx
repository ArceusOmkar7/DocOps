import React from 'react';
import { Link } from 'react-router-dom';
import { FileQuestion } from 'lucide-react';
import styles from './DashboardPage.module.css';

export const NotFoundPage: React.FC = () => {
  return (
    <div style={{ textAlign: 'center', padding: '80px 20px' }}>
      <FileQuestion size={64} style={{ margin: '0 auto 16px', opacity: 0.4 }} />
      <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>Page Not Found</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: 24 }}>The route you requested does not exist.</p>
      <Link to="/" className={styles.btnPrimary} style={{ display: 'inline-flex' }}>
        Back to Dashboard
      </Link>
    </div>
  );
};
