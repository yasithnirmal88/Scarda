import type { Alert } from '../types';

interface AlertCardProps {
  alert: Alert;
}

export function AlertCard({ alert }: AlertCardProps) {
  const severityColor =
    alert.severity === 'critical'
      ? 'bg-red-100 text-red-800'
      : alert.severity === 'warning'
        ? 'bg-yellow-100 text-yellow-800'
        : 'bg-blue-100 text-blue-800';

  return (
    <div className="border rounded-lg p-4 flex items-start gap-3">
      <span className={`px-2 py-1 rounded text-xs font-medium ${severityColor}`}>
        {alert.severity}
      </span>
      <div>
        <p className="font-medium">{alert.type}</p>
        <p className="text-sm text-gray-600">{alert.message}</p>
      </div>
    </div>
  );
}
