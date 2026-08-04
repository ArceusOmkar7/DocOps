import React from 'react';
import { ArrowRight, BookOpen, Building2, GitCompare, ReceiptIndianRupee } from 'lucide-react';
import { WORKFLOW_TEMPLATES, WorkflowTemplate } from '../../data/workflowTemplates';
import styles from './WorkflowTemplateSelector.module.css';

interface WorkflowTemplateSelectorProps {
  onSelectTemplate: (template: WorkflowTemplate) => void;
}

export const WorkflowTemplateSelector: React.FC<WorkflowTemplateSelectorProps> = ({
  onSelectTemplate,
}) => {
  const getIcon = (iconName: string) => {
    switch (iconName) {
      case 'ReceiptIndianRupee':
        return <ReceiptIndianRupee size={22} />;
      case 'GitCompare':
        return <GitCompare size={22} />;
      case 'BookOpen':
        return <BookOpen size={22} />;
      case 'Building2':
        return <Building2 size={22} />;
      default:
        return <ReceiptIndianRupee size={22} />;
    }
  };

  return (
    <div className={styles.grid}>
      {WORKFLOW_TEMPLATES.map((tmpl) => (
        <div key={tmpl.id} className={styles.card} onClick={() => onSelectTemplate(tmpl)}>
          <div className={styles.header}>
            <div className={styles.iconCircle}>{getIcon(tmpl.icon)}</div>
            <div className={styles.titleGroup}>
              <span className={styles.category}>{tmpl.category}</span>
              <h3 className={styles.title}>{tmpl.name}</h3>
            </div>
          </div>

          <p className={styles.description}>{tmpl.description}</p>

          <div className={styles.footer}>
            <span className={styles.reqCount}>{tmpl.requirements.length} Required Documents</span>
            <ArrowRight size={16} color="var(--primary-600)" />
          </div>
        </div>
      ))}
    </div>
  );
};
