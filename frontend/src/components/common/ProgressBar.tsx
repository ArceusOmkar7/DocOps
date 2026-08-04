import React from 'react';
import styles from './ProgressBar.module.css';

interface ProgressBarProps {
  current: number;
  total: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ current, total }) => {
  const percentage = total > 0 ? Math.min(100, Math.round((current / total) * 100)) : 0;
  
  const getColorClass = () => {
    if (percentage === 100) return styles.complete;
    if (percentage >= 50) return styles.medium;
    return styles.low;
  };

  return (
    <div className={styles.wrapper}>
      <span className={styles.text}>
        {current}/{total}
      </span>
      <div className={styles.track}>
        <div
          className={`${styles.fill} ${getColorClass()}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
