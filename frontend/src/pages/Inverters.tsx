import { useEffect, useState } from 'react';
import type { Inverter } from '../types';
import { inverterService } from '../services/inverterService';
import { HealthBadge } from '../components/common/HealthBadge';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export function Inverters() {
  const [inverters, setInverters] = useState<Inverter[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    inverterService.getAll().then((data) => {
      setInverters(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner size="lg" />;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-gray-900 dark:text-white">Inverters</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {inverters.map((inv) => (
          <div
            key={inv.id}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5"
          >
            <div className="flex items-center justify-between mb-2">
              <h3 className="font-semibold text-gray-900 dark:text-white">{inv.name}</h3>
              <HealthBadge status={inv.status} />
            </div>
            <p className="text-sm text-gray-500 mb-2">Section {inv.sectionId}</p>
            <div className="text-sm text-gray-700 dark:text-gray-300">
              <p>Power: {inv.power} kW</p>
              <p>Efficiency: {inv.efficiency}%</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
