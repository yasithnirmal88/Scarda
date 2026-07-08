import { useEffect, useState } from 'react';
import type { MaintenanceLog } from '../types';
import { alertService } from '../services/alertService';
import { MaintenanceTable } from '../components/tables/MaintenanceTable';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export function Maintenance() {
  const [logs, setLogs] = useState<MaintenanceLog[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    alertService.getMaintenanceLogs().then((data) => {
      setLogs(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner size="lg" />;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-gray-900 dark:text-white">Maintenance</h1>
      <MaintenanceTable data={logs} />
    </div>
  );
}
