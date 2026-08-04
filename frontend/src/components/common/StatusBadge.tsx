import React from 'react';
import styles from './StatusBadge.module.css';

interface StatusBadgeProps {
  status: string;
  variant?: 'green' | 'amber' | 'red' | 'blue' | 'gray';
  label?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, variant, label }) => {
  const normalizeVariant = (): 'green' | 'amber' | 'red' | 'blue' | 'gray' => {
    if (variant) return variant;
    const s = status.toLowerCase().replace(/_/g, ' ');
    if (s.includes('ready') || s.includes('validated') || s.includes('track') || s.includes('success') || s.includes('completed')) {
      return 'green';
    }
    if (s.includes('waiting') || s.includes('pending') || s.includes('collecting')) {
      return 'amber';
    }
    if (s.includes('review') || s.includes('reject') || s.includes('failed') || s.includes('action') || s.includes('need')) {
      return 'red';
    }
    if (s.includes('processing') || s.includes('in progress')) {
      return 'blue';
    }
    return 'gray';
  };

  const colorStyle = normalizeVariant();
  const displayLabel = label || status.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());

  return (
    <span className={`${styles.badge} ${styles[colorStyle]}`}>
      <span className={styles.dot} />
      {displayLabel}
    </span>
  );
};
