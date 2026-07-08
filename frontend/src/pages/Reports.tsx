import { useEffect, useState } from 'react';
import { Plus } from 'lucide-react';
import type { Report } from '../types';
import { reportService } from '../services/reportService';
import { ReportsTable } from '../components/tables/ReportsTable';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export function Reports() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch = () => reportService.getAll().then((data) => {
    setReports(data);
    setLoading(false);
  });

  useEffect(() => { fetch(); }, []);

  const generate = () => {
    reportService.generate('daily').then((r) => {
      setReports((prev) => [r, ...prev]);
    });
  };

  if (loading) return <LoadingSpinner size="lg" />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-gray-900 dark:text-white">Reports</h1>
        <button
          onClick={generate}
          className="flex items-center gap-2 px-4 py-2 bg-solar-600 hover:bg-solar-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          Generate Report
        </button>
      </div>
      <ReportsTable data={reports} />
    </div>
  );
}
