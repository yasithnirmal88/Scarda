import { useEffect, useState } from 'react';
import type { Alert } from '../types';
import { alertService } from '../services/alertService';
import { AlertsTable } from '../components/tables/AlertsTable';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    alertService.getAll().then((data) => {
      setAlerts(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner size="lg" />;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-gray-900 dark:text-white">Alerts</h1>
      <AlertsTable data={alerts} />
    </div>
  );
}
