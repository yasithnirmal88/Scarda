import { useState } from 'react';
import type { PVString } from '../../types';
import { Pagination } from '../common/Pagination';
import { SearchBar } from '../common/SearchBar';
import { HealthBadge } from '../common/HealthBadge';

interface StringsTableProps {
  data: PVString[];
}

export function StringsTable({ data }: StringsTableProps) {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const filtered = data.filter(
    (s) =>
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.id.toString().includes(search),
  );
  const paged = filtered.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <SearchBar value={search} onChange={setSearch} placeholder="Search strings..." />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700 text-left text-xs text-gray-500 dark:text-gray-400 uppercase">
              <th className="px-4 py-3 font-medium">ID</th>
              <th className="px-4 py-3 font-medium">Name</th>
              <th className="px-4 py-3 font-medium">Voltage</th>
              <th className="px-4 py-3 font-medium">Current</th>
              <th className="px-4 py-3 font-medium">Power</th>
              <th className="px-4 py-3 font-medium">Temperature</th>
              <th className="px-4 py-3 font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {paged.map((s) => (
              <tr key={s.id} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                <td className="px-4 py-3 text-gray-500">{s.id}</td>
                <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{s.name}</td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{s.voltage} V</td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{s.current} A</td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{s.power} kW</td>
                <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{s.temperature}°C</td>
                <td className="px-4 py-3">
                  <HealthBadge status={s.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Pagination page={page} pageSize={pageSize} total={filtered.length} onPageChange={setPage} />
    </div>
  );
}
