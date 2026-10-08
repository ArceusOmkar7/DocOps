import React, { useMemo, useState } from 'react';
import { ChevronDown, ChevronRight, Plus, X } from 'lucide-react';
import { ErrorState } from '../components/common/ErrorState';
import { PageHeader } from '../components/common/PageHeader';
import { WorkflowTemplateSelector } from '../components/workflows/WorkflowTemplateSelector';
import { WorkflowTimeline } from '../components/workflows/WorkflowTimeline';
import { useClients } from '../hooks/useClients';
import { useCreateWorkflow, useWorkflows } from '../hooks/useWorkflows';
import { WorkflowTemplate } from '../data/workflowTemplates';
import { documentTypeLabel, formatPeriod } from '../lib/format';
import { DocumentType } from '../types/api';
import ui from '../styles/ui.module.css';
import styles from './WorkflowsPage.module.css';

export const WorkflowsPage: React.FC = () => {
  const [showNew, setShowNew] = useState(false);
  const [clientId, setClientId] = useState('');
  const [expanded, setExpanded] = useState<string | null>(null);
  const [createError, setCreateError] = useState('');

  const { data: workflows = [], isLoading, isError } = useWorkflows();
  const { data: clients = [] } = useClients();
  const createWorkflow = useCreateWorkflow();

  const clientName = useMemo(() => new Map(clients.map((c) => [c.id, c.name])), [clients]);
  const selectedClient = clients.find((c) => c.id === clientId) ?? clients[0];

  const startFiling = async (tmpl: WorkflowTemplate) => {
    if (!selectedClient) return;
    setCreateError('');
    try {
      await createWorkflow.mutateAsync({
        organization_id: selectedClient.organization_id,
        client_id: selectedClient.id,
        name: `${tmpl.name}, current period`,
        workflow_type: tmpl.type,
        period_start: new Date().toISOString().substring(0, 10),
        period_end: new Date(Date.now() + 30 * 86400000).toISOString().substring(0, 10),
        requirements: tmpl.requirements.map((req) => ({
          label: req.label,
          document_type: req.document_type || DocumentType.INVOICE,
          required_count: req.required_count || 1,
        })),
      });
      setShowNew(false);
    } catch (err) {
      setCreateError(err instanceof Error ? err.message : 'The filing could not be created.');
    }
  };

  return (
    <div className={ui.page}>
      <PageHeader
        title="Filings"
        actions={
          <button className={ui.btnPrimary} onClick={() => setShowNew(!showNew)}>
            {showNew ? (
              <X size={15} strokeWidth={1.75} aria-hidden="true" />
            ) : (
              <Plus size={15} strokeWidth={1.75} aria-hidden="true" />
            )}
            {showNew ? 'Cancel' : 'New filing'}
          </button>
        }
      />

      {showNew && (
        <section className={ui.panel} aria-label="Start a filing">
          <div className={ui.panelHead}>
            <h2 className={ui.panelTitle}>Start a filing</h2>
            <div className={ui.field} style={{ flexDirection: 'row', alignItems: 'center', gap: 10 }}>
              <label className={ui.label} htmlFor="filing-client">
                For client
              </label>
              <select
                id="filing-client"
                className={ui.select}
                value={selectedClient?.id ?? ''}
                onChange={(e) => setClientId(e.target.value)}
              >
                {clients.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          {clients.length === 0 ? (
            <div className={ui.empty}>
              <span className={ui.emptyTitle}>Add a client first</span>
              <span className={ui.emptyText}>
                A filing belongs to a client. Register one on the Clients page, then come back.
              </span>
            </div>
          ) : (
            <WorkflowTemplateSelector
              onSelectTemplate={startFiling}
              disabled={createWorkflow.isPending}
            />
          )}
          {createError && (
            <p className={ui.errorText} role="alert" style={{ padding: '0 16px 14px' }}>
              {createError}
            </p>
          )}
        </section>
      )}

      <section className={ui.panel} aria-label="Filings">
        <div className={ui.panelHead}>
          <h2 className={ui.panelTitle}>
            All filings
            <span className={ui.panelCount}>{workflows.length}</span>
          </h2>
        </div>

        {isError ? (
          <ErrorState what="filings" />
        ) : isLoading ? (
          <div className={ui.empty} aria-busy="true">
            <div className={ui.skeletonRow} style={{ width: '60%' }} />
          </div>
        ) : workflows.length === 0 ? (
          <div className={ui.empty}>
            <span className={ui.emptyTitle}>No filings yet</span>
            <span className={ui.emptyText}>
              Start a GST, TDS or ITR filing and Patra will track which documents are still missing.
            </span>
          </div>
        ) : (
          <div className={ui.tableWrap}>
            <table className={ui.table}>
              <thead>
                <tr>
                  <th scope="col" aria-label="Checklist" style={{ width: 36 }} />
                  <th scope="col">Filing</th>
                  <th scope="col">Client</th>
                  <th scope="col">Period</th>
                  <th scope="col">Stage</th>
                  <th scope="col" className={ui.num}>Required documents</th>
                </tr>
              </thead>
              <tbody>
                {workflows.map((wf) => {
                  const open = expanded === wf.id;
                  const requirements = wf.requirements ?? [];
                  return (
                    <React.Fragment key={wf.id}>
                      <tr
                        className={ui.rowLink}
                        onClick={() => setExpanded(open ? null : wf.id)}
                      >
                        <td>
                          <button
                            className={styles.toggle}
                            aria-expanded={open}
                            aria-label={`${open ? 'Hide' : 'Show'} checklist for ${wf.name}`}
                            onClick={(e) => {
                              e.stopPropagation();
                              setExpanded(open ? null : wf.id);
                            }}
                          >
                            {open ? (
                              <ChevronDown size={16} strokeWidth={1.75} aria-hidden="true" />
                            ) : (
                              <ChevronRight size={16} strokeWidth={1.75} aria-hidden="true" />
                            )}
                          </button>
                        </td>
                        <td className={styles.filingName}>{wf.name}</td>
                        <td>{clientName.get(wf.client_id) ?? <span className={ui.muted}>Unknown</span>}</td>
                        <td style={{ whiteSpace: 'nowrap' }}>
                          {formatPeriod(wf.period_start, wf.period_end)}
                        </td>
                        <td>
                          <WorkflowTimeline status={wf.status} />
                        </td>
                        <td className={ui.num}>{requirements.length}</td>
                      </tr>
                      {open && (
                        <tr>
                          <td />
                          <td colSpan={5} className={styles.checklistCell}>
                            {requirements.length === 0 ? (
                              <span className={ui.muted}>This filing has no required documents.</span>
                            ) : (
                              <ul className={styles.checklist}>
                                {requirements.map((req) => (
                                  <li key={req.id}>
                                    <span>{req.label}</span>
                                    <span className={ui.muted}>
                                      {documentTypeLabel(req.document_type)}
                                      {req.required_count ? `, ${req.required_count} needed` : ''}
                                    </span>
                                  </li>
                                ))}
                              </ul>
                            )}
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};
