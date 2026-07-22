import api from './api';
import type { Alert } from '../types';
import { mockAlerts, mockMaintenanceLogs } from '../mock/mockAlerts';

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

export const alertService = {
  getAll: async (): Promise<Alert[]> => {
    try {
      const { data } = await api.get('/alerts');
      if (data?.data?.length) {
        return data.data.map(mapAlertItem);
      }
    } catch {
      // fallback to mock
    }
    return Promise.resolve([...mockAlerts]);
  },

  getActive: async (): Promise<Alert[]> => {
    try {
      const { data } = await api.get('/alerts');
      if (data?.data?.length) {
        return data.data.filter((a: AlertApiItem) => a.status === 'active').map(mapAlertItem);
      }
    } catch {
      // fallback
    }
    return Promise.resolve(mockAlerts.filter((a) => a.status === 'active'));
  },

  getMaintenanceLogs: async () => {
    return Promise.resolve([...mockMaintenanceLogs]);
  },

  acknowledge: async (alertId: string): Promise<void> => {
    await api.post(`/alerts/${alertId}/acknowledge`);
  },

  resolve: async (alertId: string): Promise<void> => {
    await api.post(`/alerts/${alertId}/resolve`);
  },
};

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
