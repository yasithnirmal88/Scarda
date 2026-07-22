import { Zap, Activity, Thermometer, Battery, AlertTriangle, Power } from 'lucide-react';
import { StatCard } from '../common/StatCard';
import { formatPower } from '../../utils/helpers';
import type { DashboardResponse } from '../../services/dashboardService';

interface PlantOverviewProps {
  data?: DashboardResponse;
  isLoading: boolean;
}

export function PlantOverview({ data, isLoading }: PlantOverviewProps) {
  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5 animate-pulse"
          >
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-20 mb-3" />
            <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded w-28 mb-2" />
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-24" />
          </div>
        ))}
      </div>
    );
  }

  const p = data.power;
  const plant = data.plant;
  const alerts = data.alerts;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total Power"
        value={formatPower(p.total_power_kw * 1000)}
        subtitle="Current generation"
        icon={<Zap size={20} />}
      />
      <StatCard
        title="Energy Today"
        value={`${p.daily_energy_kwh.toFixed(1)} kWh`}
        subtitle="Cumulative"
        icon={<Activity size={20} />}
      />
      <StatCard
        title="Active Alerts"
        value={String(alerts.total)}
        subtitle={`${alerts.critical} critical, ${alerts.warning} warning`}
        icon={<AlertTriangle size={20} />}
      />
      <StatCard
        title="Plant Status"
        value={`${plant.active_inverters}/${plant.total_inverters}`}
        subtitle="Active inverters"
        icon={<Power size={20} />}
      />
    </div>
  );
}
