import { AlertTriangle, Info, XCircle } from 'lucide-react';
import { mockAlerts } from '../../mock/mockAlerts';
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
  const recent = mockAlerts.slice(0, 5);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-5">
      <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
        Recent Alerts
      </h3>
      <div className="space-y-3">
        {recent.map((alert) => {
          const Icon = icons[alert.severity];
          return (
            <div key={alert.id} className="flex items-start gap-3">
              <Icon size={16} className={classNames('mt-0.5', iconColors[alert.severity])} />
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
    </div>
  );
}
