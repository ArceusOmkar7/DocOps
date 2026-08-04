import React, { useState } from 'react';
import { ArrowRight, GitPullRequest, Loader2, Plus, Sparkles } from 'lucide-react';
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
      alert('Please create at least one client before launching a workflow.');
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
      alert(`Failed to launch workflow: ${err.message}`);
    }
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
            <h3 className={styles.cardTitle}>Active Client Workflows ({workflows.length})</h3>
            <span className={styles.cardSubtitle}>
              Live client document checklists & automated status progression stored in PostgreSQL
            </span>
          </div>
        </div>

        {isLoading ? (
          <div style={{ padding: 40, textAlign: 'center', color: '#64748b' }}>
            <Loader2 size={24} className="animate-spin" style={{ margin: '0 auto 8px' }} />
            <span>Fetching workflows...</span>
          </div>
        ) : workflows.length === 0 ? (
          <div style={{ padding: 48, textAlign: 'center', color: '#64748b' }}>
            <GitPullRequest size={36} style={{ margin: '0 auto 12px', opacity: 0.5 }} />
            <div style={{ fontSize: 16, fontWeight: 600, color: '#0f172a' }}>
              No Active Workflows
            </div>
            <div style={{ fontSize: 13, marginTop: 4 }}>
              Click "Launch New Workflow" above to create an automated compliance checklist for your clients.
            </div>
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
                        <GitPullRequest size={16} />
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
                      Checklist Requirements: {reqs.length} Mandatory Document Items
                    </span>
                    <button className={styles.actionBtn}>
                      <span>Inspect Checklist ({reqs.length} items)</span>
                      <ArrowRight size={12} />
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
