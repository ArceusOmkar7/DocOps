import React, { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, Upload } from 'lucide-react';
import { ErrorState } from '../components/common/ErrorState';
import { PageHeader } from '../components/common/PageHeader';
import { ReadinessBar } from '../components/common/ReadinessBar';
import { StatusBadge } from '../components/common/StatusBadge';
import { useDrawer } from '../contexts/DrawerContext';
import { useClients } from '../hooks/useClients';
import { useDocuments } from '../hooks/useDocuments';
import { useWorkflows } from '../hooks/useWorkflows';
import { clientStatusLabel, documentTypeLabel, workflowStatusLabel } from '../lib/format';
import {
  documentBucket,
  emptyReadiness,
  openFilingFor,
  Readiness,
  tallyDocuments,
} from '../lib/readiness';
import ui from '../styles/ui.module.css';
import styles from './DashboardPage.module.css';

const ATTENTION_LIMIT = 8;

const plural = (n: number, one: string, many: string) => `${n} ${n === 1 ? one : many}`;

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { openDrawer } = useDrawer();
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  const clientsQuery = useClients();
  const docsQuery = useDocuments();
  const workflowsQuery = useWorkflows();

  const clients = clientsQuery.data ?? [];
  const documents = docsQuery.data ?? [];
  const workflows = workflowsQuery.data ?? [];

  const clientName = useMemo(
    () => new Map(clients.map((c) => [c.id, c.name])),
    [clients]
  );

  const readinessByClient = useMemo(() => {
    const map = new Map<string, Readiness>();
    for (const client of clients) {
      map.set(client.id, tallyDocuments(documents.filter((d) => d.client_id === client.id)));
    }
    return map;
  }, [clients, documents]);

  const totals = useMemo(() => tallyDocuments(documents), [documents]);

  const attention = useMemo(
    () =>
      documents
        .filter((d) => {
          const bucket = documentBucket(d);
          return bucket === 'review' || bucket === 'failed';
        })
        .sort((a, b) => {
          const rank = (d: typeof a) => (documentBucket(d) === 'review' ? 0 : 1);
          return rank(a) - rank(b) || b.uploaded_at.localeCompare(a.uploaded_at);
        }),
    [documents]
  );

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    return clients
      .filter((c) => {
        const matches =
          !q || c.name.toLowerCase().includes(q) || (c.tax_id ?? '').toLowerCase().includes(q);
        return matches && (statusFilter === 'ALL' || c.status === statusFilter);
      })
      .sort((a, b) => {
        const flagged = (id: string) => {
          const r = readinessByClient.get(id) ?? emptyReadiness();
          return r.review + r.failed;
        };
        return flagged(b.id) - flagged(a.id) || a.name.localeCompare(b.name);
      });
  }, [clients, query, statusFilter, readinessByClient]);

  const loading = clientsQuery.isLoading || docsQuery.isLoading;
  const failed = clientsQuery.isError || docsQuery.isError;

  const note = failed ? undefined : docsQuery.isLoading ? undefined : totals.review > 0 ? (
    <>
      <strong>{plural(totals.review, 'document needs', 'documents need')} your review.</strong>
      {totals.failed > 0 && ` ${plural(totals.failed, 'document', 'documents')} failed to extract.`}
    </>
  ) : totals.failed > 0 ? (
    `${plural(totals.failed, 'document', 'documents')} failed to extract.`
  ) : (
    'Nothing is waiting for your review.'
  );

  return (
    <div className={ui.page}>
      <PageHeader
        title="Desk"
        note={note}
        actions={
          <Link to="/documents?upload=1" className={ui.btnPrimary}>
            <Upload size={15} strokeWidth={1.75} aria-hidden="true" />
            Upload document
          </Link>
        }
      />

      <div className={styles.layout}>
        <section className={ui.panel} aria-labelledby="register-title">
          <div className={ui.panelHead}>
            <h2 id="register-title" className={ui.panelTitle}>
              Clients
              <span className={ui.panelCount}>{clients.length}</span>
            </h2>
            <div className={ui.tools}>
              <label className={ui.search}>
                <Search size={14} className={ui.searchIcon} aria-hidden="true" />
                <input
                  type="search"
                  className={ui.input}
                  placeholder="Search by name or GSTIN"
                  aria-label="Search clients by name or GSTIN"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </label>
              <select
                className={ui.select}
                aria-label="Filter by status"
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
              >
                <option value="ALL">All statuses</option>
                <option value="on_track">On track</option>
                <option value="awaiting_documents">Awaiting documents</option>
                <option value="review_required">Review required</option>
                <option value="action_required">Action required</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>

          {failed ? (
            <ErrorState what="the client register" />
          ) : loading ? (
            <div className={styles.skeletons} aria-busy="true" aria-label="Loading clients">
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className={ui.skeletonRow} />
              ))}
            </div>
          ) : rows.length === 0 ? (
            <div className={ui.empty}>
              <span className={ui.emptyTitle}>
                {clients.length === 0 ? 'No clients yet' : 'No clients match'}
              </span>
              <span className={ui.emptyText}>
                {clients.length === 0
                  ? 'Add your first client on the Clients page to start tracking filings.'
                  : 'Try a different name or GSTIN, or clear the status filter.'}
              </span>
            </div>
          ) : (
            <>
              <div className={ui.tableWrap}>
                <table className={ui.table}>
                  <thead>
                    <tr>
                      <th scope="col">Client</th>
                      <th scope="col">Open filing</th>
                      <th scope="col">Documents</th>
                      <th scope="col">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((client) => {
                      const readiness = readinessByClient.get(client.id) ?? emptyReadiness();
                      const filing = openFilingFor(client.id, workflows);
                      return (
                        <tr
                          key={client.id}
                          className={ui.rowLink}
                          onClick={() => navigate(`/documents?client=${client.id}`)}
                        >
                          <td>
                            <Link
                              to={`/documents?client=${client.id}`}
                              className={ui.primaryCell}
                              onClick={(e) => e.stopPropagation()}
                            >
                              {client.name}
                            </Link>
                            <span className={`${ui.sub} ${ui.id}`}>
                              {client.tax_id || 'No GSTIN on file'}
                            </span>
                          </td>
                          <td>
                            {filing ? (
                              <>
                                <span className={styles.filingName}>{filing.name}</span>
                                <span className={ui.sub}>{workflowStatusLabel(filing.status)}</span>
                              </>
                            ) : (
                              <span className={ui.muted}>No open filing</span>
                            )}
                          </td>
                          <td>
                            {readiness.total === 0 ? (
                              <span className={ui.muted}>No documents yet</span>
                            ) : (
                              <div className={styles.docs}>
                                <ReadinessBar readiness={readiness} />
                                <span className={styles.docsText}>
                                  {readiness.validated} of {readiness.total}
                                </span>
                              </div>
                            )}
                          </td>
                          <td>
                            <StatusBadge
                              status={client.status}
                              label={clientStatusLabel(client.status)}
                            />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>

              <div className={styles.totals}>
                <span>
                  {plural(rows.length, 'client', 'clients')}, {plural(totals.total, 'document', 'documents')}
                </span>
                <ul className={styles.legend} aria-label="Document totals">
                  <li><i className={`${styles.swatch} ${styles.sValidated}`} />{totals.validated} validated</li>
                  <li><i className={`${styles.swatch} ${styles.sReview}`} />{totals.review} in review</li>
                  <li><i className={`${styles.swatch} ${styles.sFailed}`} />{totals.failed} failed</li>
                  <li><i className={`${styles.swatch} ${styles.sPending}`} />{totals.pending} pending</li>
                </ul>
              </div>
            </>
          )}
        </section>

        <section className={ui.panel} aria-labelledby="attention-title">
          <div className={ui.panelHead}>
            <h2 id="attention-title" className={ui.panelTitle}>
              Needs your attention
              {attention.length > 0 && <span className={ui.panelCount}>{attention.length}</span>}
            </h2>
          </div>

          {docsQuery.isError ? (
            <ErrorState what="documents" />
          ) : docsQuery.isLoading ? (
            <div className={styles.skeletons} aria-busy="true" aria-label="Loading documents">
              {[0, 1, 2].map((i) => (
                <div key={i} className={ui.skeletonRow} />
              ))}
            </div>
          ) : attention.length === 0 ? (
            <div className={ui.empty}>
              <span className={ui.emptyTitle}>Nothing to review</span>
              <span className={ui.emptyText}>
                Documents the checks flag will appear here with the reason they were flagged.
              </span>
            </div>
          ) : (
            <>
              <ul className={styles.queue}>
                {attention.slice(0, ATTENTION_LIMIT).map((doc) => {
                  const isFailed = documentBucket(doc) === 'failed';
                  return (
                    <li key={doc.id}>
                      <button
                        className={styles.queueItem}
                        onClick={() => openDrawer(doc.id, doc.ocr_result_id || undefined)}
                      >
                        <span className={styles.queueTop}>
                          <span className={styles.queueFile}>{doc.source_filename}</span>
                          <span className={isFailed ? styles.tagFailed : styles.tagReview}>
                            {isFailed ? 'Failed' : 'Review'}
                          </span>
                        </span>
                        <span className={ui.sub}>
                          {clientName.get(doc.client_id) ?? 'Unknown client'} · {documentTypeLabel(doc.document_type)}
                        </span>
                        <span className={styles.reason}>
                          {doc.review_reason ||
                            (isFailed ? 'Extraction failed.' : 'Flagged for human review.')}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
              {attention.length > ATTENTION_LIMIT && (
                <Link to="/documents?show=review" className={styles.viewAll}>
                  See all {attention.length} in Documents
                </Link>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
};
