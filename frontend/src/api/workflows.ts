import { apiClient } from './client';
import { Workflow, WorkflowCreate, WorkflowStatus, WorkflowUpdate } from '../types/api';

export const workflowsApi = {
  listWorkflows(params?: {
    client_id?: string;
    organization_id?: string;
    status?: WorkflowStatus;
  }): Promise<Workflow[]> {
    const query = new URLSearchParams();
    if (params?.client_id) query.append('client_id', params.client_id);
    if (params?.organization_id) query.append('organization_id', params.organization_id);
    if (params?.status) query.append('status', params.status);
    const queryString = query.toString() ? `?${query.toString()}` : '';
    return apiClient.get<Workflow[]>(`/workflows${queryString}`);
  },

  getWorkflow(workflowId: string): Promise<Workflow> {
    return apiClient.get<Workflow>(`/workflows/${workflowId}`);
  },

  createWorkflow(data: WorkflowCreate): Promise<Workflow> {
    return apiClient.post<Workflow>('/workflows', data);
  },

  updateWorkflow(workflowId: string, data: WorkflowUpdate): Promise<Workflow> {
    return apiClient.patch<Workflow>(`/workflows/${workflowId}`, data);
  },
};
