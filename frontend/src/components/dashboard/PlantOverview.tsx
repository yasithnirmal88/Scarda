import { Zap, Activity, Thermometer, Battery } from 'lucide-react';
import { StatCard } from '../common/StatCard';

export function PlantOverview() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total Power"
        value="4.2 MW"
        subtitle="Current generation"
        icon={<Zap size={20} />}
        trend={{ value: 3.2, isUp: true }}
      />
      <StatCard
        title="Energy Today"
        value="32.8 MWh"
        subtitle="Cumulative"
        icon={<Activity size={20} />}
        trend={{ value: 1.1, isUp: true }}
      />
      <StatCard
        title="Avg Temperature"
        value="42.3°C"
        subtitle="Panel surface"
        icon={<Thermometer size={20} />}
        trend={{ value: 0.4, isUp: false }}
      />
      <StatCard
        title="Efficiency"
        value="94.7%"
        subtitle="Performance ratio"
        icon={<Battery size={20} />}
        trend={{ value: 1.8, isUp: false }}
      />
    </div>
  );
}
