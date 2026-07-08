import type { Inverter } from '../types';
import { generateMockInverters } from '../mock/mockSections';

const allInverters: Inverter[] = Array.from({ length: 4 }, (_, i) =>
  generateMockInverters(i + 1),
).flat();

export const inverterService = {
  getAll: async (): Promise<Inverter[]> => {
    return Promise.resolve([...allInverters]);
  },

  getBySection: async (sectionId: number): Promise<Inverter[]> => {
    return Promise.resolve(allInverters.filter((inv) => inv.sectionId === sectionId));
  },

  getById: async (id: number): Promise<Inverter | undefined> => {
    return Promise.resolve(allInverters.find((inv) => inv.id === id));
  },
};
