import React from 'react';
import { WorkflowStatus } from '../../types/enums';
import { workflowStatusLabel } from '../../lib/format';
import styles from './WorkflowTimeline.module.css';

interface WorkflowTimelineProps {
  status: WorkflowStatus;
}

const STAGES = [
  WorkflowStatus.COLLECTING_DOCUMENTS,
  WorkflowStatus.READY_FOR_REVIEW,
  WorkflowStatus.IN_REVIEW,
  WorkflowStatus.READY_FOR_FILING,
  WorkflowStatus.COMPLETED,
];

/** Five stages as five flat segments, with the current stage named underneath. */
export const WorkflowTimeline: React.FC<WorkflowTimelineProps> = ({ status }) => {
  const blocked = status === WorkflowStatus.BLOCKED;
  const current = STAGES.indexOf(status);

  return (
    <div className={styles.wrap}>
      <ol
        className={styles.stages}
        aria-label={`Stage ${current + 1} of ${STAGES.length}: ${workflowStatusLabel(status)}`}
      >
        {STAGES.map((stage, i) => (
          <li
            key={stage}
            className={`${styles.stage} ${!blocked && i < current ? styles.done : ''} ${
              !blocked && i === current ? styles.current : ''
            }`}
          />
        ))}
      </ol>
      <span className={blocked ? styles.labelBlocked : styles.label}>
        {workflowStatusLabel(status)}
      </span>
    </div>
  );
};
