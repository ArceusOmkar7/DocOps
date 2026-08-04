import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { organizationsApi } from '../api/organizations';
import { OrganizationCreate } from '../types/api';

export function useOrganizations() {
  return useQuery({
    queryKey: ['organizations'],
    queryFn: () => organizationsApi.listOrganizations(),
    staleTime: 60000,
  });
}

export function useCreateOrganization() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: OrganizationCreate) => organizationsApi.createOrganization(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
  });
}
