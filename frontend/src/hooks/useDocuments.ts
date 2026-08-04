import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { documentsApi } from '../api/documents';
import { DocumentStatus, DocumentType } from '../types/api';

export function useDocuments(filters?: {
  client_id?: string;
  organization_id?: string;
  document_type?: DocumentType;
  status?: DocumentStatus;
  needs_review?: boolean;
}) {
  return useQuery({
    queryKey: ['documents', filters],
    queryFn: () => documentsApi.listDocuments(filters),
    staleTime: 30000,
  });
}

export function useDocument(documentId: string | undefined) {
  return useQuery({
    queryKey: ['document', documentId],
    queryFn: () => (documentId ? documentsApi.getDocument(documentId) : null),
    enabled: !!documentId,
  });
}

export function useAttachDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      documentId,
      workflowId,
      requirementId,
    }: {
      documentId: string;
      workflowId: string;
      requirementId?: string | null;
    }) =>
      documentsApi.attachToWorkflow(documentId, {
        workflow_id: workflowId,
        requirement_id: requirementId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    },
  });
}
