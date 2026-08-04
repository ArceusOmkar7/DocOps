import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { CheckCircle2, Cpu, Database, Key, Loader2, RefreshCw, Server, Sparkles } from 'lucide-react';
import styles from './DashboardPage.module.css';

export const SettingsPage: React.FC = () => {
  const { data: health, isLoading, isError, refetch } = useQuery({
    queryKey: ['systemHealth'],
    queryFn: async () => {
      const res = await fetch('/api/v1/health');
      if (!res.ok) throw new Error('Health check failed');
      return res.json();
    },
    staleTime: 10000,
  });

  return (
    <div className={styles.container}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)' }}>
            System Settings & API Configurations
          </h2>
          <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Live status of PaddleOCR GPU engine, LLM extraction model, and PostgreSQL database.
          </p>
        </div>
        <button className={styles.btnPrimary} onClick={() => refetch()}>
          <RefreshCw size={14} />
          Refresh Status
        </button>
      </div>

      <div className={styles.cardSection} style={{ padding: 24 }}>
        {isLoading ? (
          <div style={{ padding: 36, textAlign: 'center', color: '#64748b' }}>
            <Loader2 size={24} className="animate-spin" style={{ margin: '0 auto 8px' }} />
            <span>Connecting to FastAPI backend...</span>
          </div>
        ) : isError ? (
          <div style={{ padding: 24, borderRadius: 8, backgroundColor: '#fef2f2', color: '#991b1b', fontSize: 13 }}>
            <strong>Backend Unreachable</strong>
            <div>Could not connect to FastAPI dev server on <code>http://127.0.0.1:8000</code>. Ensure uvicorn is running.</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24, maxWidth: 680 }}>
            {/* Backend Service Status */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 16, borderRadius: 8, backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
              <Server size={20} style={{ color: '#0284c7' }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a' }}>
                  {health.service} v{health.version}
                </div>
                <div style={{ fontSize: 12, color: '#64748b' }}>FastAPI backend status: OK</div>
              </div>
              <span style={{ fontSize: 12, fontWeight: 600, color: '#16a34a', backgroundColor: '#dcfce7', padding: '4px 10px', borderRadius: 999 }}>
                ● Online
              </span>
            </div>

            {/* Database Connection */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 16, borderRadius: 8, backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
              <Database size={20} style={{ color: '#4f46e5' }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a' }}>
                  PostgreSQL Database
                </div>
                <div style={{ fontSize: 12, color: '#64748b' }}>
                  SQLAlchemy 2.x asyncpg pool connection
                </div>
              </div>
              <span
                style={{
                  fontSize: 12,
                  fontWeight: 600,
                  color: health.database_connected ? '#16a34a' : '#dc2626',
                  backgroundColor: health.database_connected ? '#dcfce7' : '#fee2e2',
                  padding: '4px 10px',
                  borderRadius: 999,
                }}
              >
                {health.database_connected ? 'Connected' : 'Disconnected'}
              </span>
            </div>

            {/* OCR Pipeline */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 16, borderRadius: 8, backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
              <Cpu size={20} style={{ color: '#059669' }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a' }}>
                  OCR Layout Pipeline: {health.ocr_pipeline}
                </div>
                <div style={{ fontSize: 12, color: '#64748b' }}>
                  Device: <strong>{health.ocr_device.toUpperCase()}</strong> (CUDA 12.6 GPU) • Memory Resident:{' '}
                  {health.ocr_loaded ? 'Yes' : 'Lazy-load on first request'}
                </div>
              </div>
              <span style={{ fontSize: 12, fontWeight: 600, color: '#059669', backgroundColor: '#ecfdf5', padding: '4px 10px', borderRadius: 999 }}>
                {health.ocr_device.toUpperCase()}
              </span>
            </div>

            {/* LLM Extraction Engine */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: 16, borderRadius: 8, backgroundColor: '#f8fafc', border: '1px solid #e2e8f0' }}>
              <Sparkles size={20} style={{ color: '#d97706' }} />
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a' }}>
                  LLM Model: {health.llm_model}
                </div>
                <div style={{ fontSize: 12, color: '#64748b' }}>
                  Provider: <code>{health.llm_base_url}</code> • JSON Mode:{' '}
                  {health.llm_json_mode ? 'Enabled' : 'Disabled'}
                </div>
              </div>
              <span
                style={{
                  fontSize: 12,
                  fontWeight: 600,
                  color: health.llm_has_api_key ? '#16a34a' : '#d97706',
                  backgroundColor: health.llm_has_api_key ? '#dcfce7' : '#fef3c7',
                  padding: '4px 10px',
                  borderRadius: 999,
                }}
              >
                {health.llm_has_api_key ? 'API Key Set' : 'No Key Set'}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
