import api from './api';
import type { Inverter } from '../types';

interface InverterApiItem {
  id?: number;
  code?: string;
  name?: string;
  section_id?: number;
  sectionId?: number;
  status?: string;
}

function mapInverter(item: InverterApiItem, index: number): Inverter {
  return {
    id: item.id ?? index + 1,
    sectionId: item.section_id ?? item.sectionId ?? 0,
    name: item.name ?? item.code ?? `Inverter ${index + 1}`,
    status: (item.status as Inverter['status']) ?? 'active',
    power: 0,
  } as Inverter;
}

export const inverterService = {
  // Inverters come from the backend /inverters endpoint. No mock inverters.
  getAll: async (): Promise<Inverter[]> => {
    const { data } = await api.get('/inverters');
    return (data?.data ?? []).map(mapInverter);
  },

  getBySection: async (sectionId: number): Promise<Inverter[]> => {
    const { data } = await api.get('/inverters');
    return (data?.data ?? [])
      .filter((inv: InverterApiItem) => (inv.section_id ?? inv.sectionId) === sectionId)
      .map(mapInverter);
  },

  getById: async (id: number): Promise<Inverter | undefined> => {
    const { data } = await api.get(`/inverters/${id}`);
    return data?.data ? mapInverter(data.data, 0) : undefined;
  },
};
