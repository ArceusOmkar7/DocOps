import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ocrApi } from '../api/ocr';

export function useOCRResults() {
  return useQuery({
    queryKey: ['ocrResults'],
    queryFn: () => ocrApi.listResults(),
  });
}

export function useOCRResult(resultId: string | undefined) {
  return useQuery({
    queryKey: ['ocrResult', resultId],
    queryFn: () => (resultId ? ocrApi.getResult(resultId).catch(() => null) : null),
    enabled: !!resultId,
    retry: false,
  });
}

export function useOCRMarkdown(resultId: string | undefined) {
  return useQuery({
    queryKey: ['ocrMarkdown', resultId],
    queryFn: async () => {
      if (!resultId) return '';
      try {
        const res = await fetch(ocrApi.getMarkdownUrl(resultId));
        if (!res.ok) return '';
        return res.text();
      } catch {
        return '';
      }
    },
    enabled: !!resultId,
    retry: false,
  });
}

export function useUploadDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (file: File) => ocrApi.extractDocument(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ocrResults'] });
    },
  });
}

export function useParseDocument() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      resultId,
      organizationId,
      clientId,
    }: {
      resultId: string;
      organizationId?: string;
      clientId?: string;
    }) =>
      ocrApi.parseDocument(resultId, {
        organization_id: organizationId,
        client_id: clientId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      queryClient.invalidateQueries({ queryKey: ['clients'] });
    },
  });
}
