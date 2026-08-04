import React from 'react';
import { LucideIcon } from 'lucide-react';
import styles from './StatCard.module.css';

interface StatCardProps {
  label: string;
  value: string | number;
  trend?: string;
  trendType?: 'positive' | 'neutral' | 'warning';
  icon: LucideIcon;
  colorTheme?: 'indigo' | 'blue' | 'green' | 'amber' | 'red' | 'purple';
  sparkline?: number[];
}

const SPARKLINE_COLORS: Record<string, { stroke: string; fill: string }> = {
  indigo: { stroke: '#6366f1', fill: 'rgba(99,102,241,0.12)' },
  blue: { stroke: '#3b82f6', fill: 'rgba(59,130,246,0.12)' },
  green: { stroke: '#10b981', fill: 'rgba(16,185,129,0.12)' },
  amber: { stroke: '#f59e0b', fill: 'rgba(245,158,11,0.12)' },
  red: { stroke: '#ef4444', fill: 'rgba(239,68,68,0.12)' },
  purple: { stroke: '#8b5cf6', fill: 'rgba(139,92,246,0.12)' },
};

function buildSparklinePath(data: number[]): { line: string; area: string } {
  if (data.length < 2) return { line: '', area: '' };
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const w = 100;
  const h = 32;
  const step = w / (data.length - 1);

  const points = data.map((v, i) => ({
    x: i * step,
    y: h - ((v - min) / range) * (h - 4) - 2,
  }));

  const line = points.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
  const area = `${line} L${w},${h} L0,${h} Z`;

  return { line, area };
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  trend,
  trendType = 'positive',
  icon: Icon,
  colorTheme = 'indigo',
  sparkline,
}) => {
  const iconClass = {
    indigo: styles.iconIndigo,
    blue: styles.iconBlue,
    green: styles.iconGreen,
    amber: styles.iconAmber,
    red: styles.iconRed,
    purple: styles.iconPurple,
  }[colorTheme] || styles.iconIndigo;

  const trendClass = {
    positive: styles.trendPositive,
    neutral: styles.trendNeutral,
    warning: styles.trendWarning,
  }[trendType];

  const colors = SPARKLINE_COLORS[colorTheme] || SPARKLINE_COLORS.indigo;
  const spark = sparkline && sparkline.length >= 2 ? buildSparklinePath(sparkline) : null;

  return (
    <div className={styles.card}>
      <div className={styles.topRow}>
        <span className={styles.label}>{label}</span>
        <div className={`${styles.iconBox} ${iconClass}`}>
          <Icon size={16} />
        </div>
      </div>
      <div className={styles.valueRow}>
        <span className={styles.value}>
          {typeof value === 'number' ? value.toLocaleString() : value}
        </span>
      </div>
      {trend && (
        <span className={`${styles.trend} ${trendClass}`}>{trend}</span>
      )}
      {spark && (
        <div className={styles.sparklineWrap}>
          <svg viewBox="0 0 100 32" className={styles.sparkline} preserveAspectRatio="none">
            <path d={spark.area} fill={colors.fill} />
            <path d={spark.line} fill="none" stroke={colors.stroke} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
        </div>
      )}
    </div>
  );
};
