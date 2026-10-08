import React from 'react';
import { WORKFLOW_TEMPLATES, WorkflowTemplate } from '../../data/workflowTemplates';
import ui from '../../styles/ui.module.css';
import styles from './WorkflowTemplateSelector.module.css';

interface WorkflowTemplateSelectorProps {
  onSelectTemplate: (template: WorkflowTemplate) => void;
  disabled?: boolean;
}

export const WorkflowTemplateSelector: React.FC<WorkflowTemplateSelectorProps> = ({
  onSelectTemplate,
  disabled,
}) => (
  <ul className={styles.list}>
    {WORKFLOW_TEMPLATES.map((tmpl) => (
      <li key={tmpl.id} className={styles.item}>
        <div className={styles.text}>
          <h3 className={styles.name}>{tmpl.name}</h3>
          <p className={styles.description}>{tmpl.description}</p>
          <span className={styles.meta}>
            {tmpl.requirements.length} required documents
          </span>
        </div>
        <button className={ui.btn} disabled={disabled} onClick={() => onSelectTemplate(tmpl)}>
          Start filing
        </button>
      </li>
    ))}
  </ul>
);
