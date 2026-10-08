import { DbDocument, Workflow } from '../types/api';
import { DocumentStatus, WorkflowStatus } from '../types/enums';

export type DocBucket = 'validated' | 'review' | 'failed' | 'pending';

/** The one place that decides which readiness bucket a document falls in. */
export const documentBucket = (doc: DbDocument): DocBucket => {
  if (doc.status === DocumentStatus.FAILED || doc.status === DocumentStatus.REJECTED) {
    return 'failed';
  }
  if (doc.needs_human_review || doc.status === DocumentStatus.NEEDS_REVIEW) return 'review';
  if (doc.status === DocumentStatus.VALIDATED) return 'validated';
  return 'pending';
};

export interface Readiness {
  total: number;
  validated: number;
  review: number;
  failed: number;
  pending: number;
}

export const emptyReadiness = (): Readiness => ({
  total: 0,
  validated: 0,
  review: 0,
  failed: 0,
  pending: 0,
});

export const tallyDocuments = (docs: DbDocument[]): Readiness =>
  docs.reduce((acc, doc) => {
    acc.total += 1;
    acc[documentBucket(doc)] += 1;
    return acc;
  }, emptyReadiness());

/** The filing a client is working on now: the newest one that is not completed. */
export const openFilingFor = (clientId: string, workflows: Workflow[]): Workflow | undefined =>
  workflows
    .filter((w) => w.client_id === clientId && w.status !== WorkflowStatus.COMPLETED)
    .sort((a, b) => b.period_end.localeCompare(a.period_end))[0];
