import api from './api';
import type { ChartDataPoint } from '../types';

export interface ReadingResponse {
  status: string;
  current: Record<string, unknown>[];
  history: Record<string, unknown>[];
  total_power_kw?: number;
  active_inverters?: number;
  timestamp?: string;
}

export const readingService = {
  getCurrent: async (): Promise<ReadingResponse> => {
    const { data } = await api.get('/readings/current');
    return data;
  },
  getAll: async (): Promise<ReadingResponse> => {
    const { data } = await api.get('/readings');
    return data;
  },
  getHistory: async (limit = 100): Promise<{ status: string; data: Record<string, unknown>[] }> => {
    const { data } = await api.get(`/readings/history?limit=${limit}`);
    return data;
  },
};
