import React from 'react';
import styles from './StatusBadge.module.css';

export type Tone = 'ok' | 'warn' | 'bad' | 'idle';

/** Maps any backend status string (client, document or filing) to a tone. */
export const toneFor = (status: string): Tone => {
  const s = status.toLowerCase();
  if (/(fail|reject|action|blocked)/.test(s)) return 'bad';
  if (/(review|await|need|collecting)/.test(s)) return 'warn';
  if (/(valid|track|complete|ready_for_filing|success)/.test(s)) return 'ok';
  return 'idle';
};

interface StatusBadgeProps {
  /** Raw backend status, used to pick the tone when `tone` is not given. */
  status: string;
  label: string;
  tone?: Tone;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, label, tone }) => (
  <span className={`${styles.badge} ${styles[tone ?? toneFor(status)]}`}>{label}</span>
);
