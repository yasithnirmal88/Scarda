import type { Alert, MaintenanceLog } from '../types';
import { mockAlerts, mockMaintenanceLogs } from '../mock/mockAlerts';

export const alertService = {
  getAll: async (): Promise<Alert[]> => {
    return Promise.resolve([...mockAlerts]);
  },

  getActive: async (): Promise<Alert[]> => {
    return Promise.resolve(mockAlerts.filter((a) => a.status === 'active'));
  },

  getMaintenanceLogs: async (): Promise<MaintenanceLog[]> => {
    return Promise.resolve([...mockMaintenanceLogs]);
  },
};
