import React from 'react';
import { Readiness } from '../../lib/readiness';
import styles from './ReadinessBar.module.css';

interface ReadinessBarProps {
  readiness: Readiness;
  /** Fill the width of the parent instead of the fixed table width. */
  wide?: boolean;
}

const SEGMENTS = [
  { key: 'validated', label: 'validated', className: styles.validated },
  { key: 'review', label: 'in review', className: styles.review },
  { key: 'failed', label: 'failed', className: styles.failed },
  { key: 'pending', label: 'pending', className: styles.pending },
] as const;

export const ReadinessBar: React.FC<ReadinessBarProps> = ({ readiness, wide }) => {
  const summary = SEGMENTS.filter((s) => readiness[s.key] > 0)
    .map((s) => `${readiness[s.key]} ${s.label}`)
    .join(', ');

  return (
    <div
      className={`${styles.bar} ${wide ? styles.wide : ''}`}
      role="img"
      aria-label={`${readiness.total} documents: ${summary}`}
      title={summary}
    >
      {SEGMENTS.map((s) =>
        readiness[s.key] > 0 ? (
          <span
            key={s.key}
            className={`${styles.segment} ${s.className}`}
            style={{ flexGrow: readiness[s.key] }}
          />
        ) : null
      )}
    </div>
  );
};
