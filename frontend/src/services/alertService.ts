import api from './api';
import type { Alert, MaintenanceLog } from '../types';

export interface AlertApiItem {
  alert_id: string;
  timestamp: string;
  section: string;
  inverter: string;
  string: string;
  alert_type: string;
  severity: string;
  status: string;
  reason: string;
}

export interface MaintenanceLogApiItem {
  id?: number | string;
  title?: string;
  description?: string;
  section?: string;
  inverter_id?: number | null;
  string_id?: number | null;
  user_id?: number;
  date?: string;
  scheduled_date?: string;
  completed_date?: string | null;
  status?: string;
  technician?: string;
  created_at?: string;
}

function mapAlertItem(item: AlertApiItem): Alert {
  return {
    id: parseInt(item.alert_id.replace(/\D/g, ''), 10) || Math.random(),
    inverterId: null,
    stringId: null,
    type: item.alert_type,
    severity: item.severity as Alert['severity'],
    title: item.reason,
    message: item.reason,
    source: item.string || item.inverter,
    timestamp: item.timestamp,
    status: item.status as Alert['status'],
    createdAt: item.timestamp,
    resolvedAt: null,
  };
}

function mapMaintenance(item: MaintenanceLogApiItem, index: number): MaintenanceLog {
  return {
    id: typeof item.id === 'number' ? item.id : parseInt(String(item.id ?? index + 1).replace(/\D/g, ''), 10) || index + 1,
    inverterId: item.inverter_id ?? null,
    stringId: item.string_id ?? null,
    userId: item.user_id ?? 0,
    title: item.title ?? '',
    description: item.description ?? '',
    section: item.section ?? '',
    date: item.date ?? item.created_at ?? new Date().toISOString(),
    technician: item.technician ?? '',
    scheduledDate: item.scheduled_date ?? new Date().toISOString(),
    completedDate: item.completed_date ?? null,
    status: (item.status as MaintenanceLog['status']) ?? 'scheduled',
    createdAt: item.created_at ?? new Date().toISOString(),
  };
}

export const alertService = {
  // All alert data comes from the backend. No mock/hardcoded alerts remain —
  // the frontend never fabricates alert data.
  getAll: async (): Promise<Alert[]> => {
    const { data } = await api.get('/alerts');
    return (data?.data ?? []).map(mapAlertItem);
  },

  getActive: async (): Promise<Alert[]> => {
    const { data } = await api.get('/alerts');
    return (data?.data ?? [])
      .filter((a: AlertApiItem) => a.status === 'active')
      .map(mapAlertItem);
  },

  getMaintenanceLogs: async (): Promise<MaintenanceLog[]> => {
    const { data } = await api.get('/maintenance');
    return (data?.data ?? []).map(mapMaintenance);
  },

  acknowledge: async (alertId: string): Promise<void> => {
    await api.post(`/alerts/${alertId}/acknowledge`);
  },

  resolve: async (alertId: string): Promise<void> => {
    await api.post(`/alerts/${alertId}/resolve`);
  },
};
