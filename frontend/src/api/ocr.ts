import { apiClient } from './client';
import { DocumentExtraction, OCRResult } from '../types/api';

export const ocrApi = {
  extractDocument(file: File): Promise<OCRResult> {
    return apiClient.upload<OCRResult>('/ocr/extract', file);
  },

  listResults(): Promise<{ results: any[]; total: number }> {
    return apiClient.get('/ocr/results');
  },

  getResult(resultId: string): Promise<OCRResult> {
    return apiClient.get<OCRResult>(`/ocr/results/${resultId}`);
  },

  parseDocument(
    resultId: string,
    params?: { organization_id?: string; client_id?: string }
  ): Promise<DocumentExtraction> {
    const query = new URLSearchParams();
    if (params?.organization_id) query.append('organization_id', params.organization_id);
    if (params?.client_id) query.append('client_id', params.client_id);
    const queryString = query.toString() ? `?${query.toString()}` : '';
    return apiClient.post<DocumentExtraction>(`/ocr/results/${resultId}/parse${queryString}`);
  },

  getSourceUrl(resultId: string): string {
    return `/api/v1/ocr/results/${resultId}/source`;
  },

  getMarkdownUrl(resultId: string): string {
    return `/api/v1/ocr/results/${resultId}/markdown`;
  },
};
