import { AlertCard } from '../components/AlertCard';
import { Heatmap } from '../components/Heatmap';
import { LineChart } from '../components/LineChart';
import { NotificationPanel } from '../components/NotificationPanel';
import { StatCard } from '../components/StatCard';
import type { Alert } from '../types';

const placeholderAlerts: Alert[] = [
  {
    id: 1, inverter_id: null, string_id: 1,
    type: 'Low Power', severity: 'warning',
    message: 'String STR-001 producing below expected power',
    status: 'active', created_at: '',
  },
  {
    id: 2, inverter_id: 1, string_id: null,
    type: 'Overheating', severity: 'critical',
    message: 'Inverter INV-001 temperature exceeds threshold',
    status: 'active', created_at: '',
  },
];

export function Dashboard() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard</h2>
      <p className="text-gray-500">This page will display plant overview.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Power" value="2,450.5" unit="kW" />
        <StatCard title="Daily Energy" value="18,500" unit="kWh" />
        <StatCard title="Active Inverters" value="34" unit="/ 36" />
        <StatCard title="Efficiency" value="94.2" unit="%" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LineChart />
        <Heatmap />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-3">
          <h3 className="font-semibold">Recent Alerts</h3>
          {placeholderAlerts.map((a) => (
            <AlertCard key={a.id} alert={a} />
          ))}
        </div>
        <NotificationPanel />
      </div>
    </div>
  );
}
