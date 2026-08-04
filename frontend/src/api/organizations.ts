import { apiClient } from './client';
import { Organization, OrganizationCreate } from '../types/api';

export const organizationsApi = {
  listOrganizations(): Promise<Organization[]> {
    return apiClient.get<Organization[]>('/organizations');
  },

  getOrganization(orgId: string): Promise<Organization> {
    return apiClient.get<Organization>(`/organizations/${orgId}`);
  },

  createOrganization(data: OrganizationCreate): Promise<Organization> {
    return apiClient.post<Organization>('/organizations', data);
  },
};
