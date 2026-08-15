import api from './api';
import type { PVString } from '../types';

interface StringApiItem {
  id?: number;
  code?: string;
  name?: string;
  inverter_id?: number;
  inverterId?: number;
  status?: string;
}

function mapString(item: StringApiItem, index: number): PVString {
  return {
    id: item.id ?? index + 1,
    inverterId: item.inverter_id ?? item.inverterId ?? 0,
    name: item.name ?? item.code ?? `String ${index + 1}`,
    status: (item.status as PVString['status']) ?? 'active',
    power: 0,
    voltage: 0,
    current: 0,
  } as PVString;
}

export const stringService = {
  // Strings come from the backend /strings endpoint (populated from the live
  // provider data). No mock string generation in the frontend.
  getAll: async (): Promise<PVString[]> => {
    const { data } = await api.get('/strings');
    return (data?.data ?? []).map(mapString);
  },

  getByInverter: async (inverterId: number): Promise<PVString[]> => {
    const { data } = await api.get('/strings');
    return (data?.data ?? [])
      .filter((s: StringApiItem) => (s.inverter_id ?? s.inverterId) === inverterId)
      .map(mapString);
  },
};
