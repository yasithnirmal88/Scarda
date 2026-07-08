import type { Alert, MaintenanceLog } from '../types';

const ts = (offset: number) => new Date(Date.now() - offset).toISOString();

export const mockAlerts: Alert[] = [
  { id: 1, inverterId: 1, stringId: null, type: 'Overheating', severity: 'critical', title: 'Inverter Overheating', message: 'Inverter INV-001 temperature exceeds 85°C threshold', source: 'INV-001', timestamp: ts(0), status: 'active', createdAt: ts(0), resolvedAt: null },
  { id: 2, inverterId: null, stringId: 12, type: 'Low Power', severity: 'warning', title: 'String Underperformance', message: 'String STR-012 producing 40% below expected power', source: 'STR-012', timestamp: ts(900_000), status: 'active', createdAt: ts(900_000), resolvedAt: null },
  { id: 3, inverterId: 5, stringId: null, type: 'Communication Lost', severity: 'critical', title: 'Communication Lost', message: 'Inverter INV-005 communication timeout', source: 'INV-005', timestamp: ts(3_600_000), status: 'active', createdAt: ts(3_600_000), resolvedAt: null },
  { id: 4, inverterId: null, stringId: 87, type: 'High Voltage', severity: 'warning', title: 'Voltage Spike', message: 'String STR-087 voltage spike detected: 945V', source: 'STR-087', timestamp: ts(7_200_000), status: 'acknowledged', createdAt: ts(7_200_000), resolvedAt: null },
  { id: 5, inverterId: 12, stringId: null, type: 'Efficiency Drop', severity: 'warning', title: 'Efficiency Drop', message: 'Inverter INV-012 efficiency dropped to 87%', source: 'INV-012', timestamp: ts(14_400_000), status: 'active', createdAt: ts(14_400_000), resolvedAt: null },
  { id: 6, inverterId: null, stringId: 234, type: 'Dirty Panel', severity: 'info', title: 'Soiling Detected', message: 'String STR-234 current drop suggests soiling', source: 'STR-234', timestamp: ts(86_400_000), status: 'active', createdAt: ts(86_400_000), resolvedAt: null },
  { id: 7, inverterId: null, stringId: 456, type: 'Partial Shading', severity: 'info', title: 'Partial Shading', message: 'String STR-456 possible partial shading detected', source: 'STR-456', timestamp: ts(172_800_000), status: 'resolved', createdAt: ts(172_800_000), resolvedAt: ts(86_400_000) },
  { id: 8, inverterId: 22, stringId: null, type: 'Maintenance Required', severity: 'info', title: 'Maintenance Required', message: 'Inverter INV-022 filter replacement due', source: 'INV-022', timestamp: ts(259_200_000), status: 'active', createdAt: ts(259_200_000), resolvedAt: null },
];

const d = (offset: number) => new Date(Date.now() + offset).toISOString().slice(0, 10);

export const mockMaintenanceLogs: MaintenanceLog[] = [
  { id: 1, inverterId: 9, stringId: null, userId: 1, title: 'Inverter firmware update', description: 'Upgrade to v3.2.1', section: 'Section A', date: d(86_400_000), technician: 'Alice Chen', scheduledDate: d(86_400_000), completedDate: null, status: 'scheduled', createdAt: new Date(Date.now() - 86_400_000).toISOString() },
  { id: 2, inverterId: null, stringId: 45, userId: 1, title: 'String inspection', description: 'Check connectors and wiring', section: 'Section B', date: d(-86_400_000), technician: 'Bob Martinez', scheduledDate: d(-86_400_000), completedDate: new Date().toISOString(), status: 'completed', createdAt: new Date(Date.now() - 172_800_000).toISOString() },
  { id: 3, inverterId: 15, stringId: null, userId: 2, title: 'Coolant replacement', description: 'Replace inverter coolant', section: 'Section C', date: d(604_800_000), technician: 'Alice Chen', scheduledDate: d(604_800_000), completedDate: null, status: 'scheduled', createdAt: new Date().toISOString() },
  { id: 4, inverterId: 3, stringId: null, userId: 2, title: 'Panel cleaning', description: 'Annual panel cleaning Section A', section: 'Section A', date: d(1_209_600_000), technician: 'David Kim', scheduledDate: d(1_209_600_000), completedDate: null, status: 'scheduled', createdAt: new Date(Date.now() - 86_400_000).toISOString() },
];
