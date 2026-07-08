import type { PVString } from '../types';
import { generateMockStrings } from '../mock/mockSections';

const allStrings: PVString[] = Array.from({ length: 36 }, (_, i) =>
  generateMockStrings(i + 1),
).flat();

export const stringService = {
  getAll: async (): Promise<PVString[]> => {
    return Promise.resolve([...allStrings]);
  },

  getByInverter: async (inverterId: number): Promise<PVString[]> => {
    return Promise.resolve(allStrings.filter((s) => s.inverterId === inverterId));
  },
};
