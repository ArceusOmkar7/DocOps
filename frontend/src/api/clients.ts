import { apiClient } from './client';
import { Client, ClientCreate, ClientStatus, ClientUpdate } from '../types/api';

export const clientsApi = {
  listClients(params?: { organization_id?: string; status?: ClientStatus }): Promise<Client[]> {
    const query = new URLSearchParams();
    if (params?.organization_id) query.append('organization_id', params.organization_id);
    if (params?.status) query.append('status', params.status);
    const queryString = query.toString() ? `?${query.toString()}` : '';
    return apiClient.get<Client[]>(`/clients${queryString}`);
  },

  getClient(clientId: string): Promise<Client> {
    return apiClient.get<Client>(`/clients/${clientId}`);
  },

  createClient(data: ClientCreate): Promise<Client> {
    return apiClient.post<Client>('/clients', data);
  },

  updateClient(clientId: string, data: ClientUpdate): Promise<Client> {
    return apiClient.patch<Client>(`/clients/${clientId}`, data);
  },
};
