import { apiClient } from './client';
import { DbDocument, DocumentStatus, DocumentType } from '../types/api';

export const documentsApi = {
  listDocuments(params?: {
    client_id?: string;
    organization_id?: string;
    document_type?: DocumentType;
    status?: DocumentStatus;
    needs_review?: boolean;
  }): Promise<DbDocument[]> {
    const query = new URLSearchParams();
    if (params?.client_id) query.append('client_id', params.client_id);
    if (params?.organization_id) query.append('organization_id', params.organization_id);
    if (params?.document_type) query.append('document_type', params.document_type);
    if (params?.status) query.append('status', params.status);
    if (params?.needs_review !== undefined) query.append('needs_review', String(params.needs_review));
    const queryString = query.toString() ? `?${query.toString()}` : '';
    return apiClient.get<DbDocument[]>(`/documents${queryString}`);
  },

  getDocument(documentId: string): Promise<DbDocument> {
    return apiClient.get<DbDocument>(`/documents/${documentId}`);
  },

  attachToWorkflow(
    documentId: string,
    data: { workflow_id: string; requirement_id?: string | null }
  ): Promise<{ message: string }> {
    return apiClient.post<{ message: string }>(`/documents/${documentId}/attach`, data);
  },
};
