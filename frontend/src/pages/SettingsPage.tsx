import React from 'react';
import { Save } from 'lucide-react';
import styles from './DashboardPage.module.css';

export const SettingsPage: React.FC = () => {
  return (
    <div className={styles.container}>
      <div>
        <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>
          System Settings & API Configurations
        </h2>
        <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
          Manage PaddleOCR CUDA acceleration, LLM provider credentials, and PostgreSQL connection parameters.
        </p>
      </div>

      <div className={styles.cardSection} style={{ padding: 24 }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20, maxWidth: 600 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <label style={{ fontSize: 13, fontWeight: 600 }}>LLM Provider Base URL</label>
            <input
              type="text"
              className={styles.filterSelect}
              defaultValue="https://openrouter.ai/api/v1"
              style={{ width: '100%' }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <label style={{ fontSize: 13, fontWeight: 600 }}>Extraction Model</label>
            <input
              type="text"
              className={styles.filterSelect}
              defaultValue="openai/gpt-oss-20b"
              style={{ width: '100%' }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <label style={{ fontSize: 13, fontWeight: 600 }}>OCR Engine & Acceleration</label>
            <div style={{ padding: 12, borderRadius: 8, backgroundColor: 'var(--neutral-50)', border: '1px solid var(--border-subtle)', fontSize: 13 }}>
              <strong>PP-StructureV3 Engine</strong> • CUDA 12.6 Enabled (RTX 4060 Laptop GPU)
            </div>
          </div>

          <button className={styles.btnPrimary} style={{ width: 'fit-content', marginTop: 8 }}>
            <Save size={16} />
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  );
};
