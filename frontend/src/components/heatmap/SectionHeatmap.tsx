import { HealthBadge } from '../common/HealthBadge';

interface SectionHeatmapProps {
  name: string;
  status: string;
  inverterCount: number;
  inverters: Array<{ id: number; status: string; label: string }>;
}

export function SectionHeatmap({ name, status, inverterCount, inverters }: SectionHeatmapProps) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-semibold text-gray-900 dark:text-white">{name}</h3>
          <p className="text-xs text-gray-500">{inverterCount} inverters</p>
        </div>
        <HealthBadge status={status} />
      </div>
      <div className="grid grid-cols-3 gap-1.5">
        {inverters.map((inv) => {
          const color =
            inv.status === 'healthy'
              ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300'
              : inv.status === 'warning'
                ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300'
                : 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300';
          return (
            <div key={inv.id} className={`h-8 rounded text-xs flex items-center justify-center font-medium ${color}`}>
              {inv.label}
            </div>
          );
        })}
      </div>
    </div>
  );
}
