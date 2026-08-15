import api from './api';
import type { Report } from '../types';

interface ReportApiItem {
  id?: number;
  title?: string;
  type?: string;
  generated_at?: string;
  generatedAt?: string;
  status?: string;
}

function mapReport(item: ReportApiItem, index: number): Report {
  return {
    id: item.id ?? index + 1,
    title: item.title ?? `Report ${index + 1}`,
    type: (item.type as Report['type']) ?? 'daily',
    generatedAt: item.generated_at ?? item.generatedAt ?? new Date().toISOString(),
    status: (item.status as Report['status']) ?? 'ready',
  };
}

export const reportService = {
  // Reports come from the backend /reports endpoint. No mock reports.
  getAll: async (): Promise<Report[]> => {
    const { data } = await api.get('/reports');
    return (data?.data ?? []).map(mapReport);
  },

  generate: async (type: string): Promise<Report> => {
    const { data } = await api.post('/reports/generate', { type });
    const item = data?.data ?? {};
    return mapReport({ ...item, type: item.type ?? type }, 0);
  },
};
