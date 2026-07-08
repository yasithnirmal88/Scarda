import type { Report } from '../types';

const mockReports: Report[] = [
  { id: 1, title: 'Daily Report — 2026-07-07', type: 'daily', generatedAt: new Date().toISOString(), status: 'ready' },
  { id: 2, title: 'Weekly Report — Week 27', type: 'weekly', generatedAt: new Date(Date.now() - 86_400_000).toISOString(), status: 'ready' },
  { id: 3, title: 'Monthly Report — June 2026', type: 'monthly', generatedAt: new Date(Date.now() - 604_800_000).toISOString(), status: 'ready' },
];

export const reportService = {
  getAll: async (): Promise<Report[]> => {
    return Promise.resolve([...mockReports]);
  },

  generate: async (type: string): Promise<Report> => {
    const report: Report = {
      id: Date.now(),
      title: `${type.charAt(0).toUpperCase() + type.slice(1)} Report`,
      type: type as Report['type'],
      generatedAt: new Date().toISOString(),
      status: 'ready',
    };
    return Promise.resolve(report);
  },
};
