import { useEffect, useState } from 'react';
import type { PVString } from '../types';
import { stringService } from '../services/stringService';
import { StringsTable } from '../components/tables/StringsTable';
import { LoadingSpinner } from '../components/common/LoadingSpinner';

export function StringsPage() {
  const [strings, setStrings] = useState<PVString[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    stringService.getAll().then((data) => {
      setStrings(data);
      setLoading(false);
    });
  }, []);

  if (loading) return <LoadingSpinner size="lg" />;

  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-gray-900 dark:text-white">Strings</h1>
      <StringsTable data={strings} />
    </div>
  );
}
