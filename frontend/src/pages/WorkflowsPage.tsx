import React, { useState } from 'react';
import { ArrowRight, CheckSquare, GitPullRequest, Layers, Loader2, Plus, X } from 'lucide-react';
import { WorkflowTemplateSelector } from '../components/workflows/WorkflowTemplateSelector';
import { WorkflowTimeline } from '../components/workflows/WorkflowTimeline';
import { StatusBadge } from '../components/common/StatusBadge';
import { useClients } from '../hooks/useClients';
import { useCreateWorkflow, useWorkflows } from '../hooks/useWorkflows';
import { WorkflowTemplate } from '../data/workflowTemplates';
import { DocumentType } from '../types/api';
import styles from './DashboardPage.module.css';
import wfStyles from './WorkflowsPage.module.css';

export const WorkflowsPage: React.FC = () => {
  const [showSelector, setShowSelector] = useState(false);

  const { data: workflows = [], isLoading } = useWorkflows();
  const { data: clients = [] } = useClients();
  const createWorkflowMutation = useCreateWorkflow();

  const handleLaunchTemplate = async (tmpl: WorkflowTemplate) => {
    const targetClient = clients[0];
    if (!targetClient) {
      alert('Please register at least one client before initializing a compliance workflow.');
      return;
    }

    try {
      await createWorkflowMutation.mutateAsync({
        organization_id: targetClient.organization_id,
        client_id: targetClient.id,
        name: `${tmpl.name} — Current Period`,
        workflow_type: tmpl.type as any,
        period_start: new Date().toISOString().substring(0, 10),
        period_end: new Date(Date.now() + 30 * 86400000).toISOString().substring(0, 10),
        requirements: tmpl.requirements.map((req) => ({
          label: req.label,
          document_type: req.document_type || DocumentType.INVOICE,
          required_count: req.required_count || 1,
        })),
      });

      setShowSelector(false);
    } catch (err: any) {
      alert(`Failed to initialize workflow: ${err.message}`);
    }
  };

  return (
    <div className={styles.container}>
      {/* Header row */}
      <div className={wfStyles.pageHeader}>
        <button
          className={styles.btnPrimary}
          onClick={() => setShowSelector(!showSelector)}
        >
          {showSelector ? <X size={13} /> : <Plus size={13} />}
          <span>{showSelector ? 'Close Templates' : 'Initialize Workflow'}</span>
        </button>
      </div>

      {/* Template picker */}
      {showSelector && (
        <div className={styles.cardSection}>
          <div className={styles.cardHeader}>
            <div className={styles.titleArea}>
              <h3 className={styles.cardTitle} style={{ display: 'flex', alignItems: 'center', gap: 7 }}>
                <CheckSquare size={15} className={styles.searchIcon} />
                <span>Statutory Compliance Workflow Templates</span>
              </h3>
              <span className={styles.cardSubtitle}>
                Select an audited template to orchestrate client document collection and filing checks
              </span>
            </div>
          </div>
          <div style={{ padding: 16 }}>
            <WorkflowTemplateSelector onSelectTemplate={handleLaunchTemplate} />
          </div>
        </div>
      )}

      {/* Active workflows */}
      <div className={styles.cardSection}>
        <div className={styles.cardHeader}>
          <div className={styles.titleArea}>
            <h3 className={styles.cardTitle}>Active Compliance Workflows ({workflows.length})</h3>
            <span className={styles.cardSubtitle}>
              Client document checklists and statutory progression pipeline
            </span>
          </div>
        </div>

        {isLoading ? (
          <div className={styles.emptyState}>
            <Loader2 size={20} className="animate-spin" />
            <span>Fetching compliance workflows...</span>
          </div>
        ) : workflows.length === 0 ? (
          <div className={styles.emptyState}>
            <GitPullRequest size={28} />
            <span>No active workflows. Initialize a template above to track client filings.</span>
          </div>
        ) : (
          <div className={wfStyles.workflowList}>
            {workflows.map((wf) => {
              const reqs = wf.requirements || [];
              const periodStr = `${wf.period_start} — ${wf.period_end}`;

              return (
                <div key={wf.id} className={wfStyles.workflowCard}>
                  <div className={wfStyles.wfTop}>
                    <div className={wfStyles.wfLeft}>
                      <div className={wfStyles.wfIcon}>
                        <GitPullRequest size={15} strokeWidth={1.75} />
                      </div>
                      <div className={wfStyles.wfInfo}>
                        <h4 className={wfStyles.wfName}>{wf.name}</h4>
                        <span className={wfStyles.wfMeta}>
                          Period: {periodStr}
                        </span>
                      </div>
                    </div>
                    <StatusBadge status={wf.status} />
                  </div>

                  {/* Progression Timeline */}
                  <WorkflowTimeline status={wf.status} />

                  <div className={wfStyles.wfBottom}>
                    <span className={wfStyles.wfProgress}>
                      Checklist Requirements: {reqs.length} Statutory Document Items
                    </span>
                    <button className={styles.actionBtn}>
                      <span>Inspect Checklist ({reqs.length})</span>
                      <ArrowRight size={11} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
