import { useState } from 'react';
import type { Alert } from '../../types';
import { Pagination } from '../common/Pagination';
import { SearchBar } from '../common/SearchBar';

interface AlertsTableProps {
  data: Alert[];
}

export function AlertsTable({ data }: AlertsTableProps) {
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const filtered = data.filter(
    (a) =>
      a.title.toLowerCase().includes(search.toLowerCase()) ||
      a.source.toLowerCase().includes(search.toLowerCase()),
  );
  const paged = filtered.slice((page - 1) * pageSize, page * pageSize);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700">
        <SearchBar value={search} onChange={setSearch} placeholder="Search alerts..." />
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700 text-left text-xs text-gray-500 dark:text-gray-400 uppercase">
              <th className="px-4 py-3 font-medium">Severity</th>
              <th className="px-4 py-3 font-medium">Title</th>
              <th className="px-4 py-3 font-medium">Source</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Time</th>
            </tr>
          </thead>
          <tbody>
            {paged.map((alert) => (
              <tr key={alert.id} className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30">
                <td className="px-4 py-3">
                  <span
                    className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                      alert.severity === 'critical'
                        ? 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300'
                        : alert.severity === 'warning'
                          ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/40 dark:text-yellow-300'
                          : 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300'
                    }`}
                  >
                    {alert.severity}
                  </span>
                </td>
                <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{alert.title}</td>
                <td className="px-4 py-3 text-gray-500">{alert.source}</td>
                <td className="px-4 py-3">
                  <span
                    className={`inline-block w-2 h-2 rounded-full ${
                      alert.status === 'active' ? 'bg-red-500' : 'bg-green-500'
                    }`}
                  />
                </td>
                <td className="px-4 py-3 text-gray-500">{alert.timestamp}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Pagination page={page} pageSize={pageSize} total={filtered.length} onPageChange={setPage} />
    </div>
  );
}
