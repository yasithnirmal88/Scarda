import api from './api';
import type { Inverter, PVString, Section } from '../types';

interface SectionApiItem {
  id?: number;
  code?: string;
  name?: string;
  description?: string;
}
interface InverterApiItem {
  id?: number;
  code?: string;
  name?: string;
  section_id?: number;
  sectionId?: number;
  status?: string;
}

function mapSection(item: SectionApiItem, index: number): Section {
  return {
    id: item.id ?? index + 1,
    name: item.name ?? item.code ?? `Section ${index + 1}`,
    inverterCount: 0,
    stringCount: 0,
    totalPower: 0,
  } as Section;
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

export const sectionService = {
  // All hierarchy data comes from the backend. No mock sections/inverters/strings
  // are generated in the frontend.
  getAll: async (): Promise<Section[]> => {
    const { data } = await api.get('/sections');
    return (data?.data ?? []).map(mapSection);
  },

  getById: async (id: number): Promise<Section | undefined> => {
    const { data } = await api.get(`/sections/${id}`);
    return data?.data ? mapSection(data.data, 0) : undefined;
  },

  getInverters: async (sectionId: number): Promise<Inverter[]> => {
    const { data } = await api.get('/inverters');
    return (data?.data ?? [])
      .filter((inv: InverterApiItem) => (inv.section_id ?? inv.sectionId) === sectionId)
      .map(mapInverter);
  },

  getStrings: async (inverterId: number): Promise<PVString[]> => {
    const { data } = await api.get('/strings');
    return (data?.data ?? [])
      .filter(
        (s: { inverter_id?: number; inverterId?: number }) =>
          (s.inverter_id ?? s.inverterId) === inverterId,
      )
      .map((s: unknown, i: number) => mapString(s as StringApiItem, i));
  },
};

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

interface StringApiItem {
  id?: number;
  code?: string;
  name?: string;
  inverter_id?: number;
  inverterId?: number;
  status?: string;
}
