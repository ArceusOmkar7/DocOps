import React from 'react';
import { LucideIcon } from 'lucide-react';
import styles from './StatCard.module.css';

interface StatCardProps {
  label: string;
  value: string | number;
  trend?: string;
  trendType?: 'positive' | 'neutral' | 'warning';
  icon?: LucideIcon;
  colorTheme?: 'indigo' | 'blue' | 'green' | 'amber' | 'red' | 'purple';
  sparkline?: number[];
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  trend,
  trendType = 'positive',
  icon: Icon,
}) => {
  const trendClass = {
    positive: styles.trendPositive,
    neutral: styles.trendNeutral,
    warning: styles.trendWarning,
  }[trendType];

  return (
    <div className={styles.card}>
      <div className={styles.headerRow}>
        <span className={styles.label}>{label}</span>
        {Icon && <Icon size={14} strokeWidth={1.75} className={styles.icon} />}
      </div>
      <div className={styles.valueRow}>
        <span className={styles.value}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </span>
      </div>
      {trend && (
        <div className={styles.footerRow}>
          <span className={`${styles.trend} ${trendClass}`}>{trend}</span>
        </div>
      )}
    </div>
  );
};
