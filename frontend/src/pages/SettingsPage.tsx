import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { RefreshCw } from 'lucide-react';
import { ErrorState } from '../components/common/ErrorState';
import { PageHeader } from '../components/common/PageHeader';
import { StatusBadge, Tone } from '../components/common/StatusBadge';
import ui from '../styles/ui.module.css';
import styles from './SettingsPage.module.css';

interface Health {
  service: string;
  version: string;
  database_connected: boolean;
  ocr_pipeline: string;
  ocr_device: string;
  ocr_loaded: boolean;
  llm_model: string;
  llm_base_url: string;
  llm_json_mode: boolean;
  llm_has_api_key: boolean;
}

interface Row {
  name: string;
  detail: string;
  label: string;
  tone: Tone;
}

const toRows = (h: Health): Row[] => [
  {
    name: 'Backend',
    detail: `${h.service} version ${h.version}`,
    label: 'Online',
    tone: 'ok',
  },
  {
    name: 'Database',
    detail: 'PostgreSQL',
    label: h.database_connected ? 'Connected' : 'Disconnected',
    tone: h.database_connected ? 'ok' : 'bad',
  },
  {
    name: 'OCR engine',
    detail: `${h.ocr_pipeline} on ${h.ocr_device.toUpperCase()}. ${
      h.ocr_loaded ? 'Loaded in memory.' : 'Loads on the first upload.'
    }`,
    label: h.ocr_device.toUpperCase(),
    tone: 'ok',
  },
  {
    name: 'Extraction model',
    detail: `${h.llm_model} at ${h.llm_base_url}. JSON mode ${h.llm_json_mode ? 'on' : 'off'}.`,
    label: h.llm_has_api_key ? 'API key set' : 'No API key',
    tone: h.llm_has_api_key ? 'ok' : 'warn',
  },
];

export const SettingsPage: React.FC = () => {
  const { data: health, isLoading, isError, isFetching, refetch } = useQuery<Health>({
    queryKey: ['systemHealth'],
    queryFn: async () => {
      const res = await fetch('/api/v1/health');
      if (!res.ok) throw new Error('Health check failed');
      return res.json();
    },
    staleTime: 10000,
  });

  return (
    <div className={ui.page}>
      <PageHeader
        title="Settings"
        actions={
          <button className={ui.btn} onClick={() => refetch()} disabled={isFetching}>
            <RefreshCw
              size={15}
              strokeWidth={1.75}
              className={isFetching ? ui.spin : undefined}
              aria-hidden="true"
            />
            Check again
          </button>
        }
      />

      <section className={ui.panel} aria-labelledby="status-title">
        <div className={ui.panelHead}>
          <h2 id="status-title" className={ui.panelTitle}>
            System status
          </h2>
        </div>

        {isError ? (
          <ErrorState what="system status" />
        ) : isLoading || !health ? (
          <div className={ui.empty} aria-busy="true">
            <div className={ui.skeletonRow} style={{ width: '50%' }} />
          </div>
        ) : (
          <dl className={styles.rows}>
            {toRows(health).map((row) => (
              <div key={row.name} className={styles.row}>
                <dt className={styles.name}>{row.name}</dt>
                <dd className={styles.detail}>{row.detail}</dd>
                <dd className={styles.state}>
                  <StatusBadge status={row.label} label={row.label} tone={row.tone} />
                </dd>
              </div>
            ))}
          </dl>
        )}
      </section>
    </div>
  );
};
