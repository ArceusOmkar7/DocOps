import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { workflowsApi } from '../api/workflows';
import { WorkflowCreate, WorkflowStatus, WorkflowUpdate } from '../types/api';

export function useWorkflows(filters?: {
  client_id?: string;
  organization_id?: string;
  status?: WorkflowStatus;
}) {
  return useQuery({
    queryKey: ['workflows', filters],
    queryFn: () => workflowsApi.listWorkflows(filters),
    staleTime: 30000,
  });
}

export function useWorkflow(workflowId: string | undefined) {
  return useQuery({
    queryKey: ['workflow', workflowId],
    queryFn: () => (workflowId ? workflowsApi.getWorkflow(workflowId) : null),
    enabled: !!workflowId,
  });
}

export function useCreateWorkflow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: WorkflowCreate) => workflowsApi.createWorkflow(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
    },
  });
}

export function useUpdateWorkflow() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: WorkflowUpdate }) =>
      workflowsApi.updateWorkflow(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['workflows'] });
      queryClient.invalidateQueries({ queryKey: ['workflow', variables.id] });
    },
  });
}
