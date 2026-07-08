import type { Inverter, PVString, Section } from '../types';

export const mockSections: Section[] = [
  { id: 1, name: 'Section A', description: 'North field array', inverterCount: 9, stringCount: 216, totalPower: 612_500, status: 'healthy' },
  { id: 2, name: 'Section B', description: 'East field array', inverterCount: 9, stringCount: 216, totalPower: 598_200, status: 'healthy' },
  { id: 3, name: 'Section C', description: 'South field array', inverterCount: 9, stringCount: 216, totalPower: 436_800, status: 'warning' },
  { id: 4, name: 'Section D', description: 'West field array', inverterCount: 9, stringCount: 216, totalPower: 803_000, status: 'healthy' },
];

export function generateMockInverters(sectionId: number): Inverter[] {
  const statuses: Inverter['status'][] = ['online', 'online', 'online', 'online', 'online', 'online', 'online', 'online', 'offline'];
  return Array.from({ length: 9 }, (_, i) => ({
    id: (sectionId - 1) * 9 + i + 1,
    sectionId,
    name: `INV-${String((sectionId - 1) * 9 + i + 1).padStart(3, '0')}`,
    modelNumber: 'SUN2000-50KTL',
    status: statuses[Math.min(i, statuses.length - 1)] as Inverter['status'],
    power: 50_000 + Math.random() * 15_000,
    voltage: 800 + Math.random() * 40,
    current: 60 + Math.random() * 10,
    temperature: 35 + Math.random() * 10,
    efficiency: 94 + Math.random() * 3,
    stringCount: 24,
  }));
}

export function generateMockStrings(inverterId: number): PVString[] {
  const statuses: PVString['status'][] = ['active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'active', 'error'];
  return Array.from({ length: 24 }, (_, i) => ({
    id: (inverterId - 1) * 24 + i + 1,
    inverterId,
    name: `STR-${String((inverterId - 1) * 24 + i + 1).padStart(4, '0')}`,
    panelCount: 20,
    voltage: 800 + Math.random() * 40,
    current: 9 + Math.random() * 2,
    power: 7200 + Math.random() * 1500,
    temperature: 35 + Math.random() * 15,
    status: statuses[Math.min(i, statuses.length - 1)] as PVString['status'],
    degradation: Math.random() * 0.05,
  }));
}

export function getSectionByName(name: string): Section | undefined {
  return mockSections.find((s) => s.name === name);
}
