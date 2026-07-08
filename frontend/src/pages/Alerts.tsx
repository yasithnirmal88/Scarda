import { AlertCard } from '../components/AlertCard';
import type { Alert } from '../types';

const placeholderAlerts: Alert[] = [
  { id: 1, inverter_id: 1, string_id: null, type: 'Overheating', severity: 'critical', message: 'Inverter INV-001 temperature critical', status: 'active', created_at: '' },
  { id: 2, inverter_id: null, string_id: 3, type: 'Low Power', severity: 'warning', message: 'String STR-003 low output', status: 'active', created_at: '' },
  { id: 3, inverter_id: 2, string_id: null, type: 'Communication Lost', severity: 'critical', message: 'Inverter INV-002 no communication', status: 'active', created_at: '' },
  { id: 4, inverter_id: null, string_id: 7, type: 'High Voltage', severity: 'warning', message: 'String STR-007 voltage spike detected', status: 'acknowledged', created_at: '' },
];

export function Alerts() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Alerts</h2>
      <p className="text-gray-500">This page will display alerts and notifications.</p>

      <div className="grid grid-cols-1 gap-3">
        {placeholderAlerts.map((a) => (
          <AlertCard key={a.id} alert={a} />
        ))}
      </div>
    </div>
  );
}
