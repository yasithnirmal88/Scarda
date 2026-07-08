import type { Inverter, PVString, Section } from '../types';
import { generateMockInverters, generateMockStrings, mockSections } from '../mock/mockSections';

export const sectionService = {
  getAll: async (): Promise<Section[]> => {
    return Promise.resolve([...mockSections]);
  },

  getById: async (id: number): Promise<Section | undefined> => {
    return Promise.resolve(mockSections.find((s) => s.id === id));
  },

  getInverters: async (sectionId: number): Promise<Inverter[]> => {
    return Promise.resolve(generateMockInverters(sectionId));
  },

  getStrings: async (inverterId: number): Promise<PVString[]> => {
    return Promise.resolve(generateMockStrings(inverterId));
  },
};
