import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { clientsApi } from '../api/clients';
import { ClientCreate, ClientStatus, ClientUpdate } from '../types/api';
import { DEMO_CLIENTS } from '../data/demoData';

export function useClients(filters?: { organization_id?: string; status?: ClientStatus }) {
  return useQuery({
    queryKey: ['clients', filters],
    queryFn: async () => {
      try {
        const data = await clientsApi.listClients(filters);
        if (!data || data.length === 0) {
          return DEMO_CLIENTS;
        }
        return data;
      } catch (err) {
        // Fallback to demo dataset if backend Postgres has no records yet
        return DEMO_CLIENTS;
      }
    },
    staleTime: 30000,
  });
}

export function useClient(clientId: string | undefined) {
  return useQuery({
    queryKey: ['client', clientId],
    queryFn: async () => {
      if (!clientId) return null;
      try {
        return await clientsApi.getClient(clientId);
      } catch (err) {
        return DEMO_CLIENTS.find((c) => c.id === clientId) || DEMO_CLIENTS[0];
      }
    },
    enabled: !!clientId,
  });
}

export function useCreateClient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: ClientCreate) => clientsApi.createClient(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    },
  });
}

export function useUpdateClient() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: ClientUpdate }) =>
      clientsApi.updateClient(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['clients'] });
      queryClient.invalidateQueries({ queryKey: ['client', variables.id] });
    },
  });
}
