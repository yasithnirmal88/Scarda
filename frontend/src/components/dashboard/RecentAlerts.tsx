import { AlertTriangle, Info, XCircle, Loader } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { alertService } from '../../services/alertService';
import { classNames } from '../../utils/helpers';

const icons = {
  critical: XCircle,
  warning: AlertTriangle,
  info: Info,
};

const iconColors = {
  critical: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500',
};

export function RecentAlerts() {
  const { data: alerts, isLoading, isError } = useQuery({
    queryKey: ['alerts'],
    queryFn: alertService.getActive,
    refetchInterval: 30_000,
    staleTime: 10_000,
  });

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5 flex items-center justify-center h-40">
        <Loader className="animate-spin text-gray-400" size={20} />
      </div>
    );
  }

  const recent = (alerts ?? []).slice(0, 5);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
        Recent Alerts{isError ? ' (offline)' : ''}
      </h3>
      {recent.length === 0 ? (
        <p className="text-sm text-gray-400 dark:text-gray-500">No active alerts</p>
      ) : (
        <div className="space-y-3">
          {recent.map((alert) => {
            const Icon = icons[alert.severity as keyof typeof icons] || Info;
            return (
              <div key={alert.id} className="flex items-start gap-3">
                <Icon size={16} className={classNames('mt-0.5', iconColors[alert.severity as keyof typeof iconColors] || 'text-blue-500')} />
                <div className="min-w-0">
                  <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {alert.title}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {alert.timestamp} — {alert.source}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}