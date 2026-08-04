import React from 'react';
import { Check } from 'lucide-react';
import { WorkflowStatus } from '../../types/enums';
import styles from './WorkflowTimeline.module.css';

interface WorkflowTimelineProps {
  status: WorkflowStatus;
}

const STEPS = [
  { key: WorkflowStatus.COLLECTING_DOCUMENTS, label: 'Collecting Documents' },
  { key: WorkflowStatus.READY_FOR_REVIEW, label: 'Ready for Review' },
  { key: WorkflowStatus.IN_REVIEW, label: 'In Review' },
  { key: WorkflowStatus.READY_FOR_FILING, label: 'Ready for Filing' },
  { key: WorkflowStatus.COMPLETED, label: 'Completed' },
];

export const WorkflowTimeline: React.FC<WorkflowTimelineProps> = ({ status }) => {
  const currentIndex = Math.max(0, STEPS.findIndex((s) => s.key === status));
  const fillPct = (currentIndex / (STEPS.length - 1)) * 100;

  return (
    <div className={styles.timeline}>
      <div className={styles.lineTrack}>
        <div className={styles.lineFill} style={{ width: `${fillPct}%` }} />
      </div>

      {STEPS.map((step, idx) => {
        const isCompleted = idx < currentIndex;
        const isActive = idx === currentIndex;

        return (
          <div
            key={step.key}
            className={`${styles.step} ${isActive ? styles.active : ''} ${isCompleted ? styles.completed : ''}`}
          >
            <div className={styles.circle}>
              {isCompleted ? <Check size={13} /> : idx + 1}
            </div>
            <span className={styles.label}>{step.label}</span>
          </div>
        );
      })}
    </div>
  );
};
