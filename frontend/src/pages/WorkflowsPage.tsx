import React, { useState } from 'react';
import { ArrowRight, GitPullRequest, Plus, Sparkles } from 'lucide-react';
import { WorkflowTemplateSelector } from '../components/workflows/WorkflowTemplateSelector';
import { WorkflowTimeline } from '../components/workflows/WorkflowTimeline';
import { StatusBadge } from '../components/common/StatusBadge';
import { WorkflowTemplate } from '../data/workflowTemplates';
import { WorkflowStatus, WorkflowType } from '../types/enums';
import styles from './DashboardPage.module.css';
import wfStyles from './WorkflowsPage.module.css';

export const WorkflowsPage: React.FC = () => {
  const [showSelector, setShowSelector] = useState(false);
  const [activeWorkflows, setActiveWorkflows] = useState([
    {
      id: 'wf-1',
      name: 'GST Monthly Filing — April 2025',
      client: 'ABC Traders',
      type: WorkflowType.GST_FILING,
      status: WorkflowStatus.READY_FOR_FILING,
      received: 12,
      total: 12,
      period: 'Apr 1 - Apr 30, 2025',
    },
    {
      id: 'wf-2',
      name: 'AP 3-Way Match — Hardware Purchase',
      client: 'XYZ Industries',
      type: WorkflowType.BOOKKEEPING,
      status: WorkflowStatus.COLLECTING_DOCUMENTS,
      received: 9,
      total: 12,
      period: 'Apr 1 - Apr 30, 2025',
    },
    {
      id: 'wf-3',
      name: 'TDS Quarterly Return Q4',
      client: 'PQR Pvt Ltd',
      type: WorkflowType.TDS_FILING,
      status: WorkflowStatus.IN_REVIEW,
      received: 9,
      total: 12,
      period: 'Jan 1 - Mar 31, 2025',
    },
  ]);

  const handleLaunchTemplate = (tmpl: WorkflowTemplate) => {
    setActiveWorkflows([{
      id: `wf-${Date.now()}`,
      name: `${tmpl.name} — Current Period`,
      client: 'ABC Traders',
      type: tmpl.type,
      status: WorkflowStatus.COLLECTING_DOCUMENTS,
      received: 0,
      total: tmpl.requirements.length,
      period: 'May 1 - May 31, 2025',
    }, ...activeWorkflows]);
    setShowSelector(false);
  };

  return (
    <div className={styles.container}>
      {/* Header row */}
      <div className={wfStyles.pageHeader}>
        <button className={styles.btnPrimary} onClick={() => setShowSelector(!showSelector)}>
          <Plus size={13} />
          {showSelector ? 'Close Templates' : 'Launch New Workflow'}
        </button>
      </div>

      {/* Template picker */}
      {showSelector && (
        <div className={styles.cardSection}>
          <div className={styles.cardHeader}>
            <div className={styles.titleArea}>
              <h3 className={styles.cardTitle} style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                <Sparkles size={15} style={{ color: '#4f46e5' }} />
                Select a Prebuilt Workflow Template
              </h3>
            </div>
          </div>
          <div style={{ padding: 18 }}>
            <WorkflowTemplateSelector onSelectTemplate={handleLaunchTemplate} />
          </div>
        </div>
      )}

      {/* Active workflows */}
      <div className={styles.cardSection}>
        <div className={styles.cardHeader}>
          <div className={styles.titleArea}>
            <h3 className={styles.cardTitle}>Active Client Workflows ({activeWorkflows.length})</h3>
            <span className={styles.cardSubtitle}>Deterministic document checklists & status transitions</span>
          </div>
        </div>

        <div className={wfStyles.workflowList}>
          {activeWorkflows.map((wf) => (
            <div key={wf.id} className={wfStyles.workflowCard}>
              <div className={wfStyles.wfTop}>
                <div className={wfStyles.wfLeft}>
                  <div className={wfStyles.wfIcon}>
                    <GitPullRequest size={16} />
                  </div>
                  <div className={wfStyles.wfInfo}>
                    <h4 className={wfStyles.wfName}>{wf.name}</h4>
                    <span className={wfStyles.wfMeta}>
                      Client: <strong>{wf.client}</strong> · Period: {wf.period}
                    </span>
                  </div>
                </div>
                <StatusBadge status={wf.status} />
              </div>

              {/* Progression Timeline */}
              <WorkflowTimeline status={wf.status} />

              <div className={wfStyles.wfBottom}>
                <span className={wfStyles.wfProgress}>
                  Checklist Progress: {wf.received} / {wf.total} Documents Collected
                </span>
                <button className={styles.actionBtn}>
                  <span>Inspect Workflow Checklist</span>
                  <ArrowRight size={12} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
