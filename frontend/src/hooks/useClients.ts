import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { clientsApi } from '../api/clients';
import { ClientCreate, ClientStatus, ClientUpdate } from '../types/api';

export function useClients(filters?: { organization_id?: string; status?: ClientStatus }) {
  return useQuery({
    queryKey: ['clients', filters],
    queryFn: () => clientsApi.listClients(filters),
    staleTime: 10000,
  });
}

export function useClient(clientId: string | undefined) {
  return useQuery({
    queryKey: ['client', clientId],
    queryFn: () => (clientId ? clientsApi.getClient(clientId) : null),
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
