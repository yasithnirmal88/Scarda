import { useQuery } from '@tanstack/react-query';
import { dashboardService } from '../../services/dashboardService';
import { HealthBadge } from '../common/HealthBadge';

const SECTIONS = [
  { id: 1, name: 'Section A' },
  { id: 2, name: 'Section B' },
  { id: 3, name: 'Section C' },
  { id: 4, name: 'Section D' },
];

export function SystemStatusCard() {
  const { data, isLoading } = useQuery({
    queryKey: ['dashboard'],
    queryFn: dashboardService.get,
    refetchInterval: 30_000,
    staleTime: 10_000,
  });

  const alerts = data?.alerts;
  const total = SECTIONS.length;
  const hasCritical = (alerts?.critical ?? 0) > 0;
  const hasWarning = (alerts?.warning ?? 0) > 0;

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
        System Status
      </h3>
      {isLoading ? (
        <div className="space-y-3 animate-pulse">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-5 bg-gray-200 dark:bg-gray-700 rounded" />
          ))}
        </div>
      ) : (
        <>
          <div className="space-y-3">
            {SECTIONS.map((section) => {
              let status: 'healthy' | 'warning' | 'critical' | 'offline' = 'healthy';
              if (hasCritical) status = 'critical';
              else if (hasWarning) status = 'warning';
              return (
                <div key={section.id} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    {section.name}
                  </span>
                  <HealthBadge status={status} />
                </div>
              );
            })}
            <div className="pt-3 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between text-sm">
              <span className="font-medium text-gray-700 dark:text-gray-300">
                {alerts ? `${Math.max(0, total - (hasCritical ? 1 : 0))}/${total} sections healthy` : `${total}/${total} sections`}
              </span>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
